#!/usr/bin/env python
"""CVS Version Control Wrapper"""

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

def cvsco(module, rev="", dest=""):
    """Run CVS Checkout"""
    cmd = ["cvs", "co", "-P"]
    if rev:
        cmd.append("-r")
        cmd.append(rev)
    if dest:
        cmd.append("-d")
        cmd.append(dest)
    cmd.append(module)
    subprocess.call(cmd)

def cvsupdate(path):
    """Run CVS Update"""
    cwd = os.path.abspath(os.getcwd())
    os.chdir(path)
    cmd = ["cvs", "update"]
    subprocess.call(cmd)
    os.chdir(cwd)
