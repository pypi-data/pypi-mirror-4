# -*- coding: utf-8 -*-
"""
This module contains the tool of cs.featured
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
    )

setup(name='cs.featured',
      version=version,
      description="Content-type to reference external things: title + image + url",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Mikel Larrategi',
      author_email='mlarreategi@codesyntax.com',
      url='http://code.codesyntax.com/private/cs.featured',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cs', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        ],
      entry_points="""      
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      
      )
