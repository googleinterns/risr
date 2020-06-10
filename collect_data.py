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


    The CSV file has the following columns:
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


def main():

    # Uncomment below to get new list of intern repositories.
    # get_intern_repos()


if __name__ == "__main__":
    main()
