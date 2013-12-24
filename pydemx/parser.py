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
from pprint import pformat as pf
import os
import os.path as osp
import logging

from .logcfg import log
from . import misc as m
from .replacements import Replacement


class Parser(object):
    """
        Parses a skeleton file and writes the result to the specified location.
    """

    default_configuration = {
            # If not specified will be the original file filename without
            # ending.
            "filename" : None,
            # If not specified will be the current folder
            "folder" : ".",
            "key_func" : socket.gethostname,
            "variable_pre" : r"{{",
            "variable_post" : r"}}",
            "default_seperator" : ":",
            "key_designator" : "@", # make sure this is no python.re special
                                    # character
        }

    def __init__(self, skeleton_file):
        """
            skeleton_file: The file to be read.

            out_file: Alternate output file that is instead of the location
                      specified in the skeleton file.
        """
        self.name = skeleton_file.name if hasattr(skeleton_file, "name")\
                    else "file"
        self.log("Reading file..")
        self.skeleton = skeleton_file
        self._setup_replacements()


    def log(self, msg, level="info"):
        for line in msg.split("\n"):
            getattr(log, level)("{}: {}".format(self.name, line))

    def write(self, filename=None):
        self._write_output(filename=filename)
        self._check_unused_replacements()

    def parse(self):
        self.skeleton.seek(0)
        self._extract_magic_line()
        self._read_configuration()
        self._create_utils()
        self._read_replacements()
        self._prepare_replacements()
        if log.getEffectiveLevel() <= logging.DEBUG:
            self.log(pf(self.replacement_t.instances), level="debug")

    def _read_replacements(self):
        """
            Read all special blocks.
        """
        self.regular_text = StringIO.StringIO()
        for line in iter(self.skeleton.readline, ''):
            if not self.is_magic_line(line):
                if log.getEffectiveLevel() <= logging.DEBUG:
                    self.log("Non-special line: {}".format(
                        line.strip(os.linesep)), level="debug")
                for match in self.matcher_replacement.finditer(line):
                    gd = match.groupdict()
                    self.replacement_t(**gd)

                self.regular_text.write(line)
                continue

            # check if there was replacement designation
            match_info = self.matcher_magic_line.match(line).groupdict()

            is_meta_block = match_info["name"] is None

            new_block = self._read_block(delete_prefix=is_meta_block)

            if not is_meta_block:
                # there is a regular replacement here, dont delete the prefix
                if match_info["key"] is None:
                    # create a new replacement with the corresponding default
                    self.replacement_t(match_info["name"], new_block)

                    # and insert a placeholder indicating its position in the
                    # regular text
                    self.regular_text.write(self.format_replacement.format(
                        name=match_info["name"]))
                else:
                    self.replacement_t(match_info["name"])[match_info["key"]] =\
                            new_block

            else:
                # the block is python code to be executed
                local_context = {"R": self.replacement_t}
                compiled = compile(new_block, "<string>", "exec")
                exec(compiled, {}, local_context)


    def _read_configuration(self):
        """
            Interprets the next magic block read to be the configuration block.

            Regularly, this is the first block.
        """
        # for line in iter(self.skeleton.readline, ''):
            # if self.is_magic_line(line):
                # break

        config_block = self._read_block(delete_prefix=True)
        self.config = copy.deepcopy(self.default_configuration)
        config_context = {
                "cfg" : self.config,
                "R" : self.replacement_t,
            }

        self.config["filename"] = osp.splitext(self.skeleton.name)[0]

        config_block_code = compile(config_block, "<string>", "exec")
        exec(config_block_code, {}, config_context)

        if log.getEffectiveLevel() <= logging.DEBUG:
            self.log(pf(self.config), level="debug")


    def _create_utils(self):
        """
            Creates the appropriate matchers from the configuration as well as
            formatter strings.
        """
        magic_line = r"^.{{{len_magic_line:d}}}\s*((?P<name>\S+?)"\
            "(\s*{designator}\s*(?P<key>\S+))?)?$".format(
                len_magic_line=len(self.raw_magic_line),
                designator=self.config["key_designator"])
        self.log("Magic line: {}".format(magic_line), level="debug")
        self.matcher_magic_line = re.compile(magic_line)

        replacement_line =\
                r"{pre}(?P<name>\S+?)({sep}(?P<default>.+?))?{post}".format(
                    pre=self.config["variable_pre"],
                    post=self.config["variable_post"],
                    sep=self.config["default_seperator"])

        self.log("self.replacement_t line: {}".format(replacement_line), level="debug")
        self.matcher_replacement = re.compile(replacement_line)

        format_encode = lambda x: x.replace("{", "{{").replace("}", "}}")
        self.format_replacement = "{pre}{{name}}{post}".format(
                    pre=format_encode(self.config["variable_pre"]),
                    post=format_encode(self.config["variable_post"]))
        self.log("Format-replacement: {}".format(self.format_replacement),
                level="debug")


    def _read_block(self, delete_prefix=False):
        """
            Assumes the block starts at the current line.
        """
        self.log("Reading block starting at position: {}".format(
            self.skeleton.tell()), level="debug")
        block_cache = StringIO.StringIO()

        # since the user can omitt the last line if it is
        filepos = self.skeleton.tell()

        for line in iter(self.skeleton.readline, ''):
            if self.is_magic_line(line):
                break
            else:
                if delete_prefix and line.startswith(self.meta_prefix):
                    line = line[len(self.meta_prefix):]
                block_cache.write(line)
            filepos = self.skeleton.tell()

        if self.is_extended_magic_line(line):
            # there is a new block here, reset the filepos to before
            self.skeleton.seek(filepos)

        return block_cache.getvalue()

    def _setup_replacements(self):
        # TODO: Replace global type with specific instance
        self.replacement_t = Replacement
        self.replacement_t.clear_instances()

    def _extract_magic_line(self):
        sk = self.skeleton
        sk.seek(0)
        self.raw_magic_line = sk.readline().strip(os.linesep)

        # the second line has to contain the magic line and the prefix
        second_line = sk.readline().strip(os.linesep)

        if not self.is_magic_line(second_line):
            self.log("Second line does not start with the magic line!",
                    level="error")

        self.meta_prefix = second_line[len(self.raw_magic_line):]


    def is_magic_line(self, line):
        return line.startswith(self.raw_magic_line)


    def is_extended_magic_line(self, line):
        if not hasattr(self, "matcher_magic_line"):
            return False
        else:
            matcher = self.matcher_magic_line.match(line)
            return matcher is not None and\
                    matcher.groupdict()["name"] is not None

    def _prepare_replacements(self):
        self.replacements_done = {}

    def get_replacement_for_match(self, match):
        # if there is a default section in the match, we need to add
        # it to the 
        gd = match.groupdict()
        return self.get_replacement(gd["name"], gd["default"])

    def get_replacement(self, name, default=None):
        if name not in self.replacements_done:
            self._process_replacement(name)
        return self.replacements_done[name]

    def _process_replacement(self, name):
        self.log("Processing {}".format(name), level="debug")
        # to prevent loops when replacements reference each other
        # we insert None first (which will cause an error but not a deadlock)
        self.replacements_done[name] = None
        try:
            raw_rep = self.replacement_t(name)[self.config["key_func"]()]
        except KeyError:
            raw_rep = ""

        self.log(pf(raw_rep), level="debug")

        self.replacements_done[name] = self.matcher_replacement.sub(
                self.get_replacement_for_match, raw_rep)

    def _write_output(self, filename=None):
        """
            filename: If None, use name extracted from skeleton file.
        """
        if filename is None:
            filename = osp.join(self.config["folder"],
                    self.config["filename"])

        filename = osp.expandvars(osp.expanduser(filename))

        self.log("Writing: {}".format(filename))
        with open(filename, "w") as f:
            self.regular_text.seek(0)
            for line in iter(self.regular_text.readline, ''):
                if log.getEffectiveLevel() <= logging.DEBUG:
                    self.log("Current line: {}".format(line.strip(os.linesep)),
                            level="debug")
                    for match in self.matcher_replacement.finditer(line):
                        self.log(pf(match.groupdict()), level="debug")
                f.write(self.matcher_replacement.sub(
                    self.get_replacement_for_match, line))

    def _check_unused_replacements(self):
        if log.getEffectiveLevel() <= logging.DEBUG:
            self.log(pf(self.replacement_t.instances), level="debug")
            self.log(pf(self.replacements_done), level="debug")
        for rep in self.replacement_t.instances:
            if rep not in self.replacements_done:
                self.log("Replacment \"{}\" defined but not used.".format(rep),
                        level="warn")

