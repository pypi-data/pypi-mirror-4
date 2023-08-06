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
from itertools import groupby, product
import json
from multiprocessing import Manager, Process, Queue, Value
from os import path
try:
  from queue import Empty, Full
except ImportError:
  from Queue import Empty, Full
import re
import socket
import traceback
try:
  from urllib.parse import quote, urldefrag, urljoin, urlparse
except ImportError:
  from urllib import quote
  from urlparse import urldefrag, urljoin, urlparse
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

  def __init__(self):

    self.data = {}
    self.links = {}
    self.json_filename = None

  def load(self, src=None, jsonsrc=None, do_update=False, update_status=False):
    """Load links from a file

    src can be a URL (starting with http), file-like object, or a filename.
    jsonsrc can be a file-like or a filename.

    "src.json" may be saved if src is a file and jsonsrc isn't a file.

    do_update will update the JSON.

    The file format depends how self.process() is implemented."""
    if jsonsrc:
      self.json_filename = self.load_json(jsonsrc)
      if not do_update:
        return
      json_links = self.links

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
        if not self.json_filename:
          self.json_filename = src + '.json'
          if not do_update and path.exists(self.json_filename):
            self.load_json(self.json_filename)
            return
        f = open(src, 'r')

      self.process(f)
    finally:
      if f:
        f.close()

    if jsonsrc and do_update:
      file_links = self.links
      self.links = json_links
      self.update_links(file_links, update_status)

  def process(self, data):
    """Process the data from load()"""
    pass

  def load_json(self, src):
    """Load data and links from a JSON file

    src can be a filename or file-like object.

    returns src only if it's file and load successfully.
    """
    filename = None
    if hasattr(src, 'read'):
      jsondata = json.load(src)
      src.close()
    else:
      with open(src, 'r') as f:
        jsondata = json.load(f)
        filename = src

    # version <= 0.1.1
    if 'data' not in jsondata or 'links' not in jsondata:
      self.links = jsondata
    else:
      self.data = jsondata['data']
      self.links = jsondata['links']

    return filename

  def save_json(self, dest):
    """Save data and links to a JSON file

    dest can be a filename or a file-like object, will not be closed by
    save_json if it's a file-like object.
    """
    jsondata = {'data': self.data, 'links': self.links}
    if hasattr(dest, 'write'):
      json.dump(jsondata, dest)
      return

    with open(dest, 'w') as f:
      json.dump(jsondata, f)

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
    # skip blank fragment
    if url == '#':
      return
    d = {'status': None}
    d.update(data or {})
    self.links.update({url: d})

  def update_links(self, links, update_status=False):
    """Update self.links with links"""
    urls = set(self.links.keys())
    nurls = set(links.keys())

    # remove removed links
    for url in urls - nurls:
      del self.links[url]
    # add new links
    for url in nurls - urls:
      self.links[url] = links[url]
    # update links
    for url in urls & nurls:
      self.update_link(url, links[url], update_status)

  def update_link(self, url, new_link, update_status=False):
    """Update self.links[url] with new_link

    >>> c = Checker()
    >>> url = 'http://example.com/'
    >>> c.add_link(url)
    >>> new_link = {'status': 123, 'foobar': 'blah'}
    >>> c.update_link(url, new_link)
    >>> c.links[url]
    {'status': None, 'foobar': 'blah'}
    >>> new_link['foobar'] = 'duh'
    >>> c.update_link(url, new_link, update_status=True)
    >>> c.links[url]
    {'status': 123, 'foobar': 'duh'}
    """
    link = self.links[url]
    status = link['status']
    link.update(new_link)
    if not update_status:
      link['status'] = status

  # =====

  # http://www.w3.org/TR/html-markup/syntax.html#syntax-attributes
  RE_ID_NAME = re.compile(r'\b(?:id|name) *= *'
                          r'(?:(?P<q>[\'"])(.+?)(?P=q)|([^"\'=><`]+))', re.I)

  def _check_url_frag(self, data):
    """search for fragment in HTML attributes id or name look-likes

    return '200' if found else '###'

    >>> c = Checker()
    >>> f = c._check_url_frag
    >>> f(('', 'blah'))
    '200'
    >>> f(('foo', 'id=foo'))
    '200'
    >>> f(('foo', 'id="foo"'))
    '200'
    >>> f(('foo', 'id="nofoo"'))
    '###'
    >>> f(('bar', 'name=bar'))
    '200'
    >>> f(('bar', 'name="bar"'))
    '200'
    """
    frag, body = data
    if frag == '':
      return '200'
    for m in self.RE_ID_NAME.finditer(body):
      if frag == m.group(2) or m.group(3):
        return '200'
    return '###'

  def check_url(self, url, frags=None, local_html=None):
    """Check a url

    Returns (final status code(s) in tuple of string, final redirect url)

    >>> c = Checker()
    >>> c.check_url('http://example.com') # doctest: +SKIP
    (('200',), 'http://www.iana.org/domains/example')
    """
    MAX_REDIRS = 10
    redirs = 0
    method = 'HEAD'
    start_url = url
    status = ''
    statuses = []

    while not status:
      if url.startswith('//'):
        url = 'http:' + url
      url_comp = urlparse(url)
      if url_comp.scheme == 'http':
        conn = HTTPConnection(url_comp.netloc)
      elif url_comp.scheme == 'https':
        conn = HTTPSConnection(url_comp.netloc)
      else:
        if not url and frags and local_html:
          pairs = product(frags, (local_html,))
          statuses = tuple(map(self._check_url_frag, pairs))
          break
        status = 'SCH'
        if url_comp.scheme in ('about', 'javascript'):
          status = 'SKP'
        break

      try:
        p = url_comp.path
        if url_comp.query:
          p += '?' + url_comp.query
        if frags:
          method = 'GET'
        conn.request(method, quote(p), headers=self.HEADERS)
        resp = conn.getresponse()
        if resp.status == 200 and frags != ('',):
          # any non text/html result ### as such fragment isn't found
          if not resp.getheader('Content-Type', '').startswith('text/html'):
            status = '###'
            break
          # assume characters in fragment are valid ASCII
          rbody = resp.read().decode('ascii', 'ignore')
          pairs = product(frags, (rbody,))
          statuses = tuple(map(self._check_url_frag, pairs))
          break
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
    if not statuses:
      statuses = (status,)*len(frags)
    return statuses, url

  def check_worker(self, q, r, running, data):

    local_html = data.get('local_html', '')
    try:
      while not q.empty() or running.value:
        try:
          url, frags = q.get(timeout=0.01)
          statuses, rurl = self.check_url(url, frags, local_html=local_html)
          for frag, status in zip(frags, statuses):
            data = (url + '#' + frag if frag else url, (status, rurl))
            while data:
              try:
                r.put(data, False, 0.01)
                data = None
              except Full:
                pass
          continue
        except Empty:
          pass
    except KeyboardInterrupt:
      pass

  def check_update_links(self, r):

    while not r.empty():
      url, data = r.get(block=False)
      link = self.links[url]
      status, final_url = data
      link['status'] = status
      link['redirection'] = final_url
      self.do_update(url, link)
      return True

  def _check_groupby(self, urls):
    """Generator to group by parts of url without the fragment

    The fragments will collected as a tuple.

    >>> c = Checker()
    >>> urls = ['http://example.com']
    >>> list(c._check_groupby(urls))
    [('http://example.com', ('',))]
    >>> urls = [
    ...   'http://example.com',
    ...   'http://example.com/foo#bar1',
    ...   'http://example.com/foo#bar2',
    ...   'http://example.com/foobar',
    ...   'http://example.com/foobar#blah',
    ... ]
    >>> list(c._check_groupby(urls)) # doctest: +NORMALIZE_WHITESPACE
    [('http://example.com', ('',)),
     ('http://example.com/foo', ('bar1', 'bar2')),
     ('http://example.com/foobar', ('', 'blah'))]
    >>> urls = ['#foo1', '#foo2']
    >>> list(c._check_groupby(urls))
    [('', ('foo1', 'foo2'))]
    """
    key = lambda item: item[0]
    for url, g in groupby(sorted(map(urldefrag, urls), key=key), key):
      yield url, tuple(item[1] for item in g)

  def check(self, f=None):
    """Check links

    f is a function for passing to filter function to filter links with
    argument (url, link).
    """
    default_timeout = socket.getdefaulttimeout()
    q = Queue(self.QUEUE_SIZE)
    r = Queue(self.QUEUE_SIZE)
    running = Value('b', 1)
    workers = []
    manager = Manager()
    datadict = manager.dict(self.data)
    for i in range(self.MAX_WORKERS):
      worker = Process(name='checker #%d' % i,
                       target=self.check_worker,
                       args=(q, r, running, datadict))
      worker.start()
      workers.append(worker)

    total = 0
    count = 0
    try:
      if f is None:
        f = lambda item: item[1]['status'] is None
      urls = (item[0] for item in filter(f, self.links.items()))
      gurls = self._check_groupby(urls)
      for idx, item in enumerate(gurls, start=1):
        total += 1 if not item[1] else len(item[1])
        while item:
          try:
            q.put(item, False, 0.01)
            item = None
          except Full:
            count += 1 if self.check_update_links(r) else 0
        count += 1 if self.check_update_links(r) else 0
        if count % self.SAVE_INT == 0:
          self.do_save()
      while count < total:
        count += 1 if self.check_update_links(r) else 0
        if count % self.SAVE_INT == 0:
          self.do_save()
    except KeyboardInterrupt:
      pass

    running.value = 0
    for worker in workers:
      worker.join()
    self.check_update_links(r)
    self.do_save()
    socket.setdefaulttimeout(default_timeout)

  def do_update(self, url, link):
    """Call by update_links when a link is updated"""
    self.format_status(url, link)

  def do_save(self):
    """Call by check for saving JSON when necessary"""
    if self.json_filename:
      self.save_json(self.json_filename)

  ###########################
  # report output functions #
  ###########################

  def color_status(self, status):

    if status == '000':
      return '\033[1;36m[%s]\033[0m' % status
    if status == '200':
      return '\033[1;32m[%s]\033[0m' % status
    if status in ('SKP', 'SCH'):
      return '\033[1;33m[%s]\033[0m' % status
    else:
      return '\033[1;31m[%s]\033[0m' % status

  def format_status(self, url, link):

    status = link['status']
    redir = link['redirection']
    print('%s %s' % (self.color_status(status), url), end='')
    if redir:
      print(' \033[1;33m\n   ->\033[0m %s' % redir, end='')
    print()

  def num_len(self, n):
    """Return length of n in string including thousands separator

    >>> c = Checker()
    >>> c.num_len(123)
    3
    >>> c.num_len(1234)
    5
    """
    return len('{:,d}'.format(n))

  def print_heading(self, text):

    bar = '{0:{f}^{l}s}'.format('', f='=', l=len(text) + 4)
    print('{0}\n= {1} =\n{0}\n'.format(bar, text))

  def print_all(self):

    self.print_report()
    self.print_summary()

  # report
  #########

  def print_report(self):

    self.print_heading('report')

    links = self.links

    unchecked = 0
    key = lambda item: item[1]['status'] or '---'
    for status, g in groupby(sorted(links.items(), key=key), key=key):
      if status == '---':
        unchecked = len(list(g))
        continue
      for url, link in sorted(g):
        self.print_report_link(url, link)
    if unchecked:
      print('*** checking process is not finished, '
            '%d links have not been checked. ***' % unchecked)
    print()

  def print_report_link(self, url, link):

    if link['status'] in (None, '200', 'SCH', 'SKP'):
      return
    self.format_status(url, link)
    self.print_report_link_data(url, link)

  def print_report_link_data(self, url, link):

    pass

  # summary
  ##########

  def print_summary(self):

    self.print_heading('summary')

    key = lambda link: link['status'] or '---'
    data = []
    for status, g in groupby(sorted(self.links.values(), key=key), key=key):
      data.append((status, list(g)))
    self.print_summary_status(data)
    self.print_summary_footer()

  def print_summary_status(self, data):

    data2 = []
    for status, links in data:
      nlinks = sum(1 for l in links)
      data2.append((status, nlinks))

    l = max(self.num_len(item[1]) for item in data2)

    for status, nlinks in data2:
      print('{} {:{l},d} links'.format(self.color_status(status), nlinks, l=l))

  def print_summary_footer(self):

    print()
    print('TOTAL {:,} links'.format(len(self.links)))
    print()
