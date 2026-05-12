"""StarUML 模型构建器.

负责将 Java 分析结果转换为 StarUML 的 JSON 模型结构.
"""

from __future__ import annotations

from typing import Any

from .id_generator import generate_id


class ModelBuilder:
    """构建 StarUML 模型元素."""

    def __init__(self):
        self._elements: list[dict] = []
        self._id_map: dict[str, str] = {}  # 用于跟踪已创建的模型 ID

    def create_project(self, name: str = "Java Project") -> tuple[str, dict]:
        """创建项目根元素.

        Returns:
            (project_id, project_element)
        """
        project_id = generate_id()
        project = {
            "_type": "Project",
            "_id": project_id,
            "name": name,
            "ownedElements": [],
        }
        return project_id, project

    def create_uml_model(self, name: str = "Model", parent_id: str | None = None) -> tuple[str, dict]:
        """创建 UMLModel 元素.

        Returns:
            (model_id, model_element)
        """
        model_id = generate_id()
        model: dict[str, Any] = {
            "_type": "UMLModel",
            "_id": model_id,
            "name": name,
            "ownedElements": [],
        }
        if parent_id:
            model["_parent"] = {"$ref": parent_id}
        return model_id, model

    def create_class(
        self,
        name: str,
        attributes: list[dict] | None = None,
        operations: list[dict] | None = None,
        is_abstract: bool = False,
        is_interface: bool = False,
        parent_id: str | None = None,
        visibility: str = "public",
    ) -> tuple[str, dict]:
        """创建 UMLClass 或 UMLInterface 元素.

        Returns:
            (class_id, class_element)
        """
        class_id = generate_id()

        if is_interface:
            element_type = "UMLInterface"
        else:
            element_type = "UMLClass"

        class_element: dict[str, Any] = {
            "_type": element_type,
            "_id": class_id,
            "name": name,
            "visibility": self._map_visibility(visibility),
            "isAbstract": is_abstract and not is_interface,
            "isFinal": False,
            "isLeaf": False,
        }

        if parent_id:
            class_element["_parent"] = {"$ref": parent_id}

        if attributes:
            class_element["attributes"] = attributes

        if operations:
            class_element["operations"] = operations

        return class_id, class_element

    def create_attribute(
        self,
        name: str,
        type_str: str,
        visibility: str = "private",
        is_static: bool = False,
        is_final: bool = False,
        parent_id: str | None = None,
    ) -> dict:
        """创建 UMLAttribute 元素."""
        attr_id = generate_id()
        attr: dict[str, Any] = {
            "_type": "UMLAttribute",
            "_id": attr_id,
            "name": name,
            "visibility": self._map_visibility(visibility),
            "type": type_str,
            "isStatic": is_static,
            "isFinal": is_final,
            "isReadOnly": is_final,
        }
        if parent_id:
            attr["_parent"] = {"$ref": parent_id}
        return attr

    def create_operation(
        self,
        name: str,
        return_type: str,
        parameters: list[dict] | None = None,
        visibility: str = "public",
        is_static: bool = False,
        is_abstract: bool = False,
        parent_id: str | None = None,
    ) -> dict:
        """创建 UMLOperation 元素."""
        op_id = generate_id()
        operation: dict[str, Any] = {
            "_type": "UMLOperation",
            "_id": op_id,
            "name": name,
            "visibility": self._map_visibility(visibility),
            "isStatic": is_static,
            "isAbstract": is_abstract,
            "isFinal": False,
        }

        if return_type and return_type != "void":
            operation["type"] = return_type

        if parameters:
            operation["parameters"] = parameters

        if parent_id:
            operation["_parent"] = {"$ref": parent_id}

        return operation

    def create_parameter(
        self,
        name: str,
        type_str: str,
        direction: str = "in",
        parent_id: str | None = None,
    ) -> dict:
        """创建 UMLParameter 元素."""
        param_id = generate_id()
        param: dict[str, Any] = {
            "_type": "UMLParameter",
            "_id": param_id,
            "name": name,
            "type": type_str,
            "direction": direction,
        }
        if parent_id:
            param["_parent"] = {"$ref": parent_id}
        return param

    def create_generalization(
        self,
        source_id: str,
        target_id: str,
        parent_id: str | None = None,
    ) -> dict:
        """创建 UMLGeneralization（继承关系）元素."""
        gen_id = generate_id()
        generalization: dict[str, Any] = {
            "_type": "UMLGeneralization",
            "_id": gen_id,
            "source": {"$ref": source_id},
            "target": {"$ref": target_id},
        }
        if parent_id:
            generalization["_parent"] = {"$ref": parent_id}
        return generalization

    def create_interface_realization(
        self,
        source_id: str,
        target_id: str,
        parent_id: str | None = None,
    ) -> dict:
        """创建 UMLInterfaceRealization（实现关系）元素."""
        real_id = generate_id()
        realization: dict[str, Any] = {
            "_type": "UMLInterfaceRealization",
            "_id": real_id,
            "source": {"$ref": source_id},
            "target": {"$ref": target_id},
        }
        if parent_id:
            realization["_parent"] = {"$ref": parent_id}
        return realization

    def create_association(
        self,
        source_id: str,
        target_id: str,
        name: str = "",
        parent_id: str | None = None,
    ) -> dict:
        """创建 UMLAssociation（关联关系）元素.

        StarUML 要求 UMLAssociationEnd 的 _parent 指向所属 UMLAssociation，
        否则模型不完整，类往往无法拖到画布上。
        """
        assoc_id = generate_id()
        end1_id = generate_id()
        end2_id = generate_id()
        assoc: dict[str, Any] = {
            "_type": "UMLAssociation",
            "_id": assoc_id,
            "name": name,
            "end1": {
                "_type": "UMLAssociationEnd",
                "_id": end1_id,
                "_parent": {"$ref": assoc_id},
                "reference": {"$ref": source_id},
                "multiplicity": "1",
            },
            "end2": {
                "_type": "UMLAssociationEnd",
                "_id": end2_id,
                "_parent": {"$ref": assoc_id},
                "reference": {"$ref": target_id},
                "multiplicity": "1",
            },
        }
        if parent_id:
            assoc["_parent"] = {"$ref": parent_id}
        return assoc

    def create_dependency(
        self,
        source_id: str,
        target_id: str,
        name: str = "",
        parent_id: str | None = None,
    ) -> dict:
        """创建 UMLDependency（依赖关系）元素."""
        dep_id = generate_id()
        dependency: dict[str, Any] = {
            "_type": "UMLDependency",
            "_id": dep_id,
            "source": {"$ref": source_id},
            "target": {"$ref": target_id},
            "name": name,
        }
        if parent_id:
            dependency["_parent"] = {"$ref": parent_id}
        return dependency

    def create_package(self, name: str, parent_id: str | None = None) -> tuple[str, dict]:
        """创建 UMLPackage 元素.

        Returns:
            (package_id, package_element)
        """
        pkg_id = generate_id()
        package: dict[str, Any] = {
            "_type": "UMLPackage",
            "_id": pkg_id,
            "name": name,
            "ownedElements": [],
        }
        if parent_id:
            package["_parent"] = {"$ref": parent_id}
        return pkg_id, package

    def _map_visibility(self, visibility: str) -> str:
        """将 Java 可见性映射为 StarUML 格式."""
        mapping = {
            "public": "public",
            "private": "private",
            "protected": "protected",
            "default": "package",
            "package": "package",
        }
        return mapping.get(visibility, "public")

    def track_id(self, key: str, element_id: str):
        """跟踪 ID 映射，用于后续引用."""
        self._id_map[key] = element_id

    def get_tracked_id(self, key: str) -> str | None:
        """获取已跟踪的 ID."""
        return self._id_map.get(key)
