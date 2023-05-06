from typing import Optional

from quantiphy import Quantity

from .exceptions import *
from .response_parser import extract_quantity
from .serial_interface import SerialInterface


class Syringe(SerialInterface):
    """Expose methods to manage syringe settings."""

    async def get_diameter(self) -> Quantity:
        """Syringe diameter in mm."""
        output = await self._write("diameter")
        diameter, _ = extract_quantity(output.message[0])
        return diameter

    async def set_diameter(self, diameter: float):
        """Set syringe diameter in mm."""
        await self._write(f"diameter {diameter:.4}")

    async def get_volume(self) -> Quantity:
        """Syringe volume in ml."""
        output = await self._write("volume")
        volume, _ = extract_quantity(output.message[0])
        return volume

    async def set_volume(self, volume: Quantity):
        """Set syringe volume."""
        _check_volume(volume)
        await self._write(f"volume {volume:.4}")

    async def set_manufacturer(
        self, manufacturer: str, volume: Optional[Quantity] = None
    ):
        """Set syringe manufacturer and volume in ml or ul."""
        if volume is not None:
            _check_volume(volume)
            await self._write(f"syrmanu {manufacturer} {volume:.4} ")
        else:
            await self._write(f"syrmanu {manufacturer}")


def _check_volume(volume: Quantity):
    if volume.units != "l":
        raise ValueError("Volume must be in ml, ul or nl")
    if volume.real <= 0:
        raise ValueError("Volume must be positive")
