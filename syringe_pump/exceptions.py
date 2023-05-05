class PumpError(Exception):
    """Error condition reported by the Legato pump."""

    pass


class PumpCommandError(PumpError):
    """Executing a command caused an error to be displayed."""

    def __init__(self, message: str, command: str, *args) -> None:
        self.message = message
        self.command = command
        super().__init__(*args)

    def __str__(self) -> str:
        return f"Got {self.message!r} while executing {self.command!r}"


class PumpStateError(PumpError):
    """The pump reported an error state via the prompt."""

    def __init__(self, state: str, command: str, *args: object) -> None:
        self.state = state
        self.command = command
        super().__init__(*args)

    def __str__(self) -> str:
        return f"Unxpected pump state {self.state!r} after executing {self.command!r}"
