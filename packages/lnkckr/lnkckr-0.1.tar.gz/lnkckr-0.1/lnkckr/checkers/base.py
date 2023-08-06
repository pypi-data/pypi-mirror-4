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


from __future__ import print_function
try:
  from http.client import HTTPConnection, HTTPSConnection
except ImportError:
  from httplib import HTTPConnection, HTTPSConnection
from itertools import groupby
import json
from multiprocessing import Process, Queue, Value
from os import path
try:
  from queue import Empty
except ImportError:
  from Queue import Empty
import socket
import traceback
try:
  from urllib.parse import urljoin, urlparse
except ImportError:
  from urlparse import urljoin, urlparse
try:
  from urllib.request import urlopen
except ImportError:
  from urllib import urlopen

import lnkckr


class Checker():
  """Base checker"""
  ID = None

  MAX_WORKERS = 10
  QUEUE_SIZE = 20
  SAVE_INT = 100

  # User-Agent for some website like Wikipedia. Without it, most of requests
  # result in 403.
  HEADERS = {'User-Agent': '%s/%s' % (lnkckr.__name__, lnkckr.__version__)}

  def __init__(self, src=None, jsonsrc=None):

    self.links = {}
    self.json_filename = None
    self.load(src, jsonsrc)

  def load(self, src=None, jsonsrc=None):
    """Load links from a file

    src can be a URL (starting with http), file-like object, or a filename.

    jsonsrc can be a file-like or a filename. jsonsrc is saved at
    self.json_filename for save function if it's a filename and can be loaded
    successfully.

    jsonsrc processes first, it updates self.links and returns if something
    comes from jsonsrc. If not then process with src, then if src + '.json'
    exists, then load() will be called by itself with that filename.

    The file format depends how self.process() is implemented."""
    if jsonsrc:
      self.json_filename = self.load_json(jsonsrc)
      if self.json_filename:
        return

    if not src:
      return

    f = None
    try:
      if hasattr(src, 'startswith') and (src.startswith('http://') or
                                         src.startswith('https://')):
        f = urlopen(src)
      elif hasattr(src, 'read'):
        f = src
      else:
        self.json_filename = src + '.json'
        if path.exists(self.json_filename):
          self.load(None, src + '.json')
          return
        f = open(src, 'r')

      self.process(f)
    finally:
      if f:
        f.close()

  def process(self, data):
    """Process the data from load()"""
    pass

  def load_json(self, src):
    """Load links from a JSON file

    src can be a filename or file-like object.

    returns src only if it's file and load successfully.
    """
    if hasattr(src, 'read'):
      self.links = json.load(src)
      src.close()
      return

    with open(src, 'r') as f:
      self.links = json.load(f)
      return src

  def save_json(self, dest):
    """Save links to a JSON file

    dest can be a filename or a file-like object, will not be closed by
    save_json if it's a file-like object.
    """
    if hasattr(dest, 'write'):
      json.dump(self.links, dest)
      return

    with open(dest, 'w') as f:
      json.dump(self.links, f)

  def add_link(self, url, data=None):
    """Add a link

    If the link already exists, it will be replaced.

    >>> c = Checker()
    >>> c.add_link('http://example.com')
    >>> c.links
    {'http://example.com': {'status': None}}
    >>> c.add_link('http://example.com', {'data': 'foobar'})
    >>> c.links
    {'http://example.com': {'status': None, 'data': 'foobar'}}
    """
    d = {'status': None}
    d.update(data or {})
    self.links.update({url: d})

  def check_url(self, url):
    """Check a url

    Returns (final status code in string, final redirection url)

    >>> c = Checker()
    >>> c.check_url('http://example.com') # doctest: +SKIP
    ('200', 'http://www.iana.org/domains/example')
    """
    MAX_REDIRS = 10
    redirs = 0
    method = 'HEAD'
    start_url = url
    status = ''

    while not status:
      if url.startswith('//'):
        url = 'http:' + url
      url_comp = urlparse(url)
      if url_comp.scheme == 'http':
        conn = HTTPConnection(url_comp.netloc)
      elif url_comp.scheme == 'https':
        conn = HTTPSConnection(url_comp.netloc)
      else:
        status = 'SCH'
        if url_comp.scheme in ('about', 'javascript'):
          status = 'SKP'
        break

      try:
        p = url_comp.path
        if url_comp.query:
          p += '?' + url_comp.query
        if url_comp.fragment:
          method = 'GET'
        conn.request(method, p, headers=self.HEADERS)
        resp = conn.getresponse()
        if resp.status == 200 and url_comp.fragment:
          rbody = resp.read().decode('utf8')
          if 'id="%s"' % url_comp.fragment in rbody:
            status = '200'
          elif "id='%s'" % url_comp.fragment in rbody:
            status = '200'
          else:
            status = '###'
        elif 300 <= resp.status < 400:
          if redirs >= MAX_REDIRS:
            status = 'RRR'
          else:
            redirs += 1
            url = urljoin(url, resp.getheader('location'))
            method = 'HEAD'
        elif resp.status == 405 and method == 'HEAD':
          method = 'GET'
        else:
          status = str(resp.status)
        conn.close()
      except socket.error:
        status = '000'
      except Exception:
        traceback.print_exc()
        status = 'XXX'

    if start_url == url and not redirs:
      url = None
    return status, url

  def check_worker(self, q, r, running):

    try:
      while not q.empty() or running.value:
        try:
          url = q.get(timeout=0.01)
          r.put((url, self.check_url(url)))
        except Empty:
          pass
    except KeyboardInterrupt:
      pass

  def update_links(self, r):

    while not r.empty():
      url, data = r.get(block=False)
      link = self.links[url]
      status, final_url = data
      link['status'] = status
      link['redirection'] = final_url
      self.do_update(url, link)

  def check(self, f=None):
    """Check links

    f is a function for passing to filter function to filter links with
    argument (url, link).
    """
    default_timeout = socket.getdefaulttimeout()
    q = Queue(self.QUEUE_SIZE)
    r = Queue(self.QUEUE_SIZE*2)
    running = Value('b', 1)
    workers = []
    for i in range(self.MAX_WORKERS):
      worker = Process(name='checker #%d' % i,
                       target=self.check_worker,
                       args=(q, r, running))
      worker.start()
      workers.append(worker)

    try:
      if f is None:
        f = lambda item: item[1]['status'] is None
      for idx, item in enumerate(filter(f, self.links.items()), start=1):
        q.put(item[0])
        self.update_links(r)
        if idx % self.SAVE_INT == 0:
          self.do_save()
      self.update_links(r)
    except KeyboardInterrupt:
      pass

    running.value = 0
    for worker in workers:
      worker.join()
    self.update_links(r)
    self.do_save()
    socket.setdefaulttimeout(default_timeout)

  def do_update(self, url, link):
    """Call by update_links when a link is updated"""
    self.format_status(url, link)

  def do_save(self):
    """Call by check for saving JSON when necessary"""
    if self.json_filename:
      self.save_json(self.json_filename)

  # =====

  def color_status(self, status):

    if status == '000':
      return '\033[1;36m[%s]\033[0m' % status
    if status == '200':
      return '\033[1;32m[%s]\033[0m' % status
    if status == 'SKP':
      return '\033[1;33m[%s]\033[0m' % status
    else:
      return '\033[1;31m[%s]\033[0m' % status

  def format_status(self, url, link):

    status = link['status']
    redir = link['redirection']
    print('%s %s' % (self.color_status(status), url), end='')
    if redir:
      print(' \033[1;33m->\033[0m %s' % redir, end='')
    print()

  def print_report(self):

    print('==========')
    print('* report *')
    print('==========')
    print()

    links = self.links
    for url, link in links.items():
      self.print_report_link(url, link)

    unchecked = sum(1 for link in links.values() if link['status'] is None)
    if unchecked:
      print('*** checking process is not finished, '
            '%d links have not been checked. ***' % unchecked)
    print()

  def print_report_link(self, url, link):

    status = link['status']
    if status in (None, '200', 'SKP'):
      return
    self.format_status(url, link)
    self.print_report_link_data(url, link)

  def print_report_link_data(self, url, link):

    pass

  # -----

  def print_summary(self):

    print('===========')
    print('* summary *')
    print('===========')
    print()

    key = lambda link: link['status'] or '---'
    for status, g in groupby(sorted(self.links.values(), key=key), key=key):
      links = list(g)
      self.print_summary_status(status, links)
    print()

  def print_summary_status(self, status, links):

    nlinks = len(links)
    print('%s %5d links' % (self.color_status(status), nlinks))
