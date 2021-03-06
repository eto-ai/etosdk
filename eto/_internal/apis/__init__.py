# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from .api.accounts_api import AccountsApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from eto._internal.api.accounts_api import AccountsApi
from eto._internal.api.datasets_api import DatasetsApi
from eto._internal.api.insight_api import InsightApi
from eto._internal.api.jobs_api import JobsApi
from eto._internal.api.model_api import ModelApi
from eto._internal.api.query_api import QueryApi
