import re
from typing import TYPE_CHECKING, Tuple

from quantiphy import Quantity

from syringe_pump.response_parser import extract_quantity, extract_string

from .exceptions import *

if TYPE_CHECKING:
    from .pump import Pump


class Rate:
    """Expose methods to manage a rate of infusion or withdrawal."""

    def __init__(self, pump: "Pump", letter: str = "i") -> None:
        self.letter = letter
        self._pump = pump

    async def get(self) -> Quantity:
        """Get the currently set rate of infusion or withdrawal in ml/min."""
        command = f"{self.letter}rate"
        output = await self._pump._write(command)
        rate, _ = extract_quantity(output.message[0])
        return rate

    async def set(self, rate: Quantity):
        """Set the rate of infusion or withdrawal."""
        _check_rate(rate)
        return await self._pump._write(f"{self.letter}rate {rate:.4}")

    async def get_limits(self) -> Tuple[Quantity, Quantity]:
        """Get the minimum and maximum rate of infusion or withdrawal in ml/min."""
        command = f"{self.letter}rate lim"
        output = await self._pump._write(command)  # e.g. .0404 nl/min to 26.0035 ml/min
        low, line = extract_quantity(output.message[0])
        line = extract_string(line, "to")
        high, _ = extract_quantity(line)
        return low, high

    async def get_ramp(self) -> float:
        """Get the the target infusion rate while ramping in ml/min."""
        output = await self._pump._write(f"{self.letter}ramp")
        match = re.match(r"(\d*\.\d+) (ul|ml)/min", output.message[0])
        if not match:
            raise PumpCommandError(output, f"{self.letter}ramp")
        per_unit = 1.0 if match.group(3) == "ml" else 1e-3
        return float(match.group(2)) * per_unit


def _check_rate(rate: Quantity):
    if rate.real <= 0:
        raise ValueError("Rate must be positive")
    if rate.units != "l/min":
        raise ValueError(f"Rate must be in ml/min, ul/min or nl/min; got {rate.units}")
