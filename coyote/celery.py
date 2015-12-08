from __future__ import absolute_import
import sys
from celery import Celery
from .utils.conf_builder import AppConfig

coyote = AppConfig('config.yaml')
sys.path += coyote.syspaths
app = Celery(include=coyote.includes)
app.conf.update(CELERYBEAT_SCHEDULE=coyote.schedules)
