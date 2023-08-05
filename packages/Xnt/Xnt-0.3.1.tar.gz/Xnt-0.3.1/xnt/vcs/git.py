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
import sys
import xnt.tasks

def gitclone(url, dest=None, branch=None):
    command = ["git", "clone"]
    if branch:
        command.append("--branch")
        command.append(branch)
    command.append(url)
    if dest:
        command.append(dest)
    xnt.tasks.call(command)

def gitpull(path, source="origin", branch="master"):
    cwd = os.getcwd()
    os.chdir(path)
    command = ["git", "pull", source, branch]
    xnt.tasks.call(command)
    os.chdir(cwd)
