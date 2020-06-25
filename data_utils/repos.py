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
from data_utils.query import run_query


def get_repos_after(repo_query, cursor):
    """Gets the first 100 repositories after a cursor for a given query.

    This is necessary because GraphQL uses pagination, so only 100 results
    can be retrieved at one time.

    Args:
        repo_query: A string containing the query to find repositories.
        cursor: A string containing a cursor used for GraphQL pagination.

    Returns:
        str. A string containing the cursor of the last search result, or
        an empty string if there are no results after the current cursor.
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
    result = run_query(query.format(after=after, repo_query=repo_query))

    results = result['data']['search']['edges']
    if not results:
        return ""

    for result in results:
        main.writer.writerow([
            result['node']['owner']['login'], result['node']['name'],
            result['node']['createdAt'],
            result['node']['pullRequests']['totalCount']
        ])

    return results[-1]['cursor']


def main():
    """Retrieves all the STEP intern repos and stores them in a CSV file.

    The intern repos retrieved depend on command line arguments. Repositories
    of different types are stored in different CSV files. Current supported
    repository types are "starter" and "capstone".

    <repo_type>_repos.csv has the following columns:
        owner: The STEP intern Github username.
        name: The repository name.
        created: The time and date that the repository was created.
        pr_count: The number of pull requests in the repository.
    """

    try:
        repo_type = sys.argv[1]
    except:
        raise Exception("Usage: repos.py <repository type>")

    if repo_type == "starter":
        # Look for a specific string in a repository README.md file. Results are
        # sorted according to the date the repository was created.
        repo_query = """\"
            git clone https://github.com/googleinterns/step.git
            in:readme
            sort:created-asc
        \""""

    elif repo_type == "capstone":
        # Look for repositories that match the string "step 2020" and were
        # created within the "googleinterns" organization after 06/17/2020.
        # This query follows the STEP capstone repository naming conventions
        # and creation dates. Results are sorted according to the date the
        # repository was created.
        repo_query = """\"
            step 2020
            in:name
            org:googleinterns
            created:>2020-06-17
            sort:created-asc
        \""""

    else:
        raise Exception(repo_type, "is an unsupported repository type.")

    os.makedirs('data', exist_ok=True)

    with open(f'data/{repo_type}_repos.csv', 'w', newline="") as file:
        main.writer = csv.writer(file)
        main.writer.writerow(["owner", "name", "created", "pr_count"])
        cur_cursor = ""
        while True:
            next_cursor = get_repos_after(repo_query, cur_cursor)
            if next_cursor == "":
                break
            cur_cursor = next_cursor


if __name__ == "__main__":
    main()
