"""Parse Java source files and emit PlantUML class diagrams."""

from .javaanalyzer import JavaAnalyzer, JavaProjectAnalyZer

# Preferred spelling for new code
JavaProjectAnalyzer = JavaProjectAnalyZer

__all__ = [
    "JavaAnalyzer",
    "JavaProjectAnalyZer",
    "JavaProjectAnalyzer",
]

__version__ = "0.1.0"
