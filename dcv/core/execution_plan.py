class ExecutionPlan:
    def __init__(self):
        self.steps = []

    def add(self, node):
        self.steps.append(node)

    def __iter__(self):
        return iter(self.steps)
