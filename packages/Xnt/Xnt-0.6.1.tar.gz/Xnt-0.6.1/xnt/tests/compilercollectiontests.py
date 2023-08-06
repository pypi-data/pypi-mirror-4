#!/usr/bin/env python
"""Test Common Compiler Collection"""

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
import xnt.build.cc as cc
import unittest

#http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    """Similar to Linux/Unix `which`: return path of executable"""
    def is_exe(fpath):
        """Determine if arguement exists and is executable"""
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath = os.path.split(program)
    if fpath[0]:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

#pylint: disable-msg=C0103
@unittest.skipUnless(which("gcc"), "gcc is not in your path")
class GccTests(unittest.TestCase):
    """Test GCC"""
    def setUp(self):
        """Test Case Setup"""
        os.mkdir("temp")
        with open("temp/hello.c", "w") as test_code:
            test_code.write("""
            #include <stdio.h>
            int main() {
                printf("Hello, World!\\n");
                return 0;
            }
            """)

    def tearDown(self):
        """Test Case Teardown"""
        shutil.rmtree("temp")

    def test_gcc(self):
        """Test Default GCC"""
        cwd = os.getcwd()
        os.chdir("temp")
        cc.gcc("hello.c")
        self.assertTrue(os.path.isfile("a.out"))
        os.chdir(cwd)

    def test_gcc_o(self):
        """Test GCC with output"""
        cc.gcc_o("temp/hello.c", "temp/hello")
        self.assertTrue(os.path.isfile("temp/hello"))

@unittest.skipUnless(which("g++"), "g++ is not in your path")
class GppTests(unittest.TestCase):
    """Test G++ (C++ GCC)"""
    def setUp(self):
        """Test Case Setup"""
        os.mkdir("temp")
        with open("temp/hello.cpp", "w") as test_code:
            test_code.write("""
            #include <iostream>
            int main() {
                std::cout << "Hello, World!" << std::endl;
                return 0;
            }
            """)

    def tearDown(self):
        """Test Case Teardown"""
        shutil.rmtree("temp")

    def test_gpp(self):
        """Test Default G++"""
        cwd = os.getcwd()
        os.chdir("temp")
        cc.gpp("hello.cpp")
        self.assertTrue("a.out")
        os.chdir(cwd)

    def test_gpp_o(self):
        """Test G++ with output"""
        cc.gpp_o("temp/hello.cpp", "temp/hello")
        self.assertTrue(os.path.isfile("temp/hello"))

@unittest.skipUnless(which("javac"), "javac is not in your path")
class JavacTests(unittest.TestCase):
    """Test Javac"""
    def setUp(self):
        """Test Case Setup"""
        os.mkdir("temp")
        with open("temp/hello.java", "w") as test_code:
            test_code.write("""
            class hello {
                public static void main(String[] args) {
                    System.out.println("Hello, World!");
                }
            }
            """)

    def tearDown(self):
        """Test Case Teardown"""
        shutil.rmtree("temp")

    def test_javac(self):
        """Test Default Javac"""
        cwd = os.getcwd()
        os.chdir("temp")
        cc.javac("hello.java")
        self.assertTrue(os.path.isfile("hello.class"))
        os.chdir(cwd)

if __name__ == "__main__":
    unittest.main()
