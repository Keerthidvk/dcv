from .base_operation import BaseOperation


class ValidateOperation(BaseOperation):
    def __init__(self, column, operator, value):
        self.column = column
        self.operator = operator
        self.value = value

    def execute(self, context):
        df = context.dataframe

        if self.operator == "==":
            invalid = df[df[self.column] != self.value]
        elif self.operator == "!=":
            invalid = df[df[self.column] == self.value]
        elif self.operator == ">":
            invalid = df[df[self.column] <= self.value]
        elif self.operator == "<":
            invalid = df[df[self.column] >= self.value]
        else:
            invalid = None

        context.metadata["validation_errors"] = invalid
