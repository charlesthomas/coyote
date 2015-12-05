#!/usr/bin/env python
from __future__ import absolute_import

import os
import sys
from datetime import timedelta
from random import randrange

from celery import Celery
from celery.schedules import schedule

from .utils.conf_builder import AppConfig


class Scheduler(schedule):
    def __init__(self, run_every, odds, max_run_every=None, *args):
        self.odds = odds
        self.max_run_every = max_run_every
        super(Scheduler, self).__init__(run_every, *args)


    def is_due(self, last_run_at):
        due, next_time_to_check = super(Scheduler, self).is_due(last_run_at)
        if due:
            if self.max_run_every is not None:
                next_time_to_check = timedelta(
                    # TODO this will be broken until run_every.get_seconds() or
                    # w/e
                    seconds=randrange(run_every, self.max_run_every + 1))
            if random() <= self.odds:
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
        'task':'echoprinthello',
        'schedule': Scheduler(timedelta(seconds=1), odds='100%'),
        'args': ('this is a test',),
    },
}

config = AppConfig('./coyote_config.yaml')
import ipdb;ipdb.set_trace()

app.conf.update(CELERYBEAT_SCHEDULE=schedule)

if __name__ == '__main__':
    app.start()
