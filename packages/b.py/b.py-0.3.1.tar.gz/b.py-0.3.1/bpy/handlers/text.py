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


import cgi
import re

from bpy.handlers import base
from bpy.util import utf8_encoded


class Handler(base.BaseHandler):
  """Handler for plain text

  >>> handler = Handler(None)
  >>> handler.markup = 'post <content>\\n & something'
  >>> print handler.generate()
  post &lt;content&gt;<br/>
   &amp; something
  >>> handler.options['pre_wrap'] = True
  >>> print handler.generate()
  <pre>post &lt;content&gt;
   &amp; something</pre>
  >>> handler = Handler(None)
  >>> print handler.generate_header({'title': 'foobar'})
  !b
  title: foobar
  <BLANKLINE>
  """

  PREFIX_HEAD = ''
  PREFIX_END = ''
  HEADER_FMT = '%s: %s'

  def generate_title(self, markup=None):
    """Generate HTML from plain text

    >>> handler = Handler(None)
    >>> print handler.generate_title('a < b\\nc & d\\n\\nfoo')
    a &lt; b c &amp; d foo
    """
    html = super(Handler, self).generate_title(markup)
    html = html.replace('<pre>', '').replace('</pre>', '')
    return re.sub('(<br/> )+', ' ', html)

  def _generate(self, markup=None):
    """Generate HTML from plain text

    >>> handler = Handler(None)
    >>> print handler._generate('a < b\\nc & d\\n\\xc3\\xa1')
    a &lt; b<br/>
    c &amp; d<br/>
    \xc3\xa1
    >>> handler.options['pre_wrap'] = True
    >>> print handler._generate('abc\\ndef')
    <pre>abc
    def</pre>
    """
    if markup is None:
      markup = self.markup

    html = cgi.escape(markup.decode('utf8'))
    html = utf8_encoded(html)
    if self.options.get('pre_wrap', False):
      return '<pre>%s</pre>' % html
    else:
      return html.replace('\n', '<br/>\n')
