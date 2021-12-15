import os
from unittest import mock

import pytest

from eto.util import Config


@pytest.fixture(autouse=True)
def mock_settings_env_vars(tmp_path):
    with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(tmp_path.absolute())}):
        yield


def test_config():
    Config.create_config("http://url", "token")
    conf = Config.load()
    assert conf["url"] == "http://url"
    assert conf["token"] == "token"
