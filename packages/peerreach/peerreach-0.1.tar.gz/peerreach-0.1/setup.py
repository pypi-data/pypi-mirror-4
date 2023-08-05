#!/usr/bin/env python
"""
   Setup script for peerreach
"""
import os
from setuptools import setup
from peerreach import __version__

README = os.path.join(os.path.dirname(__file__), 'README.txt')

LONG_DESCRIPTION = open(README).read() + '\n\n'

setup(name='peerreach',
      version=__version__,
      author='Ferran Pegueroles Forcadell',
      author_email='ferran@pegueroles.com',
      description='Access peerreach api',
      url='https://bitbucket.org/ferranp/peerreach',
      long_description=LONG_DESCRIPTION,
      license='GPL',
      download_url='https://bitbucket.org/ferranp/loadcsv/downloads',
      packages=['peerreach'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Topic :: Internet',
          'Topic :: Utilities',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries',
          ],
      install_requires=['requests'],
      tests_require=['nose', 'mock', 'coverage'],
      test_suite='nose.collector',
      entry_points={
          'console_scripts': [
              'peerreach = peerreach.runner:main',
          ],
      },
)
