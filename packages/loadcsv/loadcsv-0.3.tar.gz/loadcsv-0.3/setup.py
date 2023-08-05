#!/usr/bin/env python
"""
   Setup script for loadcsv.
"""
#from distutils.core import setup
from distutils.core import setup
import os
README = os.path.join(os.path.dirname(__file__), 'README.txt')

LONG_DESCRIPTION = open(README).read() + '\n\n'

setup(name='loadcsv',
      version='0.3',
      author='Ferran Pegueroles Forcadell',
      author_email='ferran@pegueroles.com',
      description='Load a csv file into a database',
      url='https://bitbucket.org/ferranp/loadcsv',
      long_description=LONG_DESCRIPTION,
      license='GPL',
      platforms='linux,windows',
      download_url='https://bitbucket.org/ferranp/loadcsv/downloads',
      packages=[],
      py_modules=['loadcsv'],
      scripts=["loadcsv"],
      data_files=[],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Topic :: Database',
          'Topic :: Utilities',
          'Topic :: Text Processing',
          ],
      )
