import pytest

from syringe_pump.exceptions import (
    LimitSwitchError,
    PumpError,
    PumpStalledError,
    PumpStateError,
    TargetReachedError,
)
from syringe_pump.response_parser import PumpResponse


def test_response_no_output():
    with pytest.raises(PumpError):
        PumpResponse.from_output(b"", "foo")


def test_response_custom_address():
    response = PumpResponse.from_output(b"Pump address set to 2\r\n02:", "foo")
    assert response.address == 2
    assert response.prompt == ":"
    assert response.message == ["Pump address set to 2"]


def test_response_zero_address():
    response = PumpResponse.from_output(b"foo\r\n:", "foo")
    assert response.address == 0
    assert response.prompt == ":"
    assert response.message == ["foo"]


def test_response_quantity():
    response = PumpResponse.from_output(b"foo 1.23 mL\r\n:", "foo")
    assert response.address == 0
    assert response.prompt == ":"
    assert response.message == ["foo 1.23 mL"]


@pytest.mark.parametrize(
    "response,exception,message",
    [
        (PumpResponse.from_output(b"foo\r\nT*", "foo"), TargetReachedError, "target"),
        (PumpResponse.from_output(b"foo\r\n*", "foo"), PumpStalledError, "stalled"),
        (
            PumpResponse.from_output(b"foo\r\n>*", "foo"),
            LimitSwitchError,
            "infuse limit",
        ),
        (
            PumpResponse.from_output(b"foo\r\n<*", "foo"),
            LimitSwitchError,
            "withdraw limit",
        ),
        (PumpResponse.from_output(b"foo\r\nbar", "foo"), PumpStateError, "bar"),
    ],
)
def test_state_exceptions(response, exception, message: str):
    exc = PumpStateError.from_response(response)

    assert isinstance(exc, exception)
    assert "foo" in str(exc)
    assert message.lower() in str(exc).lower()
