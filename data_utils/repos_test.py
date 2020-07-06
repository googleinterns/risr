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

""" Tests for the repos module. """

import csv
import os
import sys
import unittest
from unittest.mock import patch
import repos


class ReposTest(unittest.TestCase):
    """ Repos test class. """

    def test_argument_exception(self):
        """ Test to check if missing arguments will raise exception. """
        sys.argv = ["repos.py"]
        with self.assertRaises(Exception):
            repos.main()

    def test_unsupported_repo(self):
        """ Test to check if unsupported arguments will raise exception. """
        sys.argv = ["repos.py", "repo_type"]
        with self.assertRaises(Exception):
            repos.main()

    def test_query_generator_parameters(self):
        """ Check if generated query has the correct parameters.

        query_1 should contain all parameters from params_1 and no parameters
        from params_2.
        query_2 should contail all parameters from params_2 and no parameters
        from params_1.
        Both queries should contain the shared_param string.
        """
        query_1 = repos.query_generator(search="test search",
                                        created="created:>test-date",
                                        sort="sort:test-order")
        query_2 = repos.query_generator(search="test search",
                                        loc="in:test-loc",
                                        org="org:test-org")
        params_1 = ["created:>test-date", "sort:test-order"]
        params_2 = ["in:test-loc", "org:test-org"]
        shared_param = "test search"

        self.assertTrue(all([param in query_1 for param in params_1]))
        self.assertTrue(all([param not in query_1 for param in params_2]))
        self.assertTrue(all([param in query_2 for param in params_2]))
        self.assertTrue(all([param not in query_2 for param in params_1]))
        self.assertTrue(shared_param in query_1 and shared_param in query_2)

    @patch("repos.get_repos_after")
    def test_repos_output(self, mock_results):
        """ Test to check the CSV output, given a set of query results.

        This test checks if:
        - The output CSV file is created correctly.
        - If the repository has the correct name and owner.
        """

        # Mock results: query results for the RISR repository.
        # Each item in the list corresponds to the results for one query.
        # pylint: disable=line-too-long
        mock_results.side_effect = [{
            "data": {
                "search": {
                    "repositoryCount":
                    1,
                    "edges": [{
                        "cursor": "Y3Vyc29yOjE=",
                        "node": {
                            "owner": {
                                "login": "googleinterns"
                            },
                            "name": "risr",
                            "createdAt": "2020-06-08T22:15:42Z",
                            "pullRequests": {
                                "totalCount": 4
                            }
                        }
                    }]
                }
            }
        }, {
            "data": {
                "search": {
                    "repositoryCount": 1,
                    "edges": []
                }
            }
        }]

        repos_path = "data/test_repos.csv"
        if os.path.isfile(repos_path):
            os.remove(repos_path)
        self.assertFalse(os.path.isfile(repos_path))

        sys.argv = ["repos.py", "test"]

        repos.main()
        self.assertTrue(os.path.isfile(repos_path))
        with open(repos_path) as in_csv:
            reader = csv.DictReader(in_csv)
            self.assertEqual(len(list(reader)), 1)
            for row in reader:
                self.assertEqual(row["owner"], "googleinterns")
                self.assertEqual(row["name"], "risr")


if __name__ == "__main__":
    unittest.main()
