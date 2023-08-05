"""\
Genshi rendering
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

from __future__ import absolute_import

import os.path
import weakref

try:
    from genshi import QName, Stream
    from genshi.core import Attrs, END, START, TEXT
    from genshi.template import Context, MarkupTemplate, NewTextTemplate, \
                                TemplateLoader
    from genshi.template.eval import Suite
    has_genshi = True
except ImportError:
    TemplateLoader = object
    has_genshi = False
try:
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters.html import HtmlFormatter, _get_ttype_class
    from pygments.styles import get_style_by_name
    has_pygments = True
except ImportError:
    has_pygments = False

from .site import cache_must_revalidate, renderer
from .util import guess_mimetype, hex_node


class Loader(TemplateLoader):
    """A template loader propagating the revision to included templates"""

    def load(self, filename, relative_to=None, cls=None, encoding=None):
        if relative_to is not None and '@' not in filename:
            parts = relative_to.rsplit('@', 1)
            if len(parts) == 2:
                filename += '@' + parts[1]
        return super(Loader, self).load(filename, relative_to, cls, encoding)


# A cache of template loaders by repository
_loaders = weakref.WeakKeyDictionary()


def get_template_loader(repo):
    """Return a template loader for the given repository."""
    try:
        return _loaders[repo]
    except KeyError:
        pass

    def load_template(filename):
        # Filename is "{path}@{revision}"
        path, rev = filename.rsplit('@', 1)
        rev = bytes(rev) if rev else None
        fctx = repo[rev][path]
        def uptodate():
            return rev is not None
        return filename, filename, fctx.data(), uptodate

    loader = _loaders[repo] = Loader(
        load_template, auto_reload=True, max_cache_size=100,
        default_encoding='utf-8', variable_lookup='strict')
    return loader


def execute(path, context):
    """Execute a script in the given context."""
    with open(path, 'r') as f:
        source = f.read()
    Suite(source, path).execute(context)


def make_context(req, path, **kwargs):
    """Create a rendering context."""
    context = Context(req=req, **kwargs)
    context_module = req.web.config('hgsite', 'context.genshi', '')
    if context_module:
        execute(os.path.join(req.repo.path, context_module), context)
    return context


# Mappings for removal of control characters
translate_nop = ''.join(chr(i) for i in range(256))
invalid_control_chars = ''.join(chr(i) for i in range(32)
                                if i not in [0x09, 0x0a, 0x0d])


@renderer('genshi:html', 'genshi:xhtml', 'genshi:xml', register=has_genshi)
def render_markup_template(req, path, name, config, **kwargs):
    """Render a Genshi markup template."""
    method = name.split(':', 1)[-1]
    mimetype = guess_mimetype(config.get('mimetype'), path, 'text/xml')
    encoding = config.get('encoding', 'utf-8')
    loader = get_template_loader(req.repo)
    template = loader.load('%s@%s' % (path, hex_node(req.ctx)),
                           cls=MarkupTemplate)
    context = make_context(req, path, highlight=highlight, **kwargs)
    stream = template.generate(context)
    text = stream.render(method, encoding=encoding)
    text = text.translate(translate_nop, invalid_control_chars)
    return req.send(text, mimetype=mimetype, encoding=encoding,
                    headers=cache_must_revalidate)


@renderer('genshi:text', register=has_genshi)
def render_text_template(req, path, name, config, **kwargs):
    """Render a Genshi text template."""
    method = name.split(':', 1)[-1]
    mimetype = guess_mimetype(config.get('mimetype'), path, 'text/plain')
    encoding = config.get('encoding', 'utf-8')
    loader = get_template_loader(req.repo)
    template = loader.load('%s@%s' % (path, hex_node(req.ctx)),
                           cls=NewTextTemplate)
    stream = template.generate(make_context(req, path, **kwargs))
    text = stream.render(method, encoding=encoding)
    return req.send(text, mimetype=mimetype, encoding=encoding,
                    headers=cache_must_revalidate)


@renderer('pygments:css', register=has_pygments, file_must_exist=False)
def render_pygments_css(req, path, name, config, **kwargs):
    """Render a (virtual) CSS file with Pygments styles."""
    style_cls = get_style_by_name(config.get('style', 'trac'))
    container = config.get('container', '')
    formatter = HtmlFormatter(style=style_cls, nobackground=True)
    content = formatter.get_style_defs(c.strip() for c in container.split(','))
    return req.send(content, mimetype='text/css', encoding='utf-8',
                    headers=cache_must_revalidate)


def _group_by_class(tokens):
    """Group Pygments lexer tokens with the same CSS class."""
    cls = None
    text = []
    for ttype, value in tokens:
        c = _get_ttype_class(ttype)
        if c == cls:
            text.append(value)
            continue
        if value:
            yield cls, u''.join(text)
            text = [value]
            cls = c
    if text:
        yield cls, u''.join(text)


def generate_highlight_markup(tokens):
    """Generate a Genshi stream for Pygments markup."""
    pos = (None, -1, -1)
    span = QName('span')
    class_ = QName('class')
    for cls, text_chunk in _group_by_class(tokens):
        if cls:
            yield START, (span, Attrs([(class_, cls)])), pos
            yield TEXT, text_chunk, pos
            yield END, span, pos
        else:
            yield TEXT, text_chunk, pos


def generate_text(text):
    """Generate a Genshi stream with a single text node."""
    yield TEXT, text, (None, -1, -1)


def highlight(text, lexer, tabsize=0):
    """Syntax-highlight the given text with the given lexer, and return a
    Genshi stream of the result."""
    if has_pygments:
        try:
            lexer = get_lexer_by_name(lexer, stripnl=False, ensurenl=False,
                                      tabsize=tabsize)
            tokens = lexer.get_tokens(text)
            return Stream(generate_highlight_markup(tokens))
        except Exception:
            pass
    return Stream(generate_text(text))
