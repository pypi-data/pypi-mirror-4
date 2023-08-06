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
import subprocess
import time
import shutil
import zipfile
import contextlib
import glob
import logging

logger = logging.getLogger(__name__)

#File associated tasks
def expandpath(path):
    """
    Expand path using globs to a possibly empty list of directories
    """
    return glob.iglob(path)

def cp(src="",dst="",files=[]):
    assert dst and src or len(files) > 0
    logger.info("Copying %s to %s", src, dst)
    def copy(s,d):
        if os.path.isdir(s):
            shutil.copytree(s,d)
        else:
            shutil.copy2(s,d)
    if src:
        copy(src, dst)
    else:
        for f in files:
            copy(f, dst)

def mv(src,dst):
    logger.info("Moving %s to %s", src, dst)
    shutil.move(src,dst)

def mkdir(dir,mode=0o777):
    if os.path.exists(dir):
        return
    logger.info("Making directory %s with mode %o", dir, mode)
    try:
        os.mkdir(dir,mode)
    except IOError as e:
        log(e, logging.WARNING)
    except:
        raise

def rm(*fileset):
    try:
        for g in fileset:
            for f in expandpath(g):
                if not os.path.exists(f):
                    continue
                logger.info("Removing %s", f)
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.remove(f)
    except OSError as e:
        log(e, logging.WARNING)
    except:
        raise

def zip(dir,zipfilename):
    logger.info("Zipping %s as %s", dir, zipfilename)
    assert os.path.isdir(dir) and zipfilename
    with contextlib.closing(zipfile.ZipFile(
        zipfilename,
        "w",
        zipfile.ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(dir):
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(dir)+len(os.sep):]
                z.write(absfn, zfn)

#Misc Tasks
def echo(msg, tofile):
    with open(tofile, "w") as f:
        f.write(msg)

def log(msg="",lvl=logging.INFO):
    logger.log(lvl, msg)

def xnt(target, path):
    """
    Invoke xnt on another build file in a different directory
    """
    import xnt.xenant
    xnt.xenant.invokeBuild(
        xnt.xenant.__loadBuild(path),
        target)

def call(command, stdout=None, stderr=None):
    """
    Execute the given command, redirecting stdout and stderr
    to optionally given files
    param: command - list of command and arguments
    param: stdout - file to redirect standard output to, if given
    param: stderr - file to redirect standard error to, if given
    """
    return subprocess.call(args=command, stdout=stdout, stderr=stderr)

def setup(commands, dir=""):
    """
    Invoke the ``setup.py`` file in the current or specified directory
    param: commands - list of commands and options to run/ append
    param: dir - (optional) directory to run from
    """
    cmd = [sys.executable, "setup.py",]
    for c in commands:
        cmd.append(c)
    cwd = os.getcwd()
    if dir:
        os.chdir(dir)
    ec = call(cmd)
    os.chdir(cwd)
    return ec
