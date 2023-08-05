import os

from setuptools import setup, find_packages

readme = open('README.rst').read()
changes = open('CHANGES.rst').read()

version = '1.1.3'

setup(name = 'tlspu.cookiepolicy',
      version = version,
      description = 'A Plone add-on providing a simple solution to comply with the so called "European Cookie Law".',
      long_description = readme + '\n' + changes,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers = [
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords = 'python plone zope cookie eu law',
      author = 'TLSPU',
      author_email = 'contact@tlspu.com',
      url = 'http://www.tlspu.com/consultancy/cookiepolicy',
      license = 'AGPL',
      packages = find_packages(exclude = ['ez_setup']),
      namespace_packages = ['tlspu'],
      include_package_data = True,
      zip_safe = False,
      install_requires = [
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': ['plone.app.testing'],
      },
      entry_points = """
          [z3c.autoinclude.plugin]
          target = plone
          # -*- Entry points: -*-
      """,
      )
