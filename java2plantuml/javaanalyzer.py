import os

import javalang

from .javapackage import JavaPackage, JavaClassContext

class JavaAnalyzer:
    def __init__(self):
        self.__packages : dict[str, JavaPackage] = {}

    @property
    def packages(self):
        return self.__packages

    def __javalang_analyze_file(self, filepath : str):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = javalang.parse.parse(source)
            return tree
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            return
        except javalang.parser.JavaSyntaxError as e:
            print(f"Syntax error: {str(e)}")
            return

    def analyze_file(self, filepath : str):
        tree = self.__javalang_analyze_file(filepath)
        if tree is None:
            return
        # safe get property package
        package_name = getattr(tree, "package", None)
        if package_name is not None:
            package_name = package_name.name
        else:
            package_name = "main"

        package = self.__packages.get(package_name, None)

        if package is None:
            package = JavaPackage(package_name)
            self.__packages[package_name] = package
        
        java_context = JavaClassContext(getattr(tree, 'imports', []), package)
        package.parse(tree.types, java_context) # type: ignore

    def print_packages(self):
        for package in self.__packages.values():
            print(str(package))
    
    @property
    def pakcages_plantuml(self):
        plantuml = ""
        for package in self.__packages.values():
            plantuml += str(package)
        return plantuml

    @property
    def relations_plantuml(self):
        plantuml = ""
        for package in self.__packages.values():
            relations = package.relations_list
            for relation in relations:
                plantuml += str(relation) + "\n"
        return plantuml

    def analyze_relations(self):
        for package in self.__packages.values():
            package.parse_relations()

    def print_relations(self):
        for package in self.__packages.values():
            relations = package.relations_list
            for relation in relations:
                print(relation)

class JavaProjectAnalyZer:
    def __init__(self):
        self.__analyzer = JavaAnalyzer()

    def get_analyzer(self):
        return self.__analyzer
    
    def analyze_directory(self, directory_path : str):
        if os.path.isdir(directory_path):
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if file.endswith(".java"):
                        self.__analyzer.analyze_file(os.path.join(root, file))
        else:
            print("Not a valid directory")
    
    def analyze_relations(self):
        self.__analyzer.analyze_relations()

    @property
    def pakcages_plantuml(self):
        return self.__analyzer.pakcages_plantuml

    @property
    def relations_plantuml(self):
        return self.__analyzer.relations_plantuml
