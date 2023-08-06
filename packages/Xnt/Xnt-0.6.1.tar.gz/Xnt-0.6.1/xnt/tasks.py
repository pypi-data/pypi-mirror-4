#!/usr/bin/env python
"""Common Tasks Module

Defines a set of operations that are common enough but also are tedious to
define
"""

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
import sys
import subprocess
import shutil
import zipfile
import contextlib
import glob
import logging

LOGGER = logging.getLogger(__name__)

#File associated tasks
def expandpath(path):
    """
    Expand path using globs to a possibly empty list of directories
    """
    return glob.iglob(path)

def cp(src="", dst="", files=None):
    """Copy `src` to `dst` or copy `files` to `dst`

    Copy a file or folder to a different file/folder
    If no `src` file is specified, will attempt to copy `files` to `dst`
    """
    assert dst and src or len(files) > 0
    LOGGER.info("Copying %s to %s", src, dst)
    def copy(source, destination):
        """Copy file or folder to destination.

        Depending on the type of source, call the appropriate method
        """
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
    if src:
        copy(src, dst)
    else:
        for file_to_copy in files:
            copy(file_to_copy, dst)

def mv(src, dst):
    """Move file or folder to destination"""
    LOGGER.info("Moving %s to %s", src, dst)
    shutil.move(src, dst)

def mkdir(directory, mode=0o777):
    """Make a directory with mode"""
    if os.path.exists(directory):
        LOGGER.warning("Given directory (%s) already exists" % directory)
        return
    LOGGER.info("Making directory %s with mode %o", directory, mode)
    try:
        os.mkdir(directory, mode)
    except IOError as io_error:
        log(io_error, logging.ERROR)
    except:
        raise

def rm(*fileset):
    """Remove a set of files"""
    try:
        for glob_set in fileset:
            for file_to_delete in expandpath(glob_set):
                if not os.path.exists(file_to_delete):
                    continue
                LOGGER.info("Removing %s", file_to_delete)
                if os.path.isdir(file_to_delete):
                    shutil.rmtree(file_to_delete)
                else:
                    os.remove(file_to_delete)
    except OSError as os_error:
        log(os_error, logging.ERROR)
    except:
        raise

def create_zip(directory, zipfilename):
    """Compress (Zip) folder"""
    LOGGER.info("Zipping %s as %s", directory, zipfilename)
    assert os.path.isdir(directory) and zipfilename
    with contextlib.closing(zipfile.ZipFile(
        zipfilename,
        "w",
        zipfile.ZIP_DEFLATED)) as zip_file:
        for paths in os.walk(directory):
            for file_name in paths[2]:
                absfn = os.path.join(paths[0], file_name)
                zip_file_name = absfn[len(directory) + len(os.sep):]
                zip_file.write(absfn, zip_file_name)

#Misc Tasks
def echo(msg, tofile):
    """Write a string to file"""
    with open(tofile, "w") as file_to_write:
        file_to_write.write(msg)

def log(msg="", lvl=logging.INFO):
    """Log message using tasks global logger"""
    LOGGER.log(lvl, msg)

def xntcall(buildfile, targets=None, props=None):
    """Invoke xnt on another build file in a different directory

    param: path - to the build file (including build file)
    param: targets - list of targets to execute
    param: props - dictionary of properties to pass to the build module
    """
    from xnt.xenant import invoke_build, load_build
    build = load_build(buildfile)
    path = os.path.dirname(buildfile)
    cwd = os.getcwd()
    os.chdir(path)
    error_code = invoke_build(build, targets=targets, props=props)
    os.chdir(cwd)
    return error_code

def call(command, stdout=None, stderr=None):
    """ Execute the given command, redirecting stdout and stderr
    to optionally given files

    param: command - list of command and arguments
    param: stdout - file to redirect standard output to, if given
    param: stderr - file to redirect standard error to, if given
    """
    return subprocess.call(args=command, stdout=stdout, stderr=stderr)

def setup(commands, directory=""):
    """Invoke the ``setup.py`` file in the current or specified directory

    param: commands - list of commands and options to run/ append
    param: dir - (optional) directory to run from
    """
    cmd = [sys.executable, "setup.py",]
    for command in commands:
        cmd.append(command)
    cwd = os.getcwd()
    if directory:
        os.chdir(directory)
    error_code = call(cmd)
    os.chdir(cwd)
    return error_code
