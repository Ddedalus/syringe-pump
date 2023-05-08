_External controller for Legato 100 syringe pump_

# Installation

## This package
```
poetry install
```


# Usage

Basic usage as an async context manager:

```python
import asyncio
import aioserial
from syringe_pump import Pump
from quantity import Quantity

async def main():
    serial = aioserial.AioSerial(port="COM4", baudrate=115200, timeout=2)
    async with Pump(serial=serial) as pump:
        await pump.set_rate(Quantity("1 ml/min"))
        await pump.start()
        await asyncio.sleep(10)
    # pump will stop when exiting the context manager

asyncio.run(main())
```

See [aioserial_example.py](./examples/aioserial_example.py) for a full demo.