import re
from typing import Tuple

import aioserial

from .exceptions import *
from .serial_interface import SerialInterface


class Rate(SerialInterface):
    """Expose methods to manage a rate of infusion or withdrawal."""

    def __init__(self, serial: aioserial.AioSerial, letter: str = "i") -> None:
        super().__init__(serial=serial)
        self.letter = letter

    async def get(self) -> float:
        """Get the currently set rate of infusion or withdrawal in ml/min."""
        output = await self._write(f"{self.letter}rate")
        match = re.match(r"(?:\d\d:)?(\d*\.\d+) (ul|ml)/min", output)
        if not match:
            raise PumpCommandError(output, f"{self.letter}rate")
        per_unit = 1.0 if match.group(3) == "ml" else 1e-3
        return float(match.group(2)) * per_unit

    async def set(self, rate: float, unit: str = "ml/min"):
        if rate <= 0.0:
            raise PumpError("Infusion rate must be positive!")
        return await self._write(f"irate {float(rate):.4} {unit}")

    async def get_limits(self) -> Tuple[float, float]:
        """Get the minimum and maximum rate of infusion or withdrawal in ml/min."""
        output = await self._write("irate lim")
        # e.g. .0404 nl/min to 26.0035 ml/min
        match = re.match(
            r"(?:\d\d:)?(\d*\.\d+) (ul|ml)/min to (\d*\.\d+) (ul|ml)/min", output
        )
        if not match:
            raise PumpCommandError(output, "irate lim")
        per_unit_min = 1.0 if match.group(1) == "ml" else 1e-3
        per_unit_max = 1.0 if match.group(3) == "ml" else 1e-3
        return (
            float(match.group(2)) * per_unit_min,
            float(match.group(4)) * per_unit_max,
        )

    async def get_ramp(self) -> float:
        """Get the the target infusion rate while ramping in ml/min."""
        output = await self._write(f"{self.letter}ramp")
        match = re.match(r"(?:\d\d:)?(\d*\.\d+) (ul|ml)/min", output)
        if not match:
            raise PumpCommandError(output, f"{self.letter}ramp")
        per_unit = 1.0 if match.group(3) == "ml" else 1e-3
        return float(match.group(2)) * per_unit
