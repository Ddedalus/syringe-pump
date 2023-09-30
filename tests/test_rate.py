import pytest

from syringe_pump import Pump, Quantity, Rate
from syringe_pump.rate import RateRampInfo
from tests.conftest import Random


@pytest.fixture(scope="session", params=["infusion_rate", "withdrawal_rate"])
def rate(request, pump: Pump):
    return getattr(pump, request.param)


async def test_rate_error(rate: Rate):
    with pytest.raises(ValueError):
        await rate.set(Quantity(0, "l/min"))

    with pytest.raises(ValueError):
        await rate.set(Quantity(1.0, "nonsense"))


async def test_rate_set_get(rate: Rate, rng: Random):
    new_rate = rng.uniform(1e-4, 2e-3)
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


@pytest.fixture
def random_ramp(rng: Random):
    start = round(rng.uniform(0.1, 0.3), 3)
    end = round(rng.uniform(0.4, 0.6), 3)
    return RateRampInfo(
        start=Quantity(f"{start} ml/min"),
        end=Quantity(f"{end} ml/min"),
        duration=round(rng.uniform(5, 10), 3),
    )


async def test_rate_ramp(rate: Rate, random_ramp: RateRampInfo):
    with pytest.raises(ValueError):
        await rate.set_ramp(random_ramp.start, random_ramp.end, -1)

    await rate.set_ramp(**random_ramp.model_dump())
    ramp = await rate.get_ramp()

    assert ramp
    assert float(ramp.start) == pytest.approx(random_ramp.start.real)
    assert float(ramp.end) == pytest.approx(random_ramp.end.real)
    assert float(ramp.duration) == pytest.approx(random_ramp.duration)

    await rate.reset_ramp()
    ramp = await rate.get_ramp()
    assert ramp is None
