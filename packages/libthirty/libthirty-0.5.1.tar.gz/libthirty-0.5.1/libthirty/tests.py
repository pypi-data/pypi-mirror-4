from nose.tools import eq_, assert_raises
from mock import patch, Mock
from unittest import TestCase
import json

from libthirty.state import env, uri, app_uri, service_uri
from libthirty.base import HttpBaseHandler
from libthirty.logbook import LogBookHandler
from libthirty.actions import ActionHandler
from libthirty.app import AppManager
from libthirty import validators
from docar.exceptions import ValidationError


class ValidatorTests(TestCase):
    def test_resource_naming_validator(self):
        v = validators.naming

        assert_raises(ValidationError, v, 'name!')
        assert_raises(ValidationError, v, 'name@')
        assert_raises(ValidationError, v, 'name#')
        assert_raises(ValidationError, v, 'name$')
        assert_raises(ValidationError, v, 'name%')
        assert_raises(ValidationError, v, 'name^')
        assert_raises(ValidationError, v, 'name&')
        assert_raises(ValidationError, v, 'name*')
        assert_raises(ValidationError, v, 'name(')
        assert_raises(ValidationError, v, 'name)')
        assert_raises(ValidationError, v, 'name=')
        assert_raises(ValidationError, v, 'name+')
        assert_raises(ValidationError, v, 'name[')
        assert_raises(ValidationError, v, 'name]')
        assert_raises(ValidationError, v, 'name{')
        assert_raises(ValidationError, v, 'name}')
        assert_raises(ValidationError, v, 'name/')
        assert_raises(ValidationError, v, 'name\\')
        assert_raises(ValidationError, v, 'name"')
        assert_raises(ValidationError, v, 'name:')
        assert_raises(ValidationError, v, 'name;')
        assert_raises(ValidationError, v, 'name,')
        assert_raises(ValidationError, v, 'name<')
        assert_raises(ValidationError, v, 'name>')
        assert_raises(ValidationError, v, 'name?')
        assert_raises(ValidationError, v, 'name~')
        assert_raises(ValidationError, v, 'name`')
        assert_raises(ValidationError, v, 'name-')
        assert_raises(ValidationError, v, 'Name')

        eq_(None, v('real_good_name_1234567890'))

    def test_resource_naming_with_dashes_validator(self):
        v = validators.naming_with_dashes

        assert_raises(ValidationError, v, 'name!')
        assert_raises(ValidationError, v, 'name@')
        assert_raises(ValidationError, v, 'name#')
        assert_raises(ValidationError, v, 'name$')
        assert_raises(ValidationError, v, 'name%')
        assert_raises(ValidationError, v, 'name^')
        assert_raises(ValidationError, v, 'name&')
        assert_raises(ValidationError, v, 'name*')
        assert_raises(ValidationError, v, 'name(')
        assert_raises(ValidationError, v, 'name)')
        assert_raises(ValidationError, v, 'name=')
        assert_raises(ValidationError, v, 'name+')
        assert_raises(ValidationError, v, 'name[')
        assert_raises(ValidationError, v, 'name]')
        assert_raises(ValidationError, v, 'name{')
        assert_raises(ValidationError, v, 'name}')
        assert_raises(ValidationError, v, 'name/')
        assert_raises(ValidationError, v, 'name\\')
        assert_raises(ValidationError, v, 'name"')
        assert_raises(ValidationError, v, 'name:')
        assert_raises(ValidationError, v, 'name;')
        assert_raises(ValidationError, v, 'name,')
        assert_raises(ValidationError, v, 'name<')
        assert_raises(ValidationError, v, 'name>')
        assert_raises(ValidationError, v, 'name?')
        assert_raises(ValidationError, v, 'name~')
        assert_raises(ValidationError, v, 'name`')

        eq_(None, v('real-good_name_1234567890'))

    def test_25_character_max_string_length(self):
        v = validators.max_25_chars

        def make_name(length):
            return "".join([str(i)[0] for i in range(1, length)])

        # Fail validation if the name is longer than 32 characters
        assert_raises(ValidationError, v, make_name(26))
        # Pass the test for a name with 32 characters
        eq_(None, v(make_name(25)))


