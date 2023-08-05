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
import os
import StringIO
from elfcloud.exceptions import (
        ClientMetaException,
        ClientKeyFileException,
        ECCryptException
    )
from elfcloud.utils import MetaParser
from elfcloud.utils import KeyFile
from elfcloud.utils import validate_encryption_mode

import unittest2 as unittest
from nose.plugins.skip import SkipTest


class ValidateEncryptionTestCase(unittest.TestCase):
    def test_return_false(self):
        self.assertFalse(validate_encryption_mode('Unknown', False))


class MetaParserDeserializeTestCase(unittest.TestCase):
    def _makeOne(self, string):
        print string
        return MetaParser.deserialize(string)

    def _parse_test(self, test_string):
        self.assertRaises(ClientMetaException, self._makeOne, test_string)

    def test_must_fail_abcd(self):
        self._parse_test("abcd")

    def test_must_fail_multiple_keys(self):
        self._parse_test("v1:KEY:VALUE:KEY:VALUE::")

    def test_must_fail_invalid_termintation(self):
        raise SkipTest  # Reported bug #206
        self._parse_test("v1:KEY:VALUE:KEY2:VALUE:::")

    def test_must_fail_invalid_termination_and_escaped_valued(self):
        raise SkipTest  # Reported bug #206
        self._parse_test('v1:AVAIN2:ARVO\::')

    def test_parse_invalid_end_term_with_escaped_value(self):
        test_string = "v1:AVAIN2:ARVO\:::"
        result = {
            '__version__': 1,
            'AVAIN2': "ARVO:"
        }
        self.assertEquals(result, self._makeOne(test_string))

    def test_parse_empty_value(self):
        test_string = "v1:AVAIN2:ARVO:AVAIN:::"
        result = {
            '__version__': 1,
            'AVAIN': '',
            'AVAIN2': "ARVO"
        }
        self.assertEquals(result, self._makeOne(test_string))

    def test_parse_escaped_value(self):
        test_string = 'v1:AVAIN2:ARV\:\:O\\\\:AVAIN:::'
        result = {
                    '__version__': 1,
                    'AVAIN': '',
                    'AVAIN2': "ARV::O\\"
                }
        self.assertEquals(result, self._makeOne(test_string))

    def test_parse_empty_meta(self):
        test_string = 'v1::'
        result = {'__version__': 1}
        self.assertEquals(result, self._makeOne(test_string))

    def test_parse_empty_meta2(self):
        test_string = 'v1:::'
        result = {'__version__': 1}
        self.assertEquals(result, self._makeOne(test_string))

    def test_parse_enc_type(self):
        test_string = 'v1:ENC:UNKNOWN::'
        self.assertRaises(ECCryptException, self._makeOne, test_string)

    def test_parse_invalid_utf8_value(self):
        test_string = 'v1:AVAIN1:DATA\xff\u2200::'
        self.assertRaises(ClientMetaException, self._makeOne, test_string)


class MetaParserSerializeTestCase(unittest.TestCase):
    def _makeOne(self, meta_dict):
        print meta_dict
        return MetaParser.serialize(meta_dict)

    def test_no_version(self):
        self.assertRaises(ClientMetaException, self._makeOne, {'a': 'b'})

    def test_commas_in_tags(self):
        self.assertRaises(ClientMetaException, self._makeOne, {
            '__version__': 1,
            'TGS': ['tag1', 'tag,error', 'tag3']
        })


class KeyFileParserTestCase(unittest.TestCase):
    @property
    def _makeOne(self):
        return KeyFile.parse_from_file

    def generate_key(self, iv_len, key_len):
        iv, key = os.urandom(iv_len), os.urandom(key_len)
        return StringIO.StringIO(iv + key), iv, key

    def test_parse_file_aes256(self):
        fh, iv, key = self.generate_key(16, 32)
        self.assertEquals((iv, key), self._makeOne(fh))

    def test_parse_file_aes192(self):
        fh, iv, key = self.generate_key(16, 24)
        self.assertEquals((iv, key), self._makeOne(fh))

    def test_parse_file_aes128(self):
        fh, iv, key = self.generate_key(16, 16)
        self.assertEquals((iv, key), self._makeOne(fh))

    def test_parse_file_invalid_key_length(self):
        fh, iv, key = self.generate_key(16, 10)
        self.assertRaises(ClientKeyFileException, self._makeOne, fh)

    def test_parse_file_too_long_key_length(self):
        fh, iv, key = self.generate_key(16, 100)
        self.assertRaises(ClientKeyFileException, self._makeOne, fh)

    def test_parse_file_zero_key_length(self):
        fh, iv, key = self.generate_key(16, 0)
        self.assertRaises(ClientKeyFileException, self._makeOne, fh)

    def test_parse_file_invalid_iv_length(self):
        fh, iv, key = self.generate_key(15, 0)
        self.assertRaises(ClientKeyFileException, self._makeOne, fh)

    def test_parse_file_zero_length(self):
        fh, iv, key = self.generate_key(0, 0)
        self.assertRaises(ClientKeyFileException, self._makeOne, fh)
