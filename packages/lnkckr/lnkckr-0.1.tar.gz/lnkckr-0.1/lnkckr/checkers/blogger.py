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


try:
  from io import StringIO
except:
  from StringIO import StringIO
from itertools import chain
from lxml import etree

from lnkckr.checkers.base import Checker as BaseChecker
from lnkckr.checkers.html import Checker as HTMLChecker


class Checker(BaseChecker):

  ID = 'blogger'

  def process(self, f):
    """Process a Blogger XML Export file"""
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
      post_link = entry.find(sel, namespaces=NS).attrib.get('href')

      content = entry.find('ns:content', namespaces=NS)
      content_text = content.text
      if isinstance(content_text, str) and hasattr(content_text, 'decode'):
        content_text = content_text.decode('utf8')
      htmlckr.links = {}
      htmlckr.process(StringIO(content_text))
      for link in htmlckr.links.keys():
        if link not in links:
          links[link] = {'status': None, 'posts': []}
        if post_link not in links[link]['posts']:
          links[link]['posts'].append(post_link)
    self.links = links

  # =====

  def print_report_link_data(self, url, link):

    for post in link['posts']:
      print('  %s' % post)
    print()

  # -----

  def print_summary_status(self, status, links):

    nlinks = len(links)
    nposts = len(set(chain.from_iterable(link['posts'] for link in links)))
    cstatus = self.color_status(status)

    print('%s %5d links from %5d posts' % (cstatus, nlinks, nposts))
