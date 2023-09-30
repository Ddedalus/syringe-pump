import aioserial

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
        await self._write("poll on", error_state_ok=True)
        # disable NVRAM storage which could be damaged by repeated writes
        try:
            await self._write("nvram none", error_state_ok=True)
        except PumpCommandError as e:  # Discrepancy between certain pump models
            if "Argument error: none" in e.response.message[0]:
                await self._write("nvram off", error_state_ok=True)
            raise e

    async def _write(self, command: str, error_state_ok: bool = False) -> PumpResponse:
        # TODO: configure whether screen is refreshed on command
        if not self._initialised:
            raise PumpError("Pump not initialised. Call `_initialise()` first.")
        await self.serial.write_async(f"@{command}\r\n".encode())
        response, state_ok = await self._parse_prompt(command=command)
        if state_ok or error_state_ok:
            return response

        raise PumpStateError.from_response(response)

    async def _parse_prompt(self, command: str = "") -> tuple[PumpResponse, bool]:
        # relies on poll mode being on
        raw_output = await self.serial.read_until_async(XON)
        response = PumpResponse.from_output(raw_output, command)

        if response.message and "error" in response.message[0]:
            raise PumpCommandError(response)

        return response, response.prompt in [":", ">", "<"]
