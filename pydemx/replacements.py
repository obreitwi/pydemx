#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2013-2020 Oliver Breitwieser
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pprint import pformat as pf
import logging
import re

from .logcfg import log
from .meta import Singleton

class Replacement(dict, metaclass=Singleton):
    """
        Replacement object that gets instanciated by the client to define
        replacements.
    """

    def __init__(self, name, default=None):
        self.name = name
        if default is not None:
            log.debug("{}: Setting default to {}".format(name, default))
            self.default = default
        elif  not hasattr(self, "default"):
            self.default = ""
        if getattr(self, "_initialized_once", False):
            super(Replacement, self).__init__()
            self.initialized_once= True

    def __getitem__(self, key):
        return self.get(key, self.default)

    def __repr__(self):
        return pf(super(Replacement, self).__repr__()) + " | " +\
                pf("default: {}".format(self.default))

    @classmethod
    def create_utils(cls, prefix, suffix, seperator):
        """
            Creates the appropriate matchers from the configuration as well as
            formatter strings.
        """
        replacement_line =\
                r"{pre}(?P<name>\S+?)({sep}(?P<default>.+?))?{post}".format(
                    pre=prefix, post=suffix, sep=seperator)

        log.debug("Replacement line: {}".format(
            replacement_line))
        cls.matcher = re.compile(replacement_line)

        format_encode = lambda x: x.replace("{", "{{").replace("}", "}}")
        cls.format = "{pre}{{name}}{post}".format(
                    pre=format_encode(prefix),
                    post=format_encode(suffix))
        log.debug(
            "Format-replacement: {}".format(cls.format))


def make_replacement_t(**cfg):
    """
        Generate and return a new replacement type with own registry.
    """
    return type("Replacement", (Replacement,), {"_instances" : {}})

