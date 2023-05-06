import asyncio
import random

import pytest
from quantiphy import Quantity

from syringe_pump import Pump, Syringe
from syringe_pump.exceptions import PumpError


@pytest.fixture(scope="session")
def syringe(pump: Pump):
    return pump.syringe


async def test_syringe_volume(syringe: Syringe):
    new_volume = random.uniform(0.1, 2)
    await syringe.set_volume(Quantity(f"{new_volume} ml"))
    read_volume = await syringe.get_volume()
    assert round(read_volume, 3) == round(new_volume / 1000, 3)


async def test_syringe_diameter(syringe: Syringe):
    new_diameter = random.uniform(1, 10)
    await syringe.set_diameter(new_diameter)
    read_diameter = await syringe.get_diameter()
    assert round(read_diameter, 3) == round(new_diameter / 1000, 3)
