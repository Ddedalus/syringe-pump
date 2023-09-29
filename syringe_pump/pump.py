from contextlib import AbstractAsyncContextManager
from datetime import datetime
from functools import cached_property
from logging import getLogger
from typing import Literal

import aioserial
from pydantic import BaseModel, Field

from syringe_pump.exceptions import PumpError
from syringe_pump.rate import Rate
from syringe_pump.serial_interface import PumpSerial
from syringe_pump.syringe import Syringe
from syringe_pump.time import TargetTime
from syringe_pump.volume import TargetVolume, Volume

logger = getLogger(__name__)


class PumpVersion(BaseModel):
    firmware: str = Field(default=..., alias="Firmware")
    address: int = Field(default=..., alias="Pump address")
    serial_number: str = Field(default=..., alias="Serial number")


QS_MODE_CODE = Literal["i", "w", "iw", "wi"]
EXIT_BRIGHTNESS = 15


class Pump(PumpSerial, AbstractAsyncContextManager):
    """High-level interface for the Legato 100 syringe pump."""

    @classmethod
    async def from_serial(cls, serial: aioserial.AioSerial):
        """Initialise the pump outside of a context manager. Useful for quick scripts.
        This method will:
         * disable NVRAM storage
         * set the pump to infuse-withdraw mode
         * ensure the clock on the pump is up to date
         * configure the serial protocol into a machine-readable format
        """
        self = cls(serial=serial)
        await self._initialise()
        return self

    @cached_property
    def infusion_rate(self) -> Rate:
        """Get, set or clear the infusion rate."""
        return Rate(pump=self, letter="i")

    @cached_property
    def withdrawal_rate(self) -> Rate:
        """Get, set or clear the withdrawal rate."""
        return Rate(pump=self, letter="w")

    @cached_property
    def syringe(self) -> Syringe:
        """View or edit the syringe properties that are used to calculate flow rates and volumes."""
        return Syringe(pump=self)

    @cached_property
    def infusion_volume(self) -> Volume:
        """Reset or get the infusion volume that the pump keeps track of."""
        return Volume(pump=self, letter="i")

    @cached_property
    def withdrawal_volume(self) -> Volume:
        """Reset or get the withdrawal volume that the pump keeps track of."""
        return Volume(pump=self, letter="w")

    @cached_property
    def target_volume(self) -> TargetVolume:
        """Clear, get or set the maximum volume the pump is allowed to dispense."""
        return TargetVolume(pump=self)

    @cached_property
    def target_time(self) -> TargetTime:
        """Clear, get or set the maximum time the pump is allowed to dispense."""
        return TargetTime(pump=self)

    async def _initialise(self):
        await super()._initialise()
        await self.set_mode("iw")  # set pump to infusion and withdrawal mode
        await self.set_clock()  # set pump time to current time

    async def __aenter__(self):
        await self._initialise()
        return self

    async def __aexit__(self, *args):
        await self.stop()
        try:
            await self.set_brightness(EXIT_BRIGHTNESS)
        except PumpError:
            logger.error("Failed to reset display brightness on exit!")
        self._initialised = False

    async def run(self, direction: Literal["infuse", "withdraw"] = "infuse"):
        """Start infusing or withdrawing. You need to set a rate first."""
        if direction == "infuse":
            await self._write("irun")
        elif direction == "withdraw":
            await self._write("wrun")
        else:
            raise ValueError("Direction must be 'infuse' or 'withdraw'")

    async def stop(self):
        """Stop infusing or withdrawing."""
        await self._write("stp")

    async def set_brightness(self, brightness: int):
        """Adjust brightness of the built-in pump display. Set to 0 to turn off the display."""
        if brightness < 0 or brightness > 100:
            raise PumpError("Brightness must be integer between 0 and 100")
        await self._write(f"dim {brightness}")

    async def version(self) -> PumpVersion:
        """See pump version and serial number."""
        output = await self._write("version")
        data = _parse_colon_mapping(output.message)
        return PumpVersion(**data)

    async def set_force(self, force: int):
        """Set the percentage of the maximum force to use when dispensing."""
        if force < 0 or force > 100:
            raise ValueError("Force must be integer between 0 and 100")
        await self._write(f"force {force}")

    async def get_force(self):
        output = await self._write("force")
        return int(output.message[0].strip("%"))

    async def set_address(self, address: int):
        if address < 0 or address > 99:
            raise ValueError("Address must be integer between 0 and 99")
        output = await self._write(f"addr {address}")
        return output.address

    async def set_clock(self):
        """Set the pump internal clock to the current time."""
        # Accepted format:  mm/dd/yy hh:mm:ss
        now = datetime.now().strftime("%m/%d/%y %H:%M:%S")
        response = await self._write(f"time {now}")
        return response.message[0]

    async def set_mode(self, mode: QS_MODE_CODE = "iw"):
        """Set the Quick Start mode, enabling / disabling infusion and withdrawal."""
        return await self._write(f"load qs {mode}")

    async def get_mode(self) -> str:
        """Get the current pump mode."""
        output = await self._write("load")
        return output.message[0]


def _parse_colon_mapping(lines: list[str]):
    data = {}
    for line in lines:
        key, val = line.split(":", 1)
        data[key] = val.strip()
    return data
