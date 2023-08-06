#!/usr/bin/env python
"""Test `xnt.tasks.rm`"""

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
class TaskRemoveTests(unittest.TestCase):
    """Test Case for Remove"""
    def setUp(self):
        """Test case Setup"""
        xnt.tests.set_up()

    def tearDown(self):
        """Test case Teardown"""
        xnt.tests.tear_down()

    def test_rm(self):
        """Remove cases"""
        xnt.tasks.rm("temp/testfolder1")
        self.assertFalse(os.path.exists("temp/testfolder1"))
        xnt.tasks.rm("temp/testfile1")


if __name__ == "__main__":
    unittest.main()
