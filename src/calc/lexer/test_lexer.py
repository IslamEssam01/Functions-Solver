import pytest
from .LexerError import LexerError
from .lexer import Lexer
from ..token.token import Token


def test_lexer_basic():
    # testing integers, variable, and basic operators
    input_str: str = "1 2 3 4 1234 x (+-*/^)."
    expected_output: list[Token] = [
        Token(type="number", value=1),
        Token(type="number", value=2),
        Token(type="number", value=3),
        Token(type="number", value=4),
        Token(type="number", value=1234),
        Token(type="variable", value="x"),
        Token(type="lparen", value="("),
        Token(type="plus", value="+"),
        Token(type="minus", value="-"),
        Token(type="asterisk", value="*"),
        Token(type="slash", value="/"),
        Token(type="exponent", value="^"),
        Token(type="rparen", value=")"),
        Token(type="dot", value="."),
    ]
    lexer = Lexer(input_str)
    tokens = lexer.tokens
    assert tokens == expected_output, "Test failed: lexer basic"


def test_lexer_floats():
    # testing floating point numbers
    input_str: str = "3.14 0.3 5.0"
    expected_output: list[Token] = [
        Token(type="number", value=3.14),
        Token(type="number", value=0.3),
        Token(type="number", value=5.0),
    ]
    lexer = Lexer(input_str)
    tokens = lexer.tokens
    assert tokens == expected_output, "Test failed: lexer floats"


def test_lexer_functions():
    # testing functions ( everything string that's not the variable is considered a function)
    input_str: str = "sqrt(13) log10(1.4x) ln(0.41x^2) exp(9x)"
    expected_output: list[Token] = [
        Token(type="function", value="sqrt"),
        Token(type="lparen", value="("),
        Token(type="number", value=13),
        Token(type="rparen", value=")"),

        Token(type="function", value="log10"),
        Token(type="lparen", value="("),
        Token(type="number", value=1.4),
        Token(type="variable", value="x"),
        Token(type="rparen", value=")"),

        Token(type="function", value="ln"),
        Token(type="lparen", value="("),
        Token(type="number", value=0.41),
        Token(type="variable", value="x"),
        Token(type="exponent", value="^"),
        Token(type="number", value=2),
        Token(type="rparen", value=")"),

        Token(type="function", value="exp"),
        Token(type="lparen", value="("),
        Token(type="number", value=9),
        Token(type="variable", value="x"),
        Token(type="rparen", value=")"),
    ]

    lexer = Lexer(input_str)
    tokens = lexer.tokens
    assert tokens == expected_output, f"Test failed: lexer functions"


def test_lexer_expressions():
    # combining everything together
    test_cases = [
        (
            "5*x^3 + 2*x - x.3.x",
            [
                Token(type="number", value=5),
                Token(type="asterisk", value="*"),
                Token(type="variable", value="x"),
                Token(type="exponent", value="^"),
                Token(type="number", value=3),
                Token(type="plus", value="+"),
                Token(type="number", value=2),
                Token(type="asterisk", value="*"),
                Token(type="variable", value="x"),
                Token(type="minus", value="-"),
                Token(type="variable", value="x"),
                Token(type="dot", value="."),
                Token(type="number", value=3),
                Token(type="dot", value="."),
                Token(type="variable", value="x"),
            ],
            "Polynomial",
        ),
        (
            "-x",
            [
                Token(type="minus", value="-"),
                Token(type="variable", value="x"),
            ],
            "Prefix minus operator",
        ),
        (
            "x^(2+1)",
            [
                Token(type="variable", value="x"),
                Token(type="exponent", value="^"),
                Token(type="lparen", value="("),
                Token(type="number", value=2),
                Token(type="plus", value="+"),
                Token(type="number", value=1),
                Token(type="rparen", value=")"),
            ],
            "Exponent with parenthesized expression",
        ),
        (
            "xsqrt(10x)",
            [
                Token(type="variable", value="x"),
                Token(type="function", value="sqrt"),
                Token(type="lparen", value="("),
                Token(type="number", value=10),
                Token(type="variable", value="x"),
                Token(type="rparen", value=")"),
            ],
            "Implict multiplication with function",
        ),
        (
            "((2+3)*5)^2",
            [
                Token(type="lparen", value="("),
                Token(type="lparen", value="("),
                Token(type="number", value=2),
                Token(type="plus", value="+"),
                Token(type="number", value=3),
                Token(type="rparen", value=")"),
                Token(type="asterisk", value="*"),
                Token(type="number", value=5),
                Token(type="rparen", value=")"),
                Token(type="exponent", value="^"),
                Token(type="number", value=2),
            ],
            "Nested parentheses with mixed operators",
        ),

    ]

    for input_str, expected_output, test_name in test_cases:
        lexer = Lexer(input_str)
        tokens = lexer.tokens
        assert tokens == expected_output, f"Test failed: {test_name}"


def test_lexer_errors():
    test_cases = [
        (
            "3.4.2.23",
            "LexerError at position 4: Multiple decimal points",
            "Invalid number with multiple decimal points",
        ),
        (
            "3x,",
            "LexerError at position 3: Invalid character",
            "Invalid character",
        ),

    ]
    for input_str, expected_message, test_name in test_cases:
        with pytest.raises(LexerError) as error:
            Lexer(input_str)

        assert expected_message == str(
            error.value), f"Test failed: {test_name}"
