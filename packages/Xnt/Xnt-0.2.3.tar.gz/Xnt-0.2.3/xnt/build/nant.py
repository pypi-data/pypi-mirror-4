#!/usr/bin/env python

import os
import subprocess

def nant(path="", target=""):
    cmd = ["nant", target]
    if path and os.path.exists(path):
        oldPath = os.path.abspath(os.getcwd())
        os.chdir(os.path.abspath(path))
    result = subprocess.call(cmd)
    if oldPath:
        os.chdir(oldPath)
    return result
