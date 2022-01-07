import configparser
import os
import pathlib
from typing import Optional
from urllib.parse import urlparse


class Config:
    @classmethod
    def load(self):
        """Load the default profile from XDG_CONFIG_HOME/eto/eto.conf"""
        config_home = os.environ.get("XDG_CONFIG_HOME", "~/.config")
        config_dir = pathlib.Path(config_home).expanduser() / "eto"
        conf_file = config_dir / "eto.conf"
        if not conf_file.exists():
            raise ValueError(
                "Please run eto.configure(...) first to "
                "configure your Eto url and credentials"
            )
        parser = configparser.ConfigParser()
        parser.read(str(conf_file.absolute()))
        return parser["DEFAULT"]

    @classmethod
    def create_config(
        cls,
        url: str,
        token: Optional[str] = None,
        tmp_workspace_path: Optional[str] = None,
    ):
        """Create config file at XDG_CONFIG_HOME/eto/eto.conf"""
        config_home = os.environ.get("XDG_CONFIG_HOME", "~/.config")
        config_dir = pathlib.Path(config_home).expanduser() / "eto"
        os.makedirs(config_dir, exist_ok=True)
        config_file = config_dir / "eto.conf"
        parser = configparser.ConfigParser()
        parsed = urlparse(tmp_workspace_path)
        scheme = parsed.scheme
        if not scheme:
            os.makedirs(tmp_workspace_path, exist_ok=True)
        parser["DEFAULT"] = {
            "url": url,
            "token": token,
            "tmp_workspace_path": tmp_workspace_path,
        }
        with config_file.open("w") as cf:
            parser.write(cf)

    ETO_HOST_URL = os.environ.get("ETO_HOST_URL", None)

    ETO_API_TOKEN = os.environ.get("ETO_API_TOKEN", None)
