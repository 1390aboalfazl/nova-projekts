from .lexer import tokenize
from .ast_nodes import Program, Let, Show, Literal, Name, Unary, Binary
from .errors import NovaSyntaxError

def parse(source: str) -> Program:
    return Parser(source).parse()

class Parser:
    def __init__(self, source):
        self.tokens = tokenize(source)
        self.i = 0

    @property
    def current(self):
        return self.tokens[self.i]

    def advance(self):
        t = self.current
        if t.kind != "EOF": self.i += 1
        return t

    def expect(self, kind, message=None):
        if self.current.kind != kind:
            t = self.current
            raise NovaSyntaxError(f"Line {t.line}, column {t.column}: {message or 'expected ' + kind}")
        return self.advance()

    def skip_newlines(self):
        while self.current.kind == "NEWLINE": self.advance()

    def parse(self):
        self.skip_newlines()
        self.expect("FORGE", "program must start with 'forge'")
        self.expect("PROGRAM", "expected 'program' after 'forge'")
        name = self.expect("STRING", "expected quoted program name").value
        self.expect("NEWLINE", "expected newline after header")
        self.skip_newlines()
        self.expect("BEGIN", "expected 'begin'")
        self.expect("NEWLINE", "expected newline after begin")
        self.skip_newlines()
        statements = []
        while self.current.kind not in ("END", "EOF"):
            statements.append(self.statement())
            if self.current.kind == "NEWLINE":
                self.skip_newlines()
            elif self.current.kind != "END":
                t = self.current
                raise NovaSyntaxError(f"Line {t.line}, column {t.column}: expected end of statement")
        self.expect("END", "expected 'end' to close program")
        self.skip_newlines()
        self.expect("EOF", "unexpected content after program")
        return Program(name, statements)

    def statement(self):
        if self.current.kind == "LET":
            start = self.advance()
            name = self.expect("IDENT", "expected variable name").value
            self.expect("COLON", "expected ':' after variable name")
            typ = self.expect("TYPE", "expected type Int, Float, Bool, or Text").value
            self.expect("EQUAL", "expected '=' before initializer")
            return Let(name, typ, self.expression(), start.line)
        if self.current.kind == "SHOW":
            start = self.advance()
            return Show(self.expression(), start.line)
        t = self.current
        raise NovaSyntaxError(f"Line {t.line}, column {t.column}: expected let or show")

    def expression(self):
        node = self.term()
        while self.current.kind in ("PLUS", "MINUS"):
            op = self.advance()
            node = Binary(node, op.value, self.term(), op.line)
        return node

    def term(self):
        node = self.unary()
        while self.current.kind in ("STAR", "SLASH"):
            op = self.advance()
            node = Binary(node, op.value, self.unary(), op.line)
        return node

    def unary(self):
        if self.current.kind == "MINUS":
            t = self.advance()
            return Unary("-", self.unary(), t.line)
        return self.primary()

    def primary(self):
        t = self.current
        if t.kind == "INT":
            self.advance(); return Literal(int(t.value), "Int", t.line)
        if t.kind == "FLOAT":
            self.advance(); return Literal(float(t.value), "Float", t.line)
        if t.kind == "STRING":
            self.advance(); return Literal(t.value, "Text", t.line)
        if t.kind in ("TRUE", "FALSE"):
            self.advance(); return Literal(t.kind == "TRUE", "Bool", t.line)
        if t.kind == "IDENT":
            self.advance(); return Name(t.value, t.line)
        if t.kind == "LPAREN":
            self.advance()
            value = self.expression()
            self.expect("RPAREN", "expected ')'")
            return value
        raise NovaSyntaxError(f"Line {t.line}, column {t.column}: expected expression")
