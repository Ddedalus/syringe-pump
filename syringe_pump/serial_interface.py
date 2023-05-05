import aioserial
from pydantic import BaseModel

from .exceptions import *

XON = b"\x11"
_NUMBERS = "0123456789"


class SerialInterface(BaseModel):
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

    def _prepare_pump(self):
        self.serial.write(b"poll on\r\n")
        self.serial.read_until(XON)
        self.serial.write(b"nvram none\r\n")
        self.serial.read_until(XON)
        # TODO: verify the output
        # TODO: execute this async on first command instead
