# -*- coding: utf-8 -*-
"""
Copyright 2010-2012 elfCLOUD / elfcloud.fi – SCIS Secure Cloud Infrastructure Services

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import unittest
import mock
import StringIO

from elfcloud.exceptions import ECDataItemException
from elfcloud.connection import Connection


class TestConnection(unittest.TestCase):
    def setUp(self):
        self.username = "username"
        self.password = "password"
        self.auth_method = "password"
        self.apikey = "apikey"
        self.server = "server"

    def test_connection_init(self):
        connection = Connection(self.server)
        self.assertEquals(connection._server_url, self.server)

    @mock.patch.object(Connection, 'make_request')
    def test_connection_auth(self, mock_method):
        mock_method.return_value = {'result': 'success'}
        params = {
            'username': self.username,
            'auth_data': self.password,
            'auth_method': self.auth_method,
            'apikey': self.apikey
            }
        connection = Connection(self.server)
        self.assertFalse(connection._is_authed)

        connection.auth(self.username, self.password, self.auth_method, self.apikey)
        connection.make_request.assert_called_once_with("auth", params)
        self.assertTrue(connection._is_authed)

    @mock.patch("urllib2.Request")
    @mock.patch('urllib2.build_opener')
    @mock.patch('json.JSONDecoder')
    def test_connection_make_request(self, MockJSONDecoder, MockUrllib, MockRequest):
        mock_instance1 = mock.Mock()
        mock_instance1.open.return_value = StringIO.StringIO("Test response")
        MockUrllib.return_value = mock_instance1

        mock_instance2 = mock.Mock()
        mock_instance2.decode.return_value = {'result': 'success'}
        MockJSONDecoder.return_value = mock_instance2

        MockRequest.return_value = mock.Mock()

        connection = Connection(self.server)
        response = connection.make_request('method', 'params')
        self.assertEquals('success', response)

        mock_instance2.decode.assert_called_once_with("Test response")
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        MockRequest.assert_called_once_with(self.server + '1.1/json', '{"params": "params", "method": "method"}', headers)

    @mock.patch('urllib2.urlopen')
    def test_connection_make_transaction(self, MockUrllib):
        mock_instance1 = mock.Mock()
        mock_instance1.headers = {'X-ELFCLOUD-RESULT': 'OK'}
        MockUrllib.return_value = mock_instance1
        headers = {}
        headers['Test-header'] = 'value'

        connection = Connection(self.server)
        response = connection.make_transaction(headers, '/fetch')
        self.assertEquals(MockUrllib.call_args[0][0].headers, headers)
        self.assertEquals(response.headers['X-ELFCLOUD-RESULT'], 'OK')

        mock_instance1.headers = {'X-ELFCLOUD-RESULT': 'ERROR: 404 Not found'}
        self.assertRaises(ECDataItemException, connection.make_transaction, headers, '/fetch')

