#!/usr/bin/env python
from __future__ import absolute_import

import os
import sys

from celery import Celery

LIB_DIRS = ['./coyote', './lib', '/var/lib/coyote']

def build_includes():
    includes = list()
    syspaths = list()
    for lib in LIB_DIRS:
        if not os.path.exists(lib):
            continue
        for root, dirs, files in os.walk(os.path.abspath(lib)):
            if 'tasks.py' in files:
                syspaths.append(os.path.dirname(root))
                includes.append('{d}.tasks'.format(d=os.path.basename(root)))

    for syspath in set(syspaths): # unique list
        sys.path.append(syspath)

    return includes

app = Celery('tasks', include=build_includes())

if __name__ == '__main__':
    app.start()
