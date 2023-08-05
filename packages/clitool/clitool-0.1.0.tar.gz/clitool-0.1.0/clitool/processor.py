#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Stream processing utility.
"""

import logging
import gzip
import json
import os
import sys
import time
from collections import Counter

from clitool.const import (
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

else:
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
        if type(entry) is not dict:
            return
        for k in entry:
            v = entry[k]
            if type(v) == str:
                self.counter[k + ":" + v] += 1

    def report(self):
        return dict(self.counter)


class RowMapper(object):
    """ Map list_or_tuple to dict object using given keys.
    If keys are not given, first list_or_tuple is used as keys.
    If length given data is not different from keys length,
    no valid data is returned.
    """

    def __init__(self, header=None, *args, **kwargs):
        self.header = header

    def __call__(self, row, *args, **kwargs):
        if self.header is None or self.header == row:
            self.header = row
            logging.info("New header is set, because no header was given.")
            return
        if len(self.header) == len(row):
            return dict(zip(self.header, row))
        logging.info("Couldn't map given row: header-length=%d, row-length=%d",
            len(self.header), len(row))


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
    `list.append()`.
    """

    def __init__(self, callback=None, *args, **kwargs):
        """
        :param: collect callable to collect parsed value
        :param: args procedures
        """
        self.procedures = tuple(filter(lambda r: r, args))
        self.collect = callback or (lambda r: r)
        self.reporting_interval = PROCESSING_REPORTING_INTERVAL
        logging.debug("%d procedures are set.", len(self.procedures))

    def process_stream_item(self, item):
        if not item:  # Skip
            return True
        ret = item
        for proc in self.procedures:
            ret = proc(ret)
            if ret is None:  # Skip
                return True
            elif not ret:  # Error
                return False
        self.collect(ret)
        return ret

    def iterate(self, stream):
        """ Generator interface to allow iterable process.
        """
        for i, raw in enumerate(stream, 1):
            try:
                processed = self.process_stream_item(raw)
            except KeyboardInterrupt:
                logging.info("Stopped by user interruption at %dth item.", i)
                raise SystemExit("Stopped by user interruption.")
            except:
                processed = None
                logging.error("Fail to process at %dth item.", i)
            yield processed
            if i % self.reporting_interval == 0:
                logging.info("Processed %dth item.", i)

    def consume(self, stream):
        """
        :param: stream streaming object to iterate.
        :return: stats after processing
        """
        stats = {
            PROCESSING_TOTAL: 0,
            PROCESSING_SKIPPED: 0,
            PROCESSING_SUCCESS: 0,
            PROCESSING_ERROR: 0,
            PROCESSING_FAILURE: 0
        }
        start = time.time()
        for processed in self.iterate(stream):
            if processed is True:
                stats[PROCESSING_SKIPPED] += 1
            elif processed:
                stats[PROCESSING_SUCCESS] += 1
            elif processed is None:
                stats[PROCESSING_FAILURE] += 1
            else:
                stats[PROCESSING_ERROR] += 1
            stats[PROCESSING_TOTAL] += 1
        stats[PROCESSING_TIME] = time.time() - start
        logging.info("finish processing on %f[sec].", stats[PROCESSING_TIME])
        logging.info(
            "STATS: total=%d, skipped=%d, success=%d, error=%d, failure=%d",
            stats[PROCESSING_TOTAL], stats[PROCESSING_SKIPPED],
            stats[PROCESSING_SUCCESS], stats[PROCESSING_ERROR],
            stats[PROCESSING_FAILURE])
        return stats

# XXX: Import simple map-reduce script.
# `http://www.doughellmann.com/PyMOTW/multiprocessing/mapreduce.html`


class CliHandler(object):

    def __init__(self, streamer):
        self.streamer = streamer

    def reader(self, fp, encoding=None):
        _, suffix = os.path.splitext(fp.name)
        if suffix == '.gz':
            fp.close()
            return gzip.open(fp.name)
        elif suffix == '.json':
            return json.load(fp)
        return fp

    def handle(self, files, encoding):
        stats = []
        try:
            if files:
                logging.info("Input file count: %d", len(files))
                # XXX: enable multiprocessing support
                for fp in files:
                    fname = fp.name
                    logging.info("Start processing: %s", fname)
                    reader = self.reader(fp, encoding)
                    parsed = self.streamer.consume(reader)
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
    """ Handle stream data on command line interface.

    :return: statistics of success, error, and total amount.
    """
    # Follow the rule of `parse_arguments()`
    files = kwargs.get('files')
    encoding = kwargs.get('input_encoding')

    s = Streamer(reporter, *args)
    handler = Handler(s)

    return handler.handle(files, encoding)

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
