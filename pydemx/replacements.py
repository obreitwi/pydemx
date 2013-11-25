#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2013 Oliver Breitwieser
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

from .logcfg import log

class Replacement(dict):
    """
        Replacement object that gets instanciated by the client to define
        replacements.
    """

    def __init__(self, name, default=None):
        if log.getEffectiveLevel() <= logging.DEBUG:
            log.debug("Creating replacement {}.".format(name))

        self.name = name
        self.storage = {}
        self.default = default
        super(Replacement, self).__init__()

    def __getitem__(self, key):
        return self.storage.get(key, self.default)

    def __repr__(self):
        return pf(super(Replacement, self).__repr__()) + " | " +\
                pf("default: {}".format(self.default))


class ReplacementFactory(object):
    """
        Factory for replacements that keeps track of all replacements created.
    """

    _raw_product_type = Replacement

    def __init__(self):
        self._created = {}
        self._product_type = self._create_product_type()

    def _create_product_type(self):
        # yay for creative names
        def new_new(cls, name, *args, **kwargs):
            if name in self.created:
                return self.created[name]
            else:
                instance = super(self._raw_product_type, cls).__new__(cls, name,
                        *args, **kwargs)
                self.created[name] = instance
            return instance

        dct = {
                "__new__" : new_new,
            }

        return type(self._raw_product_type.__name__ + "Tracked",
                (self._raw_product_type,), dct)

    @property
    def product_type(self):
        return self._product_type

    @property
    def created(self):
        return self._created

