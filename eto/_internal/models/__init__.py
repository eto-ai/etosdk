# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from eto._internal.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from eto._internal.model.coco_config import CocoConfig
from eto._internal.model.coco_source import CocoSource
from eto._internal.model.create_job_request import CreateJobRequest
from eto._internal.model.create_model_request import CreateModelRequest
from eto._internal.model.dataset import Dataset
from eto._internal.model.dataset_details import DatasetDetails
from eto._internal.model.inline_object import InlineObject
from eto._internal.model.inline_response200 import InlineResponse200
from eto._internal.model.inline_response404 import InlineResponse404
from eto._internal.model.inline_response2001 import InlineResponse2001
from eto._internal.model.inline_response2002 import InlineResponse2002
from eto._internal.model.job import Job
from eto._internal.model.model import Model
from eto._internal.model.model_version import ModelVersion
from eto._internal.model.query import Query
from eto._internal.model.query_status import QueryStatus
from eto._internal.model.result_set import ResultSet
from eto._internal.model.rikai_config import RikaiConfig
from eto._internal.model.tags import Tags
