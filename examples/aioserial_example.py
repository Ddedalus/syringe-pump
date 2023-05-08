import asyncio
import time

import aioserial
from quantiphy import Quantity

from syringe_pump import Pump


async def main(pump: Pump):
    async with pump:
        start = time.time()
        print(await pump.infusion_rate.get_limits())
        print(time.time() - start, "start")
        for i in range(4):
            rate = Quantity(f"{1 + (i % 2)} ml/min")
            print(await pump.infusion_rate.set(rate))
            await pump.run()
            print("Rate:", rate)
            await asyncio.sleep(1)
        print(time.time() - start, "stop")


if __name__ == "__main__":
    serial = aioserial.AioSerial(port="COM4", baudrate=115200, timeout=2)
    pump = Pump(serial=serial)
    asyncio.run(main(pump))
