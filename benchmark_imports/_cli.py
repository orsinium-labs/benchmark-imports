from __future__ import annotations

import sys
from argparse import ArgumentParser
from importlib import import_module
from typing import NamedTuple, NoReturn, TextIO

from ._colors import END, MAGENTA, RED
from ._imports import activate
from ._tracker import ModuleType


class Command(NamedTuple):
    argv: list[str]
    stream: TextIO

    def run(self) -> int:
        parser = ArgumentParser()
        parser.add_argument("--top", type=int, default=25)
        parser.add_argument("--precision", type=int, default=4)
        parser.add_argument("module_name")
        args = parser.parse_args(self.argv)

        tracker = activate(args.module_name)
        import_module(args.module_name)
        tracker.sort()
        for rec in tracker.records[:args.top]:
            time = format(rec.time, f'0.0{args.precision}f')
            line = f'{time} {rec.type.colored} {MAGENTA}{rec.module:40}{END}'
            if rec.parent and rec.type == ModuleType.TRANSITIVE:
                line += f' from {MAGENTA}{rec.parent}{END}'
            self._print(line)

        if tracker.errors:
            self._print('\nImport-time errors that were handled by modules:')
        for module, error in tracker.errors:
            etype = type(error).__name__
            self._print(f'{MAGENTA}{module}{END}: {RED}{etype}: {error}{END}')
        return 0

    def _print(self, *args, end: str = "\n") -> None:
        print(*args, end=end, file=self.stream)


def entrypoint() -> NoReturn:
    cmd = Command(argv=sys.argv[1:], stream=sys.stdout)
    sys.exit(cmd.run())
