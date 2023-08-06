#!/usr/bin/env python
"""
Copyright (c) 2012, 2013 TortoiseLabs LLC

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

This software is provided 'as is' and without any warranty, express or
implied. In no event shall the authors be liable for any damages arising
from the use of this software.
"""

from distutils.core import setup

setup(name='ApplianceKit-NG',
      version='0.2',
      description='Tools to programatically create distribution images from any distribution',
      author='William Pitcock',
      author_email='nenolod@tortois.es',
      maintainer='William Pitcock',
      maintainer_email='nenolod@tortois.es',
      url='http://www.bitbucket.org/tortoiselabs/appliancekit-ng',
      packages=['appliancekit'],
      package_data={'appliancekit': ['specs/*.spec', 'specs/base/*.tmpl', 'specs/alpine/*.tmpl', 'specs/debian/*.tmpl', 'specs/ubuntu/*.tmpl', 'specs/redhat/*.tmpl']},
      classifiers=['License :: OSI Approved :: ISC License (ISCL)', 'Operating System :: POSIX',
                   'Topic :: System :: Systems Administration'],
      platforms=['Linux'],
     )
