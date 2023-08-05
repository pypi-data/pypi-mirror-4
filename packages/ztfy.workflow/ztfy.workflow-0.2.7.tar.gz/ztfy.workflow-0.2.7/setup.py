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
This module contains ztfy.workflow package
"""
import os
from setuptools import setup, find_packages

DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')

version = '0.2.7'
long_description = open(README).read() + '\n\n' + open(HISTORY).read()

tests_require = [
        'zope.testing',
    ]

setup(name='ztfy.workflow',
      version=version,
      description="ZTFY package used to handle simple workflow",
      long_description=long_description,
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Development Status :: 4 - Beta",
          "Programming Language :: Python",
          "Framework :: Zope3",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='Zope3 workflow',
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
      #test_suite = "ztfy.workflow.tests.test_workflowdocs.test_suite",
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'hurry.query',
          'hurry.workflow',
          'pytz',
          'z3c.template',
          'zc.catalog',
          'zope.app.generations',
          'zope.app.publication',
          'zope.browserpage',
          'zope.catalog',
          'zope.component',
          'zope.componentvocabulary',
          'zope.dublincore',
          'zope.event',
          'zope.i18n',
          'zope.interface',
          'zope.intid',
          'zope.lifecycleevent',
          'zope.location',
          'zope.processlifetime',
          'zope.schema',
          'zope.security',
          'zope.tales',
          'zope.traversing',
          'zope.viewlet',
          'ztfy.comment',
          'ztfy.security',
          'ztfy.utils',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
