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

import os.path as osp
import os
import copy

from pkg_resources import resource_string

from . import misc as m
from .logcfg import log

CONFIG_FILENAME = "cfg.pydemx"
DEFAULT_SUFFIX = ".default"


def load_config_from_path(path):
    with open(path, "r") as f:
        return load_config(f.read())


def load_config(text):
    ast = compile(text, "<string>", "exec")

    cfg_locals = {}
    exec(ast, {}, cfg_locals)

    if "cfg" in cfg_locals and isinstance(cfg_locals["cfg"], dict):
        return cfg_locals["cfg"]
    else:
        log.warn("{} does not define a proper cfg-dictionary.".format(path))
        return {}


class Config(object):
    """
        Loads the default config and updates it with external config (if found)
        and the cfg section of the file in question.
    """

    def __init__(self, path, cfg_code_block):
        log.debug("Reading config.")
        cfg = copy.deepcopy(defaults)

        # update from external config
        for ext_cfg in self.find_cfgs(path):
            cfg.update(ext_cfg)

        # update from the provided config block
        # just mock an R object here because that information will be extracted
        # elsewhere
        def mock_R(*args):
            return {}

        local_context = {"cfg": {}, "R": mock_R}
        m.execute_code(cfg_code_block.lines, local_context=local_context)
        cfg.update(local_context["cfg"])

        self._cfg = cfg

    def find_cfgs(self, path):
        """
            Find all cfgs that are above the current path and return them in
            reverse order (the higher they are in the filesystem, the earlier
            they are returned).
        """
        path = osp.abspath(path)
        found_paths = []
        while osp.basename(path):
            log.debug("Checking {}".format(path))
            path_cfg = osp.join(path, CONFIG_FILENAME)

            if osp.isfile(path_cfg):
                found_paths.append(path_cfg)
            path = osp.dirname(path)

        for path_cfg in reversed(found_paths):
            yield load_config_from_path(path_cfg)

    def __getitem__(self, key):
        return self._cfg[key]

    def __setitem__(self, key, value):
        self._cfg[key] = value


defaults = load_config(resource_string(__name__, CONFIG_FILENAME + DEFAULT_SUFFIX))
