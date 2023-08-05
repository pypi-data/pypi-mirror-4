#!/usr/bin/env python

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

# see:
# http://groups.google.com/group/comp.lang.python/browse_thread/\
#      thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

DESCRIPTION = """
A tiny plugin for python-markdown to convert a key value list to a table
""".strip()

setup(name='mdSTable',
      version='0.3.1',
      description=DESCRIPTION,
      author='Mark Fiers',
      author_email='mark.fiers42@gmail.com',
      url='https://github.com/mfiers/mdSTable',
      packages=['mdx_mdSTable', ],
      package_dir={'mdx_mdSTable': './mdx_mdSTable'},
      requires=[],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
      ])
