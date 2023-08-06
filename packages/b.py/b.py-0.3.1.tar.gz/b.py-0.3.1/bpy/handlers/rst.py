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


from docutils.core import publish_parts
from docutils.parsers.rst import directives, roles

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

  def __init__(self, filename, options=None):

    super(Handler, self).__init__(filename, options)

    if not options:
      return

    for dir_name, directive in options.get('register_directives', {}).items():
      directives.register_directive(dir_name, directive)
    for role_name, role in options.get('register_roles', {}).items():
      roles.register_canonical_role(role_name, role)

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
