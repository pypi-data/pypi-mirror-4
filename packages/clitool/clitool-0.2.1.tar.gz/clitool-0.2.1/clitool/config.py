#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Configuration loader
"""

import json
import logging
import os

try:
    # 3.x name
    import configparser as configparser3
    configparser = configparser3
except ImportError:
    # 2.x name
    import ConfigParser as configparser2
    configparser = configparser2

try:
    import yaml
    YAML_ENABLED = True
except ImportError:
    YAML_ENABLED = False

from clitool import (
    RUNNING_MODE_ENVKEY,
    RUNNING_MODE_DEVELOPMENT
)


class ConfigLoader(object):

    def __init__(self, fp, filetype=None):
        self.fp = fp
        if filetype:
            if not filetype.startswith('.'):
                filetype = '.' + filetype
            self.filetype = filetype
        else:
            fname = self.fp.name
            _, extension = os.path.splitext(fname)
            logging.debug("Configfile=%s, extension=%s",
                os.path.abspath(fname), extension)
            self.filetype = extension

    def _load(self):
        extension = self.filetype
        # XXX: separate each logic using dispatcher dict.
        if extension == ".json":
            return json.load(self.fp)
        elif extension == ".py":
            # XXX: evaluate python script
            return {}
        elif extension == ".ini":
            parser = configparser.SafeConfigParser()
            parser.readfp(self.fp)
            config = {}
            for s in parser.sections():
                config[s] = dict(parser.items(s))
            return config
        elif extension == ".yml" or extension == ".yaml":
            if YAML_ENABLED:
                return yaml.load(self.fp)
            logging.error("PyYAML is not installed.")
            return {}
        else:
            logging.warn('Unknown file type extension: %s', extension)
            return {}

    def load(self, env=None):
        e = env or \
            os.environ.get(RUNNING_MODE_ENVKEY, RUNNING_MODE_DEVELOPMENT)
        config = self._load()
        if e in config:
            return config[e]
        logging.warn("Environment '%s' was not found.", e)

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
