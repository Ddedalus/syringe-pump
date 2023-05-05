import asyncio
import time

import aioserial

from syringe_pump import Pump, PumpCommandError, PumpError


async def main(pump: Pump):
    print(await pump.version())

    try:
        await pump._write("invalid")
    except PumpCommandError:
        pass
    else:
        raise ValueError("Should raise!")
    try:
        await pump._write("istop")
    except PumpError as e:
        print(e)
    else:
        raise ValueError("Should've raised!")


if __name__ == "__main__":
    serial = aioserial.AioSerial(port="COM4", baudrate=115200, timeout=2)
    pump = Pump(serial=serial)
    asyncio.run(main(pump))
