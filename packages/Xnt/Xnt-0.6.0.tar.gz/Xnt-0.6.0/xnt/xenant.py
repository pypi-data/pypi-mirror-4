#!/usr/bin/env python
"""Xnt Runner Script"""

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
import time
import logging
import argparse
from xnt import __version__
from xnt.status_codes import SUCCESS, ERROR, UNKNOWN_ERROR

logging.basicConfig(format="%(message)s")
LOGGER = logging.Logger(name=__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.WARNING)

def main():
    """Xnt Entry Point"""
    start_time = time.time()
    args = parse_args(sys.argv[1:])
    build_file = "./build.py"
    if args["verbose"]:
        LOGGER.setLevel(logging.INFO)
        logging.getLogger("xnt.tasks").setLevel(logging.INFO)
    if args["build-file"]:
        build_file = args["build-file"]
    if args["list-targets"]:
        error_code = list_targets(load_build(build_file))
    else:
        error_code = invoke_build(load_build(build_file),
                                  args["targets"],
                                  args["properties"])
    elapsed_time = time.time() - start_time
    print("Execution time: %.3f" % elapsed_time)
    if error_code != 0:
        LOGGER.error("Failure")
    from xnt.tasks import rm
    rm("build.pyc",
       "__pycache__",
       build_file + "c",
       os.path.join(os.path.dirname(build_file), "__pycache__"))
    if error_code != 0:
        sys.exit(error_code)

def load_build(buildfile="./build.py"):
    """Load build file

    Load the build.py and return the resulting import
    """
    path = os.path.dirname(buildfile)
    build = os.path.basename(buildfile)
    buildmodule = os.path.splitext(build)[0]
    if not path:
        path = os.getcwd()
    else:
        path = os.path.abspath(path)
    sys.path.append(path)
    cwd = os.getcwd()
    os.chdir(path)
    if not os.path.exists(build):
        LOGGER.error("There was no build file")
        sys.exit(1)
    try:
        return __import__(buildmodule, fromlist=[])
    except ImportError:
        LOGGER.error("HOW?!")
        return None
    finally:
        sys.path.remove(path)
        del sys.modules[buildmodule]
        os.chdir(cwd)

def invoke_build(build, targets=None, props=None):
    """Invoke Build with `targets` passing `props`"""
    def call_target(target_name, props):
        """Call target on build module"""
        def process_params(params, existing_props=None):
            """Parse and separate properties and append to build module"""
            properties = existing_props if existing_props is not None else {}
            for param in params:
                name, value = param.split("=")
                properties[name] = value
            return properties
        def __get_properties():
            """Return the properties dictionary of the build module"""
            try:
                return getattr(build, "PROPERTIES")
            except AttributeError:
                LOGGER.warning("Build file specifies no properties")
                return None
        try:
            if props and len(props) > 0:
                setattr(build,
                        "PROPERTIES",
                        process_params(props, __get_properties()))
            target = getattr(build, target_name)
            error_code = target()
            return error_code if error_code else 0
        except AttributeError:
            LOGGER.error("There was no target: %s", target_name)
            return ERROR
        except Exception as ex:
            LOGGER.critical(ex)
            return UNKNOWN_ERROR
    if targets and len(targets) > 0:
        for target in targets:
            error_code = call_target(target, props)
            if error_code:
                return error_code
        return SUCCESS
    else:
        return call_target("default", props)

def list_targets(build):
    """List targets (and doctstrings) of the provided build module"""
    try:
        for attr in dir(build):
            try:
                func = getattr(build, attr)
                if func.decorator == "target":
                    print(attr + ":")
                    if func.__doc__:
                        print(func.__doc__)
                    print("")
            except AttributeError:
                pass
    except AttributeError as ex:
        LOGGER.error(ex)
        return ERROR
    return SUCCESS

def parse_args(args_in):
    """Parse and group arguments"""
    parser = argparse.ArgumentParser(prog="Xnt")
    parser.add_argument("-v", "--verbose",
                        help="be verbose",
                        action="store_true",
                        dest="verbose")
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="print the version information and quit")
    parser.add_argument(
        "-b", "--build-file",
        dest="build-file",
        help="use the given buildfile")
    parser.add_argument("-l", "--list-targets",
                        action="store_true",
                        dest="list-targets",
                        help="print build targets")
    # Properties Group
    params_group = parser.add_argument_group("Properties")
    params_group.add_argument(
        "-D", dest="properties", action="append",
        help="use value for gvien property")
    target_group = parser.add_argument_group("Targets")

    # Targets Group
    target_group.add_argument("targets", nargs=argparse.REMAINDER,
                              help="name(s) of targets to invoke")
    return vars(parser.parse_args(args_in))

if __name__ == "__main__":
    main()
