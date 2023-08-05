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
import logging

sys.path.append(os.getcwd())
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s")
logger = logging.Logger(name=__name__)
logger.addHandler(logging.StreamHandler())

def versionAction():
    printVersion()
    sys.exit(0)

def verboseAction():
    logging.getLogger("xnt.tasks").setLevel(logging.INFO)

actions = {
    "--version": versionAction,
    "-v"     : verboseAction,
}

def main():
    opts = list(o for o in sys.argv[1:] if o.startswith('-'))
    arg = list(a for a in sys.argv[1:] if a not in opts)
    for opt in opts:
        if opt in actions:
            actions[opt]()
        else:
            logger.debug("%s is not a valid option", opt)
    invokeBuild(__loadBuild(), arg[0] if len(arg) == 1 else "default")
    from xnt.tasks import rm
    rm("build.pyc")

def invokeBuild(build, targetName):
    if targetName == "help":
        return printTargets(build)
    try:
        target = getattr(build, targetName)
        target()
    except AttributeError:
        logger.warning("There was no target: %s", targetName)
    except:
        logger.error(sys.exc_info()[1].message)

def printVersion():
    import xnt
    print(xnt.__version__)

def printTargets(build):
    printVersion()
    print("\n")
    try:
        for f in dir(build):
            try:
                fa = getattr(build, f)
                if fa.decorator == "target":
                    print(f + ":")
                    if fa.__doc__:
                        print(fa.__doc__)
                    print("\n")
            except AttributeError:
                pass
    except:
        logger.error(sys.exc_info()[1].message)

def __loadBuild():
    if not os.path.exists("build.py"):
        logger.error("There was no build file")
        sys.exit(1)
    try:
        return __import__("build", fromlist=[])
    except ImportError:
        logger.error("HOW?!")
        return None

if __name__ == "__main__":
    main()
