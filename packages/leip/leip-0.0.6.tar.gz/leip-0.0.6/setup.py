#!/usr/bin/env python

from setuptools import setup, find_packages

DESCRIPTION = """
Ultralightweight python CLI framework
"""

setup(name='leip',
      version='0.0.6',
      description=DESCRIPTION,
      author='Mark Fiers',
      author_email='mark.fiers42@gmail.com',
      url='http://mfiers.github.com/Leip',
      packages=find_packages(),
      requires=[
        'Yaco (>=0.1.11)',
        'xlrd',
        ],
      package_dir = {'Leip': 'leip'},
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          ]

     )
