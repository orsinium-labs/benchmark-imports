

from contextlib import contextmanager
from enum import Enum
from time import perf_counter
from typing import Iterator, List, NamedTuple
from . import _colors


class ModuleType(Enum):
    ROOT = "root"
    PROJECT = "project"
    DIRECT = "dependency"
    TRANSITIVE = "transitive"

    @property
    def colored(self) -> str:
        return f'{self.color}{self.value:10}{_colors.END}'

    @property
    def color(self) -> str:
        if self == ModuleType.ROOT:
            return _colors.BLUE
        if self == ModuleType.PROJECT:
            return _colors.RED
        if self == ModuleType.DIRECT:
            return _colors.YELLOW
        if self == ModuleType.TRANSITIVE:
            return _colors.GREEN
        raise RuntimeError("unreachable")


class Record(NamedTuple):
    module: str         # the absolute module name as passed in the import machinery
    type: ModuleType    # how the module is related to the one we track
    time: float         # how long it took to import the module


class Tracker:
    __slots__ = ('records', '_root')
    records: List[Record]
    _root: str

    def __init__(self, root: str) -> None:
        self.records = []
        self._root = root

    @contextmanager
    def track(self, module: str) -> Iterator[None]:
        start = perf_counter()
        try:
            yield
        finally:
            total = perf_counter() - start
            self.records.append(Record(
                module=module,
                type=self._get_type(module),
                time=total,
            ))

    def sort(self) -> None:
        self.records.sort(key=lambda r: r.time, reverse=True)

    def _get_type(self, module: str) -> ModuleType:
        if module == self._root:
            return ModuleType.ROOT
        if module.startswith(f'{self._root}.'):
            return ModuleType.PROJECT
        return ModuleType.DIRECT
