#!/usr/bin/env python

import sys

if sys.version_info < (2, 6):
      sys.stderr.write('Please install (and use) Python2.6, or greater, to run setup.py.\n')
      sys.exit(1)

try:
      from setuptools import setup
except:
      from distutils.core import setup

setup(name='python-bashcomplete',
      version='1.0-1',
      description='bashcomplete creation from python lists and dictionaries.',
      long_description=open('README.md').read(),
      author='Joaquin Casares',
      author_email='joaquin.casares AT gmail.com',
      url='http://www.github.com/joaquincasares/python-bashcomplete',
      download_url="https://github.com/joaquincasares/python-bashcomplete/zipball/master",
      py_modules=['bashcomplete'],
      package_data={'': ['README.md']},
      keywords="python bashcomplete bash complete generation generate convert converter"
     )
