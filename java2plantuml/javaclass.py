from javalang.tree import ClassDeclaration, FieldDeclaration, ConstructorDeclaration, MethodDeclaration, ReferenceType, InterfaceDeclaration, EnumDeclaration, EnumBody, TypeDeclaration

from .javavariable import JavaField
from .javamethod import JavaMethod, JavaConstructor
from .javatype import JavaType
from .java2plantumltool import Java2PlantUMLTool, UMLRelationship
from .javacontext import JavaClassContext

class BaseJavaClass:
    """
    Base class for Java Classes.
    """
    attrs = ['name', 'modifiers', 'fields', 'constructors', 'methods', 'extends', 'implements', 'relations', 'inner_classes', 'context']
    def __init__(self, declaration: ClassDeclaration, context: JavaClassContext | None = None, relations:list[str] | None = None):
        self.name = declaration.name # type: ignore
        self.modifiers = declaration.modifiers # type: ignore
        self._parse_fields(declaration.fields)
        self._parse_constructors(declaration.constructors)
        self._parse_methods(declaration.methods) 
        self._parse_extends(declaration.extends) # type: ignore
        self._parse_implements(declaration.implements) # type: ignore
        self.relations : list[str] = relations.copy() if relations else []
        self._parse_inner_classes(declaration.body) # type: ignore
        self.context = context
        self._active = False

    def _parse_fields(self, declaration: list[FieldDeclaration]):
        self.fields:list[JavaField] = []
        for field in declaration:
            self.fields.extend(JavaField.resolve_fields(field))
    
    def _parse_constructors(self, declaration: list[ConstructorDeclaration]):
        self.constructors = []
        for constructor in declaration:
            self.constructors.append(JavaConstructor(constructor))

    def _parse_methods(self, declaration: list[MethodDeclaration]):
        self.methods: list[JavaMethod] = []
        for method in declaration:
            self.methods.append(JavaMethod(method))

    def _parse_extends(self, declarations: ReferenceType):
        if isinstance(declarations, list):
            self.extends = [JavaType.resolve_type(declaration) for declaration in declarations]
        elif declarations:
            self.extends = JavaType.resolve_type(declarations)
        else:
            self.extends = None

    def _parse_implements(self, declarations: list[ReferenceType]):
        if declarations:
            self.implements = [JavaType.resolve_type(declaration) for declaration in declarations]
        else:
            self.implements = None

    def _parse_inner_classes(self, declarations: list[TypeDeclaration]):
        self.inner_classes = []
        for declaration in declarations:
            if isinstance(declaration, ClassDeclaration):
                self.inner_classes.append(JavaClass(declaration)) 
            elif isinstance(declaration, InterfaceDeclaration):
                self.inner_classes.append(JavaInterface(declaration))
            elif isinstance(declaration, EnumDeclaration):
                self.inner_classes.append(JavaEnum(declaration))
            else:
                pass

    def _strategy_print_method(self, type: str, extends_enable: bool, implement_enable: bool, contents: list[str], indent: str=''):
        output = f"{indent}{Java2PlantUMLTool.print_modifiers(self.modifiers, True)}{type} {self.name}"

        if extends_enable and self.extends:
            if isinstance(self.extends, str):
                if self.context:
                    extend_full_class_path = self.context.get_full_class_path(self.extends)
                    output += f" extends {extend_full_class_path if extend_full_class_path else self.extends}"
                else:
                    output += f" extends {extends_enable}"
            else:
                if self.context:
                    cur_context = self.context
                    output += f" extends {', '.join(map(lambda x: cur_context.get_full_class_path(x) or x, self.extends))}"
                else:
                    output += f" extends {', '.join([extend for extend in self.extends if isinstance(extend, str)])}"
        
        if implement_enable and self.implements:
            if self.context:
                cur_context = self.context
                output += f" implements {', '.join(map(lambda x: cur_context.get_full_class_path(x) or x, self.implements))}"
            else:
                output += f" implements {', '.join([implement for implement in self.implements if isinstance(implement, str)])}"

        output += '{\n'
        for content in contents:
            items = getattr(self, content)
            if items is None:
                continue
            for item in items:
                output += f'{indent}\t{str(item)}\n'
        
        output += indent + '}\n'
        
        for inner_class in self.inner_classes:
            output += str(inner_class)
        
        return output
    
    def __parse_association(self):
        if self.context is None:
            return set()
        types_set: set[str] = set()
        for field in self.fields:
            reference_types = JavaType.resolve_reference_type(field.origin_type)
            for t in reference_types:
                types_set.add(t)
        for t in types_set:
            class_path = self.context.get_full_class_path(t)
            if class_path is not None:
                self.relations.append(class_path)
        return types_set
    
    def parse_relationships(self):
        ignore = self.__parse_association()
        # ignore = set(map(lambda x: x.type, self.fields))
        ignore.add(self.name)
        if getattr(self, 'constructors', None):
            for constructor in self.constructors:
                constructor.parse_dependencies(self.context, ignore)
        for method in self.methods:
            method.parse_dependencies(self.context, ignore)
        for inner_class in self.inner_classes:
            inner_class.parse_relationships()

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value: bool):
        self._active = value
        return value

    @property
    def relations_list(self):
        dependencies = set()
        if getattr(self, 'constructors', None):
            for constructor in self.constructors:
                dependencies.update(constructor.dependencies_list)
        for method in self.methods:
            dependencies.update(method.dependencies_list)
        dependencies = set(dependencies)
        # 给每个result加上self.name:前缀
        result = list(map(lambda x: f"{self.name}::{x}", dependencies))
        for relation in self.relations:
            result.append(f"{self.name} {UMLRelationship.ASSOCIATE} {relation}")
        
        for inner_class in self.inner_classes:
            result.extend(inner_class.relations_list)
        
        return result


