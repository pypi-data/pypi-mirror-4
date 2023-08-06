#!/usr/bin/env python

from setuptools import setup

setup(name='pydiscovery',
      version='0.1',
      description='Network discovery',
      author='Christopher Probst',
      author_email='christopher-probst@online.de',
      packages=['pydiscovery'],
      package_dir={'': 'src'},
      install_requires=[
        'gevent==1.0rc2'
      ],
      dependency_links=[
        'https://github.com/downloads/SiteSupport/gevent/gevent-1.0rc2.tar.gz#egg=gevent-1.0rc2'
      ])
