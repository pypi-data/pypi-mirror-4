#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='backplane2-pyclient',
      version='0.1',
      description='Backplane 2 library for python',
      author='George Katsitadze',
      author_email='george@janrain.com',
      url='http://github.com/geokat/backplane2-pyclient',
      packages = find_packages(),
      install_requires = ['httplib2'],
      keywords= 'backplane library',
      zip_safe = True,
      test_suite='tests',
      tests_require = ['mock'])
