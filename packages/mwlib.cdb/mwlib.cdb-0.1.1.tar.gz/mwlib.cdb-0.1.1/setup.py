#! /usr/bin/env python

# Copyright (c) PediaPress GmbH
# See README.txt for additional licensing information.

import os
from setuptools import setup

install_requires = ["mwlib>=0.12.13"]


def get_version():
    d = {}
    execfile("mwlib/cdb/__init__.py", d, d)
    return str(d["version"])


def main():
    if os.path.exists('Makefile'):
        # this is a git checkout
        print 'Running make'
        os.system('make')

    setup(
        name="mwlib.cdb",
        version=get_version(),
        entry_points={'console_scripts': ['mw-buildcdb = mwlib.cdb.apps:buildcdb']},
        install_requires=install_requires,
        packages=["mwlib", "mwlib.cdb"],
        namespace_packages=['mwlib'],
        zip_safe=False,
        include_package_data=True,
        url="http://github.com/doozan/",
        description="cdb tools for mwlib",
        long_description=open("README.rst").read(),
        license="BSD License",
        maintainer="Jeff Doozan",
        maintainer_email="mwlib@doozan.com")


if __name__ == '__main__':
    main()
