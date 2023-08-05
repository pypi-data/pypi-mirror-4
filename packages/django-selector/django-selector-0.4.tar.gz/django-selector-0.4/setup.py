#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup
#from distutils.core import setup

version = '0.4'

path = os.path.dirname(__file__)
if not path: path = '.'
readme = open(path + '/README.rst', 'r').read()

setup(name='django-selector',
      version=version,
      description="django urls helper based on wsgi selector",
      long_description=readme,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Framework :: Django',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='django urls selector',
      author='Jason Moiron',
      author_email='jmoiron@jmoiron.net',
      url='http://bitbucket.org/jmoiron/django-selector/',
      license='MIT',
      py_modules=['dselector'],
      # setuptools specific
      zip_safe=False,
      test_suite = "tests",
      # django is a requirement for this but.. surely...
      install_requires=['django'] # , 'lxml'],
)


