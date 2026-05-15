"""Legacy entry: ``java2staruml`` → unified ``java2uml`` (MDJ)."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    from java2uml.cli import main as uml_main

    a = list(argv if argv is not None else sys.argv[1:])
    if not a:
        print(
            "Usage: java2staruml <path_to_java_file_or_directory> [output.mdj]",
            file=sys.stderr,
        )
        print("Equivalent: java2uml <path> -f mdj [-o output.mdj]", file=sys.stderr)
        return 1

    path = a[0]
    rest = a[1:]
    out: list[str] = ["--format", "mdj", "--verbose", path]
    if rest:
        out.extend(["-o", rest[0]])
    return uml_main(out)


if __name__ == "__main__":
    raise SystemExit(main())
