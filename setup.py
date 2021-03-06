#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2013-2018 Oliver Breitwieser
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

from setuptools import setup

import os
import os.path as osp


exec(
    compile(
        open(
            osp.join(osp.dirname(osp.abspath(__file__)), "pydemx", "version.py"), "rb"
        ).read(),
        osp.join(osp.dirname(osp.abspath(__file__)), "pydemx", "version.py"),
        "exec",
    )
)


setup(
    name="PyDeMX",
    version=".".join(map(str, __version__)),
    # install_requires=["docopt>=0.5", "PyYAML>=3.10"],
    install_requires=["docopt>=0.5"],
    packages=["pydemx"],
    url="http://github.com/obreitwi/pydemx",
    license="MIT",
    entry_points={"console_scripts": ["pydemx = pydemx.main:main_loop"]},
    package_data={"pydemx": ["cfg.pydemx.default"],},
    zip_safe=True,
)
