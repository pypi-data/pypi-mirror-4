#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Utilities to parse Apache access log.

To get known about access log, see Apache HTTP server official document.
[`en <http://httpd.apache.org/docs/2.4/en/logs.html>`_]
[`ja <http://httpd.apache.org/docs/2.4/ja/logs.html>`_]

Most simple script is::

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    from pprint import pprint

    from clitool.cli import climain
    from clitool.accesslog import logparse

    @climain
    def main(output, **kwargs):
        stats, report = logparse(**kwargs)
        pprint(report, stream=output)

    if __name__ == '__main__':
        main()

"""

import datetime
import re
import warnings
from collections import namedtuple

__all__ = ['logparse']
warnings.simplefilter("always")

# since `strptime()` is too slow, parse on regex matching.
MONTH_ABBR = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

# Probably default access log format for IPv4
LOG_FORMAT = re.compile(r"""^
    (?P<remote_address>\S+)\s-\s-\s
    \[(?P<day>\d{2})/(?P<month>[A-Z][a-z]{2})/(?P<year>\d{4}):
      (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})\s
      (?P<timezone>[+-]\d{4})\]\s
    "(?P<request_method>[A-Z]+)\s
     (?P<request_path>[^?^ ]+)\??(?P<request_query>\S+)?\s?
     (?P<request_version>HTTP/\d\.\d)?"\s
    (?P<response_status>\d{3})\s(?P<response_size>\d+|-)\s
    "(?P<referer>[^"]+)"\s"(?P<user_agent>[^"]+)"
    (?P<trailing>.*)
$""", re.VERBOSE)

Access = namedtuple('Access',
    '''remote_address day month year hour minute second timezone
    request_method request_path request_query request_version
    response_status response_size referer user_agent trailing''')


def logentry(raw):
    """ Process accesslog record to map Python dictionary.

    Returned dictionary has following keys:

    - remote_address: remote IP address.
    - access_time: datetime object.
    - request_path: HTTP request path, this will be splitted from query.
    - request_query: HTTP requert query string removed from "?".
    - request_method: HTTP request method.
    - request_version: HTTP request version.
    - response_status: HTTP response status code. (int)
    - response_size: HTTP response size, if available. (int)
    - referer: Referer header. if "-" is given, that will be ignored.
    - user_agent: User agent. if "-" is given, that will be ignored.
    - trailing: Additional information if using custom log format.

    :param access: internal object which represent accesslog record
    :type access: Access
    :rtype: dict
    """
    m = LOG_FORMAT.match(raw.rstrip())
    if m is None:
        return
    access = Access._make(m.groups())
    entry = {
        'remote_address': access.remote_address,
        'request_path': access.request_path,
        'request_query': access.request_query,
        'request_method': access.request_method,
        'request_version': access.request_version,
        'response_status': int(access.response_status)
    }
    entry['access_time'] = datetime.datetime(
        int(access.year), MONTH_ABBR[access.month], int(access.day),
        int(access.hour), int(access.minute), int(access.second))
    if access.response_size != '-':
        entry['response_size'] = int(access.response_size)
    if access.referer != '-':
        entry['referer'] = access.referer
    if access.user_agent != '-':
        entry['user_agent'] = access.user_agent
    if access.trailing:
        entry['trailing'] = access.trailing.strip()
    return entry


def logparse(*args, **kwargs):
    """ Parse access log on the terminal application.
    If list of files are given, parse each file. Otherwise, parse standard
    input.

    :param args: supporting functions after processed raw log line
    :type: list of callables
    :rtype: tuple of (statistics, key/value report)
    """
    from clitool.cli import clistream
    from clitool.processor import SimpleDictReporter

    lst = [logentry]
    analyzer = kwargs.get('analyzer')
    if analyzer:
        warnings.warn("analyzer keyword is deprecated.", DeprecationWarning)
        lst.append(analyzer)
    lst += args
    reporter = SimpleDictReporter()
    stats = clistream(reporter, *lst, **kwargs)
    return stats, reporter.report()


if __name__ == '__main__':
    import json
    from clitool.cli import parse_arguments

    args = parse_arguments(files=dict(nargs='*'))
    stats, report = logparse(files=args.files)
    json.dump({'stats': stats, 'report': report}, args.output, indent=2)

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
