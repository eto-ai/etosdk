from ctypes import Union

from eto.connectors.base import Connector
from eto._internal.api.jobs_api import CreateJobRequest, JobsApi
from eto._internal.model.coco_config import CocoConfig
from eto._internal.model.coco_source import CocoSource


class CocoConnector(Connector):
    """Connector to ingest Coco dataset"""

    def __init__(self, jobs_api: JobsApi):
        super().__init__(jobs_api)
        self._sources: list[CocoSource] = []
        self.connector_type = "coco"

    def add_source(self, source: CocoSource):
        """Add a Coco data source"""
        self._sources.append(source)

    @property
    def request_body(self) -> CreateJobRequest:
        """Form the Coco job request body"""
        if self.dataset_id is None or len(self.dataset_id) == 0:
            raise ValueError("Dataset id must be non-empty")
        kwargs = {}
        if self.partition is not None:
            kwargs = {
                "partition": [self.partition]
                if isinstance(self.partition, str)
                else self.partition
            }

        config = CocoConfig(
            dataset_name=f"{self.project_id}.{self.dataset_id}",
            source=self._sources,
            mode=self.mode,
            **kwargs,
        )
        return CreateJobRequest(connector=self.connector_type, config=config)
