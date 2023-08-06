#!/usr/bin/env python
from setuptools import setup, find_packages
import os

# Utility function to read README file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='django-logical-rules',
      version='0.1.1',
      description='A rule engine for Django apps.',
      author='Benjamin Stookey',
      author_email='ben@aashe.org',
      url='https://bitbucket.org/aashe/django-logical-rules',
      license='LICENSE',
      long_description=read("README.rst"),
      packages=[
        'logical_rules',
        'logical_rules.templatetags',
        'logical_rules.tests',
        ],
      install_requires=[
              "Django >= 1.3",
              'setuptools'
              ],
      classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Web Environment',
              'Framework :: Django',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: BSD License',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Topic :: Utilities'
          ],
      )
