#!/usr/bin/env python
from ispdb import __version__

from setuptools import setup

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(name='ispdb',
      version=__version__,
      description='Interface to Mozilla ISP database',
      author='sprt',
      author_email='hellosprt@gmail.com',
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Communications :: Email :: Email Clients (MUA)',
                   'Programming Language :: Python :: 2.7',
                   # 'Programming Language :: Python :: 3.0',
                   # 'Programming Language :: Python :: 3.1',
                   # 'Programming Language :: Python :: 3.2',
                   # 'Programming Language :: Python :: 3.3'
                   ],
      py_modules=['ispdb'],
      license=open('COPYING').read(),
      install_requires=requirements)
