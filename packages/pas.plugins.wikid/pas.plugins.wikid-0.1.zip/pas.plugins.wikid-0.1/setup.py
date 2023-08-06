# -*- coding: utf-8 -*-
"""
This module contains the tool of pas.plugins.wikid
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    read('README.rst')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs', 'CHANGES.txt'))

tests_require = ['zope.testing']

setup(name='pas.plugins.wikid',
      version=version,
      description="This is a WiKID Strong Authentication System Plugin for the Zope2 Pluggable Authentication Service (PAS).",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='Quintagroup',
      author_email='support@quintagroup.com',
      url='https://github.com/collective/pas.plugins.wikid',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pas', 'pas.plugins'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        'pyOpenSSL',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='pas.plugins.wikid.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
