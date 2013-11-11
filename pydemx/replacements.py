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

class Replacement(dict):
    """
        Replacement object that gets instanciated by the client to define
        replacements.
    """

    def __init__(self, name, default=None):
        self.name = name
        self.storage = {}
        self.default = default
        super(Replacement, self).__init__()

    def __getitem__(self, key):
        return self.storage.get(key, self.default)


class ReplacementFactory(object):
    """
        Factory for replacements that keeps track of all replacements created.
    """

    _raw_product_type = Replacement

    def __init__(self):
        self._created = {}
        self._product_type = self._create_product_type()

    def _create_product_type(self):
        def new_init(_self, name, *args, **kwargs):
            self.created[name] = _self
            super(_self.__class__, _self).__init__(name, *args, **kwargs)

        dct = {
                "__init__" : new_init,
            }

        return type(self._raw_product_type.__name__ + "Tracked",
                (self._raw_product_type,), dct)

    @property
    def product_type(self):
        return self._product_type

    @property
    def created(self):
        return self._created

