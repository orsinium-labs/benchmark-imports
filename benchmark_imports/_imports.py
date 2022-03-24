from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
import sys
from types import ModuleType
from typing import Optional
from ._tracker import Tracker
from _frozen_importlib_external import PathFinder, SourceFileLoader  # pyright: reportMissingImports=false


class BenchFinder(MetaPathFinder):
    __slots__ = ('_tracker',)
    _tracker: Tracker

    def __init__(self, tracker: Tracker) -> None:
        self._tracker = tracker

    def find_spec(self, *args, **kwargs) -> Optional[ModuleSpec]:
        finders = [PathFinder]  # sys.meta_path
        for finder in finders:
            if finder is self:
                continue
            spec = finder.find_spec(*args, **kwargs)
            if spec is None:
                continue
            if isinstance(spec.loader, SourceFileLoader):
                spec.loader = BenchLoader(spec.loader, self._tracker)
            return spec
        return None


class BenchLoader(Loader):
    __slots__ = ('_loader', )
    _loader: Loader
    _tracker: Tracker

    def __init__(self, loader: Loader, tracker: Tracker) -> None:
        self._loader = loader
        self._tracker = tracker

    def __getattr__(self, name: str):
        return getattr(self._loader, name)

    def exec_module(self, module: ModuleType) -> None:
        with self._tracker.track(module.__name__):
            return self._loader.exec_module(module)


def activate(root_module: str) -> Tracker:
    assert BenchFinder not in sys.meta_path
    tracker = Tracker(root_module)
    index = sys.meta_path.index(PathFinder)
    sys.meta_path.insert(index, BenchFinder(tracker))
    return tracker


def deactivate() -> None:
    for finder in sys.meta_path.copy():
        if isinstance(finder, BenchFinder):
            sys.meta_path.remove(finder)
