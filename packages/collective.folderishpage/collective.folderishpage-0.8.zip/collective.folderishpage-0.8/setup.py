# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.folderishpage
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.8'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    read('collective', 'folderishpage', 'README.txt')
    + '\n' +
    read('CONTRIBUTORS.txt')
    )

tests_require=['zope.testing']

setup(name='collective.folderishpage',
      version=version,
      description="A product which adds a folderish page contenttype.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='folderish page',
      author='Four Digits',
      author_email='support@fourdigits.nl',
      url='http://www.fourdigits.nl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'collective.folderishpage.tests.test_docs.test_suite',
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      # paster_plugins = ["ZopeSkel"],
      )
