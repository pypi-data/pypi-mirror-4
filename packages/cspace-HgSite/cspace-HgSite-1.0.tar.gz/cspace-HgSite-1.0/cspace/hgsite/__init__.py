# Extension entry point
# Copyright (C) 2012 Remy Blank
#
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

"""\
repository-backed website engine
"""

from mercurial import extensions
from mercurial.hgweb import hgweb_mod, webcommands, webutil

from . import genshi, meta
from .site import handle_caching, handle_default_webcmd, hgweb_templater, \
                  wc_filectx, webcmd


def uisetup(ui):
    """Hook into Mercurial modules."""
    extensions.wrapfunction(hgweb_mod, 'caching', handle_caching)
    extensions.wrapfunction(hgweb_mod.hgweb, 'templater', hgweb_templater)
    extensions.wrapfunction(webutil, 'filectx', wc_filectx)

    setattr(webcommands, webcmd, handle_default_webcmd)
    webcommands.__all__.append(webcmd)


testedwith = '2.2.3'
buglink = 'mailto:%s' % meta.author_email
