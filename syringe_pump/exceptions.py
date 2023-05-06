import re
from typing import List

from pydantic import BaseModel, Field

XON = b"\x11"


class PumpResponse(BaseModel):
    """Structured representation of a response from the pump.
    TODO: move to a dignified location."""

    command: str
    prompt: str = ":"
    address: int = Field(default=0, ge=0, le=99)
    message: List[str] = []
    raw_text: str = ""

    @classmethod
    def from_output(cls, raw_output: bytes, command: str):
        output = raw_output.rstrip(XON).strip().decode()
        self = cls(raw_text=output, command=command)
        lines = [self._strip_address(l) for l in output.split("\r\n")]

        if not lines:
            raise PumpError("No response from pump")

        self.prompt = lines[-1]
        self.message = lines[:-1]
        return self

    def _strip_address(self, line: str) -> str:
        # TODO: the prompt line may not have a colon
        if re.match(r"\d{1,2}:", line):
            address, content = line.split(":", 1)
            self.address = int(address)
            return content
        return line


class PumpError(Exception):
    """Error condition reported by the Legato pump."""

    pass


class PumpCommandError(PumpError):
    """Executing a command caused an error to be displayed."""

    def __init__(self, response: PumpResponse, *args) -> None:
        self.response = response
        super().__init__(*args)

    def __str__(self) -> str:
        message = "\n".join(self.response.message)
        return f"Got {message!r} while executing {self.response.command!r}"


class PumpStateError(PumpCommandError):
    """The pump reported an error state via the prompt."""

    def __str__(self) -> str:
        return (
            f"Unxpected pump state {self.response.prompt!r} "
            f"after executing {self.response.command!r}"
        )
