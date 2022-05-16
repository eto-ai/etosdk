"""Eto SDK Fluent API for managing models"""
from typing import Any, Optional

from rikai.spark.sql.codegen.mlflow_logger import MlflowLogger, KNOWN_FLAVORS

from eto.config import Config


class EtoMlflowLogger(MlflowLogger):

    def log_model(
        self,
        model: Any,
        artifact_path: str,
        schema: Optional[str] = None,
        registered_model_name: Optional[str] = None,
        customized_flavor: Optional[str] = None,
        model_type: Optional[str] = None,
        labels: Optional[dict] = None,
        **kwargs,
    ):
        import mlflow
        uri = _get_mlflow_tracking_uri()
        mlflow.set_tracking_uri(uri)
        super().log_model(model, artifact_path, schema, registered_model_name, customized_flavor,
                          model_type, labels, **kwargs)


def _get_mlflow_tracking_uri():
    conf = Config.load()
    url = conf["url"]
    if url.endswith("/"):
        url = url[:-1]
    return url + '/api/mlflow'


for flavor in KNOWN_FLAVORS:
    globals()[flavor] = EtoMlflowLogger(flavor)