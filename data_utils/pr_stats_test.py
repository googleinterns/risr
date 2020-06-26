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
from data_utils import pr_stats


class PrStatsTest(unittest.TestCase):
    """ Repos test class. """

    def test_get_stats_no_args(self):
        """ Test to check if missing arguments will raise exception. """
        sys.argv = ['repos.py']
        with self.assertRaises(Exception):
            pr_stats.main()

    def test_get_comments_no_file(self):
        """ Test to check if unsupported arguments will raise exception. """
        sys.argv = ['repos.py', 'repo_type']
        self.assertFalse(os.path.isfile("data/repo_type.csv"))
        with self.assertRaises(Exception):
            pr_stats.main()

    def test_get_pr_stats(self):
        """ Test for getting test repository PR statistics.

        This test generates a CSV with test repositories and checks if the
        output pull request statistics CSV file is created correctly.
        The generated test files are deleted upon test completion.
        """
        test_data = [["name", "owner"],
                     ["risr", "googleinterns"]]
        with open("data/test_repos.csv", "w", newline="") as out_csv:
            writer = csv.writer(out_csv)
            writer.writerows(test_data)

        pr_stats_path = "data/test_pr_stats.csv"

        if os.path.isfile(pr_stats_path):
            os.remove(pr_stats_path)
        self.assertFalse(os.path.isfile(pr_stats_path))

        sys.argv = ['repos.py', 'test']
        pr_stats.main()
        self.assertTrue(os.path.isfile(pr_stats_path))
        with open(pr_stats_path) as in_csv:
            reader = csv.DictReader(in_csv)
            self.assertGreater(len(list(reader)), 1)
            for row in reader:
                self.assertTrue("/googleinterns/risr/pull/" in row["pr_path"])
        os.remove(pr_stats_path)
        os.remove("data/test_repos.csv")


if __name__ == '__main__':
    unittest.main()
