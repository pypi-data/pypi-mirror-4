#!/usr/bin/env python
"""Wrapping methods around build tools"""

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
import subprocess

def ant(path="", target="", flags=None):
    """Wrapper around Apache Ant"""
    cmd = __add_flags(["ant", target], flags)
    return __run_in(path, lambda: subprocess.call(cmd))

def make(path="", target="", flags=None):
    """Wrapper around GNU Make"""
    cmd = __add_flags(["make", target], flags)
    return __run_in(path, lambda: subprocess.call(cmd))

def nant(path="", target="", flags=None):
    """Wrapper around .NET Ant"""
    cmd = __add_flags(["nant", target], flags)
    return __run_in(path, lambda: subprocess.call(cmd))

def __add_flags(cmd, flags):
    """Add flags to command and return new list"""
    command = list(cmd)
    for flag in flags:
        command.append(flag)
    return command

def __run_in(path, function):
    """Execute function while in a different running directory"""
    cwd = os.path.abspath(os.getcwd())
    if path and os.path.exists(path):
        os.chdir(os.path.abspath(path))
    result = function()
    if cwd:
        os.chdir(cwd)
    return result
