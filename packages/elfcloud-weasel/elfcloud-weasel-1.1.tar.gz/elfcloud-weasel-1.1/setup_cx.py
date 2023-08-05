import os
import sys
from setuptools import find_packages
from cx_Freeze import setup, Executable

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

build_exe_options = {"packages": ["os", "Crypto"],
                     "excludes": ['elfcloud.tests', 'unittest']}

requires = ['decorator',
            'pycrypto',
]

test_requires = [
  'mock',
  'nose',
]

targetName = "ecw"
if sys.platform == "win32":
    targetName = "ecw.exe"

base = None
setup(name='elfcloud-weasel',
      version="1.1",
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
      test_suite="elfcloud",
      entry_points="""\
      [console_scripts]
      ecw = elfcloud.cli:main
      """,
      options={"build_exe": build_exe_options},
      executables=[Executable(os.path.join("elfcloud", "cli", "__init__.py"),
                        base=base,
                        copyDependentFiles=True,
                        targetName=targetName,
                        icon="icon.ico",
                        compress=True,
                        appendScriptToExe=True,
                        appendScriptToLibrary=True,
                        )]
      )
