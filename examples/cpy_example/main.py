import board
import busio
import digitalio
import asyncio

try:
    import logging
except ImportError:
    import adafruit_logging as logging

from fluidpy import FluidNC, BufferInterface

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
    Implement one or more 'handle_*' methods to receive incoming messages
    """

    def __init__(self, io: BufferInterface) -> None:
        # enable the debug log for the default implementation of fluidnc's handlers (optional)
        # fluidpy_logger = logging.getLogger("fluidpy.fluidnc")
        # fluidpy_logger.setLevel(logging.DEBUG)

        super().__init__(io)

    def handle_version(self, message: str) -> None:
        print(f"Version: {message}")


def main():
    print("\nWaiting for data...")
    uart_io = UARTInterface()
    my_expander = MyFluidExpander(uart_io)

    # start the loop to listen for incoming message
    my_expander.listen()


async def other_task():
    while True:
        print("Doing other stuff...")
        await asyncio.sleep(1)

async def amain():
    uart_io = UARTInterface()
    my_expander = MyFluidExpander(uart_io)

    tasks = list()
    # start an async task to listen for incoming messages
    tasks.append(asyncio.create_task(my_expander.alisten()))

    # start some other async task
    tasks.append(asyncio.create_task(other_task()))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # asyncio.run(amain())
    main()