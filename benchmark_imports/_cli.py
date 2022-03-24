from __future__ import annotations
from importlib import import_module

import sys
from argparse import ArgumentParser
from typing import NamedTuple, NoReturn, TextIO

from ._imports import activate


class Command(NamedTuple):
    argv: list[str]
    stream: TextIO

    def run(self) -> int:
        parser = ArgumentParser()
        parser.add_argument("--top", type=int, default=20)
        parser.add_argument("--precision", type=int, default=4)
        parser.add_argument("module_name")
        args = parser.parse_args(self.argv)
        tracker = activate(args.module_name)
        import_module(args.module_name)
        tracker.sort()
        for r in tracker.records[:args.top]:
            time = format(r.time, f'0.0{args.precision}f')
            self._print(f'{time} {r.type.colored} {r.module}')
        return 0

    def _print(self, *args, end: str = "\n") -> None:
        print(*args, end=end, file=self.stream)


def entrypoint() -> NoReturn:
    cmd = Command(argv=sys.argv[1:], stream=sys.stdout)
    sys.exit(cmd.run())
