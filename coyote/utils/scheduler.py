from datetime import timedelta
from logging import getLogger
from random import random, randrange

from celery.beat import PersistentScheduler
from celery.schedules import schedule as celeryschedule

logger = getLogger('celery.beat')


class Scheduler(PersistentScheduler):
    def maybe_due(self, entry, publisher=None):
	if not hasattr(entry.schedule, 'odds'):
	    return super(Scheduler, self).maybe_due(entry, publisher)

	is_due, next_time_to_run = entry.is_due()
	if is_due and random() <= entry.schedule.odds:
	    logger.info('Scheduler: Sending due task %s (%s)', entry.name, entry.task)
            try:
                result = self.apply_async(entry, publisher=publisher)
            except Exception as exc:
                logger.error('Message Error: %s\n%s',
                      exc, traceback.format_stack(), exc_info=True)
            else:
                logger.debug('%s sent. id->%s', entry.task, result.id)
	elif is_due:
	    logger.info("didn't fire: {}".format(entry.name))
	    self.reserve(entry)
	    entry.schedule.run_every = entry.schedule.randomize_run_every()
        return next_time_to_run


class schedule(celeryschedule):
    def __init__(self, name, odds, min_run_every, max_run_every=None,
                 run_every=None, relative=False, nowfun=None, app=None):
        self.name = name
        self.odds = odds
	self.min_run_every = min_run_every
	self.max_run_every = max_run_every
	self.run_every = run_every or self.randomize_run_every()
	self.relative = relative
	self.nowfun = nowfun
	self._app = app


    def __repr__(self):
        return ("schedule(name={}, odds={}, min_run_every={}, max_run_every={} "
                "run_every={})".format(self.name, self.odds, self.min_run_every,
                                       self.max_run_every, self.run_every))


    def __reduce__(self):
        return self.__class__, (self.name, self.odds, self.min_run_every,
				self.max_run_every, self.run_every,
                                self.relative, self.nowfun)


    def randomize_run_every(self):
        if self.max_run_every is None:
            return self.min_run_every
        run = randrange(self.min_run_every.total_seconds(),
                         self.max_run_every.total_seconds() + 1)
	return timedelta(seconds=run)
