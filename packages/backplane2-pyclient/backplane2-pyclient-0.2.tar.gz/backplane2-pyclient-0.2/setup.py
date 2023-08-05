#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='backplane2-pyclient',
      version='0.2',
      description='Backplane 2 library for python',
      author='George Katsitadze',
      author_email='george@janrain.com',
      url='http://github.com/janrain/backplane2-pyclient',
      license='Apache License 2.0',
      packages = find_packages(),
      install_requires = ['requests'],
      keywords= 'backplane library',
      zip_safe = True,
      test_suite='tests',
      tests_require = ['mock'])
