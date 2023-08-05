#!/usr/bin/env python
#------------------------------------------------------------------------------
# file: $Id: setup.py 58 2012-09-06 03:46:56Z griff1n $
# lib:  pysyncml
# auth: griffin <griffin@uberdev.org>
# date: 2012/04/20
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The egg-generating setup file for the ``pysyncml`` package.
'''

import sys, os

if sys.hexversion < 0x02060200:
  raise RuntimeError('This package requires python 2.6.2 or later')

try:
  from setuptools import setup, find_packages
except ImportError:
  from ez_setup import use_setuptools
  use_setuptools()
  from setuptools import setup, find_packages

test_packages = [
  'nose                 >= 1.1.2',
  'coverage             >= 3.5.2',
  # 'sphinx               >= 1.1.3',
  ]

install_packages = [
  'distribute           >= 0.6.10',
  'PyYAML               >= 3.10',
  'SQLAlchemy           >= 0.7.7',
  ]

if sys.hexversion < 0x02070000:
  install_packages.extend([
    'argparse           >= 1.2.1',
    ])

# installed scripts
entry_points = {
  'console_scripts': [
    # 'sync-files         = pysyncml.cli.files:main',
    'sync-notes         = pysyncml.cli.notes:main',
    ],
  }

setup(

  # generic info
  name                  = 'pysyncml',
  version               = '0.1',

  # build instructions
  package_dir           = {'': 'src'},
  packages              = find_packages('src'), #, exclude=['ext']),
  package_data          = {}, # {'': ['res/*']},
  zip_safe              = True,

  # dependencies
  install_requires      = install_packages,
  tests_require         = test_packages,

  # environment
  test_suite            = 'pysyncml',
  entry_points          = entry_points,

  # metadata for upload to PyPI
  url                   = 'http://www.pysyncml.org/',
  # these did NOT work:
  # download_url = 'http://sourceforge.net/projects/pysyncml/files/trunk/',
  # download_url = 'http://sourceforge.net/projects/pysyncml/files/latest/download?source=files',
  # download_url = 'http://sourceforge.net/projects/pysyncml/files/trunk/pysyncml-0.1.dev-r29.tar.gz/download',
  # download_url = 'http://sourceforge.net/p/pysyncml/code-0/HEAD/tree/trunk/dist/',
  # this DOES work, but hard-codes the latest release and does not give me any download stats...
  # download_url = 'http://downloads.sourceforge.net/project/pysyncml/trunk/pysyncml-0.1.dev-r29.tar.gz',
  author                = 'griffin',
  author_email          = 'griffin@uberdev.org',
  description           = 'A pure-python implementation of the SyncML adapter framework and protocol.',
  license               = 'copyloose',
  keywords              = 'syncml python synchronize mobile desktop framework adapter open mobile alliance'
                          ' contacts agenda calendar files notes',
  platforms             = ['any'],
  classifiers           = [
    'Development Status :: 4 - Beta',
    # 'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Environment :: Handhelds/PDA\'s',
    'Environment :: Web Environment',
    'Environment :: Win32 (MS Windows)',
    'Environment :: X11 Applications',
    'Intended Audience :: Developers',
    'License :: Public Domain',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet',
    'Topic :: Other/Nonlisted Topic',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: System :: Distributed Computing',
    'Topic :: System :: Filesystems',
    'Topic :: Utilities',
  ],

  # todo: pull in a changelog from subversion?...
  long_description      = open(os.path.join(os.path.dirname(__file__), 'README.txt'), 'rb').read(),

)

#------------------------------------------------------------------------------
# end of $Id: setup.py 58 2012-09-06 03:46:56Z griff1n $
#------------------------------------------------------------------------------
