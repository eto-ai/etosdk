import os
from unittest import mock

import pandas as pd
import pytest
from rikai.torch.data import DataLoader

import eto
from eto.config import Config
from eto.fluent import _get_api
from eto.internal.api.datasets_api import DatasetsApi


@pytest.fixture(autouse=True)
def mock_settings_env_vars(tmp_path):
    with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(tmp_path.absolute())}):
        yield


def test_configure():
    eto.configure("http://host", "token")
    conf = Config.load()
    assert conf["url"] == "http://host"
    assert conf["token"] == "token"


def test_get_api():
    eto.configure("http://host", "token")
    api = _get_api("datasets")
    assert isinstance(api, DatasetsApi)
    assert api.api_client.configuration.host == "http://host"


def test_list_datasets():
    eto.configure()
    datasets = eto.list_datasets()
    assert len(datasets) == 1
    assert datasets[0]["project_id"] == "default"
    assert datasets[0]["dataset_id"] == "coco"


def test_get_dataset():
    eto.configure()
    d = eto.get_dataset("coco")
    assert d["project_id"] == "default"
    assert d["dataset_id"] == "coco"
    assert d["uri"] == "s3a://eto-public/datasets/coco"


def test_pandas_reader():
    eto.configure()
    df = pd.read_eto("coco", limit=10)
    assert len(df) == 10


def test_rikai_resolver():
    eto.configure()
    loader = DataLoader("coco")
    next(loader.__iter__())


def test_ingest_coco():
    eto.configure()
    job = eto.ingest_coco(
        "test",
        source={
            "image_dir": "s3://image_dir",
            "annotation": "s3://annotations",
            "extras": {"foo": "bar"},
        },
        partition="split",
    )
    assert job["id"] is not None
