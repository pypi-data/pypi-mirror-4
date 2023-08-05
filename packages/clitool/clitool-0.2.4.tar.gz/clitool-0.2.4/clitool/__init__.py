# -*- coding: utf-8 -*-

"""
Command Line Script Support Utility
===================================

* One line argument parsing function
* Simple stream utility with some logging
* CSV reader/writer unicode support (example impl. in official document)
* Apache accesslog parser

"""

__title__ = 'clitool'
__version__ = '0.2.4'
__author__ = 'KITAZAKI Shigeru'

# Constant values.

DEFAULT_ENCODING = 'utf-8'

RUNNING_MODE_ENVKEY = 'PYTHON_CLITOOL_ENV'
RUNNING_MODE_DEVELOPMENT = 'development'
RUNNING_MODE_STAGING = 'staging'
RUNNING_MODE_PRODUCTION = 'production'

PROCESSING_REPORTING_INTERVAL = 10000
PROCESSING_SUCCESS = 'success'
PROCESSING_SKIPPED = 'skipped'
PROCESSING_ERROR = 'error'
PROCESSING_TOTAL = 'total'
PROCESSING_TIME = 'time'

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
