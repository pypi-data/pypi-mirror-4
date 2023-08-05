# -*- coding: utf-8 -*-
"""
This module contains the tool of adi.suite
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.6'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs/HISTORY.txt')
    )

tests_require = ['zope.testing']

setup(name='adi.suite',
      version=version,
      description="A suite for javascript multimedia galleries.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.1',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='Ida Ebkes',
      author_email='contact@ida-ebkes.eu',
      url='http://ida-ebkes.eu',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['adi', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'collective.contentleadimage',
                        'collective.fancybox',
                        'collective.quickupload',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='adi.suite.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
