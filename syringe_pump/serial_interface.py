import aioserial

from .exceptions import *

XON = b"\x11"
_NUMBERS = "0123456789"


class SerialInterface:
    """Provides wrapper methods to send commands and receive pump responses."""

    def __init__(self, serial: aioserial.AioSerial) -> None:
        self.serial = serial

    async def _write(self, command: str):
        # TODO: configure whether screen is refreshed on command
        await self.serial.write_async(f"@{command}\r\n".encode())
        return await self._parse_prompt(command=command)

    async def _parse_prompt(self, command: str = "") -> str:
        # relies on poll mode being on
        raw_output = await self.serial.read_until_async(XON)
        output = raw_output.rstrip(XON).strip().decode()
        # TODO: handle device number

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