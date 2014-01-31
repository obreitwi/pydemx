#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2013-2014 Oliver Breitwieser
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
import logging
from pprint import pformat as pf

from .config import Config
from .tokenizer import Tokenizer
from .parser import Parser
from .generator import Generator
from . import logcfg
from . import logcfg
from .logcfg import log

raw_docstring = """

Usage:
    {prog} [options] <file_or_folder>...

Agruments:
    <file_or_folder>
        If argument is a filename it will be converted; if it is a foldername,
        {prog} converts all `.pydemx` files contained within it.

Options:
    -r --recursive
        Recurse into subfolders of specified folders. Does NOT recurse files.

    -c --current-folder
        Force output into the current folder. The resulting filename will be
        that of the original file with its extension popped. (Mostly used for
        testing purposes.)

    -k --key-value <key>
        Overwrite the key-value returned by the key-function.

    -e --extension <ext>
        Specify a different extention for input files. [default: .pydemx]

    -v --verbose
        Verbose (debug) output.

"""

from .version import __version__


def get_updated_docstring():
    return raw_docstring.format(prog=osp.basename(sys.argv[0]))

def old_parse_file(filename, args):
    current_folder = args["--current-folder"]

    with open(filename, "r") as f:
        parser = Parser(f)
        parser.config()
        parser.parse()
        key_value = args["--key-value"]
        if key_value is not None:
            log.info("Setting key-value to: {}".format(key_value))
            parser.config["key_func"] = lambda:key_value
        kwargs ={}
        if current_folder:
            kwargs["filename"] = osp.splitext(filename)[0]
        parser.write(**kwargs)

def parse_file(filename, args):
    fileformatter = logging.Formatter("%(asctime)s {}: "
        "%(message)s".format(filename), datefmt="%y-%m-%d %H:%M:%S")
    log.handlers[0].setFormatter(fileformatter)

    with open(filename, "r") as f:
        tokenizer = Tokenizer(f)

    cfg = Config(filename, tokenizer.code_blocks[0])
    if cfg["folder"] is None or args["--current-folder"]:
        cfg["folder"] = osp.dirname(osp.abspath(filename))

    if cfg["filename"] is None:
        cfg["filename"] = osp.splitext(filename)[0]

    key_value = args["--key-value"] 
    if key_value is not None:
        log.info("Setting key-value to: {}".format(key_value))
        parser.config["key_func"] = lambda:key_value

    parser = Parser(cfg,
            tokenizer.text_blocks,
            tokenizer.repl_blocks,
            tokenizer.code_blocks)

    generator = Generator(cfg, parser.text_blocks, parser.replacement_t)
    generator.write()

    log.handlers[0].setFormatter(logcfg.formatter_in_use)


def main_loop(argv=None):
    if argv is None:
        argv = sys.argv

    args = docopt.docopt(get_updated_docstring(), argv=argv[1:],
            version=".".join(map(str, __version__)))
    if args["--verbose"]:
        logcfg.make_verbose()
        log.debug(pf(args))


    ext = args["--extension"]
    recursive = args["--recursive"]

    files_and_folders = []
    files_and_folders.extend(args["<file_or_folder>"])

    for faf in files_and_folders:
        if osp.isfile(faf):
            parse_file(faf, args)
        elif osp.isdir(faf):
            for entry in os.listdir(faf):
                path = osp.join(faf, entry)

                valid_file = osp.isfile(path) and\
                        osp.splitext(path)[-1] == ext
                valid_folder = recursive and osp.isdir(path)

                if valid_file or valid_folder:
                    files_and_folders.append(path)


