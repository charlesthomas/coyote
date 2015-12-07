from datetime import timedelta
from random import random, randrange

from celery.schedules import schedule

class Scheduler(schedule):
    def __init__(self, run_every, odds, max_run_every=None, *args):
        self.odds = odds
        self.max_run_every = max_run_every
        super(Scheduler, self).__init__(run_every, *args)


    def is_due(self, last_run_at):
        print self.odds
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
