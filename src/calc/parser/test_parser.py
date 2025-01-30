import pytest

from .ParserError import ParserError
from ..lexer.lexer import Lexer
from ..ast.ast import *
from ..parser.parser import Parser


def test_parser_basic():
    # testing basic AST nodes parsing
    test_cases = [
        (
            "5",
            NumberLiteral(5),
            "Number literal"
        ),
        (
            "x",
            Variable("x"),
            "Variable"
        ),

    ]

    for input_str, expected_ast, test_name in test_cases:
        lexer = Lexer(input_str)
        tokens = lexer.tokens
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast == expected_ast, f"Test failed: {test_name}"


def test_parser_prefix_expressions():
    # testing prefix expression AST (e.g., +x , -x)
    test_cases = [
        (
            "-5",
            PrefixExpression("-", NumberLiteral(5.0)),
            "One minus"
        ),
        (
            "-x",
            PrefixExpression("-", Variable("x")),
            "One minus on variable"
        ),
        (
            "--x",
            PrefixExpression("-", PrefixExpression("-", Variable("x"))),
            "Multiple minuses on variable"
        ),

        # Plus in the prefix position has no effect
        (
            "+5",
            NumberLiteral(5.0),
            "One plus"
        ),
        (
            "+x",
            Variable("x"),
            "One plus on variable"
        ),
        (
            "+-x",
            PrefixExpression("-", Variable("x")),
            "One plus then one minus on variable"
        ),
    ]
    for input_str, expected_ast, test_name in test_cases:
        lexer = Lexer(input_str)
        tokens = lexer.tokens
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast == expected_ast, f"Test failed: {test_name}"


def test_parser_infix_expressions_with_precedence():
    # testing infix expressions and precedence
    test_cases = [
        (
            "3 + 4",
            InfixExpression(NumberLiteral(3.0), "+", NumberLiteral(4.0)),
            "Simple addition"
        ),
        (
            "3 * 4 + 5",
            InfixExpression(
                InfixExpression(NumberLiteral(3.0), "*", NumberLiteral(4.0)),
                "+",
                NumberLiteral(5.0)
            ),
            "Precedence: multiplication before addition"
        ),
        (
            "3 + 4 * 5",
            InfixExpression(
                NumberLiteral(3.0),
                "+",
                InfixExpression(NumberLiteral(4.0), "*", NumberLiteral(5.0))
            ),
            "Precedence: addition after multiplication"
        ),
        (
            "3 ^ 2 ^ 2",
            InfixExpression(
                NumberLiteral(3.0),
                "^",
                InfixExpression(NumberLiteral(2.0), "^", NumberLiteral(2.0))
            ),
            "Right associativity for exponent"
        ),
        # ----- Parentheses -----
        (
            "(3 + 4) * 5",
            InfixExpression(
                InfixExpression(NumberLiteral(3.0), "+", NumberLiteral(4.0)),
                "*",
                NumberLiteral(5.0)
            ),
            "Parentheses override precedence"
        ),
    ]
    for input_str, expected_ast, test_name in test_cases:
        lexer = Lexer(input_str)
        tokens = lexer.tokens
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast == expected_ast, f"Test failed: {test_name}"


def test_parser_functions():
    # testing functions
    test_cases = [
        (
            "sqrt(16)",
            FunctionCall("sqrt", NumberLiteral(16.0)),
            "Function call with one argument"
        ),
        (
            "log10(100*x)",
            FunctionCall(
                "log10",
                InfixExpression(
                    NumberLiteral(100.0),
                    "*",
                    Variable("x")
                )
            ),
            "Function call with expression argument"
        ),
        (
            "sin(3+x",
            FunctionCall("sin", InfixExpression(
                NumberLiteral(3), "+", Variable("x"))),
            "Function call without closing parentheses"
        ),
    ]
    for input_str, expected_ast, test_name in test_cases:
        lexer = Lexer(input_str)
        tokens = lexer.tokens
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast == expected_ast, f"Test failed: {test_name}"


def test_parser_implicit_multiplication():
    # testing implicit multiplication (3x -> 3*x)
    test_cases = [
        (
            "5x",
            InfixExpression(NumberLiteral(5.0), "*", Variable("x")),
            "Implicit multiplication (number and variable)"
        ),
        (
            "x(3 + 4)",
            InfixExpression(
                Variable("x"),
                "*",
                InfixExpression(NumberLiteral(3.0), "+", NumberLiteral(4.0))
            ),
            "Implicit multiplication after variable"
        ),
        (
            "xsqrt(3 + 4)x",
            InfixExpression(
                Variable("x"),
                "*",
                InfixExpression(FunctionCall("sqrt", InfixExpression(NumberLiteral(3.0), "+", NumberLiteral(4.0))),
                                "*",
                                Variable("x")),
            ),
            "Implicit multiplication after variable"
        ),
    ]

    for input_str, expected_ast, test_name in test_cases:
        lexer = Lexer(input_str)
        tokens = lexer.tokens
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast == expected_ast, f"Test failed: {test_name}"


def test_parser_errors():
    test_cases = [
        (
            "5 +",
            "ParserError: Nothing to parse at the end of the input",
            "Infix operator missing right operand",
        ),
        (
            "-",
            "ParserError: Nothing to parse at the end of the input",
            "Prefix operator missing operand",
        ),
        (
            "3 + * 4",
            "ParserError: No prefix function for *",
            "Invalid operator sequence (missing operand)",
        ),
        (
            "sqrt()",
            "ParserError: No prefix function for )",
            "Function call with no arguments",
        ),
        (
            "3 4",
            "ParserError: Not a valid expression",
            "Unexpected number after expression",
        ),
        (
            "x 5",
            "ParserError: Not a valid expression",
            "Unexpected number after variable",
        ),
        (
            "sqrt",
            "ParserError: Expected left parenthesis",
            "Function without parentheses"
        )


    ]

    for input_str, expected_message, test_name in test_cases:
        with pytest.raises(ParserError) as error:
            tokens = Lexer(input_str).tokens
            Parser(tokens).parse()

        assert expected_message == str(
            error.value), f"Test failed: {test_name}"
