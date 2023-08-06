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
import xnt.build.cc as cc
import unittest

#http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

@unittest.skipUnless(which("gcc"), "gcc is not in your path")
class gccTests(unittest.TestCase):
    def setUp(self):
        os.mkdir("temp")
        with open("temp/hello.c", "w") as f:
            f.write("""
            #include <stdio.h>
            int main() {
                printf("Hello, World!\\n");
                return 0;
            }
            """)

    def tearDown(self):
        shutil.rmtree("temp")

    def test_gcc(self):
        oldPath = os.getcwd()
        os.chdir("temp")
        cc.gcc("hello.c")
        self.assertTrue(os.path.isfile("a.out"))
        os.chdir(oldPath)

    def test_gcc_o(self):
        cc.gcc_o("temp/hello.c", "temp/hello")
        self.assertTrue(os.path.isfile("temp/hello"))

@unittest.skipUnless(which("g++"), "g++ is not in your path")
class gppTests(unittest.TestCase):
    def setUp(self):
        os.mkdir("temp")
        with open("temp/hello.cpp", "w") as f:
            f.write("""
            #include <iostream>
            int main() {
                std::cout << "Hello, World!" << std::endl;
                return 0;
            }
            """)

    def tearDown(self):
        shutil.rmtree("temp")

    def test_gpp(self):
        oldPath = os.getcwd()
        os.chdir("temp")
        cc.gpp("hello.cpp")
        self.assertTrue("a.out")
        os.chdir(oldPath)

    def test_gpp_o(self):
        cc.gpp_o("temp/hello.cpp", "temp/hello")
        self.assertTrue(os.path.isfile("temp/hello"))

@unittest.skipUnless(which("javac"), "javac is not in your path")
class javacTests(unittest.TestCase):
    def setUp(self):
        os.mkdir("temp")
        with open("temp/hello.java", "w") as f:
            f.write("""
            class hello {
                public static void main(String[] args) {
                    System.out.println("Hello, World!");
                }
            }
            """)

    def tearDown(self):
        shutil.rmtree("temp")

    def test_javac(self):
        oldPath = os.getcwd()
        os.chdir("temp")
        cc.javac("hello.java")
        self.assertTrue(os.path.isfile("hello.class"))
        os.chdir(oldPath)

if __name__ == "__main__":
    unittest.main()
