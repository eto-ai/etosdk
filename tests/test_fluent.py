import os
from unittest import mock

import pytest

import eto
from eto.config import Config
from eto.fluent import _get_api
from eto.internal.api.datasets_api import DatasetsApi


@pytest.fixture(autouse=True)
def mock_settings_env_vars(tmp_path):
    with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(tmp_path.absolute())}):
        yield


def test_configure():
    eto.configure('http://host', 'token')
    conf = Config.load()
    assert conf['url'] == 'http://host'
    assert conf['token'] == 'token'


def test_get_api():
    eto.configure('http://host', 'token')
    api = _get_api('datasets')
    assert isinstance(api, DatasetsApi)
    assert api.api_client.configuration.host == 'http://host'
