#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2013-2018 Oliver Breitwieser
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

import logging

from .logcfg import log

class Singleton(type):
    _instances = {}

    def __call__(cls, name, *args, **kwargs):
        log.debug("Getting replacement {}".format(name))
        if name in cls.instances:
            instance = cls._instances[name]
            instance.__init__(name, *args, **kwargs)
        else:
            instance = super(Singleton, cls).__call__(name, *args, **kwargs)
            cls.add_instance(name, instance)
        return instance

    @property
    def instances(cls):
        return cls._instances

    def add_instance(cls, name, instance):
        cls._instances[name] = instance

    def clear_instances(cls):
        cls._instances = {}


