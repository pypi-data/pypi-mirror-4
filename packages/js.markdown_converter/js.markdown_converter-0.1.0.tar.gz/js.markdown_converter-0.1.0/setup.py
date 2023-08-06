#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# setup
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-19


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)
                        # XXX: Don't put absolute imports in setup.py

import os, sys
from setuptools import setup, find_packages

# Import the version from the release module
project_name = 'js.markdown_converter'
_current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(_current_dir, 'js', 'markdown_converter'))
from release import VERSION as version

setup(name=project_name,
      version=version,
      description="Fanstatic resource definition for Markdown.Converter",
      long_description=open(os.path.join("docs", "readme.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
      ],
      keywords='fanstatic markdown-converter resource',
      author='Merchise Autrement',
      author_email='',
      url='http://www.merchise.org',
      license='GPL 3+',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['js', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'fanstatic>=0.16',
      ],
      entry_points="""
      [fanstatic.libraries]
      js.markdown_converter = js.markdown_converter:lib
      """,
      )
