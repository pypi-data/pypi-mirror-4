# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import mock
import nagios.responsetime.check
import nagiosplugin.cookie
import nagiosplugin.state
import os
import pkg_resources
import unittest


class FakeStatistics(object):

    min = 5
    max = 7
    mean = 5.5
    stddev = 1.25
    count = 27
    last_date = datetime.datetime(2011, 5, 19, 10, 51, 37)


class CheckResponseTimeTest(unittest.TestCase):

    def setUp(self):
        ANY = mock.Mock()
        self.check = nagios.responsetime.check.CheckResponseTime(ANY, ANY)

    def tearDown(self):
        # XXX We should do something clever to prevent the cookie from ending
        # up in $HOME.
        cookie = nagiosplugin.cookie.Cookie('nagios.responsetime')
        os.unlink(cookie.filename)

    def test_status_is_always_ok(self):
        with mock.patch.object(self.check, 'get_statistics') as get:
            get.return_value = FakeStatistics()
            self.check.obtain_data()

        self.assertEqual(
            nagiosplugin.state.Ok,
            reduce(nagiosplugin.state.dominantstate, self.check.states()))

    def test_performance_data_is_computed(self):
        with mock.patch.object(self.check, 'get_statistics') as get:
            get.return_value = FakeStatistics()
            self.check.obtain_data()

        self.assertEqual(
            [27, 7, 5.5, 5, 1.25],
            [m.value
             for m in sorted(self.check.measures, key=lambda m: m.name)])

    def test_no_records_available_returns_no_performance(self):
        from nagios.responsetime.logfile import Statistics
        with mock.patch.object(self.check, 'get_statistics') as get:
            get.return_value = Statistics([])
            self.check.obtain_data()
        for m in self.check.measures:
            self.assertEqual(0, m.value)

    def test_repeated_call_remembers_data_seen(self):
        self.check.log_file = mock.sentinel.log_file
        with mock.patch.object(self.check, 'get_statistics') as get:
            stats = FakeStatistics()
            get.return_value = stats

            self.check.obtain_data()
            get.assert_called_with(
                mock.sentinel.log_file, datetime.datetime.min)
            self.check.obtain_data()
            get.assert_called_with(mock.sentinel.log_file, stats.last_date)


class EndtoEndTest(unittest.TestCase):

    def run_check(self, argv):
        main = nagiosplugin.Controller(
            nagios.responsetime.check.CheckResponseTime, argv)
        main.run()
        return main.format() + main.stderr

    def test_logfile_option_is_mandatory(self):
        self.assertEqual('RESPONSE UNKNOWN - -f|--logfile is required\n',
                         self.run_check([]))

    def test_endtoend(self):
        self.assertEqual(
            'RESPONSE OK | min=0.007 max=0.289 mean=0.118111111111'
            ' stddev=0.111523613373\n| count=18\n',
            self.run_check(['-f', pkg_resources.resource_filename(
                'nagios.responsetime.tests', 'fixtures/example.log')]))
