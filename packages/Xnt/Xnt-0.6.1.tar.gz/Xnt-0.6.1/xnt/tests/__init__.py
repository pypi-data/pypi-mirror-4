#!/usr/bin/env python
"""Tests Module"""

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
import shutil

def set_up():
    """Shared Setup Code"""
    os.mkdir("temp")
    os.mkdir("temp/testfolder1")
    for i in range(1, 5):
        with open("temp/testfile" + str(i), "w") as test_file:
            test_file.write("this is a test file")
    with open("temp/test.py", "w") as test:
        test.write("#!/usr/bin/env python\n")
        test.write("import sys\n")
        test.write("sys.stdout.write(sys.argv[1])\n")
        test.write("sys.stderr.write(sys.argv[2])\n")

def tear_down():
    """Shared Teardown Code"""
    shutil.rmtree("temp")
