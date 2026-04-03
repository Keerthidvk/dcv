from .base_operation import BaseOperation


class TrimOperation(BaseOperation):
    def __init__(self, column):
        self.column = column

    def execute(self, context):
        context.dataframe[self.column] = (
            context.dataframe[self.column].astype(str).str.strip()
        )


class RemoveNullsOperation(BaseOperation):
    def __init__(self, column):
        self.column = column

    def execute(self, context):
        context.dataframe = context.dataframe.dropna(subset=[self.column])
