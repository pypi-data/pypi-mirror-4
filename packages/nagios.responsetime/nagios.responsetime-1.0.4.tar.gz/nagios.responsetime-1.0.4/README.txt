A Nagios plugin that collects response times from logs.

Usage: ``check_responsetime --logfile /path/to/logfile``

The plugin remembers the timestamp of the latest log entry it has seen on each
run, and on the next run only considers log entries that are more recent.

Log format
==========

The supported log format is as follows::

    <timestamp> "<http-verb> <path> <http-version>" <responsetime>

- timestamp: %d/%b/%Y:%H:%M:%S %z
- http-verb: GET, POST
- path: the requested URL path
- http-version: e.g. HTTP/1.1
- responsetime in seconds, e. g. 0.5

Example::

    17/May/2011:14:11:18 +0200 "GET /index.html HTTP/1.1" 0.289

An example configuration for the nginx server looks like this::

    http {
        log_format timing '$time_local "$request" $upstream_response_time';

        server {
            access_log /path/to/timing.log timing;
        }
    }


Future directions
=================

One obvious additional feature is the ability to define thresholds (e.g. "a
mean responsetime above 3 seconds is WARN, above 5 CRITICAL")


Development
===========

The source code is available in the mercurial repository at
https://code.gocept.com/hg/public/nagios.responsetime

Please report any bugs you find to `Wolfgang Schnerring`_.

.. _`Wolfgang Schnerring`: mailto:ws@gocept.com
