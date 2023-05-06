import asyncio
import random

import pytest

from syringe_pump import Pump
from syringe_pump.exceptions import PumpError


async def test_pump_version(pump: Pump):
    output = await pump.version()
    assert "Firmware" in output
    assert "Pump address" in output
    assert "Serial number" in output


@pytest.mark.skip(reason="Don't annoy the pump")
async def test_start_stop(pump: Pump):
    await pump.start()
    await asyncio.sleep(0.1)
    await pump.stop()


async def test_set_brightness(pump: Pump):
    with pytest.raises(PumpError):
        await pump.set_brightness(-1)
    with pytest.raises(PumpError):
        await pump.set_brightness(150)
    await pump.set_brightness(15)


async def test_infusion_rate(pump: Pump):
    irate = pump.infusion_rate

    with pytest.raises(PumpError):
        await irate.set(0)

    with pytest.raises(PumpError):
        await irate.set(1.0, "nonsense")

    rate = random.uniform(0.1, 2.0)
    await irate.set(rate, "ml/min")
    set_rate = await irate.get()
    assert int(set_rate * 1000) == int(rate * 1000)  # round to 3 decimal places

    await irate.set(1.0, "ml/min")
    set_rate = await irate.get()
    assert set_rate == 1.0  # special case where pump returns 1 instead of 1.0
