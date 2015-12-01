#!/usr/bin/env python
from __future__ import absolute_import

from subprocess import Popen
from time import sleep

from coyote.celery import app

@app.task
def cprint(string):
    print string

@app.task
def down_iface(iface, timeout=10):
    Popen(['sudo', 'ifdown', iface])
    sleep(timeout)
    Popen(['sudo', 'ifup', iface])
