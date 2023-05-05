import re

import aioserial
from pydantic import BaseModel, PrivateAttr

XON = b"\x11"
_NUMBERS = "0123456789"


class PumpError(Exception):
    """Error condition reported by the Legato pump."""

    pass


class PumpCommandError(PumpError):
    """Executing a command caused an error to be displayed."""

    def __init__(self, message: str, command: str, *args) -> None:
        self.message = message
        self.command = command
        super().__init__(*args)

    def __str__(self) -> str:
        return f"Got {self.message!r} while executing {self.command!r}"


class PumpStateError(PumpError):
    """The pump reported an error state via the prompt."""

    def __init__(self, state: str, command: str, *args: object) -> None:
        self.state = state
        self.command = command
        super().__init__(*args)

    def __str__(self) -> str:
        return f"Unxpected pump state {self.state!r} after executing {self.command!r}"


class BaseInterface(BaseModel):
    """Provides wrapper methods to send commands and receive pump responses."""

    serial: aioserial.AioSerial

    class Config:
        arbitrary_types_allowed = True

    async def _write(self, command: str):
        await self.serial.write_async((command + "\r\n").encode())
        return await self._parse_prompt(command=command)

    async def _parse_prompt(self, command: str = "") -> str:
        # relies on poll mode being on
        raw_output = await self.serial.read_until_async(XON)
        output = raw_output.rstrip(XON).strip().decode()
        # TODO: fully handle device number
        output = output.lstrip(_NUMBERS)

        if "error" in output:
            message = output.split("\r")[1].strip()
            raise PumpCommandError(message, command)

        prompt = output.split("\r\n")[-1].lstrip(_NUMBERS)
        if prompt not in [":", ">", "<"]:
            raise PumpStateError(output, command)
        return output


class Syringe(BaseInterface):
    """Expose methods to manage syringe settings."""

    async def get_diameter(self) -> float:
        """Syringe diameter in mm."""
        output = await self._write("diameter")
        match = re.match(r"(\d\d:)?(\d*\.\d+) mm", output)
        if not match:
            raise PumpCommandError(output, "diameter")
        return float(match.group(2))


class Pump(BaseInterface):
    """High-level interface for the Legato 100 syringe pump.
    Upon initialisation, sets poll mode to on, making prompts parsable.
    """

    _syringe: Syringe = PrivateAttr(...)

    @property
    def syringe(self) -> Syringe:
        return self._syringe

    def __init__(self, **data):
        super().__init__(**data)
        self._syringe = Syringe(serial=self.serial)

        self.serial.write(b"poll on\r\n")
        self.serial.read_until(XON)
        self.serial.write(b"nvram none\r\n")
        self.serial.read_until(XON)
        # TODO: verify the output
        # TODO: execute this async on first command instead

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

    async def set_infusion_rate(self, rate: float, unit: str = "ml/min"):
        if rate == 0:
            raise PumpError("Infusion rate must be positive!")
        return await self._write(f"irate {float(rate):.4} {unit}")

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
