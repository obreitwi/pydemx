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

# import numpy as np
import os

# import yaml
# try:
    # from yaml import CLoader as YamlLoader, CDumper as YamlDumper
# except ImportError:
    # from yaml import YamlLoader, YamlDumper

# def load(obj):
    # "Load yaml from object."
    # return yaml.load(obj, Loader=YamlLoader)

# def write(file,  obj):
    # yaml.dump(obj, file, Dumper=YamlDumper)

def readline(file):
    """
        Reads a line from file and strips line endings.

        Returns None if EOF is reached.
    """
    line = file.readline()
    if len(line) > 0:
        # we still have something in the file (be it line endings)
        return line.strip(os.linesep)
    else:
        return None


