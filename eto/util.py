"""Utility functions"""
import configparser
import os
import pathlib
from functools import wraps
from typing import Optional
from urllib.parse import ParseResult, urlparse


class Config:
    @classmethod
    def load(cls):
        """Load the default profile from XDG_CONFIG_HOME/eto/eto.conf"""
        config_file = get_config_file()
        if not config_file.exists():
            raise ValueError(
                "Please run eto.configure(...) first to "
                "configure your Eto url and credentials"
            )
        parser = configparser.ConfigParser()
        parser.read(str(config_file.absolute()))
        return parser["DEFAULT"]

    @classmethod
    def create_config(cls, url: str, token: Optional[str]):
        """Create config file at XDG_CONFIG_HOME/eto/eto.conf"""
        config_file = get_config_file()
        parser = configparser.ConfigParser()
        parser["DEFAULT"] = {"url": url, "token": token}
        with config_file.open("w") as cf:
            parser.write(cf)


def get_config_file():
    config_home = os.environ.get("XDG_CONFIG_HOME", "~/.config")
    config_dir = pathlib.Path(config_home).expanduser() / "eto"
    os.makedirs(config_dir, exist_ok=True)
    return config_dir / "eto.conf"


def get_dataset_ref_parts(qualified_name: str):
    if "." in qualified_name:
        project_id, dataset_id = qualified_name.rsplit(".", 1)
    else:
        project_id, dataset_id = None, qualified_name
    return project_id, dataset_id


def add_method(cls):
    """Add a method to an existing class"""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        setattr(cls, func.__name__, wrapper)
        return func

    return decorator
