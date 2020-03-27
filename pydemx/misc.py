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

import logging
import os
import os.path as osp
from pprint import pformat as pf
from contextlib import contextmanager

from .logcfg import log

@contextmanager
def save_filepos(fileobject):
    """
        Saves and resets the current file position on the passed file object.
    """
    filepos = fileobject.tell()
    yield fileobject
    fileobject.seek(filepos)

def ensure_folder_exists(path):
    try:
        os.makedirs(path)
    except OSError:
        pass

def setifnone(dct, key, value):
    if dct.get(key, None) is None:
        dct[key] = value

def execute_code(lines, local_context=None):
    if local_context is None:
        local_context = {}
    # if log.getEffectiveLevel() <= logging.DEBUG:
        # log.debug("Supplied lines:" + os.linesep + "{}".format(pf(lines)))
    combined_lines = os.linesep.join(lines) + os.linesep
    if log.getEffectiveLevel() <= logging.DEBUG:
        log.debug("Compiling:"+os.linesep+combined_lines)
        log.debug("Context: {}".format(pf(local_context)))

    compiled = compile(combined_lines, "<string>", "exec")
    if log.getEffectiveLevel() <= logging.DEBUG:
        log.debug("Type: {}".format(type(compiled)))
    exec(compiled, {}, local_context)

