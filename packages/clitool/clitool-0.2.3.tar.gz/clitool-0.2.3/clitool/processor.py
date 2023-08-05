#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Stream processing utility.
"""

import gzip
import json
import logging
import multiprocessing
import os
import sys
import time
from collections import Counter

from clitool import (
    PROCESSING_REPORTING_INTERVAL,
    PROCESSING_SUCCESS,
    PROCESSING_SKIPPED,
    PROCESSING_ERROR,
    PROCESSING_FAILURE,
    PROCESSING_TOTAL,
    PROCESSING_TIME
)


if sys.version_info.major == 3:
    import csv
    import io

    def csvreader3(fp, encoding):
        return csv.reader(io.TextIOWrapper(fp.buffer, encoding))

    csvreader = csvreader3
    imap = map  # backward compat

else:
    from itertools import imap
    from ._unicodecsv import UnicodeReader

    def csvreader2(fp, encoding):
        return UnicodeReader(fp, encoding=encoding)

    csvreader = csvreader2


class SimpleDictReporter(object):
    """ Reporting class for streamer API.
    Passing processed data as mapping object, report the key/value pair
    if value is string. To call ``report()``, you can get the result as dict.
    """

    def __init__(self, *args, **kwargs):
        self.counter = Counter()

    def __call__(self, entry):
        """
        :param entry: dictionary
        :rtype: None
        """
        if type(entry) is not dict:
            return
        for k in entry:
            v = entry[k]
            if type(v) == str:
                self.counter[k + ":" + v] += 1

    def report(self):
        """
        :rtype: dict
        """
        return dict(self.counter)


class RowMapper(object):
    """ Map `list_or_tuple` to dict object using given keys.
    If keys are not given, first `list_or_tuple` is used as keys.
    If length of given data is not different from keys length,
    no valid data is returned.

    Since this object is aimed to use with :class:`Streamer`,
    mapping is fired to call this.

    :param header: list of header values.
    """

    def __init__(self, header=None, *args, **kwargs):
        self.header = header

    def __call__(self, row, *args, **kwargs):
        """
        :param row: tuple value such as each row of csv file.
        :type row: tuple or list
        :rtype: dictionary after binding with header values.
        """
        if self.header is None or self.header == row:
            self.header = row
            logging.info("New header is set, because no header was given.")
            return
        if len(self.header) == len(row):
            return dict(zip(self.header, row))
        logging.info("Couldn't map given row: header-length=%d, row-length=%d",
            len(self.header), len(row))


class Functions(object):

    """
    :param item: item to process.
    :rtype: True if skipped, False if error, and valid object if processed.
    """

    def __init__(self, *args):
        self.procedures = tuple(filter(lambda r: r, args))
        logging.debug("%d procedures are set.", len(self.procedures))
        self.reporting_interval = PROCESSING_REPORTING_INTERVAL

    def __call__(self, tup):
        i, item = tup
        if i % self.reporting_interval == 0:
            logging.info("Processing %dth item.", i)
        if not item:  # Skip
            return True
        ret = item
        for proc in self.procedures:
            try:
                ret = proc(ret)
            except KeyboardInterrupt:
                logging.info("Stopped by user interruption at %dth item.", i)
                raise SystemExit("Stopped by user interruption.")
            except:
                logging.error("Fail to process at %dth item.", i)
                return None
            if ret is None:  # Skip
                return True
            elif not ret:  # Error
                return False
        return ret


# Can not recycle pool . . .
# http://stackoverflow.com/questions/5481104/multiprocessing-pool-imap-broken
class Streamer(object):

    """ Simple streaming module to accept step-by-step procedures.
    General steps are:

    1. check input value meets your requirements.
    2. parse something for your business.
    3. collect parsed value.

    Step 1 and Step 2 have to follow these rules:

    - return True to skip parsing
    - return False to report error
    - return something valid to continue processing the item

    Step 3 is arbitrary function to accept one argument such as
    :func:`list.append()`.

    :param callback: function to collect parsed value
    :type callback: callable
    :param args: callables
    :type args: list
    """

    def __init__(self, callback=None, *args, **kwargs):
        self.func = Functions(*args)
        self.collect = callback or (lambda r: r)
        self.processes = kwargs.get('processes')
        if self.processes and self.processes > multiprocessing.cpu_count():
                logging.warn("given processes is %d, count of CPU is %d" % (
                    self.processes, multiprocessing.cpu_count()))

    def consume(self, stream, chunksize=1):
        """ Consuming given strem object and returns processing stats.

        :param stream: streaming object to consume
        :type stream: iterable
        :rtype: dict
        """
        stats = {
            PROCESSING_TOTAL: 0,
            PROCESSING_SKIPPED: 0,
            PROCESSING_SUCCESS: 0,
            PROCESSING_ERROR: 0,
            PROCESSING_FAILURE: 0
        }
        if self.processes:
            pool = multiprocessing.Pool(processes=self.processes)
            results = pool.imap_unordered(self.func,
                        enumerate(stream, 1), chunksize=chunksize)
        else:
            results = imap(self.func, enumerate(stream, 1))
        start = time.time()
        for processed in results:
            if processed is True:
                stats[PROCESSING_SKIPPED] += 1
            elif processed:
                stats[PROCESSING_SUCCESS] += 1
                self.collect(processed)
            elif processed is None:
                stats[PROCESSING_FAILURE] += 1
            else:
                stats[PROCESSING_ERROR] += 1
            stats[PROCESSING_TOTAL] += 1
        if self.processes:
            pool.close()
            pool.join()
        stats[PROCESSING_TIME] = time.time() - start
        logging.info("finish processing on %f[sec].", stats[PROCESSING_TIME])
        logging.info(
            "STATS: total=%d, skipped=%d, success=%d, error=%d, failure=%d",
            stats[PROCESSING_TOTAL], stats[PROCESSING_SKIPPED],
            stats[PROCESSING_SUCCESS], stats[PROCESSING_ERROR],
            stats[PROCESSING_FAILURE])
        return stats


class CliHandler(object):

    """ Simple command line arguments handler.

    :param streamer: streaming object
    :type streamer: Streamer
    """

    def __init__(self, streamer):
        self.streamer = streamer

    def reader(self, fp, encoding=None):
        """ Simple `open` wrapper for several file types.
        This supports ``.gz`` and ``.json``.

        :param fp: opened file
        :type fp: file pointer
        :param encoding: encoding of opened file
        :type encoding: string
        :rtype: file pointer
        """
        _, suffix = os.path.splitext(fp.name)
        if suffix == '.gz':
            fp.close()
            return gzip.open(fp.name)
        elif suffix == '.json':
            return json.load(fp)
        return fp

    def handle(self, files, encoding, chunksize=1):
        """ Handle given files with given encoding.

        :param files: opened files.
        :type files: list
        :param encoding: encoding of opened file
        :type encoding: string
        :param chunksize: a number of chunk
        :type chunksize: int
        :rtype: list
        """
        stats = []
        try:
            if files:
                logging.info("Input file count: %d", len(files))
                for fp in files:
                    fname = fp.name
                    logging.info("Start processing: %s", fname)
                    reader = self.reader(fp, encoding)
                    parsed = self.streamer.consume(reader, chunksize)
                    logging.info("End processing: %s", fname)
                    parsed['file'] = fname
                    stats.append(parsed)
            else:
                reader = self.reader(sys.stdin, encoding)
                parsed = self.streamer.consume(reader)
                stats.append(parsed)
        except KeyboardInterrupt:
            logging.info("Stopped by user interruption.")
        return stats


class CsvHandler(CliHandler):

    def reader(self, fp, encoding):
        return csvreader(fp, encoding)


def clistream(Handler, reporter, *args, **kwargs):
    """ Handle stream data on command line interface,
    and returns statistics of success, error, and total amount.

    :param Handler: Handler for file-like streams.
    :type Handler: CliHandler which supports `handle` method.
    :param reporter: callback to report processed value
    :type reporter: callable
    :param args: functions to parse each item in the stream.
    :param kwargs: keywords, including ``files`` and ``input_encoding``.
    :rtype: list
    """
    # Follow the rule of `parse_arguments()`
    files = kwargs.get('files')
    encoding = kwargs.get('input_encoding')
    processes = kwargs.get('processes')
    chunksize = kwargs.get('chunksize')

    s = Streamer(reporter, processes=processes, *args)
    handler = Handler(s)

    return handler.handle(files, encoding, chunksize)

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
