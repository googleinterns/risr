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

""" Tests for the host module. """

import csv
import os
import sys
import unittest
from unittest.mock import patch
import host


class HostTest(unittest.TestCase):
    """ Host test class. """

    def test_no_args(self):
        """ Test to check if missing arguments will raise exception. """
        sys.argv = ["host.py"]
        with self.assertRaises(Exception):
            host.main()

    def test_missing_file(self):
        """ Test to check if missing file raises error. """
        sys.argv = ["host.py", "missing_file.csv"]
        with self.assertRaises(Exception):
            host.main()

    def test_get_hosts_from_teams_csv(self):
        """ Test to check that method gets hosts from teams CSV file. """
        # Create test teams CSV.
        teams_file = "data/test_teams.csv"
        with open(teams_file, "w", newline="") as out_csv:
            writer = csv.writer(out_csv)
            writer.writerow([
                "Github username 1",
                "Github username 2",
                "Start Date",
                "Team Number"
            ])
            row_two_hosts = ["host1", "host2", "date1", "team1"]
            row_only_first_host = ["host3", "", "date2", "team2"]
            row_only_second_host = ["", "host4", "date3", "team3"]
            writer.writerows([
                row_two_hosts,
                row_only_first_host,
                row_only_second_host
            ])

        host_dict = dict()
        correct_dict = {
            "host1": ["date1", "team1"],
            "host2": ["date1", "team1"],
            "host3": ["date2", "team2"],
            "host4": ["date3", "team3"],
        }
        host.get_hosts_from_teams_csv(teams_file, host_dict)
        self.assertDictEqual(host_dict, correct_dict)
        os.remove("data/test_teams.csv")

    def test_get_interns_from_repo_csv(self):
        """ Test to check that method gets interns from a CSV file. """
        repos_file = "data/test_repos.csv"
        intern_usernames = set()
        correct_set = {"googleinterns"}
        host.get_interns_from_repos_csv(repos_file, intern_usernames)
        self.assertSetEqual(intern_usernames, correct_set)

    @patch("host.get_pr_reviewers")
    def test_get_hosts_from_pr_reviews(self, mock_results):
        """ Test that method gets hosts from pull request reviews. """

        # Mock results to test all the supported query result cases.
        mock_results.return_value = {
            "data": {
                "repository": {
                    "pullRequests": {
                        "nodes": [{
                            "createdAt": "2020-06-26T22:26:47Z",
                            "timelineItems": {
                                "nodes": [
                                    {
                                        "requestedReviewer": {
                                            "login": "host_reviewer"
                                        }
                                    },
                                    {
                                        "requestedReviewer": {
                                            "login": "host_duplicate"
                                        }
                                    },
                                    {
                                        "requestedReviewer": {}
                                    },
                                    {
                                        "author": {
                                            "login": "host_author"
                                        }
                                    },
                                    {
                                        "author": {
                                            "login": "host_author"
                                        }
                                    },
                                    {
                                        "author": {
                                            "login": "intern"
                                        }
                                    },
                                    {},
                                    {}
                                ]
                            }
                        }]
                    }
                }
            }
        }

        repos_file = "data/test_repos.csv"
        host_dict = {
            "host_duplicate": ["date1", "team1"]
        }
        intern_usernames = {"intern"}
        host.get_hosts_from_pr_reviews(repos_file, host_dict, intern_usernames)
        correct_dict = {
            "host_duplicate": ["date1", "team1"],
            "host_reviewer": ["6/15/2020", "unknown"],
            "host_author": ["6/15/2020", "unknown"],
        }
        self.assertDictEqual(host_dict, correct_dict)

    def test_write_host_information(self):
        """ Test that host information is written correctly to CSV file. """
        hosts_file = "data/test_create_host_info.csv"
        host_dict = {
            "host1": ["date1", "team1"],
            "host2": ["date1", "team1"],
            "host3": ["date2", "team2"]
        }
        host.write_host_information(hosts_file, host_dict)
        with open(hosts_file, newline="") as in_csv:
            reader = csv.reader(in_csv)
            self.assertEqual(next(reader), ["username", "start_date", "team"])
            self.assertEqual(next(reader), ["host1", "date1", "team1"])
            self.assertEqual(next(reader), ["host2", "date1", "team1"])
            self.assertEqual(next(reader), ["host3", "date2", "team2"])
        os.remove(hosts_file)


if __name__ == "__main__":
    unittest.main()
