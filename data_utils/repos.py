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

""" Module for retrieving intern repositories. """

import csv
import sys
import os
from query import run_query


def get_repos_after(repo_query, cursor):
    """Gets the first 100 repositories after a cursor for a given query.

    This is necessary because GraphQL uses pagination, so only 100 results
    can be retrieved at one time.

    Args:
        repo_query: A string containing the query to find repositories.
        cursor: A string containing a cursor used for GraphQL pagination.

    Returns:
        A JSON object with the pull request comment information.
    """

    query = """{{
        search(
            first: 100,
            {after}
            query: {repo_query},
            type: REPOSITORY) {{
            repositoryCount
            edges {{
                cursor
                node {{
                    ... on Repository {{
                        owner {{
                            login
                        }}
                        name
                        createdAt
                        pullRequests {{
                            totalCount
                        }}
                    }}
                }}
            }}
        }}
    }}"""

    # Modify the search query to include a cursor if necessary.
    after = ""
    if cursor != "":
        after = f"""after: "{cursor}","""
    return run_query(query.format(after=after, repo_query=repo_query))


def process_query_results(writer, result, repo_type):
    """ Processes the query results for the repository search.

    Uses the writer to record the repository information.

    Args:
        writer: CSV writer to record the data in a CSV file.
        result: the results from the query.
        repo_type: the repository type.

    Returns:
        str. A string containing the cursor of the last search result, or
            an empty string if there are no results after the current cursor.
    """
    try:
        repositories = result["data"]["search"]["edges"]
    except:
        raise Exception(
            "Query results for repositories does not have a structure that is"
            " currently supported by RISR.")

    if not repositories:
        return ""

    for repo in repositories:
        writer.writerow([
            repo["node"]["owner"]["login"], repo["node"]["name"],
            repo["node"]["createdAt"],
            repo["node"]["pullRequests"]["totalCount"],
            repo_type
        ])

    return repositories[-1]["cursor"]


def query_generator(search="", loc="", org="", created="", sort=""):
    """ Generates a query for repository search based on input parameters.

    Args:
        search: the string that the query is looking for.
        loc: where the query should look for the search string.
        org: the repository that contains the repository.
        created: the date range for repository creation that is considered.
        sort: the order in which results are sorted.

    Returns:
        Query string for the "get_repos_after" function.
    """
    param_list = [search, loc, org, created, sort]
    query_str = " ".join(list(filter(None, param_list)))
    return f"""\"{query_str}\""""


def get_query_from_repo_type(repo_type):
    """ Calls query_generator with parameters for the specified repository type.

    Args:
        type: the string with the repository type. Currently supports "starter",
        "capstone", and "test" (for testing purposes).

    Returns:
        Query string for the repository type.
    """

    repo_query = ""
    if repo_type == "starter":
        # This query looks for a specific string in a repository README.md file.
        repo_query = query_generator(
            search="git clone https://github.com/googleinterns/step.git",
            loc="in:readme",
            sort="sort:created-asc")

    elif repo_type == "capstone":
        # This query follows the STEP capstone repository naming conventions
        # and creation dates.
        repo_query = query_generator(search="step 2020",
                                     loc="in:name",
                                     org="googleinterns",
                                     created="created:>2020-06-17",
                                     sort="sort:created-asc")

    elif repo_type == "test":
        # Look for the RISR repository.
        repo_query = query_generator(search="risr",
                                     loc="in:name",
                                     org="googleinterns")

    return repo_query


def main():
    """Retrieves all the STEP intern repos and stores them in a CSV file.

    The intern repos retrieved depend on command line arguments. Repositories
    of different types are stored in different CSV files. Current supported
    repository types are "starter" and "capstone".

    repos.csv has the following columns:
        owner: The STEP intern Github username.
        name: The repository name.
        created: The time and date that the repository was created.
        pr_count: The number of pull requests in the repository.
        repo_type: The type of repository.
    """

    arg_count = len(sys.argv)
    supported_types = {"test", "starter", "capstone"}

    # Check if there are arguments that specify repository types.
    if arg_count == 1:
        raise Exception("Usage: repos.py <repository type>...")

    repo_types = sys.argv[1:]

    if not set(repo_types).issubset(supported_types):
        raise Exception("Arguments contain unsupported repository type.")

    os.makedirs("data", exist_ok=True)

    out_csv_path = "data/repos.csv"

    # Create a different file for testing.
    if repo_types == ["test"]:
        out_csv_path = "data/test_repos.csv"

    with open(out_csv_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "owner",
            "name",
            "created",
            "pr_count",
            "repo_type"
        ])
        for repo_type in repo_types:
            repo_query = get_query_from_repo_type(repo_type)
            cur_cursor = ""
            while True:
                query_results = get_repos_after(repo_query, cur_cursor)
                next_cursor = process_query_results(
                    writer,
                    query_results,
                    repo_type
                )
                if next_cursor == "":
                    break
                cur_cursor = next_cursor


if __name__ == "__main__":
    main()
