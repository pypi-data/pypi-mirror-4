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

from appliancekit import env

import os
import subprocess
import errno

def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)

class UnimplementedOperationException(Exception):
    pass

class UnimplementedOperation(object):
    def __init__(self, operation, **kwargs):
        self.operation = operation
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<{}: '{}'>".format(type(self).__name__, self.operation)

    def visit(self, state):
        raise UnimplementedOperationException(self.operation)

class NoOpOperation(UnimplementedOperation):
    '''An operation which does nothing.'''
    def visit(self, state):
        pass

class SetEnvOperation(UnimplementedOperation):
    def __repr__(self):
        return "<{}: '{}' = '{}'>".format(type(self).__name__, self.key, self.value)

    def visit(self, state):
        simulate = state.get('simulate', False)
        print 'setenv', '{}={}'.format(self.key, self.value)
        if simulate:
            return
        if self.value:
            os.environ[self.key] = self.value
        elif os.environ.has_key(self.key):
            del os.environ[self.key]

class RunCmdOperation(UnimplementedOperation):
    def __repr__(self):
        return "<{}: '{}'{}>".format(type(self).__name__, self.command[0], " (chroot)" if self.chroot else "")

    def visit(self, state):
        simulate = state.get('simulate', False)
        cmdline = list()
        if self.chroot:
            cmdline += ['chroot', state['chroot']]
        for i in self.command:
            st = i
            for k, v in state.iteritems():
                st = st.replace('$' + str(k), str(v))
            cmdline.append(st)
        print ' '.join(cmdline)
        if simulate:
            return
        return subprocess.call(cmdline, close_fds=True)

class RenderTemplateOperation(UnimplementedOperation):
    def __repr__(self):
        return "<{}: '{}'>".format(type(self).__name__, self.template)

    def visit(self, state):
        simulate = state.get('simulate', False)
        print 'RenderTemplate', '{} -> {}{}'.format(self.template, state['chroot'], self.target)
        if simulate:
            return
        tmpl = env.get_template(self.template)
        target = state['chroot'] + self.target
        mkdir_p(os.path.dirname(target))
        target_fd = open(target, 'w')
        target_fd.write(tmpl.render(**state))
        target_fd.close()

optree = {
    'noop': NoOpOperation,
    'runcmd': RunCmdOperation,
    'setenv': SetEnvOperation,
    'render_template': RenderTemplateOperation,
}

def compile_parsetree(parsetree):
    '''Compiles a parse tree into bytecode.'''
    lst = list()

    for i in parsetree:
        cons = lambda op: optree[op] if optree.has_key(op) else UnimplementedOperation
        op = i.pop('operation', 'noop')
        cstr = cons(op)

        # Optimization: We can now remove noop operations, since they exist only to keep the
        # IR layer happy.  Blame JSON for requiring this hack.
        if cstr == NoOpOperation: continue

        lst.append(cstr(op, **i))

    return lst

def interpret_parsetree(set, state):
    '''Executes bytecode and returns the results of all computations.'''
    return [i.visit(state) for i in set]
