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


import argparse as ap
import httplib2
import imp
import os
from os import path
from os.path import dirname, expanduser, realpath
import re
from StringIO import StringIO
import sys
import traceback

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage as BaseStorage
from oauth2client.tools import run

HAS_LNKCKR = False
try:
  from lnkckr.checkers.html import Checker
  HAS_LNKCKR = True
except ImportError:
  pass

__program__ = 'b.py'
__description__ = 'Post to Blogger in markup language seamlessly'
__copyright__ = 'Copyright 2013, Yu Jie Lin'
__license__ = 'MIT'
__version__ = '0.4.1'
__website__ = 'http://bitbucket.org/livibetter/b.py'

__author__ = 'Yu-Jie Lin'
__email__ = 'livibetter@gmail.com'

# API stuff
###########

# global stuff
http = None
service = None

# filename of credentials
search_path = [
  dirname(realpath(sys.argv[0])),
  '/usr/share/' + __program__,
  '/usr/local/share/' + __program__,
  '~/share/' + __program__,
  '~/.local/share/' + __program__,
]
search_path = [expanduser(p + '/client_secrets.json') for p in search_path]
search_path = filter(path.exists, search_path)
CLIENT_SECRETS = ''
if search_path:
  CLIENT_SECRETS = search_path[0]
API_SCOPE = 'https://www.googleapis.com/auth/blogger'
NOTFOUND_MESSAGE = 'Could not found client_secrets.json'
API_STORAGE = 'b.dat'


class Storage(BaseStorage):
  """Inherit the API Storage to suppress CredentialsFileSymbolicLinkError
  """

  def __init__(self, filename):

    super(Storage, self).__init__(filename)
    self._filename_link_warned = False

  def _validate_file(self):

    if os.path.islink(self._filename) and not self._filename_link_warned:
      print 'File: %s is a symbolic link.' % self._filename
      self._filename_link_warned = True


# b.py stuff
############

# filename of local configuration without '.py' suffix.
BRC = 'brc'
TEMPLATE_PATH = path.join(os.getcwd(), 'tmpl.html')

# handlers for markup files
handlers = {
  'AsciiDoc': {
    'match': re.compile(r'.*\.asciidoc$'),
    'module': path.join('bpy', 'handlers', 'asciidoc'),
  },
  'HTML': {
    'match': re.compile(r'.*\.(html?|raw)$'),
    'module': path.join('bpy', 'handlers', 'html'),
  },
  'Markdown': {
    'match': re.compile(r'.*\.(markdown|md(own)?|mkdn?)$'),
    'module': path.join('bpy', 'handlers', 'mkd'),
  },
  'reStructuredText': {
    'match': re.compile(r'.*\.rst$'),
    'module': path.join('bpy', 'handlers', 'rst'),
  },
  'Text': {
    'match': re.compile(r'.*\.te?xt$'),
    'module': path.join('bpy', 'handlers', 'text'),
  },
}


def parse_args():

  p = ap.ArgumentParser()
  p.add_argument('--version', action='version',
                 version='%(prog)s ' + __version__)
  sp = p.add_subparsers(help='commands')

  pblogs = sp.add_parser('blogs', help='list blogs')
  pblogs.set_defaults(subparser=pblogs, command='blogs')

  psearch = sp.add_parser('search', help='search for posts')
  psearch.add_argument('-b', '--blog', help='Blog ID')
  psearch.add_argument('q', nargs='+', help='query text')
  psearch.set_defaults(subparser=psearch, command='search')

  pgen = sp.add_parser('generate', help='generate html')
  pgen.add_argument('filename')
  pgen.set_defaults(subparser=pgen, command='generate')

  pchk = sp.add_parser('checklink', help='check links in chkerateed html')
  pchk.add_argument('filename')
  pchk.set_defaults(subparser=pchk, command='checklink')

  ppost = sp.add_parser('post', help='post or update a blog post')
  ppost.add_argument('filename')
  ppost.set_defaults(subparser=ppost, command='post')

  args = p.parse_args()
  return args


def load_config():

  rc = None
  try:
    search_path = [os.getcwd()]
    _mod_data = imp.find_module(BRC, search_path)
    print 'Loading local configuration...'
    try:
      rc = imp.load_module(BRC, *_mod_data)
    finally:
      if _mod_data[0]:
        _mod_data[0].close()
  except ImportError:
    pass
  except Exception:
    traceback.print_exc()
    print 'Error in %s, aborted.' % _mod_data[1]
    sys.exit(1)
  return rc


