"""
    A swagger API

    powered by Flasgger  # noqa: E501

    The version of the OpenAPI document: 0.0.1
    Generated by: https://openapi-generator.tech
"""


import unittest

import eto.internal
from eto.internal.api.jobs_api import JobsApi  # noqa: E501


class TestJobsApi(unittest.TestCase):
    """JobsApi unit test stubs"""

    def setUp(self):
        self.api = JobsApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_create_ingest_job(self):
        """Test case for create_ingest_job

        Create a dataset Ingestion job  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
