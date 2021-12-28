import os
from unittest import mock

import pandas as pd
import pytest
from rikai.torch.data import DataLoader

import eto
from eto.config import Config
from eto.fluent import _get_api
from eto._internal.api.datasets_api import DatasetsApi


@pytest.fixture(autouse=True)
def mock_settings_env_vars(tmp_path):
    with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(tmp_path.absolute())}):
        yield


def test_configure():
    eto.configure("account", "token")
    conf = Config.load()
    assert conf["url"] == "https://account.eto.ai"
    assert conf["token"] == "token"


def test_get_api():
    eto.configure("account", "token")
    api = _get_api("datasets")
    assert isinstance(api, DatasetsApi)
    assert api.api_client.configuration.host == "https://account.eto.ai"


def test_list_datasets():
    eto.configure()
    datasets = eto.list_datasets()
    assert len(datasets) == 1
    assert datasets.iloc[0].project_id == "default"
    assert datasets.iloc[0].dataset_id == "little_coco"


def test_get_dataset():
    eto.configure()
    d = eto.get_dataset("little_coco")
    assert d.project_id == "default"
    assert d.dataset_id == "little_coco"
    assert d.uri.endswith("little_coco")


def test_pandas_reader():
    eto.configure()
    df = pd.read_eto("little_coco", limit=10)
    assert len(df) == 10


def test_pandas_reader_with_columns():
    eto.configure()
    df = pd.read_eto("little_coco", columns=["image_id", "annotations"], limit=10)
    assert len(df) == 10
    assert (df.columns == ["image_id", "annotations"]).all()


def test_rikai_resolver():
    eto.configure()
    loader = DataLoader("little_coco")
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
    assert job.id is not None
    assert job.check_status() in ("created", "scheduled", "running")
    jobs = eto.list_jobs("default")
    assert len(jobs) > 0
    assert job.id in set([row.id for _, row in jobs.iterrows()])
    assert all([row.project_id == "default" for _, row in jobs.iterrows()])
    job.wait(1)
