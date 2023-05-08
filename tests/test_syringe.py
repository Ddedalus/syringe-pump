import pytest
from quantiphy import Quantity

from syringe_pump import Pump, Syringe
from tests.conftest import Random


@pytest.fixture(scope="session")
def syringe(pump: Pump):
    return pump.syringe


async def test_syringe_volume(syringe: Syringe, rng: Random):
    new_volume = rng.uniform(8, 20)
    await syringe.set_volume(Quantity(f"{new_volume} ml"))
    read_volume = await syringe.get_volume()
    assert round(read_volume, 3) == round(new_volume / 1000, 3)


async def test_syringe_diameter(syringe: Syringe, rng: Random):
    new_diameter = round(rng.uniform(7, 12), 3)
    await syringe.set_diameter(new_diameter)
    read_diameter = await syringe.get_diameter()
    assert round(read_diameter, 3) == round(new_diameter / 1000, 3)


@pytest.mark.skip("Don't annoy the pump. No easy way to go back to cusotm O.o")
async def test_syringe_manufacturer(syringe: Syringe):
    with pytest.raises(ValueError):
        await syringe.set_manufacturer(
            Syringe.Manufacturer.STAINLESS_STEEL, Quantity("1 ml")
        )

    response = await syringe.set_manufacturer(
        Syringe.Manufacturer.STAINLESS_STEEL, Quantity("20 ml")
    )
    assert not response.message  # pump gives no inofrmation on success

    (manu, volume, diam) = await syringe.get_manufacturer()

    # This is neither code nor full name; highly inconsistent
    assert manu == "Stainless"
    assert diam == 0.01913  # This appears to be computed / known by the pump
    assert volume == 0.02


def test_random(rng: Random):
    n = rng.uniform(0, 1)
    assert n == pytest.approx(0.052363598850944326)


@pytest.mark.parametrize("param", [1, 2, 3])
def test_random_2(rng: Random, param):
    n = rng.uniform(0, 1)
    assert n == pytest.approx(0.052363598850944326)
