import aioserial
from typing_extensions import Protocol

from syringe_pump.exceptions import *
from syringe_pump.response_parser import XON, PumpResponse


class PumpSerial:
    """Provides wrapper methods to send commands and receive pump responses."""

    def __init__(self, serial: aioserial.AioSerial) -> None:
        self.serial = serial
        self._initialised: bool = False

    async def _initialise(self):
        """Ensure the pump is configured correctly to receive commands."""
        self._initialised = True
        await self._write("poll on")
        # disable NVRAM storage which could be damaged by repeated writes
        await self._write("nvram none")

    async def _write(self, command: str):
        # TODO: configure whether screen is refreshed on command
        if not self._initialised:
            raise PumpError("Pump not initialised. Call `_initialise()` first.")
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
