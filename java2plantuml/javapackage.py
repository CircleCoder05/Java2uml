from javalang.tree import ClassDeclaration, InterfaceDeclaration, EnumDeclaration

from .javaclass import JavaClass, JavaInterface, JavaEnum
from .javacontext import JavaClassContext

class JavaPackage:
    attrs = ['name', 'classes']

    def __init__(self, name: str):
        self.name = name
        self.classes : dict[str, JavaClass | JavaInterface | JavaEnum] = {}

    def parse(self, declarations: list, context: JavaClassContext | None = None):
        if context is None:
            context = JavaClassContext([], self)
        
        for declaration in declarations:
            if isinstance(declaration, ClassDeclaration) and declaration.name not in self.classes: #type: ignore
                class_ = JavaClass(declaration, context)
                self.classes[class_.name] = class_
            elif isinstance(declaration, InterfaceDeclaration) and declaration.name not in self.classes: #type: ignore
                interface_ = JavaInterface(declaration, context)
                self.classes[interface_.name] = interface_
            elif isinstance(declaration, EnumDeclaration) and declaration.name not in self.classes: #type: ignore
                enum_ = JavaEnum(declaration, context)
                self.classes[enum_.name] = enum_
            else:
                pass

    def __str__(self):
        output = f'package {self.name}' + ' {\n'
        classes_dict_value = self.classes.values()
        for class_ in classes_dict_value:
            output += str(class_)
        output += '}\n'
        return output
    
    def parse_relations(self):
        classes_dict_value = self.classes.values()
        for class_ in classes_dict_value:
            class_.parse_relationships()
    
    @property
    def relations_list(self):
        relations = []
        classes_dict_value = self.classes.values()
        for class_ in classes_dict_value:
            relations.extend(class_.relations_list)
        #给每个关系添加package.前缀
        return list(map(lambda x: f'{self.name}.{x}', relations))
