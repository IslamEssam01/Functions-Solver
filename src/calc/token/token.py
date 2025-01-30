from typing import Literal


TokenType = Literal["number", "variable",
                    "minus", "plus", "slash", "asterisk", "dot", "exponent", "lparen", "rparen", "function"]


class Token:
    def __init__(self, type: TokenType, value: str | float | int) -> None:
        self.type = type
        self.value = value

    def __eq__(self, value: object, /) -> bool:
        return (isinstance(value, Token) and self.type == value.type and self.value == value.value)

    def __repr__(self) -> str:
        return f"Token(type={self.type!r}, value={self.value!r})"
