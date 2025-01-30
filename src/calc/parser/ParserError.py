class ParserError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"ParserError: {message}")
