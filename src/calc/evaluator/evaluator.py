from ..ast.ast import *
from .EvaluatorError import EvaluatorError
from .UnknownFunctionError import UnknownFunctionError
import math


class Evaluator:
    def __init__(self,  ast: ASTNode) -> None:
        """
        Initialize the evaluator with an abstract syntax tree (AST).

        Args:
            ast (ASTNode): The root node of the AST to evaluate.
        """
        self.ast = ast
        self.variable_value = 0

    def evaluate(self, variable_value: int | float) -> int | float:
        """
        Evaluate the AST with a given variable value.

        Args:
            variableValue (int | float): The value to substitute for the variable in the expression.

        Returns:
            int | float: The result of the evaluation.
        """
        self.variable_value = variable_value
        return self.evaluate_expression(self.ast)

    def evaluate_expression(self, ast: ASTNode,) -> int | float:
        """
        Evaluate an expression node in the AST.

        Args:
            ast (ASTNode): The AST node to evaluate.

        Returns:
            int | float: The result of the evaluation.
        """
        if isinstance(ast, NumberLiteral):
            return self.evaluate_number(ast)
        elif isinstance(ast, Variable):
            return self.evaluate_variable()
        elif isinstance(ast, PrefixExpression):
            return self.evaluate_prefix_expression(ast)
        elif isinstance(ast, InfixExpression):
            return self.evaluate_infix_expression(ast)
        elif isinstance(ast, FunctionCall):
            return self.evaluate_function_call(ast)

        return 1

    def evaluate_number(self, number: NumberLiteral) -> int | float:
        """
        Evaluate a number literal node.

        Args:
            number (NumberLiteral): The number literal node to evaluate.

        Returns:
            int | float: The value of the number literal.
        """
        return number.value

    def evaluate_variable(self) -> int | float:
        """
        Evaluate a variable node.

        Returns:
            int | float: The value of the variable.
        """
        return self.variable_value

    def evaluate_prefix_expression(self, expression: PrefixExpression) -> int | float:
        """
        Evaluate a prefix expression node.

        Args:
            expression (PrefixExpression): The prefix expression node to evaluate.

        Returns:
            int | float: The result of the evaluation.
        """
        if expression.operator == "-":
            return -self.evaluate_expression(expression.operand)
        elif expression.operator == "+":
            return self.evaluate_expression(expression.operand)

        raise EvaluatorError("Not a vaild prefix operator")

    def evaluate_infix_expression(self, expression: InfixExpression) -> int | float:
        """
        Evaluate an infix expression node.

        Args:
            expression (InfixExpression): The infix expression node to evaluate.

        Returns:
            int | float: The result of the evaluation.
        """
        match expression.operator:
            case "+":
                return self.evaluate_expression(expression.left)+self.evaluate_expression(expression.right)
            case "-":
                return self.evaluate_expression(expression.left)-self.evaluate_expression(expression.right)
            case "*":
                return self.evaluate_expression(expression.left)*self.evaluate_expression(expression.right)
            case "/":
                dividend = self.evaluate_expression(expression.left)
                divisor = self.evaluate_expression(expression.right)
                if divisor == 0:
                    raise EvaluatorError("Division by zero")
                return dividend/divisor
            case "^":
                return self.evaluate_expression(expression.left)**self.evaluate_expression(expression.right)
            case _:
                raise EvaluatorError("Not a vaild infix operator")

    def evaluate_function_call(self, function: FunctionCall) -> int | float:
        """
        Evaluate a function call node.

        Args:
            function (FunctionCall): The function call node to evaluate.

        Returns:
            int | float: The result of the evaluation.
        """
        match function.function:
            case "sqrt":
                value = self.evaluate_expression(function.parameter)
                if value < 0:
                    raise EvaluatorError("Square root of negative number")
                return math.sqrt(value)
            case "log10":
                value = self.evaluate_expression(function.parameter)
                if value <= 0:
                    raise EvaluatorError("Logarithm of non-positive number")
                return math.log10(value)
            case "sin":
                value = self.evaluate_expression(function.parameter)
                return math.sin(value)
            case "cos":
                value = self.evaluate_expression(function.parameter)
                return math.cos(value)
            case _:
                raise UnknownFunctionError(function.function)
