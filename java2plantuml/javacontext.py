from javalang.tree import Import

class JavaClassContext:
    attrs = ['class_package_dict', 'cur_package']

    def __init__(self, declarations: list[Import], cur_package):
        self.class_package_dict: dict[str, str] = {}
        self.cur_package = cur_package
        for declaration in declarations:
            path = getattr(declaration, 'path', None)
            if path is None:
                continue
            if path.startswith('java.'):
                continue
            if path.startswith('javax.'):
                continue
            if path.startswith('org.w3c.'):
                continue
            if path.startswith('org.xml.'):
                continue
            if path.startswith('org.w3.'):
                continue
            if path.startswith('org.omg.'):
                continue
            # 将最后的类拆除作为键，将去掉最后类名的包路径作为值存储在字典中。
            _ = path.split('.')
            __ = _[-1]
            self.class_package_dict[__] = '.'.join(_[:-1])


    def get_full_class_path(self, class_name: str):
        _ = class_name.split('.')
        package_path = self.class_package_dict.get(_[0], None)
        if package_path is not None:
            return f"{package_path}.{class_name}"
        if self.cur_package is None:
            return None
        if _[0] in self.cur_package.classes:
            return f"{self.cur_package.name}.{class_name}"
        return None
