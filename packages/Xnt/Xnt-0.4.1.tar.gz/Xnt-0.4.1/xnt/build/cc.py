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

"""
Common Compilers
"""

import os
import logging
import sys
from xnt.tasks import call

logger = logging.getLogger(__name__)

def gcc(src, flags=[]):
    """gcc compiler, non-named output file"""
    return _gcc(src, flags)

def gpp(src, flags=[]):
    """g++ compiler, non-named output file"""
    return _gcc(src, flags, "g++")

def gcc_o(src, o, flags=[]):
    """gcc compiler, with output file"""
    return _gcc_o(src, o, flags)

def gpp_o(src, o, flags=[]):
    """g++ compiler, with output file"""
    return _gcc_o(src, o, flags, "g++")

def javac(src, flags=[]):
    """Javac: compile Java programs"""
    logger.info("Compiling %s", src)
    cmd = __generateCommand(src, flags, "javac")
    return __compile(cmd)

def _gcc(src, flags=[], compiler="gcc"):
    logger.info("Compiling %s", src)
    return __compile(__generateCommand(src, flags, compiler))

def _gcc_o(src, o, flags=[], compiler="gcc"):
    logger.info("Compiling %s to %s", src, o)
    cmd = __generateCommand(src, flags, compiler)
    cmd.append("-o")
    cmd.append(o)
    return __compile(cmd)

def __generateCommand(src, flags=[], compiler="gcc"):
    cmd = [compiler, src]
    for f in flags:
        cmd.append(f)
    return cmd

def __compile(cmd):
    return call(cmd)

def __is_newer(a, b):
    return os.path.getmtime(a) > os.path.getmtime(b)
