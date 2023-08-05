# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from contextlib import contextmanager
import datetime
import nagiosplugin.cookie
import time


class DatetimeCookie(nagiosplugin.cookie.Cookie):

    def get(self, default=None):
        raw = super(DatetimeCookie, self).get(default)
        if raw is default:
            return default
        return datetime.datetime.fromtimestamp(float((raw or '0').strip()))

    def set(self, value=None):
        if value:
            value = str(time.mktime(value.timetuple()))
        super(DatetimeCookie, self).set(value)


@contextmanager
def datetime_cookie(filename, dir=None):
    c = DatetimeCookie(filename, dir)
    yield c
    c.close()
