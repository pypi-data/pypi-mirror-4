#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

from setuptools import setup, find_packages

if sys.version_info[:2] < (2, 5):
    raise Exception('This version of srtmerge needs Python 2.5 or later. ')

if sys.argv[-1] in ("submit", "publish"):
    os.system("python setup.py bdist_egg sdist --format=zip upload")
    os.system("python2.6 setup.py bdist_egg upload")
    sys.exit()

README = ''
try:
    f = open('README')
    README = f.read()
    f.close()
except:
    pass

setup(name='srtmerge',
      version='0.5',
      author='wistful',
      author_email='wst.public.mail@gmail.com',
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      description="srtmerge (.srt) used to merge two Srt files",
      long_description=README,
      url="https://github.com/wistful/srtmerge",
      license="LGPL",
      platforms=["Unix,"],
      keywords="srtmerge, srt, subtitle",
      test_suite='tests',
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 2",
          "Topic :: Text Processing",
          "Topic :: Utilities"
      ],
      entry_points={
      'console_scripts': [
          'srtmerge = srtmerge.srtmerge:main'
      ]},
      )
