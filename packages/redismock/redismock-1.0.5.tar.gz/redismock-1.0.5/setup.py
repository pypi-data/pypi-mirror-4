#!/usr/bin/env python

from setuptools import setup, find_packages
import os

setup(name='redismock',
      version='1.0.5',
      description='Mock for redis-py',
      url='https://github.com/HackingHabits/mockredis',
      license='Apache2',
      packages=find_packages(exclude=['*.tests']),
      setup_requires=[
          'nose>=1.0'
      ],
      install_requires=[
      ],
      tests_require=[
      ],
      test_suite='mocks.redismock.tests',
      )
