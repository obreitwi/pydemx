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
from pprint import pformat as pf

from .parser import Parser
from . import logcfg
log = logcfg.log

raw_docstring = """

Usage:
    {prog} [-v] [-r] [-c] [-e <ext>] <file_or_folder>...

Agruments:
    <file_or_folder>
        If argument is a filename it will be converted; if it is a foldername,
        {prog} converts all `.skel` files contained within it.

Options:
    -v --verbose
        Verbose output.

    -r --recursive
        Recurse into subfolders of specified folders. Does NOT recurse files.

    -c --current-folder
        Force output into the current folder. The resulting filename will be
        that of the original skeleton file with its extension popped. (Mostly
        used for testing purposes.)

    -e --extension <ext>
        Specify a different extention for skeleton files. [default: skel]
"""


def get_updated_docstring():
    return raw_docstring.format(prog=osp.basename(sys.argv[0]))

def parse_file(filename, args):
    current_folder = args["--current-folder"]

    with open(filename, "r") as f:
        parser = Parser(f)
        parser.config()
        parser.parse()
        kwargs ={}
        if current_folder:
            kwargs["filename"] = osp.splitext(filename)[0]
        parser.write(**kwargs)

def main_loop(argv=None):
    if argv is None:
        argv = sys.argv

    args = docopt.docopt(get_updated_docstring(), argv=argv[1:])
    if args["--verbose"]:
        logcfg.make_verbose()
        log.debug(pf(args))


    ext = args["--extension"]
    recursive = args["--recursive"]

    files_and_folders = args["<file_or_folder>"]

    for faf in files_and_folders:
        if osp.isfile(faf):
            parse_file(faf, args)
        elif osp.isdir(faf):
            for entry in os.listdir(faf):
                path = osp.join(faf, entry)

                valid_file = osp.isfile(path) and\
                        osp.splitext(path)[-1] == osp.extsep + ext
                valid_folder = recursive and osp.isdir(path)

                if valid_file or valid_folder:
                    files_and_folders.append(path)


