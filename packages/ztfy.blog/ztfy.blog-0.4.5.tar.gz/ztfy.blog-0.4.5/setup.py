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
This module contains ztfy.blog package
"""
import os
from setuptools import setup, find_packages

DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')

version = '0.4.5'
long_description = open(README).read() + '\n\n' + open(HISTORY).read()

tests_require = [
    'zope.testing',
]

setup(name='ztfy.blog',
      version=version,
      description="ZTFY blog handling package",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Development Status :: 4 - Beta",
          "Programming Language :: Python",
          "Framework :: Zope3",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='ZTFY Zope3 blog package',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='http://www.ztfy.org',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['ztfy'],
      include_package_data=True,
      package_data={'': ['*.zcml', '*.txt', '*.pt', '*.pot', '*.po', '*.mo', '*.png', '*.gif', '*.css', '*.js']},
      zip_safe=False,
      # uncomment this to be able to run tests with setup.py
      #test_suite = "ztfy.comment.tests.test_commentdocs.test_suite",
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'fanstatic',
          'hurry.query',
          'Pygments',
          'pytz',
          'transaction',
          'z3c.form',
          'z3c.formui',
          'z3c.formjs',
          'z3c.json',
          'z3c.jsonrpc',
          'z3c.language.negotiator',
          'z3c.language.switch',
          'z3c.menu.simple',
          'z3c.table',
          'z3c.template',
          'z3c.viewlet',
          'z3c.zrtresource',
          'zc.catalog',
          'zope.annotation',
          'zope.app.content',
          'zope.app.publication',
          'zope.authentication',
          'zope.browserpage',
          'zope.catalog',
          'zope.component',
          'zope.container',
          'zope.copypastemove',
          'zope.dublincore',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.intid',
          'zope.location',
          'zope.pluggableauth',
          'zope.processlifetime',
          'zope.schema',
          'zope.site',
          'zope.tales',
          'zope.traversing',
          'zope.viewlet',
          'zopyx.txng3.core',
          'zopyx.txng3.ext',
          'ztfy.extfile >= 0.2.0',
          'ztfy.file',
          'ztfy.i18n',
          'ztfy.jqueryui >= 0.6.0',
          'ztfy.security >= 0.2.1',
          'ztfy.skin >= 0.3.0',
          'ztfy.utils >= 0.3.10',
          'ztfy.workflow >= 0.2.1',
      ],
      entry_points={
          'fanstatic.libraries': [
              'ztfy.blog = ztfy.blog.browser:library',
              'ztfy.blog.defaultskin = ztfy.blog.defaultskin:library'
          ]
      })
