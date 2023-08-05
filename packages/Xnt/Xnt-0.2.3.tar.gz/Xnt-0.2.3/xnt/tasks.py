#!/usr/bin/env python

import os
import sys
import subprocess
import time
import shutil
import zipfile
import contextlib
import logging

logger = logging.getLogger(__name__)

#File associated tasks
def cp(src,dst):
    logger.info("Copying %s to %s", src, dst)
    if os.path.isdir(src):
        shutil.copytree(src,dst)
    else:
        shutil.copy2(src,dst)

def mv(src,dst):
    logger.info("Moving %s to %s", src, dst)
    shutil.move(src,dst)

def mkdir(dir,mode=0o777):
    if os.path.exists(dir):
        return
    logger.info("Making directory %s with mode %o", dir, mode)
    try:
        os.mkdir(dir,mode)
    except IOError:
        pass
    except:
        raise

def rm(*fileset):
    try:
        for f in fileset:
            if not os.path.exists(f):
                continue
            logger.info("Removing %s", f)
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
    except OSError:
        pass
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

def call(command, stdout=None, stderr=None):
    """
    Execute the given command, redirecting stdout and stderr
    to optionally given files
    param: command - list of command and arguments
    param: stdout - file to redirect standard output to, if given
    param: stderr - file to redirect standard error to, if given
    """
    subprocess.call(args=command, stdout=stdout, stderr=stderr)
