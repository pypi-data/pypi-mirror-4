#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='supertools',
      version='1.0.1',
      description='A simple python module to provide .__super ability to python 2 classes.',
      author='Arthibus Gisséhel',
      author_email='public-dev-supertools@gissehel.org',
      url='https://github.com/gissehel/supertools.git',
      packages=['supertools'],
      license='MIT',
      keywords='super supertools superable',
      long_description=open('README.rst').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2 :: Only',
      ],
)
