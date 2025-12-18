import board
import busio
import digitalio

try:
    import logging
except ImportError:
    import adafruit_logging as logging

from fluidpy.fluidnc import FluidNC, BufferInterface, FluidParseError

logger = logging.getLogger(__name__)


class UARTInterface(BufferInterface):
    """
    Simple wrapper around the CircuitPython UART class to implement
    an interface for a FluidNC channel communication
    """

    def __init__(self):
        self.uart = busio.UART(board.D6, board.D7, baudrate=115200)

    def read(self, n: int) -> bytes:
        return self.uart.read(n)

    def write(self, buffer: bytes) -> int:
        return self.uart.write(buffer)

    def readline(self) -> bytes:
        return self.uart.readline()


class MyFluidExpander(FluidNC):
    """
    Implement 'handle_*' methods to receive incoming messages
    """

    def __init__(self, io: BufferInterface) -> None:
        super().__init__(io)


if __name__ == "__main__":
    print("\nWaiting for data...")
    uart_io = UARTInterface()
    my_expander = MyFluidExpander(uart_io)

    # start a loop to listen for incoming messages

    my_expander.listen()

