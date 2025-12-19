<img src="https://raw.githubusercontent.com/ajmirsky/fluidpy/refs/heads/main/docs/imgs/fluidpy.svg" width="450" />

## Introduction

The motion controller project [FluidNC](https://github.com/bdring/FluidNC) allows for the expansion of functionality
using its [channels protocol](http://wiki.fluidnc.com/en/config/uart_sections#uart-channels). In addition to receiving GRBL
[g-codes](http://wiki.fluidnc.com/en/features/grbl_compatibility) and [extension commands](http://wiki.fluidnc.com/en/features/commands_and_settings)
over a UART channel, FluidNC will provide a [stream of data]() that follows the [GRBL Line Protocol](https://github.com/gnea/grbl/wiki/Grbl-v1.1-Interface) 
and [FluidNC's serial protocol](http://wiki.fluidnc.com/en/support/serial_protocol). This data can be used to update a display,
control other devices, etc. Over a UART channel, FluidNC will also send [initialization information](http://wiki.fluidnc.com/en/config/uart_sections#channel-io)
that describes how the channel listener (aka expander) should configure itself so that it can receive specific control commands.

FluidPy is a python library that provides an interface for interacting with FluidNC's serial protocol.

## Platforms

FluidPy is currently supported on Python 3.10+, [MicroPython](https://micropython.org/) and [CircuitPython](https://circuitpython.org/)
which enables interfacing with the FluidNC controller on multiple platforms including microcontrollers, single board computers 
(with a [GPIO header such as a RaspberryPi](https://pinout.xyz/)) or even full desktop computers (with a [serial to USB adapter](https://www.google.com/search?q=usb+to+serial+adapter&oq=usb+to+serial)).

> Wiring diagrams are below for a few example platforms. When defining the uart section in your FluidNC config,
> note the Tx pin of the controller connects to the Rx pin of the expander microcontroller; and the controller's Rx pin to the expander's Tx pin.

## Getting Started...

Additional details can be found in the [API reference](api.md).

### ...with Microcontrollers

CircuitPython can be run on a [wide range of microcontrollers](https://circuitpython.org/downloads).

1. Install CircuitPython per the instructions on the [CircuitPython website](https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython/).
2. Clone this repository and copy the contents of `src/fluidpy` to the `lib/fluidpy` directory of your CircuitPython device.
3. Copy `examples/cpy_example/main.py` to `main.py` on your device (delete `code.py` if it exists).

### ...with single board and desktop computers

1. Create a new python virtual environment: `python -m venv .venv; source .venv/bin/activate`
2. Install the fluidpy library: `pip install fluidpy`
3. Copy `examples/py_example.py` to your project directory as `main.py`.

## Connections

> Note: Microcontrollers can be powered by the +5V from the UART header or the RJ12 connector, but _should not_ be connected
> while communicating with the microcontroller via USB.

<figure>
    <a href="https://raw.githubusercontent.com/ajmirsky/fluidpy/refs/heads/main/docs/imgs/board_example_1.png" target="_blank" rel="noopener noreferrer">
        <img src="https://raw.githubusercontent.com/ajmirsky/fluidpy/refs/heads/main/docs/imgs/board_example_1.png" width="600" />
    </a>
    <figcaption>PiBot v4 board with a Seeeduino Xaio RP2040 microcontroller.</figcaption>
</figure>

<figure>
    <a href="https://raw.githubusercontent.com/ajmirsky/fluidpy/refs/heads/main/docs/imgs/board_example_2.png" target="_blank" rel="noopener noreferrer">
        <img src="https://raw.githubusercontent.com/ajmirsky/fluidpy/refs/heads/main/docs/imgs/board_example_2.png" width="600" />
    </a>
    <figcaption>Corgi board with a Raspberry Pi Pico microcontroller.</figcaption>
</figure>

<figure>
    <a href="https://raw.githubusercontent.com/ajmirsky/fluidpy/refs/heads/main/docs/imgs/board_example_3.png" target="_blank" rel="noopener noreferrer">
        <img src="https://raw.githubusercontent.com/ajmirsky/fluidpy/refs/heads/main/docs/imgs/board_example_3.png" width="600" />
    </a>
    <figcaption>Raspberry Pi connections.</figcaption>
</figure>

<figure>
    <a href="https://raw.githubusercontent.com/ajmirsky/fluidpy/refs/heads/main/docs/imgs/board_example_4.png" target="_blank" rel="noopener noreferrer">
        <img src="https://raw.githubusercontent.com/ajmirsky/fluidpy/refs/heads/main/docs/imgs/board_example_4.png" width="600" />
    </a>
    <figcaption>Adafruit's <a href="https://www.adafruit.com/product/5335)>USB-to-Serial Adapter</a>.</figcaption>
</figure>
