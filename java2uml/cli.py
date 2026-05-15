"""Command-line entry: ``java2uml`` (PlantUML or StarUML .mdj)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from java2staruml.exporter import StarUMLExporter

from .analysis import analyze_java, iter_java_files


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="java2uml",
        description="Parse Java sources and emit PlantUML class diagram text or a StarUML .mdj model.",
    )
    p.add_argument(
        "path",
        help="Path to a .java file or a directory (recursively scanned for .java files).",
    )
    p.add_argument(
        "-f",
        "--format",
        choices=("plantuml", "mdj", "staruml"),
        default="plantuml",
        help="Output format: plantuml (text) or mdj/staruml (StarUML JSON). Default: plantuml.",
    )
    p.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Output file. PlantUML: default is stdout. MDJ: default is output.mdj.",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print per-file parse status when exporting MDJ.",
    )
    p.add_argument(
        "-n",
        "--name",
        metavar="NAME",
        help="Project name inside the MDJ (default: stem of the input path).",
    )
    return p


def _normalize_format(fmt: str) -> str:
    if fmt == "staruml":
        return "mdj"
    return fmt


def run(args: argparse.Namespace) -> int:
    path = args.path
    fmt = _normalize_format(args.format)

    if not os.path.exists(path):
        print("Error: path does not exist", file=sys.stderr)
        return 1

    java_files = iter_java_files(path)

    if fmt == "plantuml":
        if not java_files:
            # Match legacy java2plantuml: still emit a minimal diagram.
            text = "@startuml\n@enduml\n"
            out_path = args.output
            if out_path:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(text)
            else:
                sys.stdout.write(text)
            return 0
        project, _errors = analyze_java(path, resilient=False)
        inner = project.get_analyzer()
        body_lines: list[str] = ["@startuml"]
        for package in inner.packages.values():
            body_lines.append(str(package))
        for package in inner.packages.values():
            for relation in package.relations_list:
                body_lines.append(str(relation))
        body_lines.append("@enduml")
        text = "\n".join(body_lines) + "\n"

        out_path = args.output
        if out_path:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            sys.stdout.write(text)
        return 0

    if not java_files:
        print("Error: no .java files found at this path", file=sys.stderr)
        return 1

    # MDJ
    def on_ok(fp: str) -> None:
        if args.verbose:
            print(f"  [OK] {os.path.basename(fp)}")

    def on_err(fp: str, msg: str) -> None:
        if args.verbose:
            print(f"  [Error] {os.path.basename(fp)}: {msg}")

    print(f"Analyzing Java sources from: {path}")
    project, errors = analyze_java(path, resilient=True, on_file_ok=on_ok, on_file_error=on_err)

    if errors and args.verbose:
        ok = len(java_files) - len(errors)
        print(f"\n  Parsed {ok} files successfully, {len(errors)} files with errors.")

    inner = project.get_analyzer()
    total_packages = len(inner.packages)
    total_classes = sum(len(pkg.classes) for pkg in inner.packages.values())
    print("\nAnalysis complete.")
    print(f"  Found {total_packages} package(s), {total_classes} class(es)/interface(s)/enum(s)")

    if total_classes == 0:
        print("\nError: No classes were successfully parsed.", file=sys.stderr)
        if errors:
            print("Please fix the syntax errors above and try again.", file=sys.stderr)
        return 1

    out_path = args.output or "output.mdj"
    if not str(out_path).endswith(".mdj"):
        out_path = str(out_path) + ".mdj"

    project_name = args.name or Path(path).stem
    print("\nExporting to StarUML format...")
    try:
        StarUMLExporter().export_to_file(project, out_path, project_name)
    except OSError as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        return 1

    print(f"Successfully exported to: {out_path}")
    print("You can now open this file in StarUML.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
