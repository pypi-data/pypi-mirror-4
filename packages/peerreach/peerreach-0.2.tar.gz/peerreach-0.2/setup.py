#!/usr/bin/env python
"""
   Setup script for peerreach
"""
import os
from setuptools import setup


def read(fname):
    full_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), fname)
    if os.path.exists(full_path):
        return open(full_path).read()


setup(name='peerreach',
      version="0.2",
      author='Ferran Pegueroles Forcadell',
      author_email='ferran@pegueroles.com',
      description='Access peerreach api',
      url='https://bitbucket.org/ferranp/peerreach',
      long_description=read('README.rst'),
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
      install_requires=['requests==1.1.0'],
      tests_require=['nose', 'mock', 'coverage'],
      test_suite='nose.collector',
      entry_points={
          'console_scripts': [
              'peerreach = peerreach.runner:main',
          ],
      },
)
