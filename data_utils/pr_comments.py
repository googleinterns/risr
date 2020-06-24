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
from query import run_query


def get_pr_comments(name, owner):
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

    result = run_query(query)

    pull_requests = result['data']['repository']['pullRequests']['nodes']

    for pull_request in pull_requests:
        for pr_comment in pull_request['comments']['nodes']:
            process_comment(pr_comment)
        for review in pull_request['reviews']['nodes']:
            process_comment(review)
            for review_comment in review['comments']['nodes']:
                process_comment(review_comment)


def process_comment(comment):
    """ Helper function to process a comment.

    This function updates the total_comments variable and appends
    relevant information to the comment_list list.

    Args:
        comment: The comment node retrieved from the API.

    Returns:
        None.
    """

    if comment['body'] != "" and comment:
        # For the special case where the author has been deleted
        if not comment['author']:
            comment['author'] = {"login": "deleted-user"}

        main.writer.writerow([
            comment['resourcePath'], comment['createdAt'],
            comment['author']['login'], comment['body']
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

    with open('data/intern_repos.csv', newline='') as in_csv, \
         open('data/pr_comments.csv', 'w', newline="") as out_csv:
        reader = csv.DictReader(in_csv)
        main.writer = csv.writer(out_csv)
        main.writer.writerow(["comment_path", "created", "author", "comment"])
        for row in reader:
            get_pr_comments(row['name'], row['owner'])


if __name__ == "__main__":
    main()
