#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Command line utilities.

Basically, this module provides three features:

1. ``@climain`` decorator for main function.
2. ``cliconfig()`` function to load config file.
3. ``clistream()`` to handle command line arguments of files.

Basic script looks like::

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    from pprint import pprint

    from clitool.cli import climain, cliconfig, clistream

    def tsv(line):
        return line.split('\t')

    @climain
    def main(config, output, **kwargs):
        cfg = cliconfig(config)
        cfg.get("YOUR_CONFIG_KEY")
        data = []
        clistream(data.append, tsv, **kwargs)
        pprint(data, stream=output)

    if __name__ == '__main__':
        main()

This module is also executable to create script boilerplate. ::

    $ python -m clitool.cli -o your-script.py
    $ ./your-script.py --help
"""

import logging
import inspect
import os
import sys
import argparse
from functools import wraps

from clitool import DEFAULT_ENCODING
from clitool.config import ConfigLoader
from clitool.processor import CliHandler, Streamer


def base_parser():
    """ Create arguments parser with basic options and no help message.

    * -c, --config: load configuration file.
    * -v, --verbose: set up logging verbosity.
    * -q, --quiet: quiet logging.
    * -o, --output: output file. (default=sys.stdout)
    * --basedir: base directory. (default=os.getcwd)
    * --input-encoding: input data encoding. (default=utf-8)
    * --output-encoding: output data encoding. (default=utf-8)
    * --processes: count of processes.
    * --chunksize: a number of chunks submitted to the process pool.

    :rtype: ArgumentParser object
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

    parser.add_argument("--processes", dest="processes", type=int,
                help="number of processes")

    parser.add_argument("--chunksize", dest="chunksize", type=int,
                default=1,
                help="number of chunks submitted to the process pool")

    group = parser.add_mutually_exclusive_group()

    group.add_argument("-v", "--verbose", dest="verbose",
                default=False, action="store_true",
                help="set logging to verbose mode")

    group.add_argument("-q", "--quiet", dest="quiet",
                default=False, action="store_true",
                help="set logging to quiet mode")

    return parser


def parse_arguments(**kwargs):
    """ Parse command line arguments after setting basic options.
    If successfully parsed, set logging verbosity.

    Examples ::

    cliargs = parse_arguments(files=dict(nargs='*'))
    cliargs = parse_arguments(files=dict(nargs='1'))
    cliargs = parse_arguments(mode=dict(flags=('-m', '--mode')))

    :param kwargs: keywords arguments to pass `add_argument` method.
    :rtype: NameSpace object
    """
    parser = argparse.ArgumentParser(parents=[base_parser(), ])

    for name in kwargs:
        opts = kwargs[name]
        if 'flags' in opts:
            opts['dest'] = name
            name_or_flags = opts['flags']
            del opts['flags']
        else:
            name_or_flags = name
        if name == 'files':
            opts['type'] = argparse.FileType('r')
            opts['metavar'] = "FILE"
        parser.add_argument(name_or_flags, **opts)

    try:
        args = parser.parse_args()
    except IOError:
        e = sys.exc_info()[1]
        parser.error("File not found: %s" % (e, ))

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        if args.processes:
            import multiprocessing.util
            multiprocessing.util.log_to_stderr(logging.DEBUG)
    elif not args.quiet:
        logging.basicConfig(level=logging.INFO)

    return args


def climain(func):

    @wraps(func)
    def wrapper():
        spec = inspect.getargspec(func)
        args, varargs, keywords, defaults = spec
        cliargs = parse_arguments(files=dict(nargs='*'))
        kwargs = vars(cliargs)
        if keywords:
            return func(**kwargs)
        # if keywords is not defined, choose explicitly defined ones.
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


def clistream(reporter, *args, **kwargs):
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

    Handler = kwargs.get('Handler', CliHandler)
    s = Streamer(reporter, processes=processes, *args)
    handler = Handler(s)

    return handler.handle(files, encoding, chunksize)


if __name__ == '__main__':
    args = parse_arguments()
    boilerplate = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Description is here.
"""

import logging

from clitool.cli import climain


@climain
def main(basedir, files, output, **kwargs):
    logging.debug("Base directory  : " + basedir)
    print("Output          : " + output.name)
    if files:
        logging.debug("Input file count: %d", len(files))

if __name__ == '__main__':
    main()

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
'''.strip()
    args.output.write(boilerplate)
    if not args.output.isatty():
        os.chmod(args.output.name, 0o775)

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
