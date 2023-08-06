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

from xnt.basecommand import Command
from xnt.status_codes import SUCCESS, ERROR, UNKNOWN_ERROR
import logging

logger = logging.getLogger("xnt")

class TargetCommand(Command):
    name = '<target>'
    usage = """"""
    summary = "Invokes target(s) in build.py"
    needs_build = True

    def __init__(self, build):
        self.build = build

    def run(self, targets=[], props=[]):
        if targets:
            for t in targets:
                ec = self.callTarget(t, props)
                if ec:
                    return ec
            return SUCCESS
        else:
            return self.callTarget("default", props)

    def callTarget(self, targetName, props):
        def processParams(params, buildProperties={}):
            properties = buildProperties if buildProperties is not None else {}
            for p in params:
                name, value = p[2:].split("=")
                properties[name] = value
            return properties
        def __getProperties():
            try:
                return getattr(self.build, "properties")
            except AttributeError:
                return None
        try:
            if len(props) > 0:
                setattr(self.build,
                        "properties",
                        processParams(props, __getProperties()))
            target = getattr(self.build, targetName)
            ec = target()
            return ec if ec else 0
        except AttributeError:
            logger.warning("There was no target: %s", targetName)
            return ERROR
        except Exception as ex:
            logger.error(ex)
            return UNKNOWN_ERROR

