from dataclasses import dataclass
from typing import List


# =========================
# Base Node
# =========================

class ASTNode:
    pass


# =========================
# Program
# =========================

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]


# =========================
# Statements
# =========================

@dataclass
class Load(ASTNode):
    path: str
    delimiter: str | None
    skiprows: int | None
    line: int


@dataclass
class Save(ASTNode):
    path: str
    line: int


@dataclass
class Trim(ASTNode):
    column: str
    line: int


@dataclass
class RemoveNulls(ASTNode):
    column: str
    line: int


@dataclass
class Cast(ASTNode):
    column: str
    target_type: str
    line: int


@dataclass
class AddColumn(ASTNode):
    column: str
    expression: ASTNode
    line: int


@dataclass
class Validate(ASTNode):
    expression: ASTNode
    line: int


@dataclass
class Mode(ASTNode):
    value: str
    line: int


# =========================
# Expressions
# =========================

@dataclass
class Identifier(ASTNode):
    name: str
    line: int


@dataclass
class Literal(ASTNode):
    value: any
    line: int


@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode
    line: int


@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    line: int


@dataclass
class IfExpression(ASTNode):
    condition: ASTNode
    true_expr: ASTNode
    false_expr: ASTNode
    line: int

@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: list
    line: int

# =========================
# Aggregation
# =========================

@dataclass
class GroupBy(ASTNode):
    columns: List[str]
    line: int


@dataclass
class AggregateBlock(ASTNode):
    aggregations: List[ASTNode]
    line: int


@dataclass
class AggregateItem(ASTNode):
    function: str
    column: str
    alias: str
    line: int
# =========================
# Data Shaping
# =========================

@dataclass
class Filter(ASTNode):
    expression: ASTNode
    line: int


@dataclass
class Select(ASTNode):
    columns: List[str]
    line: int


@dataclass
class RemoveColumns(ASTNode):
    columns: List[str]
    line: int


@dataclass
class Rename(ASTNode):
    mappings: dict
    line: int
