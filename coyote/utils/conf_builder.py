import os.path
from datetime import timedelta
from os import walk
from random import random
from re import search
from string import letters

from yaml import safe_load

class ConfigInitError(Exception):
    pass


class TaskConfig(object):
    def __init__(self, name, config=dict()):
        self.name = name
        self.raw_config = config
        self.needs_sudo = config.get('needs_sudo', False)
        # TODO account for AppConfig.halt_on_init_error
        self.runs = self._build_run(config.get('runs', None))
        self.odds = self._calculate_odds(config.get('odds', None))
        args = config.get('args', None)
        if args is not None:
            if type(args) != list:
                raise ConfigInitError("args must be a list!\n",args)
            self.args = args


    @property
    def schedule(self):
        # TODO this should be fixed if/when we figure out custom scheduler
        d = dict(task=self.name) #, schedule=self.runs)
        if type(self.runs) == tuple:
            self.runs = self.runs[0]
        d.update(schedule=self.runs)
        if hasattr(self, 'args'):
            d.update(args=self.args)
        return d


    def _build_run(self, runs):
        if runs is None:
            return timedelta(seconds=30)
        if type(runs) == int:
            return timedelta(seconds=runs)
        if type(runs) == str:
            return self._calculate_timedelta(runs)
        if type(runs) == dict and runs.has_key('min') and runs.has_key('max'):
            minn = self._calculate_timedelta(runs['min'])
            maxx = self._calculate_timedelta(runs['max'])
            if minn > maxx:
                return (maxx, minn)
            return (minn, maxx)
        raise ConfigInitError(
            'unable to figure out how often {name} should based on '
            '{sched}'.format(name=self.name, sched=runs))


    def _calculate_odds(self, odds):
        if odds is None:
            return float(1)/2
        if type(odds) == float:
            return odds
        if '%' in odds or 'p' in odds:
            return float((odds.translate(None, letters + '%'))) / 100
        match = search(r'(\d+)\s?(\S*)\s?(\d+)', odds)
        if match is not None:
            numerator = float(match.group(1))
            denominator = float(match.group(3))
            designator = match.group(2)
            if designator == ':' or designator.lower() == 'to':
                denominator = numerator + denominator
            return numerator / denominator
        raise ConfigInitError('unable to determine odds of', odds)


    def _calculate_timedelta(self, time_string):
        time_string = str(time_string)
        if 'd' in time_string and 'c' not in time_string:
            key = 'days'
        elif 'h' in time_string:
            key = 'hours'
        elif 'm' in time_string:
            key = 'minutes'
        else:
            key = 'seconds'
        kwargs = {key: int(time_string.translate(None, letters + ' '))}
        return timedelta(**kwargs)


class ModConfig(object):
    def __init__(self, yamlpath):
        yamlpath = os.path.abspath(yamlpath)
        try:
            with open(yamlpath) as f:
                self.raw_config = safe_load(f)
        except Exception as err:
            raise ConfigInitError(err)
        self.import_path = self.raw_config.get('path', None)
        if self.import_path is None or not os.path.exists(self.import_path):
            raise ConfigInitError('path is missing for', yamlpath)
        self.tasks = [TaskConfig(key, val) for key, val in \
                      self.raw_config.get('tasks', dict()).items()]


    @property
    def schedules(self):
        schedules = dict()
        for task in self.tasks:
            key = task.schedule['task']
            schedules[key] = task.schedule
        return schedules


    @property
    def syspath(self):
        # TODO this def won't work on windows
        # does that matter?
        syspath = self.import_path.split('/')[:-2]
        if len(syspath) == 0:
            return None
        if syspath[0] == '':
            syspath[0] = '/'
        syspath = os.path.join(*syspath)
        return syspath


    @property
    def include(self):
        return '{i}.tasks'.format(i=self.import_path.split('/')[-2])


class AppConfig(object):
    DEFAULT_CONFIG_DIRS = ['./conf', '/etc/coyote/conf.d']
    def __init__(self, yamlpath):
        yamlpath = os.path.abspath(yamlpath)
        try:
            with open(yamlpath) as f:
                self.raw_config = safe_load(f)
        except Exception as err:
            raise ConfigInitError(err)
        if self.raw_config is None:
            self.raw_config = dict()
        self.has_sudo = self.raw_config.get('has_sudo', False)
        self.config_dirs = self.raw_config.get(
            'config_dirs', [d for d in self.DEFAULT_CONFIG_DIRS if
                            os.path.exists(d)])
        self.celery_config = self.raw_config.get('celery_config', None)
        self.dry_run = self.raw_config.get('dry_run', False)
        self.halt_on_init_error = self.raw_config.get('halt_on_init_error', True)
        # TODO this doesn't do anything yet
        self.include_default_tasks = self.raw_config.get('include_default_tasks', True)
        self.modules = self._build_modules_list()


    @property
    def schedules(self):
        schedules = dict()
        for module in self.modules:
            for key, val in module.schedules.items():
                schedules[key]=val
        return schedules


    @property
    def syspaths(self):
        return list(set( # unique the list
            [m.syspath for m in self.modules if m.syspath is not None]))


    @property
    def includes(self):
        return list(set([m.include for m in self.modules]))


    def _build_modules_list(self):
        yamls = list()
        mods = list()
        for config_dir in self.config_dirs:
            for root, dirs, files in walk(config_dir):
                [yamls.append(os.path.join(root, f)) for f in files if
                 f.endswith('.yaml')]
        for yaml in yamls:
            try:
                mods.append(ModConfig(yaml))
            except ConfigInitError as err:
                if self.halt_on_init_error:
                    raise
                else:
                    # TODO this should be a log
                    print err
        return mods
