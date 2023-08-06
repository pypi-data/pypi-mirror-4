# -*- coding: utf-8 -*-
"""
This module contains the tool of cs.featured
"""
import os
from setuptools import setup, find_packages

version = '1.0'

setup(name='cs.featured',
      version=version,
      description="Content-type to reference external things: title+image+url",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Mikel Larreategi',
      author_email='mlarreategi@codesyntax.com',
      url='http://github.com/codesyntax/cs.featured',
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
