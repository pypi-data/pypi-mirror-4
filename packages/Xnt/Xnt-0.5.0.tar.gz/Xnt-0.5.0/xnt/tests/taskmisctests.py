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


class TaskMiscTests(unittest.TestCase):
    def setUp(self):
        os.mkdir("temp")
        os.mkdir("temp/testfolder1")
        for i in range(1, 5):
            with open("temp/testfile" + str(i), "w") as f:
                f.write("this is a test file")
        with open("temp/test.py", "w") as test:
            test.write("#!/usr/bin/env python\n")
            test.write("import sys\n")
            test.write("sys.stdout.write(sys.argv[1])\n")
            test.write("sys.stderr.write(sys.argv[2])\n")

    def tearDown(self):
        shutil.rmtree("temp")

    def test_echo(self):
        xnt.tasks.echo("this is my cool echo", "temp/mynewcoolfile")
        self.assertTrue(os.path.exists("temp/mynewcoolfile"))
        with open("temp/mynewcoolfile", "r") as f:
            self.assertEqual("this is my cool echo", f.read())

    def test_call(self):
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
        with open("temp/testout", "r") as o:
            self.assertEqual("42", o.read())
        with open("temp/testerr", "r") as e:
            self.assertEqual("hello", e.read())

if __name__ == "__main__":
    unittest.main()
