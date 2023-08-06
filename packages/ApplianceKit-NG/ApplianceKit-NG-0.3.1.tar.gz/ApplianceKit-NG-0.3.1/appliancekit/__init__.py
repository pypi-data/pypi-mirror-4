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

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader(__name__, 'specs'))
env.globals['isinstance'] = isinstance
env.globals['dict'] = dict

import appliancekit.compiler
import appliancekit.axml
import appliancekit.driver
import appliancekit.parsetree
