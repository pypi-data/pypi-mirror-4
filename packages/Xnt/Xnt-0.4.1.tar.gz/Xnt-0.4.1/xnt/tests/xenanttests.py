
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
import xnt
import xnt.tasks
import xnt.xenant as xenant
import unittest


class XenantTests(unittest.TestCase):
    def setUp(self):
        os.mkdir("temp")

    def tearDown(self):
        shutil.rmtree("temp")

    def test_version(self):
        actual = xenant.version()
        self.assertEqual(xnt.__version__, xenant.version())

if __name__ == "__main__":
    unittest.main()
