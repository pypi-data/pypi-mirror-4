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

from xnt.commands.help import HelpCommand
from xnt.commands.listtargets import ListTargetsCommand
from xnt.commands.version import VersionCommand
from xnt.commands.target import TargetCommand

commands = {
    HelpCommand.name: HelpCommand,
    ListTargetsCommand.name: ListTargetsCommand,
    VersionCommand.name: VersionCommand,
    TargetCommand.name: TargetCommand,
}

def get_summaries(ignore_hidden=True):
    items = []

    for name, command_class in commands.items():
        if ignore_hidden and command_class.hidden:
            continue
        items.append((name, command_class.summary))

    return sorted(items)
