from .tokens import TokenType
from .ast_nodes import *
from dcv.errors.syntax_error import DCVSyntaxError


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # =========================
    # Utility
    # =========================

    def current(self):
        return self.tokens[self.pos]

    def eat(self, expected_type=None):
        token = self.current()

        if expected_type and token.type != expected_type:
            raise DCVSyntaxError(
                f"Unexpected token {token.type}",
                token.line
            )

        self.pos += 1
        return token

    # =========================
    # Program
    # =========================

    def parse(self):
        statements = []

        while self.current().type != TokenType.EOF:
            statements.append(self.statement())

        return Program(statements)

    # =========================
    # Statements
    # =========================

    def statement(self):
        token = self.current()

        if token.value == "LOAD":
            return self.load()

        if token.value == "SAVE":
            return self.save()

        if token.value == "TRIM":
            return self.trim()

        if token.value == "REMOVE_NULLS":
            return self.remove_nulls()

        if token.value == "CAST":
            return self.cast()

        if token.value == "ADD_COLUMN":
            return self.add_column()

        if token.value == "VALIDATE":
            return self.validate()
        
        if token.value == "FILTER":
            return self.filter()

        if token.value == "SELECT":
            return self.select()

        if token.value == "REMOVE_COLUMNS":
            return self.remove_columns()

        if token.value == "RENAME":
            return self.rename()

        if token.value == "MODE":
            return self.mode()
        
        if token.value == "GROUP_BY":
            return self.group_by()
        
        if token.value== "AGGREGATE":
            return self.aggregate_block()

        raise DCVSyntaxError(f"Invalid statement starting with '{token.value}' (type={token.type})",token.line)

    def load(self):
        token = self.eat()
        path = self.eat(TokenType.STRING)
        delimiter = None
        skiprows = None
        while self.current().type == TokenType.KEYWORD:
            if self.current().value == "DELIMITER":
                self.eat()
                delim=self.eat(TokenType.STRING)
                delimiter = delim.value
            elif self.current().value=="SKIPROWS":
                self.eat()
                num=self.eat(TokenType.NUMBER)
                skiprows = num.value
            else:
                break

        return Load(path.value,delimiter,skiprows,token.line)

    def save(self):
        token = self.eat()
        path = self.eat(TokenType.STRING)
        return Save(path.value, token.line)

    def trim(self):
        token = self.eat()
        col = self.eat(TokenType.STRING)
        return Trim(col.value, token.line)

    def remove_nulls(self):
        token = self.eat()
        col = self.eat(TokenType.STRING)
        return RemoveNulls(col.value, token.line)

    def cast(self):
        token = self.eat()
        col = self.eat(TokenType.STRING)

        to_token = self.eat()
        if to_token.value != "TO":
            raise DCVSyntaxError("Expected TO in CAST", to_token.line)

        target = self.eat(TokenType.IDENTIFIER)
        return Cast(col.value, target.value, token.line)

    def add_column(self):
        token = self.eat()
        col = self.eat(TokenType.STRING)

        eq_token = self.eat()
        if eq_token.value != "=":
            raise DCVSyntaxError("Expected '=' in ADD_COLUMN", eq_token.line)

        expr = self.expression()
        return AddColumn(col.value, expr, token.line)

    def validate(self):
        token = self.eat()
        expr = self.expression()
        return Validate(expr, token.line)

    def mode(self):
        token = self.eat()
        value = self.eat(TokenType.STRING)
        return Mode(value.value.lower(), token.line)
    
    def filter(self):
        token=self.eat()
        expr=self.expression()
        return Filter(expr,token.line)
    
    def select(self):
        token = self.eat()
        columns = []

        col = self.eat(TokenType.IDENTIFIER)
        columns.append(col.value)

        while self.current().type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            col = self.eat(TokenType.IDENTIFIER)
            columns.append(col.value)

        return Select(columns, token.line)
    
    def remove_columns(self):
        token = self.eat()
        columns = []

        col = self.eat(TokenType.IDENTIFIER)
        columns.append(col.value)

        while self.current().type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            col = self.eat(TokenType.IDENTIFIER)
            columns.append(col.value)

        return RemoveColumns(columns, token.line)
    

    def rename(self):
        token = self.eat()

        mappings = {}

        old = self.eat(TokenType.IDENTIFIER)

        as_token = self.eat()
        if as_token.value != "AS":
            raise DCVSyntaxError("Expected AS", as_token.line)

        new = self.eat(TokenType.IDENTIFIER)

        mappings[old.value] = new.value

        return Rename(mappings, token.line)
    

    # =========================
    # Expression Parsing
    # =========================

    def expression(self):
        return self.parse_or()

    def parse_or(self):
        node = self.parse_and()

        while (
            self.current().type == TokenType.KEYWORD
            and self.current().value == "OR"
        ):
            op = self.eat()
            right = self.parse_and()
            node = BinaryOp(node, "OR", right, op.line)

        return node

    def parse_and(self):
        node = self.parse_comparison()

        while (
            self.current().type == TokenType.KEYWORD
            and self.current().value == "AND"
        ):
            op = self.eat()
            right = self.parse_comparison()
            node = BinaryOp(node, "AND", right, op.line)

        return node

    def parse_comparison(self):
        node = self.parse_term_expr()

        if self.current().type == TokenType.OPERATOR:
            op = self.eat()
            right = self.parse_term_expr()
            return BinaryOp(node, op.value, right, op.line)

        return node

    def parse_term_expr(self):
        node = self.parse_factor()

        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.eat()
            right = self.parse_factor()
            node = BinaryOp(node, op.value, right, op.line)

        return node

    def parse_factor(self):
        node = self.parse_unary()

        while self.current().type in (TokenType.MUL, TokenType.DIV):
            op = self.eat()
            right = self.parse_unary()
            node = BinaryOp(node, op.value, right, op.line)

        return node

    def parse_unary(self):
        token = self.current()

        if (
            token.type == TokenType.KEYWORD
            and token.value == "NOT"
        ):
            op = self.eat()
            operand = self.parse_unary()
            return UnaryOp("NOT", operand, op.line)

        if token.type == TokenType.MINUS:
            op = self.eat()
            operand = self.parse_unary()
            return UnaryOp("-", operand, op.line)

        return self.parse_primary()

    def parse_primary(self):
        token = self.current()

        # Numbers
        if token.type == TokenType.NUMBER:
            tok = self.eat()
            return Literal(tok.value, tok.line)

        # Strings
        if token.type == TokenType.STRING:
            tok = self.eat()
            return Literal(tok.value, tok.line)

        # Identifier or Function Call
        if token.type == TokenType.IDENTIFIER:
            tok = self.eat()

            # Function call detected
            if self.current().type == TokenType.LPAREN:
                self.eat()  # consume '('

                args = []

                if self.current().type != TokenType.RPAREN:
                    args.append(self.expression())

                    # 🔴 THIS IS WHERE IT GOES
                    while self.current().type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        args.append(self.expression())

                self.eat(TokenType.RPAREN)

                return FunctionCall(tok.value.upper(), args, tok.line)

            return Identifier(tok.value, tok.line)

        # Parentheses
        if token.type == TokenType.LPAREN:
            self.eat()
            expr = self.expression()
            self.eat(TokenType.RPAREN)
            return expr

        # IF expression
        if token.type == TokenType.KEYWORD and token.value == "IF":
            return self.parse_if()

        raise DCVSyntaxError("Invalid expression", token.line)

    def parse_if(self):
        token = self.eat()  # IF

        condition = self.expression()

        then_token = self.eat()
        if then_token.value != "THEN":
            raise DCVSyntaxError("Expected THEN", then_token.line)

        true_expr = self.expression()

        else_token = self.eat()
        if else_token.value != "ELSE":
            raise DCVSyntaxError("Expected ELSE", else_token.line)

        false_expr = self.expression()

        return IfExpression(condition, true_expr, false_expr, token.line)
    
    def group_by(self):
        token = self.eat()  # GROUP_BY

        columns = []

        col = self.eat(TokenType.IDENTIFIER)
        columns.append(col.value)

        while self.current().type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            col = self.eat(TokenType.IDENTIFIER)
            columns.append(col.value)

        return GroupBy(columns, token.line)
    
    def aggregate_block(self):
        token = self.eat()  # AGGREGATE

        self.eat(TokenType.COLON)

        aggregations = []

        while self.current().type == TokenType.IDENTIFIER:
            func = self.eat(TokenType.IDENTIFIER)
            column = self.eat(TokenType.IDENTIFIER)

            as_token = self.eat()
            if as_token.value != "AS":
                raise DCVSyntaxError("Expected AS", as_token.line)

            alias = self.eat(TokenType.IDENTIFIER)

            aggregations.append(
                AggregateItem(func.value.upper(), column.value, alias.value, func.line)
            )

        return AggregateBlock(aggregations, token.line)


