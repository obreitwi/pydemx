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

__all__ = ["Parser"]

import re
import io
import copy
import socket
from pprint import pformat as pf
import os
import os.path as osp
import logging
import functools as ft
import itertools as it

from .logcfg import log
from . import misc as m
from .replacements import make_replacement_t
from . import io


class Parser(object):

    config_keys = [
            "replacement_prefix",
            "replacement_suffix",
            "default_seperator",
            "key_designator",
            "multi_key_seperator"
        ]

    def __init__(self, cfg, tokenizer):
        text_blocks = tokenizer.text_blocks
        repl_blocks = tokenizer.repl_blocks
        code_blocks = tokenizer.code_blocks

        log.debug("Parsing file.")
        self.cfg = {k:cfg[k] for k in self.config_keys}
        self.replacement_t = make_replacement_t()

        self._create_utils()

        self.text_blocks = text_blocks

        # scrape all textblocks for defined replacements
        # scrape the contents of all replacement blcoks as well
        for tb in text_blocks:
            self.read_replacements(tb.lines)

        # define replacements from replacement blocks
        known_repl_block_names = set()
        for rb in repl_blocks:
            self.read_replacements(rb.lines)
            match = self.matcher_repl_block_title.match(rb.title).groupdict()

            log.debug("Match object for replacement block: {}".format(pf(match)))

            # if we haven't seen a replacement block yet, it should be inserted
            # into regular text where first defined
            if match["name"] not in known_repl_block_names:
                known_repl_block_names.add(match["name"])
                text_repl = self.replacement_t.format.format(name=match["name"])
                if log.getEffectiveLevel() <= logging.DEBUG:
                    log.debug("Text inserted for replacement block: {}".format(
                        pf(text_repl)))
                if rb.index > 0:
                    self.text_blocks[rb.index - 1].lines.append(text_repl)
                else:
                    self.text_blocks[0].lines.insert(0, text_repl)

            repl = self.replacement_t(match["name"])
            combined_lines = os.linesep.join(rb.lines)
            if match["key"] is not None:
                # see if we have more than one key fo which we have the same
                # replacement
                mks = self.cfg["multi_key_seperator"]
                if mks is not None and mks in match["key"]:
                    keys = match["key"].split(mks)
                else:
                    keys = [match["key"]]

                log.debug("Keys for {}: {}".format(match["name"], pf(keys)))

                for k in keys:
                    repl[k] = combined_lines
            else:
                repl.default = combined_lines

            if log.getEffectiveLevel() <= logging.DEBUG:
                log.debug(pf(repl))

        # execute the code from code blocks
        # include a dummy cfg dict to be compatible with the first cfg block

        # allow the code lines to pass data along
        context = {"R": self.replacement_t, "cfg":copy.deepcopy(cfg)}
        m.execute_code(code_blocks[0].lines, context)
        for cb in code_blocks[1:]:
            m.execute_code(cb.lines, context)


    def read_replacements(self, lines):
        for line in lines:
            log.debug("Reading replacements for line: {}".format(line))
            for match in self.replacement_t.matcher.finditer(line):
                gd = match.groupdict()
                log.debug("Read replacment {}".format(gd))
                self.replacement_t(**gd)

    def _create_utils(self):
        """
            Creates the appropriate matchers from the configuration as well as
            formatter strings.
        """
        repl_block_title_line = r"^\s*((?P<name>\S+?)"\
            "(\s*{designator}\s*(?P<key>(\S|{mks})+))?)?$".format(
                designator=self.cfg["key_designator"],
                mks=self.cfg["multi_key_seperator"])

        log.debug("Replacement block title matcher: {}".format(
            repl_block_title_line))

        self.matcher_repl_block_title = re.compile(repl_block_title_line)

        self.replacement_t.create_utils(
                prefix=self.cfg["replacement_prefix"],
                suffix=self.cfg["replacement_suffix"],
                seperator=self.cfg["default_seperator"])

