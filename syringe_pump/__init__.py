from datetime import datetime
from typing import List, Literal

import aioserial
from pydantic import PrivateAttr

from .exceptions import *
from .rate import Rate
from .serial_interface import SerialInterface
from .syringe import Syringe


class Pump(SerialInterface):
    """High-level interface for the Legato 100 syringe pump.
    Upon initialisation, sets poll mode to on, making prompts parsable.
    """

    @property
    def infusion_rate(self) -> Rate:
        return self._irate

    @property
    def withdrawal_rate(self) -> Rate:
        return self._wrate

    @property
    def syringe(self) -> Syringe:
        return self._syringe

    def __init__(self, *, serial: aioserial.AioSerial):
        super().__init__(serial=serial)
        self._syringe = Syringe(serial=self.serial)
        self._irate = Rate(serial=self.serial, letter="i")
        self._wrate = Rate(serial=self.serial, letter="w")

        super()._prepare_pump()

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

    async def version(self):
        output = await self._write("version")
        return _parse_colon_mapping(output.message)

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


def _parse_colon_mapping(lines: List[str]):
    data = {}
    for line in lines:
        key, val = line.split(":", 1)
        data[key] = val.strip()
    return data
