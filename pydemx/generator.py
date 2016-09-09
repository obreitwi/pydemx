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

import os
import os.path as osp
import sys

from .logcfg import log

class Generator(object):

    config_keys = [
            "filename",
            "folder",
            "permissions",
            "key_func",
        ]

    def __init__(self, cfg, parser):
        log.debug("Generating.")
        self.cfg = {k: cfg[k] for k in self.config_keys}
        self.replacement_t = parser.replacement_t
        self.text_blocks = parser.text_blocks

        self.key_value = self.cfg["key_func"]()

        # stack to keep track of which replacements are currently being
        # processed (used to detect circular dependencies)
        self.processing = set()
        self.processed = {}

    def get_replacement(self, match):
        name = match.groupdict()["name"]
        retval = None

        if name in self.processed:
            retval = self.processed[name]

        elif name in self.processing:
            log.error("Replacement {}: Circular dependency detected!".format(
                name))
            retval = ""

        else:
            self.processing.add(name)

            retval = self.processed[name] = self.process_text(
                    self.replacement_t(name)[self.key_value])

            self.processing.remove(name)

        return retval

    def process_text(self, text):
        return self.replacement_t.matcher.sub(
                    self.get_replacement, str(text))

    def write(self):
        """
            Write the generated text to the file specified by the cfg.
        """
        if self.cfg["filename"] is not None:
            filename = osp.expanduser(osp.expandvars(
                osp.join(self.cfg["folder"], self.cfg["filename"])))
            log.info("Writing to output file {}".format(filename))
        else:
            filename = None
            log.info("Writing to stdout.")

        if filename is not None:
            try:
                os.makedirs(osp.dirname(filename))
            except OSError:
                pass
            f = open(filename, "w")
        else:
            f = sys.stdout

        for tb in self.text_blocks:
            f.write(self.process_text(os.linesep.join(tb.lines)+os.linesep))

        if filename is not None:
            f.close()

        if self.cfg["permissions"] is not None and filename is not None:
            log.debug("Changing file permissions to {:o}".format(
                self.cfg["permissions"]))
            os.chmod(filename, self.cfg["permissions"])

