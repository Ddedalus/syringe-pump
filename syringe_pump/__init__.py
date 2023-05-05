from pydantic import PrivateAttr

from .exceptions import *
from .rate import Rate
from .serial_interface import SerialInterface
from .syringe import Syringe


class Pump(SerialInterface):
    """High-level interface for the Legato 100 syringe pump.
    Upon initialisation, sets poll mode to on, making prompts parsable.
    """

    _syringe: Syringe = PrivateAttr(...)
    _irate: Rate = PrivateAttr(...)

    @property
    def infusion_rate(self) -> Rate:
        return self._irate

    @property
    def syringe(self) -> Syringe:
        return self._syringe

    def __init__(self, **data):
        super().__init__(**data)
        self._syringe = Syringe(serial=self.serial)
        self._irate = Rate(serial=self.serial, letter="i")

        super()._prepare_pump()

    async def start(self):
        await self._write("run")

    async def stop(self):
        await self._write("stp")

    async def set_brightness(self, brightness: int):
        if brightness < 0 or brightness > 100:
            raise PumpError("Brightness must be integer between 0 and 100")
        await self._write(f"dim {brightness}")

    async def version(self):
        output = await self._write("version")
        return _parse_colon_mapping(output)

    async def set_withdrawal_rate(self, rate: float, unit: str = "ml/min"):
        return await self._write(f"wrate {rate} {unit}")

    async def get_rate_limits(self):
        return await self._write("irate lim")

    async def get_infusion_rate(self):
        return await self._write("irate")


def _parse_colon_mapping(output: str):
    lines = output.split("\r\n")[:-1]  # skip the prompt line
    data = {}
    for line in lines:
        key, val = line.split(":", 1)
        data[key] = val.strip()
    return data
