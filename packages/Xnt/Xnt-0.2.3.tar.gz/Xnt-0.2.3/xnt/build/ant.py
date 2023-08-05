#!/usr/bin/env python

import os
import subprocess

def ant(path="", target=""):
    cmd = ["ant", target]
    if path and os.path.exists(path):
        oldPath = os.path.abspath(os.getcwd())
        os.chdir(os.path.abspath(path))
    result = subprocess.call(cmd)
    if oldPath:
        os.chdir(oldPath)
    return result
