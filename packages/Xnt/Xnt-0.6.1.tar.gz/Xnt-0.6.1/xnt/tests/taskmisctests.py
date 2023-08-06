#!/usr/bin/env python
"""Misc Tasks Tests"""

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

import os
import xnt.tasks
import xnt.tests
import unittest

#pylint: disable-msg=C0103
class TaskMiscTests(unittest.TestCase):
    """Test Misc Tasks"""
    def setUp(self):
        """Test Case Setup"""
        xnt.tests.set_up()

    def tearDown(self):
        """Test Case Teardown"""
        xnt.tests.tear_down()

    def test_echo(self):
        """Test Echo Task"""
        xnt.tasks.echo("this is my cool echo", "temp/mynewcoolfile")
        self.assertTrue(os.path.exists("temp/mynewcoolfile"))
        with open("temp/mynewcoolfile", "r") as temp_file:
            self.assertEqual("this is my cool echo", temp_file.read())

    def test_call(self):
        """Test Call, testing redirection"""
        out = open("temp/testout", "w")
        err = open("temp/testerr", "w")
        xnt.tasks.call(["python",
                        os.path.abspath("temp/test.py"),
                        "42", "hello"],
                       out,
                       err)
        out.close()
        err.close()
        self.assertTrue(os.path.exists("temp/testout"))
        self.assertTrue(os.path.exists("temp/testerr"))
        with open("temp/testout", "r") as std_out:
            self.assertEqual("42", std_out.read())
        with open("temp/testerr", "r") as std_err:
            self.assertEqual("hello", std_err.read())

if __name__ == "__main__":
    unittest.main()
