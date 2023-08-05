# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime


class LogFile(object):

    def __init__(self, log_file):
        if isinstance(log_file, str):
            log_file = open(log_file)
        self.log_file = log_file

    def parse(self):
        result = []
        for line in self.log_file.readlines():
            parts = line.strip().split(' ')
            try:
                result.append(Record(
                    # XXX handle timezone info in parts[1]
                    date=self._parse_date(parts[0]),
                    url=parts[3],
                    time=float(parts[-1])))
            except ValueError:
                continue
        return result

    def _parse_date(self, date):
        return datetime.datetime.strptime(date, '%d/%b/%Y:%H:%M:%S')

    def records_since(self, last_seen_date):
        return [x for x in self.parse() if x.date > last_seen_date]


class Record(object):

    def __init__(self, **kw):
        self.__dict__.update(kw)


class Statistics(object):

    def __init__(self, records):
        # assumption: records are sorted chronologically
        self.records = records
        self.times = [x.time for x in self.records]

    @property
    def min(self):
        if self.count == 0:
            return 0
        return min(self.times)

    @property
    def max(self):
        if self.count == 0:
            return 0
        return max(self.times)

    @property
    def mean(self):
        if self.count == 0:
            return 0
        return sum(self.times) / self.count

    @property
    def stddev(self):
        if self.count <= 1:
            return 0
        squares = sum([(i - self.mean) ** 2 for i in self.times])
        return (squares / (self.count - 1)) ** 0.5

    @property
    def count(self):
        return len(self.records)

    @property
    def last_date(self):
        return self.records[-1].date
