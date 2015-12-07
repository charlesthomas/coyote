from __future__ import absolute_import
import sys
from celery import Celery
from .utils.conf_builder import AppConfig

coyoteconf = AppConfig('./coyote_config.yaml')
sys.path += coyoteconf.syspaths
app = Celery(include=coyoteconf.includes)
app.conf.update(CELERYBEAT_SCHEDULE=coyoteconf.schedules)
