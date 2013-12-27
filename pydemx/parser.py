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
from .replacements import make_replacement_t


class Parser(object):
    """
        Parses a skeleton file and writes the result to the specified location.
    """

    default_configuration = {
            # If not specified will be the original file filename without
            # ending.
            "filename" : None,
            # If not specified will be the current folder
            "folder" : None,
            # file permissions after writing to it
            "permissions" : None,
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
        log.info(self.prefix_log("Reading file.."))
        self.skeleton = skeleton_file
        self._setup_replacements()
        self.read_config = False
        self.parsed_file = False

    def prefix_log(self, msg):
        return "\n".join(("{}: {}".format(self.name, line)\
                for line in msg.split("\n")))

    def write(self, filename=None):
        """
            Write the output file.
        """
        assert self.read_config, "The skeleton file has not been parsed yet."
        self._get_key_value()
        self._write_output(filename=filename)
        self._check_unused_replacements()

    def _get_key_value(self):
        self.key_value = self.config["key_func"]()

    def config(self):
        """
            Read the configuration as it is present in the skeleton file.
        """
        self.skeleton.seek(0)
        self._extract_magic_line()
        self._read_configuration()
        self._filepos_after_config = self.skeleton.tell()
        self.read_config = True

    def parse(self):
        """
            Parse the file with the configuration present.

            The user may want to modify the configuration after it has been
            read, hence there is a separate parse function.
        """
        assert self.read_config, "The configuration has to be read prior to "\
                "parsing."
        self.skeleton.seek(self._filepos_after_config)
        self._create_utils()
        self._read_replacements()
        self._prepare_replacements()
        if log.getEffectiveLevel() <= logging.DEBUG:
            log.debug(self.prefix_log(pf(self.replacement_t.instances)))
        self.parsed_file = True

    def _read_replacements(self):
        """
            Read all special blocks.
        """
        self.regular_text = StringIO.StringIO()
        for line in iter(self.skeleton.readline, ''):
            if not self.is_magic_line(line):
                if log.getEffectiveLevel() <= logging.DEBUG:
                    log.debug(self.prefix_log("Non-special line: {}".format(
                        line.strip(os.linesep))))
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

        self._set_default_config()

        config_context = {
                "cfg" : self.config,
                "R" : self.replacement_t,
            }

        self.config["filename"] = osp.splitext(self.skeleton.name)[0]

        config_block_code = compile(config_block, "<string>", "exec")
        exec(config_block_code, {}, config_context)

        if log.getEffectiveLevel() <= logging.DEBUG:
            log.debug(self.prefix_log(pf(self.config)))

    def _set_default_config(self):
        self.config["folder"] = osp.dirname(osp.abspath(self.name))

    def _create_utils(self):
        """
            Creates the appropriate matchers from the configuration as well as
            formatter strings.
        """
        magic_line = r"^.{{{len_magic_line:d}}}\s*((?P<name>\S+?)"\
            "(\s*{designator}\s*(?P<key>\S+))?)?$".format(
                len_magic_line=len(self.raw_magic_line),
                designator=self.config["key_designator"])
        log.debug(self.prefix_log("Magic line: {}".format(magic_line)))
        self.matcher_magic_line = re.compile(magic_line)

        replacement_line =\
                r"{pre}(?P<name>\S+?)({sep}(?P<default>.+?))?{post}".format(
                    pre=self.config["variable_pre"],
                    post=self.config["variable_post"],
                    sep=self.config["default_seperator"])

        log.debug(self.prefix_log("Replacement line: {}".format(
            replacement_line)))
        self.matcher_replacement = re.compile(replacement_line)

        format_encode = lambda x: x.replace("{", "{{").replace("}", "}}")
        self.format_replacement = "{pre}{{name}}{post}".format(
                    pre=format_encode(self.config["variable_pre"]),
                    post=format_encode(self.config["variable_post"]))
        log.debug(self.prefix_log(
            "Format-replacement: {}".format(self.format_replacement)))


    def _read_block(self, delete_prefix=False):
        """
            Assumes the block starts at the current line.
        """
        log.debug(self.prefix_log(
            "Reading block starting at position: {}".format(
                self.skeleton.tell())))
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
        self.replacement_t = make_replacement_t()
        self.replacement_t.clear_instances()

    def _extract_magic_line(self):
        sk = self.skeleton
        sk.seek(0)
        self.raw_magic_line = sk.readline().strip(os.linesep)

        pos_second_line = sk.tell()
        # the second line has to contain the magic line and the prefix
        second_line = sk.readline().strip(os.linesep)

        if not self.is_magic_line(second_line)\
                or len(second_line) == len(self.raw_magic_line):
            log.warn(self.prefix_log("Second line does not define prefix!"))
            self.meta_prefix = ""
            # since we saw no prefix the second line already is part of the
            # configuration block -> rewind!
            sk.seek(pos_second_line)
        else:
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
        log.debug(self.prefix_log("Processing {}".format(name)))
        # to prevent loops when replacements reference each other
        # we insert None first (which will cause an error but not a deadlock)
        self.replacements_done[name] = None
        try:
            raw_rep = self.replacement_t(name)[self.key_value]
        except KeyError:
            raw_rep = ""

        log.debug(self.prefix_log(pf(raw_rep)))

        self.replacements_done[name] = self.matcher_replacement.sub(
                self.get_replacement_for_match, str(raw_rep))

    def _write_output(self, filename=None):
        """
            filename: If None, use name extracted from skeleton file.
        """
        if filename is None:
            filename = osp.join(self.config["folder"],
                    self.config["filename"])

        filename = osp.expandvars(osp.expanduser(filename))

        log.info(self.prefix_log("Writing: {}".format(filename)))
        with open(filename, "w") as f:
            self.regular_text.seek(0)
            for line in iter(self.regular_text.readline, ''):
                if log.getEffectiveLevel() <= logging.DEBUG:
                    log.debug(self.prefix_log(
                        "Current line: {}".format(line.strip(os.linesep))))
                    for match in self.matcher_replacement.finditer(line):
                        log.debug(self.prefix_log(pf(match.groupdict())))
                f.write(self.matcher_replacement.sub(
                    self.get_replacement_for_match, line))

        permissions = self.config["permissions"]
        if permissions is not None:
            os.chmod(filename, int(permissions))

    def _check_unused_replacements(self):
        if log.getEffectiveLevel() <= logging.DEBUG:
            log.debug(self.prefix_log(pf(self.replacement_t.instances)))
            log.debug(self.prefix_log(pf(self.replacements_done)))
        for rep in self.replacement_t.instances:
            if rep not in self.replacements_done:
                log.warn(self.prefix_log(
                    "Replacement \"{}\" defined but not used.".format(rep)))

