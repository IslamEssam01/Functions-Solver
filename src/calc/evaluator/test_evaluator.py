import pytest

from .UnknownFunctionError import UnknownFunctionError

from .EvaluatorError import EvaluatorError

from .evaluator import Evaluator
from ..lexer.lexer import Lexer
from ..parser.parser import Parser


def test_evaluator_basic():
    # (expression,variable value , expected output, test name)
    test_cases = [
        ("5", None, 5.0, "Number literal"),
        ("x", 2.0, 2.0, "Variable substitution"),
        ("x", -5.0, -5.0, "Negative variable"),
        ("-5", None, -5.0, "One minus (literal)"),
        ("-x", 3.0, -3.0, "One minus (variable)"),
        ("3 + 4", None, 7.0, "Addition"),
        ("10 - 3", None, 7.0, "Subtraction"),
        ("6 * 4", None, 24.0, "Multiplication"),
        ("12 / 3", None, 4.0, "Division"),
        ("2 ^ 3", None, 8.0, "Exponent (integer)"),
        ("4 ^ 0.5", None, 2.0, "Exponent (sqrt)"),
    ]
    for expression, variable_value, expected_output, test_name in test_cases:
        lexer = Lexer(expression)
        tokens = lexer.tokens
        parser = Parser(tokens)
        ast = parser.parse()
        evaluator = Evaluator(ast)
        result = evaluator.evaluate(variable_value)
        assert round(result, 4) == pytest.approx(
            expected_output, abs=1e-6), f"Test failed: {test_name}"


def test_evaluator_expressions():
    test_cases = [

        ("3 + 4 * 5", None, 23.0, "Precedence (multiplication first)"),
        ("(3 + 4) * 5", None, 35.0, "Parentheses override precedence"),
        ("2 ^ 3 ^ 2", None, 512.0, "Right associativity for exponentiation"),
        ("x^4 - 3x^3", 2.0, -8.0, "Fourth power polynomial with cubic term"),
        ("x^3 + 2*x^2 - 5*x", 3.0, 30.0, "Mixed power polynomial"),
        ("sqrt(x^2 + 4) * log10(x + 1)", 3.0, 2.1708, "Mixed function expression"),
        ("sqrt(16)", None, 4.0, "Square root function"),
        ("log10(100)", None, 2.0, "Logarithm base 10"),
        ("sqrt(x^2)", 5.0, 5.0, "Function with expression argument"),
        ("5x", 3.0, 15.0, "Implicit multiplication (number and variable)"),
        ("x(3 + 4)", 2.0, 14.0, "Implicit multiplication (variable and parentheses)"),
        ("sqrt(3^2 + 4^2)", None, 5.0, "Pythagorean theorem"),
        ("log10(1000) + 5 * 2", None, 13.0, "Mixed operations and functions"),
    ]
    for expression, variable_value, expected_output, test_name in test_cases:
        lexer = Lexer(expression)
        tokens = lexer.tokens
        parser = Parser(tokens)
        ast = parser.parse()
        evaluator = Evaluator(ast)
        result = evaluator.evaluate(variable_value)
        assert round(result, 4) == pytest.approx(
            expected_output, abs=1e-6), f"Test failed: {test_name}"


def test_evaluator_errors():
    test_cases = [
        ("5 / 0", None, "EvaluatorError: Division by zero"),
        ("x / 0", 10.0, "EvaluatorError: Division by zero"),
        ("sqrt(-1)", None, "EvaluatorError: Square root of negative number"),
        ("log10(0)", None, "EvaluatorError: Logarithm of non-positive number"),
        ("log10(-5)", None, "EvaluatorError: Logarithm of non-positive number"),
    ]
    for expression, variable_value, expected_message in test_cases:
        lexer = Lexer(expression)
        tokens = lexer.tokens
        parser = Parser(tokens)
        ast = parser.parse()
        evaluator = Evaluator(ast)
        with pytest.raises(EvaluatorError) as error:
            evaluator.evaluate(variable_value)
        assert expected_message == str(
            error.value), f"Error message missing: {expected_message}"


def test_unkown_function():
    lexer = Lexer("foo(5)")
    tokens = lexer.tokens
    parser = Parser(tokens)
    ast = parser.parse()
    evaluator = Evaluator(ast)
    with pytest.raises(UnknownFunctionError) as error:
        evaluator.evaluate(0)

    assert "Unknown Function: foo" == str(
        error.value), "Error message missing: Unknown Function: foo"
