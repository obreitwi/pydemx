
from setuptools import setup

import os
import os.path as osp

execfile(osp.join(osp.dirname(osp.abspath(__file__)), "pydemx", "version.py"))

setup(
        name="PyDeMX",
        version=".".join(map(str, __version__)),
        install_requires=["docopt>=0.5", "PyYAML>=3.10"],
        packages=["pydemx"],
        url="http://github.com/obreitwi/pydemx",
        license="MIT",
        entry_points = {
            "console_scripts" : [
                    "pydemx = pydemx.main:main_loop"
                ]
            },
        zip_safe=True,
    )


