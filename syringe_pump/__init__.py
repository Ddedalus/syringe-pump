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


def _parse_colon_mapping(output: str):
    lines = output.split("\r\n")[:-1]  # skip the prompt line
    data = {}
    for line in lines:
        key, val = line.split(":", 1)
        data[key] = val.strip()
    return data
