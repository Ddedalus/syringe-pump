import asyncio
import random

import pytest
from quantiphy import Quantity

from syringe_pump import Pump
from syringe_pump.exceptions import PumpError
from syringe_pump.rate import Rate


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


@pytest.fixture(scope="session", params=["infusion_rate", "withdrawal_rate"])
def rate(request, pump: Pump):
    return getattr(pump, request.param)


async def test_rate_error(rate: Rate):
    with pytest.raises(ValueError):
        await rate.set(Quantity(0, "l/min"))

    with pytest.raises(ValueError):
        await rate.set(Quantity(1.0, "nonsense"))


async def test_rate_set_get(rate: Rate):
    new_rate = random.uniform(1e-3, 2e-2)
    await rate.set(Quantity(f"{new_rate} l/min"))
    read_rate = await rate.get()
    assert round(read_rate, 3) == round(new_rate, 3)


async def test_rate_set_get_int(rate: Rate):
    # special case where pump returns 1 instead of 1.0
    await rate.set(Quantity("1.0 ml/min"))
    read_rate = await rate.get()
    assert read_rate == 0.001


async def test_rate_limits(rate: Rate):
    low, high = await rate.get_limits()
    assert low < high
    assert 0 < low < 1e-6
    assert 1e-3 < high
