import os
import requests
import json
import csv

GITHUB_PAT = os.getenv('GITHUB_PAT')


def run_query(query):
    """Sends request to Github GraphQL API v4.

    Args:
        query: A string containing the query.

    Returns:
        JSON. A JSON object containing the results of the query.

    Raises:
        Exception: An error occurred when sending a request to the Github API.
    """
    headers = {'Authorization': 'token ' + GITHUB_PAT}
    request = requests.post("https://api.github.com/graphql",
                            headers=headers,
                            json={'query': query})
    if request.status_code == requests.codes.ok:
        return request.json()
    else:
        raise Exception("Request to Github GraphQL API failed.")


def get_intern_repos():
    """Retrieves all the STEP intern repos and stores them in a CSV file.


    intern_repos.csv has the following columns:
        owner: The STEP intern Github username.
        name: The repository name.
        created: The time and date that the repository was created.
        pr_count: The number of pull requests in the repository.
    """

    def get_intern_repos_after(cursor):
        """Gets the first 100 repositories after a cursor.

        Args:
            cursor: A string containing a cursor used for GraphQL pagination.

        Returns:
            str. A string containing the cursor of the last search result, or
            an empty string if there are no results after the current cursor.
        """

        query = """{{
            search(first: 100,
                   {after}
                   query: "sort:updated-asc
                           in:readme
                           git clone
                               https://github.com/googleinterns/step.git",
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
            intern_repos.append([
                result['node']['owner']['login'],
                result['node']['name'],
                result['node']['createdAt'],
                result['node']['pullRequests']['totalCount']
            ])
        return results[-1]['cursor']

    intern_repos = []
    cur_cursor = ""
    while True:
        next_cursor = get_intern_repos_after(cur_cursor)
        if next_cursor == "":
            break
        cur_cursor = next_cursor

    with open('intern_repos.csv', 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["owner", "name", "created", "pr_count"])
        writer.writerows(intern_repos)


def get_pr_comments():
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
    
    def get_pr_comments_per_repo(name, owner):
        """ Gets the pull request comments from a particular repository.

        This function processes the results from the Github API query and
        appends relevant information to the comment_counts list.

        Args:
            name: A string containing the repository name.
            owner: A string containing the repository owner.

        Returns:
            None.
        """

        def process_comment(comment):
            """ Helper function to process a comment.

            This function updates the total_comments variable and appends
            relevant information to the comment_list list.
            
            Args:
                comment: The comment node retrieved from the API.
            
            Returns:
                None.
            """

            nonlocal total_comments
            if comment['body'] != "" and comment:
                total_comments += 1

                # For the special case where the author has been deleted
                if not comment['author']:
                    comment['author'] = {"login": "deleted-user"}
                
                comment_list.append(
                    [comment['resourcePath'], comment['createdAt'],
                     comment['author']['login'], comment['body']]
                )
            return

        query = f"""{{
            repository(name: "{name}", owner: "{owner}") {{
                pullRequests(first: 20) {{
                    nodes {{
                        resourcePath
                        number
                        createdAt
                        deletions
                        additions
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

        for pr in pull_requests:
            total_comments = 0
            for pr_comment in pr['comments']['nodes']:
                process_comment(pr_comment)
            for review in pr['reviews']['nodes']:
                process_comment(review)
                for review_comment in review['comments']['nodes']:
                    process_comment(review_comment)
            comment_counts.append([
                pr['resourcePath'], pr['number'], 
                pr['createdAt'], total_comments, 
                pr['deletions'] + pr['additions']
            ])

    comment_counts = []
    comment_list = []

    with open('intern_repos.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            get_pr_comments_per_repo(row['name'], row['owner'])

    with open('pr_comment_counts.csv', 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "pr_path", "pr_number", "created", "total_comments",
            "pr_lines_changed"
        ])
        writer.writerows(comment_counts)

    with open('pr_comments.csv', 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["comment_path", "created", "author", "comment"])
        writer.writerows(comment_list)

def main():

    # Uncomment below to get new list of intern repositories.
    # get_intern_repos()

    # Uncomment below to get new comments from pull requests.
    get_pr_comments()


if __name__ == "__main__":
    main()
