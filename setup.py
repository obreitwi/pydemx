
from setuptools import setup

setup(
        name="PyDeMX",
        version="0.0.1",
        install_requires=["docopt>=0.5"],
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


