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

""" Tests for the pr_comments module. """

import csv
import os
import sys
import unittest
from data_utils import pr_comments


class PrCommentsTest(unittest.TestCase):
    """ PR Comments test class. """
    def test_get_comments_no_args(self):
        """ Test to check if missing arguments will raise exception. """
        sys.argv = ['repos.py']
        with self.assertRaises(Exception):
            pr_comments.main()

    def test_get_comments_no_file(self):
        """ Test to check if unsupported arguments will raise exception. """
        sys.argv = ['repos.py', 'repo_type']
        self.assertFalse(os.path.isfile("data/repo_type.csv"))
        with self.assertRaises(Exception):
            pr_comments.main()

    def test_process_comment_no_author(self):
        """ Test to check comment processing when data has no author. """
        test_comment = {
            'author': None,
            'resourcePath': 'test path',
            'createdAt': 'test date',
            'body': 'Looks good!'
        }
        self.assertEqual(
            pr_comments.process_comment(test_comment)[2], "deleted-user")

    def test_process_comment_no_body(self):
        """ Test to check comment processing when data has no body. """
        test_comment = {
            'author': {'login': 'test login'},
            'resourcePath': 'test path',
            'createdAt': 'test date',
            'body': ''
        }
        self.assertIsNone(pr_comments.process_comment(test_comment))

    def test_process_comment(self):
        """ Test to check comment processing when data is formatted
            correctly. """
        test_comment = {
            'author': {'login': 'test login'},
            'resourcePath': 'test path',
            'createdAt': 'test date',
            'body': 'test body'
        }
        comment_row = pr_comments.process_comment(test_comment)
        self.assertEqual(comment_row[0], 'test path')
        self.assertEqual(comment_row[1], 'test date')
        self.assertEqual(comment_row[2], 'test login')
        self.assertEqual(comment_row[3], 'test body')

    def test_process_comment_no_comment(self):
        """ Test to check comment processing when no comment is given. """
        self.assertIsNone(pr_comments.process_comment(None))

    def test_get_pr_comments(self):
        """ Test for getting test repository PR comments.

        This test generates a CSV with test repositories and checks if the
        output pull request comments CSV file is created correctly.
        The generated test files are deleted upon test completion.
        """
        test_data = [["name", "owner"], ["risr", "googleinterns"]]
        with open("data/test_repos.csv", "w", newline="") as out_csv:
            writer = csv.writer(out_csv)
            writer.writerows(test_data)

        pr_comments_path = "data/test_pr_comments.csv"

        if os.path.isfile(pr_comments_path):
            os.remove(pr_comments_path)
        self.assertFalse(os.path.isfile(pr_comments_path))

        sys.argv = ['repos.py', 'test']
        pr_comments.main()
        self.assertTrue(os.path.isfile(pr_comments_path))
        with open(pr_comments_path) as in_csv:
            reader = csv.DictReader(in_csv)
            self.assertGreater(len(list(reader)), 1)
            for row in reader:
                self.assertTrue(
                    "/googleinterns/risr/pull/" in row["comment_path"])
        os.remove(pr_comments_path)
        os.remove("data/test_repos.csv")


if __name__ == '__main__':
    unittest.main()
