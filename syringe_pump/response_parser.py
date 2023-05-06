import re
from typing import List

from pydantic import BaseModel, Field

from .exceptions import PumpError

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
