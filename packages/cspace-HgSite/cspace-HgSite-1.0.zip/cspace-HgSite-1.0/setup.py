#!/usr/bin/env python
"""\
Installation script for HgSite
Copyright (C) 2012 Remy Blank
"""
# This file is part of HgSite.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, version 3. A copy of the license is provided
# in the file COPYING.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.

from os.path import dirname, join
from setuptools import setup, find_packages
import sys

if __name__ == '__main__':
    execfile(join(dirname(__file__), 'cspace', 'hgsite', 'meta.py'))

    if sys.version_info < min_python_version:
        mpv = '.'.join(['%d'] * len(min_python_version)) % min_python_version
        sys.stderr.write("%s requires Python %s or later\n" % (name, mpv))
        sys.exit(1)

    setup(
        name = name,
        version = version,
        author = author,
        author_email = author_email,
        license = license,
        url = url,
        download_url = download_url,
        description = description,
        long_description = long_description,
        keywords = keywords,
        platforms = platforms,
        classifiers = classifiers,

        namespace_packages = ['cspace'],
        packages = find_packages('.'),
        include_package_data = True,
        zip_safe = True,
        use_2to3 = True,

        install_requires = [
            'setuptools>=0.6',
        ],
        extras_require = {
            'Genshi': ['Genshi>=0.6'],
            'Pygments': ['Pygments>=1.5'],
#            'reST': ['docutils>=0.9.1'],
        },
    )
