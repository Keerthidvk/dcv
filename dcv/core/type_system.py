class DCVType:
    name = "unknown"

    def __str__(self):
        return self.name

    def is_compatible(self, other):
        return isinstance(other, self.__class__)


class StringType(DCVType):
    name = "string"


class IntType(DCVType):
    name = "int"


class FloatType(DCVType):
    name = "float"


class BoolType(DCVType):
    name = "bool"


class UnknownType(DCVType):
    name = "unknown"


def infer_type_from_value(value):
    if isinstance(value, bool):
        return BoolType()
    if isinstance(value, int):
        return IntType()
    if isinstance(value, float):
        return FloatType()
    if isinstance(value, str):
        return StringType()
    return UnknownType()
