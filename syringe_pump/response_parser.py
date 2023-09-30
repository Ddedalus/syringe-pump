import re

from pydantic import BaseModel, Field
from quantiphy import Quantity

from syringe_pump.exceptions import PumpError

XON = b"\x11"


class PumpResponse(BaseModel):
    """Structured representation of a response from the pump.
    TODO: move to a dignified location."""

    command: str
    prompt: str = ":"
    address: int = Field(default=0, ge=0, le=99)
    message: list[str] = []
    raw_text: str = ""

    @classmethod
    def from_output(cls, raw_output: bytes, command: str):
        output = raw_output.rstrip(XON).strip().decode()
        if not output:
            raise PumpError("No response from pump")

        self = cls(raw_text=output, command=command)
        lines = output.split("\r\n")
        if lines:
            self._strip_address(lines[-1])
        if self.address:
            lines = [self._strip_address(l) for l in lines]

        if lines[-1]:  # there is prompt in last line, because there is no address
            self.prompt = lines[-1]
        self.message = lines[:-1]
        return self

    def _strip_address(self, line: str) -> str:
        if match := re.match(r"(\d{1,2})(:|[><T]\*?|\*)(.*)", line):
            self.address = int(match.group(1))
            self.prompt = match.group(2)
            return match.group(3)
        return line

    def __str__(self) -> str:
        full_response = "\n".join(self.message)
        return f"Command: {self.command!r}\n Response: {full_response!r}\n"


def extract_quantity(line: str) -> tuple[Quantity, str]:
    """Extract a value and unit from a line of text."""
    try:
        value, unit, *rest = line.split(" ")
        return Quantity(f"{value} {unit}"), " ".join(rest).strip()
    except Exception as e:
        raise PumpError(f"Could not extract value from {line!r}") from e


def extract_string(line: str, prefix: str) -> str:
    """Extract a string from a line of text."""
    try:
        return line.split(prefix, 1)[1].strip()
    except Exception as e:
        raise PumpError(f"Could not extract string from {line!r}") from e
