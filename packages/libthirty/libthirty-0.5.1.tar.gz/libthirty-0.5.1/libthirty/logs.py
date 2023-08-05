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
"""Retrieve a list of log messages from the 30loops platform."""

import json

from urllib import urlencode

from .state import env
from .base import HttpBaseHandler


class QueryParameters(dict):
    """A simple query dict class. you can add query parameters to it and output
    them in a safe way.

    IMPORTANT: Can't handle multiple values for the same key yet, eg:
      a=whatever&a=somethingelse

    """
    def urlencode(self):
        output = []
        encode = lambda k, v: urlencode({k: v})

        for k, v in self.iteritems():
            output.append(encode(k, v))

        return '&'.join(output)


class LogsHandler(HttpBaseHandler):
    """The ``LogsHandler`` class retrieves logs related to an app and
    environment."""

    def __init__(self, name, environment, process=None, limit=None):
        super(LogsHandler, self).__init__()
        self.qp = QueryParameters()

        self.name = name
        self.environment = environment

        if process:
            self.qp['process'] = process

        if limit:
            self.qp['limit'] = limit

        self.messages = []

    def uri(self):
        uri = "%s/%s/%s/apps/%s/logs%s" % (
                env.base_uri.strip('/'),
                env.api_version.strip('/'),
                env.account.strip('/'),
                self.name,
                "?%s" % self.qp.urlencode() if len(self.qp) > 0 else ""
                )
        return uri

    def fetch(self):
        self.get()

        if self.response.status_code == 200:
            msg = json.loads(self.response.content)

        self.messages = msg['messages']

        return self.messages
