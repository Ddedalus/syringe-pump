""" Control the times configurable in the syringe pump, e.g. target time. """

from datetime import timedelta
from typing import TYPE_CHECKING

from syringe_pump.response_parser import extract_quantity

if TYPE_CHECKING:
    from .pump import Pump


class TargetTime:
    def __init__(self, pump: "Pump") -> None:
        self._pump = pump

    async def get(self) -> timedelta | None:
        """Get the target time as a timedelta object."""
        output = await self._pump._write("ttime")
        message = output.message[0].strip()
        if "Target time not set" in message:
            return None
        if "seconds" in message:
            duration = extract_quantity(output.message[0])[0]
            return timedelta(seconds=float(duration))

        values = reversed(message.split(":"))  # MM:SS or HH:MM:SS
        seconds, minutes, hours, *_ = [int(v) for v in [*values, 0, 0]]

        return timedelta(hours=hours, minutes=minutes, seconds=seconds)

    async def set(self, duration: timedelta | int | None) -> timedelta | None:
        """Set the target time. Accepts:
        * `datetime.timedelta`
        * an integer of seconds
        * `None` to clear the target time
        """
        if duration is None:
            await self.clear()
            return None

        if isinstance(duration, int):
            duration = timedelta(seconds=duration)
        if duration < timedelta(seconds=0):
            raise ValueError("Target time must be positive.")
        if duration > timedelta(hours=99, minutes=59, seconds=59):
            raise ValueError("Target time out of range.")

        if duration > timedelta(hours=1):
            hours = int(duration.total_seconds() // 3600)
            minutes = int(duration.seconds % 3600 // 60)
            time = f"{hours:02d}:{minutes:02d}:{duration.seconds % 60:02d}"
        else:
            time = int(duration.total_seconds())

        await self._pump._write(f"ttime {time}")
        return duration

    async def clear(self):
        """Clear the target time."""
        await self._pump._write("cttime")
