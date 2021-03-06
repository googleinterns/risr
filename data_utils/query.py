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

""" Module for sending a request to the Github API. """

import os
from time import sleep
import requests


def run_query(query, attempt=1):
    """Sends request to Github GraphQL API v4.

    Args:
        query: A string containing the query.
        attempt: The number of attempts to send request for a particular query.

    Returns:
        JSON. A JSON object containing the results of the query.

    Raises:
        Exception: An error occurred when sending a request to the Github API.
    """

    # Get the Github Personal Access Token from your local environment since
    # authentication is required to make large requests to the Github API.
    # You can set the environment variable with the following command:
    #     $ export GITHUB_PAT="YOUR GITHUB PERSONAL ACCESS TOKEN HERE"

    github_pat = os.getenv("GITHUB_PAT")

    if github_pat is None:
        raise Exception("GITHUB_PAT environment variable is not set.")

    headers = {"Authorization": "token " + github_pat}
    request = requests.post("https://api.github.com/graphql",
                            headers=headers,
                            json={"query": query})

    # pylint: disable=no-member
    if request.status_code == requests.codes.ok:
        result = request.json()
        if "errors" in result.keys():
            print("There was an error in the Github API query.",
                  result)
            return []
        return result

    # Try to send request again in case it failed due to rate limiting.
    if (attempt == 1 and
            (request.status_code == requests.codes.forbidden
             or request.status_code == requests.codes.bad_gateway)):
        sleep(1)
        print(f"Request status code: {request.status_code}. Trying again.")
        run_query(query, 2)
    print("Request to Github GraphQL API failed.", request)
    return []
