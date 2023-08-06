#!/usr/bin/env python
"""Test xnt.tasks.cp"""

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
class TaskCopyTests(unittest.TestCase):
    """Test Case for Copy Tasks Method"""
    def setUp(self):
        """Test Setup"""
        xnt.tests.set_up()

    def tearDown(self):
        """Test Teardown"""
        xnt.tests.tear_down()

    def test_cp(self):
        """Test default use of cp"""
        xnt.tasks.cp("temp/testfolder1", "temp/testfolder2")
        self.assertTrue(os.path.exists("temp/testfolder2"))
        self.assertTrue(os.path.exists("temp/testfolder1"))
        xnt.tasks.cp("temp/testfile1", "temp/testfile5")
        self.assertTrue(os.path.exists("temp/testfile5"))
        self.assertTrue(os.path.exists("temp/testfile1"))
        with open("temp/testfile5", "r") as testfile:
            self.assertEqual("this is a test file", testfile.read())

    def test_cp_filelist(self):
        """Test filelist copy"""
        xnt.tasks.cp(dst="temp/testfolder2",
                     files=["temp/testfile1",
                            "temp/testfile2",
                            "temp/testfile3"])
        self.assertTrue(os.path.exists("temp/testfile1"))
        self.assertTrue(os.path.exists("temp/testfile2"))
        self.assertTrue(os.path.exists("temp/testfile3"))
        with open("temp/testfile2", "r") as testfile:
            self.assertEqual("this is a test file", testfile.read())


if __name__ == "__main__":
    unittest.main()
