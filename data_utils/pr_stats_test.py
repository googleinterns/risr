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

""" Tests for the pr_stats module. """

import csv
import os
import sys
import unittest
from unittest.mock import patch
import pr_stats


class PrStatsTest(unittest.TestCase):
    """ Repos test class. """

    def test_get_comments_no_file(self):
        """ Test to check if unsupported arguments will raise exception. """
        sys.argv = ["repos.py", "repo_type"]
        self.assertFalse(os.path.isfile("data/repo_type.csv"))
        with self.assertRaises(Exception):
            pr_stats.main()

    @patch("pr_stats.get_pr_stats")
    def test_get_pr_stats(self, mock_results):
        """ Test for getting test repository PR statistics.

        This test uses a CSV with test repositories and checks if the
        output pull request statistics CSV file is created correctly.
        The generated test files are deleted upon test completion.
        """

        # Mock results: pull requests for RISR repository.
        # pylint: disable=line-too-long
        mock_results.return_value = [
            {
                "resourcePath": "/googleinterns/risr/pull/1",
                "number": 1,
                "createdAt": "2020-06-11T20:54:31Z",
                "closedAt": "2020-06-12T19:36:08Z",
                "deletions": 0,
                "additions": 653,
                "comments": {
                    "totalCount": 0
                },
                "reviews": {
                    "nodes": [{
                        "body": "text1",
                        "comments": {
                            "totalCount": 3
                        }
                    }, {
                        "body": "",
                        "comments": {
                            "totalCount": 1
                        }
                    }, {
                        "body":
                        "text2",
                        "comments": {
                            "totalCount": 2
                        }
                    }, {
                        "body": "text3",
                        "comments": {
                            "totalCount": 2
                        }
                    }]
                }
            }, {
                "resourcePath": "/googleinterns/risr/pull/2",
                "number": 2,
                "createdAt": "2020-06-12T22:01:36Z",
                "closedAt": "2020-06-24T16:30:31Z",
                "deletions": 48,
                "additions": 631,
                "comments": {
                    "totalCount": 0
                },
                "reviews": {
                    "nodes": [{
                        "body": "",
                        "comments": {
                            "totalCount": 1
                        }
                    }, {
                        "body":
                        "text4",
                        "comments": {
                            "totalCount": 0
                        }
                    }]
                }
            }, {
                "resourcePath": "/googleinterns/risr/pull/3",
                "number": 3,
                "createdAt": "2020-06-24T16:36:50Z",
                "closedAt": "2020-06-24T20:25:02Z",
                "deletions": 19,
                "additions": 61,
                "comments": {
                    "totalCount": 1
                },
                "reviews": {
                    "nodes": [{
                        "body": "text5",
                        "comments": {
                            "totalCount": 2
                        }
                    }, {
                        "body": "",
                        "comments": {
                            "totalCount": 1
                        }
                    }, {
                        "body": "",
                        "comments": {
                            "totalCount": 1
                        }
                    }, {
                        "body": "",
                        "comments": {
                            "totalCount": 0
                        }
                    }]
                }
            }, {
                "resourcePath": "/googleinterns/risr/pull/4",
                "number": 4,
                "createdAt": "2020-06-26T22:26:47Z",
                "closedAt": None,
                "deletions": 32,
                "additions": 392,
                "comments": {
                    "totalCount": 0
                },
                "reviews": {
                    "nodes": []
                }
            }]

        pr_stats_path = "data/test_pr_stats.csv"

        if os.path.isfile(pr_stats_path):
            os.remove(pr_stats_path)
        self.assertFalse(os.path.isfile(pr_stats_path))

        sys.argv = ["repos.py", "test"]
        pr_stats.main()
        self.assertTrue(os.path.isfile(pr_stats_path))
        with open(pr_stats_path) as in_csv:
            reader = csv.DictReader(in_csv)
            self.assertGreater(len(list(reader)), 1)
            for i, row in enumerate(reader, 1):
                self.assertTrue("/googleinterns/risr/pull/" in row["pr_path"])
                self.assertEqual(row["pr_number"], i)
        os.remove(pr_stats_path)


if __name__ == "__main__":
    unittest.main()