class ActionHandlerTests(TestCase):
    def setUp(self):
        self.http_patcher = patch('libthirty.base.requests')
        self.mock_requests = self.http_patcher.start()
        self.mock_requests.ConnectionError = Exception

        self.dirname_patcher = patch('libthirty.base.os.path.dirname')
        self.mock_dirname = self.dirname_patcher.start()
        self.mock_dirname.return_value = "/path/"

    def tearDown(self):
        self.http_patcher.stop()
        self.dirname_patcher.stop()

    def test_uri_construction(self):
        action = ActionHandler(action='deploy')
        env.label = 'app'
        env.appname = "thirtyblog"
        env.account = '30loops'

        expected = "https://api.30loops.net/0.9/30loops/apps/thirtyblog"

        eq_(expected, action.uri())

    def test_queue_action(self):
        env.label = 'app'
        env.account = '30loops'
        env.resource = 'thirtyblog'

        response = Mock()
        response.status_code = 202
        response.headers = {'Location': 'http://location/uuid'}

        self.mock_requests.request.return_value = response

        action = ActionHandler('deploy', {})
        action.queue()

        self.mock_requests.request.assert_called_once_with(
                url=action.uri(), method='post',
                verify='/path/ssl/StartSSL_CA.pem',
                data=json.dumps({'action': 'deploy', 'options': {}})
                )


class LogBookHandlerTests(TestCase):
    def setUp(self):
        self.http_patcher = patch('libthirty.base.requests')
        self.mock_requests = self.http_patcher.start()
        env.account = '30loops'

        self.dirname_patcher = patch('libthirty.base.os.path.dirname')
        self.mock_dirname = self.dirname_patcher.start()
        self.mock_dirname.return_value = "/path/"

        self.auth_patcher = patch('libthirty.base.HTTPBasicAuth')
        self.mock_auth = self.auth_patcher.start()
        self.auth_token = self.mock_auth.return_value

    def tearDown(self):
        self.http_patcher.stop()
        self.dirname_patcher.stop()
        self.auth_patcher.stop()

    def test_uri_construction(self):
        lbh = LogBookHandler(uuid='uuid')

        expected = "https://api.30loops.net/0.9/30loops/logbook/uuid"

        eq_(expected, lbh.uri())

    def test_logbook_status(self):
        msg = {
            "status": "queued",
            "messages": []
        }
        response = Mock()
        response.status_code = 200
        response.content = json.dumps(msg)

        self.mock_requests.request.return_value = response

        lbh = LogBookHandler('uuid')

        eq_('unknown', lbh.status)

        lbh.fetch()

        eq_('queued', lbh.status)
        self.mock_requests.request.assert_called_once_with(
                url=lbh.uri(), method='get',
                verify='/path/ssl/StartSSL_CA.pem',
                )

    def test_internal_message_list(self):
        msg = {
            "status": "queued",
            "messages": []
        }

        response = Mock()
        response.status_code = 200
        response.content = json.dumps(msg)

        self.mock_requests.request.return_value = response

        lbh = LogBookHandler('uuid')

        # The logbook starts off with no messages
        eq_(0, len(lbh.messages))

        msg['messages'].append(
        {
            "asctime": "2012-02-08T11:15:04",
            "message": "message1",
        })

        response.content = json.dumps(msg)
        self.mock_requests.request.return_value = response

        new_msg = lbh.fetch()

        # The logbook has one message now
        eq_(1, len(lbh.messages))
        eq_(new_msg, lbh.messages)

        messages = [
        {
            "asctime": "2012-02-08T11:15:05",
            "message": "message2",
        },
        {
            "asctime": "2012-02-08T11:15:06",
            "message": "message3",
        }]

        msg['messages'].extend(messages)

        response.content = json.dumps(msg)
        self.mock_requests.request.return_value = response

        new_msg = lbh.fetch()

        # The logbook has one message now
        eq_(3, len(lbh.messages))
        eq_(new_msg, messages)


class UrlConstructionTests(TestCase):
    """Test the behaviour of ``resource_uri``."""

    def test_base_uri(self):
        """Generate the base URI from parameters."""
        expected = "https://api.30loops.net/0.9/30loops"
        eq_(expected, uri(account='30loops'))

    def test_app_uri(self):
        """Generate the app uri."""
        expected = "https://api.30loops.net/0.9/30loops/apps/thirtyblog"
        eq_(expected, app_uri(account='30loops', appname='thirtyblog'))

    def test_service_uri(self):
        """Generate the service uri."""
        expected = (
                "https://api.30loops.net/0.9/30loops/"
                "apps/thirtyblog/services/postgres"
                )
        eq_(expected, service_uri(
                    account='30loops',
                    appname='thirtyblog',
                    service='postgres'
                    ))

    def test_base_uri_using_env(self):
        """Generate the base URI from env."""
        expected = "https://api.30loops.net/0.9/env_uri"
        env.account = 'env_uri'
        eq_(expected, uri())

    def test_app_uri_using_env(self):
        """Generate the app uri."""
        expected = "https://api.30loops.net/0.9/env_app/apps/env_app"
        env.account = env.appname = 'env_app'
        eq_(expected, app_uri())

    def test_service_uri_using_env(self):
        """Generate the service uri."""
        expected = (
                "https://api.30loops.net/0.9/env_service/"
                "apps/env_service/services/env_service"
                )
        env.account = env.appname = env.service = 'env_service'
        eq_(expected, service_uri())