class JavaClass(BaseJavaClass):
    attrs = ['name', 'modifiers', 'fields', 'constructors', 'methods', 'extends', 'implements', 'relations', 'inner_classes', 'context']

    def __str__(self):
        return self._strategy_print_method('abstract' if 'abstract' in self.modifiers else 'class', True, True, ['fields', 'constructors', 'methods'], '\t')


class JavaInterface(BaseJavaClass):
    attrs = ['name', 'modifiers', 'fields', 'methods', 'extends', 'relations', 'inner_classes', 'context']
    def __init__(self, declaration: InterfaceDeclaration, context: JavaClassContext | None = None, relations:list[str] | None = None):
        self.name = declaration.name # type: ignore
        self.modifiers = declaration.modifiers # type: ignore
        self._parse_fields(declaration.fields)
        self._parse_methods(declaration.methods)
        self._parse_extends(declaration.extends) # type: ignore
        self.relations : list[str] = relations.copy() if relations else []
        self._parse_inner_classes(declaration.body) # type: ignore
        self.context = context
        self.active = False

    def __str__(self):
        return self._strategy_print_method('interface', True, False, ['fields', 'methods'], '\t')


class JavaEnum(BaseJavaClass):
    attrs = ['name', 'modifiers', 'constants', 'constructors', 'methods', 'implements', 'relations', 'inner_classes', 'context']
    def __init__(self, declaration: EnumDeclaration, context: JavaClassContext | None = None, relations:list[str] | None = None):
        self.name = declaration.name # type: ignore
        self.modifiers = declaration.modifiers # type: ignore
        self._parse_constants(declaration.body) # type: ignore
        self._parse_constructors(declaration.constructors)
        self._parse_methods(declaration.methods)
        self._parse_implements(declaration.implements) # type: ignore
        self.relations : list[str] = relations.copy() if relations else []
        self._parse_inner_classes(declaration.body) # type: ignore
        self.context = context
        self.active = False

    def _parse_constants(self, body: EnumBody):
        self.constants = []
        for enum_constant_declaration in body.constants: #type: ignore
            self.constants.append(enum_constant_declaration.name)

    def __str__(self):
        return self._strategy_print_method('enum', False, True, ['constants', 'constructors', 'methods'], '\t')
    
    def parse_relationships(self):
        # ignore = set(map(lambda x: x.type, self.fields))
        ignore = {self.name}
        if getattr(self, 'constructors', None):
            for constructor in self.constructors:
                constructor.parse_dependencies(self.context, ignore)
        for method in self.methods:
            method.parse_dependencies(self.context, ignore)
        for inner_class in self.inner_classes:
            inner_class.parse_relationships()
