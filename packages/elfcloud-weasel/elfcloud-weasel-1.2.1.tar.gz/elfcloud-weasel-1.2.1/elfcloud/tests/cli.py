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
