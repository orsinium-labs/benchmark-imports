from contextlib import contextmanager
from typing import Iterator, List, Optional


class Stack:
    _stack: List[str]

    def __init__(self) -> None:
        self._stack = []

    @contextmanager
    def context(self, module_name: str) -> Iterator[Optional[str]]:
        parent = self._stack[-1] if self._stack else None
        self._stack.append(module_name)
        try:
            yield parent
        finally:
            self._stack.pop()
