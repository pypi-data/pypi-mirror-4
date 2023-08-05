# -*- coding: utf-8 -*-
"""
This module contains the tool of rer.giunta
"""
import os
from setuptools import setup, find_packages

version = '1.1.1'

tests_require = ['zope.testing']

setup(name='rer.giunta',
      version=version,
      description="An Archetype for alderman informations",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.2",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='rer giunta',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/rer.giunta',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rer', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='rer.giunta.tests.test_docs.test_suite',
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
