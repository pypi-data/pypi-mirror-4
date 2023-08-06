#!/usr/bin/env python
"""Xenant Arg Parser Tests"""

#   Xnt -- A Wrapper Build Tool
#   Copyright (C) 2013  Kenny Ballou

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import xnt.xenant
import unittest

#pylint: disable-msg=C0103
class XenantArgParserTests(unittest.TestCase):
    """Test Cases for Xenant Args Parsing"""

    def test_nil_args(self):
        """Test the empty case (no arguements)"""
        args_in = []
        args = xnt.xenant.parse_args(args_in)
        self.assertIsNotNone(args)
        self.assertFalse(args["verbose"])
        self.assertFalse(args["list-targets"])
        self.assertIsNone(args["properties"])
        self.assertIsNotNone(args["targets"])
        self.assertEqual(len(args["targets"]), 0)

    def test_single_target(self):
        """Test the single target case"""
        args_in = ["my_target"]
        args = xnt.xenant.parse_args(args_in)
        self.assertIsNotNone(args)
        self.assertFalse(args["verbose"])
        self.assertFalse(args["list-targets"])
        self.assertIsNone(args["properties"])
        self.assertIsNotNone(args["targets"])
        self.assertEqual(len(args["targets"]), 1)

    def test_verbose(self):
        """Test verbose flag"""
        args_in = ["-v"]
        args = xnt.xenant.parse_args(args_in)
        self.assertIsNotNone(args)
        self.assertTrue(args["verbose"])
        self.assertFalse(args["list-targets"])
        self.assertIsNone(args["properties"])
        self.assertIsNotNone(args["targets"])
        self.assertEqual(len(args["targets"]), 0)

    def test_list_targets_short(self):
        """Test list targets flag, short hand"""
        args_in = ["-l"]
        args = xnt.xenant.parse_args(args_in)
        self.assertIsNotNone(args)
        self.assertFalse(args["verbose"])
        self.assertTrue(args["list-targets"])
        self.assertIsNone(args["properties"])
        self.assertIsNotNone(args["targets"])
        self.assertEqual(len(args["targets"]), 0)

    def test_list_targets_long(self):
        """Test list targets flag, long hand"""
        args_in = ["--list-targets"]
        args = xnt.xenant.parse_args(args_in)
        self.assertIsNotNone(args)
        self.assertFalse(args["verbose"])
        self.assertTrue(args["list-targets"])
        self.assertIsNone(args["properties"])
        self.assertIsNotNone(args["targets"])
        self.assertEqual(len(args["targets"]), 0)

    def test_single_verbose(self):
        """Test the verbose single case"""
        args_in = ["-v", "my_verbose_target"]
        args = xnt.xenant.parse_args(args_in)
        self.assertIsNotNone(args)
        self.assertTrue(args["verbose"])
        self.assertFalse(args["list-targets"])
        self.assertIsNone(args["properties"])
        self.assertIsNotNone(args["targets"])
        self.assertEqual(len(args["targets"]), 1)

    def test_multi_target(self):
        """Test the verbose single case"""
        args_in = ["my_first_target", "my_second_target"]
        args = xnt.xenant.parse_args(args_in)
        self.assertIsNotNone(args)
        self.assertFalse(args["verbose"])
        self.assertFalse(args["list-targets"])
        self.assertIsNone(args["properties"])
        self.assertIsNotNone(args["targets"])
        self.assertEqual(len(args["targets"]), 2)

    def test_properties_no_target(self):
        """Test property parsing"""
        args_in = ["-Dmyvar=myvalue"]
        args = xnt.xenant.parse_args(args_in)
        self.assertIsNotNone(args)
        self.assertFalse(args["verbose"])
        self.assertFalse(args["list-targets"])
        self.assertIsNotNone(args["properties"])
        self.assertEqual(len(args["properties"]), 1)
        self.assertEqual(args["properties"][0], "myvar=myvalue")
        self.assertIsNotNone(args["targets"])
        self.assertEqual(len(args["targets"]), 0)

    def test_more_properties(self):
        """Test property parsing"""
        args_in = ["-Dmyvar=myvalue", "-Dmyothervar=myothervalue"]
        args = xnt.xenant.parse_args(args_in)
        self.assertIsNotNone(args)
        self.assertFalse(args["verbose"])
        self.assertFalse(args["list-targets"])
        self.assertIsNotNone(args["properties"])
        self.assertEqual(len(args["properties"]), 2)
        self.assertEqual(args["properties"][0], "myvar=myvalue")
        self.assertEqual(args["properties"][1], "myothervar=myothervalue")
        self.assertIsNotNone(args["targets"])
        self.assertEqual(len(args["targets"]), 0)

    def test_build_file_spec_short(self):
        """Test build file option"""
        args_in = ["-b", "mybuildfile.py"]
        args = xnt.xenant.parse_args(args_in)
        self.assertIsNotNone(args)
        self.assertFalse(args["verbose"])
        self.assertFalse(args["list-targets"])
        self.assertIsNotNone(args["build-file"])
        self.assertEqual(args["build-file"], "mybuildfile.py")
        self.assertIsNone(args["properties"])
        self.assertIsNotNone(args["targets"])
        self.assertEqual(len(args["targets"]), 0)

    def test_build_file_spec_long(self):
        """Test build file option"""
        args_in = ["--build-file", "mybuildfile.py"]
        args = xnt.xenant.parse_args(args_in)
        self.assertIsNotNone(args)
        self.assertFalse(args["verbose"])
        self.assertFalse(args["list-targets"])
        self.assertIsNotNone(args["build-file"])
        self.assertEqual(args["build-file"], "mybuildfile.py")
        self.assertIsNone(args["properties"])
        self.assertIsNotNone(args["targets"])
        self.assertEqual(len(args["targets"]), 0)

if __name__ == "__main__":
    unittest.main()
