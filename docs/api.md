# FluidNC API reference

A subclass should be created from the parent `fluidpy.FluidNC` and can implement one or more of the `handle_*` methods
to receive callbacks when certain messages are received.

## FluidNC Usage Example

Each platform will have a different mechanism for communicating with the controller, and will
each require a different [`BufferInterface`](#fluidpy.BufferInterface) implementation, defining `read`, `write` and `readline` methods. See
`examples` directory for CircuitPython and Python implementations.

Subclass `fluidpy.FluidNC` and implement `handle_version` method which is called when the controller has started.
 
Once the I/O interface is defined, instantiate subclass of `fluidpy.FluidNC` and call the `listen` method.


```python
from fluidpy import FluidNC

class MyFluidExpander(FluidNC):
    """
    Implement one or more 'handle_*' methods to receive incoming messages
    """

    def __init__(self, io: BufferInterface) -> None:
        super().__init__(io)

    def handle_version(self, message: str) -> None:
        print(f"Version: {message}")

io = MyBufferInterface()
fluid = MyFluidExpander(io)
fluid.listen()
```

## API


::: fluidpy.FluidNC
    rendering:
      show_root_heading: true
      show_source: true
    options:
      summary:
        functions: false

::: fluidpy.Position
    rendering:
      show_root_heading: true
      show_source: false
    options:
      extra:
        class_style: "simple"

::: fluidpy.Mode
    rendering:
      show_root_heading: true
      show_source: false
    options:
      extra:
        class_style: "simple"

::: fluidpy.BufferInterface
    rendering:
      show_root_heading: true
      show_source: false
    options:
      summary:
        functions: false

