import pandas as pd
import numpy as np
import os

from .ast_nodes import *
from .function_registry import FunctionRegistry
from dcv.errors.runtime_error import DCVRuntimeError


class Executor:

    def __init__(self, program):
        self.program = program
        self.df = None
        self.mode = "strict"
        self.group_columns = None

        self.function_registry = FunctionRegistry()

        self.report = {
            "cast_errors": 0,
            "validation_filtered": 0,
        }

    # =========================
    # Execution Entry
    # =========================

    def execute(self):

        for stmt in self.program.statements:
            self.run(stmt)

        if self.mode == "tolerant":
            print("\nExecution Report:")
            print(f"Rows removed due to cast errors: {self.report['cast_errors']}")
            print(f"Rows removed by validation: {self.report['validation_filtered']}")
            print(f"Final row count: {len(self.df)}")

    # =========================
    # Statement Dispatcher
    # =========================

    def run(self, stmt):

        if isinstance(stmt, Mode):
            self.handle_mode(stmt)

        elif isinstance(stmt, Load):
            self.handle_load(stmt)

        elif isinstance(stmt, Save):
            if self.df is None:
                raise DCVRuntimeError("No dataset loaded", stmt.line)

            self.df.to_csv(stmt.path, index=False)

        elif isinstance(stmt, Trim):
            self.ensure_column(stmt.column, stmt.line)
            self.df[stmt.column] = self.df[stmt.column].astype(str).str.strip()

        elif isinstance(stmt, RemoveNulls):
            self.ensure_column(stmt.column, stmt.line)
            self.df = self.df.dropna(subset=[stmt.column])

        elif isinstance(stmt, Cast):
            self.handle_cast(stmt)

        elif isinstance(stmt, AddColumn):
            self.df[stmt.column] = self.evaluate(stmt.expression)

        elif isinstance(stmt, Validate):
            self.handle_validate(stmt)

        elif isinstance(stmt, GroupBy):
            self.group_columns = stmt.columns

        elif isinstance(stmt, AggregateBlock):
            self.handle_aggregate_block(stmt)

        elif isinstance(stmt, Filter):
            condition = self.evaluate(stmt.expression)
            self.df = self.df[condition]

        elif isinstance(stmt, Select):

            for col in stmt.columns:
                self.ensure_column(col, stmt.line)

            self.df = self.df[stmt.columns]

        elif isinstance(stmt, RemoveColumns):

            for col in stmt.columns:
                self.ensure_column(col, stmt.line)

            self.df = self.df.drop(columns=stmt.columns)

        elif isinstance(stmt, Rename):

            for old in stmt.mappings:
                self.ensure_column(old, stmt.line)

            self.df = self.df.rename(columns=stmt.mappings)

        else:
            raise DCVRuntimeError("Unknown statement", stmt.line)

    # =========================
    # LOAD
    # =========================

    def handle_load(self, stmt):

        try:
            if not os.path.exists(stmt.path):
                raise DCVRuntimeError(
                    f"File not found → '{stmt.path}'",
                    stmt.line
                )

            read_args = {}

            if stmt.delimiter:
                read_args["sep"] = stmt.delimiter

            if stmt.skiprows:
                read_args["skiprows"] = stmt.skiprows

            if stmt.path.endswith(".csv") or stmt.path.endswith(".txt"):
                self.df = pd.read_csv(stmt.path, **read_args)

            elif stmt.path.endswith(".xlsx"):
                self.df = pd.read_excel(stmt.path)

            else:
                raise DCVRuntimeError(
                    f"Unsupported file format → '{stmt.path}'",
                    stmt.line
                )

        except DCVRuntimeError:
            raise

        except Exception as e:
            raise DCVRuntimeError(
                f"Failed to load file → {str(e)}",
                stmt.line
            )

    # =========================
    # Mode
    # =========================

    def handle_mode(self, stmt):

        if stmt.value not in ("strict", "tolerant"):
            raise DCVRuntimeError("Invalid mode", stmt.line)

        self.mode = stmt.value

    # =========================
    # CAST
    # =========================

    def handle_cast(self, stmt):

        self.ensure_column(stmt.column, stmt.line)

        if self.mode == "strict":
            self.df[stmt.column] = self.df[stmt.column].astype(stmt.target_type)
            return

        before = len(self.df)

        if stmt.target_type == "int":
            self.df[stmt.column] = pd.to_numeric(
                self.df[stmt.column],
                errors="coerce"
            ).astype("Int64")

        elif stmt.target_type == "float":
            self.df[stmt.column] = pd.to_numeric(
                self.df[stmt.column],
                errors="coerce"
            )

        else:
            self.df[stmt.column] = self.df[stmt.column].astype(stmt.target_type)

        self.df = self.df.dropna(subset=[stmt.column])

        after = len(self.df)
        self.report["cast_errors"] += (before - after)

    # =========================
    # VALIDATE
    # =========================

    def handle_validate(self, stmt):

        result = self.evaluate(stmt.expression)

        if self.mode == "strict":
            if not result.all():
                raise DCVRuntimeError("Validation failed", stmt.line)

        else:
            before = len(self.df)
            self.df = self.df[result]
            after = len(self.df)

            self.report["validation_filtered"] += (before - after)

    # =========================
    # Expression Evaluator
    # =========================

    def evaluate(self, expr):

        if isinstance(expr, Literal):
            return expr.value

        if isinstance(expr, Identifier):
            self.ensure_column(expr.name, expr.line)
            return self.df[expr.name]

        if isinstance(expr, UnaryOp):

            value = self.evaluate(expr.operand)

            if expr.operator == "NOT":
                return ~value

            if expr.operator == "-":
                return -value

            raise DCVRuntimeError("Invalid unary operator", expr.line)

        if isinstance(expr, BinaryOp):

            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)

            if expr.operator == "AND":
                return left & right

            if expr.operator == "OR":
                return left | right

            if expr.operator == "+":
                return left + right

            if expr.operator == "-":
                return left - right

            if expr.operator == "*":
                return left * right

            if expr.operator == "/":
                return left / right

            if expr.operator == ">":
                return left > right

            if expr.operator == "<":
                return left < right

            if expr.operator == ">=":
                return left >= right

            if expr.operator == "<=":
                return left <= right

            if expr.operator == "==":
                return left == right

            if expr.operator == "!=":
                return left != right

            raise DCVRuntimeError("Invalid binary operator", expr.line)

        if isinstance(expr, IfExpression):

            condition = self.evaluate(expr.condition)
            true_val = self.evaluate(expr.true_expr)
            false_val = self.evaluate(expr.false_expr)

            return np.where(condition, true_val, false_val)

        if isinstance(expr, FunctionCall):

            func = self.function_registry.get(expr.name)

            if func is None:
                raise DCVRuntimeError(
                    f"Unknown function '{expr.name}'",
                    expr.line
                )

            evaluated_args = [self.evaluate(arg) for arg in expr.arguments]

            return func(*evaluated_args)

        raise DCVRuntimeError("Invalid expression", getattr(expr, "line", None))

    # =========================
    # AGGREGATION
    # =========================

    def handle_aggregate_block(self, stmt):

        if self.group_columns is None:
            raise DCVRuntimeError(
                "GROUP_BY must be defined before AGGREGATE",
                stmt.line
            )

        agg_dict = {}

        for item in stmt.aggregations:

            self.ensure_column(item.column, item.line)

            if item.function == "SUM":
                agg_func = "sum"

            elif item.function == "AVG":
                agg_func = "mean"

            elif item.function == "COUNT":
                agg_func = "count"

            elif item.function == "MIN":
                agg_func = "min"

            elif item.function == "MAX":
                agg_func = "max"

            else:
                raise DCVRuntimeError(
                    f"Unsupported aggregation function {item.function}",
                    item.line
                )

            agg_dict[item.alias] = (item.column, agg_func)

        grouped = self.df.groupby(self.group_columns).agg(**agg_dict).reset_index()

        self.df = grouped

        self.group_columns = None

    # =========================
    # Column Validation
    # =========================

    def ensure_column(self, column, line):

        if column not in self.df.columns:
            raise DCVRuntimeError(
                f"Column '{column}' not found in dataset",
                line
            )