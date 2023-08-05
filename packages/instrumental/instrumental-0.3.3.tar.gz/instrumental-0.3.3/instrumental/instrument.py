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
""" instrument.py - instruments ASTs representing Python programs
    
    We define instrument here to mean adding code that will have a side effect
    that we can measure so that we can determine when the code was executed.
    
    This is made difficult by the fact that python is so dynamic and that
    boolean operations have the properties that they do. The problems are that
    (a) the first non-True value will be returned from an and operation and the
    first non-False value will be returned from an or operation, (b) evaluation
    stops when the result of the operation has been determined.
    
"""
import sys

from astkit import ast
from astkit.render import SourceCodeRenderer

from instrumental import recorder
from instrumental.pragmas import PragmaNoCover

def force_location(tree, lineno, col_offset=0):
    for node in ast.walk(tree):
        if hasattr(node, 'lineno'):
            node.lineno = lineno
            node.col_offset = col_offset

def has_docstring(defn):
    return ast.get_docstring(defn) is not None

def has_future_import(module):
    if not module.body:
        return False
    return (isinstance(module.body[0], ast.ImportFrom)
            and module.body[0].module == '__future__')

class InstrumentedNodeFactory(object):
    
    def __init__(self, recorder):
        self._recorder = recorder
    
    def instrument_node(self, modulename, node, pragmas, parent):
        if isinstance(node, ast.BoolOp):
            return self._recorder.add_BoolOp(modulename, node, pragmas, parent)
        else:
            return node
    
    def instrument_test(self, modulename, node):
        if not isinstance(node, ast.BoolOp):
            return self._recorder.add_test(modulename, node)
        else:
            return node
    
    def instrument_statement(self, modulename, node):
        return self._recorder.add_statement(modulename, node)

class AnnotatorFactory(object):
    
    def __init__(self, recorder):
        self.recorder = recorder
    
    def create(self, modulename, module_source):
        self.recorder.add_source(modulename, module_source)
        return CoverageAnnotator(modulename, self.recorder)

