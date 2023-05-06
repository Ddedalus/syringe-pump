import re
from typing import Optional

from .exceptions import *
from .serial_interface import SerialInterface


class Syringe(SerialInterface):
    """Expose methods to manage syringe settings."""

    async def get_diameter(self) -> float:
        """Syringe diameter in mm."""
        output = await self._write("diameter")
        match = re.match(r"(\d*\.\d+) mm", output.message[0])
        if not match:
            raise PumpCommandError(output, "diameter")
        return float(match.group(2))

    async def set_diameter(self, diameter: float):
        """Set syringe diameter in mm."""
        await self._write(f"diameter {diameter:.4}")

    async def get_volume(self) -> float:
        """Syringe volume in ml."""
        output = await self._write("volume")
        match = re.match(r"(\d*\.\d+) (ul|ml)", output.message[0])
        if not match:
            raise PumpCommandError(output, "volume")
        per_unit = 1.0 if match.group(3) == "ml" else 1e-3
        return float(match.group(2)) * per_unit

    async def set_volume(self, volume: float, unit: str = "ml"):
        """Set syringe volume in ml or ul."""
        await self._write(f"volume {volume:.4} {unit}")

    async def set_manufacturer(
        self, manufacturer: str, volume: Optional[float] = None, unit: str = "ml"
    ):
        """Set syringe manufacturer and volume in ml or ul."""
        if volume is not None:
            await self._write(f"syrmanu {manufacturer} {volume:.4} {unit}")
        else:
            await self._write(f"syrmanu {manufacturer}")
