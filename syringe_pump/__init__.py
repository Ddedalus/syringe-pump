import aioserial
from pydantic import BaseModel

XON = b"\x11"
_NUMBERS = "0123456789"


class PumpError(Exception):
    """Error condition reported by the Legato pump."""

    pass


class PumpCommandError(Exception):
    def __init__(self, message: str, command: str, *args) -> None:
        self.message = message
        self.command = command
        super().__init__(*args)

    def __str__(self) -> str:
        return f"Got {self.message!r} while executing {self.command!r}"


class Pump(BaseModel):
    """High-level interface for the Legato 100 syringe pump.
    Upon initialisation, sets poll mode to on, making prompts parsable.
    """

    serial: aioserial.AioSerial

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.serial.write(b"poll on\r\n")
        output = self.serial.read_until(XON)
        # TODO: verify the output

    async def start(self):
        await self._write("run")

    async def stop(self):
        await self._write("stop")

    async def set_brightness(self, brightness: int):
        if brightness < 0 or brightness > 100:
            raise PumpError("Brightness must be integer between 0 and 100")
        await self._write(f"dim {brightness}")

    async def version(self):
        output = await self._write("version")
        lines = output.split("\r\n")[:-1]  # skip the prompt line
        data = {}
        for line in lines:
            key, val = line.split(":", 1)
            data[key] = val
        return data

    async def _write(self, command: str):
        await self.serial.write_async((command + "\r\n").encode())
        return await self._parse_prompt(command=command)

    async def _parse_prompt(self, command: str = "") -> str:
        # relies on poll mode being on
        raw_output = await self.serial.read_until_async(XON)
        output = raw_output.rstrip(XON).strip().decode()
        # TODO: fully handle device number
        output = output.lstrip(_NUMBERS)

        if output.startswith("Command error"):
            message = output.split("\r")[1].strip()
            raise PumpCommandError(message, command)

        prompt = output.split("\r\n")[-1].lstrip(_NUMBERS)
        if prompt not in [":", ">", "<"]:
            raise PumpError(f"Unexpected prompt {output}")
        return output
