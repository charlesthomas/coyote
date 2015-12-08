from __future__ import absolute_import
import logging
import sys
from os import environ

from celery import Celery

from .utils.conf_builder import AppConfig

coyote_config = environ.get('COYOTECONFIG', 'coyote.yaml')
coyote = AppConfig(coyote_config)
logging.info(coyote)
sys.path += coyote.syspaths
app = Celery(include=coyote.includes)

# assume this shouldn't be trapped by coyote.halt_on_init_error = False
if coyote.celery_config is not None:
    app.config_from_object(coyote.celery_config)

app.conf.update(CELERYBEAT_SCHEDULE=coyote.schedules)
