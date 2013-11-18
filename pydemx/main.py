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


import sys
import os
import os.path as osp
import docopt

from .parser import Parser

raw_docstring = """

Usage: 
    {prms} [-v] [-r] [-e <ext>] <file_or_folder>...

Agruments:
    <file_or_folder>
        If file it will be converted; if folder, convert all `.skel` files in it.

Options:
    -r --recursive
        Recurse into subfolders of specified folders. Does NOT recurse files.

    -e --extension <ext>
        Specify a different extention for skeleton files. [default: skel]
"""


def get_updated_docstring():
    return raw_docstring.format(prog=osp.basename(sys.argv[0]))


def mainloop(argv=None):
    if argv is None:
        argv = sys.argv

    args = docopt.docopt(get_updated_docstring(), argv=argv[1:])

    ext = args["--extension"]
    recursive = args["--recursive"]

    files_and_folders = args["file_or_folder"]

    for faf in files_and_folders:
        if osp.isfile(faf):
            Parser(faf)
        elif osp.isdir(faf):
            for entry in os.listdir(faf):
                path = osp.join(faf, entry)
                valid_file = osp.isfile(path) and\
                        osp.splitext(path)[-1] == osp.extsep + ext
                valid_folder = recursive and osp.isdir(path)

                if valid_file or valid_folder:
                    files_and_folders.append(path)
