"""Shared Java source analysis for all export formats."""

from __future__ import annotations

import os
from collections.abc import Callable

import javalang.parser

from java2plantuml.javaanalyzer import JavaProjectAnalyZer


def iter_java_files(path: str) -> list[str]:
    """Return sorted list of .java paths for a file or recursive directory walk."""
    if not os.path.exists(path):
        return []
    if os.path.isfile(path):
        return [path] if path.endswith(".java") else []
    out: list[str] = []
    for root, _dirs, files in os.walk(path):
        for name in files:
            if name.endswith(".java"):
                out.append(os.path.join(root, name))
    return sorted(out)


def analyze_java(
    path: str,
    *,
    resilient: bool,
    on_file_ok: Callable[[str], None] | None = None,
    on_file_error: Callable[[str, str], None] | None = None,
) -> tuple[JavaProjectAnalyZer, list[tuple[str, str]]]:
    """Parse Java sources into a ``JavaProjectAnalyZer`` and run ``analyze_relations``.

    If *resilient* is True, syntax errors in individual files are skipped and reported
    in the returned error list; otherwise behavior matches ``JavaAnalyzer.analyze_file``
    (errors printed by the analyzer, file skipped).
    """
    files = iter_java_files(path)
    project = JavaProjectAnalyZer()
    inner = project.get_analyzer()
    errors: list[tuple[str, str]] = []

    for filepath in files:
        if resilient:
            try:
                inner.analyze_file(filepath)
                if on_file_ok:
                    on_file_ok(filepath)
            except javalang.parser.JavaSyntaxError as e:
                msg = str(e)
                errors.append((filepath, msg))
                if on_file_error:
                    on_file_error(filepath, f"Syntax error: {msg}")
            except Exception as e:
                msg = f"{type(e).__name__}: {e}"
                errors.append((filepath, msg))
                if on_file_error:
                    on_file_error(filepath, msg)
        else:
            inner.analyze_file(filepath)

    project.analyze_relations()
    return project, errors
