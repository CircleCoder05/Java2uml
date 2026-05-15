# 快速开始

环境：**Python 3.11+**，本仓库根目录（含 `pyproject.toml`）。

## 安装

```cmd
pip install -e .
```

或安装已打好的 wheel：

```cmd
pip install dist\java2uml-0.2.0-py3-none-any.whl
```

（版本号以 `dist` 里实际文件名为准。）

---

## 统一命令 `java2uml`

`<路径>` 为**单个 `.java` 文件**或**目录**（递归扫描 `.java`）。

### PlantUML（文本）

```cmd
java2uml path\to\Your.java
java2uml path\to\src\ -f plantuml -o diagram.puml
```

默认 `-f plantuml`；不写 `-o` 时输出到**标准输出**（含 `@startuml` / `@enduml`）。

### StarUML（`.mdj`）

```cmd
java2uml path\to\src\ -f mdj -o output.mdj
java2uml path\to\src\ -f mdj -v
```

不写 `-o` 时默认 **`output.mdj`**。`-v` 打印每个文件的解析状态。

---

## 兼容命令（可选）

```cmd
java2plantuml path\to\src\
java2staruml path\to\src\ output.mdj
```

---

## 代码里调用（可选）

```python
from java2plantuml import JavaProjectAnalyzer
from java2staruml import StarUMLExporter

a = JavaProjectAnalyzer()
a.analyze_directory(r"path\to\java")
a.analyze_relations()
StarUMLExporter().export_to_file(a, r"path\to\out.mdj")
```

更细的说明见根目录 [readme.md](readme.md) 与 [java2staruml/README.md](java2staruml/README.md)。
