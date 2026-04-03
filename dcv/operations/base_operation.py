class BaseOperation:
    def execute(self, context):
        raise NotImplementedError("Operation must implement execute()")
