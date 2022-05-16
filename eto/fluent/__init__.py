"""Eto SDK fluent api's"""
import logging

import pandas as pd
from rikai.logging import logger

from eto.resolver import register_resolver

from .client import *
from .datasets import *
from .jobs import *
from .models import *

# Define the fluent API methods here
__all__ = [
    "configure",
    "ingest_rikai",
    "ingest_coco",
    "list_jobs",
    "get_job_info",
    "CocoSource",
    "list_datasets",
    "get_dataset",
    "init",
    "pytorch"
]


def init():
    # monkey patch pandas
    pd.read_eto = read_eto
    # register Rikai resolver
    register_resolver()
    # Suppress Rikai info output
    logger.setLevel(logging.WARNING)
    # Add wait/check status methods
    patch_jobs_client()
