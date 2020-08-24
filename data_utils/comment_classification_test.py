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

""" Tests for the comment_classification module. """

import csv
import os
import sys
import unittest
from unittest.mock import patch
import comment_classification


class CommentClassTest(unittest.TestCase):
    """ Comment classification test class. """

    @patch("os.path.isfile")
    def test_get_comments_no_file(self, mock_results):
        """ Test to check missing file will raise exception. """
        mock_results.return_value = False
        self.assertFalse(os.path.isfile("data/.csv"))
        with self.assertRaises(Exception):
            comment_classification.main()

    def test_get_only_host_comments(self):
        """ Test to check that generated CSV only has host comments. """
        sys.argv = ["comment_classification.py", "test"]
        test_file_path = "data/test_pr_comments.csv"
        with open(test_file_path, "w", newline="") as test_csv:
            writer = csv.writer(test_csv)
            header = [
                "comment_path",
                "created",
                "author",
                "comment",
                "repo_type",
                "is_host"
            ]
            writer.writerows([
                header,
                ["path1", "date1", "author1", "comment1", "type1", "True"],
                ["path2", "date2", "author2", "comment2", "type2", "False"],
                ["path3", "date3", "author3", "comment3", "type3", "True"],
                ["path4", "date4", "author4", "comment4", "type4", "False"],
                ["path5", "date5", "author5", "comment5", "type5", "False"],
                ["path6", "date6", "author6", "comment6", "type6", "True"]
            ])
        comment_classification.main()
        with open("data/test_training_comments.csv", newline="") as in_csv:
            reader = csv.DictReader(in_csv)
            num_rows = 0
            for row in reader:
                self.assertEqual(row["is_host"], "True")
                num_rows += 1
            self.assertEqual(num_rows, 3)
        os.remove(test_file_path)

if __name__ == "__main__":
    unittest.main()