class HttpBaseHandlerTests(TestCase):
    def setUp(self):
        self.http_patcher = patch('libthirty.base.requests')
        self.mock_requests = self.http_patcher.start()
        env.account = '30loops'

        self.dirname_patcher = patch('libthirty.base.os.path.dirname')
        self.mock_dirname = self.dirname_patcher.start()
        self.mock_dirname.return_value = "/path/"

        self.auth_patcher = patch('libthirty.base.HTTPBasicAuth')
        self.mock_auth = self.auth_patcher.start()
        self.auth_token = self.mock_auth.return_value

    def tearDown(self):
        self.http_patcher.stop()
        self.dirname_patcher.stop()
        self.auth_patcher.stop()

    def test_get_requests(self):
        handler = HttpBaseHandler()
        # Mock the uri method, since the handler doesn't provide one
        handler.uri = Mock()
        handler.uri.return_value = '/'
        handler.get()

        self.mock_requests.request.assert_called_once_with(url='/',
                method='get',
                verify='/path/ssl/StartSSL_CA.pem',
                )

    def test_put_requests(self):
        handler = HttpBaseHandler()
        # Mock the uri method, since the handler doesn't provide one
        handler.uri = Mock()
        handler.uri.return_value = '/'
        handler.put("data")

        self.mock_requests.request.assert_called_once_with(
                url='/', data="data", method='put',
                verify='/path/ssl/StartSSL_CA.pem',
                )

    def test_post_requests(self):
        handler = HttpBaseHandler()
        # Mock the uri method, since the handler doesn't provide one
        handler.uri = Mock()
        handler.uri.return_value = '/'
        handler.post("data")

        self.mock_requests.request.assert_called_once_with(
                url='/', data="data", method='post',
                verify='/path/ssl/StartSSL_CA.pem',
                )

    def test_delete_requests(self):
        handler = HttpBaseHandler()
        # Mock the uri method, since the handler doesn't provide one
        handler.uri = Mock()
        handler.uri.return_value = '/'
        handler.delete()

        self.mock_requests.request.assert_called_once_with(url='/',
                method='delete',
                verify='/path/ssl/StartSSL_CA.pem',
                )

    def test_basic_auth(self):
        env.username = 'crito'
        env.password = 'secret'
        handler = HttpBaseHandler()
        # Mock the uri method, since the handler doesn't provide one
        handler.uri = Mock()
        handler.uri.return_value = '/'
        handler.get()

        self.mock_requests.request.assert_called_once_with(url='/',
                method='get',
                verify='/path/ssl/StartSSL_CA.pem',
                auth=self.auth_token
                )

        env.username = None
        env.password = None

    def test_change_cert_file(self):
        handler = HttpBaseHandler()
        handler.cert_file = 'something'
        # Mock the uri method, since the handler doesn't provide one
        handler.uri = Mock()
        handler.uri.return_value = '/'
        handler.get()

        self.mock_requests.request.assert_called_once_with(url='/',
                method='get',
                verify='something',
                )


class AppManagerTests(TestCase):
    def setUp(self):
        self.http_patcher = patch('libthirty.base.requests')
        self.mock_requests = self.http_patcher.start()
        env.account = '30loops'

        self.dirname_patcher = patch('libthirty.base.os.path.dirname')
        self.mock_dirname = self.dirname_patcher.start()
        self.mock_dirname.return_value = "/path/"

        self.auth_patcher = patch('libthirty.base.HTTPBasicAuth')
        self.mock_auth = self.auth_patcher.start()
        self.auth_token = self.mock_auth.return_value

    def tearDown(self):
        self.http_patcher.stop()
        self.dirname_patcher.stop()
        self.auth_patcher.stop()

    def test_app_manager_list(self):
        rm = AppManager()

        msg = {
            "size": 2,
            "items": [
                {"name": "name1"},
                {"name": "name2"}
                ]}

        response = Mock()
        response.status_code = 200
        response.content = json.dumps(msg)

        self.mock_requests.request.return_value = response

        rm.list()

        self.mock_requests.request.assert_called_once_with(
                url=rm.uri(), method='get',
                verify='/path/ssl/StartSSL_CA.pem',
                )
        eq_(2, len(rm._collection.collection_set))
