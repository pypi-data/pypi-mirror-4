# -*- coding: utf-8 -*-
import re
import hashlib

from .exceptions import HolviCryptException
from .exceptions import ClientMetaException
from .exceptions import ClientKeyFileException

ENC_NONE = "NONE"
ENC_AES128 = "AES128"
ENC_AES192 = "AES192"
ENC_AES256 = "AES256"
IV_DEFAULT = "1234567890123456"
SERVER_DEFAULT = "https://api.elfcloud.fi/"
APIKEY_DEFAULT = "atk8vzrhnc2by4f"
VAULT_TYPE_DEFAULT = "fi.elfcloud.datastore"


def validate_encryption_mode(level, throw_exception=True):
    if level in [ENC_NONE, ENC_AES128, ENC_AES192, ENC_AES256]:
        return True
    if throw_exception:
        raise HolviCryptException(901, 'Invalid encryption mode')
    return False


class MetaParser(object):
    @staticmethod
    def deserialize_tags(tags_string):
        return [x.decode('ascii') for x in tags_string.split(",")]

    @staticmethod
    def deserialize(meta_string):
        result_dict = {}

        match_parts = re.compile('((?:\\\\.|[^\\\\:])*)(?::|$)')

        if not meta_string.startswith("v") or len(meta_string) < 4:
            raise ClientMetaException("Invalid meta header")

        result_dict['__version__'] = int(meta_string[1])

        if len(meta_string) <= 4:
            return result_dict

        keyvalue_string = meta_string[3:-2]
        parts = match_parts.findall(keyvalue_string)

        for i in range(0, len(parts), 2):
            key = parts[i]
            value = None

            if key == '':
                continue

            try:
                value = parts[i + 1]
                value = re.sub(r'\\(.)', r'\1', value.decode("ascii"))
            except:
                raise ClientMetaException(u"Error while parsing value for key '{0}'".format(key))

            if key == "TGS":
                value = MetaParser.deserialize_tags(value)
            if key == 'ENC':
                validate_encryption_mode(value)

            if key in result_dict:
                raise ClientMetaException("Multiple values for same key")

            result_dict[key] = value

        return result_dict

    @staticmethod
    def serialize(meta_dict):
        meta_dict = meta_dict.copy()

        version = meta_dict.pop('__version__', None)
        if version is None:
            raise ClientMetaException("No version specified")

        meta_list = []
        for key in meta_dict:
            value = meta_dict[key]

            if key == 'TGS':
                for tag in value:
                    if ',' in tag:
                        raise ClientMetaException("Comma is not allowed in tag")
                value = ",".join(value)

            ascii_key = key.encode("ascii")
            ascii_value = value.encode("ascii")
            meta_list.extend([ascii_key, ascii_value])

        meta_string = "v{0}:".format(version)
        meta_string += ':'.join(meta_list)
        meta_string += "::"
        return meta_string


class KeyFile(object):
    @staticmethod
    def parse_from_file(fh):
        iv = fh.read(16)
        key = fh.read()

        if len(iv) != 16:
            raise ClientKeyFileException("Invalid key file (file too short)")

        if len(key) not in [32, 24, 16]:  # Only 128, 192 and 256 bytes supported
            raise ClientKeyFileException("Invalid key file (invalid key size)")

        return iv, key

    @staticmethod
    def calc_hash(iv, key):
        final_hash = iv + key
        for i in range(0, 10000):
            m = hashlib.md5()
            m.update(final_hash)
            final_hash = m.digest()
        return final_hash.encode("hex")
