#!/usr/bin/env python

import os
import sys
from mercurial import hg
from mercurial import ui
from mercurial import commands

def hgclone(url, dest=None,rev=None,branch=None):
    commands.clone(
        ui=ui.ui(),
        source=url,
        dest=dest,
        opts={"-r":rev,
              "-b":branch})

def hgfetch(path, source='default'):
    repo = hg.repository(ui.ui(), path)
    commands.pull(repo.ui, repo, source)
    commands.update(repo.ui, repo)