def find_handler(filename):

  search_path = [os.getcwd()] + sys.path
  module = None
  for name, hdlr in handlers.items():
    if hdlr['match'].match(filename):
      try:
        _mod_data = imp.find_module(hdlr['module'], search_path)
        try:
          module = imp.load_module(name, *_mod_data)
        finally:
          if _mod_data[0]:
            _mod_data[0].close()
          if module:
            break
      except Exception:
        print 'Cannot load module %s of handler %s' % (hdlr['module'], name)
        traceback.print_exc()
  if module:
    return module.Handler(filename, hdlr.get('options', {}))
  return None


def posting(post, http, service):

  kind = post['kind'].replace('blogger#', '')
  title = post['title']

  if kind == 'post':
    posts = service.posts()
  else:
    raise ValueError('Unsupported kind: %s' % kind)

  if 'id' in post:
    print 'Updating a %s: %s' % (kind, title)
    req = posts.update(blogId=post['blog']['id'], postId=post['id'], body=post)
  else:
    print 'Posting a new %s: %s' % (kind, title)
    req = posts.insert(blogId=post['blog']['id'], body=post)

  resp = req.execute(http=http)
  return resp


def do_search(rc, args):

  http, service = get_http_service()
  posts = service.posts()
  if args.blog:
    blog_id = args.blog
  elif hasattr(rc, 'blog'):
    blog_id = rc.blog
  else:
    print >> sys.stderr, 'no blog ID to search'
    sys.exit(1)
  q = ' '.join(args.q)
  fields = 'items(labels,published,title,url)'
  req = posts.search(blogId=blog_id, q=q, fields=fields)
  resp = req.execute(http=http)
  items = resp.get('items', [])
  print 'Found %d posts on Blog %s' % (len(items), blog_id)
  print
  for post in items:
    print post['title']
    labels = post.get('labels', [])
    if labels:
      print 'Labels:', ', '.join(labels)
    print 'Published:', post['published']
    print post['url']
    print


def get_http_service():

  global http, service

  if http and service:
    return http, service

  FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
                                 scope=API_SCOPE,
                                 message=NOTFOUND_MESSAGE)

  storage = Storage(API_STORAGE)
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)

  http = httplib2.Http()
  http = credentials.authorize(http)
  service = build("blogger", "v3", http=http)

  return http, service


def main():

  args = parse_args()

  rc = load_config()
  if rc:
    if hasattr(rc, 'handlers'):
      for name, handler in rc.handlers.items():
        if name in handlers:
          handlers[name].update(handler)
        else:
          handlers[name] = handler.copy()

  if args.command == 'blogs':
    http, service = get_http_service()
    blogs = service.blogs()
    req = blogs.listByUser(userId='self')
    resp = req.execute(http=http)
    print '%-20s: %s' % ('Blog ID', 'Blog name')
    for blog in resp['items']:
      print '%-20s: %s' % (blog['id'], blog['name'])
  elif args.command == 'search':
    do_search(rc, args)
  elif args.command in ('generate', 'checklink', 'post'):
    handler = find_handler(args.filename)
    if not handler:
      print 'No handler for the file!'
      sys.exit(1)

    hdr = handler.header

    post = {
      # default resource kind is blogger#post
      'kind': 'blogger#%s' % hdr.get('kind', 'post'),
      'content': handler.generate(),
    }
    if rc:
      if hasattr(rc, 'blog'):
        post['blog'] = {'id': rc.blog}
    post.update(handler.generate_post())

    if args.command == 'generate':
      with open('/tmp/draft.html', 'w') as f:
        f.write(post['content'])

      if args.command == 'generate' and path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH) as f:
          html = f.read()
        html = html.replace('%%Title%%', post['title'])
        html = html.replace('%%Content%%', post['content'])
        with open('/tmp/preview.html', 'w') as f:
          f.write(html)
      return
    elif args.command == 'checklink':
      if not HAS_LNKCKR:
        print 'You do not have lnkckr library'
        return
      c = Checker()
      c.process(StringIO(post['content']))
      c.check()
      c.print_report()
      c.print_summary()
      return

    if 'blog' not in post:
      print ('You need to specify which blog to post on '
             'in either brc.py or header of %s.' % handler.filename)
      sys.exit(1)

    http, service = get_http_service()
    resp = posting(post, http, service)

    handler.merge_header(resp)
    handler.write()


if __name__ == '__main__':
  main()
