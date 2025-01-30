class LexerError(Exception):
    def __init__(self, message: str, position: int) -> None:
        super().__init__(f"LexerError at position {position}: {message}")
        self.message = message
