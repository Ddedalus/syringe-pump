from typing import TYPE_CHECKING

from quantiphy import Quantity

from syringe_pump.exceptions import PumpCommandError
from syringe_pump.response_parser import extract_quantity

if TYPE_CHECKING:
    from .pump import Pump


class Volume:
    def __init__(self, pump: "Pump", letter: str = "i") -> None:
        self.letter = letter
        self._pump = pump

    async def clear(self):
        """Clear the volume dispensed counter."""
        await self._pump._write(f"c{self.letter}volume", error_state_ok=True)

    async def get(self):
        """Get the volume dispensed."""
        output = await self._pump._write(f"{self.letter}volume", error_state_ok=True)
        volume, _ = extract_quantity(output.message[0])
        return volume


class TargetVolume:
    """Expose methods to manage a target volume."""

    def __init__(self, pump: "Pump") -> None:
        self._pump = pump

    async def clear(self):
        """Clear the target volume."""
        await self._pump._write(f"ctvolume", error_state_ok=True)

    async def get(self) -> Quantity | None:
        """Get the currently set target volume."""
        output = await self._pump._write(f"tvolume", error_state_ok=True)
        if "Target volume not set" in output.message[0]:
            return None
        volume, _ = extract_quantity(output.message[0])
        return volume

    async def set(self, volume: Quantity):
        """Set the target volume."""
        _check_volume(volume)
        try:
            await self._pump._write(f"tvolume {volume:.4}")
        except PumpCommandError as e:
            if "out of range" in str(e):
                raise ValueError("Target volume out of range") from e
            raise e


def _check_volume(volume: Quantity):
    if volume.real <= 0:
        raise ValueError("Volume must be positive.")
    if volume.units != "l":
        raise ValueError("Target volume must be in (mili)liters.")
