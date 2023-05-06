import random

import pytest

from syringe_pump import Pump, Quantity, Rate


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
