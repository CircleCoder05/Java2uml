from javalang.tree import BasicType, ReferenceType

class JavaType:
    @staticmethod
    def resolve_type(type_node, all_classes=None):
        """增强类型解析的容错处理"""
        if type_node is None:
            return 'void'
        
        try:
            if isinstance(type_node, ReferenceType):
                base_type = type_node.name #type: ignore
                if type_node.sub_type: #type: ignore
                    sub_type = JavaType.resolve_type(type_node.sub_type) #type: ignore
                    return f"{base_type}.{sub_type}"
                if type_node.arguments:  # 处理泛型 #type: ignore
                    args = [JavaType.resolve_type(arg.type) for arg in type_node.arguments] #type: ignore
                    return f"{base_type}<{', '.join(filter(lambda x: x != None, args))}>"
                return base_type
            elif isinstance(type_node, BasicType):
                return type_node.name #type: ignore
            elif hasattr(type_node, 'name'):
                return type_node.name
        except AttributeError as e:
            print(f"Type resolve error: {str(e)}")
        return str(type_node)
    @staticmethod
    def resolve_reference_type(type_node):
        if type_node is None:
            return {'void'}
        
        try:
            if isinstance(type_node, ReferenceType):
                base_type = type_node.name #type: ignore
                if type_node.sub_type: #type: ignore
                    sub_type:set = JavaType.resolve_reference_type(type_node.sub_type)#type: ignore
                    return sub_type
                if type_node.arguments:  # 处理泛型 #type: ignore
                    # args = [JavaType.resolve_type(arg.type) for arg in type_node.arguments] #type: ignore
                    args = set()
                    for arg in type_node.arguments: #type: ignore
                        _ = JavaType.resolve_reference_type(arg.type)
                        for t in _:
                            args.add(t)
                    result = set(filter(lambda x: x != None, args))
                    result.add(base_type)
                    return result
                return {base_type}
            elif isinstance(type_node, BasicType):
                return {type_node.name} #type: ignore
            elif hasattr(type_node, 'name'):
                return {type_node.name}
        except AttributeError as e:
            print(f"Type resolve error: {str(e)}")
        return {str(type_node)}
