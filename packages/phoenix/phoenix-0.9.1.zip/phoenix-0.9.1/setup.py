#!/usr/bin/env python

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

setup(name='phoenix',
      version='0.9.1',
      description='MUS Interface for Phoenix Emulator 3.x',
      author='Bui',
      author_email='bui@bui.pm',
      url='https://pypi.python.org/pypi/phoenix',
      packages=['phoenix'],
      data_files=[('phoenix', ['LICENSE'])]
     )
