from .LexerError import LexerError
from ..token.token import Token


class Lexer:
    def __init__(self, text: str, variable: str = "x") -> None:
        """
        Initialize the Lexer with the input text and optional variable name.

        Args:
            text (str): The input text to be lexed.
            variable (str): The variable name to be used in the lexer (default is "x").
        """
        self.text: str = text
        self.curPosition: int = 0
        self.variable: str = variable
        self.tokens: list[Token] = []
        self.lex()

    def lex(self) -> None:
        """
        Perform lexical analysis on the input text and generate tokens.
        """
        while self.curPosition < len(self.text):
            match self.text[self.curPosition]:
                case self.variable:
                    self.tokens.append(
                        Token("variable", "x"))
                case char if char.isdigit():
                    self.tokens.append(self.read_number())
                    continue
                case char if char.isspace():
                    self.ignoreWhitespaces()
                    continue
                case "-":
                    self.tokens.append(Token("minus", char))
                case "+":
                    self.tokens.append(Token("plus", char))
                case "*":
                    self.tokens.append(
                        Token("asterisk", char))
                case "/":
                    self.tokens.append(Token("slash", char))
                case "^":
                    self.tokens.append(
                        Token("exponent", char))
                case "(":
                    self.tokens.append(Token("lparen", "("))
                case ")":
                    self.tokens.append(Token("rparen", ")"))
                case char if char.isalpha():
                    # Every string that's not the variable is considered a function
                    self.tokens.append(self.read_function())
                    continue
                case ".":
                    self.tokens.append(
                        Token("dot", char))
                case _:
                    raise LexerError("Invalid character", self.curPosition+1)

            self.curPosition += 1

    def peekChar(self) -> str:
        if self.curPosition+1 >= len(self.text):
            return ""
        return self.text[self.curPosition+1]

    def read_number(self) -> Token:
        """
        Read a number from the input text and return a token.

        Returns:
            Token: The token representing the number.
        """
        num: str = ""
        hasDecimalPoint: bool = False
        while self.curPosition < len(self.text):
            if self.text[self.curPosition].isdigit():
                num += self.text[self.curPosition]
            elif self.text[self.curPosition] == "." and self.curPosition+1 < len(self.text) and self.text[self.curPosition+1].isdigit() and hasDecimalPoint == False:
                num += "."
                hasDecimalPoint = True
            elif self.text[self.curPosition] == "." and self.curPosition+1 < len(self.text) and self.text[self.curPosition+1].isdigit() and hasDecimalPoint == True:
                raise LexerError(
                    "Multiple decimal points", self.curPosition+1)
            else:
                break

            self.curPosition += 1

        if hasDecimalPoint == True:
            return Token("number", float(num))

        return Token("number", int(num))

    def read_function(self) -> Token:
        """
        Read a function name from the input text and return a token.

        Returns:
            Token: The token representing the function.
        """
        fun: str = ""
        startingPosition: int = self.curPosition
        while self.curPosition < len(self.text) and self.text[self.curPosition].isalnum():
            fun += self.text[self.curPosition]
            self.curPosition += 1
        return Token("function", fun)

    def ignoreWhitespaces(self) -> None:
        """
        Ignore whitespace characters in the input text.
        """
        while self.curPosition < len(self.text) and self.text[self.curPosition].isspace():
            self.curPosition += 1
