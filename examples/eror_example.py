import asyncio
import time
from typing import Coroutine, Type

import aioserial

from syringe_pump import Pump, PumpCommandError, PumpError


async def should_raise(coroutine: Coroutine, exception: Type[Exception]):
    try:
        print(await coroutine)
    except exception:
        return
    else:
        raise ValueError(f"Should raise {exception}")


async def main(pump: Pump):
    print(await pump.version())

    await should_raise(pump._write("invalid"), PumpCommandError)
    await should_raise(pump.set_infusion_rate(1, "nonsense"), PumpCommandError)


if __name__ == "__main__":
    serial = aioserial.AioSerial(port="COM4", baudrate=115200, timeout=2)
    pump = Pump(serial=serial)
    asyncio.run(main(pump))
