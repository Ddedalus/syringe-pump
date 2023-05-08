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
    new_rate = random.uniform(1e-4, 2e-3)
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


async def test_rate_ramp(rate: Rate):
    start = round(random.uniform(0.1, 0.3), 3)
    end = round(random.uniform(0.4, 0.6), 3)
    duration = round(random.uniform(5, 10), 3)
    await rate.set_ramp(
        Quantity(f"{start} ml/min"), Quantity(f"{end} ml/min"), duration
    )
    ramp = await rate.get_ramp()

    assert ramp
    assert float(ramp.start) == pytest.approx(0.001 * start)
    assert float(ramp.end) == pytest.approx(0.001 * end)
    assert float(ramp.duration) == pytest.approx(duration)

    await rate.reset_ramp()
    ramp = await rate.get_ramp()
    assert ramp is None
