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

""" Module for retrieving pull request statistics. """

import csv
import os
import sys
from query import run_query


def get_pr_stats(name, owner):
    """ Gets the pull request statistics from a particular repository.

    This function processes the results from the Github API query.

    Args:
        name: A string containing the repository name.
        owner: A string containing the repository owner.

    Returns:
        A JSON object with the pull request statistics information.
    """

    query = f"""{{
        repository(name: "{name}", owner: "{owner}") {{
            pullRequests(first: 50) {{
                nodes {{
                    resourcePath
                    number
                    createdAt
                    closedAt
                    deletions
                    additions
                    comments {{
                        totalCount
                    }}
                    reviews(first: 50) {{
                        nodes {{
                            body
                            comments {{
                                totalCount
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}"""

    return run_query(query)


def process_stats_query_results(writer, result):
    """ Processes the query results for pull request statistics.

    Uses the writer to record the pull request statistics information.

    Args:
        writer: CSV writer to record the data in a CSV file.
        result: the results from the query.

    Returns:
        None.
    """
    try:
        pull_requests = result["data"]["repository"]["pullRequests"]["nodes"]
    except:
        raise Exception(
            "Query results for PR statistics does not have a structure that is"
            " currently supported by RISR.")

    for pull_request in pull_requests:
        total_comments = pull_request["comments"]["totalCount"]
        for review in pull_request["reviews"]["nodes"]:
            if review["body"] != "" and review:
                total_comments += 1
            total_comments += review["comments"]["totalCount"]
        writer.writerow([
            pull_request["resourcePath"], pull_request["number"],
            pull_request["createdAt"], pull_request["closedAt"],
            total_comments,
            pull_request["deletions"] + pull_request["additions"]
        ])


def main():
    """ Retrieves pull request statistics for intern repositories.

    The pull requests retrieved depend on command line arguments. Repositories
    of different types are stored in different CSV files. Current supported
    repository types are "starter" and "capstone".

    <repo_type>_pr_stats.csv has the following columns:
        pr_path: The resource path to the pull request.
        pr_number: The pull request number.
        created: The date and time that the PR was created.
        closed: The date and time that the PR was closed.
        total_comments: The total number of comments for a pull request.
        pr_lines_changed: The number of lines of code that were changed in a
            pull request.
    """

    try:
        repo_type = sys.argv[1]
    except:
        raise Exception("Usage: pr_stats.py <repository type>")

    repo_csv = f"data/{repo_type}_repos.csv"

    if not os.path.isfile(repo_csv):
        raise Exception(
            f"The CSV for {repo_type} repositories does not exist.")

    with open(repo_csv, newline="") as in_csv, \
            open(f"data/{repo_type}_pr_stats.csv", "w", newline="") as out_csv:
        reader = csv.DictReader(in_csv)
        writer = csv.writer(out_csv)
        writer.writerow([
            "pr_path", "pr_number", "created", "closed", "total_comments",
            "pr_lines_changed"
        ])
        for row in reader:
            query_results = get_pr_stats(row["name"], row["owner"])
            process_stats_query_results(writer, query_results)


if __name__ == "__main__":
    main()
