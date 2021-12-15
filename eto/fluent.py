from typing import Iterable, Optional, Union
from urllib.parse import urlparse

import pandas as pd

from eto.config import Config
from eto.connectors.coco import CocoConnector, CocoSource
from eto.internal.api.jobs_api import JobsApi
from eto.internal.api_client import ApiClient
from eto.internal.apis import DatasetsApi
from eto.internal.configuration import Configuration
from eto.internal.model.dataset import Dataset
from eto.resolver import register_resolver
from eto.internal.model.job import Job
from eto.spark import get_session
from eto.util import get_dataset_ref_parts

__all__ = ["list_datasets", "get_dataset", "ingest_coco", "CocoSource", "init", "configure"]

_LAZY_CLIENTS = {}


def _get_api(api_name: str):
    if _LAZY_CLIENTS.get(api_name) is None:
        client = _get_client()
        _LAZY_CLIENTS[api_name] = _create_api(api_name, client)
    return _LAZY_CLIENTS[api_name]


def _get_client() -> ApiClient:
    sdk_conf = Config.load()
    url = sdk_conf["url"]
    conf = Configuration(host=url)
    return ApiClient(
        configuration=conf,
        header_name="Authorization",
        header_value=f'Bearer {sdk_conf["token"]}',
    )


def _create_api(api_name, client):
    if api_name not in ["datasets", "jobs"]:
        raise NotImplementedError("Only datasets and jobs api supported")
    cls_map = {
        "datasets": DatasetsApi,
        "jobs": JobsApi
    }
    api = cls_map[api_name]
    return api(client)


def list_datasets(project="default") -> list[Dataset]:
    """Lists existing datasets (dataset_id, uri, and other metadata)

    Parameters
    ----------
    project: str, default 'default'
        List all datasets in a particular project.
        If omitted just lists datasets in 'default'
    """
    return _get_api("datasets").list_datasets(project)['datasets']


def get_dataset(dataset_name: str) -> Dataset:
    """Retrieve metadata for a given dataset

    Parameters
    ----------
    dataset_name: str
        Qualified name <project.dataset>.
        If no project is specified, assume it's the 'default' project
    """
    project_id, dataset_id = get_dataset_ref_parts(dataset_name)
    project_id = project_id or 'default'
    return _get_api("datasets").get_dataset(project_id, dataset_id)


def ingest_coco(dataset_name: str,
                source: Union[CocoSource, dict, Iterable[CocoSource], Iterable[dict]],
                mode: str = 'append',
                partition: str = None) -> Job:
    """Create a data ingestion job to convert coco datasets to Rikai format
    and create a new entry in the Eto dataset registry

    Parameters
    ----------
    dataset_name: str
        The name of the new Eto dataset
    source: dict, Iterable[dict], CocoSource, Iterable[CocoSource]
        Specification for the raw data sources in Coco format. For multiple
        sources, just specify all of the sources in a single list
        Example: {'image_dir': 's3://path/to/images',
                  'annotation': 's3://path/to/annotation',
                  'extras': {'split': 'train'}}
    mode: str, default 'append'
        Defines behavior when the dataset already exists
        'overwrite' means existing data is replaced
        'append' means the new data will be added
    partition: str or list of str
        Which field to partition on (ex. 'split')
    """
    conn = CocoConnector(_get_api("jobs"))
    if '.' in dataset_name:
        project_id, dataset_id = dataset_name.split('.', 1)
    else:
        project_id, dataset_id = 'default', dataset_name
    conn.project_id = project_id
    conn.dataset_id = dataset_id
    if isinstance(source, (CocoSource, dict)):
        source = [source]
    [conn.add_source(s if isinstance(s, CocoSource) else CocoSource(**s))
     for s in source]
    conn.mode = mode or 'append'
    if partition is not None:
        conn.partition = [partition] if isinstance(partition, str) else partition
    return conn.ingest()


def init():
    # monkey patch pandas
    def read_eto(dataset_name: str, limit: int = None) -> pd.DataFrame:
        """Read an Eto dataset as a pandas dataframe

        Parameters
        ----------
        dataset_name: str
            The name of the dataset to be read
        limit: Optional[int]
            The max rows to retrieve. If omitted then all rows are retrieved
        """
        uri = get_dataset(dataset_name).uri
        sdf = get_session().read.format("rikai").load(uri)
        if limit is not None and limit > 0:
            sdf = sdf.limit(limit)
        return sdf.toPandas()

    pd.read_eto = read_eto

    # register Rikai resolver
    register_resolver()


def configure(
    url: Optional[str] = None,
    token: Optional[str] = None,
):
    """One time setup to configure the SDK to connect to Eto API

    Parameters
    ----------
    url: str, default None
        host url for the Eto API backend. If not supplied then will default
        to ETO_HOST_URL environment variable
    token: str, default None
        the api token. If omitted then will default to ETO_API_TOKEN
        environment variable
    """
    url = url or Config.ETO_HOST_URL
    token = token or Config.ETO_API_TOKEN
    if url is None:
        raise ValueError("Please provide the host url for the Eto API")
    if token is None:
        raise ValueError("Please provide the API token for the Eto API")
    o = urlparse(url)
    if o.scheme is None:
        raise ValueError("No scheme was found in url")
    if o.netloc is None:
        raise ValueError("Host location was empty in the url")
    Config.create_config(url, token)
    _LAZY_CLIENTS.clear()
