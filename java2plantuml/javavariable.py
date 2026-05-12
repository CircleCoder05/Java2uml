import inspect
from javalang.tree import VariableDeclaration, FieldDeclaration, FormalParameter, ReferenceType

from .javatype import JavaType
from .java2plantumltool import Java2PlantUMLTool

class JavaField:
    # 'initial value' for future
    attrs = ['name', 'type', 'modifiers', 'documentation']

    def __new__(cls, *args, **kwargs):
        # 检查调用者是否是类本身
        cur_frame = inspect.currentframe()
        if cur_frame:
            caller_frame = cur_frame.f_back
            if caller_frame:
                caller_name = caller_frame.f_globals['__name__']
            
            # 如果调用者不是类本身，则不允许实例化
                if caller_name != __name__:
                    raise Exception("Cannot create instance of RestrictedClass directly. Use the static method 'resolve_fields' instead.")
        
        # 如果是类本身调用，则正常创建实例
        return super().__new__(cls)
    

    def __init__(self, origin_type: ReferenceType, type: str, modifiers: set[str], documentation: str, declaration: VariableDeclaration):
        self.name = declaration.name #type: ignore
        self.type = type 
        self.documentation = documentation
        self.modifiers = modifiers
        self.dimensions = declaration.dimensions #type: ignore
        self.origin_type = origin_type

    def __str__(self):
        return f"{Java2PlantUMLTool.print_modifiers(self.modifiers)}{self.type}{'[]' * self.dimensions.__len__()} {self.name}"

    @staticmethod
    def resolve_fields(declaration: FieldDeclaration):
        type = JavaType.resolve_type(declaration.type) #type: ignore
        modifiers = declaration.modifiers #type: ignore
        return [JavaField(declaration.type, type, modifiers, declaration.documentation, declarator) for declarator in declaration.declarators] #type: ignore


class JavaFormalParameter:
    attas = ["name", "type", 'modifiers', "varargs"]
    def __init__(self, param: FormalParameter):
        self.name = param.name #type: ignore
        self.modifiers = param.modifiers #type: ignore
        self.origin_type = param.type #type: ignore
        self.type = JavaType.resolve_type(param.type) #type: ignore  
        self.dimensions = param.type.dimensions #type: ignore
        self.varargs = param.varargs #type: ignore
    
    def __str__(self):
        return f"{Java2PlantUMLTool.print_modifiers(self.modifiers)}{self.type}{'[]'*self.dimensions.__len__()} {self.name}{'...' if self.varargs else ''}"
