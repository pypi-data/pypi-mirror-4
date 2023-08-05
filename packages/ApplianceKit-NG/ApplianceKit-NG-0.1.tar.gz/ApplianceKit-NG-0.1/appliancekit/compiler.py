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

import json

from appliancekit import env

def compile_string(specname, **kwargs):
    tmpl = env.get_template(specname)
    return tmpl.render(**kwargs)

def compile_ir_string(string, **kwargs):
    tmpl = env.from_string(string)
    return tmpl.render(**kwargs)

def compile(specname, **kwargs):
    im = compile_string(specname, **kwargs)
    return json.loads(im)

