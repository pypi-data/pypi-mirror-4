# Copyright (C) 2011-2013 by Yu-Jie Lin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import subprocess
from docutils import nodes
from docutils.core import publish_parts
from docutils.parsers.rst import Directive, directives, roles
from xml.sax.saxutils import escape

from bpy.handlers import base
from bpy.util import utf8_encoded


def register_directive(dir_name):
  """For lazy guys

  @register_directive(name)
  class MyDirective(Directive):
    [...]
  """
  def _register_directive(directive):
    directives.register_directive(dir_name, directive)
    return directive
  return _register_directive


def register_role(role_name):

  def _register_role(role):

    roles.register_canonical_role(role_name, role)
    return role

  return _register_role


# YouTube video embedding by Jason Stitt. MIT License
# http://countergram.com/youtube-in-rst
# TODO convert to class style, so it will read a bit cleaner
# TODO support iframe style
def youtube(name, args, options, content, lineno,
            contentOffset, blockText, state, stateMachine):
    """ Restructured text extension for inserting youtube embedded videos """
    CODE = """\
    <object type="application/x-shockwave-flash"
            width="%(width)s"
            height="%(height)s"
            class="youtube-embed"
            data="http://www.youtube.com/v/%(yid)s">
        <param name="movie" value="http://www.youtube.com/v/%(yid)s"></param>
        <param name="wmode" value="transparent"></param>%(extra)s
    </object>
    """

    PARAM = """\n    <param name="%s" value="%s"></param>"""

    if len(content) == 0:
        return
    string_vars = {
        'yid': content[0],
        'width': 425,
        'height': 344,
        'extra': ''
    }
    extra_args = content[1:]  # Because content[0] is ID
    extra_args = [ea.strip().split("=") for ea in extra_args]  # key=value
    extra_args = [ea for ea in extra_args if len(ea) == 2]  # drop bad lines
    extra_args = dict(extra_args)
    if 'width' in extra_args:
        string_vars['width'] = extra_args.pop('width')
    if 'height' in extra_args:
        string_vars['height'] = extra_args.pop('height')
    if extra_args:
        params = [PARAM % (key, extra_args[key]) for key in extra_args]
        string_vars['extra'] = "".join(params)
    return [nodes.raw('', CODE % (string_vars), format='html')]
youtube.content = True
directives.register_directive('youtube', youtube)


@register_directive('precode')
class PreCode(Directive):
  """Generate HTML as <pre><code> style for highlight.js"""
  optional_arguments = 1
  option_spec = {'class': directives.unchanged}
  has_content = True

  @staticmethod
  def _run(code, lang=None, options=None):
    if options is None:
      options = {}

    if lang:
      tmpl = '<code class="%s">%%s</code>' % lang
    else:
      tmpl = '<code>%s</code>'

    if 'class' in options:
      tmpl = ('<pre class="%s">' % options['class']) + tmpl + '</pre>'
    else:
      tmpl = '<pre>' + tmpl + '</pre>'

    html = tmpl % escape(code)
    return html

  def run(self):

    lang = self.arguments[0] if len(self.arguments) else None
    raw = nodes.raw(
      '',
      self._run('\n'.join(self.content), lang, self.options),
      format='html'
    )
    return [raw]


@register_directive('pyrun')
class PyRun(Directive):
  """Append the output of Python code

  The encoding definition may be required when use Unicode characters:

    # -*- coding: utf-8 -*-
  """
  # TODO expand this to arbitrary command
  option_spec = {'command': directives.unchanged,
                 'class': directives.unchanged,
                 }
  has_content = True

  def _generate_std(self, content):

    content = escape(content.decode('utf-8'))
    return nodes.raw(
      '',
      '<pre class="pyrun stdout">%s</pre>' % content,
      format='html'
    )

  def run(self):
    code = '\n'.join(self.content)

    cmd = 'python'
    if 'command' in self.options:
      cmd = self.options['command']
    proc = subprocess.Popen((cmd, '-'),
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate(code.encode('utf-8'))

    raws = [nodes.raw(
      '',
      PreCode._run(code, self.options.get('class', 'python'), self.options),
      format='html'
    )]
    if not stdout:
      stdout = '*** NO OUTPUT ***'
    raws.append(self._generate_std(stdout))
    if stderr:
      raws.append(self._generate_std(stderr))
    return raws


@register_role('kbd')
def kbd(name, rawtext, text, lineno, inliner, options=None, content=None):
  """Generate kbd element"""

  return [nodes.raw('', '<kbd>%s</kbd>' % text, format='html')], []


class Handler(base.BaseHandler):
  """Handler for reStructuredText markup language

  >>> handler = Handler(None)
  >>> print handler.generate_header({'title': 'foobar'})
  .. !b
     title: foobar
  <BLANKLINE>
  """

  PREFIX_HEAD = '.. '
  PREFIX_END = ''
  HEADER_FMT = '   %s: %s'

  def _generate(self, markup=None):
    """Generate HTML from Markdown

    >>> handler = Handler(None)
    >>> print handler._generate('a *b*')
    <p>a <em>b</em></p>
    """
    if markup is None:
      markup = self.markup

    settings_overrides = {
      'output_encoding': 'utf8',
      'initial_header_level': 2,
      'doctitle_xform': 0,
      'footnote_references': 'superscript',
    }
    settings_overrides.update(self.options.get('settings_overrides', {}))

    id_affix = self.id_affix
    if id_affix:
      settings_overrides['id_prefix'] = id_affix + '-'
      self.set_header('id_affix', id_affix)

    doc_parts = publish_parts(markup,
                              settings_overrides=settings_overrides,
                              writer_name="html")

    html = doc_parts['body_pre_docinfo'] + doc_parts['body'].rstrip()
    return utf8_encoded(html)
