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
import time
import logging

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s")
logger = logging.Logger(name=__name__)
logger.addHandler(logging.StreamHandler())

def usageAction():
    print(usage());
    sys.exit(0)

def versionAction():
    print(version())
    sys.exit(0)

def verboseAction():
    logging.getLogger("xnt").setLevel(logging.INFO)

actions = {
    "--usage": usageAction,
    "--version": versionAction,
    "-v"     : verboseAction,
}

def main():
    start_time = time.time()
    params = list(p for p in sys.argv[1:] if p.startswith('-D'))
    opts = list(o for o in sys.argv[1:]
        if o.startswith('-') and o not in params)
    arg = list(a for a in sys.argv[1:] if a not in opts and a not in params)
    for opt in opts:
        if opt in actions:
            actions[opt]()
        else:
            logger.debug("%s is not a valid option", opt)
    ec = invokeBuild(
        __loadBuild(),
        arg[0] if len(arg) == 1 else "default",
        params)
    from xnt.tasks import rm
    rm("build.pyc",
       "__pycache__")
    elapsed_time = time.time() - start_time
    logger.info("Execution time: %.3f", elapsed_time)
    print("Success" if ec == 0 else "Failure")

def invokeBuild(build, targetName, props=[]):
    def __getProperties():
        try:
            return getattr(build, "properties")
        except AttributeError:
            return None

    if targetName == "list-targets":
        return printTargets(build)
    try:
        if len(props) > 0:
            setattr(build, "properties", __processParams(props,
                                                         __getProperties()))
        target = getattr(build, targetName)
        ec = target()
        return ec if ec else 0
    except AttributeError:
        logger.warning("There was no target: %s", targetName)
        return -2
    except Exception as e:
        logger.error(e)
        return -3

def usage():
    import xnt
    endl = os.linesep
    usageText = \
        xnt.__version__ + endl + \
        xnt.__license__ + endl + \
        "Usage:\txnt [options] [target]" + endl + \
        "Where [target] is a target in your ``build.py`` file" + endl + \
        "  And [options] is one of the falling:" + endl + \
        "\t-v: print verbose information about Xnt's running" + endl + \
        "\t--usage: Print this message" + endl + \
        "In addition to targets defined by your ``build.py`` file" + endl + \
        "\t``list-targets`` can be used in place of [targets] to" + endl + \
        "\t\tlist targets and docstrings defined in your ``build.py`` file" + \
        endl + \
        "\tIf no [target] is provided, Xnt will try the target: ``default``" \
        + endl
    return usageText

def version():
    import xnt
    return xnt.__version__

def printTargets(build):
    print(version())
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
    except Exception as e:
        logger.error(e)

def __loadBuild(path=""):
    if not path:
        path = os.getcwd()
    else:
        path = os.path.abspath(path)
    sys.path.append(path)
    cwd = os.getcwd()
    os.chdir(path)
    if not os.path.exists("build.py"):
        logger.error("There was no build file")
        sys.exit(1)
    try:
        return __import__("build", fromlist=[])
    except ImportError:
        logger.error("HOW?!")
        return None
    finally:
        sys.path.remove(path)
        del sys.modules["build"]
        os.chdir(cwd)

def __processParams(params, buildProperties={}):
    properties = buildProperties if buildProperties is not None else {}
    for p in params:
        name, value = p[2:].split("=")
        properties[name] = value
    return properties

if __name__ == "__main__":
    main()
