#!/usr/bin/env python
from __future__ import absolute_import

import os
import sys
from datetime import timedelta

from celery import Celery
from celery.schedules import schedule


class OddsChecker(object):
    def __init__(self, odds):
        self.odds = odds


    def should_i_run(self):
        return True


class Scheduler(schedule):
    def __init__(self, run_every, odds, *args):
        self.odds = OddsChecker(odds)
        super(Scheduler, self).__init__(run_every, *args)


    def is_due(self, last_run_at):
        due, next_time_to_check = super(Scheduler, self).is_due(last_run_at)
        if due and self.odds.should_i_run():
            return (True, next_time_to_check)
        return (False, next_time_to_check)

# LIB_DIRS = ['./coyote', './lib', '/var/lib/coyote']
LIB_DIRS = ['./coyote', ]#'./lib', '/var/lib/coyote']


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

schedule = {
    'test': {
        'task':'tasks.cstring',
        'schedule': Scheduler(timedelta(seconds=1), odds='100%'),
        'args': ('this is a test',),
    },
}

app.conf.update(CELERYBEAT_SCHEDULE=schedule)

if __name__ == '__main__':
    app.start()
