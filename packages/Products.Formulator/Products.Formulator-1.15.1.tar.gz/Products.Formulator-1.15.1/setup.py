# -*- coding: utf-8 -*-
# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: setup.py 50564 2012-12-12 11:07:10Z sylvain $

from setuptools import setup, find_packages
import os

version = '1.15.1'


tests_require = [
    'infrae.wsgi [test]',
    ]

def read_file(filename):
    with open(os.path.join("Products", "Formulator", filename)) as data:
        return data.read() + '\n'


setup(name='Products.Formulator',
      version=version,
      description="Form library for Zope 2.",
      long_description=read_file("README.txt") +
                       read_file("CREDITS.txt") +
                       read_file("HISTORY.txt"),
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
      keywords='form generator zope2',
      author='Martijn Faassen and community',
      author_email='info@infrae.com',
      url='http://infrae.com/products/formulator',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'five.grok',
        'zope.interface',
        'zope.component',
        'zope.i18nmessageid',
        'zope.cachedescriptors',
        'zeam.form.base',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
