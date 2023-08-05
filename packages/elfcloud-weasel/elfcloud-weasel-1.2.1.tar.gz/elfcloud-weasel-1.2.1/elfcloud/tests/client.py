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

import elfcloud.client as client
from elfcloud.exceptions import (
        ECCryptException,
        ECAPIException,
    )
from elfcloud.utils import ENC_AES256, ENC_NONE


class TestClientFunctions(unittest.TestCase):
    def setUp(self):
        self.client = client.Client('username', 'password')

    def test_add_vault(self):
        conn = mock.Mock()
        conn.make_request.return_value = {
                'a': "a1",
                'b': 'b2'
        }
        self.client.connection = conn

        result = self.client.add_vault('new_vault2', 'vault_type1')

        self.assertEquals(result.a, 'a1')
        self.assertEquals(result.b, 'b2')

        params = {
            'vault_type': 'vault_type1',
            'name': 'new_vault2'
        }
        conn.make_request.assert_called_once_with('add_vault', params)

    def test_add_cluster(self):
        conn = mock.Mock()
        conn.make_request.return_value = {
                    'a': 'a1',
                    'b': 'b1'
            }
        self.client.connection = conn

        result = self.client.add_cluster(name="new_cluster", parent_id="1")

        self.assertEquals(result.a, 'a1')
        self.assertEquals(result.b, 'b1')
        params = {
                'name': 'new_cluster',
                'parent_id': '1'
            }
        conn.make_request.assert_called_once_with('add_cluster', params)

    @mock.patch('elfcloud.client.Cluster')
    def test_list_clusters(self, MockCluster):
        mock_instance = mock.Mock()
        mock_instance.children = ["Cluster1", "Cluster2"]
        MockCluster.return_value = mock_instance

        self.client.connection._is_authed = True
        result = self.client.list_clusters("1")

        MockCluster.assert_called_once_with(self.client, id="1")
        self.assertEquals(result, mock_instance.children)

    def test_list_vaults(self):
        conn = mock.Mock()
        conn.make_request.return_value = [{
                'a': 'a1',
                'b': 'b1'
                }]
        self.client.connection = conn

        result = self.client.list_vaults(vault_type="type", id_="1")

        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].a, 'a1')
        self.assertEquals(result[0].b, 'b1')
        params = {
            'vault_type': 'type',
            'id_': '1',
            'role': None
            }
        conn.make_request.assert_called_once_with('list_vaults', params)

    @mock.patch('elfcloud.client.Cluster')
    def test_list_dataitems(self, MockCluster):
        mock_instance = mock.Mock()
        mock_instance.dataitems = ["dataitem1", "dataitem2"]
        MockCluster.return_value = mock_instance

        self.client.connection._is_authed = True
        result = self.client.list_dataitems("1")

        MockCluster.assert_called_once_with(self.client, id="1")
        self.assertEquals(result, mock_instance.dataitems)

    @mock.patch('elfcloud.client.Cluster')
    def test_remove_cluster(self, MockCluster):
        mock_instance = mock.Mock()
        mock_instance.remove.return_value = "remove"
        MockCluster.return_value = mock_instance
        self.client.connection._is_authed = True

        result = self.client.remove_cluster("1")

        self.assertEquals(result, "remove")

    @mock.patch('elfcloud.client.Vault')
    def test_remove_vault(self, MockVault):
        mock_instance = mock.Mock()
        mock_instance.remove.return_value = "remove"
        MockVault.return_value = mock_instance
        self.client.connection._is_authed = True

        result = self.client.remove_vault("1")
        self.assertEquals(result, "remove")

    @mock.patch('elfcloud.client.DataItem')
    def test_remove_dataitem(self, MockDataItem):
        mock_instance = mock.Mock()
        mock_instance.remove.return_value = "remove"
        MockDataItem.return_value = mock_instance
        self.client.connection._is_authed = True

        result = self.client.remove_dataitem("1", "key")
        MockDataItem.assert_called_once_with(self.client, parent_id="1", name="key")
        self.assertEquals(result, "remove")

    @mock.patch('elfcloud.client.DataItem')
    def test_fetch_data(self, MockDataItem):
        mock_instance = mock.Mock()
        mock_instance.data = "Test data"
        MockDataItem.return_value = mock_instance

        self.client.connection._is_authed = True
        result = self.client.fetch_data("1", "key")

        MockDataItem.assert_called_once_with(self.client, parent_id="1", name="key")
        self.assertEquals(result, mock_instance.data)

    @mock.patch('elfcloud.client.DataItem')
    def test_store_data(self, MockDataItem):
        mock_instance = mock.Mock()
        mock_instance.store_data.return_value = "OK"
        MockDataItem.return_value = mock_instance

        self.client.connection._is_authed = True
        result = self.client.store_data("1", "key", "test_data")

        MockDataItem.assert_called_once_with(self.client, parent_id="1", name="key")
        self.assertEquals(result, mock_instance.store_data())

        self.client.set_encryption_key('12345678901234561234567890123456')
        self.client.encryption_mode = ENC_AES256
        self.client.connection._is_authed = True
        result = self.client.store_data("1", "key", "test_data")

    def test_change_encryption_mode(self):
        client = self.client

        self.assertRaises(ECCryptException, setattr, client, 'encryption_mode', "INVALID ENCRYPTION MODE")
        client.encryption_mode = ENC_NONE
        self.assertEquals(client.encryption_mode, ENC_NONE)
        client.encryption_mode = ENC_AES256
        self.assertEquals(client.encryption_mode, ENC_AES256)

    def test_change_apikey(self):
        client = self.client
        self.assertFalse(client.connection._is_authed)

        client.connection._is_authed = True
        self.assertTrue(client.connection._is_authed)

        client.apikey = "newkey"
        self.assertFalse(client.connection._is_authed)
        self.assertEquals(client.apikey, "newkey")

    def test_change_server_url(self):
        client = self.client
        self.assertFalse(client.connection._is_authed)

        client.connection._is_authed = True
        self.assertTrue(client.connection._is_authed)

        client.server_url = "newhost"
        self.assertFalse(client.connection._is_authed)
        self.assertEquals(client.server_url, "newhost")

    def test_change_encryption_key(self):
        client = self.client

        self.assertEquals(client.crypt._crypt_key, None)
        client.set_encryption_key("newkey")
        self.assertEquals(client.crypt._crypt_key, "newkey")

    def test_change_password(self):
        client = self.client
        self.assertFalse(client.connection._is_authed)

        client.connection._is_authed = True
        self.assertTrue(client.connection._is_authed)

        client.set_password("newpassword")
        self.assertFalse(client.connection._is_authed)
        self.assertEquals(client._auth_data, "newpassword")

    def test_change_username(self):
        client = self.client
        self.assertFalse(client.connection._is_authed)

        client.connection._is_authed = True
        self.assertTrue(client.connection._is_authed)

        client.username = "new-user"
        self.assertFalse(client.connection._is_authed)
        self.assertEquals(client.username, "new-user")

    def test_change_request_size(self):
        client = self.client

        client.set_request_size(1024)

        self.assertEquals(client._request_size, 1024)
        self.assertRaises(ValueError, client.set_request_size, "asdfasdf")
        self.assertRaises(TypeError, client.set_request_size, None)
        self.assertRaises(ECAPIException, client.set_request_size, -1)

    def test_auth(self):
        conn = mock.Mock()
        self.client.connection = conn
        self.client.apikey = "apikey"

        self.client.auth()

        conn.auth.assert_called_once_with(self.client.username, self.client._auth_method,
                                          self.client._auth_data, self.client.apikey)

    def _mock_client_make_request(self, checksum=u'0f9aec7fe5ccbc22d4fcfd3bc8427b10',
                                        modified_date=u'2012-10-15T07:42:28.824216+00:00',
                                        meta=u'v1:CHA:d8c2eafd90c266e19ab9dcacc479f8af:ENC:AES256:TGS:A,B:KHA:257e3a285b3d6a257e6739ba085ddf2d:DSC:JE::',
                                        length=26246026,
                                        name=u'Wildlife.wmv',
                                        parent_id=392,
                                        last_accessed_date=u'2012-10-15T09:56:27.505500+00:00'):
        conn = mock.Mock()
        self.client.connection = conn
        conn.make_request.return_value = [{
            u'modified_date': modified_date,
            u'name': name,
            u'md5sum': str(checksum),
            u'parent_id': parent_id,
            u'last_accessed_date': last_accessed_date,
            u'meta': meta,
            u'size': length
        }]
        return conn

    def test_get_dataitem_info(self):
        conn = self._mock_client_make_request()

        self.client.connection = conn
        self.client.get_dataitem(1, "key")

        conn.make_request.assert_called_once_with('list_dataitems', {'parent_id': 1, 'names': ['key']})
