#!/usr/bin/env python3
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

from distutils.core import Command, setup
from unittest import TestLoader, TextTestRunner
import sys

# scripts to be exculded from checking
EXCLUDE_SCRIPTS = ()

library_name = 'lnkckr'
script_name = 'linkcheck'

# ============================================================================


class cmd_test(Command):

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


class cmd_pep8(Command):

  description = 'run pep8'
  user_options = []

  def initialize_options(self):

    pass

  def finalize_options(self):

    pass

  def run(self):

    try:
      import pep8
    except ImportError:
      print('Cannot import pep8, you forgot to install?\n'
            'run `pip install pep8` to install.', file=sys.stderr)
      sys.exit(1)

    p8 = pep8.StyleGuide()

    # do not include code not written in b.py
    p8.options.exclude += EXCLUDE_SCRIPTS
    # ignore four-space indentation error
    p8.options.ignore += ('E111', 'E121')

    print()
    print('Options')
    print('=======')
    print()
    print('Exclude:', p8.options.exclude)
    print('Ignore :', p8.options.ignore)

    print()
    print('Results')
    print('=======')
    print()
    report = p8.check_files('.')

    print()
    print('Statistics')
    print('==========')
    print()
    report.print_statistics()
    print('%-7d Total errors and warnings' % report.get_count())


class cmd_pyflakes(Command):

  description = 'run Pyflakes'
  user_options = []

  def initialize_options(self):

    pass

  def finalize_options(self):

    pass

  def run(self):

    try:
      from pyflakes import api
      from pyflakes import reporter as modReporter
    except ImportError:
      print('Cannot import pyflakes, you forgot to install?\n'
            'run `pip install pyflakes` to install.', file=sys.stderr)
      sys.exit(1)

    from os.path import basename

    reporter = modReporter._makeDefaultReporter()

    # monkey patch for exclusion of pathes
    api_iterSourceCode = api.iterSourceCode

    def _iterSourceCode(paths):
      for path in api_iterSourceCode(paths):
        if basename(path) not in EXCLUDE_SCRIPTS:
          yield path
    api.iterSourceCode = _iterSourceCode

    print()
    print('Options')
    print('=======')
    print()
    print('Exclude:', EXCLUDE_SCRIPTS)

    print()
    print('Results')
    print('=======')
    print()
    warnings = api.checkRecursive('.', reporter)
    print()
    print('Total warnings: %d' % warnings)


class cmd_pylint(Command):

  description = 'run Pylint'
  user_options = []

  def initialize_options(self):

    pass

  def finalize_options(self):

    pass

  def run(self):

    from glob import glob
    try:
      from pylint import lint
    except ImportError:
      print('Cannot import pylint, you forgot to install?\n'
            'run `pip install pylint` to install.', file=sys.stderr)
      sys.exit(1)

    print()
    print('Options')
    print('=======')
    print()
    print('Exclude:', EXCLUDE_SCRIPTS)

    files = ['setup.py', script_name, 'lnkckr'] + glob('tests/*.py')
    args = [
      '--ignore=%s' % ','.join(EXCLUDE_SCRIPTS),
      '--output-format=colorized',
      '--include-ids=y',
      '--indent-string="  "',
    ] + files
    print()
    lint.Run(args)

# ============================================================================

with open(library_name + '/__init__.py') as f:
  meta = dict(
    (k.strip(' _'), eval(v)) for k, v in
      # There will be a '\n', with eval(), it's safe to ignore
      (line.split('=') for line in f if line.startswith('__'))
  )

  # renaming meta-data keys
  meta_renames = [
    ('library', 'name'),
    ('website', 'url'),
    ('email', 'author_email'),
  ]
  for old, new in meta_renames:
    if old in meta:
      meta[new] = meta[old]
      del meta[old]

  # keep these
  meta_keys = ['name', 'description', 'version', 'license', 'url', 'author',
               'author_email']
  meta = dict(filter(lambda m: m[0] in meta_keys, meta.items()))

classifiers = [
  'Development Status :: 3 - Alpha',
  'Environment :: Console',
  'Intended Audience :: End Users/Desktop',
  'License :: OSI Approved :: MIT License',
  'Natural Language :: English',
  'Operating System :: POSIX :: Linux',
  'Programming Language :: Python :: 2.7',
  'Programming Language :: Python :: 3',
  'Topic :: Other/Nonlisted Topic',
]

packages = [
  'lnkckr',
  'lnkckr.checkers',
]

setup_d = dict(
  cmdclass={
    'pep8': cmd_pep8,
    'pyflakes': cmd_pyflakes,
    'pylint': cmd_pylint,
    'test': cmd_test,
  },
  classifiers=classifiers,
  scripts=[script_name],
  packages=packages,
  **meta
)

if __name__ == '__main__':
  setup(**setup_d)
