#!/usr/bin/env python
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https: // www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Module that defines different views for the dashboard app."""

import os
import csv
import json

from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings


@api_view(['GET'])
def dashboard_list(request):
    """ Handles GET operations over the root endpoint of the API.

    Reads data from a CSV file and returns it in JSON format as a response.

    Args:
        request: A rest_framework.request.Request instance.

    Returns:
        A rest_framework.Response instance containing the data, if any.
    """
    if request.method == 'GET':
        with open(os.path.join(settings.BASE_DIR, 'data/cap_pr_count.csv')) as csv_in:
            reader = csv.DictReader(csv_in)
            data = []
            for row in reader:
                data.append({
                    'pr_range': row['pr_range'],
                    'repo_count': int(row['repo_count'])
                })
        return Response(json.dumps(data))
    return Response()
