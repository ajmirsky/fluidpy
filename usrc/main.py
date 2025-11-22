import board
import busio
import digitalio

from fluidnc import FluidNC

# For most CircuitPython boards:
led = digitalio.DigitalInOut(board.LED_BLUE)
# For QT Py M0:
# led = digitalio.DigitalInOut(board.SCK)
led.direction = digitalio.Direction.OUTPUT

# uart = busio.UART(board.D6, board.D7, baudrate=115200)

# reporting = "$Report/Interval=75"
#
# uart.write(reporting.encode())

print("\nWaiting for data...")

fluidnc = FluidNC()

fluidnc.listen()

#
# while True:
#
#     data = fluidnc.read_message()
#
#     if data is not None:
#         led.value = not led.value
#         print(data)
