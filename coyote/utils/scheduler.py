from datetime import timedelta
from random import random, randrange

from celery.schedules import schedule

class Scheduler(schedule):
    def __init__(self, run_every, *args, **kwargs):
        super(Scheduler, self).__init__(run_every, *args, **kwargs)
        self.odds = kwargs.get('odds', 1)
        self.max_run_every = kwargs.get('max_run_every', None)


    def __repr__(self):
        superrepr = super(Scheduler, self).__repr__()[:-1]
        return "{sr}, odds: {o}, max_run_every: {mre}>".format(
            sr=superrepr, o=self.odds, mre=self.max_run_every)


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
