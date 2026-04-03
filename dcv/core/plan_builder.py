from .execution_plan import ExecutionPlan
from .ast_nodes import *


class PlanBuilder:
    def build(self, program):
        plan = ExecutionPlan()

        for stmt in program.statements:
            plan.add(stmt)

        return plan
