# StarUML Exporter for java2plantuml

将 Java 源代码分析结果导出为 StarUML (.mdj) 格式的工具。

## 功能特性

- 导出类、接口、枚举到 StarUML 模型
- 支持属性和方法的完整导出（可见性、静态、final 等修饰符）
- 自动识别和创建以下关系：
  - **继承关系** (UMLGeneralization)
  - **实现关系** (UMLInterfaceRealization)
  - **关联关系** (UMLAssociation) - 基于字段类型
  - **依赖关系** (UMLDependency) - 基于方法参数和返回值
- 生成有效的 StarUML ID 引用

## 项目结构

```
starumlexporter/
├── __init__.py          # 包入口，导出 StarUMLExporter 类
├── __main__.py          # 模块入口，支持 python -m starumlexporter
├── cli.py               # 命令行接口
├── id_generator.py      # StarUML 风格 ID 生成器
├── model_builder.py     # StarUML 模型元素构建器
├── exporter.py          # 主导出逻辑
└── README.md            # 本文件
```

## 使用方法

### 方式一：命令行

```bash
# 分析单个 Java 文件
python -m starumlexporter path/to/MyClass.java output.mdj

# 分析整个目录
python -m starumlexporter path/to/project/src/ output.mdj

# 或者直接运行 CLI
python starumlexporter/cli.py path/to/src/ output.mdj
```

### 方式二：代码中调用

```python
from java2plantuml import JavaProjectAnalyzer
from starumlexporter import StarUMLExporter

# 1. 分析 Java 项目
analyzer = JavaProjectAnalyzer()
analyzer.analyze_directory("path/to/java/project")
analyzer.analyze_relations()

# 2. 导出为 StarUML 格式
exporter = StarUMLExporter()
exporter.export_to_file(analyzer, "output.mdj", "My Project")

# 或者获取 JSON 字符串
json_str = exporter.export_to_string(analyzer, "My Project")
print(json_str)
```

### 方式三：获取 JSON 字典

```python
from starumlexporter import StarUMLExporter

exporter = StarUMLExporter()
project_dict = exporter.export(analyzer, "My Project")

# 现在 project_dict 是一个可以直接序列化为 JSON 的字典
import json
with open("output.mdj", "w") as f:
    json.dump(project_dict, f, indent=2)
```

## 生成的 .mdj 文件结构

```json
{
  "_type": "Project",
  "_id": "AAAAAAFF+h6SjaM2Hec=",
  "name": "Java Project",
  "ownedElements": [
    {
      "_type": "UMLModel",
      "_id": "...",
      "name": "Model",
      "ownedElements": [
        {
          "_type": "UMLClass",
          "_id": "...",
          "name": "User",
          "visibility": "public",
          "attributes": [...],
          "operations": [...]
        },
        {
          "_type": "UMLGeneralization",
          "_id": "...",
          "source": {"$ref": "..."},
          "target": {"$ref": "..."}
        }
      ]
    }
  ]
}
```

## 在 StarUML 中打开

1. 启动 StarUML
2. 选择 **File → Import → StarUML Project (.mdj)**
3. 选择生成的 `.mdj` 文件
4. 在 **Model Explorer** 中查看导入的模型

**注意**：由于目前只生成了模型层（Model），没有视图层（View），你需要：
- 在 StarUML 中手动创建类图（Class Diagram）
- 从 Model Explorer 拖拽类到画布上
- StarUML 会自动创建视图元素

## 与 PlantUML 的对比

| 特性 | PlantUML | StarUML (.mdj) |
|-----|---------|---------------|
| 文件格式 | 纯文本 (.puml) | JSON (.mdj) |
| 可编辑性 | 文本编辑 | 可视化编辑 |
| 模型+视图 | 仅模型，自动布局 | 分离，需手动布局 |
| 复杂度 | 简单 | 复杂（需要ID、引用等） |
| 工具支持 | 广泛 | 需要 StarUML |

## 待实现功能

- [ ] 视图层（UMLClassView 等）生成
- [ ] 自动布局算法
- [ ] UMLPackage 嵌套结构
- [ ] 更完善的泛型类型处理
- [ ] 注释（UMLComment）支持

## ID 生成说明

StarUML 使用特定格式的 ID 进行元素引用，格式类似：
```
AAAAAAFF+h6SjaM2Hec=
```

本工具实现了兼容的 ID 生成器，确保：
- 每个元素有唯一 ID
- 引用使用 `$ref` 语法
- ID 格式与 StarUML 兼容

## 依赖

- `java2plantuml` - 本项目的核心 Java 分析模块
- `javalang` - Java 语法解析（通过 java2plantuml 引入）

## 许可证

与本项目一致（MIT）
