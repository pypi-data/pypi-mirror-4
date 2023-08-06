# This file is part of longtang.
# Copyright 2013, Guillermo Szeliga.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

import os
from setuptools import setup, find_packages

setup(name='longtang',
      version='1.0.0',
      description=
        'Audio collection id3tag tagger and organizer',
      author='Guillermo Szeliga',
      author_email='gszeliga@gmail.com',
      url='https://bitbucket.org/gszeliga/longtang',
      download_url='',
      license='MIT',
      platforms='ALL',
      long_description=open('README.md', 'rt').read(),
      install_requires = ['pyacoustid','gevent','nose','PyHamcrest', 'mutagen','argparse'],
      packages=find_packages(),
      scripts=['bin/longtang'],
      test_suite = 'nose.collector',
      #test_suite = "longtang.test.test_all",
      classifiers=[
		  'Development Status :: 6 - Mature',
		  'Environment :: Console',
		  'Intended Audience :: End Users/Desktop',
		  'Operating System :: Unix',
		  'Programming Language :: Python :: 2.7',
		  'Topic :: Multimedia :: Sound/Audio',
          'Topic :: Multimedia :: Sound/Audio :: Conversion',
          'Topic :: Multimedia :: Sound/Audio :: Editors',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities'
      ],
)
