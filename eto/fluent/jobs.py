"""Eto SDK fluent API for managing jobs"""
import time
from typing import Iterable, Optional, Union

import pandas as pd

from eto._internal.model.dataset_details import DatasetDetails
from eto._internal.model.job import Job
from eto.connectors.coco import CocoConnector, CocoSource
from eto.connectors.rikai import RikaiConnector
from eto.fluent.client import get_api


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
        Example:
        {
        'image_dir': 's3://path/to/images',
        'annotation': 's3://path/to/annotation',
        'extras': {'split': 'train'}
        }
    mode: str, default 'append'
        Defines behavior when the dataset already exists
        'overwrite' means existing data is replaced
        'append' means the new data will be added
    partition: str or list of str
        Which field to partition on (ex. 'split')
    """
    conn = CocoConnector(get_api("jobs"))
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


def ingest_rikai(
    dataset_name: str,
    url: str,
    mode: str = "append",
    partition: str = None,
    primary_key: Optional[str] = None
) -> Job:
    """Create a data ingestion job to create a new dataset using existing Rikai format data

    Parameters
    ----------
    dataset_name: str
        The name of the new Eto dataset
    url: str
        The url of the existing Rikai format data to be added to the catalog
    mode: str, default 'append'
        Defines behavior when the dataset already exists
        'overwrite' means existing data is replaced
        'append' means the new data will be added
    partition: str or list of str
        Which field to partition on (ex. 'split')
    """
    conn = RikaiConnector(get_api("jobs"))
    if "." in dataset_name:
        project_id, dataset_id = dataset_name.split(".", 1)
    else:
        project_id, dataset_id = "default", dataset_name
    conn.project_id = project_id
    conn.dataset_id = dataset_id
    conn.url = url
    conn.mode = mode or "append"
    if partition is not None:
        conn.partition = [partition] if isinstance(partition, str) else partition
    if primary_key is not None:
        conn.primary_key = primary_key
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
    jobs = get_api("jobs")
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
    jobs = get_api("jobs")
    return jobs.get_ingest_job(project_id, job_id)


def patch_jobs_client():
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
