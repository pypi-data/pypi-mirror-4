"""\
Project metadata
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

import time as _time


project             = 'HgSite'
name                = 'cspace-%s' % (project,)
version             = '1.0'
devel               = version.endswith('dev')
date                = '2012-11-15' if not devel else _time.strftime('%Y-%m-%d')
author              = "Remy Blank"
author_email        = 'software@c-space.org'
copyright           = 'Copyright (C) %s %s' % (date[0:4], author)
license             = 'GPLv3'
license_url         = 'http://www.gnu.org/licenses/gpl-3.0.html'
repository_url      = 'http://rc.c-space.org/hg/%s' % project
url                 = repository_url
download_url        = 'http://c-space.org/download/%s/' % project
min_python_version  = (2, 6)
description         = "Serve a web site straight out of a Mercurial repository"
long_description    = """\
%(project)s is a Mercurial extension that allows serving a dynamic, read-only
website using a Mercurial repository as the backend storage. Pages are served
by `hgweb`, the same component that serves the Mercurial repository, and no
additional configuration is necessary in the web server.

For more information, see the project site at:

  %(url)s
""" % globals()
keywords            = [
    "mercurial", "extension", "version control", "web site", "documentation",
]
platforms           = ["OS Independent"]
classifiers         = [
#    "Development Status :: 3 - Alpha",
    "Development Status :: 4 - Beta",
#    "Development Status :: 5 - Production/Stable",
    "Environment :: Plugins",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
#    "Programming Language :: Python :: 3",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Internet :: WWW/HTTP :: Site Management",
    "Topic :: Software Development :: Version Control",
]
