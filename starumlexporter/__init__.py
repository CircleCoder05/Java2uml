"""StarUML MDJ 格式导出器.

将 Java 分析结果导出为 StarUML 可导入的 .mdj 文件格式.
"""

from .exporter import StarUMLExporter

__all__ = ["StarUMLExporter"]
__version__ = "0.1.0"
