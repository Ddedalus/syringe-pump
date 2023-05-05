import re

from .exceptions import *
from .serial_interface import SerialInterface


class Syringe(SerialInterface):
    """Expose methods to manage syringe settings."""

    async def get_diameter(self) -> float:
        """Syringe diameter in mm."""
        output = await self._write("diameter")
        match = re.match(r"(\d\d:)?(\d*\.\d+) mm", output)
        if not match:
            raise PumpCommandError(output, "diameter")
        return float(match.group(2))
