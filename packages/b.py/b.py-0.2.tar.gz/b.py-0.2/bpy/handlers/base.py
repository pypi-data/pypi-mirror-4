#!/usr/bin/env python
# Copyright (C) 2013 by Yu-Jie Lin
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


from abc import abstractmethod, ABCMeta
from hashlib import md5
from os.path import basename, splitext
import re
import sys

import smartypants
from smartypants import smartyPants


class BaseHandler():
  """The base clase of markup handler"""
  __metaclass__ = ABCMeta

  # default handler options
  OPTIONS = {
    'markup_prefix': '',
    'markup_suffix': '',
    'smartypants': False,
    'id_affix': None,
    }
    
  MERGE_HEADERS = ('kind', 'blog', 'id', 'url')
  HEADER_FMT = '%s: %s'
  PREFIX_HEAD = ''
  PREFIX_END = ''

  RE_SPLIT = re.compile(r'^(?:([^\n]*?!b.*?)\n\n)?(.*)', re.DOTALL | re.MULTILINE)
  RE_HEADER = re.compile(r'(.*?)\s*[=:]\s*(.*)\s*')

  def __init__(self, filename, options=None):

    self.filename = filename
    self.title = ''
    self.options = self.OPTIONS.copy()
    self.options.update(options or {})
    if filename:
      with open(filename) as f:
        self.source = f.read()
      header, markup = self.split_header_markup()
      self.title = splitext(basename(filename))[0]
    else:
      header = {}
      markup = ''
    self.header = header
    self.markup = markup
    self.modified = False

  def set_header(self, k, v):
    """Set header

    >>> class Handler(BaseHandler):
    ...   def _generate(self, source=None): return source
    >>> handler = Handler(None)
    >>> print handler.header
    {}
    >>> handler.modified
    False
    >>> handler.set_header('foo', 'bar')
    >>> handler.header
    {'foo': 'bar'}
    >>> handler.modified
    True
    """
    if k in self.header and self.header[k] == v:
      return

    self.header[k] = v
    self.modified = True

  def merge_header(self, header):
    """Merge header

    >>> class Handler(BaseHandler):
    ...   def _generate(self, source=None): return source
    >>> handler = Handler(None)
    >>> handler.merge_header({'id': 12345, 'bogus': 'blah'})
    >>> handler.header
    {'id': 12345}
    >>> handler.modified
    True
    """
    for k, v in header.items():
      if k not in self.MERGE_HEADERS:
        continue
      if k == 'blog':
        v = v['id']
      elif k == 'kind':
        v = v.replace('blogger#', '')
      self.set_header(k, v)

  @property
  def markup(self):
    """Return markup with markup_prefix and markup_suffix
    
    >>> class Handler(BaseHandler):
    ...   def _generate(self, source=None): return source
    >>> options = {
    ...   'markup_prefix': 'the prefix\\n',
    ...   'markup_suffix': '\\nthe suffix',
    ...   }
    >>> handler = Handler(None, options)
    >>> handler.markup = 'content'
    >>> print handler.markup
    the prefix
    content
    the suffix
    """
    return '%s%s%s' % (
      self.options['markup_prefix'],
      self._markup,
      self.options['markup_suffix'],
      )

  @markup.setter
  def markup(self, markup):
    """Set the markup"""
    self._markup = markup

  @property
  def id_affix(self):
    """Return id_affix

    The initial value is from self.options, and can be overriden by
    self.header.

    Returns None if it's None.
    Returns value if value is not ''
    Returns first 4 digits of md5 of value if value is '', and assign back to
            self.options. _generate method of Handler should write back to
            self.header.

    >>> class Handler(BaseHandler):
    ...   def _generate(self, source=None): return source
    >>> options = {
    ...   'id_affix': None,
    ...   }
    >>> handler = Handler(None, options)
    >>> print repr(handler.id_affix)
    None
    >>> handler.options['id_affix'] = 'foobar'
    >>> print repr(handler.id_affix)
    'foobar'
    >>> # auto generate an id affix from title
    >>> handler.options['id_affix'] = ''
    >>> handler.title = 'abc'
    >>> print repr(handler.id_affix)
    '9001'
    >>> handler.header['id_affix'] = 'override-affix'
    >>> print repr(handler.id_affix)
    'override-affix'
    """
    id_affix = self.options['id_affix']
    # override?
    if 'id_affix' in self.header:
      id_affix = self.header['id_affix']
      if self.header['id_affix'] and id_affix != 'None':
        return self.header['id_affix']

    # second case is from header of post, has to use string 'None'
    if id_affix is None or id_affix == 'None':
      return None

    if id_affix:
      return id_affix

    m = md5()
    m.update(self.title)
    return m.hexdigest()[:4]

  @abstractmethod
  def _generate(self, markup=None):
    """Generate HTML of markup source"""
    raise NotImplementError

  def generate(self, markup=None):
    """Generate HTML
    
    >>> class Handler(BaseHandler):
    ...   def _generate(self, markup=None): return markup
    >>> handler = Handler(None)
    >>> print handler.generate('foo "bar"')
    foo "bar"
    >>> handler.options['smartypants'] = True
    >>> print handler.generate('foo "bar"')
    foo &#8220;bar&#8221;
    """

    if markup is None:
      markup = self.markup

    html = self._generate(markup)

    if self.options.get('smartypants', False):
      RE = smartypants.tags_to_skip_regex 
      pattern = RE.pattern.replace('|code', '|code|tt')
      pattern = pattern.replace('|script', '|script|style')
      RE = re.compile(pattern, RE.flags)
      smartypants.tags_to_skip_regex = RE
      html = smartyPants(html)

    return html.encode('utf-8')

  def generate_header(self, header=None):
    """Generate header in text for writing back to the file
    
    >>> class Handler(BaseHandler):
    ...   PREFIX_HEAD = 'foo '
    ...   PREFIX_END = 'bar'
    ...   HEADER_FMT = '--- %s: %s'
    ...   def _generate(self, source=None): pass
    >>> handler = Handler(None)
    >>> print handler.generate_header({'title': 'foobar'})
    foo !b
    --- title: foobar
    bar
    <BLANKLINE>
    >>> print handler.generate_header({'labels': ['foo', 'bar']})
    foo !b
    --- labels: foo, bar
    bar
    <BLANKLINE>
    """
    if header is None:
      header = self.header

    lines = [self.PREFIX_HEAD + '!b']
    for k, v in header.items():
      if k == 'labels':
        v = ', '.join(v)
      lines.append(self.HEADER_FMT % (k, v))
    lines.append(self.PREFIX_END)
    return '\n'.join(filter(None, lines)) + '\n'

  def generate_title(self, title=None):
    """Generate title for posting
    
    >>> class Handler(BaseHandler):
    ...   def _generate(self, source=None): return source
    >>> handler = Handler(None)
    >>> print handler.generate_title('foo "bar"')
    foo "bar"
    >>> handler.options['smartypants'] = True
    >>> print handler.generate_title('foo "bar"')
    foo &#8220;bar&#8221;
    >>> print repr(handler.generate_title('foo\\nbar\\n\\n'))
    'foo bar'
    """
    if title is None:
      title = self.header.get('title', self.title)

    title = self.generate(title)
    title = title.replace('<p>', '').replace('</p>', '')
    # no trailing newlines
    title = title.rstrip('\n')
    title = title.replace('\n', ' ')
    return title

  def generate_post(self):
    """Generate dict for merging to post object of API"""
    post = {'title': self.generate_title()}
    for k in ('blog', 'id', 'labels'):
      if k not in self.header:
        continue
      if k == 'blog':
        post[k] = {'id': self.header[k]}
      else:
        post[k] = self.header[k]
    return post

  def split_header_markup(self, source=None):
    """Split source into header and markup parts
    
    It also parses header into a dict."""
    if source is None:
      source = self.source

    header, markup = self.RE_SPLIT.match(source).groups()

    _header = {}
    if header:
      for item in header.split('\n'):
        m = self.RE_HEADER.match(item)
        if not m:
          continue
        k, v = map(str.strip, m.groups())
        if k == 'labels':
          v = filter(None, [label.strip() for label in v.split(',')])
        _header[k] = v
    header = _header

    return header, markup

  def update_source(self, header=None, markup=None, only_returned=False):

    if header is None:
      header = self.header
    if markup is None:
      markup = self.markup

    source = self.generate_header(header) + \
             '\n' + \
             markup
    if not only_returned:
      self.source = source
    return source

  def write(self, forced=False):
    """Write source back to file"""
    if not self.modified:
      if not forced:
        return
    else:
      self.update_source()

    with open(self.filename, 'w') as f:
      f.write(self.source)
    self.modified = False
