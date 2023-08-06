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

from appliancekit.axml import compile_axml_file
from appliancekit.compiler import compile_ir_string
from appliancekit.parsetree import compile_parsetree, interpret_parsetree

default_phases = ['bootstrap', 'packages', 'custom', 'configure', 'xen-tweaks', 'cleanup']

def ak_to_debarch(arch):
    if arch == 'x86': return 'i386'
    if arch == 'x86_64': return 'amd64'
    return arch

def run_ir_string(data, chroot, state, phases=default_phases, arch='x86_64'):
    tree = compile_parsetree(data)

    state['chroot'] = chroot
    state['arch'] = arch
    state['debarch'] = ak_to_debarch(arch)

    interpret_parsetree(tree, state)

def run_ir(file, chroot, state, phases=default_phases, arch='x86_64'):
    ir_data = open(file).read()
    data = compile_ir_string(ir_data, phases=phases)
    run_ir_string(data, chroot, state, phases, arch)

def run_axml(file, chroot, state, phases=default_phases, arch='x86_64'):
    data = compile_axml_file(file, phases=phases)
    run_ir_string(data, chroot, state, phases, arch)
