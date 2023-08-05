# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from StringIO import StringIO
import datetime
import mock
import nagios.responsetime.logfile
import unittest


class LogFileTest(unittest.TestCase):

    def test_accepts_filename_instead_of_file(self):
        with mock.patch('__builtin__.open') as open:
            logfile = nagios.responsetime.logfile.LogFile('/path/to/file')
            open.assert_called_with('/path/to/file')
            self.assertEqual(open(), logfile.log_file)

    def test_parses_file_into_records(self):
        logfile = nagios.responsetime.logfile.LogFile(StringIO("""\
17/May/2011:14:09:42 +0200 "GET /RN342/@@searchresults.html HTTP/1.1" 0.282
17/May/2011:14:09:42 +0200 "GET /RN342/@@/kita_icon.png HTTP/1.1" 0.009
17/May/2011:14:09:43 +0200 "GET /RN342/einrichtung_4/54/ HTTP/1.1" 0.128
17/May/2011:14:09:44 +0200 "GET /RN342/++resource++arrowup.gif HTTP/1.1" 0.012
"""))
        records = logfile.parse()
        self.assertEqual(4, len(records))
        r = records[0]
        self.assertEqual(datetime.datetime(2011, 5, 17, 14, 9, 42), r.date)
        self.assertEqual('/RN342/@@searchresults.html', r.url)
        self.assertEqual(0.282, r.time)

    def test_lines_without_url_are_skipped(self):
        logfile = nagios.responsetime.logfile.LogFile(StringIO("""\
17/May/2011:14:09:42 +0200 "GET /RN342/@@searchresults.html HTTP/1.1" 0.282
17/May/2011:01:33:00 +0100 "-" -
"""))
        records = logfile.parse()
        self.assertEqual(1, len(records))

    def test_lines_without_time_are_skipped(self):
        logfile = nagios.responsetime.logfile.LogFile(StringIO("""\
17/May/2011:14:09:42 +0200 "GET /RN342/@@searchresults.html HTTP/1.1" 0.282
17/May/2011:01:31:51 +0100 "GET /login HTTP/1.1" -
"""))
        records = logfile.parse()
        self.assertEqual(1, len(records))

    def test_filters_records_according_to_date(self):
        ANY = StringIO()
        logfile = nagios.responsetime.logfile.LogFile(ANY)

        with mock.patch.object(logfile, 'parse') as parse:
            old = mock.Mock()
            old.date = datetime.datetime(2011, 5, 17, 14, 0)
            new = mock.Mock()
            new.date = datetime.datetime(2011, 5, 17, 15, 0)
            parse.return_value = [old, new]
            self.assertEqual([new], logfile.records_since(
                datetime.datetime(2011, 5, 17, 14, 0)))


class StatisticsTest(unittest.TestCase):

    def setUp(self):
        from nagios.responsetime.logfile import Record
        from datetime import datetime
        self.stats = nagios.responsetime.logfile.Statistics([
            Record(date=datetime(2011, 5, 17, 14, 1), time=0.5),
            Record(date=datetime(2011, 5, 17, 14, 2), time=1),
            Record(date=datetime(2011, 5, 17, 14, 3), time=1),
            Record(date=datetime(2011, 5, 17, 14, 4), time=1.5),
        ])

    def test_statistics(self):
        self.assertEqual(4, self.stats.count)
        self.assertEqual(0.5, self.stats.min)
        self.assertEqual(1.5, self.stats.max)
        self.assertEqual(1, self.stats.mean)
        self.assertAlmostEqual(0.4, self.stats.stddev, 1)
        self.assertEqual(datetime.datetime(2011, 5, 17, 14, 4),
                         self.stats.last_date)

    def test_single_entry_stddev_is_zero(self):
        from nagios.responsetime.logfile import Record
        from datetime import datetime
        self.stats = nagios.responsetime.logfile.Statistics([
            Record(date=datetime(2011, 5, 17, 14, 1), time=0.5)])
        self.assertEqual(1, self.stats.count)
        self.assertEqual(0.5, self.stats.mean)
        self.assertEqual(0, self.stats.stddev)
