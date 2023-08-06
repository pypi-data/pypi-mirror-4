#!/usr/bin/env python
"""Git Version Control Module"""

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
import xnt.tasks
import xnt.vcs

def gitclone(url, dest=None, branch=None):
    """Clone a repository"""
    command = ["git", "clone"]
    command = xnt.vcs.clone_options(command, url, branch, dest)
    xnt.tasks.call(command)

def gitpull(path, source="origin", branch="master"):
    """Pull/Update a cloned repository"""
    cwd = os.getcwd()
    os.chdir(path)
    command = ["git", "pull", source, branch]
    xnt.tasks.call(command)
    os.chdir(cwd)
