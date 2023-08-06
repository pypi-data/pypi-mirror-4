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
  from io import StringIO
except:
  from StringIO import StringIO
from itertools import chain, groupby, islice, product
from lxml import etree

from lnkckr.checkers.base import Checker as BaseChecker
from lnkckr.checkers.html import Checker as HTMLChecker


class Checker(BaseChecker):

  ID = 'blogger'

  def process(self, f):
    """Process a Blogger XML Export file

    f is a file-like object.
    """
    SCHEME_KIND = "http://schemas.google.com/g/2005#kind"
    VALID_KINDS = ("http://schemas.google.com/blogger/2008/kind#post",
                   "http://schemas.google.com/blogger/2008/kind#page")
    NS = {'ns': 'http://www.w3.org/2005/Atom'}

    d = etree.parse(f)

    htmlckr = HTMLChecker()
    links = {}

    entries = d.xpath('//ns:feed/ns:entry', namespaces=NS)
    for entry in entries:
      sel = "ns:category[@scheme='%s']" % SCHEME_KIND
      kind = entry.find(sel, namespaces=NS)
      if kind.attrib.get('term') not in VALID_KINDS:
        continue
      sel = "ns:link[@rel='alternate']"
      altlink = entry.find(sel, namespaces=NS)
      if altlink is None:
        # for scheduled posts, the post URL isn't decided yet, skip such posts
        # since lnkckr wouldn't be possible to provide URL of the posts.
        continue
      post_link = altlink.attrib.get('href')

      content = entry.find('ns:content', namespaces=NS)
      content_text = content.text
      if isinstance(content_text, str) and hasattr(content_text, 'decode'):
        content_text = content_text.decode('utf8')
      htmlckr.links = {}
      htmlckr.process(StringIO(content_text))
      for link in htmlckr.links.keys():
        # is a blank fragment?
        if link == '#' or link == post_link + '#':
          continue
        # is a local fragment?
        if link.startswith('#'):
          link = post_link + link
        if link not in links:
          links[link] = {'status': None, 'posts': []}
        if post_link not in links[link]['posts']:
          links[link]['posts'].append(post_link)
    self.links = links

  ###########################
  # report output functions #
  ###########################

  def print_all(self):

    self.print_report()
    self.print_summary()
    self.print_toplist()

  # report
  #########

  def print_report_link_data(self, url, link):

    for post in link['posts']:
      print('  %s' % post)

  # summary
  ##########

  def print_summary_status(self, data):

    data2 = []
    for status, links in data:
      nlinks = sum(1 for l in links)
      nposts = len(set(chain.from_iterable(link['posts'] for link in links)))
      data2.append((status, nlinks, nposts))

    l_links = max(self.num_len(item[1]) for item in data2)
    l_posts = max(self.num_len(item[2]) for item in data2)

    for status, nlinks, nposts in data2:
      cstatus = self.color_status(status)

      print('{} {:{l_links},d} links from {:{l_posts},d} posts'.format(cstatus,
            nlinks, nposts, l_links=l_links, l_posts=l_posts))

  def print_summary_status1(self, status, links):

    nlinks = len(links)
    nposts = len(set(chain.from_iterable(link['posts'] for link in links)))
    cstatus = self.color_status(status)

    print('{} {:6,d} links from {:6,d} posts'.format(cstatus, nlinks, nposts))

  def print_summary_footer(self):

    links = self.links
    posts = set(chain.from_iterable(link['posts'] for link in links.values()))
    nposts = len(posts)

    print()
    print('TOTAL {:,} links from {:,} posts'.format(len(links), nposts))
    print()

  # toplist
  ##########

  def print_toplist(self):

    self.print_heading('toplist')

    # make list of (status, postlink) from links
    f = lambda link: link['status'] not in (None, '200', 'SCH', 'SKP')
    links = filter(f, self.links.values())
    links = (product((link['status'],), link['posts']) for link in links)
    links = chain.from_iterable(links)
    f = lambda link: link[1]
    links = groupby(sorted(links, key=f), key=f)
    links = ((post, sum(1 for _ in g)) for post, g in links)

    print('%6s %s' % ('Errors', 'Post URL'))
    for post, count in islice(sorted(links, key=f, reverse=True), 10):
      print('%6d %s' % (count, post))
    print()
