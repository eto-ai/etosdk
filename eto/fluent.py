import logging
import time
from itertools import islice
from typing import Iterable, Optional, Union
from urllib.parse import urlparse

import pandas as pd
from rikai.io import _normalize_uri
from rikai.logging import logger
from rikai.parquet.dataset import Dataset as RikaiDataset

from eto.config import Config
from eto.connectors.coco import CocoConnector, CocoSource
from eto._internal.api.jobs_api import JobsApi
from eto._internal.api_client import ApiClient
from eto._internal.apis import DatasetsApi
from eto._internal.configuration import Configuration
from eto._internal.model.dataset_details import DatasetDetails
from eto._internal.model.job import Job
from eto.resolver import register_resolver
from eto.util import get_dataset_ref_parts

__all__ = [
    "list_datasets",
    "get_dataset",
    "ingest_coco",
    "list_jobs",
    "get_job_info",
    "CocoSource",
    "init",
    "configure",
]

_LAZY_CLIENTS = {}


def _get_api(api_name: str):
    if _LAZY_CLIENTS.get(api_name) is None:
        client = _get_client()
        _LAZY_CLIENTS[api_name] = _create_api(api_name, client)
    return _LAZY_CLIENTS[api_name]


def _get_client() -> ApiClient:
    sdk_conf = Config.load()
    url = sdk_conf["url"]
    if url.endswith("/"):
        url = url[:-1]
    conf = Configuration(host=url)
    return ApiClient(
        configuration=conf,
        header_name="Authorization",
        header_value=f'Bearer {sdk_conf["token"]}',
    )


def _create_api(api_name, client):
    if api_name not in ["datasets", "jobs"]:
        raise NotImplementedError("Only datasets and jobs api supported")
    cls_map = {"datasets": DatasetsApi, "jobs": JobsApi}
    api = cls_map[api_name]
    return api(client)


def list_datasets(project="default") -> pd.DataFrame:
    """Lists existing datasets (dataset_id, uri, and other metadata)

    Parameters
    ----------
    project: str, default 'default'
        List all datasets in a particular project.
        If omitted just lists datasets in 'default'
    """
    datasets = _get_api("datasets").list_datasets(project)["datasets"]
    return pd.DataFrame([x.to_dict() for x in datasets])


def get_dataset(dataset_name: str) -> pd.Series:
    """Retrieve metadata for a given dataset

    Parameters
    ----------
    dataset_name: str
        Qualified name <project.dataset>.
        If no project is specified, assume it's the 'default' project
    """
    project_id, dataset_id = get_dataset_ref_parts(dataset_name)
    project_id = project_id or "default"
    return _get_api("datasets").get_dataset(project_id, dataset_id)


