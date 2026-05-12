"""StarUML 导出器主模块.

将 Java 分析结果导出为 StarUML .mdj 文件.
"""

from __future__ import annotations

import json
from typing import Any

from java2plantuml.javaanalyzer import JavaAnalyzer, JavaProjectAnalyZer
from java2plantuml.javaclass import JavaClass, JavaInterface, JavaEnum
from java2plantuml.javamethod import JavaMethod, JavaConstructor
from java2plantuml.javavariable import JavaField

from .model_builder import ModelBuilder
from .id_generator import reset_generator


class StarUMLExporter:
    """将 Java 分析结果导出为 StarUML MDJ 格式."""

    def __init__(self):
        """初始化导出器."""
        self.builder = ModelBuilder()
        self.class_id_map: dict[str, str] = {}  # 类全名 -> ID
        self.model_classes: list[dict] = []  # 模型中的类元素
        self.model_relations: list[dict] = []  # 模型中的关系元素

    def export(
        self,
        analyzer: JavaAnalyzer | JavaProjectAnalyZer,
        project_name: str = "Java Project",
    ) -> dict:
        """导出分析结果为 StarUML 模型.

        Args:
            analyzer: Java 分析器（已分析过文件）
            project_name: 项目名称

        Returns:
            StarUML 格式的 JSON 字典
        """
        # 重置 ID 生成器以获得一致的 ID
        reset_generator()

        # 清理之前的数据
        self.class_id_map.clear()
        self.model_classes.clear()
        self.model_relations.clear()

        # 创建项目结构
        project_id, project = self.builder.create_project(project_name)
        model_id, model = self.builder.create_uml_model("Model", project_id)
        project["ownedElements"].append(model)

        # 获取实际的分析器
        if isinstance(analyzer, JavaProjectAnalyZer):
            inner_analyzer = analyzer._JavaProjectAnalyZer__analyzer  # type: ignore
        else:
            inner_analyzer = analyzer

        # 第一步：创建所有类和包结构
        for package_name, package in inner_analyzer.packages.items():
            self._process_package(package_name, package, model_id)

        # 第二步：处理继承和实现关系
        self._process_inheritance_and_realization(inner_analyzer)

        # 第三步：处理关联和依赖关系
        self._process_associations_and_dependencies(inner_analyzer)

        # 去掉空的 ownedElements（与 StarUML 原生导出一致，避免空数组引发校验问题）
        for cls in self.model_classes:
            owned = cls.get("ownedElements")
            if isinstance(owned, list) and len(owned) == 0:
                del cls["ownedElements"]

        # 将类添加到模型（关系现在放在类的 ownedElements 里）
        model["ownedElements"].extend(self.model_classes)

        # 验证：确保所有直接子元素都有 _parent 指向 model
        for element in model["ownedElements"]:
            if "_parent" not in element:
                element["_parent"] = {"$ref": model_id}

        return project

    def export_to_file(
        self,
        analyzer: JavaAnalyzer | JavaProjectAnalyZer,
        output_path: str,
        project_name: str = "Java Project",
    ) -> None:
        """导出并保存到文件.

        Args:
            analyzer: Java 分析器
            output_path: 输出文件路径（.mdj）
            project_name: 项目名称
        """
        project = self.export(analyzer, project_name)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=2, ensure_ascii=False)

    def export_to_string(
        self,
        analyzer: JavaAnalyzer | JavaProjectAnalyZer,
        project_name: str = "Java Project",
    ) -> str:
        """导出为 JSON 字符串.

        Args:
            analyzer: Java 分析器
            project_name: 项目名称

        Returns:
            JSON 字符串
        """
        project = self.export(analyzer, project_name)
        return json.dumps(project, indent=2, ensure_ascii=False)

    def _process_package(
        self,
        package_name: str,
        package,
        model_id: str,
    ) -> None:
        """处理包及其中的类."""
        # 对于简单包，直接将类放在模型下
        # 复杂包结构可以用 UMLPackage 嵌套

        for class_name, class_obj in package.classes.items():
            full_class_name = f"{package_name}.{class_name}"
            class_element = self._create_class_element(
                class_obj, full_class_name, model_id
            )
            if class_element:
                self.model_classes.append(class_element)

    def _create_class_element(
        self,
        class_obj: JavaClass | JavaInterface | JavaEnum,
        full_class_name: str,
        parent_id: str,
    ) -> dict | None:
        """根据 Java 类对象创建 StarUML 类元素."""

        is_interface = isinstance(class_obj, JavaInterface)
        is_enum = isinstance(class_obj, JavaEnum)

        # 先创建类（不带属性和方法，后面再添加）
        class_id, class_element = self.builder.create_class(
            name=class_obj.name,
            attributes=None,
            operations=None,
            is_abstract="abstract" in getattr(class_obj, "modifiers", []),
            is_interface=is_interface,
            parent_id=parent_id,
            visibility=self._get_visibility_from_modifiers(
                getattr(class_obj, "modifiers", [])
            ),
        )

        # 记录类 ID 映射
        self.class_id_map[full_class_name] = class_id
        self.class_id_map[class_obj.name] = class_id

        # 现在用 class_id 作为 parent 创建属性和方法
        attributes: list[dict] = []
        if not is_interface and hasattr(class_obj, "fields"):
            for field in class_obj.fields:
                if isinstance(field, JavaField):
                    attr = self._convert_field_to_attribute(field, class_id)
                    attributes.append(attr)

        # 枚举常量作为属性
        if is_enum and hasattr(class_obj, "constants"):
            for constant in class_obj.constants:
                attr = self.builder.create_attribute(
                    name=constant,
                    type_str=class_obj.name,
                    visibility="public",
                    is_static=True,
                    is_final=True,
                    parent_id=class_id,
                )
                attributes.append(attr)

        # 处理操作（方法）
        operations: list[dict] = []

        # 构造函数
        if hasattr(class_obj, "constructors"):
            for constructor in class_obj.constructors:
                if isinstance(constructor, JavaConstructor):
                    op = self._convert_constructor_to_operation(constructor, class_id)
                    operations.append(op)

        # 普通方法
        if hasattr(class_obj, "methods"):
            for method in class_obj.methods:
                if isinstance(method, JavaMethod):
                    op = self._convert_method_to_operation(method, class_id)
                    operations.append(op)

        # 添加属性和方法到类元素
        if attributes:
            class_element["attributes"] = attributes
        if operations:
            class_element["operations"] = operations

        # ownedElements：仅在有关系时写入（空数组部分 StarUML 版本会异常）
        class_element["ownedElements"] = []

        return class_element

    def _convert_field_to_attribute(self, field: JavaField, parent_id: str) -> dict:
        """将 JavaField 转换为 UMLAttribute."""
        visibility = self._get_visibility_from_modifiers(field.modifiers)
        is_static = "static" in field.modifiers
        is_final = "final" in field.modifiers

        # 处理数组类型
        type_str = field.type
        if hasattr(field, "dimensions") and field.dimensions:
            type_str += "[]" * len(field.dimensions)

        return self.builder.create_attribute(
            name=field.name,
            type_str=type_str,
            visibility=visibility,
            is_static=is_static,
            is_final=is_final,
            parent_id=parent_id,
        )

    def _convert_method_to_operation(self, method: JavaMethod, parent_id: str) -> dict:
        """将 JavaMethod 转换为 UMLOperation."""
        visibility = self._get_visibility_from_modifiers(method.modifiers)
        is_static = "static" in method.modifiers
        is_abstract = "abstract" in method.modifiers

        # 先创建操作（不带参数）
        op = self.builder.create_operation(
            name=method.name,
            return_type=method.return_type,
            parameters=None,
            visibility=visibility,
            is_static=is_static,
            is_abstract=is_abstract,
            parent_id=parent_id,
        )
        op_id = op["_id"]

        # 用 op_id 作为 parent 创建参数
        parameters: list[dict] = []
        if hasattr(method, "parameters"):
            for param in method.parameters:
                type_str = param.type
                if hasattr(param, "dimensions") and param.dimensions:
                    type_str += "[]" * len(param.dimensions)
                if getattr(param, "varargs", False):
                    type_str += "..."

                param_dict = self.builder.create_parameter(
                    name=param.name,
                    type_str=type_str,
                    parent_id=op_id,
                )
                parameters.append(param_dict)

        if parameters:
            op["parameters"] = parameters

        return op

    def _convert_constructor_to_operation(self, constructor: JavaConstructor, parent_id: str) -> dict:
        """将 JavaConstructor 转换为 UMLOperation."""
        visibility = self._get_visibility_from_modifiers(constructor.modifiers)

        # 先创建操作（不带参数）
        op = self.builder.create_operation(
            name=constructor.name,
            return_type="",
            parameters=None,
            visibility=visibility,
            is_static=False,
            is_abstract=False,
            parent_id=parent_id,
        )
        # 标记为构造函数
        op["stereotype"] = "constructor"
        op_id = op["_id"]

        # 用 op_id 作为 parent 创建参数
        parameters: list[dict] = []
        if hasattr(constructor, "parameters"):
            for param in constructor.parameters:
                type_str = param.type
                if hasattr(param, "dimensions") and param.dimensions:
                    type_str += "[]" * len(param.dimensions)
                if getattr(param, "varargs", False):
                    type_str += "..."

                param_dict = self.builder.create_parameter(
                    name=param.name,
                    type_str=type_str,
                    parent_id=op_id,
                )
                parameters.append(param_dict)

        if parameters:
            op["parameters"] = parameters

        return op

    def _process_inheritance_and_realization(self, analyzer: JavaAnalyzer) -> None:
        """处理继承和实现关系."""
        for package_name, package in analyzer.packages.items():
            for class_name, class_obj in package.classes.items():
                source_full_name = f"{package_name}.{class_name}"
                source_id = self.class_id_map.get(source_full_name)

                if not source_id:
                    continue

                # 获取类元素
                class_element = self._find_class_element(source_id)
                if not class_element:
                    continue

                # 处理继承（extends）
                if hasattr(class_obj, "extends") and class_obj.extends:
                    extends = class_obj.extends
                    if isinstance(extends, str):
                        extends = [extends]

                    for parent_class in extends:
                        target_id = self._find_class_id(parent_class, package_name, analyzer)
                        if target_id:
                            gen = self.builder.create_generalization(
                                source_id=source_id,
                                target_id=target_id,
                                parent_id=source_id,
                            )
                            class_element["ownedElements"].append(gen)

                # 处理实现（implements）
                if hasattr(class_obj, "implements") and class_obj.implements:
                    for interface_name in class_obj.implements:
                        target_id = self._find_class_id(interface_name, package_name, analyzer)
                        if target_id:
                            realization = self.builder.create_interface_realization(
                                source_id=source_id,
                                target_id=target_id,
                                parent_id=source_id,
                            )
                            class_element["ownedElements"].append(realization)

    def _process_associations_and_dependencies(self, analyzer: JavaAnalyzer) -> None:
        """处理关联和依赖关系."""
        for package_name, package in analyzer.packages.items():
            for class_name, class_obj in package.classes.items():
                source_full_name = f"{package_name}.{class_name}"
                source_id = self.class_id_map.get(source_full_name)

                if not source_id:
                    continue

                # 获取类元素
                class_element = self._find_class_element(source_id)
                if not class_element:
                    continue

                # 处理关联关系（字段类型）
                if hasattr(class_obj, "relations") and class_obj.relations:
                    for relation_target in class_obj.relations:
                        target_id = self._find_class_id(relation_target, package_name, analyzer)
                        if target_id and target_id != source_id:
                            assoc = self.builder.create_association(
                                source_id=source_id,
                                target_id=target_id,
                                parent_id=source_id,
                            )
                            class_element["ownedElements"].append(assoc)

                # 处理依赖关系（从方法/构造函数中解析）
                dependencies = set()

                # 从方法收集依赖
                if hasattr(class_obj, "methods"):
                    for method in class_obj.methods:
                        if hasattr(method, "dependencies") and method.dependencies:
                            dependencies.update(method.dependencies)

                # 从构造函数收集依赖
                if hasattr(class_obj, "constructors"):
                    for constructor in class_obj.constructors:
                        if hasattr(constructor, "dependencies") and constructor.dependencies:
                            dependencies.update(constructor.dependencies)

                # 创建依赖关系
                for dep_target in dependencies:
                    target_id = self._find_class_id(dep_target, package_name, analyzer)
                    if target_id and target_id != source_id:
                        # 检查是否已经是关联关系
                        if not self._has_association_in_class(class_element, source_id, target_id):
                            dep = self.builder.create_dependency(
                                source_id=source_id,
                                target_id=target_id,
                                parent_id=source_id,
                            )
                            class_element["ownedElements"].append(dep)

    def _find_class_id(
        self,
        class_name: str,
        current_package: str,
        analyzer: JavaAnalyzer,
    ) -> str | None:
        """查找类的 ID，支持多种引用方式."""
        # 1. 尝试直接查找（简单名称或全名）
        if class_name in self.class_id_map:
            return self.class_id_map[class_name]

        # 2. 在当前包中查找
        full_name = f"{current_package}.{class_name}"
        if full_name in self.class_id_map:
            return self.class_id_map[full_name]

        # 3. 在所有包中查找
        for pkg_name, pkg in analyzer.packages.items():
            test_full_name = f"{pkg_name}.{class_name}"
            if test_full_name in self.class_id_map:
                return self.class_id_map[test_full_name]
            if class_name in pkg.classes:
                return self.class_id_map.get(class_name)

        return None

    def _find_class_element(self, class_id: str) -> dict | None:
        """根据类 ID 查找类元素."""
        for element in self.model_classes:
            if element["_id"] == class_id:
                return element
        return None

    def _has_association_in_class(self, class_element: dict, source_id: str, target_id: str) -> bool:
        """检查类的 ownedElements 中是否已存在关联关系."""
        for element in class_element.get("ownedElements", []):
            if element["_type"] == "UMLAssociation":
                end1 = element.get("end1", {})
                end2 = element.get("end2", {})
                ref1 = end1.get("reference", {}).get("$ref", "")
                ref2 = end2.get("reference", {}).get("$ref", "")

                if (ref1 == source_id and ref2 == target_id) or \
                   (ref1 == target_id and ref2 == source_id):
                    return True
        return False

    def _has_association(self, source_id: str, target_id: str) -> bool:
        """检查是否已存在两个类之间的关联关系（全局）."""
        # 检查所有类的 ownedElements
        for class_element in self.model_classes:
            if self._has_association_in_class(class_element, source_id, target_id):
                return True
        return False

    def _get_visibility_from_modifiers(self, modifiers: set[str] | list[str]) -> str:
        """从修饰符集合中提取可见性."""
        if isinstance(modifiers, (list, set)):
            if "public" in modifiers:
                return "public"
            if "private" in modifiers:
                return "private"
            if "protected" in modifiers:
                return "protected"
        return "package"  # default
