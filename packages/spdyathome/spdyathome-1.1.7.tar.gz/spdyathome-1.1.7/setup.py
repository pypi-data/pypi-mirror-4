#!/usr/bin/env python

from setuptools import setup


setup(
  name = 'spdyathome',
  version = '1.1.7',
  description = 'A simple script to run in order to collect data for comparing SPDY and HTTP',
  author = 'Brian Stack',
  author_email = 'bis12@case.edu',
  url = 'http://github.com/bis12/spdyathome',
  packages = ['spdyathome'],
  provides = ['spdyathome'],
  scripts = ['scripts/spdyathome'],
  zip_safe = False,
  long_description = open("README").read(),
  license = 'MIT',
  install_requires = [
    'thor-spdy',
    'argparse == 1.2.1',
    'progress == 1.0.2'
  ],
  dependency_links = ['git://github.com/bis12/thor.git@spdy#egg=thor-spdy'],
  classifiers = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
  ]
)
