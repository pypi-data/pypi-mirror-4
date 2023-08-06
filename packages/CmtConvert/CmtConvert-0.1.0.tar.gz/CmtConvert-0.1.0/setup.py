#! /usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup


setup(name='CmtConvert',
      version='0.1.0',
      author='Eric Hutton',
      author_email='eric.hutton@colorado.edu',
      url='https://csdms.colorado.edu/trac/csdms',
      description='Plugin-based file format converter',
      long_description=open ('README.txt').read (),
      packages=['cmt_convert', 'cmt_convert.plugins', 'cmt_convert.tests'],
      entry_points={
          'console_scripts': ['map = cmt_convert.map:main',
                              'convert = cmt_convert.convert:main']
      },
      test_suite='cmt_convert.tests',
     )
