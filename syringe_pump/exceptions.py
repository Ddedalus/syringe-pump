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
            f"Got {message!r} while executing {self.response.command!r}"
            f"\n{self.response}"
        )


class PumpStateError(PumpCommandError):
    """The pump reported an error state via the prompt."""

    def _get_message(self) -> str:
        return f"Unexpected pump state {self.response.prompt!r}"

    def __str__(self) -> str:
        return f"Pump state error: {self._get_message()}\n{self.response}"

    @classmethod
    def from_response(cls, response: "PumpResponse") -> "PumpStateError":
        if response.prompt == "T*":
            return TargetReachedError(response)
        elif response.prompt == "*":
            return PumpStalledError(response)
        elif response.prompt in [">*", "<*"]:
            return LimitSwitchError(response)
        else:
            return cls(response)


class TargetReachedError(PumpStateError):
    """Target volume or time was reached and the pump stopped."""

    def _get_message(self) -> str:
        return f"Target volume or time was reached"


class PumpStalledError(PumpStateError):
    """The pumpt stalled because of excessive reistance of the syringe."""

    def _get_message(self) -> str:
        return f"Pump stalled because of excessive resistance of the syringe"


class LimitSwitchError(PumpStateError):
    """Withdraw/infuse limit switch was hit."""

    def _get_message(self) -> str:
        if self.response.prompt == ">*":
            return f"Infuse limit switch activated"
        elif self.response.prompt == "<*":
            return f"Withdraw limit switch activated"
        return "Limit switch activated"
