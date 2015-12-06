#!/usr/bin/env python
from datetime import timedelta
from unittest import main, TestCase

from coyote.utils.conf_builder import (AppConfig, ConfigInitError,
                                       ModConfig, TaskConfig)


class TestHelloWorld(TestCase):
    def test_hello_world(self):
        self.assertTrue(True)


class TestTaskConfig(TestCase):
    def test_defaults(self):
        tc = TaskConfig('test_defaults')
        self.assertEqual(tc.raw_config, dict())
        self.assertFalse(tc.needs_sudo)
        self.assertEqual(tc.runs, timedelta(seconds=30))
        self.assertEqual(tc.odds, float(1/2))
        self.assertFalse(hasattr(tc, 'args'))


    def _assert_timedelta(self, time_string, want):
        tc = TaskConfig('_assert_timedelta')
        self.assertEqual(want, tc._calculate_timedelta(time_string))


    def test_seconds(self):
        self._assert_timedelta(1, timedelta(seconds=1))
        self._assert_timedelta('2', timedelta(seconds=2))
        self._assert_timedelta('3s', timedelta(seconds=3))
        self._assert_timedelta('4 s', timedelta(seconds=4))
        self._assert_timedelta('5seconds', timedelta(seconds=5))
        self._assert_timedelta('6 seconds', timedelta(seconds=6))
        self._assert_timedelta('7sec', timedelta(seconds=7))
        self._assert_timedelta('8 sec', timedelta(seconds=8))


    def test_minutes(self):
        self._assert_timedelta('1m', timedelta(minutes=1))
        self._assert_timedelta('2 m', timedelta(minutes=2))
        self._assert_timedelta('3min', timedelta(minutes=3))
        self._assert_timedelta('4 min', timedelta(minutes=4))
        self._assert_timedelta('5minutes', timedelta(minutes=5))
        self._assert_timedelta('6 minutes', timedelta(minutes=6))
        self._assert_timedelta('7mins', timedelta(minutes=7))
        self._assert_timedelta('8 mins', timedelta(minutes=8))


    def test_hours(self):
        self._assert_timedelta('1h', timedelta(hours=1))
        self._assert_timedelta('2 h', timedelta(hours=2))
        self._assert_timedelta('3hr', timedelta(hours=3))
        self._assert_timedelta('4 hr', timedelta(hours=4))
        self._assert_timedelta('5hours', timedelta(hours=5))
        self._assert_timedelta('6 hours', timedelta(hours=6))
        self._assert_timedelta('7hrs', timedelta(hours=7))
        self._assert_timedelta('8 hrs', timedelta(hours=8))


    def test_days(self):
        self._assert_timedelta('1d', timedelta(days=1))
        self._assert_timedelta('2 d', timedelta(days=2))
        self._assert_timedelta('3day', timedelta(days=3))
        self._assert_timedelta('4 day', timedelta(days=4))
        self._assert_timedelta('5days', timedelta(days=5))
        self._assert_timedelta('6 days', timedelta(days=6))


    def _assert_odds(self, odds, want):
        tc = TaskConfig('_assert_odds', {'odds': odds})
        self.assertEqual(tc.odds, float(want))


    def test_odds(self):
        self._assert_odds(None, 1/2)
        self._assert_odds(float(1/3), 1/3)
        self._assert_odds('1 / 4', 1/4)
        self._assert_odds('1/4', 1/5)
        self._assert_odds('1 in 4', 1/4)
        self._assert_odds('1in5', 1/5)
        self._assert_odds('1to6', 1/7)
        self._assert_odds('1 to 6', 1/7)
        self._assert_odds('1:7', 1/8)
        self._assert_odds('1 : 7', 1/8)
        self._assert_odds('8to1', 8/9)
        self._assert_odds('8 to 1', 8/9)
        self._assert_odds('9:1', 9/10)
        self._assert_odds('9 : 1', 9/10)
        self._assert_odds('10%', 1/10)
        self._assert_odds('10 %', 1/10)
        self._assert_odds('90 percent', 9/10)
        self._assert_odds('110pct', 11/10)


    def test_build_runs(self):
        pass


if __name__ == '__main__':
    main()
