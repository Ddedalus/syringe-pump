import asyncio
import time

import aioserial
from pydantic import BaseModel


class Pump(BaseModel):
    serial: aioserial.AioSerial

    class Config:
        arbitrary_types_allowed = True

    async def start(self):
        await self.serial.write_async(b"run\r\n")

    async def stop(self):
        await self.serial.write_async(b"stop\r\n")

    async def read_line(self):
        output = (await self.serial.readline_async()).decode(errors="ignore")
        print(len(output), output.strip(), flush=True)


async def main(pump: Pump):
    start = time.time()
    await pump.start()
    print(time.time() - start, "start")
    await asyncio.sleep(1)
    print(time.time() - start, "sleep")
    await pump.read_line()
    print(time.time() - start, "line 1")
    await pump.read_line()
    print(time.time() - start, "line 2")
    try:
        await pump.read_line()
    except Exception as e:
        print(e)
    print(time.time() - start, "line 3")
    await pump.stop()
    print(time.time() - start, "stop")


if __name__ == "__main__":
    serial = aioserial.AioSerial(
        port="COM4",
        baudrate=9600,
        cancel_read_timeout=0.5,
        cancel_write_timeout=0.5,
        timeout=3,
    )
    pump = Pump(serial=serial)
    asyncio.run(main(pump))
