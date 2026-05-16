# java2uml

从 **`.java` 源码**（不解析字节码）生成 **PlantUML** 类图文本，或导出可在 **StarUML** 中打开的 **`.mdj`** 模型。解析基于 [javalang](https://github.com/c2nes/javalang)。

**环境：** Python 3.11 及以上。

## 安装

```bash
pip install java2uml
```

## 使用

```bash
java2uml <路径> -f plantuml              # 默认；结果打到标准输出
java2uml <路径> -f plantuml -o out.puml   # 写入文件
java2uml <路径> -f mdj -o model.mdj       # StarUML；不写 -o 时默认为 output.mdj
java2uml <路径> -f mdj -v                 # -v：逐个文件打印解析情况
java2uml --help
```

`<路径>` 为单个 `.java` 文件或目录（递归扫描）。`-f staruml` 与 `-f mdj` 相同。

兼容旧命令：`java2plantuml`、`java2staruml`（仍由本包提供）。

## 说明

支持多文件、包、类 / 接口 / 枚举、字段与方法及常见关系；复杂语法与内部类等可能不完整。`.mdj` 为模型层，在 StarUML 里需自行建图或拖入类。
