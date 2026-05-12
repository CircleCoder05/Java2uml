"""StarUML ID 生成器.

StarUML 使用特定格式的 ID 字符串来引用元素.
格式类似: AAAAAAFF+h6SjaM2Hec=
"""

import base64
import random
import string


class StarUMLIDGenerator:
    """生成 StarUML 风格的唯一 ID."""

    def __init__(self, seed: int | None = None):
        """初始化 ID 生成器.

        Args:
            seed: 随机种子，用于可重复生成
        """
        if seed is not None:
            random.seed(seed)
        self._counter = 0

    def generate(self) -> str:
        """生成一个新的 StarUML 风格 ID.

        Returns:
            StarUML 格式的 ID 字符串
        """
        self._counter += 1
        # StarUML ID 通常是 22 个字符的 base64 编码
        # 格式: AAAAAAFF+h6SjaM2Hec=
        # 我们生成类似的格式
        prefix = "AAAAAAFF"
        # 生成 10 字节的随机数据，编码为 base64 得到约 14 个字符
        random_bytes = random.randbytes(10)
        suffix = base64.b64encode(random_bytes).decode('ascii').rstrip('=')
        return f"{prefix}{suffix[:12]}{self._counter:03d}="

    def generate_short(self) -> str:
        """生成较短的 ID（用于测试）."""
        self._counter += 1
        return f"ID{self._counter:06d}=="


# 全局 ID 生成器实例
_id_generator = StarUMLIDGenerator()


def generate_id() -> str:
    """生成新的 StarUML ID."""
    return _id_generator.generate()


def reset_generator(seed: int | None = None):
    """重置 ID 生成器."""
    global _id_generator
    _id_generator = StarUMLIDGenerator(seed)
