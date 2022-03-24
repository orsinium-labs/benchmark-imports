

from contextlib import contextmanager
from enum import Enum
from time import perf_counter
from typing import Iterator, List, NamedTuple, Optional, Tuple

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
    module: str             # the absolute module name
    type: ModuleType        # how the module is related to the one we track
    time: float             # how long it took to import the module
    parent: Optional[str]   # the name of the parent module


class Tracker:
    __slots__ = ('records', '_root', 'errors')
    records: List[Record]
    errors: List[Tuple[str, Exception]]
    _root: str

    def __init__(self, root: str) -> None:
        self.records = []
        self.errors = []
        self._root = root

    @contextmanager
    def track(self, *, module: str, parent: Optional[str]) -> Iterator[None]:
        start = perf_counter()
        try:
            yield
        finally:
            total = perf_counter() - start
            self.records.append(Record(
                module=module,
                type=self._get_type(module=module, parent=parent),
                time=total,
                parent=parent,
            ))

    def record_error(self, module: str, error: Exception) -> None:
        self.errors.append((module, error))

    def sort(self) -> None:
        self.records.sort(key=lambda r: r.time, reverse=True)

    def _get_type(self, *, module: Optional[str], parent: Optional[str]) -> ModuleType:
        if module is None:
            return ModuleType.ROOT
        if module == self._root or self._root.startswith(f'{module}.'):
            return ModuleType.ROOT
        if module.startswith(f'{self._root}.'):
            return ModuleType.PROJECT
        direct_parent = (ModuleType.ROOT, ModuleType.PROJECT)
        if self._get_type(module=parent, parent=None) in direct_parent:
            return ModuleType.DIRECT
        return ModuleType.TRANSITIVE
