import elfcloud.cli

import argparse
import unittest
import mock


class TestTagParser(unittest.TestCase):
    def test_tags_parse(self):
        self.assertEquals(['test', 'test'], elfcloud.cli.tag_parser('test,test'))

    def test_tags_parse_error(self):
        self.assertRaises(argparse.ArgumentTypeError, elfcloud.cli.tag_parser, None)


class TestParseArgs(unittest.TestCase):
    def test_args_parse(self):
        self.assertRaises(SystemExit, elfcloud.cli.parse_args, [])


class TestCLIMain(unittest.TestCase):
    @mock.patch("elfcloud.cli.parse_args")
    def test_main(self, mock_parse_args):
        mock_args = mock.Mock()
        mock_parser = mock.Mock()
        mock_parse_args.return_value = mock_args, mock_parser

        mock_args.user = "user"
        mock_args.password = "pass"

        mock_args.func = mock.Mock()

        elfcloud.cli.main([])
