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
from datetime import datetime
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
            pullRequests(first: 100) {{
                nodes {{
                    participants(first: 10) {{
                        nodes {{
                            login
                        }}
                    }}
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
                    timelineItems(first: 100) {{
                        nodes {{
                            ... on PullRequestReview {{
                                state
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}"""

    result = run_query(query)
    try:
        pull_requests = result["data"]["repository"]["pullRequests"]["nodes"]
        return pull_requests
    except (KeyError, TypeError):
        print(f"PR statistics results for {owner}/{name} does not have a"
              "structure that is currently supported by RISR.")
        return []


def process_stats_query_results(writer, pull_requests, host_dict):
    """ Processes the query results for pull request statistics.

    Uses the writer to record the pull request statistics information.

    Args:
        writer: CSV writer to record the data in a CSV file.
        pull_requests: the results from the query.
        host_dict: dictionary with host logins as keys and start dates as
                   values.

    Returns:
        None.
    """

    for pull_request in pull_requests:
        participants = pull_request["participants"]["nodes"]
        start_date = "unknown"
        for user in participants:
            # Special case in which host account has been deleted
            try:
                cur_username = user["login"]
            except (TypeError, KeyError):
                continue
            if cur_username in host_dict:
                start_date = host_dict[cur_username]
                break
        total_comments = pull_request["comments"]["totalCount"]
        for review in pull_request["reviews"]["nodes"]:
            if review["body"] != "" and review:
                total_comments += 1
            total_comments += review["comments"]["totalCount"]
        created_date = datetime.fromisoformat(pull_request["createdAt"][:-1])
        created_date = created_date.strftime("%-m/%-d/%Y")

        review_count = 0
        for item in pull_request["timelineItems"]["nodes"]:
            if not item:
                continue
            review_count += 1

        writer.writerow([
            pull_request["resourcePath"], pull_request["number"],
            start_date, created_date,
            total_comments, review_count,
            pull_request["deletions"] + pull_request["additions"]
        ])


def main():
    """ Retrieves pull request statistics for intern repositories.

    The pull requests retrieved depend on command line arguments. If there
    are no arguments, statistics for "starter" and "capstone" repositories
    will be retrieved by default.

    <repo_type>_pr_stats.csv has the following columns:
        pr_path: The resource path to the pull request.
        pr_number: The pull request number.
        created: The date and time that the PR was created.
        closed: The date and time that the PR was closed.
        total_comments: The total number of comments for a pull request.
        pr_lines_changed: The number of lines of code that were changed in a
            pull request.
    """

    arg_count = len(sys.argv)

    # If no extra arguments are given, then get pull request comments from
    # all repositories (capstone and starter).
    if arg_count == 1:
        repo_csv = "data/repos.csv"
        stats_csv = "data/pr_stats.csv"
    else:
        # If in testing mode, then use testing files.
        if sys.argv[1] == "test":
            repo_csv = "data/test_repos.csv"
            stats_csv = "data/test_pr_stats.csv"
        else:
            raise Exception(f"Unsupported mode {sys.argv[1]}.")

    if not os.path.isfile(repo_csv):
        raise Exception("The CSV for repositories does not exist.")

    # Keep dictionary of known host - start date mappings.
    host_dict = dict()
    with open("data/host_info.csv", newline="") as in_csv:
        reader = csv.DictReader(in_csv)
        for row in reader:
            host_dict[row["username"]] = row["start_date"]


    with open(repo_csv, newline="") as in_csv, \
            open(stats_csv, "w", newline="") as out_csv:
        reader = csv.DictReader(in_csv)
        writer = csv.writer(out_csv)
        writer.writerow([
            "pr_path", "pr_number", "start_date", "created_date",
            "total_comments", "review_count", "pr_lines_changed"
        ])
        for row in reader:
            query_results = get_pr_stats(row["name"], row["owner"])
            process_stats_query_results(writer, query_results, host_dict)


if __name__ == "__main__":
    main()
