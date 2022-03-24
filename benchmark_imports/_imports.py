import sys
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Optional

from _frozen_importlib_external import \
    SourceFileLoader  # pyright: reportMissingImports=false

from ._stack import Stack
from ._tracker import Tracker


class BenchFinder(MetaPathFinder):
    __slots__ = ('_tracker', '_stack')
    _tracker: Tracker
    _stack: Stack

    def __init__(self, tracker: Tracker) -> None:
        self._tracker = tracker
        self._stack = Stack()

    def find_spec(self, *args, **kwargs) -> Optional[ModuleSpec]:
        for finder in sys.meta_path:
            if finder is self:
                continue
            try:
                spec = finder.find_spec(*args, **kwargs)
            except AttributeError:
                continue
            if spec is None:
                continue
            if isinstance(spec.loader, SourceFileLoader):
                spec.loader = BenchLoader(spec.loader, self._tracker, self._stack)
            return spec
        return None


class BenchLoader(Loader):
    def __init__(self, loader: Loader, tracker: Tracker, stack: Stack) -> None:
        self._loader = loader
        self._tracker = tracker
        self._stack = stack

    def __getattr__(self, name: str):
        return getattr(self._loader, name)

    def exec_module(self, module: ModuleType) -> None:
        with self._stack.context(module.__name__) as parent:
            with self._tracker.track(module=module.__name__, parent=parent):
                try:
                    self._loader.exec_module(module)
                except Exception as exc:
                    self._tracker.record_error(module.__name__, exc)
                    raise


def activate(root_module: str) -> Tracker:
    assert BenchFinder not in sys.meta_path
    tracker = Tracker(root_module)
    sys.meta_path.insert(0, BenchFinder(tracker))
    return tracker


def deactivate() -> None:
    for finder in sys.meta_path.copy():
        if isinstance(finder, BenchFinder):
            sys.meta_path.remove(finder)
