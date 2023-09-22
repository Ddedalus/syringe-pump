from typing import TYPE_CHECKING, Optional, Tuple

from pydantic import BaseModel
from quantiphy import Quantity

from syringe_pump.response_parser import extract_quantity, extract_string

if TYPE_CHECKING:
    from .pump import Pump


class RateRampInfo(BaseModel):
    start: Quantity
    end: Quantity
    duration: float


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

    async def get_ramp(self) -> Optional[RateRampInfo]:
        """Get information about current ramp, i.e. linear change of pump speed"""
        output = await self._pump._write(f"{self.letter}ramp")
        if "Ramp not set up." in output.message[0]:
            return None
        start, line = extract_quantity(output.message[0])
        line = extract_string(line, "to")
        end, line = extract_quantity(line)
        line = extract_string(line, "in")
        duration, _ = extract_quantity(line)
        return RateRampInfo(start=start, end=end, duration=float(duration))

    async def set_ramp(self, start: Quantity, end: Quantity, duration: float):
        """Set up a linear change of pump speed, i.e. a ramp.

        Ramp duration is in seconds.
        """
        _check_rate(start)
        _check_rate(end)
        if duration <= 0:
            raise ValueError("Duration must be positive")
        command = f"{self.letter}ramp {start:.4} {end:.4} {float(duration):.4}"
        await self._pump._write(command)

    async def reset_ramp(self):
        """Reset the ramp by clearing target time."""
        return await self._pump._write(f"cttime")


def _check_rate(rate: Quantity):
    if rate.real <= 0:
        raise ValueError("Rate must be positive")
    if rate.units != "l/min":
        raise ValueError(f"Rate must be in ml/min, ul/min or nl/min; got {rate.units}")
