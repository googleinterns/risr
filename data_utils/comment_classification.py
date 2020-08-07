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


def create_training_dataset(comments_file):
	random.seed(10)
	training_file = "data/training_comments.csv"
	with open(comments_file, newline="") as in_csv, \
		 open(training_file, "w", newline="") as out_csv:
		reader = csv.reader(in_csv)
		writer = csv.writer(out_csv)
		# Ignore first row of comments CSV.
		header_row = next(reader)
		all_comments = list(reader)
		training_comments = random.choices(all_comments, k=200)
		writer.writerow(header_row)
		writer.writerows(training_comments)



def main():
	comments_file = "data/pr_comments.csv"
	if not os.path.isfile(comments_file):
		raise Exception("The CSV for code review comments does not exist.")
	create_training_dataset(comments_file)


if __name__ == "__main__":
    main()
