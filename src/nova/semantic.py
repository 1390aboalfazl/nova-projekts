from .ast_nodes import Let, Show, Literal, Name, Unary, Binary
from .errors import NovaTypeError

NUMERIC = {"Int", "Float"}

def infer(expr, symbols):
    if isinstance(expr, Literal):
        return expr.literal_type
    if isinstance(expr, Name):
        if expr.value not in symbols:
            raise NovaTypeError(f"Line {expr.line}: unknown variable {expr.value!r}")
        return symbols[expr.value]
    if isinstance(expr, Unary):
        typ = infer(expr.operand, symbols)
        if typ not in NUMERIC:
            raise NovaTypeError(f"Line {expr.line}: unary minus requires a number, got {typ}")
        return typ
    if isinstance(expr, Binary):
        left, right = infer(expr.left, symbols), infer(expr.right, symbols)
        if left in NUMERIC and right in NUMERIC:
            if expr.operator == "/" or "Float" in (left, right):
                return "Float"
            return "Int"
        raise NovaTypeError(f"Line {expr.line}: operator {expr.operator!r} not defined for {left} and {right}")
    raise NovaTypeError("internal error: unknown expression")

def check(program):
    symbols = {}
    for stmt in program.statements:
        if isinstance(stmt, Let):
            if stmt.name in symbols:
                raise NovaTypeError(f"Line {stmt.line}: variable {stmt.name!r} already declared")
            actual = infer(stmt.value, symbols)
            expected = stmt.declared_type
            if actual != expected and not (expected == "Float" and actual == "Int"):
                raise NovaTypeError(f"Line {stmt.line}: cannot initialize {expected} variable {stmt.name!r} with {actual}")
            symbols[stmt.name] = expected
        elif isinstance(stmt, Show):
            infer(stmt.value, symbols)
    return symbols
