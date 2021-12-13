from ctypes import Union

from eto.internal.api.jobs_api import JobsApi, CreateJobRequest
from eto.connectors.base import Connector


class CocoSource:

    def __init__(self, image_dir: str, annotations: str, extras: dict):
        """Specifications for a single coco data source

        Parameters
        ----------
        image_dir: str
            The url/path to the raw images
        annotations: str
            The url/path to the annotations
        extras: dict
            Additional fields/values to set
        """
        self.image_dir = image_dir
        self.annotations = annotations
        self.extras = extras

    def to_dict(self):
        return {
            'image_dir': self.image_dir,
            'annotations': self.annotations,
            'extras': self.extras
        }


class CocoConnector(Connector):
    """Connector to ingest Coco dataset"""

    def __init__(self, jobs_api: JobsApi):
        super().__init__(jobs_api)
        self._sources = []
        self.connector_type = 'coco'

    def add_source(self, source: CocoSource):
        """Add a Coco data source"""
        self._sources.append(source)

    @property
    def request_body(self) -> CreateJobRequest:
        """Form the Coco job request body"""
        project_id = self.project_id if self.project_id is not None else 'default'
        mode = self.mode if self.mode is not None else 'error'
        if self.dataset_id is None or len(self.dataset_id) == 0:
            raise ValueError('Dataset id must be non-empty')
        return CreateJobRequest(dataset_name=f"{project_id}.{self.dataset_id}",
                                sources=[x.to_dict() for x in self._sources],
                                mode=mode,
                                partition=self.partition)
