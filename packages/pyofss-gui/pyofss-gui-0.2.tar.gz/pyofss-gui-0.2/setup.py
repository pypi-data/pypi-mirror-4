#!/usr/bin/env python

"""
    Copyright (C) 2012  David Bolt

    This file is part of pyofss-gui.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

metadata = dict(
    name="pyofss-gui",
    version="0.2",
    license="GNU GPL",
    platforms="POSIX",
    author="David Bolt (daibo)",
    author_email="djb@curvedthoughts.com",
    url="http://curvedthoughts.com/pyofss",
    download_url="http://pypi.python.org/pypi/pyofss-gui",
    description=("Graphical user interface for pyofss"),
    keywords=["photonic", "simulation", "fiber", "fibre", "optical"],
    packages=["pyofss_gui"],
    long_description=open("README.rst").read(),
    scripts=["pyofss"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Physics"]
)

extra_metadata = dict(
    install_requires=["pyofss>=0.9"],
    include_package_data=True
)

if __name__ == "__main__":

    try:
        from setuptools import setup
        metadata.update(extra_metadata)
    except ImportError:
        from distutils.core import setup

    # No matter which imports were used, use the same setup call:
    setup(**metadata)
