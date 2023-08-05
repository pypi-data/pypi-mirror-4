===================================
Command Line Script Support Utility
===================================

* One line argument parsing function and decorator
* CSV reader/writer unicode support for Python 2.x (example impl. in official document)
* Stream utility with some logging
* Simple configuration loader
* Apache accesslog parser

Requirements
============

* Python 2.7 or 3.3

Python 2.4, 2.5, 2.6 are not supported.

Install
=======

Use ``pip`` via PyPI.

::

    pip install clitool

Bootstrap
=========

At first, create your script file using module script, ``clitool.cli``.

::

    $ python -m clitool.cli > your-script.py
    $ chmod +x your-script.py

This file can parse  basic command line options and arguments.

::

    $ ./your-script.py --help
    usage: your-script.py [-h] [-c FILE] [-o FILE] [--basedir BASEDIR]
                          [--input-encoding INPUT_ENCODING]
                          [--output-encoding OUTPUT_ENCODING] [-v | -q]
                          [FILE [FILE ...]]

    positional arguments:
      FILE

    optional arguments:
      -h, --help            show this help message and exit
      -c FILE, --config FILE
                            configuration file
      -o FILE, --output FILE
                            output file
      --basedir BASEDIR     base directory
      --input-encoding INPUT_ENCODING
                            encoding of input source
      --output-encoding OUTPUT_ENCODING
                            encoding of output distination
      -v, --verbose         set logging to verbose mode
      -q, --quiet           set logging to quiet mode

Edit this script on your own :D

Examples
========

Example scripts exist in git repository.

* csv2db.py: read csv data and import database via 'SQLAlchemy'.
* csv2json.py: read csv data and dump them by JSON format.
* csv2kml.py: read csv data and dump them by KML format via 'simplekml'.
* logfile.py: parse Apache access log and create report.
* logparams.py: parse Apache access log and analyze query parameters.

