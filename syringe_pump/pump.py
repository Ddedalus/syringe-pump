from contextlib import AbstractAsyncContextManager
from datetime import datetime
from functools import cached_property
from logging import getLogger
from typing import List, Literal

import aioserial
from pydantic import BaseModel, Field

from syringe_pump.exceptions import PumpError
from syringe_pump.rate import Rate
from syringe_pump.serial_interface import PumpSerial
from syringe_pump.syringe import Syringe

logger = getLogger(__name__)


class PumpVersion(BaseModel):
    firmware: str = Field(default=..., alias="Firmware")
    address: int = Field(default=..., alias="Pump address")
    serial_number: str = Field(default=..., alias="Serial number")


QS_MODE_CODE = Literal["i", "w", "iw", "wi"]
EXIT_BRIGHTNESS = 15


class Pump(PumpSerial, AbstractAsyncContextManager):
    """High-level interface for the Legato 100 syringe pump."""

    @cached_property
    def infusion_rate(self) -> Rate:
        return Rate(pump=self, letter="i")

    @cached_property
    def withdrawal_rate(self) -> Rate:
        return Rate(pump=self, letter="w")

    @cached_property
    def syringe(self) -> Syringe:
        return Syringe(pump=self)

    @classmethod
    async def from_serial(cls, serial: aioserial.AioSerial):
        self = Pump(serial=serial)
        await self._initialise()
        return self

    async def _initialise(self):
        await super()._initialise()
        await self.set_mode("iw")  # set pump to infusion and withdrawal mode
        await self.set_time()  # set pump time to current time

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
        if direction == "infuse":
            await self._write("irun")
        elif direction == "withdraw":
            await self._write("wrun")
        else:
            raise ValueError("Direction must be 'infuse' or 'withdraw'")

    async def stop(self):
        await self._write("stp")

    async def set_brightness(self, brightness: int):
        if brightness < 0 or brightness > 100:
            raise PumpError("Brightness must be integer between 0 and 100")
        await self._write(f"dim {brightness}")

    async def version(self) -> PumpVersion:
        output = await self._write("version")
        data = _parse_colon_mapping(output.message)
        return PumpVersion(**data)

    async def set_force(self, force: int):
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

    async def set_time(self):
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


def _parse_colon_mapping(lines: List[str]):
    data = {}
    for line in lines:
        key, val = line.split(":", 1)
        data[key] = val.strip()
    return data
