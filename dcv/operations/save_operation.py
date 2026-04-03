from .base_operation import BaseOperation
from dcv.io.writer import write_file


class SaveOperation(BaseOperation):
    def __init__(self, filepath):
        self.filepath = filepath

    def execute(self, context):
        write_file(context.dataframe, self.filepath)
