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

import os
import subprocess
import logging


def ant(path="", target=""):
    cmd = ["ant", target]
    return __run_in(path, lambda: subprocess.call(cmd))

def make(path="", target=""):
    cmd = ["make", target]
    return __run_in(path, lambda: subprocess.call(cmd))

def nant(path="", target=""):
    cmd = ["nant", target]
    return __run_in(path, lambda: subprocess.call(cmd))

def __run_in(path, f):
    oldPath = os.path.abspath(os.getcwd())
    if path and os.path.exists(path):
        os.chdir(os.path.abspath(path))
    result = f()
    if oldPath:
        os.chdir(oldPath)
    return result
