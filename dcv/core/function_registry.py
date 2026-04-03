import pandas as pd
import numpy as np


class FunctionRegistry:

    def __init__(self):
        self.functions = {}
        self._register_builtins()

    def _register(self, name, implementation):
        self.functions[name.lower()] = implementation

    def _register_builtins(self):

        self._register(
            "trim",
            lambda x: x.astype(str).str.strip()
        )

        self._register(
            "upper",
            lambda x: x.astype(str).str.upper()
        )

        self._register(
            "lower",
            lambda x: x.astype(str).str.lower()
        )

        self._register(
            "length",
            lambda x: x.astype(str).str.len()
        )

        self._register(
            "to_int",
            lambda x: pd.to_numeric(x, errors="coerce").astype("Int64")
        )

        self._register(
            "to_float",
            lambda x: pd.to_numeric(x, errors="coerce")
        )

        self._register(
            "isnull",
            lambda x: pd.isnull(x)
        )

        self._register(
            "notnull",
            lambda x: pd.notnull(x)
        )

        self._register(
            "round",
            lambda x, n: np.round(x, int(n))
        )

    def get(self, name):
        return self.functions.get(name.lower())
