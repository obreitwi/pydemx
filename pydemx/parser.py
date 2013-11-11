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

__all__ = ["Parser"]

import re
import StringIO
import copy
import socket

from .logcfg import log
from . import misc as m
from .replacements import ReplacementFactory


class Parser(object):
    """
        Parses a skeleton file and writes the result to the specified location.
    """

    default_configuration = {
            # If not specified will be the original file filename without ending.
            "target_filename" : None,
            # If not specified will be the current folder
            "target_folder" : ".",
            "key_func" : socket.gethostname,
            "variable_pre" : "{{",
            "variable_post" : "}}",
            "default_seperator" : ":",
            "key_designator" : "@",
        }

    def __init__(self, skeleton_file, out_file=None):
        """
            skeleton_file: The file to be read. 

            out_file: Alternate output file that is instead of the location
                      specified in the skeleton file.
        """
        log.info("Reading {}..".format(
            skeleton_file.name if hasattr(skeleton_file, "name") else "file"))
        self.skeleton = skeleton_file
        self.templates = {}

        self.setup_replacements()

        self.parse_file()


    def parse_file(self):
        self.skeleton.seek(0)
        self.extract_magic_line()
        self.read_configuration()
        self.create_matcher()
        self.read_replacements()


    def read_replacements(self):
        """
            Read all special blocks.
        """
        for line in iter(self.skeleton.readline, ''):
            if not self.is_magic_line(line):
                continue

            new_block = self.read_block()

            match_info = self.matcher_magic_line.match(line).groupdict()

            # check if there was replacement designation
            if match_info["name"] is not None:
                if match_info["key"] is None:
                    # create a new replacement with the corresponding default
                    self.replacement_type(match_info["name"], new_block)
                else:
                    self.replacements[match_info["name"]][match_info["key"]] =\
                            new_block

            else:
                # the block is python code to be executed
                local_context = {"R": self.replacement_type}
                compiled = compile(new_block, "<string>", "exec")
                exec(compiled, {}, local_context)


    def read_configuration(self):
        """
            Interprets the next magic block read to be the configuration block.

            Regularly, this is the first block.
        """
        for line in iter(self.skeleton.readline, ''):
            if self.is_magic_line(line):
                break

        config_block = self.read_block()
        self.config = copy.deepcopy(self.default_configuration),
        config_context = {
                "config" : self.config,
                "R" : self.replacement_type,
            }

        config_block_code = compile(config_block, "<string>", "exec")
        exec(config_block_code, {}, config_context)


    def create_matcher(self):
        """
            Creates the appropriate matchers from the configuration.
        """
        magic_line = r"^.{{{len_magic_line:d}}}\s+?(P<name>\S+?)"\
            "(\s*{designator}\s*(?<key>\S+))?$".format(
                len_magic_line=len(self.raw_magic_line),
                designator=self.config["key_designator"])
        self.matcher_magic_line(re.compile(magic_line))

        self.matcher_replacement = re.compile(
                r"{pre}(?<name>\S+?)({sep}(?P<default>\S+?)){post}".format(
                    pre=self.config["variable_pre"],
                    post=self.config["variable_post"],
                    sep=self.config["default_seperator"]))


    def read_block(self):
        """
            Assumes the block starts at the current line.
        """
        log.debug("Reading block starting at position: {}".format(
            self.skeleton.tell()))
        block_cache = StringIO.StringIO()

        # since the user can omitt the last line if it is
        filepos = self.skeleton.tell()

        for line in iter(self.skeleton.readline, ''):
            if self.is_magic_line(line):
                break
            else:
                block_cache.write(line)
            filepos = self.skeleton.tell()

        if self.is_extended_magic_line(line):
            # there is a new block here, reset the filepos to before
            self.skeleton.seek(filepos)

        return block_cache.getvalue()


    def setup_replacements(self):
        self.replacement_factory = ReplacementFactory()
        self.replacement_type = self.replacement_factory.product_type
        self.replacements = self.replacement_factory.created


    def extract_magic_line(self):
        with m.save_filepos(self.skeleton) as sk:
            sk.seek(0)
            self.raw_magic_line = sk.readline().strip()



    def is_magic_line(self, line):
        return line.startswith(self.raw_magic_line)


    def is_extended_magic_line(self, line):
        return self.matcher_magic_line.match(line) is not None


    def write(self, filename=None):
        """
            filename: If None, use name extracted from skeleton file.
        """
        pass

