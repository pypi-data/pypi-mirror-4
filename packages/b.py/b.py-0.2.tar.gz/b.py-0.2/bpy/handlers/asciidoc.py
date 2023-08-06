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


import re
import StringIO
import sys

from bpy.api.asciidocapi import AsciiDocAPI
from bpy.handlers import base


class Handler(base.BaseHandler):
  """Handler for AsciiDoc markup language

  >>> handler = Handler(None)
  >>> print handler.generate_header({'title': 'foobar'})
  // !b
  // title: foobar
  <BLANKLINE>
  """

  PREFIX_HEAD = '// '
  PREFIX_END = ''
  HEADER_FMT = '// %s: %s'

  def _generate(self, markup=None):
    """Generate HTML from AsciiDoc

    >>> handler = Handler(None)
    >>> print handler._generate('a *b*')
    <p>a <strong>b</strong></p>
    """
    if markup is None:
      markup = self.markup

    asciidoc = AsciiDocAPI()
    infile = StringIO.StringIO(markup)
    outfile = StringIO.StringIO()
    asciidoc.options('--no-header-footer')
    asciidoc.execute(infile, outfile, backend='html4')

    return outfile.getvalue().rstrip()
