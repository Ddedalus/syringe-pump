<center>

_Python controller for Legato family of syringe pumps_


<img src="https://raw.githubusercontent.com/Ddedalus/syringe-pump/main/assets/logo/syringe_icon.png" width="100" height="100" alt="Syringe logo by Freepik @ Flaticon.com" />

| ![Tests](https://github.com/Ddedalus/syringe-pump/actions/workflows/test.yml/badge.svg) | [![Test Coverage](https://coveralls.io/repos/github/Ddedalus/syringe-pump/badge.svg?branch=main)](https://coveralls.io/github/Ddedalus/syringe-pump?branch=main) | [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) |
|:-:|:-:|:-:|
| [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) | [![Latest version](https://badge.fury.io/py/python-syringe-pump.svg)](https://pypi.org/project/python-syringe-pump/) | [![GitHub issues](https://img.shields.io/github/issues/ddedalus/syringe-pump)]()

</center>

Control a syringe pumpt (e.g. Legato 100 / 101) using a computer.
This package uses a COM port to communicate with the pump via an USB cable.
It enables you to write python programs that control the pump, e.g. turn it on and off, set the flow rate, etc.

# Installation

```bash
pip install python-syringe-pump
```
or
```bash
poetry add python-syringe-pump
```

# Usage

## Working example

Copy-paste this to get going!

```python
import asyncio
import aioserial
from syringe_pump import Pump, Quantity

async def main():
    serial = aioserial.AioSerial(port="COM4", baudrate=115200, timeout=2)
    async with Pump(serial=serial) as pump:
        await pump.infusion_rate.set(Quantity("1 ml/min"))
        await pump.run()
        await asyncio.sleep(10)
    # pump will stop when exiting the context manager

asyncio.run(main())
```

Curious about the pieces of code above? Read on!

### Serial port connection
The `syringe_pump` uses [aioserial](https://pypi.org/project/aioserial/)
to communicate with the pump via the COM port.
To use the controller, create a serial connection and pass it into the Pump class.

```python
import aioserial
serial = aioserial.AioSerial(port="COM4", baudrate=115200, timeout=2)
```

### Async communication
This package uses [asyncio](https://realpython.com/async-io-python/#the-10000-foot-view-of-async-io) to communicate with the pump.
As a result, you need to add a few `await` statements to your code, which may seem like a pain.
However, the benefits will be worth it, especially when working with multiple pumps or sending experiment results via a network.

``` python
from syringe_pump import Pump, Quantity

pump = await Pump.from_serial(serial=serial)
await pump.infusion_rate.set(Quantity("1 ml/min"))
await pump.run()
```

**Note**: The `from_serial` class method will configure the pump to
use the correct communication protocol and disable NVRAM, following manufacturer's recommendations.

### Async context manager

In python, it's common to use [context managers](https://www.pythontutorial.net/advanced-python/python-context-managers/)
to handle external resources such as files, network connections, etc.

Instead of the above examle, you can use the `Pump` as such context manager, which will
automatically stop the pump in case of an error or at the end of the program.

```python
from syringe_pump import Pump, Quantity

async with Pump(serial=serial) as pump:
    await pump.infusion_rate.set(Quantity("1 ml/min"))
    await pump.run()
```

### Running async code
To run the async code in a normal python file,
you need to use the `asyncio.run` function or similar:

```python
import asyncio
# in regular python file:

async def main():
    asyncio.sleep(1)

asyncio.run(main())
```

**Note**: To benefit from non-blocking asyncio code, use `asyncio.sleep` instead of `time.sleep`.

**Note**: in a jupyter notebook, you can use `await` directly in the cell:

```python
# in jupyter notebook only:
await main()
```

## API

### Units
The pump controller uses the [quantiphy](https://pypi.org/project/quantiphy/) package to handle flow rates, volumes etc.

Example usage:
```python
from syringe_pump import Quantity
Quantity("1 ml/min")
Quantity("13.54 ml")
```

### Pump class
The controller implements most of the functionality specified in
[Legato user Commands](https://datasci.app.box.com/s/fkzmervnhyciy91hnn446eio7yazb7k2).

The methods and their parameters are easy to discover using autocomplete in your IDE.

Here's a quick overview of the popular methods:
 * `run` & `stop`: control the pump operation
 * `set_brightness`: control the onboard display. Set to 0 to turn off.
 * `set_force` & `get_force`: control the force applied to the syringe

Next, the pump controller has some properties that allow you to manage other parameters:

### Pump.infusion_rate and Pump.withdrawal_rate
The pump flow rates can be controlled here, including ramping.
Common methods available are:
 * `set` and `get`
 * `set_ramp(start, end, duration)`

Example:
```python
rate = await pump.infusion_rate.get_rate()
await pump.infusion_rate.set_rate(2 * rate)
await pump.infusion_rate.set_ramp(2 * rate, 0, 10)
```

### Pump.syringe
The syringe parameters can be controlled here.
The pump uses them to convert between flow rates and volumes.

Important methods:
 * `get_diameter` and `set_diameter`
 * `get_volume` and `set_volume`
 * `set_manufacturer` - to use pre-defined settings for common syringes

Example:
```python
from syringe_pump import Manufacturer
await pump.syringe.set_manufacturer(Manufacturer.HOSHI, Quantity("1 ml"))
```

# Examples
See the [examples](https://github.com/Ddedalus/syringe-pump/tree/main/examples) folder for more examples.

### Pump.infusion_volume and Pump.withdrawal_volume
Allows you to inspect and reset the volume dispensed by the pump.
The pump keeps track of the volume since last reset by itself.

Methods:
 * `get`
 * `clear`

### Pump.target_volume
Allows you to set a volume after which the pump will stop by itself.
This is useful to prevent the pump from over-dispensing and damaging the syringe.

Methods:
 * `set`
 * `clear`
 * `get` - returns the target volume or `None` if not set

Note that there is only one target volume across infusion and withdrawal.
Negative values are not allowed.

### Pump.target_time
Allows you to set a time after which the pump will stop by itself.
The time is represented as a `datetime.timedelta` object.

Methods:
 * `set`
 * `clear`
 * `get` - returns the target time or `None` if not set

Example:
```python
from datetime import timedelta
await pump.target_time.set(timedelta(hours=2, minutes=10))
```

**Note**: it seems the pumpt can only handle target time or target volume, but not both.

# Development

Have a look at [CONTRIBUTING.md](https://github.com/Ddedalus/syringe-pump/blob/main/CONTRIBUTING.md) for more information on the scope of the project and how to contribute.

# Credits

Project logo: [Freepik @ Flaticon.com](https://www.flaticon.com/free-icons/syringe)
