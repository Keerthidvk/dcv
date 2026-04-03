from .tokens import TokenType, KEYWORDS
from dcv.errors.syntax_error import DCVSyntaxError


class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1

    def tokenize(self):
        tokens = []

        while self.pos < len(self.text):
            ch = self.text[self.pos]

            if ch=="#":
                while self.pos<len(self.text) and self.text[self.pos]!="\n":
                    self.pos+=1
                continue

            if ch in " \t":
                self.pos += 1
                continue

            if ch == "\n":
                self.line += 1
                self.pos += 1
                continue

            if ch == '"':
                tokens.append(self._string())
                continue

            if ch.isdigit():
                tokens.append(self._number())
                continue

            if ch.isalpha() or ch == "_":
                tokens.append(self._identifier())
                continue

            # Arithmetic
            if ch == "+":
                tokens.append(Token(TokenType.PLUS, "+", self.line))
                self.pos += 1
                continue

            if ch == "-":
                tokens.append(Token(TokenType.MINUS, "-", self.line))
                self.pos += 1
                continue

            if ch == "*":
                tokens.append(Token(TokenType.MUL, "*", self.line))
                self.pos += 1
                continue

            if ch == "/":
                tokens.append(Token(TokenType.DIV, "/", self.line))
                self.pos += 1
                continue

            if ch == "(":
                tokens.append(Token(TokenType.LPAREN, "(", self.line))
                self.pos += 1
                continue

            if ch == ")":
                tokens.append(Token(TokenType.RPAREN, ")", self.line))
                self.pos += 1
                continue

            # Comparison operators
            if ch in "=><!":
                tokens.append(self._operator())
                continue

            if ch == ",":
                tokens.append(Token(TokenType.COMMA, ",", self.line))
                self.pos += 1
                continue

            if ch == ":":
                tokens.append(Token(TokenType.COLON, ":", self.line))
                self.pos += 1
                continue



            raise DCVSyntaxError(f"Unexpected character '{ch}'", self.line)

        tokens.append(Token(TokenType.EOF, None, self.line))
        return tokens

    def _string(self):
        self.pos += 1
        start = self.pos

        while self.pos < len(self.text) and self.text[self.pos] != '"':
            self.pos += 1

        if self.pos >= len(self.text):
            raise DCVSyntaxError("Unterminated string", self.line)

        value = self.text[start:self.pos]
        self.pos += 1
        return Token(TokenType.STRING, value, self.line)

    def _number(self):
        start = self.pos

        while self.pos < len(self.text) and (
            self.text[self.pos].isdigit() or self.text[self.pos] == "."
        ):
            self.pos += 1

        value = self.text[start:self.pos]

        if "." in value:
            return Token(TokenType.NUMBER, float(value), self.line)
        return Token(TokenType.NUMBER, int(value), self.line)

    def _identifier(self):
        start = self.pos

        while self.pos < len(self.text) and (
            self.text[self.pos].isalnum() or self.text[self.pos] == "_"
        ):
            self.pos += 1

        value = self.text[start:self.pos]

        if value.upper() in KEYWORDS:
            return Token(TokenType.KEYWORD, value.upper(), self.line)

        return Token(TokenType.IDENTIFIER, value, self.line)

    def _operator(self):
        start = self.pos

        while self.pos < len(self.text) and self.text[self.pos] in "=><!":
            self.pos += 1

        return Token(TokenType.OPERATOR, self.text[start:self.pos], self.line)
