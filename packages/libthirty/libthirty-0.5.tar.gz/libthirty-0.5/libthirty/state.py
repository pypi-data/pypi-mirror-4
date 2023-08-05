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
"""Environment dictionary - support structures"""


class _AttributeDict(dict):
    """
    Dictionary subclass enabling attribute lookup/assignment of keys/values.

    For example::

        >>> m = _AttributeDict({'foo': 'bar'})
        >>> m.foo
        'bar'
        >>> m.foo = 'not bar'
        >>> m['foo']
        'not bar'

    ``_AttributeDict`` objects also provide ``.first()`` which acts like
    ``.get()`` but accepts multiple keys as arguments, and returns the value of
    the first hit, e.g.::

        >>> m = _AttributeDict({'foo': 'bar', 'biz': 'baz'})
        >>> m.first('wrong', 'incorrect', 'foo', 'biz')
        'bar'

    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # to conform with __getattr__ spec
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def first(self, *names):
        for name in names:
            value = self.get(name)
            if value:
                return value

# Global config dictionary. Stores the global state.
env = _AttributeDict({
    'base_uri': 'https://api.30loops.net',
    'api_version': '0.9',
    'account': None,
    'service': None,
    'appname': None,
    'username': None,
    'password': None
})


def uri(
        base_uri=None,
        api_version=None,
        account=None):
    """Compose the base uri."""
    if not base_uri:
        base_uri = env.base_uri
    if not api_version:
        api_version = env.api_version
    if not account:
        account = env.account
    path = []
    path.append(api_version.strip('/'))
    if not isinstance(account, type(None)):
        path.append(account.strip('/'))

    return "%s/%s" % (base_uri.strip('/'), '/'.join(path))


def app_uri(
        base_uri=None,
        api_version=None,
        account=None,
        appname=None):
    """Compose the app uri."""
    if not appname:
        appname = env.appname

    return "%s/apps/%s" % (uri(base_uri, api_version, account), appname)


def service_uri(
        base_uri=None,
        api_version=None,
        account=None,
        appname=None,
        service=None):
    """Compose as service uri."""
    if not service:
        service = env.service

    return "%s/services/%s" % (app_uri(base_uri, api_version, account, appname),
            service)


def resource_collection_uri(
        base_uri=None,
        api_version=None,
        account=None,
        label=None):
    """Return the URI of a resource as a string."""
    if not base_uri:
        base_uri = env.base_uri
    if not api_version:
        api_version = env.api_version
    if not account:
        account = env.account
    if not label:
        label = env.label
    path = []
    path.append(api_version.strip('/'))
    path.append(account.strip('/'))
    path.append(label.strip('/'))

    return "%s/%s" % (base_uri.strip('/'), '/'.join(path))
