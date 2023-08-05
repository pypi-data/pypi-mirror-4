# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py
#
# unified interface to FSEvents and inotify

import sys

from os.path import getmtime

try:
    import fsevents
except ImportError:
    fsevents = None

try:
    import pyinotify
except ImportError:
    pyinotify = None




def shedule(directories, callback):

    if not (fsevents or pyinotify):
        pass
