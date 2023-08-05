#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Utilities to parse Apache access log.
"""

import datetime
import re
import logging
try:     # Python 3.x
    import urllib.parse
    urlparse = urllib.parse.urlparse
    parse_qs = urllib.parse.parse_qs
except:  # Python 2.x
    import urlparse as urlparse2
    urlparse = urlparse2.urlparse
    parse_qs = urlparse2.parse_qs


# Probably default access log format for IPv4
LOG_FORMAT = re.compile(r"""^
    (?P<remote_address>\d+\.\d+\.\d+\.\d+)\ -\ -\ \[(?P<access_time>.+)\]\s
    "(?P<request_method>[A-Z]+)\s(?P<request_path>\S+)\s?
    (?P<request_version>HTTP/[\d]\.[\d])?"\s
    (?P<response_status>\d+)\s(?P<response_size>\d+|-)\s
    "(?P<referer>[^"]+)"\s"(?P<user_agent>[^"]+)"
    .*  # implement on your own if using custom log format
$""", re.VERBOSE)


# http://stackoverflow.com/questions/526406/python-time-to-age-part-2-timezones
def parse_access_time(s, ignore_timezone=True):
    d, tz = s.split(' ')
    t = datetime.datetime.strptime(d, "%d/%b/%Y:%H:%M:%S")
    if ignore_timezone:
        return t
    else:
        try:
            offset = int(tz)
        except:
            return None
        delta = datetime.timedelta(hours=offset / 100)
        return t - delta


def parse_request_path(s):
    """ Parse request path and return tuple of path and query params.
    """
    o = urlparse(s)
    if o.query:
        return (o.path, parse_qs(o.query))
    return (o.path, None)


class AccesslogParser(object):

    def __init__(self, logformat=LOG_FORMAT):
        self.logformat = logformat

    def __call__(self, raw):
        entry = self.logformat.match(raw.strip())
        if entry:
            return entry.groupdict()
        logging.error("Could not match given log format: %s", raw)


def logentry(entry):
    """ Process mapped entry which has following keys:

    - access_time: date-time string formatted by ``%d/%b/%Y:%H:%M:%S``.
    - request_path: HTTP request path, this will be splitted from query.
    - response_status: HTTP response status code.
    - response_size: HTTP response size, this will be casted to 'int'.
    - referer: Referer header. if "-" is given, that will be ignored.

    If error response_status was detected, its access time and request path
    is reported via logger. And retured entry includes error key.

    "request_query" will be added if "request_path" has query string.
    Note that this is key/values mapping even if values have one element.

    :param entry: regex parsed object
    :type entry: dict
    :rtype: dict
    """
    entry['access_time'] = parse_access_time(entry['access_time'])
    path, query = parse_request_path(entry['request_path'])
    entry['request_path'] = path
    if query:
        entry['request_query'] = query
    if entry['response_status']:
        s = int(entry['response_status'])
        if s >= 400:
            logging.info("Error response [%d] was detected: %s at [%s]",
                        s, entry['request_path'], entry['access_time'])
            entry['error_%d' % (s,)] = entry['request_path']
    if entry['response_size'] == '-':  # Apache internal dummy connection
        entry['response_size'] = None
    elif entry['response_size']:
        # int type is not reported on processor.SimpleDictReporter
        entry['response_size'] = int(entry['response_size'])
    if entry['referer'] == '-':
        entry['referer'] = None
    return entry


def logparse(logformat=LOG_FORMAT, analyzer=None, *args, **kwargs):
    """ Parse access log.

    :param logformat: access log format
    :type logformat: regex
    :param analyzer: function for each parsed object
    :type analyzer: callable
    :rtype: tuple of (statistics, key/value report)
    """

    from clitool.processor import clistream, CliHandler, SimpleDictReporter

    reporter = SimpleDictReporter()
    stats = clistream(CliHandler, reporter,
                AccesslogParser(logformat), logentry, analyzer, **kwargs)
    return stats, reporter.report()


if __name__ == '__main__':
    from pprint import pprint
    from clitool.cli import parse_arguments

    args = parse_arguments()
    stats, report = logparse(files=args.files, encoding=args.input_encoding)
    pprint(stats)
    pprint(report)

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
