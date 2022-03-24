from importlib import import_module
from benchmark_imports._imports import activate, deactivate
from benchmark_imports._tracker import ModuleType


def test_smoke():
    name = 'tests.example'
    tr = activate(name)
    try:
        import_module(name)
    finally:
        deactivate()
    assert len(tr.records) == 1
    rec = tr.records[0]
    assert rec.module == name
    assert rec.parent is None
    assert rec.type == ModuleType.ROOT
    assert 0 < rec.time < 5
