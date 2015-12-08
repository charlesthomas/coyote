#!/usr/bin/env python
from unittest import main, TestCase

from coyote.utils.conf_builder import ConfigInitError, AppConfig

class TestAppConfig(TestCase):
    def test_app_config_dne(self):
        self.assertRaises(ConfigInitError, AppConfig, '/d/n/e/conf.yaml')


    def test_defaults(self):
        app = AppConfig('tests/cases/empty_app_config/coyote.yaml')
        self.assertEqual(app.raw_config, dict())
        self.assertTrue(app.halt_on_init_error)
        self.assertFalse(app.dry_run)
        self.assertIsNone(app.celery_config)


    def test_config_dir_dne(self):
        self.assertRaises(ConfigInitError, AppConfig,
                          'tests/cases/config_dne_do_halt/coyote.yaml')
        # TODO swallow error logging for test run
        app = AppConfig('tests/cases/config_dne_dont_halt/coyote.yaml')


if __name__ == '__main__':
    main()
