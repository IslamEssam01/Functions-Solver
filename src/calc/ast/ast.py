from abc import ABC, abstractmethod
from sympy import symbols,  Add, Mul, Pow, sqrt, log,  Expr, sin, cos
from ..parser.ParserError import ParserError
from typing import no_type_check


x: Expr = symbols("x", real=True)


# Abstract base class to use as a general type
class ASTNode(ABC):
    # This function must be implemented in all AST nodes to be able to solve symbolically
    @abstractmethod
    def to_sympy_expr(self) -> Expr | int | float:
        pass


# AST node representing a number literal
class NumberLiteral(ASTNode):
    def __init__(self, value: float | int) -> None:
        self.value:  float | int = value

    def __eq__(self, value: object, /) -> bool:
        return (isinstance(value, NumberLiteral) and value.value == self.value)

    def __repr__(self) -> str:
        return f"{self.value}"

    def to_sympy_expr(self) -> int | float:
        return self.value


# AST node representing a variable
class Variable(ASTNode):
    def __init__(self, value: str) -> None:
        self.value: str = value

    def __eq__(self, value: object, /) -> bool:
        return (isinstance(value, Variable) and value.value == self.value)

    def __repr__(self) -> str:
        return f"{self.value}"

    def to_sympy_expr(self) -> Expr:
        return x


# AST node representing a prefix expression (e.g., -x)
class PrefixExpression(ASTNode):
    def __init__(self, operator: str, operand: ASTNode) -> None:
        self.operator = operator
        self.operand = operand

    def __eq__(self, value: object, /) -> bool:
        return (isinstance(value, PrefixExpression) and value.operator == self.operator and value.operand == self.operand)

    def __repr__(self) -> str:
        return f"{self.operator}{self.operand}"

    def to_sympy_expr(self) -> Expr:
        match self.operator:
            case "-": return Mul(self.operand.to_sympy_expr(), -1)
            case _: raise ParserError("Not a valid prefix operator")


# AST node representing an infix expression (e.g., x + y)
class InfixExpression(ASTNode):
    def __init__(self, left: ASTNode, operator: str, right: ASTNode) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def __eq__(self, value: object, /) -> bool:
        return (isinstance(value, InfixExpression) and value.left == self.left and value.operator == self.operator and value.right == self.right)

    def __repr__(self) -> str:
        return f"{self.left}{self.operator}{self.right}"

    def to_sympy_expr(self) -> Expr:
        match self.operator:
            case "+": return Add(self.left.to_sympy_expr(), self.right.to_sympy_expr())
            case "-": return Add(self.left.to_sympy_expr(), Mul(self.right.to_sympy_expr(), -1))
            case "*": return Mul(self.left.to_sympy_expr(), self.right.to_sympy_expr())
            case "/": return Mul(self.left.to_sympy_expr(), Pow(self.right.to_sympy_expr(), -1))
            case "^": return Pow(self.left.to_sympy_expr(), self.right.to_sympy_expr())
            case _: raise ParserError("Not a valid infix operator")


# AST node representing a function call (e.g., sqrt(x))
class FunctionCall(ASTNode):
    def __init__(self, function: str, parameter: ASTNode) -> None:
        self.function = function
        self.parameter = parameter

    def __eq__(self, value: object, /) -> bool:
        return (isinstance(value, FunctionCall) and value.function == self.function and value.parameter == self.parameter)

    def __repr__(self) -> str:
        return f"{self.function}({self.parameter})"

    @no_type_check
    def to_sympy_expr(self) -> Expr:
        match self.function:
            case "sqrt": return sqrt(self.parameter.to_sympy_expr())
            case "log10": return log(self.parameter.to_sympy_expr(), 10)
            case "sin": return sin(self.parameter.to_sympy_expr())
            case "cos": return cos(self.parameter.to_sympy_expr())

            case _: raise ParserError("Not a valid function", -1)
