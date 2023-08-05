# -*- coding: utf-8 -*-

import utils
import filecrypt
import hashlib
import base64
from elfcloud.exceptions import HolviDataItemException
from elfcloud.exceptions import ClientException


class DataItem(object):
    """DataItem provides methods for handling data.

    """

    @property
    def description(self):
        if not self._info_retrieved:
            self._get_item_info()
        return self.meta.get("DSC")

    @property
    def tags(self):
        if not self._info_retrieved:
            self._get_item_info()
        return self.meta.get("TGS")

    @property
    def content_hash(self):
        if not self._info_retrieved:
            self._get_item_info()
        return self.meta.get("CHA")

    @property
    def key_hash(self):
        if not self._info_retrieved:
            self._get_item_info()
        return self.meta.get("KHA")

    @property
    def data(self):
        """Returns a dict that contains DataItem checksum and data.
        Queries the elfCLOUD.fi server with dataitems's parent ID and returns a dictionary.
        Dictionary contains keys 'data' and 'checksum'.

        """
        headers = {}
        headers['X-HOLVI-KEY'] = base64.b64encode(self.name.encode("utf-8"))
        headers['X-HOLVI-PARENT'] = self.parent_id
        url_suffix = "/fetch"

        response = self._client.connection.make_transaction(headers, url_suffix)

        checksum = response.headers.get('X-HOLVI-HASH')
        if self._client.encryption_mode == utils.ENC_AES256:
            self.key_data = self._client.crypt.decrypt(response, self._client._request_size)
        else:
            self.key_data = filecrypt.FileIterator(response, self._client._request_size)

        return {'data': self.key_data,
                'checksum': checksum}

    def __init__(self, client, **kwargs):
        """Initializer for DataItem.

        :param client: Client used by DataItem methods.
        :param parent_id: ID number of the Vault/Cluster where the DataItem is in.
        :param key: Name of the dataitem.

        """
        self._client = client
        self._info_retrieved = False

        if 'meta' in kwargs:
            if type(kwargs['meta']) == dict:
                meta_dict = kwargs.pop('meta')
                if not '__version__' in meta_dict:
                    meta_dict['__version__'] = 1  # TODO: Should use Client.__META_VERSION__
                kwargs['meta'] = utils.MetaParser.serialize(meta_dict)
            self._set_raw_meta(kwargs['meta'])

        self.name = kwargs.get("name")
        self.parent_id = kwargs.get("parent_id")

    def __getattribute__(self, name):
        dynamic_attrs = [
            'last_accesed_date',
            'modified_date',
            'md5sum',
            'meta',
            'raw_meta',
            'size'
        ]
        if name == 'meta':
            try:
                return object.__getattribute__(self, name)
            except:
                pass
        if name in dynamic_attrs and self._info_retrieved == False:
            self._get_item_info()
        return object.__getattribute__(self, name)

    def _set_raw_meta(self, meta_string):
        update_dict = {
            'raw_meta': meta_string,
            'meta': utils.MetaParser.deserialize(meta_string)
        }
        self.__dict__.update(update_dict)

    def _update(self):
        if not self._info_retrieved:
            self._get_item_info()

        method = 'update_dataitem'
        params = {
            'parent_id': self.parent_id,
            'name': self.name,
            'meta': utils.MetaParser.serialize(self.meta)
        }
        return self._client.connection.make_request(method, params)

    def _get_item_info(self, result=None):
        """Queries elfCLOUD.fi server for DataItem information.

        """
        if result is None:
            method = 'list_dataitems'
            params = {
                'parent_id': self.parent_id,
                'names': [self.name],
            }
            result = self._client.connection.make_request(method, params)
            if len(result) <= 0:
                raise ClientException("DataItem does not exist")
            result = result[0]

        self._set_raw_meta(result.pop('meta', ''))
        self.__dict__.update(result)
        self._info_retrieved = True

    def update(self, description, tags):
        """Updates dataitem description and tags.

        :param description: New description for dataitem. If None, then old value is preserved.
        :param tags: New list of tags for dataitem. If None, then old value is preserved.
        """
        if not self._info_retrieved:
            self._get_item_info()
        if description is not None:
            self.meta['DSC'] = description
        if tags is not None:
            self.meta['TGS'] = tags

        self._update()

    def rename(self, new_name):
        """Renames dataitem.

        :param new_name: New name for dataitem.
        """
        method = 'rename_dataitem'
        params = {
            'parent_id': self.parent_id,
            'name': self.name,
            'new_name': new_name
        }
        r_value = self._client.connection.make_request(method, params)
        self.name = new_name
        return r_value

    def relocate(self, new_id, new_name):
        """Relocates dataitem.

        :param new_id: New parent id.
        :param new_id: New name for dataitem.
        """
        method = 'relocate_dataitem'
        params = {
            'parent_id': self.parent_id,
            'name': self.name,
            'new_parent_id': new_id,
            'new_name': new_name
        }
        return self._client.connection.make_request(method, params)

    def store_data(self, data, method, offset=None, description=None, tags=None, key_hash=None):
        """Stores data to elfCLOUD.fi server.

        :param data: File-like object to be stored.
        :param method: Storing method ['new', 'replace', 'patch', 'append'].
        :param offset: Starting byte when using method 'patch'.
        :param description: New description for the dataitem. If None, then
                            description preserved from existing dataitem.
        :param description: New tag-list for the dataitem. If None, then
                            tag-list preserved from existing dataitem.

        """

        headers = {}
        headers['X-HOLVI-STORE-MODE'] = method
        headers['X-HOLVI-KEY'] = base64.b64encode(self.name.encode("utf-8"))
        headers['X-HOLVI-PARENT'] = self.parent_id

        meta_dict = {}
        if method != 'new':
            if not self._info_retrieved:
                self._get_item_info()
            meta_dict = self.meta

        if method == 'patch':
            if offset is None:
                raise ClientException("Offset must be given when using 'patch'-method")
            headers['X-HOLVI-OFFSET'] = int(offset)

        meta_dict.update({
            '__version__': self._client.__META_VERSION__,
            'ENC': self._client._encryption_mode,
        })

        if description is not None:
            meta_dict['DSC'] = description
        if tags is not None:
            meta_dict['TGS'] = tags

        # Remove KHA if current encryption is disabled
        if self._client._encryption_mode == utils.ENC_NONE and \
           'KHA' in meta_dict:
            del meta_dict['KHA']

        # Enforce KHA, if encryption is enabled
        if self._client._encryption_mode != utils.ENC_NONE:
            if key_hash is None:
                raise ClientException("No key hash given when encryption enabled")
            meta_dict['KHA'] = key_hash

        # CHA is updated after succeeded store
        if 'CHA' in meta_dict:
            del meta_dict['CHA']

        headers['X-HOLVI-META'] = utils.MetaParser.serialize(meta_dict)

        headers['Content-Type'] = 'application/octet-stream'
        url_suffix = "/store"

        try:
            data_chunk = data.next()
            md5 = hashlib.md5()
            md5.update(data_chunk)
            headers['X-HOLVI-HASH'] = md5.hexdigest()
            headers['Content-Length'] = len(data_chunk)
            self._client.connection.make_transaction(headers, url_suffix, data_chunk)
            if method == 'patch':
                offset += len(data_chunk)
        except StopIteration:
            raise HolviDataItemException(700, "Empty content")

        for data_chunk in data:
            md5 = hashlib.md5()
            md5.update(data_chunk)
            headers['X-HOLVI-HASH'] = md5.hexdigest()
            headers['Content-Length'] = len(data_chunk)
            if method != 'patch':
                headers['X-HOLVI-STORE-MODE'] = 'append'
            elif method == 'patch':
                headers['X-HOLVI-OFFSET'] = offset
                offset += len(data_chunk)
            self._client.connection.make_transaction(headers, url_suffix, data_chunk)

        # Calculating CHA is only possible when using new or replace modes
        if method in ['replace', 'new']:
            meta_dict['CHA'] = data.get_content_hash()
            self._set_raw_meta(utils.MetaParser.serialize(meta_dict))
            self._update()

    def remove(self):
        """Removes dataitem using it's parent_id and name (key).

        """
        method = "remove_dataitem"
        params = {
            'parent_id': self.parent_id,
            'name': self.name
            }
        return self._client.connection.make_request(method, params)
