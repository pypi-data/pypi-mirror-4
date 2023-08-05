#!/usr/bin/env python

from setuptools import setup
import spdyathome


setup(
  name = 'spdyathome',
  version = spdyathome.__version__,
  description = 'A simple script to run in order to collect data for comparing SPDY and HTTP',
  author = 'Brian Stack',
  author_email = 'bis12@case.edu',
  url = 'http://github.com/bis12/spdyathome',
  packages = ['spdyathome'],
  package_dir={'spdyathome': 'spdyathome'},
  package_data = {'spdyathome': ['conf.yaml', 'data/*']},
  provides = ['spdyathome'],
  scripts = ['scripts/spdyathome'],
  zip_safe = False,
  include_package_data = True,
  long_description = open("README").read(),
  license = 'MIT',
  install_requires = [
    'pyyaml >= 3.09',
    'thor',
    'argparse==1.2.1',
    'progress==1.0.2'
  ],
  dependency_links = ['git://github.com/bis12/thor.git@spdy#egg=thor'],
  classifiers = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
  ]
)
