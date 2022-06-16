# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from eto._internal.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from eto._internal.model.bar_chart import BarChart
from eto._internal.model.bar_chart_y_inner import BarChartYInner
from eto._internal.model.box2d import Box2d
from eto._internal.model.coco_config import CocoConfig
from eto._internal.model.coco_source import CocoSource
from eto._internal.model.create_job_request import CreateJobRequest
from eto._internal.model.create_model_request import CreateModelRequest
from eto._internal.model.create_project_request import CreateProjectRequest
from eto._internal.model.dataset import Dataset
from eto._internal.model.dataset_details import DatasetDetails
from eto._internal.model.download_dataset200_response import DownloadDataset200Response
from eto._internal.model.embedding import Embedding
from eto._internal.model.embeddings_response import EmbeddingsResponse
from eto._internal.model.embeddings_response_data_inner import (
    EmbeddingsResponseDataInner,
)
from eto._internal.model.filter_spec import FilterSpec
from eto._internal.model.get_download_job200_response import GetDownloadJob200Response
from eto._internal.model.get_insight200_response import GetInsight200Response
from eto._internal.model.heat_map_chart import HeatMapChart
from eto._internal.model.image import Image
from eto._internal.model.job import Job
from eto._internal.model.list_dataset_insights200_response import (
    ListDatasetInsights200Response,
)
from eto._internal.model.list_datasets200_response import ListDatasets200Response
from eto._internal.model.list_datasets404_response import ListDatasets404Response
from eto._internal.model.list_ingest_jobs200_response import ListIngestJobs200Response
from eto._internal.model.list_models200_response import ListModels200Response
from eto._internal.model.mislabels_result_set import MislabelsResultSet
from eto._internal.model.mislabels_result_set_attributes import (
    MislabelsResultSetAttributes,
)
from eto._internal.model.model import Model
from eto._internal.model.model_version import ModelVersion
from eto._internal.model.polygon import Polygon
from eto._internal.model.query import Query
from eto._internal.model.query_status import QueryStatus
from eto._internal.model.result_set import ResultSet
from eto._internal.model.result_set_attributes import ResultSetAttributes
from eto._internal.model.rikai_config import RikaiConfig
from eto._internal.model.rle_mask import RLEMask
from eto._internal.model.row import Row
from eto._internal.model.scalar_type import ScalarType
from eto._internal.model.similar_response import SimilarResponse
from eto._internal.model.similar_response_data_inner import SimilarResponseDataInner
from eto._internal.model.struct_type import StructType
from eto._internal.model.tags import Tags
