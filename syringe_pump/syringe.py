from enum import Enum
from typing import TYPE_CHECKING, Optional

from quantiphy import Quantity

from syringe_pump.exceptions import *
from syringe_pump.response_parser import extract_quantity

if TYPE_CHECKING:
    from .pump import Pump


class Manufacturer(Enum):
    AIR_TITE_HSW_NORM_JECT = "air"
    BECTON_DICKINSON_GLASS = "bdg"
    BECTON_DICKINSON_PLASTI_PAK = "bdp"
    CADENCE_SCIENCE_MICRO_MATE_GLASS = "cad"
    COLE_PARMER_STAINLESS_STEEL = "cps"
    HAMILTON_GLASS_700 = "hm1"
    HAMILTON_GLASS_1000 = "hm2"
    HAMILTON_GLASS_1700 = "hm3"
    HAMILTON_GLASS_7000 = "hm4"
    HOSHI = "hos"
    KDS_GLASS = "kgl"
    NATSUME = "nat"
    NIPRO = "nip"
    SGE_SCIENTIFIC_GLASS_ENGINEERING = "sge"
    SHERWOOD_MONOJECT_PLASTIC = "smp"
    STAINLESS_STEEL = "sst"
    TERUMO = "ter"
    TOP = "top"


class Syringe:
    """Expose methods to manage syringe settings."""

    Manufacturer = Manufacturer

    def __init__(self, pump: "Pump") -> None:
        self._pump = pump

    async def get_diameter(self) -> Quantity:
        """Get syringe diameter configured in the pump."""
        output = await self._pump._write("diameter")
        diameter, _ = extract_quantity(output.message[0])
        return diameter

    async def set_diameter(self, diameter: float):
        """Set syringe diameter in mm."""
        return await self._pump._write(f"diameter {diameter:.4}")

    async def get_volume(self) -> Quantity:
        """Get syringe volume configured in the pump."""
        output = await self._pump._write("svolume")
        volume, _ = extract_quantity(output.message[0])
        return volume

    async def set_volume(self, volume: Quantity):
        """Set syringe volume."""
        _check_volume(volume)
        await self._pump._write(f"svolume {volume:.4}")

    async def set_manufacturer(
        self, manufacturer: Manufacturer, volume: Optional[Quantity] = None
    ):
        """Set syringe manufacturer and volume."""
        try:
            if volume is not None:
                _check_volume(volume)
                response = await self._pump._write(
                    f"syrmanu {manufacturer.name} {volume:.4} "
                )
            else:
                response = await self._pump._write(f"syrmanu {manufacturer.name}")
        except PumpCommandError as e:
            if "Unknown syringe" in e.response.message[1]:
                options = await self._pump._write(f"syrmanu {manufacturer.name} ?")
                raise ValueError(
                    f"Unknown syringe. Valid volumes are: \n{options.raw_text}"
                ) from e
            raise
        return response

    async def get_manufacturer(self):
        """Get syringe manufacturer configured in the pump."""
        output = await self._pump._write("syrmanu")
        print(output.message)
        manu, volume, diam = output.message[0].split(",")
        return manu, Quantity(volume), Quantity(diam)


def _check_volume(volume: Quantity):
    if volume.units != "l":
        raise ValueError("Volume must be in ml, ul or nl")
    if volume.real <= 0:
        raise ValueError("Volume must be positive")
