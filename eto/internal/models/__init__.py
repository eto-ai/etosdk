# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from eto.internal.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from eto.internal.model.coco_config import CocoConfig
from eto.internal.model.coco_source import CocoSource
from eto.internal.model.create_job_request import CreateJobRequest
from eto.internal.model.dataset import Dataset
from eto.internal.model.dataset_details import DatasetDetails
from eto.internal.model.inline_response200 import InlineResponse200
from eto.internal.model.inline_response404 import InlineResponse404
from eto.internal.model.inline_response2001 import InlineResponse2001
from eto.internal.model.job import Job
