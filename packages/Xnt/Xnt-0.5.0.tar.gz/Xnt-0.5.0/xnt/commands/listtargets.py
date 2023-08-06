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
from xnt.status_codes import SUCCESS, ERROR
import logging

logger = logging.getLogger(__name__)

class ListTargetsCommand(Command):
    name = 'list-targets'
    usage = """"""
    summary = "Prints targets in build file"
    needs_build = True

    def __init__(self, build):
        self.build = build

    def run(self, arguments=[]):
        logger.debug("build is null? %s", self.build == None)
        try:
            for f in dir(self.build):
                logger.debug("Attribute %s:", f)
                try:
                    fa = getattr(self.build, f)
                    if fa.decorator == "target":
                        print(f + ":")
                        if fa.__doc__:
                            print(fa.__doc__)
                        print("\n")
                except AttributeError:
                    pass
        except Exception as ex:
            logger.error(ex)
            return ERROR
        return SUCCESS
