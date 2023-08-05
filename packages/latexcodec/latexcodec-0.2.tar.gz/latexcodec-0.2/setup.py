#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='latexcodec',
      version='0.2',
      description='Python codec for generating international characters in Latex syntax',
      license = 'Academic Free License, version 3',
      author='Peter Troeger',
      author_email='peter@troeger.eu',
      url='http://pypi.python.org/pypi/latexcodec',
      long_description=open('README').read(),
      py_modules = ['latexcodec']
     )

