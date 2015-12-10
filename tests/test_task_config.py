#!/usr/bin/env python
from datetime import timedelta
from unittest import main, TestCase

from coyote.utils.conf_builder import ConfigInitError, TaskConfig


class TestTaskConfig(TestCase):
    def test_defaults(self):
        tc = TaskConfig('test_defaults')
        self.assertEqual(tc.raw_config, dict())
        self.assertEqual(tc.runs, timedelta(seconds=30))
        self.assertEqual(tc.odds, float(1)/2)
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
        self.assertEqual(tc.odds, want)


    def test_odds(self):
        self._assert_odds(None, float(2)/4)
        self._assert_odds(float(1)/3, 1/float(3))
        self._assert_odds('1 / 4', float(1)/4)
        self._assert_odds('1/4', float(1)/4)
        self._assert_odds('1 in 4', float(1)/4)
        self._assert_odds('1in5', float(1)/5)
        self._assert_odds('1to6', float(1)/7)
        self._assert_odds('1 to 6', float(1)/7)
        self._assert_odds('1:7', float(1)/8)
        self._assert_odds('1 : 7', float(1)/8)
        self._assert_odds('8to1', float(8)/9)
        self._assert_odds('8 to 1', float(8)/9)
        self._assert_odds('9:1', float(9)/10)
        self._assert_odds('9 : 1', float(9)/10)
        self._assert_odds('10%', float(1)/10)
        self._assert_odds('10 %', float(1)/10)
        self._assert_odds('90 percent', float(9)/10)
        self._assert_odds('110pct', float(11)/10)
        # TODO add tests for bad odds


    def _assert_runs(self, runs, want):
        tc = TaskConfig('_assert_runs', {'runs': runs})
        self.assertEqual(tc.runs, want)


    def test_build_runs(self):
        self._assert_runs(None, timedelta(seconds=30))
        self._assert_runs(10, timedelta(seconds=10))
        self._assert_runs('20', timedelta(seconds=20))
        self._assert_runs({'min': 2, 'max': 5},
                          (timedelta(seconds=2), timedelta(seconds=5)))
        self._assert_runs({'min': '2h', 'max': '5d'},
                          (timedelta(hours=2), timedelta(days=5)))
        self._assert_runs({'max': '2h', 'min': '5d'},
                          (timedelta(hours=2), timedelta(days=5)))
        self._assert_runs({'min': '2h', 'max': '5d', 'ignore':'this'},
                          (timedelta(hours=2), timedelta(days=5)))

        kwargs = {'name': 'test', 'config': {'runs':{}}}
        self.assertRaises(ConfigInitError, TaskConfig, **kwargs)
        kwargs = {'name': 'test', 'config': {'runs':{'min':1}}}
        self.assertRaises(ConfigInitError, TaskConfig, **kwargs)
        kwargs = {'name': 'test', 'config': {'runs':{'max':2}}}
        self.assertRaises(ConfigInitError, TaskConfig, **kwargs)


    def test_bad_args_types(self):
        kwargs = {'name': 'test', 'config': {'args': str()}}
        self.assertRaises(ConfigInitError, TaskConfig, **kwargs)
        kwargs = {'name': 'test', 'config': {'args': dict()}}
        self.assertRaises(ConfigInitError, TaskConfig, **kwargs)
        kwargs = {'name': 'test', 'config': {'args': set()}}
        self.assertRaises(ConfigInitError, TaskConfig, **kwargs)


if __name__ == '__main__':
    main()
