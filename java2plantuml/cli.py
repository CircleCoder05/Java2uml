"""Command-line entry: ``java2plantuml <path>``."""

from __future__ import annotations

import os
import sys

from .javaanalyzer import JavaAnalyzer


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("Usage: java2plantuml <path_to_java_file_or_directory>", file=sys.stderr)
        return 1
    path_to_java_files = args[0]
    if not os.path.exists(path_to_java_files):
        print("Error: path does not exist", file=sys.stderr)
        return 1

    analyzer = JavaAnalyzer()
    if not os.path.isdir(path_to_java_files):
        analyzer.analyze_file(path_to_java_files)
    else:
        for root, _dirs, files in os.walk(path_to_java_files):
            for file in files:
                if file.endswith(".java"):
                    analyzer.analyze_file(os.path.join(root, file))

    analyzer.analyze_relations()

    print("@startuml")
    analyzer.print_packages()
    analyzer.print_relations()
    print("@enduml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
