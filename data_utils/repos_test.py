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
from data_utils import repos


class ReposTest(unittest.TestCase):
    """ Repos test class. """
    def test_argument_exception(self):
        """ Test to check if missing arguments will raise exception. """
        sys.argv = ['repos.py']
        with self.assertRaises(Exception):
            repos.main()

    def test_unsupported_repo(self):
        """ Test to check if unsupported arguments will raise exception. """
        sys.argv = ['repos.py', 'repo_type']
        with self.assertRaises(Exception):
            repos.main()

    def test_get_capstone_repos(self):
        """ Test to check if STEP capstone repository data is collected.

        This test checks if:
        - The output CSV file is created correctly.
        - If the number of capstone repositories is around 260 (the real
          number).
        - If all capstone repositories have the expected owner and name.
        """
        sys.argv = ['repos.py', 'capstone']
        if os.path.isfile("data/capstone_repos.csv"):
            os.remove("data/capstone_repos.csv")
        self.assertFalse(os.path.isfile("data/capstone_repos.csv"))
        repos.main()
        self.assertTrue(os.path.isfile('data/capstone_repos.csv'))
        with open('data/capstone_repos.csv') as in_csv:
            csv_line_count = sum(1 for line in in_csv)
            self.assertGreater(csv_line_count, 245)
            self.assertLess(csv_line_count, 265)
            reader = csv.DictReader(in_csv)
            for row in reader:
                self.assertEqual(row['owner'], "googleinterns")
                self.assertTrue('step' in row['name'])


if __name__ == '__main__':
    unittest.main()
