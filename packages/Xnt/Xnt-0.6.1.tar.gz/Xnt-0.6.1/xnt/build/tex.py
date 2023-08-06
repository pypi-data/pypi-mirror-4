#!/usr/bin/env python
"""LaTeX Build Module"""

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
import logging
import xnt.tasks
from xnt import VERBOSE

LOGGER = logging.getLogger(__name__)

def pdflatex(document,
             path="./",
             bibtex=False,
             makeglossary=False):
    """Generate PDF LaTeX Document"""
    devnull = None if VERBOSE else open(os.devnull, 'w')
    documentbase = os.path.splitext(document)[0]
    cwd = os.getcwd()
    os.chdir(path)
    def pdf(draftmode=False):
        """Generate PDF"""
        cmd = ["pdflatex", document, "-halt-on-error",]
        if draftmode:
            cmd.append('-draftmode')
        return xnt.tasks.call(cmd, stdout=devnull)

    def run_bibtex():
        """Generate BibTex References"""
        return xnt.tasks.call(["bibtex", documentbase + ".aux"],
                              stdout=devnull)

    def makeglossaries():
        """Generate Glossary"""
        return xnt.tasks.call(["makeglossaries", documentbase], stdout=devnull)

    error_codes = []
    error_codes.append(pdf(draftmode=True))
    if makeglossary:
        error_codes.append(makeglossaries())
    if bibtex:
        error_codes.append(run_bibtex())
        error_codes.append(pdf(draftmode=True))
    error_codes.append(pdf(draftmode=False))
    os.chdir(cwd)
    if devnull:
        devnull.close()
    return sum(error_codes)

def clean(path="./", remove_pdf=False):
    """Clean up generated files of PDF compiliation"""
    cwd = os.getcwd()
    os.chdir(path)
    xnt.tasks.rm("*.out",
                 "*.log",
                 "*.aux",
                 "*.toc",
                 "*.tol",
                 "*.tof",
                 "*.tot",
                 "*.bbl",
                 "*.blg",
                 "*.nav",
                 "*.snm",
                 "*.mtc",
                 "*.mtc0",
                 "*.glo",
                 "*.ist",
                 "*.glg",
                 "*.gls")
    if remove_pdf:
        xnt.tasks.rm("*.pdf")
    os.chdir(cwd)
