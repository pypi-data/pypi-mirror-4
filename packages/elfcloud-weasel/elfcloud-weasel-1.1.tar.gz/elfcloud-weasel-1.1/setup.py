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
      version = "1.1",
      description='elfCLOUD.fi Weasel',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Utilities",
        ],
      author='elfCLOUD',
      author_email='support.dev@elfcloud.fi',
      url='http://elfcloud.fi/',
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=requires,
      tests_require=requires,
      test_suite="nose.collector",
      entry_points="""\
      [console_scripts]
      ecw = elfcloud.cli:main
      """
      )
