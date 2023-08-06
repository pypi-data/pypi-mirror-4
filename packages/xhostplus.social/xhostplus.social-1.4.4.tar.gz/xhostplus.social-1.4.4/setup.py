# -*- coding: utf-8 -*-
"""
This module contains the tool of xhostplus.social
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.4.4'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

tests_require = ['zope.testing']

setup(name='xhostplus.social',
      version=version,
      description="Displays social buttons (facebook, google+, twitter, linkedin) on the Plone site.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='',
      author_email='',
      url='http://www.xhostplus.at/de/services/plone-downlods',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xhostplus', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'archetypes.schemaextender',
                        'httplib2',
                        # -*- Extra requirements: -*-
                        'Products.CMFPlone',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='xhostplus.social.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
