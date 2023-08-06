#!/usr/bin/env python
"""Main xnt module

Contains definition for version (referenced from version module), license,
target decorator, and imports task methods from tasks module
"""

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

import xnt.version
__version__ = "Xnt " + xnt.version.__version__
__license__ = """
   Xnt -- A Wrapper Build Tool
   Copyright (C) 2012  Kenny Ballou

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from xnt.tasks import cp, mv, mkdir, rm, create_zip, log, xntcall, call, setup

def target(target_fn):
    """Decorator function for marking a method in
       build file as a "target" method, or a method meant
       to be invoked from Xnt
    """
    def wrap():
        """Inner wrapper function for decorator"""
        print(target_fn.__name__ + ":")
        return target_fn()
    wrap.decorator = "target"
    wrap.__doc__ = target_fn.__doc__
    return wrap
