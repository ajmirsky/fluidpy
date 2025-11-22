
from fluidpy.fluidnc import BufferInterface, FluidNC


class MockInterface(BufferInterface):

    def read(self, n: int) -> bytes:
        return b"1234567890"

    def readline(self) -> bytes:
        return b"1234567890\n"

    def write(self, buffer: bytes) -> int:
        return len(buffer)


def test_parse_version_message():

    test_fluidnc = FluidNC(MockInterface())