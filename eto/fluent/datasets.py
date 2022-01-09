"""Eto SDK Fluent API for managing datasets"""
from itertools import islice
import os
import uuid
from typing import Optional, Union

import pandas as pd
from rikai.io import _normalize_uri
from rikai.parquet.dataset import Dataset as RikaiDataset

from eto.config import Config
from eto.fluent.client import get_api
from eto.fluent.jobs import ingest_rikai
from eto.util import add_method, get_dataset_ref_parts


def list_datasets(project="default") -> pd.DataFrame:
    """Lists existing datasets (dataset_id, uri, and other metadata)

    Parameters
    ----------
    project: str, default 'default'
        List all datasets in a particular project.
        If omitted just lists datasets in 'default'
    """
    datasets = get_api("datasets").list_datasets(project)["datasets"]
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
    return get_api("datasets").get_dataset(project_id, dataset_id)


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
        rows = islice(dataset, limit)
        return pd.DataFrame(rows)


@add_method(pd.DataFrame)
def to_eto(
    self,
    dataset_name: str,
    partition: Optional[str] or list[str] = None,
    mode: str = "append",
    async_: bool = False,
    max_wait_sec: int = -1,
    schema: "pyspark.sql.types.StructType" = None,
):
    """Create a new dataset from this DataFrame

    Parameters
    ----------
    dataset_name: str
        The name of the new dataset that will be created
    partition: Optional[str] or list[str], default None
        Which columns to partition by
    mode: str, default 'append'
        Controls behavior if the dataset_name already exists
    async_: bool, default False
        If True then return immediately with the ingestion Job
    max_wait_sec: int, default -1
        Maximum number of seconds to wait. If negative then wait forever.
        If async_ is True then this is ignored
    schema: pyspark.sql.types.StructType, default None
        By default the schema is inferred. Specify this override if needed.
    """
    from eto.spark import get_session

    spark = get_session()
    df = spark.createDataFrame(self, schema)
    sdk_conf = Config.load()
    path = os.path.join(sdk_conf["tmp_workspace_path"], str(uuid.uuid4()))
    df.write.format("rikai").mode(mode).partitionBy(partition).save(path)
    job = ingest_rikai(dataset_name, path, mode, partition)
    if async_:
        return job
    else:
        job.wait(max_wait_sec)
        return job
