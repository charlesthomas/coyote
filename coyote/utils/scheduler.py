from datetime import timedelta
from random import random, randrange

from celery.schedules import schedule as celeryschedule

class schedule(celeryschedule):
    def __init__(self, odds, run_every, max_run_every=None,
                 relative=False, nowfun=None, app=None):
        self.odds = odds
        self.max_run_every = max_run_every
        super(schedule, self).__init__(run_every, relative, nowfun, app)


    def __repr__(self):
        return "schedule(odds={o}, run_every={re}, max_run_every={mre})".format(
            o=self.odds, re=self.run_every, mre=self.max_run_every)


    def __reduce__(self):
        return self.__class__, (self.odds, self.run_every, self.max_run_every,
                                self.relative, self.nowfun)


    def is_due(self, last_run_at):
        print "odds: {o}".format(o=self.odds)
        due, next_time_to_check = super(schedule, self).is_due(last_run_at)
        if due:
            if self.max_run_every is not None:
                next_time_to_check = timedelta(
                    # TODO this will be broken until run_every.get_seconds() or
                    # w/e
                    seconds=randrange(self.run_every, self.max_run_every + 1))
            if random() <= self.odds:
                return (True, next_time_to_check)
        return (False, next_time_to_check)
