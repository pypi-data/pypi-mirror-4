from astkit import ast

from instrumental.recorder import ExecutionRecorder

class KnownValue(object):
    pass

class TestRecorder(object):
    def setup(self):
        # Reset recorder
        ExecutionRecorder.reset()
    
    def test_construct_with_literal(self):
        recorder = ExecutionRecorder.get()
        node = ast.BoolOp(op=ast.Or(),
                          values=[ast.Name(id="foo"),
                                  ast.Str(s='""')],
                          lineno=1,
                          col_offset=0)
        recorder.add_BoolOp('somemodule', node, [], None)
    
    def test_add_a_non_BoolOp(self):
        recorder = ExecutionRecorder.get()
        node = ast.BoolOp(op=4,
                          values=[ast.Name(id="foo"),
                                  ast.Str(s='""')],
                          lineno=1,
                          col_offset=0)
        try:
            recorder.add_BoolOp('somemodule', node, [], None)
        except TypeError as exc:
            assert "BoolOp" in str(exc), exc
    
    def test_constructs_accessor(self):
        recorder = ExecutionRecorder.get()
        recorder._constructs = KnownValue
        assert KnownValue == recorder.constructs
    
    def test_statements_accessor(self):
        recorder = ExecutionRecorder.get()
        recorder._statements = KnownValue
        assert KnownValue == recorder.statements
    
    def test_sources_accessor(self):
        recorder = ExecutionRecorder.get()
        recorder._sources = KnownValue
        assert KnownValue == recorder.sources
    
