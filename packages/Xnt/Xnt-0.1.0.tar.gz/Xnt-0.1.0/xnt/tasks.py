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
    logger.info("Making directory %s with mode %o", dir, mode)
    try:
        os.mkdir(dir,mode)
    except IOError:
        pass
    except:
        raise

def rm(path):
    logger.info("Removing %s", path)
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
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
def echo(message="",tofile=""):
    if tofile:
        with open(tofile, "w") as f:
            subprocess.call(["echo", message], stdout=f)
    else:
        print(message)
