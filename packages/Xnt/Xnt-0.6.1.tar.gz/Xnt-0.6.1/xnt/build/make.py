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

def ant(path="", target="", flags=None, pkeys=None, pvalues=None):
    """Wrapper around Apache Ant"""
    cmd = __add_params(["ant"],
                       __build_param_list(pkeys, pvalues),
                       lambda x: "-D%s" % x)
    cmd = __add_flags(cmd, flags)
    cmd.append(target)
    return __run_in(path, lambda: subprocess.call(cmd))

def make(path="", target="", flags=None, pkeys=None, pvalues=None):
    """Wrapper around GNU Make"""
    cmd = __add_params(["make"], __build_param_list(pkeys, pvalues))
    cmd = __add_flags(cmd, flags)
    cmd.append(target)
    return __run_in(path, lambda: subprocess.call(cmd))

def nant(path="", target="", flags=None, pkeys=None, pvalues=None):
    """Wrapper around .NET Ant"""
    cmd = __add_params(["nant"],
                        __build_param_list(pkeys, pvalues),
                        lambda x: "-D:%s" % x)
    cmd = __add_flags(cmd, flags)
    cmd.append(target)
    return __run_in(path, lambda: subprocess.call(cmd))

def __add_flags(cmd, flags):
    """Add flags to command and return new list"""
    command = list(cmd)
    for flag in flags:
        command.append(flag)
    return command

def __build_param_list(keys, values):
    """Build a list of key-value for appending to the command list"""
    parameters = []
    if not keys or not values:
        return parameters
    params = zip(keys, values)
    for param in params:
        parameters.append("%s=%s" % param)
    return parameters

def __add_params(cmd, params, param_map=lambda x: x):
    """Append parameters to cmd list using fn"""
    if not params:
        return cmd
    command = list(cmd)
    for param in params:
        command.append(param_map(param))
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
