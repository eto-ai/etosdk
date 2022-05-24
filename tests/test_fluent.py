import os
import uuid
from unittest import mock

import pandas as pd
import pytest
from rikai.pytorch.data import Dataset

import eto
from eto._internal.api.datasets_api import DatasetsApi
from eto.config import Config
from eto.fluent.client import get_api


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
    api = get_api("datasets")
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
    dataset = Dataset("little_coco")
    next(dataset.__iter__())


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


def test_to_eto():
    eto.configure()
    df = pd.read_eto("little_coco", limit=10)
    job = df.to_eto("new_coco", max_wait_sec=1)
    assert job.id is not None


def test_spark():
    import eto.spark

    eto.configure()
    (
        eto.spark.configure("spark.driver.memory", "2g").configure(
            "spark.executor.memory", "2g"
        )
    )
    spark = eto.spark.get_session()
    assert spark.conf.get("spark.driver.memory") == "2g"
    assert spark.conf.get("spark.executor.memory") == "2g"


@pytest.fixture(scope="session")
def resnet_model_uri(tmp_path_factory):
    import torch
    import torchvision

    tmp_path = tmp_path_factory.mktemp(str(uuid.uuid4()))
    resnet = torchvision.models.detection.fasterrcnn_resnet50_fpn(
        pretrained=True,
        progress=False,
    )
    model_uri = tmp_path / "resnet.pth"
    torch.save(resnet, model_uri)
    return model_uri


def test_log_model(resnet_model_uri):
    import mlflow
    import rikai
    import torch

    from eto.fluent.models import _get_mlflow_tracking_uri

    eto.configure()
    mlflow_tracking_uri = _get_mlflow_tracking_uri()
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    with mlflow.start_run():
        model = torch.load(resnet_model_uri)
        eto.pytorch.log_model(
            model,
            "artifact_path",
            "output_schema",
        )
        run_id = mlflow.active_run().info.run_id
        run = mlflow.get_run(run_id)
        tags = run.data.tags
        assert tags[rikai.mlflow.CONF_MLFLOW_ARTIFACT_PATH] == "artifact_path"
        assert tags[rikai.mlflow.CONF_MLFLOW_OUTPUT_SCHEMA] == "output_schema"
