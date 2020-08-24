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
from datetime import datetime
from query import run_query


def get_pr_reviewers(name, owner):
    """ Gets the reviewer usernames for a particular repository.

    This method processes the results from the Github API query. It looks
    for review requested and pull request review items in the pull request
    timeline, since those are generally associated with hosts.

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
                    createdAt
                    resourcePath
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

    start_dates = [
        "2020-05-18",
        "2020-06-15",
        "2020-07-06"
        ]

    start_dates = [datetime.fromisoformat(date) for date in start_dates]

    for pull_request in pull_requests:
        timeline_items = pull_request["timelineItems"]["nodes"]
        for review_item in timeline_items:
            if not review_item:
                continue
            if "requestedReviewer" in review_item:
                host = review_item["requestedReviewer"]
            if "author" in review_item:
                host = review_item["author"]

            # Special case in which host account has been deleted
            try:
                host_username = host["login"]
            except (TypeError, KeyError):
                continue

            # Check if host is already in dictionary and if intern reviewed
            # their own pull request.
            if host_username not in host_dict and \
                host_username not in intern_usernames:
                date_created = datetime.fromisoformat(pull_request["createdAt"][:-1])

                start_date = start_dates[0]
                for date in start_dates:
                    if date <= date_created:
                        start_date = date
                    else:
                        break

                start_date = start_date.strftime("%-m/%-d/%Y")

                # Team number is unknown in this case.
                host_dict[host_username] = [start_date, "unknown"]


def get_hosts_from_teams_csv(teams_file, host_dict):
    """ Gets host information from the internal STEP teams CSV file.

    Args:
        teams_file: File name for STEP teams CSV.
        host_dict: Dictionary to be updated with host information.
    """

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


def get_interns_from_repos_csv(repos_file, intern_usernames):
    """ Gets intern usernames from owners of starter project repositories.

    Args:
        repos_file: File name for repository CSV.
        intern_usernames: Set to be updated with intern usernames.
    """
    with open(repos_file, newline="") as in_csv:
        reader = csv.DictReader(in_csv)
        for row in reader:
            if row["repo_type"] == "capstone":
                continue
            intern_usernames.add(row["owner"])


def get_hosts_from_pr_reviews(repos_file, host_dict, intern_usernames):
    """ Gets host username based on pull request reviewers.

    Only checks starter project repositories because the capstone projects
    had a peer review component. Capstone repositories, which are made in the
    googleinterns organization, are ignored.

    The test repo_type is used for testing and refers to the RISR repository.
    Although RISR is owned by the googleinterns organization, it should not be
    skipped.

    Args.
        repos_file: File name for the repository CSV.
        host_dict: Dictionary to be updated with host information.
        intern_usernames: Set containing intern usernames.
    """
    with open(repos_file, newline="") as in_csv:
        reader = csv.DictReader(in_csv)
        for row in reader:
            if row["repo_type"] == "capstone":
                continue
            # Ignore repositories made in the googleinterns organization.
            if row["owner"] == "googleinterns" and row["repo_type"] != "test":
                continue
            query_results = get_pr_reviewers(row["name"], row["owner"])
            process_reviewer_query_results(
                query_results,
                host_dict,
                intern_usernames
            )


def write_host_information(hosts_file, host_dict):
    """ Writes host information to CSV file.

    Args:
        hosts_file: File name for host usernames CSV.
        host_dict: Dictionary containing host usernames, start dates,
            and team number.
    """
    with open(hosts_file, "w", newline="") as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(["username", "start_date", "team"])
        for host in host_dict:
            writer.writerow([host, host_dict[host][0], host_dict[host][1]])


def main():
    """ Saves host information from STEP teams CSV and pull request reviews.

    Expects file path to STEP teams CSV to be provided in the command
    line arguments.

    host_info.csv is created to store the host usernames, intern start
    date, and team number from the STEP teams CSV.
    """

    try:
        teams_file = sys.argv[1]
    except:
        raise Exception("Usage: host.py <STEP teams CSV>")

    if not os.path.isfile(teams_file):
        raise Exception("The CSV for the Github usernames does not exist.")

    repos_file = "data/repos.csv"
    hosts_file = "data/host_info.csv"

    host_dict = dict()
    get_hosts_from_teams_csv(teams_file, host_dict)

    intern_usernames = set()
    get_interns_from_repos_csv(repos_file, intern_usernames)

    get_hosts_from_pr_reviews(repos_file, host_dict, intern_usernames)

    write_host_information(hosts_file, host_dict)


if __name__ == "__main__":
    main()
