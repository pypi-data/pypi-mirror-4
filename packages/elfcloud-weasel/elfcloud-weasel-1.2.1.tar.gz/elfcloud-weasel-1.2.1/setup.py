# -*- coding: utf-8 -*-
__license__ = """
Copyright 2010-2012 elfCLOUD / elfcloud.fi – SCIS Secure Cloud Infrastructure Services

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = ['decorator',
            'pycrypto',
            'argparse',
]

test_requires = [
  'mock',
  'nose',
  'unittest2'
]

setup(name='elfcloud-weasel',
      version="1.2.1",
      description='elfcloud.fi Weasel',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Environment :: Console"
        ],
      author='elfcloud',
      author_email='support.dev@elfcloud.fi',
      url='https://elfcloud.fi/',
      license=open('LICENSE.txt').read(),
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      package_data={'elfcloud': [
          'README.txt',
          'LICENSE.txt',
          'NOTICE.txt',
          'CHANGES.txt',
        ]},
      zip_safe=True,
      install_requires=requires,
      tests_require=requires,
      test_suite="nose.collector",
      entry_points="""\
      [console_scripts]
      ecw = elfcloud.cli:main
      """
      )
