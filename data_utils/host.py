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
from query import run_query


def get_pr_reviewers(name, owner):
    """ Gets the reviewer usernames for a particular repository.

    This method processes the results from the Github PAI query.

    Args:
        name: A string containing the repository name.
        owner: A string containing the repository owner.

    Returns:
        A JSON object with the pull request reviewer information.
    """

    query = f"""{{
        repository(name: "{name}", owner: "{owner}") {{
            pullRequests(first: 5) {{
                nodes {{
                    resourcePath
                    author {{
                        login
                    }}
                    timelineItems(first: 100) {{
                        nodes {{
                            ... on ReviewRequestedEvent {{
                                requestedReviewer {{
                                    ... on User {{
                                        login
                                    }}
                                }}
                            }}
                            ... on PullRequestReview {{
                                author {{
                                    login
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}"""

    return run_query(query)


def process_reviewer_query_results(result, host_dict, intern_usernames):
    """ Processes the query results for the reviewer usernames.

    Updates host_dict if new host usernames are found. Assumes that reviewers
    in starter projects are hosts.

    Args:
        result: The results from the query.
        host_dict: Dictionary containing host information.
        intern_usernames: Set of known intern usernames.

    Returns:
        None.
    """

    try:
        pull_requests = (result["data"]["repository"]["pullRequests"]["nodes"])
    except:
        raise Exception(
            "Query results for reviewers does not have a structure that is"
            " currently supported by RISR.")

    for pull_request in pull_requests:
        reviewers = pull_request["timelineItems"]["nodes"]
        for reviewer in reviewers:
            if not reviewer:
                continue
            if "requestedReviewer" in reviewer:
                host = reviewer["requestedReviewer"]
            if "author" in reviewer:
                host = reviewer["author"]
            # Special case in which host account has been deleted
            try:
                host_username = host["login"]
            except KeyError:
                continue

            # Check if host is already in dictionary and if intern reviewed
            # their own pull request.
            if host_username not in host_dict and \
                host_username not in intern_usernames:
                # Start date and team number are unknown in this case.
                host_dict[host_username] = ["unknown", "unknown"]


def main():
    """ Saves host usernames from STEP teams CSV.

    Expects file path to STEP teams CSV to be provided in the command
    line arguments.

    host_usernames.csv is created to store the host usernames, intern start
    date, and team number from the STEP teams CSV.
    """

    try:
        teams_file = sys.argv[1]
    except:
        raise Exception("Usage: host.py <STEP teams CSV>")

    if not os.path.isfile(teams_file):
        raise Exception("The CSV for the Github usernames does not exist.")

    host_dict = dict()

    # Get host information from the STEP team CSV
    with open(teams_file, newline="") as in_csv:
        reader = csv.DictReader(in_csv)
        for row in reader:
            start_date = row["Start Date"]
            team = row["Team Number"]
            host1 = row["Github username 1"]
            host2 = row["Github username 2"]
            if host1:
                host_dict[host1] = [start_date, team]
            if host2:
                host_dict[host2] = [start_date, team]

    # Store list of intern usernames based on owners of starter project
    # repositories.
    intern_usernames = set()

    # Check starter repositories for users that approved pull requests
    with open("data/repos.csv", newline="") as in_csv:
        reader = csv.DictReader(in_csv)
        for row in reader:
            if row["repo_type"] == "capstone":
                continue
            intern_usernames.add(row["owner"])
            query_results = get_pr_reviewers(row["name"], row["owner"])
            process_reviewer_query_results(
                query_results,
                host_dict,
                intern_usernames
            )


    with open("data/host_usernames.csv", "w", newline="") as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(["username", "start_date", "team"])
        for host in host_dict:
            writer.writerow([host, host_dict[host][0], host_dict[host][1]])


if __name__ == "__main__":
    main()
