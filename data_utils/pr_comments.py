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

""" Module for retrieving pull request comments. """

import csv
import os
import sys
from query import run_query


def get_pr_comments(name, owner):
    """ Gets the pull request comments from a particular repository.

    This function fetches the results from the Github API query.

    Args:
        name: A string containing the repository name.
        owner: A string containing the repository owner.

    Returns:
        A JSON object with the pull request comment information.
    """

    query = f"""{{
        repository(name: "{name}", owner: "{owner}") {{
            pullRequests(first: 20) {{
                nodes {{
                    comments(first: 20) {{
                        nodes {{
                            resourcePath
                            body
                            createdAt
                            author {{
                                login
                            }}
                        }}
                    }}
                    reviews(first: 20) {{
                        nodes {{
                            resourcePath
                            body
                            createdAt
                            author {{
                                login
                            }}
                            comments(first: 20) {{
                                nodes {{
                                    resourcePath
                                    body
                                    createdAt
                                    author {{
                                        login
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}"""

    return run_query(query)


def process_comment_query_results(writer, result, repo_type, host_usernames):
    """ Processes the query results for pull request comments.

    Uses the writer to record the pull request comment information.

    Args:
        writer: CSV writer to record the data in a CSV file.
        result: The results from the query.
        repo_type: A string containing the repository type.
        host_usernames: A set containing all known host usernames.

    Returns:
        None.
    """
    try:
        pull_requests = result["data"]["repository"]["pullRequests"]["nodes"]
    except:
        raise Exception(
            "Query results for PR comments does not have a structure that is"
            " currently supported by RISR.")

    for pull_request in pull_requests:
        for pr_comment in pull_request["comments"]["nodes"]:
            comment_row = process_comment(
                repo_type,
                host_usernames,
                pr_comment)
            if comment_row:
                writer.writerow(comment_row)

        for review in pull_request["reviews"]["nodes"]:
            comment_row = process_comment(
                repo_type,
                host_usernames,
                review)
            if comment_row:
                writer.writerow(comment_row)
            for review_comment in review["comments"]["nodes"]:
                comment_row = process_comment(
                    repo_type,
                    host_usernames,
                    review_comment)
                if comment_row:
                    writer.writerow(comment_row)


def process_comment(repo_type, host_usernames, comment):
    """ Helper function to process a comment.

    This function processes the comment JSON to get the comment path,
    creation date, comment author, and comment text.

    Args:
        repo_type: The repository type.
        host_usernames: A set containing all known host usernames.
        comment: The comment node retrieved from the API.

    Returns:
        List of strings that contains the comment data.
    """

    if comment and comment["body"] != "":
        # For the special case where the author has been deleted
        if not comment["author"]:
            comment["author"] = {"login": "deleted-user"}

        is_host = comment["author"]["login"] in host_usernames

        return [
            comment["resourcePath"], comment["createdAt"],
            comment["author"]["login"], comment["body"],
            repo_type, is_host
        ]
    return None


def main():
    """ Retrieves the comments in pull requests for intern repositories.

    pr_comments.csv has the following columns:
        comment_path: The resource path to the comment.
        created: The date and time that the comment was created.
        author: The Github username of the comment author.
        comment: The text in the comment.
        repo_type: The type of repository that the comment was made in.
        is_host: Boolean that indicates if author is a host.
    """
    arg_count = len(sys.argv)

    # If no extra arguments are given, then get pull request comments from
    # all repositories (capstone and starter).
    if arg_count == 1:
        comment_csv = "data/pr_comments.csv"
        repo_csv = "data/repos.csv"
        host_csv = "data/host_info.csv"
    else:
        # If in testing mode, then use testing files.
        if sys.argv[1] == "test":
            comment_csv = "data/test_pr_comments.csv"
            repo_csv = "data/test_repos.csv"
            host_csv = "data/test_host_info.csv"

    if not os.path.isfile(repo_csv):
        raise Exception("The CSV for intern repositories does not exist.")

    host_usernames = set()
    with open(host_csv, newline="") as host_csv:
        reader = csv.DictReader(host_csv)
        for row in reader:
            host_usernames.add(row["username"])

    with open(repo_csv, newline="") as in_csv, \
         open(comment_csv, "w", newline="") as out_csv:
        reader = csv.DictReader(in_csv)
        writer = csv.writer(out_csv)
        writer.writerow([
            "comment_path",
            "created",
            "author",
            "comment",
            "repo_type",
            "is_host"
        ])
        for row in reader:
            query_results = get_pr_comments(row["name"], row["owner"])
            process_comment_query_results(
                writer,
                query_results,
                row["repo_type"],
                host_usernames)


if __name__ == "__main__":
    main()
