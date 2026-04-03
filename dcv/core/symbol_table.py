from .type_system import UnknownType


class SymbolTable:
    def __init__(self):
        self.columns = {}
        self.functions = {}

    def define_column(self, name, column_type):
        self.columns[name] = column_type

    def get_column(self, name):
        return self.columns.get(name, UnknownType())

    def has_column(self, name):
        return name in self.columns

    def define_function(self, name, function_def):
        self.functions[name.lower()] = function_def

    def get_function(self, name):
        return self.functions.get(name.lower())
