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

import functools as ft
import logging

from .logcfg import log
from . import io

class Block(object):
    __slots__ = ["lines"]

    def __init__(self):
        self.lines = []

class SpecialBlock(Block):
    pass

class CodeBlock(SpecialBlock):
    pass

class TextBlock(Block):
    pass

class ReplacementBlock(SpecialBlock):
    __slots__ = ["title", "index"]

    def __init__(self, title, index):
        super(ReplacementBlock, self).__init__()
        self.title = title
        self.index = index


class Tokenizer(object):
    """
        Tokenizes the input file into blocks. 
    """
    def __init__(self, file):
        log.debug("Tokenizing file.")
        file.seek(0)
        self._extract_magic_line(file)

        self.repl_blocks = []
        self.code_blocks = []
        self.text_blocks = []

        # the first block per definition is the configuration block, which is a
        # CodeBlock
        current_block = CodeBlock()
        # the current index tracks where in terms of textblocks
        # replacementblocks are defined
        current_index = 0

        # we alread read two lines
        # plus we count lines starting at 1
        line_offset = 2 + 1
        for ln, line in enumerate(iter(ft.partial(io.readline, file), None)):

            if self.is_magic_line(line):
                # we will for sure have a new block, so file the current one
                if log.getEffectiveLevel() <= logging.DEBUG:
                    log.debug("{} finished at line number {}.".format(
                        current_block.__class__.__name__, ln+line_offset))
                current_index = self.file_new_block(
                        current_block, current_index)

                # see what kind of transition we need to make
                if self.is_extended_magic_line(line):
                    # extended magic lines always indicate a new replacement
                    # block
                    current_block = ReplacementBlock(
                            title=line[len(self.magic_line):],
                            index=current_index)

                elif isinstance(current_block, TextBlock):
                    # if we are currently in a TextBlock a regular magic line
                    # defines the start of a CodeBlock
                    current_block = CodeBlock()

                else:
                    # if we are currently in a Code or ReplacementBlock, it will
                    # be ended by a magic line
                    current_block = TextBlock()

            elif isinstance(current_block, CodeBlock)\
                    and line.startswith(self.code_prefix):
                # clear the prefix
                current_block.lines.append(line[len(self.code_prefix):])

            else:
                current_block.lines.append(line)

        # finally, file the last block
        self.file_new_block(current_block, current_index)

    def file_new_block(self, block, current_text_index):
        if block is None:
            return current_text_index

        if isinstance(block, TextBlock):
            self.text_blocks.append(block)

            # we filed a new TextBlock instance, hence we need to increase the
            # counter
            current_text_index += 1

        elif isinstance(block, CodeBlock):
            self.code_blocks.append(block)

        elif isinstance(block, ReplacementBlock):
            self.repl_blocks.append(block)

        else:
            log.error("Invalid blocktype encountered, not saved!")

        return current_text_index


    def is_magic_line(self, line):
        return line.startswith(self.magic_line)

    def is_extended_magic_line(self, line):
        return len(line) > len(self.magic_line)

    def _extract_magic_line(self, file):
        self.magic_line = io.readline(file)

        pos_second_line = file.tell()
        # the second line has to contain the magic line and the prefix
        second_line = io.readline(file)

        if not self.is_magic_line(second_line)\
                or len(second_line) == len(self.magic_line):
            log.warn("Second line does not define prefix!")
            self.code_prefix = ""
            # since we saw no prefix the second line already is part of the
            # configuration block -> rewind!
            file.seek(pos_second_line)
        else:
            self.code_prefix = second_line[len(self.magic_line):]

