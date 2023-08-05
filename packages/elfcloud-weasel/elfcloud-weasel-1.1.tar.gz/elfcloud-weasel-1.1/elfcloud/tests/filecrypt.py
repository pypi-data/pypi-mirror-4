import unittest
import StringIO
import hashlib

from elfcloud.exceptions import (
        HolviCryptException
    )
from elfcloud.filecrypt import FileIterator, FileCrypt


class TestFileHandling(unittest.TestCase):

    def test_crypt_iterator(self):
        original_data = StringIO.StringIO("test data to be iterated")

        enc_iterator = FileCrypt('Invalidkey', '1234567890123456')
        self.assertRaises(HolviCryptException, enc_iterator.encrypt, original_data, 1)

        enc_iterator = FileCrypt('12345678901234561234567890123456', 'InvalidIV')
        self.assertRaises(HolviCryptException, enc_iterator.encrypt, original_data, 1)

        enc_iterator = FileCrypt('Invalidkey', 'InvalidIV')
        self.assertRaises(HolviCryptException, enc_iterator.encrypt, original_data, 1)

        enc_iterator = FileCrypt('12345678901234561234567890123456', '1234567890123456')

        data_enc_out = StringIO.StringIO()
        encrypt = enc_iterator.encrypt(original_data, 1)
        for data in encrypt:
            data_enc_out.write(data)

        data_enc_out.seek(0)
        self.assertNotEqual(original_data.read(), data_enc_out.read())
        data_enc_out.seek(0)

        data_dec_out = StringIO.StringIO()

        dec_iterator = FileCrypt('Invalidkey', '1234567890123456')
        self.assertRaises(HolviCryptException, dec_iterator.decrypt, data_enc_out, 1)

        dec_iterator = FileCrypt('12345678901234561234567890123456', 'InvalidIV')
        self.assertRaises(HolviCryptException, dec_iterator.decrypt, data_enc_out, 1)

        dec_iterator = FileCrypt('Invalidkey', 'InvalidIV')
        self.assertRaises(HolviCryptException, dec_iterator.decrypt, data_enc_out, 1)

        dec_iterator = FileCrypt('12345678901234561234567890123456', '1234567890123456')
        decrypt = dec_iterator.decrypt(data_enc_out, 1)

        for data in decrypt:
            data_dec_out.write(data)

        original_data.seek(0), data_dec_out.seek(0)
        self.assertEquals(original_data.read(), data_dec_out.read())

    def test_crypt_iterator_content_hash(self):
        original_data = StringIO.StringIO("test data to be iterated")
        iterator = FileCrypt('12345678901234561234567890123456', '1234567890123456')
        enc_iter = iterator.encrypt(original_data)
        for enc_data in enc_iter:
            pass
        original_data.seek(0)

        content_hash = hashlib.md5()
        content_hash.update(original_data.read())
        content_hash = content_hash.hexdigest()

        self.assertEquals(content_hash, enc_iter.get_content_hash())

    def test_file_iterator(self):
        original_data = StringIO.StringIO("test data to be iterated")

        file_iterator = FileIterator(original_data, 1)

        iter_out = StringIO.StringIO()
        for data in file_iterator:
            iter_out.write(data)

        original_data.seek(0), iter_out.seek(0)
        self.assertEquals(original_data.read(), iter_out.read())
