#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Configuration loader to support multi file types.
Available file types are:

* ini/cfg
* json
* yaml (if "pyyaml_" is installed)

.. _pyyaml: http://pypi.python.org/pypi/PyYAML
"""

import json
import logging
import os

from six.moves import configparser

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
    """ Multi file type support config loader.

    :param fp: file pointer to load
    :param filetype: file type either of 'ini|cfg', 'json', or 'yml|yaml'.
    :type filetype: string
    """

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
        self.config = None

    def _load(self):
        if self.config is not None:
            return
        self.config = {}
        extension = self.filetype
        # XXX: separate each logic using dispatcher dict.
        if extension == ".json":
            self.config = json.load(self.fp)
        elif extension == ".py":
            # XXX: evaluate python script
            pass
        elif extension == ".ini" or extension == ".cfg":
            parser = configparser.SafeConfigParser()
            parser.readfp(self.fp)
            for s in parser.sections():
                self.config[s] = dict(parser.items(s))
        elif extension == ".yml" or extension == ".yaml":
            if YAML_ENABLED:
                self.config = yaml.load(self.fp)
            logging.error("PyYAML is not installed.")
        else:
            logging.warn('Unknown file type extension: %s', extension)

    def load(self, env=None):
        """ Load a section values of given environment.

        :param env: environment to load
        :type env: string
        :rtype: dict
        """
        self._load()
        e = env or \
            os.environ.get(RUNNING_MODE_ENVKEY, RUNNING_MODE_DEVELOPMENT)
        if e in self.config:
            return self.config[e]
        logging.warn("Environment '%s' was not found.", e)

    def flip(self):
        """ Provide flip view to compare how key/value pair is defined in each
        environment for administrative usage.

        :rtype: dict
        """
        self._load()
        groups = self.config.keys()
        tabular = {}
        for g in groups:
            config = self.config[g]
            for k in config:
                r = tabular.get(k, {})
                r[g] = config[k]
                tabular[k] = r
        return tabular

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
