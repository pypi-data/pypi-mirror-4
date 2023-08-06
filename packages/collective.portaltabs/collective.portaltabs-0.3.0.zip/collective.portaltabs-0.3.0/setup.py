# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version = '0.3.0'

tests_require = ['plone.app.testing', 'pyquery']

setup(name='collective.portaltabs',
      version=version,
      description="Manage site's portal tabs from Plone interface in a simple way",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        ],
      keywords='plone portal-tabs plonegov',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/collective.portaltabs',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          'elementtree',
          'collective.autopermission',
          'plone.app.registry',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
