import typing

if typing.TYPE_CHECKING:
    from .response_parser import PumpResponse


class PumpError(Exception):
    """Error condition reported by the Legato pump."""

    pass


class PumpCommandError(PumpError):
    """Executing a command caused an error to be displayed."""

    def __init__(self, response: "PumpResponse", *args) -> None:
        self.response = response
        super().__init__(*args)

    def __str__(self) -> str:
        message = "\n".join(self.response.message)
        return (
            f"Got {message!r} while executing {self.response.command!r}\n"
            f"{self.response.dict()!r}"
        )


class PumpStateError(PumpCommandError):
    """The pump reported an error state via the prompt."""

    def __str__(self) -> str:
        return (
            f"Unexpected pump state {self.response.prompt!r} "
            f"after executing {self.response.command!r}"
        )
