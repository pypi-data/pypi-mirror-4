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

from distutils.core import Command, setup
from unittest import TestLoader, TextTestRunner

script_name = 'b.py'

class test(Command):

  description = 'run tests'
  user_options = []

  def initialize_options(self):

    pass

  def finalize_options(self):

    pass

  def run(self):

    loader = TestLoader()
    tests = loader.discover(start_dir='tests')
    runner = TextTestRunner(verbosity=2)
    runner.run(tests)

with open(script_name) as f:
  meta = dict(
    (k.strip(' _'), eval(v)) for k, v in
      # There will be a '\n', with eval(), it's safe to ignore
      (line.split('=') for line in f if line.startswith('__'))
    )

classifiers = [
  'Development Status :: 3 - Alpha',
  'Environment :: Console',
  'Intended Audience :: End Users/Desktop',
  'License :: OSI Approved :: MIT License',
  'Natural Language :: English',
  'Operating System :: POSIX :: Linux',
  'Programming Language :: Python :: 2.7',
  'Topic :: Other/Nonlisted Topic',
  ]

packages = [
  'bpy',
  'bpy.api',
  'bpy.handlers',
  ]

data_files = [
  ('share/' + script_name, ['client_secrets.json']),
  ]

setup_d = dict(
  cmdclass = {'test': test},

  name        = meta['program'],
  version     = meta['version'],
  license     = meta['license'],
  url         = meta['website'],

  description = meta['description'],

  author       = meta['author'],
  author_email = meta['email'],

  classifiers = classifiers,

  scripts  = [script_name],
  packages = packages,

  data_files = data_files,
  )

if __name__ == '__main__':
  setup(**setup_d)
