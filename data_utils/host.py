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

""" Module for saving host usernames. """


import csv
import os
import sys

def main():
    """ Saves host usernames from STEP teams CSV.

    Expects file path to STEP teams CSV to be provided in the command
    line arguments.

    host_usernames.csv is created to store the host usernames, intern start
    date, and team number from the STEP teams CSV.
    """

    try:
        filename = sys.argv[1]
    except:
        raise Exception("Usage: host.py <STEP teams CSV>")

    if not os.path.isfile(filename):
        raise Exception("The CSV for the Github usernames does not exist.")

    with open(filename, newline="") as in_csv, \
         open("data/host_usernames.csv", "w", newline="") as out_csv:
        reader = csv.DictReader(in_csv)
        writer = csv.writer(out_csv)
        writer.writerow(["username", "start_date", "team"])
        for row in reader:
            start_date = row["Start Date"]
            team = row["Team Number"]
            if row["Github username 1"]:
                writer.writerow([row["Github username 1"], start_date, team])
            if row["Github username 2"]:
                writer.writerow([row["Github username 2"], start_date, team])


if __name__ == "__main__":
    main()
