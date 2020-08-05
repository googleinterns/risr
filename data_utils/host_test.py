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

    def test_output_csv_has_expected_columns(self):
        """ Test to check if output CSV has three columns. """
        sys.argv = ["host.py", "test_usernames.csv"]

        with open("test_usernames.csv", "w", newline="") as out_csv:
            writer = csv.writer(out_csv)
            writer.writerow([
                "Github username 1",
                "Github username 2",
                "Start Date",
                "Team Number"
            ])
            writer.writerow(["user1", "user2", "date1", "number1"])
            writer.writerow(["user3", "", "date2", "number2"])

        host.main()

        with open("data/host_usernames.csv", newline="") as in_csv:
            reader = csv.reader(in_csv)
            self.assertEqual(next(reader), ["username", "start_date", "team"])
            self.assertEqual(next(reader), ["user1", "date1", "number1"])
            self.assertEqual(next(reader), ["user2", "date1", "number1"])
            self.assertEqual(next(reader), ["user3", "date2", "number2"])

        os.remove("test_usernames.csv")


if __name__ == "__main__":
    unittest.main()
