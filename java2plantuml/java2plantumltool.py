class Java2PlantUMLTool:

    _VISIT_MODIFIERS_SYMBOL = {
        'private': '-',
        'public': '+',
        'protected': '#',
        'default': '-'
    }

    _OTHER_MODIFIERS_SYMBOL = {
        'static': r'{static}',
        'abstract': r'{abstract}'
    }

    def __init__(self):
        raise SystemError("it's a static class!!!")

    @staticmethod
    def print_modifiers(modifiers: set[str] | str, only_visit: bool = False):
        """打印修饰符方法"""
        if isinstance(modifiers, str):
            if only_visit:
                return Java2PlantUMLTool._VISIT_MODIFIERS_SYMBOL.get(modifiers, '')
            else:
                return Java2PlantUMLTool._VISIT_MODIFIERS_SYMBOL.get(modifiers) or Java2PlantUMLTool._OTHER_MODIFIERS_SYMBOL.get(modifiers, modifiers + ' ')
        else:
            if only_visit:
                return ''.join(Java2PlantUMLTool._VISIT_MODIFIERS_SYMBOL.get(modifier, '') for modifier in modifiers)

            visit = ''
            other = ''
            rest = ''
            for modifier in modifiers:
                symbol = Java2PlantUMLTool._VISIT_MODIFIERS_SYMBOL.get(modifier)
                if symbol is not None:
                    visit += symbol
                    continue
                symbol = Java2PlantUMLTool._OTHER_MODIFIERS_SYMBOL.get(modifier)
                if symbol is not None:
                    other += symbol
                    continue
                rest += modifier + ' '
            return visit + other + rest
        

from enum import StrEnum

class UMLRelationship(StrEnum):
    """UML关系枚举类"""
    INNER = "-+"
    DEPEND = ".>"
    ASSOCIATE = "->"
    IMPLEMENT = ".|>"
    EXTEND = "-|>"
