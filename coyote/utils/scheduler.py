from datetime import timedelta
from random import random, randrange

from celery.beat import PersistentScheduler
from celery.schedules import schedule as celeryschedule

class Scheduler(PersistentScheduler):
    def sync(self, *args, **kwargs):
        # horrible hack so shelve.sync() won't nuke schedule.odds
        return

class schedule(celeryschedule):
    def __init__(self, run_every, *args, **kwargs):
        self.odds = kwargs.pop('odds')
        self.max_run_every = kwargs.pop('max_run_every', None)
        super(schedule, self).__init__(run_every, *args, **kwargs)


    def __repr__(self):
        superrepr = super(Scheduler, self).__repr__()[:-1]
        return "{sr}, odds: {o}, max_run_every: {mre}>".format(
            sr=superrepr, o=self.odds, mre=self.max_run_every)


    def is_due(self, last_run_at):
        due, next_time_to_check = super(schedule, self).is_due(last_run_at)
        if due:
            if self.max_run_every is not None:
                next_time_to_check = timedelta(
                    # TODO this will be broken until run_every.get_seconds() or
                    # w/e
                    seconds=randrange(run_every, self.max_run_every + 1))
            if random() <= self.odds:
                return (True, next_time_to_check)
        return (False, next_time_to_check)
