from javalang.tree import MethodDeclaration, ConstructorDeclaration, ReferenceType, MethodInvocation

from .java2plantumltool import Java2PlantUMLTool, UMLRelationship
from .javavariable import JavaFormalParameter
from .javatype import JavaType
from .javacontext import JavaClassContext

class BaseJavaMethod:
    def __init__(self, declaration: MethodDeclaration, context: JavaClassContext|None = None):
        self.name = declaration.name #type: ignore
        self.return_type = JavaType.resolve_type(declaration.return_type) #type: ignore
        self.origin_return_type = declaration.return_type #type: ignore
        self.modifiers = declaration.modifiers #type: ignore
        self.parameters = [JavaFormalParameter(p) for p in declaration.parameters] #type: ignore
        self.body = declaration.body #type: ignore
        self.throws = declaration.throws #type: ignore
        self.dependencies = []
        # self.context = context
    
    def __print_plantuml__(self, has_return: bool = True):
        return f"{Java2PlantUMLTool.print_modifiers(self.modifiers)}{self.return_type} {self.name}({', '.join([str(p) for p in self.parameters])})" if has_return else f"{self.name}({', '.join([str(p) for p in self.parameters])})"

    def _strategy_parse_dependencies(self, context: JavaClassContext | None, ignore: set[str] | None = None, check_return: bool = True):
        if context is None:
            return
        types_set:set[str] = set()
        if check_return:
            reference_types = JavaType.resolve_reference_type(self.origin_return_type)
            for t in reference_types:
                if ignore is None or t not in ignore:
                    types_set.add(t)
        
        for parameter in self.parameters:
            reference_types = JavaType.resolve_reference_type(parameter.origin_type)
            for t in reference_types:
                if ignore is None or t not in ignore:
                    types_set.add(t)
        
        if self.body:
            for statement in self.body:
                for _, node in statement.filter(ReferenceType):
                    if ignore is None or node.name not in ignore:
                        types_set.add(node.name)
                for _, node in statement.filter(MethodInvocation):
                    qualifier = BaseJavaMethod.__handle_MethodInvocation(node)
                    if qualifier is not None and (ignore is None or node not in ignore):
                        types_set.add(qualifier)
                    

        for t in types_set:
            class_path = context.get_full_class_path(t)
            if class_path is not None:
                self.dependencies.append(class_path)
    
    @staticmethod
    def __handle_MethodInvocation(method_invocation: MethodInvocation):
        parts = []
        current = method_invocation.qualifier #type:ignore
        if isinstance(current, str): 
            return current
        else:
            return None

    @property
    def dependencies_list(self):
        return [f"{self.name} {UMLRelationship.DEPEND} {d}" for d in self.dependencies]
    
    @property
    def is_entrance(self):
        return self.name == "main" and self.return_type == "void" and self.modifiers.__len__() == 2 and "public" in self.modifiers and "static" in self.modifiers and self.parameters.__len__() == 1 and self.parameters[0].type == "String" and self.parameters[0].dimensions.__len__() == 1

class JavaMethod(BaseJavaMethod):
    # 'throws' for future
    attrs = ['name', 'return_type', 'modifiers', 'parameters', 'throws', 'body', 'dependencies']
    def __init__(self, declaration: MethodDeclaration, context: JavaClassContext|None = None):
        self.name = declaration.name #type: ignore
        self.return_type = JavaType.resolve_type(declaration.return_type) #type: ignore
        self.modifiers = declaration.modifiers #type: ignore
        self.parameters = [JavaFormalParameter(p) for p in declaration.parameters] #type: ignore
        self.body = declaration.body #type: ignore
        self.throws = declaration.throws #type: ignore
        self.dependencies = []
        self.origin_return_type = declaration.return_type #type: ignore
        # self.context = context
    
    def __str__(self):
        return f"{Java2PlantUMLTool.print_modifiers(self.modifiers)}{self.return_type} {self.name}({', '.join([str(p) for p in self.parameters])})"

    def parse_dependencies(self, context: JavaClassContext | None, ignore: set[str] | None = None):
        self._strategy_parse_dependencies(context, ignore, True)


class JavaConstructor(BaseJavaMethod):
    attrs = ['name', 'modifiers', 'parameters', 'throw', 'body', 'dependencies']
    def __init__(self, declaration: ConstructorDeclaration, context: JavaClassContext | None = None):
        self.name = declaration.name #type: ignore
        self.modifiers = declaration.modifiers #type: ignore
        self.parameters = [JavaFormalParameter(p) for p in declaration.parameters] #type: ignore
        self.body = declaration.body #type: ignore
        self.throws = declaration.throws #type: ignore
        # self.context = context
        self.dependencies = []

    def __str__(self):
        return f"{Java2PlantUMLTool.print_modifiers(self.modifiers)}{self.name}({', '.join([str(p) for p in self.parameters])})"

    def parse_dependencies(self, context: JavaClassContext | None, ignore: set[str] | None = None):
        self._strategy_parse_dependencies(context, ignore, False)
