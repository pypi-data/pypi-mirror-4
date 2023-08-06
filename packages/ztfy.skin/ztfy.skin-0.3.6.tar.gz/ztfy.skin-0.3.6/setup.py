### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
This module contains ztfy.skin package
"""
import os
from setuptools import setup, find_packages

DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')

version = '0.3.6'
long_description = open(README).read() + '\n\n' + open(HISTORY).read()

tests_require = [
        'zope.testing',
    ]

setup(name='ztfy.skin',
      version=version,
      description="ZTFY skin utility package, including views, forms and viewlets base classes",
      long_description=long_description,
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Development Status :: 4 - Beta",
          "Programming Language :: Python",
          "Framework :: Zope3",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='ZTFY Zope3 skin',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='http://www.ztfy.org',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['ztfy'],
      include_package_data=True,
      package_data={'': ['*.zcml', '*.txt', '*.pt', '*.pot', '*.po', '*.mo', '*.png', '*.gif', '*.jpeg', '*.jpg', '*.css', '*.js']},
      zip_safe=False,
      # uncomment this to be able to run tests with setup.py
      #test_suite = "ztfy.skin.tests.test_skindocs.test_suite",
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'fanstatic',
          'jquery.layer',
          'z3c.form',
          'z3c.formjs',
          'z3c.formui',
          'z3c.json',
          'z3c.jsonrpc',
          'z3c.language.switch',
          'z3c.layer.pagelet',
          'z3c.menu.simple',
          'z3c.table',
          'z3c.template',
          'zope.app.renderer',
          'zope.authentication',
          'zope.browserpage',
          'zope.browserresource',
          'zope.component',
          'zope.container',
          'zope.contentprovider',
          'zope.dublincore',
          'zope.event',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.intid',
          'zope.lifecycleevent',
          'zope.publisher',
          'zope.schema',
          'zope.security',
          'zope.traversing',
          'zope.viewlet',
          'ztfy.jqueryui >= 0.5.3',
          'ztfy.utils >= 0.3.10',
      ],
      entry_points={
          'fanstatic.libraries': [
              'ztfy.skin = ztfy.skin:library',
          ]
      })
