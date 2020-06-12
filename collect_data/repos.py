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

import csv
from query import run_query


def get_repos_after(cursor):
    """Gets the first 100 repositories after a cursor.

    This is necessary because GraphQL uses pagination, so only 100 results
    can be retrieved at one time.

    Args:
        cursor: A string containing a cursor used for GraphQL pagination.

    Returns:
        str. A string containing the cursor of the last search result, or
        an empty string if there are no results after the current cursor.
    """

    query = """{{
        search(first: 100,
               {after}
               query: "sort:created-asc
                       in:readme
                       git clone https://github.com/googleinterns/step.git",
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
    result = run_query(query.format(after=after))

    results = result['data']['search']['edges']
    if not results:
        return ""

    for result in results:
        main.repo_list.append([
            result['node']['owner']['login'],
            result['node']['name'],
            result['node']['createdAt'],
            result['node']['pullRequests']['totalCount']
        ])
    
    return results[-1]['cursor']


def main():
    """Retrieves all the STEP intern repos and stores them in a CSV file.

    intern_repos.csv has the following columns:
        owner: The STEP intern Github username.
        name: The repository name.
        created: The time and date that the repository was created.
        pr_count: The number of pull requests in the repository.
    """

    main.repo_list = []
    cur_cursor = ""

    while True:
        next_cursor = get_repos_after(cur_cursor)
        if next_cursor == "":
            break
        cur_cursor = next_cursor
    
    with open('data/intern_repos.csv', 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["owner", "name", "created", "pr_count"])
        writer.writerows(main.repo_list)


if __name__ == "__main__":
    main()