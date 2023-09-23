import pytest

from syringe_pump import Pump, Quantity
from syringe_pump.volume import Volume
from tests.conftest import Random


@pytest.fixture(scope="session", params=["infusion_volume", "withdrawal_volume"])
def volume(request, pump: Pump):
    return getattr(pump, request.param)


async def test_clear_volume(volume: Volume):
    await volume.clear()
    vol = await volume.get()
    assert vol == 0


async def test_clear_target_volume(pump: Pump):
    await pump.target_volume.clear()
    vol = await pump.target_volume.get()
    assert vol is None


async def test_target_set_get(pump: Pump, rng: Random):
    new_target = rng.uniform(1e-4, 2e-3)
    await pump.target_volume.set(Quantity(f"{new_target} l"))
    target = await pump.target_volume.get()
    assert target is not None
    assert round(target, 3) == round(new_target, 3)


async def test_target_set_get_int(pump: Pump):
    await pump.target_volume.set(Quantity("1.0 ml"))
    target = await pump.target_volume.get()
    assert target == 0.001
