# Copyright (c) 2011-2012, 30loops.net
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of 30loops.net nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL 30loops.net BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Base mixin classes for 30loops handlers."""

import os
import json
import requests
from requests.auth import HTTPBasicAuth

from .state import env
from .exceptions import HttpError, HttpReturnError


class HttpBaseHandler(object):
    """Base class for requests to the 30loops API. It serves as a HTTP mixin
    class for all handlers that are talking to an API endpoint."""
    def __init__(self):
        self.cert_file = os.path.join(
            os.path.dirname(__file__), "ssl", "StartSSL_CA.pem")

    def request(self, uri, method='GET', data=None, headers=None):
        # additional arguments for the http request
        kwargs = {}

        if data:
            kwargs['data'] = data

        if env.username and env.password:
            kwargs['auth'] = HTTPBasicAuth(
                    username=env.username,
                    password=env.password)
        if headers is None:
            headers = {}
        headers['Accept'] = "application/json"

        kwargs['verify'] = self.cert_file

        try:
            response = requests.request(
                method=method.lower(),
                url=uri,
                **kwargs)
        except requests.ConnectionError:
            raise HttpError("Connection error.")

        bad_statuses = [400, 401, 403, 404]

        if response.status_code in bad_statuses:
            error = json.loads(response.content)
            raise HttpReturnError(response.status_code, error['message'])

        error_statuses = [500, 501, 502, 503, 504]

        if response.status_code in error_statuses:
            raise HttpReturnError(response.status_code,
                    "There seems to be an error on 30loops.net. Chances are \
good that we are already working on it.")

        self.response = response

    def get(self):
        self.request(self.uri(), 'GET')

    def put(self, data):
        self.request(self.uri(), 'PUT', data)

    def post(self, data):
        self.request(self.uri(), 'POST', data)

    def delete(self):
        self.request(self.uri(), 'DELETE')
