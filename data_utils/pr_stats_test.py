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
from datetime import datetime
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

    def test_calculate_week(self):
        """ Test to check that weeks are calculated correctly. """
        start_date1 = "05/12/2020"
        created_date1 = datetime.strptime("05/12/2020", "%m/%d/%Y")
        week1 = pr_stats.calculate_week(start_date1, created_date1)
        self.assertEqual(week1, 1)

        start_date2 = "05/12/2020"
        created_date2 = datetime.strptime("05/18/2020", "%m/%d/%Y")
        week2 = pr_stats.calculate_week(start_date2, created_date2)
        self.assertEqual(week2, 1)

        start_date3 = "05/12/2020"
        created_date3 = datetime.strptime("05/19/2020", "%m/%d/%Y")
        week3 = pr_stats.calculate_week(start_date3, created_date3)
        self.assertEqual(week3, 2)


    def test_get_start_date(self):
        """ Test to check if start dates are found correctly based on
            participants. """
        participants = [
            {
                "login": "user1"
            },
            {
                "login": "user2"
            },
            {
                "login": "user3"
            }
        ]

        host_dict = dict()
        repo_dates = dict()
        repo = "test_repo"
        start_date = pr_stats.get_start_date(
            participants, host_dict, repo_dates, repo)
        self.assertEqual(start_date, "unknown")

        host_dict["user3"] = "05/12/2020"
        start_date = pr_stats.get_start_date(
            participants, host_dict, repo_dates, repo)
        self.assertEqual(start_date, "05/12/2020")
        self.assertEqual(repo_dates[repo], "05/12/2020")


    @patch("pr_stats.get_pr_stats")
    def test_get_pr_stats(self, mock_results):
        """ Test for getting test repository PR statistics.

        This test uses a CSV with test repositories and checks if the
        output pull request statistics CSV file is created correctly.
        The generated test files are deleted upon test completion.
        """

        # Mock results: pull requests for RISR repository.
        # pylint: disable=line-too-long
        mock_results.return_value = {
            "data": {
                "repository": {
                    "nameWithOwner": "googleinterns/risr",
                    "pullRequests": {
                        "nodes": [{
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
                            },
                            "participants": {
                                "nodes": [
                                    {"host1": "05/12/2020"}
                                ]
                            },
                            "timelineItems": {
                                "nodes": [
                                    {},
                                    {},
                                    {},
                                    {
                                        "state": "CHANGES_REQUESTED"
                                    },
                                    {},
                                    {
                                        "state": "APPROVED"
                                    },
                                    {},
                                    {},
                                    {}
                                ]
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
                            },
                            "participants": {
                                "nodes": [
                                    {"host1": "05/12/2020"}
                                ]
                            },
                            "timelineItems": {
                                "nodes": [
                                    {},
                                    {},
                                    {},
                                    {
                                        "state": "CHANGES_REQUESTED"
                                    },
                                    {},
                                    {
                                        "state": "APPROVED"
                                    },
                                    {},
                                    {},
                                    {}
                                ]
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
                            },
                            "participants": {
                                "nodes": [
                                    {"host1": "05/12/2020"}
                                ]
                            },
                            "timelineItems": {
                                "nodes": [
                                    {},
                                    {},
                                    {},
                                    {
                                        "state": "CHANGES_REQUESTED"
                                    },
                                    {},
                                    {
                                        "state": "APPROVED"
                                    },
                                    {},
                                    {},
                                    {}
                                ]
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
                            },
                            "participants": {
                                "nodes": [
                                    {"host1": "05/12/2020"}
                                ]
                            },
                            "timelineItems": {
                                "nodes": [
                                    {},
                                    {},
                                    {},
                                    {
                                        "state": "CHANGES_REQUESTED"
                                    },
                                    {},
                                    {
                                        "state": "APPROVED"
                                    },
                                    {},
                                    {},
                                    {}
                                ]
                            }
                        }]
                    }
                }
            }
        }

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
                self.assertEqual(row["start_date"], "05/12/2020")
        os.remove(pr_stats_path)


if __name__ == "__main__":
    unittest.main()
