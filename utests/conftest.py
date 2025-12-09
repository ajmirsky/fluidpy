from unittest.mock import Mock, MagicMock

import pytest

from fluidpy.fluidnc import BufferInterface, FluidNC, Position, Mode
from fluidpy.udecimal import DecimalNumber as Decimal


class TestFluidExpander(FluidNC):

    def __init__(self, io: BufferInterface) -> None:
        super().__init__(io)

        # find all the handlers...
        handlers = [
            method for method in dir(self)
            if method.startswith("handle_") and callable(getattr(self, method))
        ]

        # ... and replace them with mocks
        for handler in handlers:
            setattr(self, handler, MagicMock())


@pytest.fixture
def fnc() -> FluidNC:
    class TestInterface(BufferInterface):
        pass

    fluidnc = TestFluidExpander(TestInterface())

    yield fluidnc
