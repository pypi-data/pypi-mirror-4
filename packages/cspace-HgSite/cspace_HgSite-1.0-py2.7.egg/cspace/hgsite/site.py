"""\
'site' web command handling
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

import re
import sys
import time
from urlparse import urlunparse

from mercurial import config, error, revset, util
from mercurial.hgweb import common, webcommands, webutil

from .util import exists_in_wc, find_line_no, get_ext, guess_mimetype, \
                  hex_node, href_builder, http_date

# TODO: Hook into hgweb.__call__ instead of using a web command
# TODO: Fix unicode issues (try accented chars in URL)
# TODO: Hook into hgwebdir and allow replacing the repository index
# TODO: Allow specifying caching by path regexp

# The web command name used for registration
webcmd = 'hgsite'

# The prefix marking that the path starts with a node
node_prefix = '~'


class Config(config.config):
    """Per-repository configuration"""

    def __init__(self, req):
        super(Config, self).__init__()
        self.parse('.hgsite', req.ctx['.hgsite'].data())

    @util.propertycache
    def base_path(self):
        """Return the base path for site files."""
        return self.get('config', 'base_path', 'site').strip().strip('/')

    @util.propertycache
    def error_page(self):
        """Return the path to the error page."""
        return self.get('config', 'error_page', '').strip().lstrip('/')

    @util.propertycache
    def ext_search_order(self):
        """Return the extension search order."""
        value = self.get('config', 'ext_search_path', '')
        return dict((ext, i) for i, ext in
                    enumerate(ext.strip() for ext in value.split(',')))

    @util.propertycache
    def site_index(self):
        """Return the entry point for the site."""
        return self.get('config', 'site_index', 'index').strip()

    @util.propertycache
    def render_info(self):
        """Get all rendering information."""
        patterns = {}
        config = {}
        for key, value in self['render'].iteritems():
            parts = key.split('.', 1)
            value = value.strip()
            if len(parts) == 1:
                patterns[key] = re.compile(value)
                config.setdefault(key, {})
            else:
                config.setdefault(parts[0], {})[parts[1]] = value
        return [(patterns[name], config[name].pop('renderer', 'static'),
                 config[name]) for name in sorted(patterns)]

    def get_render_info(self, path):
        """Get rendering info for the given path."""
        for pattern, renderer, config in self.render_info:
            if pattern.match(path):
                return renderer, config
        return None, {}

    def site_path(self, path):
        """Return the repository path corresponding to a site path."""
        return '%s/%s' % (self.base_path, path.lstrip('/'))


class Request(object):
    """A wrapper for a Mercurial WSGI request object."""

    def __init__(self, web, req):
        self.web = web
        self.repo = web.repo
        self._req = req
        self.status = common.HTTP_OK

    def __getattr__(self, name):
        return getattr(self._req, name)

    @util.propertycache
    def path_info(self):
        """Return the path info for this request."""
        if 'PATH_INFO' in self.env:
            parts = self.env['PATH_INFO'].strip('/').split('/')
            repo_parts = self.env.get('REPO_NAME', '').split('/')
            if parts[:len(repo_parts)] == repo_parts:
                parts = parts[len(repo_parts):]
            return '/'.join(parts)
        else:
            qs = self.env['QUERY_STRING'].split('&', 1)[0].split(';', 1)[0]
            return qs.strip('/')

    @util.propertycache
    def default_revision(self):
        """Return the default revision configured in `hgrc`."""
        expr = self.web.config('hgsite', 'default_revision', 'default').strip()
        if not expr:
            return ''
        match = revset.match(self.repo.ui, expr)
        revs = match(self.repo, xrange(len(self.repo)))
        if not revs:
            self.repo.ui.warn("[hgsite] default_revision yields empty set\n")
            raise self.not_found("revision")
        return revs[0]

    def abs_url(self, url):
        """Make the given URL absolute."""
        if url.startswith(('http://', 'https://')):
            return url
        scheme = self.env.get('wsgi.url_scheme')
        host = self.env.get('HTTP_HOST')
        if not host:
            host = self.env['SERVER_NAME']
            port = self.env['SERVER_PORT']
            if port != ('443' if scheme == 'https' else '80'):
                host += ':%s' % port
        return urlunparse((scheme, host, url, None, None, None))

    def redirect(self, url, status=302):
        """Generate a redirection response to the given URL."""
        self.header([
            ('Location', self.abs_url(url)),
            ('Pragma', 'no-cache'),
            ('Cache-Control', 'no-cache'),
            ('Expires', 'Fri, 01 Jan 1999 00:00:00 GMT')])
        self.respond(status, type='text/plain')
        return ['']

    def send(self, content, mimetype=None, encoding=None, headers=None,
             status=None):
        """Generate a response with the given content and metadata."""
        content_type = mimetype
        if content_type is not None and encoding is not None:
            content_type += ';charset=%s' % encoding
        if headers is not None:
            self.header(headers)
        if status is None:
            status = self.status
        self.respond(status, type=content_type, length=len(content))
        return [content]

    def not_found(self, label, what=None):
        """Return a '{something} not found' exception."""
        if what is None:
            msg = "The requested %s was not found" % label
        else:
            msg = "The requested %s was not found: %s" % (label, what)
        return common.ErrorResponse(common.HTTP_NOT_FOUND, msg)


# Cache control headers
cache_must_revalidate = [
    ('Cache-Control', 'must-revalidate'),
    ('Expires', 'Fri, 01 Jan 1999 00:00:00 GMT'),
]


def browse_href_builder(base, ctx):
    """Return a URL builder to link to repository files in the file browser."""
    node = ctx.hex() if ctx.node() is not None else node_prefix
    href = href_builder(base.rstrip('/') + '/file/' + node)

    def build_href(path, line=None, n=1):
        """Build a URL to the given file, optionally linking to a line.

        `line` can be a line number, or a regexp to be matched against the
        lines of the file."""
        hash = ''
        if isinstance(line, basestring):
            try:
                data = ctx[path].data()
                line = find_line_no(line, data, n)
            except Exception:
                line = None
        if isinstance(line, (int, long)):
            hash = '#l%d' % line
        return href(path) + hash

    return build_href


# Renderer registry
_renderers = {}


def renderer(*names, **kwargs):
    """Decorate a function to mark it as a renderer."""
    def decorate(f):
        f.__dict__.update(kwargs)
        if getattr(f, 'register', True):
            for name in names:
                _renderers[name] = f
        return f
    return decorate


@renderer('static')
def render_static(req, path, name, config, **kwargs):
    """Render static content."""
    mimetype = guess_mimetype(config.get('mimetype'), path,
                              'application/octet-stream')
    if req.url_node:
        headers = [('Cache-Control', 'public'),
                   ('Expires', http_date(time.time() + 365 * 24 * 3600))]
    else:
        headers = cache_must_revalidate
    return req.send(req.ctx[path].data(), mimetype=mimetype,
                    encoding=config.get('encoding'), headers=headers)


@renderer('exec')
def render_exec(req, path, name, config, **kwargs):
    """Render by calling a `render()` function in a module."""
    globals = {}
    exec req.ctx[path].data() in globals
    render = globals.get('render')
    if render is None:
        raise req.not_found("page", req.path)
    return render(req, path, name, **kwargs)


def render(req, url_path, kwargs=None):
    """Render the given URL path in the given request."""
    path = webutil.cleanpath(req.repo, req.cfg.site_path(url_path.rstrip('/')))
    ext_order = req.cfg.ext_search_order

    def match_key(p):
        ext = get_ext(p)
        return not p == path, ext_order.get(ext, sys.maxint), ext

    match = req.ctx.match([r're:%s(?:\.[^/]*)?$' % re.escape(path)])
    try:
        file_path = min(req.ctx.walk(match), key=match_key)
        file_exists = True
    except ValueError:
        file_path = path
        file_exists = False

    name, config = req.cfg.get_render_info(file_path)
    renderer = _renderers.get(name)
    if renderer is None \
       or not file_exists and getattr(renderer, 'file_must_exist', True):
        raise req.not_found("page", req.url_path)
    return renderer(req, file_path, name, config, **(kwargs or {}))


def prepare_request(req, node):
    """Prepare the request object to render at the given node."""
    # Get configuration
    repo_node = node if node is not None else req.default_revision
    allow_wc = req.web.configbool('hgsite', 'allow_wc', False)
    if repo_node == '' and not allow_wc:
        raise req.not_found("revision")
    try:
        req.ctx = req.repo[repo_node or None]
    except error.RepoLookupError:
        raise req.not_found("revision", node)
    try:
        req.cfg = Config(req)
    except (IOError, error.LookupError):
        return False

    # Add URL builders to the request object
    if node is None:
        req.href = href_builder(req.url)
    else:
        req.href = href_builder(req.url + node_prefix + node)
    req.rev_href = href_builder(req.url + node_prefix + hex_node(req.ctx))
    req.repo_href = href_builder(req.url)

    if repo_node != '':
        def build_static_href(path):
            """Return a site URL for a static resource."""
            fctx = req.ctx[req.cfg.site_path(path)]
            # Find the last changeset where the file was modified
            fctx = fctx.filectx(fctx.filerev())
            return req.repo_href(node_prefix + fctx.hex(), path)
        req.static_href = build_static_href
    else:
        req.static_href = req.rev_href

    def build_hist_href(node, *args, **kwargs):
        """Return a historical site URL at the given node."""
        return req.repo_href(node_prefix + node if node is not None else None,
                             *args, **kwargs)
    req.hist_href = build_hist_href
    req.browse_href = browse_href_builder(req.url, req.ctx)
    req.repo_default = req.repo_href(req.web._default_cmd)
    return True


def handle_default_webcmd(web, req, tmpl):
    """Handle the default web command."""
    req = Request(web, req)

    # Extract node and path from PATH_INFO
    if req.path_info.startswith(node_prefix):
        # PATH_INFO is '~{node}' or '~{node}/{path}'
        parts = req.path_info.split('/', 1)
        req.url_node = parts[0][len(node_prefix):]
        req.url_path = parts[1] if len(parts) > 1 else ''
    else:
        # PATH_INFO is '' or '{path}'
        req.url_node = None
        req.url_path = req.path_info

    try:
        if not prepare_request(req, req.url_node):
            # Configuration not found, do as if we didn't exist
            default_handler = getattr(webcommands, req.web._default_cmd)
            return default_handler(req.web, req._req, tmpl)
        return render(req, req.url_path or req.cfg.site_index)

    except Exception:
        exc_info = sys.exc_info()
        if not (prepare_request(req, None) and req.cfg.error_page):
            raise
        req.status = exc_info[1].code \
                     if isinstance(exc_info[1], common.ErrorResponse) \
                     else common.HTTP_SERVER_ERROR
        kwargs = {'exc_info': exc_info}
        return render(req, req.cfg.error_page, kwargs)


def handle_caching(orig, web, req, *args, **kwargs):
    """Customize page caching."""
    cmd = req.form['cmd'][0]
    if cmd == webcmd:
        return  # Site caching is decided by renderers
    if cmd == 'file' and req.form.get('node', [''])[0] == node_prefix:
        return  # Prevent caching of working copy file pages
    return orig(web, req, *args, **kwargs)


def wc_filectx(orig, repo, req, *args, **kwargs):
    """Hack to allow viewing files from the working copy in the file browser.

    When `[hgsite] allow_wc` is True, and the node passed in the URL is
    `node_prefix`, temporarily substitute the node with None and call the
    original `filectx()`. It will return a `workingfilectx` instance pointing
    to the desired file.

    However, this `fctx` will raise an exception at rendering time, due to
    a call to `fctx.hex()`. By dynamically subclassing the instance, the call
    can be intercepted and a dummy value can be returned."""
    if (req.form['cmd'][0] != 'file'
            or req.form.get('node', ['']) != [node_prefix]
            or not repo.ui.configbool('hgsite', 'allow_wc', False)):
        return orig(repo, req, *args, **kwargs)

    # Temporarily substitute the node to get a `workingfilectx`
    req.form['node'] = [None]
    try:
        fctx = orig(repo, req, *args, **kwargs)
        if fctx.node() is None:
            if not exists_in_wc(repo, fctx.path()):
                raise error.LookupError(node_prefix, fctx.path(),
                                        'not found')
            # Make fctx safe for rendering
            class SafeWorkingFileCtx(fctx.__class__):
                def hex(self):
                    return ''
            fctx.__class__ = SafeWorkingFileCtx
    finally:
        req.form['node'] = [node_prefix]
    return fctx


def hgweb_templater(orig, self, req, *args, **kwargs):
    """Override the default command if redirection is enabled."""
    tmpl = orig(self, req, *args, **kwargs)
    self._default_cmd = tmpl.cache.get('default', 'shortlog')
    tmpl.cache['default'] = webcmd
    return tmpl
