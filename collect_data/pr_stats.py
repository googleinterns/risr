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

    
def get_pr_stats(name, owner):
    """ Gets the pull request comments from a particular repository.

    This function processes the results from the Github API query and
    appends relevant information to the comment_counts list.

    Args:
        name: A string containing the repository name.
        owner: A string containing the repository owner.

    Returns:
        None.
    """

    query = f"""{{
        repository(name: "{name}", owner: "{owner}") {{
            pullRequests(first: 50) {{
                nodes {{
                    resourcePath
                    number
                    createdAt
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

    result = run_query(query)

    pull_requests = result['data']['repository']['pullRequests']['nodes']

    for pr in pull_requests:
        total_comments = pr['comments']['totalCount']
        for review in pr['reviews']['nodes']:
            if review['body'] != "" and review:
                total_comments += 1
            total_comments += review['comments']['totalCount']
        main.pr_stats.append([
            pr['resourcePath'], pr['number'], 
            pr['createdAt'], total_comments, 
            pr['deletions'] + pr['additions']
        ])



def main():
    """ Retrieves the comments in pull requests for intern repositories.

    pr_comment_counts.csv has the following columns:
        pr_path: The resource path to the pull request.
        created: The date and time that the pull request was created.
        total_comments: Number of comments in pull request.

    pr_comments.csv has the following columns:
        comment_path: The resource path to the comment.
        created: The date and time that the comment was created.
        author: The Github username of the comment author.
        comment: The text in the comment.
    """

    main.pr_stats = []

    with open('data/intern_repos.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            get_pr_stats(row['name'], row['owner'])

    with open('data/pr_stats.csv', 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "pr_path", "pr_number", "created", "total_comments",
            "pr_lines_changed"
        ])
        writer.writerows(main.pr_stats)


if __name__ == "__main__":
    main()