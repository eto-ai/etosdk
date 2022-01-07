from typing import Optional

from eto._internal.api.jobs_api import CreateJobRequest, JobsApi
from eto._internal.model.rikai_config import RikaiConfig
from eto.connectors.base import Connector


class RikaiConnector(Connector):
    """Connector to ingest Coco dataset"""

    def __init__(self, jobs_api: JobsApi):
        super().__init__(jobs_api)
        self.url: Optional[str] = None
        self.connector_type = "rikai"

    @property
    def request_body(self) -> CreateJobRequest:
        """Form the Rikai job request body"""
        if self.dataset_id is None or len(self.dataset_id) == 0:
            raise ValueError("Dataset id must be non-empty")
        kwargs = {}
        if self.partition is not None:
            kwargs = {
                "partition": [self.partition]
                if isinstance(self.partition, str)
                else self.partition
            }

        config = RikaiConfig(
            dataset_name=f"{self.project_id}.{self.dataset_id}",
            url=self.url,
            mode=self.mode,
            **kwargs,
        )
        return CreateJobRequest(connector=self.connector_type, config=config)
