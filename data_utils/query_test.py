# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Tests for the query module. """

import os
import unittest
from data_utils import query


class QueryTest(unittest.TestCase):
    """ Query test class. """

    def test_run_query_repository(self):
        """ Test to get the googleinterns risr repository. """
        query_input = """{
            repository(name: "risr", owner: "googleinterns") {
                nameWithOwner
            }
        }"""
        name_with_owner = "googleinterns/risr"
        result = query.run_query(query_input)
        self.assertFalse('errors' in result.keys())
        self.assertEqual(result['data']['repository']['nameWithOwner'],
                         name_with_owner)

    def test_run_query_exception(self):
        """ Test to check if exception is raised when environment variable
        for the Github Personal Access Token is not set. """
        cur_github_pat = os.getenv('GITHUB_PAT')
        os.environ['GITHUB_PAT'] = ""
        with self.assertRaises(Exception):
            query.run_query("")
        os.environ['GITHUB_PAT'] = cur_github_pat

    def test_run_query_error(self):
        """ Test to check if incorrect queries get an error JSON object. """
        result = query.run_query("")
        self.assertTrue('errors' in result.keys())


if __name__ == '__main__':
    unittest.main()
