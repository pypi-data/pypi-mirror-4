#!/usr/bin/env python

from setuptools import setup
import os

setup(name='python-astrid',
      version='0.1',
      description='Python Distribution Utilities',
      author='Dusty Phillips',
      author_email='dusty@buchuki.com',
      requires=["requests"],
      url='https://bitbucket.org/dusty/python-astrid/',
      long_description=(open(
        os.path.join(
            os.path.dirname(__file__), 'README.txt')).read()),
      py_modules=["astrid"]
     )