class CoverageAnnotator(ast.NodeTransformer):
    
    def __init__(self, modulename, recorder):
        self.modulename = modulename
        self.pragmas = recorder.pragmas[modulename]
        self.node_factory = InstrumentedNodeFactory(recorder)
        self.modifiers = []
        self.expression_context = []
    
    def _has_pragma(self, lineno, pragma_klass):
        return any(isinstance(pragma, pragma_klass)
                   for pragma in self.pragmas[lineno])
    
    def visit_Module(self, module):
        self.generic_visit(module)
        recorder_setup = recorder.get_setup()
        for node in recorder_setup:
            force_location(node, 1)
        if has_docstring(module):
            recorder_setup = [module.body.pop(0) + recorder_setup]
        if has_future_import(module):
            future_import = module.body.pop(0)
            if has_docstring(module):
                recorder_setup.insert(1, future_import)
            else:
                recorder_setup.insert(0, future_import)
        module.body = recorder_setup + module.body
        
        return module
    
    def visit_BoolOp(self, boolop):
        if PragmaNoCover in self.modifiers:
            result = boolop
        else:
            pragmas = self.pragmas.get(boolop.lineno, [])
            if self.expression_context:
                parent = self.expression_context[-1]
            else:
                parent = None
            result =\
                self.node_factory.instrument_node(self.modulename, boolop, pragmas, parent)
            self.expression_context.append(result)
            result = self.generic_visit(result)
            self.expression_context.pop(-1)
        return result
    
    def visit_IfExp(self, ifexp):
        if PragmaNoCover in self.modifiers:
            result = ifexp
        else:
            ifexp.test = self.node_factory.instrument_test(self.modulename, ifexp.test)
            result = self.generic_visit(ifexp)
        return result
    
    def _visit_stmt(self, node):
        if self._has_pragma(node.lineno, PragmaNoCover):
            self.modifiers.append(PragmaNoCover)
        
        if PragmaNoCover in self.modifiers:
            result = node
        else:
            marker = self.node_factory.instrument_statement(self.modulename, node)
            self.generic_visit(node)
            result = [marker, node]
        
        if self._has_pragma(node.lineno, PragmaNoCover):
            self.modifiers.pop(-1)
        return result
    
    def visit_AugAssign(self, augassign):
        return self._visit_stmt(augassign)
    
    def visit_Assign(self, assign):
        return self._visit_stmt(assign)
    
    def visit_Break(self, break_):
        return self._visit_stmt(break_)
    
    def _visit_defn_with_docstring(self, defn):
        if PragmaNoCover in self.modifiers:
            self.generic_visit(defn)
            result = defn
        else:
            # grab the docstring so that it isn't visited generically
            # docstrings don't seem to ever be 'executed', so we shouldn't
            # count them
            docstring = defn.body.pop(0)
            self.generic_visit(defn)
            
            # and put the docstring back
            defn.body = [docstring] + defn.body
            
            marker = self.node_factory.instrument_statement(self.modulename, defn)
            result = [marker, defn]
        return result
    
    def visit_ClassDef(self, defn):
        if not has_docstring(defn):
            visitor = self._visit_stmt
        else:
            visitor = self._visit_defn_with_docstring
            
        if self._has_pragma(defn.lineno, PragmaNoCover):
            self.modifiers.append(PragmaNoCover)
        
        if PragmaNoCover in self.modifiers:
            result = defn
        else:
            result = visitor(defn)
        
        if self._has_pragma(defn.lineno, PragmaNoCover):
            self.modifiers.pop(-1)
        
        return result
    
    def visit_Continue(self, continue_):
        return self._visit_stmt(continue_)
    
    def visit_Delete(self, delete):
        return self._visit_stmt(delete)
    
    def visit_Exec(self, exec_):
        return self._visit_stmt(exec_)
    
    def visit_Expr(self, expr):
        return self._visit_stmt(expr)
    
    def visit_ExceptHandler(self, excepthandler):
        if self._has_pragma(excepthandler.lineno, PragmaNoCover):
            self.modifiers.append(PragmaNoCover)
        
        self.generic_visit(excepthandler)
        
        if self._has_pragma(excepthandler.lineno, PragmaNoCover):
            self.modifiers.pop(-1)
        
        return excepthandler
    
    def visit_For(self, for_):
        if self._has_pragma(for_.lineno, PragmaNoCover):
            self.modifiers.append(PragmaNoCover)
        
        if PragmaNoCover in self.modifiers:
            result = for_
        else:
            self.generic_visit(for_)
            marker = self.node_factory.instrument_statement(self.modulename, for_)
            result = [marker, for_]
        
        if self._has_pragma(for_.lineno, PragmaNoCover):
            self.modifiers.pop(-1)
        
        return result
        
    def visit_FunctionDef(self, defn):
        if not has_docstring(defn):
            return self._visit_stmt(defn)
        
        if self._has_pragma(defn.lineno, PragmaNoCover):
            self.modifiers.append(PragmaNoCover)
        
        result = self._visit_defn_with_docstring(defn)
        
        if self._has_pragma(defn.lineno, PragmaNoCover):
            self.modifiers.pop(-1)
        
        return result
    
    def visit_Global(self, global_):
        return self._visit_stmt(global_)
    
    def visit_If(self, if_):
        if self._has_pragma(if_.lineno, PragmaNoCover):
            self.modifiers.append(PragmaNoCover)
        
        if PragmaNoCover in self.modifiers:
            result = if_
        else:
            if_.test = self.node_factory.instrument_test(self.modulename, if_.test)
            if_ = self.generic_visit(if_)
            marker = self.node_factory.instrument_statement(self.modulename, if_)
            result = [marker, if_]
        
        if self._has_pragma(if_.lineno, PragmaNoCover):
            self.modifiers.pop(-1)
        return result
    
    def visit_Import(self, import_):
        return self._visit_stmt(import_)
    
    def visit_ImportFrom(self, import_):
        if self._has_pragma(import_.lineno, PragmaNoCover):
            self.modifiers.append(PragmaNoCover)
        
        self.generic_visit(import_)
        if PragmaNoCover in self.modifiers:
            result = import_
        else:
            marker = self.node_factory.instrument_statement(self.modulename, import_)
            if import_.module == '__future__':
                result = [import_, marker]
            else:
                result = [marker, import_]
        
        if self._has_pragma(import_.lineno, PragmaNoCover):
            self.modifiers.pop(-1)
        return result
    
    def visit_Pass(self, pass_):
        return self._visit_stmt(pass_)
    
    def visit_Print(self, print_):
        return self._visit_stmt(print_)
    
    def visit_Raise(self, raise_):
        return self._visit_stmt(raise_)
    
    def visit_Return(self, return_):
        return self._visit_stmt(return_)
    
    def visit_TryExcept(self, try_):
        return self._visit_stmt(try_)
    
    def visit_TryFinally(self, try_):
        return self._visit_stmt(try_)
    
    def visit_While(self, while_):
        if self._has_pragma(while_.lineno, PragmaNoCover):
            self.modifiers.append(PragmaNoCover)
        
        if PragmaNoCover in self.modifiers:
            result = while_
        else:
            while_.test = self.node_factory.instrument_test(self.modulename, while_.test)
            self.generic_visit(while_)
            marker = self.node_factory.instrument_statement(self.modulename, while_)
            result = [marker, while_]
        
        if self._has_pragma(while_.lineno, PragmaNoCover):
            self.modifiers.pop(-1)
        return result

    def visit_With(self, with_):
        return self._visit_stmt(with_)
