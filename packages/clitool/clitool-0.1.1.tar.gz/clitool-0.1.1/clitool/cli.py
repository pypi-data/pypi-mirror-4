#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Command line utilities.

This module is executable to create script boilerplate. ::

    $ python -m clitool.cli
"""

import logging
import inspect
import os
import sys
import argparse
from functools import wraps

from clitool import DEFAULT_ENCODING
from clitool.config import ConfigLoader


def base_parser():
    """ Create arguments parser with basic options and no help message.

    * -c, --config: load configuration file.
    * -v, --verbose: set up logging verbosity.
    * -q, --quiet: quiet logging.
    * -o, --output: output file. (default=sys.stdout)
    * --basedir: base directory. (default=os.getcwd)
    * --input-encoding: input data encoding. (default=utf-8)
    * --output-encoding: output data encoding. (default=utf-8)
    """
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("-c", "--config", dest="config",
                type=argparse.FileType('r'),
                metavar="FILE",
                help="configuration file")

    parser.add_argument("-o", "--output", dest="output",
                type=argparse.FileType('w'),
                metavar="FILE",
                default=sys.stdout,
                help="output file")

    parser.add_argument("--basedir", dest="basedir",
                default=os.getcwd(),
                help="base directory")

    parser.add_argument("--input-encoding", dest="input_encoding",
                default=DEFAULT_ENCODING,
                help="encoding of input source")

    parser.add_argument("--output-encoding", dest="output_encoding",
                default=DEFAULT_ENCODING,
                help="encoding of output distination")

    group = parser.add_mutually_exclusive_group()

    group.add_argument("-v", "--verbose", dest="verbose",
                default=False, action="store_true",
                help="set logging to verbose mode")

    group.add_argument("-q", "--quiet", dest="quiet",
                default=False, action="store_true",
                help="set logging to quiet mode")

    return parser


def parse_arguments(*args, **kwargs):
    """ Parse command line arguments after setting basic options.
    If successfully parsed, set logging verbosity.
    """
    parser = argparse.ArgumentParser(parents=[base_parser(), ])

    parser.add_argument('files', nargs='*',
                type=argparse.FileType('r'),
                metavar="FILE")

    try:
        args = parser.parse_args()
    except IOError:
        # XXX: how to catch exception object on both Py2 and Py3 ?
        parser.error("File not found.")

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif not args.quiet:
        logging.basicConfig(level=logging.INFO)

    return args


def climain(func):
    """ Annotation for main function to parse basic command line arguments.

    ::

        @climain
        def main():
            # your main function goes here

    ``main()`` function can accept option values. The sequence is on your own.

    ::

        @climain
        def main(files, input_encoding, output, output_encoding):
            # your main function goes here

    """

    @wraps(func)
    def wrapper():
        # pass only arguments defined in function.
        spec = inspect.getargspec(func)
        cliargs = parse_arguments()
        args, varargs, keywords, defaults = spec
        kwargs = vars(cliargs)
        params = {}
        for k in args:
            params[k] = kwargs[k]
        return func(**params)

    return wrapper


def cliconfig(fp, env=None):
    """ Load configuration data.

    :param fp: opened file pointer of configuration
    :type fp: FileType
    :rtype: dict
    """
    if fp is None:
        raise SystemExit('No configuration file is given.')
    loader = ConfigLoader(fp)
    cfg = loader.load(env)
    if not cfg:
        logging.warn('Configuration may be empty.')
    return cfg


if __name__ == '__main__':
    boilerplate = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Description is here.
"""

import logging

from clitool.cli import climain


@climain
def main(basedir, files, output):
    logging.debug("Base directory  : " + basedir)
    print("Output          : " + output.name)
    if files:
        logging.debug("Input file count: %d", len(files))

if __name__ == '__main__':
    main()

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
'''.strip()
    print(boilerplate)

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
