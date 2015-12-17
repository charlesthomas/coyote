import logging
import os.path
from datetime import timedelta
from os import walk
from random import random
from re import search
from string import letters

from yaml import safe_load

from coyote.utils.scheduler import schedule


# steal celery's log format, but change name for distinction in messages
logging.basicConfig(format="[%(asctime)s: %(levelname)s/COYOTECONFIG] %(message)s")
logger = logging.getLogger(__name__)


class ConfigInitError(Exception):
    pass


class BaseConfig(object):
    def _build_config_from_yaml(self, yamlpath):
        yamlpath = os.path.abspath(yamlpath)
        try:
            with open(yamlpath) as f:
                conf = safe_load(f)
                if conf is None:
                    return dict()
                return conf
        except Exception as err:
            raise ConfigInitError(err)


class TaskConfig(BaseConfig):
    def __init__(self, name, config=dict()):
        self.name = name
        self.raw_config = config
        self.runs = self._build_run(config.get('runs', None))
        self.odds = self._calculate_odds(config.get('odds', None))
        args = config.get('args', None)
        if args is not None:
            # celery requires args to be a list or tuple
            if type(args) != list and type(args) != tuple:
                args = [args]
            self.args = args
        # schedule requires args to be set first
        self.schedule = self._build_schedule()
        logger.info('New Task: {}'.format(self))


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        s = "TaskConfig(name={n}, runs={r}, odds={o}"
        kwargs = dict(n=self.name, r=self.runs, o=self.odds)
        if hasattr(self, 'args'):
            s += ", args={a}"
            kwargs.update(a=self.args)
        return s.format(**kwargs)


    def _build_schedule(self):
        if type(self.runs) == tuple:
            sched = dict(min_run_every=self.runs[0], max_run_every=self.runs[1])
        else:
            sched = dict(min_run_every=self.runs)
        built_schedule = dict(task=self.name,
                              schedule=schedule(name=self.name, odds=self.odds,
                              **sched))
        if hasattr(self, 'args'):
            built_schedule.update(args=self.args)
        return built_schedule



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


class ModConfig(BaseConfig):
    def __init__(self, yamlpath, halt_on_init_error=True):
        logger.info('Building ModConfig from {}'.format(yamlpath))
        self.yamlpath = yamlpath
        self.halt_on_init_error = halt_on_init_error
        self.raw_config = self._build_config_from_yaml(yamlpath)
        self.import_path = self.raw_config.get('path', None)
        logger.debug('ModConfig import_path: {}'.format(self.import_path))
        logger.debug('ModConfig include: {}'.format(self.include))
        logger.debug('ModConfig syspath: {}'.format(self.syspath))
        if self.import_path is None or not os.path.exists(self.import_path):
            raise ConfigInitError('path is missing for', yamlpath)
        self.tasks = self._build_tasks_list(halt_on_init_error)


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        return ("ModConfig(import_path={imp}, include={inc}, schedules={sch}, "
                "syspath={sysp}, tasks={tasks}".format(
                    imp=self.import_path, inc=self.include, sch=self.schedules,
                    sysp=self.syspath, tasks=[t.__str__() for t in self.tasks]))


    @property
    def include(self):
        a, b = self.import_path.split('/')[-2:]
        b = b.replace('.py','')
        return '{}.{}'.format(a, b)


    @property
    def schedules(self):
        schedules = dict()
        for task in self.tasks:
            if task.schedule is not None:
                key = task.schedule['task']
                schedules[key] = task.schedule
        return schedules


    @property
    def syspath(self):
        syspath = self.import_path.split(os.path.sep)[:-2]
        if len(syspath) == 0:
            return None
        if syspath[0] == '':
            syspath[0] = '/'
        syspath = os.path.join(*syspath)
        return syspath


    def _build_tasks_list(self, halt_on_init_error):
        tasks = list()
        for key, val in self.raw_config.get('tasks', dict()).items():
            try:
                tasks.append(TaskConfig(key, val))
            except ConfigInitError as err:
                if halt_on_init_error:
                    raise err
                else:
                    logger.error(err)
        return tasks


class AppConfig(BaseConfig):
    DEFAULT_CONFIG_DIRS = ['./task_configs', '/etc/coyote/conf.d']
    def __init__(self, yamlpath):
        self.app_config_path = yamlpath
        self.raw_config = self._build_config_from_yaml(yamlpath)

        self.log_level = self.raw_config.get('log_level', 'ERROR')
        logger.setLevel(self.log_level.upper())
        logger.info('Building AppConfig from {}'.format(yamlpath))
        logger.debug('AppConfig log_level: {}'.format(self.log_level))
        self.celery_config = self.raw_config.get('celery_config', None)
        logger.debug('AppConfig celery_config: {}'.format(self.celery_config))
        self.dry_run = self.raw_config.get('dry_run', False)
        logger.debug('AppConfig dry_run: {}'.format(self.dry_run))
        self.include_default_tasks = self.raw_config.get('include_default_tasks', True)
        logger.debug('AppConfig include_default_tasks: {}'.format(
            self.include_default_tasks))
        self.halt_on_init_error = self.raw_config.get('halt_on_init_error', True)
        logger.debug('AppConfig halt_on_init_error: {}'.format(
            self.halt_on_init_error))

        # these may require options set above
        self.config_dirs = self._build_config_dirs()
        logger.debug('AppConfig config_dirs: {}'.format(
            ', '.join(self.config_dirs)))
        self.modules = self._build_modules_list()


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        return ("AppConfig(app_config_path={a}, celery_config={cc}, "
                "dry_run={dr}, include_default_tasks={idt}, "
                "halt_on_init_error={h}, config_dirs={cd}, includes={inc}, "
                "schedule{sch}, syspaths={sysp}, modules={m}".format(
                    a=self.app_config_path, cc=self.celery_config,
                    dr=self.dry_run, idt=self.include_default_tasks,
                    h=self.halt_on_init_error, cd=self.config_dirs,
                    inc=self.includes, sch=self.schedules, sysp=self.syspaths,
                    m=[mod.__str__() for mod in self.modules]))


    def _build_config_dirs(self):
        config_dirs = list()
        if self.include_default_tasks:
            config_dirs += [d for d in self.DEFAULT_CONFIG_DIRS if
                            os.path.exists(d)]
        for d in self.raw_config.get('config_dirs', list()):
            if not os.path.exists(d):
                err = ("{a} specifies scanning {d} for task configs but it "
                      "doesn't exist".format(a=self.app_config_path, d=d))

                if self.halt_on_init_error:
                    raise ConfigInitError(err)
                else:
                    logger.error(err)
                    continue
            config_dirs.append(d)
        return config_dirs


    @property
    def includes(self):
        return list(set([m.include for m in self.modules]))


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


    def _build_modules_list(self):
        yamls = list()
        mods = list()
        for config_dir in self.config_dirs:
            for root, dirs, files in walk(config_dir):
                [yamls.append(os.path.join(root, f)) for f in files if
                 f.endswith('.yaml')]
        for yaml in yamls:
            try:
                mods.append(ModConfig(yaml, self.halt_on_init_error))
            except ConfigInitError as err:
                if self.halt_on_init_error:
                    raise
                else:
                    logger.error(err)
        return mods
