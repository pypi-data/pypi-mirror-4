# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import nagios.responsetime.logfile
import nagios.responsetime.util
import nagiosplugin
import nagiosplugin.measure


class CheckResponseTime(nagiosplugin.Check):

    name = 'Response time check'
    version = '0.1'

    log_file = None

    def __init__(self, optparser, logger):
        super(CheckResponseTime, self).__init__(optparser, logger)
        self.logger = logger
        optparser.add_option('-f', '--logfile', help='nginx timing log file',
                             default=None)

    def process_args(self, opts, args):
        self.log_file = opts.logfile
        if not self.log_file:
            return '-f|--logfile is required'

    def obtain_data(self):
        with nagios.responsetime.util.datetime_cookie(
                'nagios.responsetime') as cookie:
            last_seen_date = cookie.get(default=datetime.datetime.min)
            stats = self.get_statistics(self.log_file, last_seen_date)
            self.measures = self.convert_to_measures(stats)
            if stats.count:
                cookie.set(stats.last_date)

    def get_statistics(self, log_file, last_seen_date):
        logfile = nagios.responsetime.logfile.LogFile(log_file)
        return nagios.responsetime.logfile.Statistics(
            logfile.records_since(last_seen_date))

    def convert_to_measures(self, stats):
        return [nagiosplugin.measure.Measure(name, getattr(stats, name))
                for name in ('min', 'max', 'mean', 'stddev', 'count')]


def main():
    nagiosplugin.Controller(CheckResponseTime)()
