from abc import ABC, abstractmethod

from eto._internal.api.jobs_api import CreateJobRequest, Job, JobsApi


class Connector(ABC):
    """Abstract class for dataset connectors"""

    def __init__(self, jobs_api: JobsApi):
        self._api_client = jobs_api
        self.project_id = None
        self.dataset_id = None
        self.partition = None
        self._mode = None
        self._connector_type = None

    @property
    def mode(self) -> str:
        """If the dataset already exists, specifies ingest behavior"""
        return self._mode

    @mode.setter
    def mode(self, mode: str):
        """If the dataset already exists, specifies behavior

        Parameters
        ----------
        mode: str
            'append', 'overwrite',
        """
        mode = mode.lower().strip()
        if mode not in ["append", "overwrite", "error", "ignore"]:
            raise NotImplementedError(f"Unrecognized mode {mode}")
        self._mode = mode

    @property
    def connector_type(self) -> str:
        return self._connector_type

    @connector_type.setter
    def connector_type(self, connector_type: str):
        connector_type = connector_type.lower().strip()
        if connector_type not in ["coco", "rikai"]:
            raise NotImplementedError("Only the Coco connector is supported")
        self._connector_type = connector_type

    @property
    @abstractmethod
    def request_body(self) -> CreateJobRequest:
        """The ingest request body"""
        pass

    def ingest(self) -> Job:
        """Call the Eto API and ingest the dataset"""
        return self._api_client.create_ingest_job(self.project_id, self.request_body)
