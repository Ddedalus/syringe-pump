from datetime import timedelta

import pytest

from syringe_pump import Pump, Quantity


@pytest.mark.parametrize(
    "set,get",
    [
        (30, timedelta(seconds=30)),
        (timedelta(minutes=2, seconds=60), timedelta(minutes=3)),
        (timedelta(hours=1, minutes=30), timedelta(hours=1, minutes=30)),
        (timedelta(hours=99, minutes=1), timedelta(hours=99, minutes=1)),
        (None, None),
    ],
)
async def test_get_set_target_time(set, get: timedelta, pump: Pump):
    await pump.target_time.set(set)
    assert await pump.target_time.get() == get


async def test_clear_target_time(pump: Pump):
    await pump.target_time.clear()
    assert await pump.target_time.get() is None


@pytest.mark.parametrize("value", [timedelta(hours=100), timedelta(seconds=-1)])
async def test_target_time_error(value, pump: Pump):
    with pytest.raises(ValueError):
        await pump.target_time.set(value)
