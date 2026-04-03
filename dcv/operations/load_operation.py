from .base_operation import BaseOperation
from dcv.io.reader import read_file


class LoadOperation(BaseOperation):
    def __init__(self, filepath):
        self.filepath = filepath

    def execute(self, context):
        context.dataframe = read_file(self.filepath)
