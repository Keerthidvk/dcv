from .ast_nodes import *
from .type_system import (
    StringType,
    IntType,
    FloatType,
    BoolType,
    UnknownType,
)
from .symbol_table import SymbolTable
from .function_registry import FunctionRegistry
from dcv.errors.semantic_error import DCVSemanticError


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.function_registry = FunctionRegistry()

    def analyze(self, program):
        for statement in program.statements:
            self.visit(statement)

    # ---------------------------
    # Statement Visitors
    # ---------------------------

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)

        if not method:
            raise DCVSemanticError(f"No semantic rule for {type(node).__name__}")

        return method(node)

    def visit_LoadStatement(self, node):
        pass  # Columns defined at runtime after load

    def visit_SaveStatement(self, node):
        pass

    def visit_TrimStatement(self, node):
        if not self.symbol_table.has_column(node.column):
            raise DCVSemanticError(
                f"Column '{node.column}' not defined"
            )

    def visit_RemoveNullsStatement(self, node):
        if not self.symbol_table.has_column(node.column):
            raise DCVSemanticError(
                f"Column '{node.column}' not defined"
            )

    def visit_CastStatement(self, node):
        if not self.symbol_table.has_column(node.column):
            raise DCVSemanticError(
                f"Column '{node.column}' not defined"
            )

        if node.target_type not in ("int", "float", "string", "bool"):
            raise DCVSemanticError(
                f"Unsupported target type '{node.target_type}'"
            )

    def visit_AddColumnStatement(self, node):
        expr_type = self.visit(node.expression)
        self.symbol_table.define_column(node.column_name, expr_type)

    def visit_ValidateStatement(self, node):
        if not self.symbol_table.has_column(node.column):
            raise DCVSemanticError(
                f"Column '{node.column}' not defined"
            )

        self.visit(node.value)

    # ---------------------------
    # Expression Visitors
    # ---------------------------

    def visit_Literal(self, node):
        if isinstance(node.value, str):
            return StringType()
        if isinstance(node.value, int):
            return IntType()
        if isinstance(node.value, float):
            return FloatType()
        if isinstance(node.value, bool):
            return BoolType()
        return UnknownType()

    def visit_ColumnReference(self, node):
        if not self.symbol_table.has_column(node.name):
            raise DCVSemanticError(
                f"Column '{node.name}' not defined"
            )
        return self.symbol_table.get_column(node.name)

    def visit_BinaryExpression(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if type(left_type) != type(right_type):
            raise DCVSemanticError(
                "Type mismatch in binary expression"
            )

        return BoolType()

    def visit_IfExpression(self, node):
        condition_type = self.visit(node.condition)

        if not isinstance(condition_type, BoolType):
            raise DCVSemanticError(
                "IF condition must evaluate to boolean"
            )

        true_type = self.visit(node.true_expr)
        false_type = self.visit(node.false_expr)

        if type(true_type) != type(false_type):
            raise DCVSemanticError(
                "IF branches must return same type"
            )

        return true_type
