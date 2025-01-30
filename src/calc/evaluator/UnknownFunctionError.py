class UnknownFunctionError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Unknown Function: {message}")
