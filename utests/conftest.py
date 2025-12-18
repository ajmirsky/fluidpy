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

        # ... and replace them with a Mock
        self.mocks = dict()
        for handler in handlers:
            self.mocks[handler] = MagicMock()
            setattr(self, handler, self.mocks[handler])


@pytest.fixture
def fnc() -> FluidNC:
    class TestInterface(BufferInterface):
        def write(self, buffer: bytes) -> int:
            return len(buffer)


    fluidnc = TestFluidExpander(TestInterface())

    yield fluidnc
