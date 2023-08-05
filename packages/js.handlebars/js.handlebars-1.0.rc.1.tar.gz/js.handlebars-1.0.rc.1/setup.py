#!/usr/bin/python

import setuptools
from setuptools import find_packages

setuptools.setup(
  name = 'js.handlebars',
  version = '1.0.rc.1',
  license = 'BSD',
  description = 'Fanstatic package for Handlebars.js',
  long_description = open('README.txt').read(),
  author = 'Matt Good',
  author_email = 'matt@matt-good.net',
  url = 'http://github.com/mgood/js.handlebars/',
  platforms = 'any',
  packages=find_packages(),
  namespace_packages=['js'],
  zip_safe = False,
  install_requires=[
    'fanstatic',
  ],
  entry_points={
    'fanstatic.libraries': [
      'handlebars = js.handlebars:library',
    ],
  },
)
