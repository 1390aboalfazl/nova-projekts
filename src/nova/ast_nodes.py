from dataclasses import dataclass
from typing import Union

@dataclass
class Literal:
    value: object
    literal_type: str
    line: int

@dataclass
class Name:
    value: str
    line: int

@dataclass
class Unary:
    operator: str
    operand: "Expr"
    line: int

@dataclass
class Binary:
    left: "Expr"
    operator: str
    right: "Expr"
    line: int

Expr = Union[Literal, Name, Unary, Binary]

@dataclass
class Let:
    name: str
    declared_type: str
    value: Expr
    line: int

@dataclass
class Show:
    value: Expr
    line: int

@dataclass
class Program:
    name: str
    statements: list
