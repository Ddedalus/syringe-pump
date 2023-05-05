import asyncio
import time

import aioserial
from pydantic import BaseModel, PrivateAttr

XON = b"\x11"


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

    async def _write(self, command: str):
        return await self.serial.write_async((command + "\r\n").encode())

    async def start(self):
        await self._write("run")
        return await self.parse_prompt()

    async def stop(self):
        await self._write("stop")

    async def parse_prompt(self) -> str:
        output = await self.serial.read_until_async(XON)
        output.rstrip(XON).lstrip(b"\n")
        return output.decode()


async def main(pump: Pump):
    start = time.time()
    print(await pump.start())
    print(time.time() - start, "start")
    await asyncio.sleep(1)
    print(time.time() - start, "sleep")
    await pump.stop()
    print(time.time() - start, "stop")


if __name__ == "__main__":
    serial = aioserial.AioSerial(port="COM4", baudrate=115200, timeout=2)
    pump = Pump(serial=serial)
    asyncio.run(main(pump))
