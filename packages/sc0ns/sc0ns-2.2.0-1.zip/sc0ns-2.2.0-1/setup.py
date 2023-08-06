#! /usr/bin/env python

from setuptools import setup, find_packages


setup(name="sc0ns",
      description="scons, which can be installed with easy_install/pip",
      version="2.2.0",
      packages=find_packages(),
      zip_safe=False,
      entry_points={
        "console_scripts": ["scons=SCons.Script:main"]},
      maintainer="Ralf Schmitt",
      maintainer_email="ralf@systemexit.de")
