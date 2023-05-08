import aioserial

from .exceptions import *
from .response_parser import XON, PumpResponse


class SerialInterface:
    """Provides wrapper methods to send commands and receive pump responses."""

    def __init__(self, serial: aioserial.AioSerial) -> None:
        self.serial = serial

    async def _write(self, command: str):
        # TODO: configure whether screen is refreshed on command
        await self.serial.write_async(f"@{command}\r\n".encode())
        return await self._parse_prompt(command=command)

    async def _parse_prompt(self, command: str = "") -> PumpResponse:
        # relies on poll mode being on
        raw_output = await self.serial.read_until_async(XON)
        response = PumpResponse.from_output(raw_output, command)

        if response.message and "error" in response.message[0]:
            raise PumpCommandError(response)

        if response.prompt not in [":", ">", "<"]:
            raise PumpStateError(response)
        return response