def ingest_coco(
    dataset_name: str,
    source: Union[CocoSource, dict, Iterable[CocoSource], Iterable[dict]],
    mode: str = "append",
    partition: str = None,
) -> Job:
    """Create a data ingestion job to convert coco to Rikai format and create a new entry in the Eto dataset registry

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
    if "." in dataset_name:
        project_id, dataset_id = dataset_name.split(".", 1)
    else:
        project_id, dataset_id = "default", dataset_name
    conn.project_id = project_id
    conn.dataset_id = dataset_id
    if isinstance(source, (CocoSource, dict)):
        source = [source]
    [
        conn.add_source(s if isinstance(s, CocoSource) else CocoSource(**s))
        for s in source
    ]
    conn.mode = mode or "append"
    if partition is not None:
        conn.partition = [partition] if isinstance(partition, str) else partition
    return conn.ingest()


def list_jobs(
    project_id: str = "default", _page_size: int = 50, _start_page_token: int = 0
) -> pd.DataFrame:
    """List all jobs for a given project

    Parameters
    ----------
    project_id: str, default 'default'
      Show jobs under this project
    """
    jobs = _get_api("jobs")
    frames = []
    page = jobs.list_ingest_jobs(
        project_id, page_size=_page_size, page_token=_start_page_token
    )
    while len(page["jobs"]) > 0:
        frames.append(pd.DataFrame([j.to_dict() for j in page["jobs"]]))
        page = jobs.list_ingest_jobs(
            project_id, page_size=_page_size, page_token=page["next_page_token"]
        )
    return pd.concat(frames, ignore_index=True).drop_duplicates(
        ["id"], ignore_index=True
    )


def get_job_info(job_id: str, project_id: str = "default") -> Job:
    jobs = _get_api("jobs")
    return jobs.get_ingest_job(project_id, job_id)


def init():
    # monkey patch pandas
    pd.read_eto = read_eto

    # register Rikai resolver
    register_resolver()

    # Suppress Rikai info output
    logger.setLevel(logging.WARNING)

    _patch_openapi_client()


def read_eto(
    dataset_name: str, columns: Union[str, list[str]] = None, limit: int = None
) -> pd.DataFrame:
    """Read an Eto dataset as a pandas dataframe

    Parameters
    ----------
    dataset_name: str
        The name of the dataset to be read
    columns: str or list of str, default None
        Which columns to read in. All columns by default.
    limit: Optional[int]
        The max rows to retrieve. If omitted or <=0 then all rows are retrieved
    """
    uri = _normalize_uri(get_dataset(dataset_name).uri)
    if isinstance(columns, str):
        columns = [columns]
    dataset = RikaiDataset(uri, columns)
    if limit is None or limit <= 0:
        return pd.DataFrame(dataset)
    else:
        rows = [None] * limit
        i = 0
        for i, r in enumerate(dataset):
            rows[i] = r
            if i == limit - 1:
                break
        if i < limit - 1:
            rows = rows[: i + 1]
        return pd.DataFrame(rows)


def _patch_openapi_client():
    # Monkey patch the generated openapi classes
    # update the to_str method in DatasetDetails for better schema display
    def to_str(self):
        summary = pd.Series(self.to_dict()).to_string(dtype=False)
        return "DatasetDetails:\n" + summary

    DatasetDetails.to_str = to_str

    def _repr_html_(self):
        fields = pd.Series(self.to_dict())
        cols = ["project_id", "dataset_id", "uri", "size", "created_at"]
        headers = fields[cols].to_string(dtype=False)
        schema = pd.DataFrame(
            list(_convert_types(self.schema).items()),
            columns=["name", "type"],
        )
        schema.style.set_tooltips(schema)
        return f"<pre>{headers}\nSchema</pre>" + schema._repr_html_()

    DatasetDetails._repr_html_ = _repr_html_

    def check_status(self):
        """Call the Eto API to check for the latest job status"""
        return get_job_info(self.id, self.project_id).status

    Job.check_status = check_status

    Job.wait = _wait_for_job


def _wait_for_job(self, max_seconds: int = -1, poke_interval: int = 10) -> str:
    """Wait for the job to complete (either failed or success)

    Parameters
    ----------
    max_seconds: int, default -1
      Max number of seconds to wait. If -1 wait forever.
    poke_interval: int, default 10
      Interval between checks in seconds
    """
    status = self.status
    sleep_sec = poke_interval if max_seconds < 0 else min(poke_interval, max_seconds)
    elapsed = 0
    while status not in ("failed", "success"):
        time.sleep(sleep_sec)
        status = self.check_status()
        elapsed += poke_interval
        if 0 <= max_seconds < elapsed:
            break
    return status


def _get_account_url(account, use_ssl, port):
    scheme = "https" if use_ssl else "http"
    url = f"{scheme}://{account}.eto.ai"
    if port is not None:
        url = url + f":{port}"
    return url


def _convert_types(schema: Union[str, dict]):
    """Convert schema fields for better display"""
    if isinstance(schema, str):
        # simple types
        return schema
    typ = schema["type"]
    if typ == "array":
        element_type = _convert_types(schema["elementType"])
        return f"[{element_type}]"
    elif typ == "struct":
        fields = schema["fields"]
        return {f["name"]: _convert_types(f["type"]) for f in fields}
    elif typ == "map":
        return {_convert_types(schema["keyType"]): _convert_types(schema["valueType"])}
    elif typ == "udt":
        return schema.get("pyClass", schema["class"]).rsplit(".", 1)[-1]
    else:
        raise ValueError(f"Unrecognized field type {typ}")


def configure(
    account: Optional[str] = None,
    token: Optional[str] = None,
    use_ssl: bool = True,
    port: Optional[int] = None,
):
    """One time setup to configure the SDK to connect to Eto API

    Parameters
    ----------
    account: str, default None
        Your Eto account name
    token: str, default None
        the api token. If omitted then will default to ETO_API_TOKEN
        environment variable
    use_ssl: bool, default True
        Whether to use an SSL-enabled connection
    port: int, default None
        Optional custom port to connect on
    """
    url = None
    if account is not None:
        url = _get_account_url(account, use_ssl, port)
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
