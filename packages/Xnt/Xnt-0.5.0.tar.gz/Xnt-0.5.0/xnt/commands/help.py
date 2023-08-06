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
from xnt.status_codes import SUCCESS

class HelpCommand(Command):
    name = 'help'
    usage = """"""
    summary = 'Print Usage Summary'
    needs_build = False

    def run(self, arguments=[]):
        from xnt.commands import get_summaries
        from xnt import __version__, __license__
        commands = get_summaries()
        print(__version__)
        print(__license__)
        print("Available Commands:")
        for name, summary in commands:
            print(name)
            print("\t" + summary)

        return SUCCESS
