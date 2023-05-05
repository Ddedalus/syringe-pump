import asyncio
import time

import aioserial

from syringe_pump import Pump


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
