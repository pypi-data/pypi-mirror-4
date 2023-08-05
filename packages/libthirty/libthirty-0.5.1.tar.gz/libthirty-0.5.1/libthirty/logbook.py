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
"""Poll a logbook from the 30loops platform."""

import json

from .state import env
from .base import HttpBaseHandler


class LogBookHandler(HttpBaseHandler):
    """Access a logbook of an action.

    :param uuid: The unique uuid of the queued action.
    :type uuid: string

    You can continously fetch the new messages of a logbook. The handler stores
    a list of all messages of the logbook and returns only new messages on each
    consecutive fetch. You can also query the status of the action as an
    instance attribute, eg:

    >>> l = LogBookHandler('uuid')
    >>> l.fetch()
    ['message1']
    >>> l.fetch()
    ['message2']
    >>> l.messages
    ['message1', 'message2']
    >>> l.status
    'Running'

    """
    def __init__(self, uuid=None):
        super(LogBookHandler, self).__init__()

        self.uuid = uuid
        self.status = 'unknown'
        self.messages = []

    def uri(self):
        uri = "%s/%s/%s/logbook/%s" % (
                env.base_uri.strip('/'),
                env.api_version.strip('/'),
                env.account.strip('/'),
                self.uuid
                )
        return uri

    def fetch(self):
        """Fetch the logbook from the server.

        :returns: A list of message entries, that are new since the last fetch.
        :rtype: list

        """
        #Fetch the logbook
        #FIXME: check if the logbook is already closed, and dont fetch again in
        #       this case (action status).
        self.get()

        if self.response.status_code == 200:
            msg = json.loads(self.response.content)

        self.status = msg['status']

        # we gonna store the diff between the new and old messages in this list
        diff_messages = []

        # thats the new list of messages
        messages = msg['messages']

        # we slice the new messages out
        diff_messages = messages[len(self.messages):]

        # we set the new full list of messages
        self.messages = messages

        return diff_messages
