#!/usr/bin/env python2
# coding=utf-8

# Last modified: <2012-12-10 12:13:05 Monday by richard>

# @version 0.1
# @author : Richard Wong
# Email: chao787@gmail.com

# public lisence: BSD
import os
try:
    from setuptools import setup
    has_setuptools = True
except ImportError:
    from distutils.core import setup
    has_setuptools = False

from python_org._version import version


setup_kwargs = {}

if has_setuptools:
    setup_kwargs['test_suite'] = 'python_org.test'

readme = open(os.path.join(os.path.dirname(__file__), 'README')).read()

setup(name='python_org',
      description='Fast most-functional organizer for org-mode.',
      long_description=readme,
      # technical info
      version=version,
      packages=['python_org', 'python_org.test'],
      requires=[
          'python (>= 2.6)',
      ],
      provides=['python_org'],

      # copyright
      author='Richard Wong',
      author_email='chao787@gmail.com',
      license="Two-clause BSD license",

      # URL info
      url='https://github.com/chao787/python_org',

      # misc settings.
      zip_safe=True,

      # categorization
      keywords=('query database api model models orm key/value '
                'orgtoolment-oriented org-mode non-relational emacs'),

      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Plugins',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Information Technology',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Database',
          'Topic :: Database :: Database Engines/Servers',
          'Topic :: Database :: Front-Ends',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      **setup_kwargs)
# setup.py ended here
