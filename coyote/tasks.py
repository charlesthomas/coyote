#!/usr/bin/env python
from __future__ import absolute_import

from bcrypt import hashpw
from celery import Celery

app = Celery('tasks')

key = '''
THIS IS MY TERRIBLE BUT SUPER SECRET KEY FOR BCRYPT
'''

@app.task
def read_cmd(cmd, timestamp, sig):
    if not _validate_sig(cmd, timestamp, sig):
        print "uh oh"
        return
    print "{timestamp}: {cmd}".format(timestamp=timestamp, cmd=cmd)


def _validate_sig(cmd, timestamp, sig):
    return sig == hashpw(cmd + timestamp + key, sig)
