import unittest
import mock
import StringIO
import hashlib
import base64

import elfcloud.client as client
from elfcloud.exceptions import HolviDataItemException, ClientException
from elfcloud.dataitem import DataItem
from elfcloud.filecrypt import FileIterator, CryptIterator
from elfcloud.utils import ENC_AES256, ENC_NONE


class TestDataItem(unittest.TestCase):

    def setUp(self):
        self.client = client.Client('username', 'password')
        self.keyname = "keyname"
        self.parent_id = 1

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

    def test_dataitem_init(self):
        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)

        self.assertEquals(dataitem.name, self.keyname)
        self.assertEquals(dataitem.parent_id, self.parent_id)

    def test_fetch_data(self):
        headers = {}
        headers['X-HOLVI-KEY'] = base64.b64encode(self.keyname)
        headers['X-HOLVI-PARENT'] = self.parent_id

        conn = mock.Mock()
        conn.make_transaction.return_value = mock.Mock(headers={'X-HOLVI-HASH': "4321"})
        self.client.connection = conn

        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        response = dataitem.data

        self.assertEquals(response['checksum'], "4321")
        self.assertEquals(type(response['data']), FileIterator)
        conn.make_transaction.assert_called_once_with(headers, "/fetch")

        self.client.set_encryption_key("12345678901234561234567890123456")
        self.client.encryption_mode = ENC_AES256
        response = dataitem.data
        self.assertEquals(type(response['data']), CryptIterator)

    def test_store_data(self):
        test_data = StringIO.StringIO("Some test data to be sent to server")
        md5 = hashlib.md5()
        md5.update(test_data.read())
        test_data.seek(0)
        test_data.get_content_hash = lambda: "aabbccddeeff1122"

        headers = {}
        headers['X-HOLVI-STORE-MODE'] = "new"
        headers['X-HOLVI-KEY'] = base64.b64encode(self.keyname)
        headers['X-HOLVI-PARENT'] = self.parent_id
        headers['X-HOLVI-META'] = 'v1:TGS:tag1,tag2:DSC:NewDescription:ENC:NONE::'
        headers['Content-Type'] = 'application/octet-stream'
        headers['X-HOLVI-HASH'] = md5.hexdigest()
        headers['Content-Length'] = len(test_data.read())
        test_data.seek(0)

        conn = self._mock_client_make_request(name=self.keyname,
                                              parent_id=self.parent_id,
                                              meta='v1:TGS:tag1,tag2:DSC:NewDescription:ENC:NONE::',
                                              checksum=md5.hexdigest())
        conn.make_transaction.return_value = None
        self.client.connection = conn

        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        response = dataitem.store_data(test_data, "new", offset=None, description="NewDescription", tags=['tag1', 'tag2'])
        self.assertEquals(response, None)
        conn.make_transaction.assert_called_with(headers, '/store', 'Some test data to be sent to server')

        conn.reset_mock()
        test_data.seek(0)
        self.client.set_encryption_key("12345678901234561234567890123456")
        self.client.encryption_mode = ENC_AES256
        headers['X-HOLVI-META'] = 'v1:KHA:abcdef123456789:ENC:AES256::'

        response = dataitem.store_data(test_data, method="new", offset=None, key_hash="abcdef123456789")
        self.assertEquals(response, None)
        conn.make_transaction.assert_called_with(headers, '/store', 'Some test data to be sent to server')

        self.assertRaises(HolviDataItemException, dataitem.store_data, test_data, "new", offset=None, key_hash="abcdef123456789")

        conn.reset_mock()
        test_data.seek(0)
        file_iter = FileIterator(test_data, 4)
        test_md5 = hashlib.md5()
        test_md5.update('ver')
        self.client.set_encryption_key("")
        self.client.encryption_mode = ENC_NONE
        headers['X-HOLVI-META'] = 'v1:ENC:NONE::'
        headers['X-HOLVI-HASH'] = test_md5.hexdigest()
        headers['Content-Length'] = 3
        headers['X-HOLVI-STORE-MODE'] = "append"
        response = dataitem.store_data(file_iter, "new", offset=None)
        self.assertEquals(response, None)
        self.assertEquals(conn.make_transaction.mock_calls[8], mock.call(headers, '/store', 'ver'))

    def test_store_data_del_kha_del_cha(self):
        test_data = StringIO.StringIO("Some test data to be sent to server")
        md5 = hashlib.md5()
        md5.update(test_data.read())
        test_data.seek(0)
        test_data.get_content_hash = lambda: "aabbccddeeff1122"

        headers = {}
        headers['X-HOLVI-STORE-MODE'] = "replace"
        headers['X-HOLVI-KEY'] = base64.b64encode(self.keyname)
        headers['X-HOLVI-PARENT'] = self.parent_id
        headers['X-HOLVI-META'] = 'v1:TGS:tag1,tag2:ENC:NONE:DSC:NewDescription::'
        headers['Content-Type'] = 'application/octet-stream'
        headers['X-HOLVI-HASH'] = md5.hexdigest()
        headers['Content-Length'] = len(test_data.read())
        test_data.seek(0)

        conn = mock.Mock()
        conn.make_request.return_value = [{
            u'modified_date': None,
            u'name': self.keyname,
            u'md5sum': "aabbccddeeff1122",
            u'parent_id': self.parent_id,
            u'last_accessed_date': None,
            'meta': 'v1:TGS:tag1,tag2:ENC:AES128:DSC:NewDescription:KHA:ajsidoasj:CHA:ajsdoijas::',
            u'size': 999
        }]

        self.client.connection = conn
        self.client.set_encryption_key("")
        self.client.encryption_mode = ENC_NONE

        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        response = dataitem.store_data(test_data, "replace", offset=None, description="NewDescription", tags=['tag1', 'tag2'])
        self.assertEquals(response, None)
        conn.make_transaction.assert_called_once_with(headers, '/store', 'Some test data to be sent to server')

    def test_store_data_no_key_hash_exception(self):
        conn = self._mock_client_make_request(name=self.keyname,
                                              parent_id=self.parent_id,
                                              meta='v1:A:B:C:D:ENC:NONE::')
        conn.make_query.return_value = {}
        conn.make_transaction.return_value = None
        self.client.connection = conn
        self.client.encryption_mode = ENC_AES256

        test_data = StringIO.StringIO("Some test data to be sent to server")
        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        self.assertRaises(ClientException, dataitem.store_data, test_data, "append", 0)

    def test_store_with_patch(self):
        test_data = StringIO.StringIO("Some test data to be sent to server")
        md5 = hashlib.md5()
        md5.update(test_data.read())
        test_data.seek(0)
        headers = {}
        headers['X-HOLVI-STORE-MODE'] = "patch"
        headers['X-HOLVI-KEY'] = base64.b64encode(self.keyname)
        headers['X-HOLVI-PARENT'] = self.parent_id
        headers['X-HOLVI-META'] = 'v1:A:B:C:D:ENC:NONE::'
        headers['Content-Type'] = 'application/octet-stream'
        headers['X-HOLVI-HASH'] = md5.hexdigest()
        headers['X-HOLVI-OFFSET'] = 13
        headers['Content-Length'] = len(test_data.read())
        test_data.seek(0)

        response_headers = {'X-HOLVI-META': 'v1:A:B:C:D::'}
        conn = self._mock_client_make_request(name=self.keyname,
                                              parent_id=self.parent_id,
                                              meta='v1:A:B:C:D:ENC:NONE::',
                                              checksum=md5.hexdigest())
        conn.make_transaction.return_value = "OK"
        conn.make_query.return_value = response_headers  # Old headers
        self.client.connection = conn

        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        response = dataitem.store_data(test_data, "patch", offset=13)
        self.assertEquals(response, None)
        conn.make_transaction.assert_called_with(headers, '/store', 'Some test data to be sent to server')
        conn.reset_mock()
        test_data.seek(0)
        test_md5 = hashlib.md5()
        test_md5.update('ver')
        headers['X-HOLVI-HASH'] = test_md5.hexdigest()
        headers['X-HOLVI-OFFSET'] = 13 + len(test_data.read()) - 3  # start offset + len(content) - last chunk size
        headers['Content-Length'] = 3
        test_data.seek(0)
        file_iter = FileIterator(test_data, 4)

        response = dataitem.store_data(file_iter, "patch", offset=13)
        self.assertEquals(response, None)
        self.assertEquals(conn.make_transaction.mock_calls[8], mock.call(headers, '/store', 'ver'))

    def test_dataitem_size(self):
        self._mock_client_make_request(length=4321)
        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        response = dataitem.size

        self.assertEquals(response, 4321)
        self.assertNotEquals(dataitem.size, None)

    def test_dataitem_checksum(self):
        self._mock_client_make_request(checksum=4321)
        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        response = dataitem.md5sum

        self.assertEquals(response, "4321")
        self.assertNotEquals(dataitem.md5sum, None)

    def test_dataitem_modified_date(self):
        self._mock_client_make_request(modified_date="1234")
        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        response = dataitem.modified_date
        self.assertEquals(response, "1234")
        self.assertNotEquals(dataitem.modified_date, None)

    def test_dataitem_meta(self):
        self._mock_client_make_request(meta="v1:META:DATA::")
        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        response = dataitem.meta
        self.assertEquals(response, {'META': 'DATA', '__version__': 1})
        self.assertNotEquals(dataitem.meta, None)

    def test_dataitem_init_meta(self):
        self._mock_client_make_request(meta=None)
        meta = "v1:TEST:DATA::"
        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname, meta=meta)
        self.assertEquals(dataitem.meta, {'TEST': 'DATA', '__version__': 1})

    def test_dataitem_rename(self):
        conn = mock.Mock()
        self.client.connection = conn

        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        dataitem.rename('new_name2')
        params = {
                'parent_id': dataitem.parent_id,
                'name': self.keyname,
                'new_name': 'new_name2'
            }
        conn.make_request.assert_called_once_with('rename_dataitem', params)
        self.assertNotEquals(self.keyname, dataitem.name)

    def test_dataitem_relocate(self):
        conn = mock.Mock()
        self.client.connection = conn

        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        dataitem.relocate(6, 'new_name2')
        params = {
                'parent_id': dataitem.parent_id,
                'name': dataitem.name,
                'new_parent_id': 6,
                'new_name': 'new_name2'
            }
        conn.make_request.assert_called_once_with('relocate_dataitem', params)

    def test_dataitem_remove(self):
        conn = mock.Mock()
        self.client.connection = conn

        dataitem = DataItem(self.client, parent_id=self.parent_id, name=self.keyname)
        dataitem.remove()
        params = {
                'parent_id': dataitem.parent_id,
                'name': dataitem.name
            }
        conn.make_request.assert_called_once_with('remove_dataitem', params)
