#!/usr/bin/env python
from __future__ import absolute_import

from random import choice
from sys import argv

from coyote.celery import build_includes

CELERY_TASK_STR = "<class 'celery.local.PromiseProxy'>"

catalog = dict()

for inc in build_includes():
    functions = list()
    mod = __import__(inc)
    for name in dir(mod.tasks):
        f = getattr(mod.tasks, name, None)
        if hasattr(f, 'delay') and str(type(f)) == CELERY_TASK_STR:
            functions.append((name, f))
    catalog[inc] = functions

# cause mayhem reimburse expenses
src = choice(catalog.keys())
fun = choice(catalog[src])
print "cause mayhem reimburse expenses..."
print "running {module}.{function}...".format(module=src, function=fun[0])
fun[1].delay()
