#!/usr/bin/env python

import os
import sys
import subprocess

def cvsco(module, rev="", dest=""):
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
    oldPath = os.path.abspath(os.getcwd())
    os.chdir(path)
    cmd = ["cvs", "update"]
    os.chdir(oldPath)
