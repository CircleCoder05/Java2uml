"""StarUML 导出器命令行接口."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 确保能找到 java2plantuml 模块
try:
    from java2plantuml.javaanalyzer import JavaAnalyzer, JavaProjectAnalyZer
    from .exporter import StarUMLExporter
except ImportError:
    # 当作为独立脚本运行时
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from java2plantuml.javaanalyzer import JavaAnalyzer, JavaProjectAnalyZer
    from starumlexporter.exporter import StarUMLExporter


def main(argv: list[str] | None = None) -> int:
    """命令行入口.

    Usage: python -m starumlexporter <path_to_java> [output.mdj]
    """
    args = argv if argv is not None else sys.argv[1:]

    if len(args) < 1:
        print("Usage: python -m starumlexporter <path_to_java_file_or_directory> [output.mdj]", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  python -m starumlexporter ./src/MyClass.java output.mdj", file=sys.stderr)
        print("  python -m starumlexporter ./src/myproject/ output.mdj", file=sys.stderr)
        return 1

    input_path = args[0]
    output_path = args[1] if len(args) > 1 else "output.mdj"

    if not os.path.exists(input_path):
        print(f"Error: Path does not exist: {input_path}", file=sys.stderr)
        return 1

    # 确保输出路径以 .mdj 结尾
    if not output_path.endswith(".mdj"):
        output_path += ".mdj"

    print(f"Analyzing Java sources from: {input_path}")

    try:
        # 使用 JavaProjectAnalyZer 批量分析
        analyzer = JavaProjectAnalyZer()

        if os.path.isdir(input_path):
            # 使用安全的目录分析
            success_count, error_files = safe_analyze_directory(analyzer, input_path)
            if error_files:
                print(f"\n  Parsed {success_count} files successfully, {len(error_files)} files with errors.")
        else:
            # 单个文件处理
            single_analyzer = JavaAnalyzer()
            single_analyzer.analyze_file(input_path)
            # 复制分析结果到 project analyzer
            analyzer = JavaProjectAnalyZer()
            analyzer._JavaProjectAnalyZer__analyzer = single_analyzer  # type: ignore

        # 分析关系
        analyzer.analyze_relations()

        # 打印分析摘要
        print("\nAnalysis complete.")
        inner = analyzer._JavaProjectAnalyZer__analyzer  # type: ignore
        total_packages = len(inner.packages)
        total_classes = sum(len(pkg.classes) for pkg in inner.packages.values())
        print(f"  Found {total_packages} package(s), {total_classes} class(es)/interface(s)/enum(s)")

        if total_classes == 0:
            print("\nError: No classes were successfully parsed.", file=sys.stderr)
            print("Please fix the syntax errors above and try again.", file=sys.stderr)
            return 1

        print("\nExporting to StarUML format...")

        # 导出
        exporter = StarUMLExporter()
        project_name = Path(input_path).stem
        exporter.export_to_file(analyzer, output_path, project_name)

        print(f"Successfully exported to: {output_path}")
        print(f"You can now open this file in StarUML.")
        return 0

    except Exception as e:
        print(f"Error during export: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def safe_analyze_directory(analyzer, input_path):
    """安全地分析目录，捕获并报告错误但不中断."""
    import javalang.parser
    import os
    
    java_files = []
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    
    success_count = 0
    error_files = []
    
    for filepath in java_files:
        try:
            inner = analyzer._JavaProjectAnalyZer__analyzer
            inner.analyze_file(filepath)
            success_count += 1
            print(f"  [OK] {os.path.basename(filepath)}")
        except javalang.parser.JavaSyntaxError as e:
            error_files.append((filepath, str(e)))
            print(f"  [Error] {os.path.basename(filepath)}: Syntax error")
        except Exception as e:
            error_files.append((filepath, f"{type(e).__name__}: {e}"))
            print(f"  [Error] {os.path.basename(filepath)}: {type(e).__name__}")
    
    return success_count, error_files


def print_summary(analyzer):
    """打印分析摘要."""
    total_classes = 0
    total_packages = 0
    for pkg_name, pkg in analyzer.packages.items():
        total_packages += 1
        class_count = len(pkg.classes)
        total_classes += class_count
        if class_count > 0:
            print(f"  Package '{pkg_name}': {class_count} classes/interfaces/enums")
    
    print(f"\nSummary: {total_packages} packages, {total_classes} total classes/interfaces/enums")


if __name__ == "__main__":
    sys.exit(main())
