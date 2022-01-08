"""API client and configuration"""
from typing import Optional
from urllib.parse import urlparse

from eto._internal.api.jobs_api import JobsApi
from eto._internal.api_client import ApiClient
from eto._internal.apis import DatasetsApi
from eto._internal.configuration import Configuration
from eto.config import Config


_LAZY_CLIENTS = {}


def get_api(api_name: str):
    """Return the OpenAPI client for this api_name

    Parameters
    ----------
    api_name: str
        "jobs", "datasets"
    """
    if _LAZY_CLIENTS.get(api_name) is None:
        client = _get_client()
        _LAZY_CLIENTS[api_name] = _create_api(api_name, client)
    return _LAZY_CLIENTS[api_name]


def _get_client() -> ApiClient:
    sdk_conf = Config.load()
    url = sdk_conf["url"]
    if url.endswith("/"):
        url = url[:-1]
    conf = Configuration(host=url)
    return ApiClient(
        configuration=conf,
        header_name="Authorization",
        header_value=f'Bearer {sdk_conf["token"]}',
    )


def _create_api(api_name, client):
    if api_name not in ["datasets", "jobs"]:
        raise NotImplementedError("Only datasets and jobs api supported")
    cls_map = {"datasets": DatasetsApi, "jobs": JobsApi}
    api = cls_map[api_name]
    return api(client)


def configure(
    account: Optional[str] = None,
    token: Optional[str] = None,
    use_ssl: bool = True,
    port: Optional[int] = None,
    tmp_workspace_path: Optional[str] = None,
):
    """One time setup to configure the SDK to connect to Eto API

    Parameters
    ----------
    account: str, default None
        Your Eto account name
    token: str, default None
        the api token. If omitted then will default to ETO_API_TOKEN
        environment variable
    use_ssl: bool, default True
        Whether to use an SSL-enabled connection
    port: int, default None
        Optional custom port to connect on
    tmp_workspace_path: Optional[str]
        The tmp workspace that new datasets will be written to.
        Must be accessible by Eto.
    """
    url = None
    if account is not None:
        url = _get_account_url(account, use_ssl, port)
    url = url or Config.ETO_HOST_URL
    token = token or Config.ETO_API_TOKEN
    if url is None:
        raise ValueError("Please provide the host url for the Eto API")
    if token is None:
        raise ValueError("Please provide the API token for the Eto API")
    o = urlparse(url)
    if o.scheme is None:
        raise ValueError("No scheme was found in url")
    if o.netloc is None:
        raise ValueError("Host location was empty in the url")
    Config.create_config(url, token, tmp_workspace_path)
    _LAZY_CLIENTS.clear()


def _get_account_url(account, use_ssl, port):
    scheme = "https" if use_ssl else "http"
    url = f"{scheme}://{account}.eto.ai"
    if port is not None:
        url = url + f":{port}"
    return url
