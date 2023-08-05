# 
# Copyright (C) 2012  Matthew J Desmarais

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
from copy import copy
from copy import deepcopy
import inspect
import sys

from astkit import ast

from instrumental.constructs import BooleanDecision
from instrumental.constructs import LogicalAnd
from instrumental.constructs import LogicalOr
from instrumental.pragmas import PragmaFinder

def __setup_recorder(): # pragma: no cover
    from instrumental.recorder import ExecutionRecorder
    _xxx_recorder_xxx_ = ExecutionRecorder.get()

def get_setup():
    source = inspect.getsource(__setup_recorder)
    mod = ast.parse(source)
    defn = mod.body[0]
    setup = defn.body[:]
    for stmt in setup:
        stmt.lineno -= 1
    return setup

class ExecutionRecorder(object):
    
    @classmethod
    def reset(cls):
        cls._instance = None
    
    _instance = None
    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self._next_label = 1
        self._constructs = {}
        self._sources = {}
        self._statements = {}
        self._branches = {}
        self.pragmas = {}
        self.recording = False
        
    def start(self):
        self.recording = True
    
    def stop(self):
        self.recording = False
    
    def add_source(self, modulename, source):
        self._sources[modulename] = source
        self.pragmas[modulename] = self._find_pragmas(source)
    
    def _find_pragmas(self, source):
        finder = PragmaFinder()
        return finder.find_pragmas(source)
    
    @property
    def sources(self):
        return self._sources
    
    @property
    def constructs(self):
        return self._constructs
    
    @property
    def statements(self):
        return self._statements
    
    def next_label(self):
        label = self._next_label
        self._next_label += 1
        return label
    
    @staticmethod
    def get_recorder_call():
        kall = ast.Call()
        kall.func = ast.Attribute(value=ast.Name(id="_xxx_recorder_xxx_",
                                                 ctx=ast.Load()),
                                  attr="record",
                                  ctx=ast.Load())
        kall.keywords = []
        return kall
    
    def record(self, arg, label, *args, **kwargs):
        if self.recording:
            self._constructs[label].record(arg, *args, **kwargs)
        return arg
    
    def add_BoolOp(self, modulename, node, pragmas, parent):
        if isinstance(node.op, ast.And):
            construct_klass = LogicalAnd
        elif isinstance(node.op, ast.Or):
            construct_klass = LogicalOr
        else:
            raise TypeError("Expected a BoolOp node with an op field of ast.And or ast.Or")
        construct = construct_klass(modulename, node, parent)
        for pragma in pragmas:
            construct = pragma(construct)
        
        label = self.next_label()
        self._constructs[label] = construct
        
        # Now wrap the individual values in recorder calls
        base_call = self.get_recorder_call()
        base_call.args = \
            [ast.Num(n=label, lineno=node.lineno, col_offset=node.col_offset)]
        for i, value in enumerate(node.values):
            # Try to determine if the condition is a literal
            # Maybe we can do something with this information?
            try:
                literal = ast.literal_eval(value)
                construct.literals[i] = literal
            except ValueError:
                pass
            recorder_call = deepcopy(base_call)
            recorder_call.args.insert(0, node.values[i])
            recorder_call.args.append(ast.copy_location(ast.Num(n=i), node.values[i]))
            node.values[i] = ast.copy_location(recorder_call, node.values[i])
        ast.fix_missing_locations(node)
        return node
    
    def add_test(self, modulename, node):
        label = self.next_label()
        construct = BooleanDecision(modulename, node)
        self._constructs[label] = construct
        
        base_call = ast.copy_location(self.get_recorder_call(),
                                      node)
        base_call.args = \
            [node,
             ast.Num(n=label, lineno=node.lineno, col_offset=node.col_offset)]
        ast.fix_missing_locations(base_call)
        return base_call
    
    @staticmethod
    def get_statement_recorder_call(modulename, lineno):
        kall = ast.Call()
        kall.func = ast.Attribute(value=ast.Name(id="_xxx_recorder_xxx_",
                                                 ctx=ast.Load()),
                                  attr="record_statement",
                                  ctx=ast.Load())
        kall.args = [ast.Str(s=modulename),
                     ast.Num(n=lineno),
                     ]
        kall.keywords = []
        kall_stmt = ast.Expr(value=kall)
        return kall_stmt
    
    def record_statement(self, modulename, lineno):
        if self.recording:
            self._statements[modulename][lineno] = True
    
    def add_statement(self, modulename, node):
        lines = self._statements.setdefault(modulename, {})
        lines[node.lineno] = False
        marker = self.get_statement_recorder_call(modulename, node.lineno)
        marker = ast.copy_location(marker, node)
        ast.fix_missing_locations(marker)
        return marker
