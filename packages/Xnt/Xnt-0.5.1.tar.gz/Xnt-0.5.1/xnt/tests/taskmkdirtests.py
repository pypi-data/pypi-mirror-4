#!/usr/bin/env python

#   Xnt -- A Wrapper Build Tool
#   Copyright (C) 2012  Kenny Ballou

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

import sys
import os
import shutil
import xnt.tasks
import unittest


class TaskMkdirTests(unittest.TestCase):
    def setUp(self):
        os.mkdir("temp")
        os.mkdir("temp/testfolder1")
        for i in range(1, 5):
            with open("temp/testfile" + str(i), "w") as f:
                f.write("this is a test file")

    def tearDown(self):
        shutil.rmtree("temp")

    def test_mkdir(self):
        xnt.tasks.mkdir("temp/mynewtestfolder")
        self.assertTrue(os.path.exists("temp/mynewtestfolder"))
        self.assertTrue(os.path.exists("temp/testfolder1"))
        xnt.tasks.mkdir("temp/testfolder1")


if __name__ == "__main__":
    unittest.main()
