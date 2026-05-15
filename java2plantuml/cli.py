"""Legacy entry: ``java2plantuml`` → unified ``java2uml`` (PlantUML)."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    from java2uml.cli import main as uml_main

    a = argv if argv is not None else sys.argv[1:]
    return uml_main(["--format", "plantuml", *list(a)])


if __name__ == "__main__":
    raise SystemExit(main())
