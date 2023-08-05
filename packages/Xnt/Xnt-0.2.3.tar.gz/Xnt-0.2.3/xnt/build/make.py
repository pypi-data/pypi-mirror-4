#!/usr/bin/env python

import os
import subprocess

def make(path="", target=""):
    cmd = ["make", target]
    if path and os.path.exists(path):
        oldPath = os.path.abspath(os.getcwd())
        os.chdir(os.path.abspath(path))
    result = subprocess.call(cmd)
    if oldPath:
        os.chdir(oldPath)
    return result
