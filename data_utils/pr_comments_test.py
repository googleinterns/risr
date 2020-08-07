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
from unittest.mock import patch
import pr_comments


class PrCommentsTest(unittest.TestCase):
    """ PR Comments test class. """

    @patch("os.path.isfile")
    def test_get_comments_no_file(self, mock_results):
        """ Test to check missing file will raise exception. """
        mock_results.return_value = False
        self.assertFalse(os.path.isfile("data/repos.csv"))
        with self.assertRaises(Exception):
            pr_comments.main()

    def test_process_comment_no_author(self):
        """ Test to check comment processing when data has no author. """
        test_comment = {
            "author": None,
            "resourcePath": "test path",
            "createdAt": "test date",
            "body": "test body!"
        }
        host_usernames = set()
        repo_type = "test_type"
        self.assertEqual(pr_comments.process_comment(
            repo_type,
            host_usernames,
            test_comment
        )[2], "deleted-user")

    def test_process_comment_no_body(self):
        """ Test to check comment processing when data has no body. """
        test_comment = {
            "author": {"login": "test login"},
            "resourcePath": "test path",
            "createdAt": "test date",
            "body": ""
        }
        host_usernames = set()
        repo_type = "test_type"
        self.assertIsNone(pr_comments.process_comment(
            repo_type,
            host_usernames,
            test_comment
        ))

    def test_process_comment_not_host(self):
        """ Test to check comment processing when data is formatted
            correctly and author is not host. """
        test_comment = {
            "author": {"login": "test login"},
            "resourcePath": "test path",
            "createdAt": "test date",
            "body": "test body"
        }
        host_usernames = set()
        repo_type = "test type"
        comment_row = pr_comments.process_comment(
            repo_type,
            host_usernames,
            test_comment)
        self.assertEqual(comment_row[0], "test path")
        self.assertEqual(comment_row[1], "test date")
        self.assertEqual(comment_row[2], "test login")
        self.assertEqual(comment_row[3], "test body")
        self.assertEqual(comment_row[4], "test type")
        self.assertEqual(comment_row[5], False)

    def test_process_comment_is_host(self):
        """ Test to check comment processing when data is formatted
            correctly and author is host. """
        test_comment = {
            "author": {"login": "test login"},
            "resourcePath": "test path",
            "createdAt": "test date",
            "body": "test body"
        }
        host_usernames = {"test login"}
        repo_type = "test type"
        comment_row = pr_comments.process_comment(
            repo_type,
            host_usernames,
            test_comment)
        self.assertEqual(comment_row[0], "test path")
        self.assertEqual(comment_row[1], "test date")
        self.assertEqual(comment_row[2], "test login")
        self.assertEqual(comment_row[3], "test body")
        self.assertEqual(comment_row[4], "test type")
        self.assertEqual(comment_row[5], True)

    def test_process_comment_no_comment(self):
        """ Test to check comment processing when no comment is given. """
        host_usernames = set()
        repo_type = "test type"
        self.assertIsNone(pr_comments.process_comment(
            repo_type,
            host_usernames,
            None
        ))

    @patch("pr_comments.get_pr_comments")
    def test_get_pr_comments(self, mock_results):
        """ Test for getting test repository PR comments.

        This test uses a CSV with test repositories and checks if the
        output pull request comments CSV file is created correctly.
        The generated test files are deleted upon test completion.
        """

        # Mock results: first three comments from host1 in a pull request
        # pylint: disable=line-too-long
        mock_results.return_value = {
            "data": {
                "repository": {
                    "pullRequests": {
                        "nodes": [{
                            "comments": {
                                "nodes": []
                            },
                            "reviews": {
                                "nodes": [{
                                    "resourcePath":
                                    "/googleinterns/risr/pull/1#pullrequestreview-429318666",
                                    "body":
                                    "comment1",
                                    "createdAt": "2020-06-11T21:51:20Z",
                                    "author": {
                                        "login": "host1"
                                    },
                                    "comments": {
                                        "nodes": [{
                                            "resourcePath":
                                            "/googleinterns/risr/pull/1#discussion_r439090660",
                                            "body":
                                            "comment2",
                                            "createdAt":
                                            "2020-06-11T21:51:20Z",
                                            "author": {
                                                "login": "host1"
                                            }
                                        }, {
                                            "resourcePath":
                                            "/googleinterns/risr/pull/1#discussion_r439092264",
                                            "body":
                                            "comment3",
                                            "createdAt":
                                            "2020-06-11T21:53:36Z",
                                            "author": {
                                                "login": "host1"
                                            }
                                        }]
                                    }
                                }]
                            }
                        }]
                    }
                }
            }
        }

        pr_comments_path = "data/test_pr_comments.csv"

        if os.path.isfile(pr_comments_path):
            os.remove(pr_comments_path)
        self.assertFalse(os.path.isfile(pr_comments_path))

        sys.argv = ["repos.py", "test"]
        pr_comments.main()
        self.assertTrue(os.path.isfile(pr_comments_path))
        with open(pr_comments_path) as in_csv:
            reader = csv.DictReader(in_csv)
            for row in reader:
                self.assertTrue(
                    "/googleinterns/risr/pull/" in row["comment_path"])
                self.assertEqual("host1", row["author"])
                print(row["is_host"])
                self.assertTrue(row["is_host"])
        os.remove(pr_comments_path)


if __name__ == "__main__":
    unittest.main()
