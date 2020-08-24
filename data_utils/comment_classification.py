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

""" Module for code review comment classification. """

import csv
import os
import random
import sys


def main():
    """" Creates training dataset with 200 host code review comments.

    The 200 comments from hosts are selected at random.

    Args:
        comments_file: CSV containing all code review comments.
    """

    if len(sys.argv) == 1:
        comments_file = "data/pr_comments.csv"
        training_file = "data/training_comments.csv"
    else:
        if sys.argv[1] == "test":
            comments_file = "data/test_pr_comments.csv"
            training_file = "data/test_training_comments.csv"
        else:
            raise Exception("Invalid command line argument.")

    if not os.path.isfile(comments_file):
        raise Exception("The CSV for code review comments does not exist.")

    # Uncomment if deterministic behavior is desired.
    # random.seed(10)

    with open(comments_file, newline="") as in_csv, \
         open(training_file, "w", newline="") as out_csv:
        reader = csv.reader(in_csv)
        writer = csv.writer(out_csv)
        headers = next(reader)
        host_comments = [row for row in reader if row[5] == "True"]
        num_comments = min(200, len(host_comments))
        training_comments = random.choices(host_comments, k=num_comments)
        writer.writerow(headers)
        writer.writerows(training_comments)


if __name__ == "__main__":
    main()
