from enum import Enum, auto


class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()

    LPAREN = auto()
    RPAREN = auto()

    OPERATOR = auto()      # == != > < >= <=
    EOF = auto()
    COMMA = auto()
    COLON = auto()




KEYWORDS = {
    "LOAD",
    "SAVE",
    "TRIM",
    "REMOVE_NULLS",
    "CAST",
    "TO",
    "ADD_COLUMN",
    "VALIDATE",
    "MODE",

    # Expression keywords
    "IF",
    "THEN",
    "ELSE",
    "AND",
    "OR",
    "NOT",

    # Aggregation control
    "GROUP_BY",
    "AGGREGATE",
    "AS",

    #New Commands
    "FILTER",
    "SELECT",
    "REMOVE_COLUMNS",
    "RENAME"

    #Delimiter
    "DELIMITER"
    "SKIPROWS"
}
