import asyncio
import time

import aioserial

from syringe_pump import Pump


async def main(pump: Pump):
    start = time.time()
    print(await pump.get_rate_limits())
    print(await pump.start())
    print(time.time() - start, "start")
    for i in range(10):
        rate = 1 + (i % 2)
        print(await pump.set_infusion_rate(rate))
        print("Rate:", rate)
        await asyncio.sleep(1)
    await pump.stop()
    print(time.time() - start, "stop")


if __name__ == "__main__":
    serial = aioserial.AioSerial(port="COM4", baudrate=115200, timeout=2)
    pump = Pump(serial=serial)
    asyncio.run(main(pump))
