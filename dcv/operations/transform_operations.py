from .base_operation import BaseOperation


class CastOperation(BaseOperation):
    def __init__(self, column, target_type):
        self.column = column
        self.target_type = target_type

    def execute(self, context):
        if self.target_type == "int":
            context.dataframe[self.column] = context.dataframe[self.column].astype(int)
        elif self.target_type == "float":
            context.dataframe[self.column] = context.dataframe[self.column].astype(float)
        elif self.target_type == "string":
            context.dataframe[self.column] = context.dataframe[self.column].astype(str)
        elif self.target_type == "bool":
            context.dataframe[self.column] = context.dataframe[self.column].astype(bool)
