import re

from .exceptions import *
from .serial_interface import SerialInterface


class Volume(SerialInterface):
    """Expose methods to manage syringe volume settings."""

    # TODO: is this needed?
