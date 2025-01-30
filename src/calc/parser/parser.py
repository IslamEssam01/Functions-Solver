from typing import Callable, Dict

from .ParserError import ParserError

from ..token.token import Token, TokenType
from ..ast.ast import *


PrefixFunction = Callable[[Token], ASTNode]
InfixFunction = Callable[[ASTNode, Token], ASTNode]


# Precedence levels for different operators
precedences = {
    "plus": 1,  # +
    "minus": 1,  # +
    "asterisk": 2,  # *
    "slash": 2,  # /
    "exponent": 3,  # ^
    "variable": 4,  # any variable (default is x)
    "lparen": 4,  # (
    "function": 4  # any function
}


# Tokens that can have implicit multiplication
implicitMultiplications = ["variable",  # 3x -> 3*x
                           "function",  # 3sqrt(x) -> 3*sqrt(x)
                           "lparen"  # 3(x+2) -> 3*(x+2)
                           ]


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        """
        Initialize the parser with a list of tokens.

        Args:
            tokens (list[Token]): The list of tokens to parse.
        """

        self.tokens = tokens
        self.curToken = 0

        self.prefixFunctions: Dict[str, PrefixFunction] = {}
        self.registerPrefix("number", self.parseNumber)
        self.registerPrefix("variable", self.parseVariable)
        self.registerPrefix("minus", self.parsePrefixExpression)
        self.registerPrefix("plus", lambda _: self.parseExpression())
        self.registerPrefix("lparen", self.parseParen)
        self.registerPrefix("function", self.parseFunction)

        # Infix expressions is everything that's not prefix expressions
        # In this case all infix expressions needs a left and a right expression
        self.infixFunctions: Dict[str, InfixFunction] = {}
        self.registerInfix("plus", self.parseInfixExpression)
        self.registerInfix("minus", self.parseInfixExpression)
        self.registerInfix("asterisk", self.parseInfixExpression)
        self.registerInfix("slash", self.parseInfixExpression)
        self.registerInfix("exponent", self.parseInfixExpression)
        self.registerInfix("variable", self.parseImplicitMultiplication)
        self.registerInfix("lparen", self.parseImplicitMultiplication)
        self.registerInfix("function", self.parseImplicitMultiplication)

    def parse(self) -> ASTNode:
        """
        Parse the list of tokens into an abstract syntax tree (AST).

        Returns:
            ASTNode: The root node of the parsed AST.
        """
        tree = self.parseExpression()

        if self.curToken < len(self.tokens):
            # Having a token not parsed means that the expression isn't a valid equation (e.g., "x3")
            raise ParserError("Not a valid expression")

        return tree

    def parseExpression(self, precedence: int = 0) -> ASTNode:
        """
        Parse an expression based on the current token and precedence level.

        Args:
            precedence (int): The current precedence level (default is 0).

        Returns:
            ASTNode: The parsed expression as an AST node.
        """
        if self.curToken >= len(self.tokens):
            raise ParserError(
                "Nothing to parse at the end of the input")
        token = self.tokens[self.curToken]
        self.curToken += 1
        if token.type not in self.prefixFunctions:
            raise ParserError(
                f"No prefix function for {token.value}")
        prefix = self.prefixFunctions[token.type]
        left = prefix(token)

        # After parsing the prefix token, if the next token has a bigger precedence than the current operation it gets parsed
        # (e.g., 3+2 -> after parsing the 3 the plus gets parsed as an infix expression)
        while (self.curToken < len(self.tokens) and precedence < self.getPrecedence()):
            token = self.tokens[self.curToken]
            if token.type not in implicitMultiplications:
                self.curToken += 1
            infix = self.infixFunctions[token.type]
            left = infix(left, token)

        return left

    def parseNumber(self, token: Token) -> NumberLiteral:
        """
        Parse a number token into a NumberLiteral AST node.

        Args:
            token (Token): The number token to parse.

        Returns:
            NumberLiteral: The parsed number as a NumberLiteral node.
        """
        if not isinstance(token.value, (int, float)):
            raise TypeError("token.value must be int or float")

        return NumberLiteral(token.value)

    def parseVariable(self, token: Token) -> Variable:
        """
        Parse a variable token into a Variable AST node.

        Args:
            token (Token): The variable token to parse.

        Returns:
            Variable: The parsed variable as a Variable node.
        """
        if not isinstance(token.value, str):
            raise TypeError("toke.value must be str")
        return Variable(token.value)

    def parseImplicitMultiplication(self, left: ASTNode, _: Token) -> InfixExpression:
        """
        Parse an implicit multiplication expression.

        Args:
            left (ASTNode): The left-hand side of the expression.
            _ (Token): The token representing the implicit multiplication.

        Returns:
            InfixExpression: The parsed implicit multiplication as an InfixExpression node.
        """
        return InfixExpression(left, "*", self.parseExpression(precedences["asterisk"]))  # We use precedences["asterisk"] to mimic multiplication precedence

    def parsePrefixExpression(self, token: Token) -> PrefixExpression:
        """
        Parse a prefix expression (e.g., -x).

        Args:
            token (Token): The prefix token to parse.

        Returns:
            PrefixExpression: The parsed prefix expression as a PrefixExpression node.
        """
        if not isinstance(token.value, str):
            raise TypeError("toke.value must be str")
        return PrefixExpression(token.value, self.parseExpression())

    def parseInfixExpression(self, left: ASTNode, token: Token) -> InfixExpression:
        """
        Parse an infix expression (e.g., x + y).

        Args:
            left (ASTNode): The left-hand side of the expression.
            token (Token): The infix token to parse.

        Returns:
            InfixExpression: The parsed infix expression as an InfixExpression node.
        """
        if not isinstance(token.value, str):
            raise TypeError("toke.value must be str")

        if token.type == "exponent":
            return InfixExpression(left, token.value, self.parseExpression(precedences[token.type]-1))
        return InfixExpression(left, token.value, self.parseExpression(precedences[token.type]))

    def parseParen(self, _: Token) -> ASTNode:
        """
        Parse a parenthesis expression.

        Args:
            _ (Token): The left parenthesis token.

        Returns:
            ASTNode: The parsed expression inside the parentheses.
        """
        node = self.parseExpression()
        if self.curToken < len(self.tokens) and self.tokens[self.curToken].type != "rparen":
            raise ParserError("Expected right parenthesis")

        self.curToken += 1
        return node

    def parseFunction(self, token: Token) -> FunctionCall:
        """
        Parse a function call expression.

        Args:
            token (Token): The function token to parse.

        Returns:
            FunctionCall: The parsed function call as a FunctionCall node.
        """
        if self.curToken >= len(self.tokens):
            raise ParserError("Expected left parenthesis")
        if self.tokens[self.curToken].type != "lparen":
            raise ParserError("Expected left parenthesis")
        self.curToken += 1
        if not isinstance(token.value, str):
            raise TypeError("Functions must be strings")

        return FunctionCall(token.value, self.parseParen(token))

    def registerPrefix(self, tokenType: TokenType, func: PrefixFunction) -> None:
        """
        Register a prefix function for a given token type.

        Args:
            tokenType (TokenType): The type of token to register the function for.
            func (PrefixFunction): The function to register.
        """
        self.prefixFunctions[tokenType] = func

    def registerInfix(self, tokenType: TokenType, func: InfixFunction) -> None:
        """
        Register an infix function for a given token type.

        Args:
            tokenType (TokenType): The type of token to register the function for.
            func (InfixFunction): The function to register.
        """
        self.infixFunctions[tokenType] = func

    def getPrecedence(self) -> int:
        """
        Get the precedence level of the current token.

        Returns:
            int: The precedence level of the current token.
        """
        if self.tokens[self.curToken].type not in precedences:
            return 0
        return precedences[self.tokens[self.curToken].type]
