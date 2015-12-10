from logging import getLogger
from random import random, randrange

from celery.schedules import schedule as celeryschedule

logger = getLogger('celery.beat')

class schedule(celeryschedule):
    def __init__(self, name, odds, run_every, max_run_every=None,
                 relative=False, nowfun=None, app=None):
        self.name = name
        self.odds = odds
        self.max_run_every = max_run_every
        super(schedule, self).__init__(run_every, relative, nowfun, app)


    def __repr__(self):
        return "schedule(name={}, odds={}, run_every={}, max_run_every={})".format(
                   self.name, self.odds, self.run_every, self.max_run_every)


    def __reduce__(self):
        return self.__class__, (self.name, self.odds, self.run_every,
                                self.max_run_every, self.relative, self.nowfun)


    def is_due(self, last_run_at):
        due, next_time_to_check = super(schedule, self).is_due(last_run_at)
        if due:
            logger.info('{}: Due. Odds are {} or less to actually fire.'.format(
                self.name, self.odds))
            next_time_to_check = self._real_next_time_to_check()
            rando = random()
            logger.debug('{}: Got {} from random.'.format(self.name, rando))
            if rando <= self.odds:
                return (True, next_time_to_check)
            else:
                logger.debug('{}: Not this time.'.format(self.name))
        return (False, next_time_to_check)


    def _real_next_time_to_check(self):
        if self.max_run_every is None:
            next_time_to_check = self.run_every.seconds
        else:
            logger.debug('{}: First we need to know when to run next.'.format(
                self.name))
            minn = self.run_every.seconds
            maxx = self.max_run_every.seconds
            logger.debug('{}: Between {} and {} seconds.'.format(
                self.name, minn, maxx))
            next_time_to_check = randrange(minn, maxx + 1)
        logger.info('{}: Next check in {} seconds.'.format(
            self.name, next_time_to_check))
        return next_time_to_check
