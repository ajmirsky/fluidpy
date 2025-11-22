import board
import busio
import re
from udecimal import DecimalNumber as Decimal

VALID_STATES = ('Idle', 'Run', 'Hold', 'Jog', 'Alarm', 'Door', 'Check', 'Home', 'Sleep')

class Position:

    __slots__ = ("x", "y", "z", "a", "b", "c")
    def __init__(self,
                 x: Decimal | str = Decimal(0),
                 y: Decimal | str = Decimal(0),
                 z: Decimal | str = Decimal(0),
                 a: Decimal | str = Decimal(0),
                 b: Decimal | str = Decimal(0),
                 c: Decimal | str = Decimal(0)):

        self.x: Decimal = x if isinstance(x, Decimal) else Decimal(str(x))
        self.y: Decimal = y if isinstance(y, Decimal) else Decimal(str(y))
        self.z: Decimal = z if isinstance(z, Decimal) else Decimal(str(z))
        self.a: Decimal = a if isinstance(a, Decimal) else Decimal(str(a))
        self.b: Decimal = b if isinstance(b, Decimal) else Decimal(str(b))
        self.c: Decimal = c if isinstance(c, Decimal) else Decimal(str(c))

    def __repr__(self) -> str:
        return f"Position(x={self.x}, y={self.y}, z={self.z}, a={self.a}, b={self.b}, c={self.c})"

class Mode:
    PLANES = ('XY', 'XZ', 'YZ')
    FEED_RATE_MODES = ('INVERSE', 'UNITS/MIN', 'UNITS/REV')
    COOLANT = ('MIST', 'FLOOD', 'OFF')


    def __init__(self,
                 is_rapid: bool = False, # rapid mode (G0), feed rate mode (G1),
                 wco_index: int = 0, # G54, G55, etc
                 plane: str = 'XY', # XY (G17), XZ (G18), YZ (G19),
                 is_inches: bool = False, # inches (G20), mm (G21),
                 is_absolute: bool = False, # absolute (G90), relative (G91),
                 feed_rate_mode: str = 'UNITS/MIN', # INVERSE (G93), UNITS/MIN (G94), UNITS/REV (G95)
                 coolant: str = 'FLOOD', # MIST (M7), FLOOD (M8), OFF (M9)
                 tool_number: int = 0,
                 feed_rate: Decimal = Decimal(0),
                 spindle_speed: Decimal = Decimal(0),
                 ):
        self.is_rapid = is_rapid
        self.wco_index = wco_index
        self.plane = plane
        self.is_inches = is_inches
        self.is_absolute = is_absolute
        self.feed_rate_mode = feed_rate_mode
        self.coolant = coolant
        self.tool_number = tool_number
        self.feed_rate = feed_rate
        self.spindle_speed = spindle_speed

    def __repr__(self) -> str:
        return f"Mode(is_rapid={self.is_rapid}, wco_index={self.wco_index}, plane={self.plane}, is_inches={self.is_inches}, is_absolute={self.is_absolute}, feed_rate_mode={self.feed_rate_mode}, coolant={self.coolant}, tool_number={self.tool_number}, feed_rate={self.feed_rate}, spindle_speed={self.spindle_speed})"

    @classmethod
    def from_string(cls, mode_string: str) -> 'Mode':
        params = dict()
        for mode in mode_string.split(" "):
            if mode in ("G0", "G1"):
                params['is_rapid'] = mode == "G0"
            elif mode.startswith("G5"):
                params['wco_index'] = int(mode[2:]) - 3
            elif mode in ("G17", "G18", "G19"):
                params['plane'] = cls.PLANES[int(mode[1:]) - 17]
            elif mode in ("G20", "G21"):
                params['is_inches'] = mode == "G20"
            elif mode in ("G90", "G91"):
                params['is_absolute'] = mode == "G90"
            elif mode in ("M7", "M8", "M9"):
                params['coolant'] = cls.COOLANT[int(mode[1:]) - 7]
            elif mode.startswith("T"):
                params['tool_number'] = int(mode[1:])
            elif mode.startswith("F"):
                params['feed_rate'] = Decimal(mode[1:])
            elif mode.startswith("S"):
                params['spindle_speed'] = Decimal(mode[1:])
            else:
                print(f"unknown mode: {mode}")

        return cls(**params)


class FluidNC:
    version_re = re.compile(r"FluidNC\sv([\d\.]+)")

    # eg. <Jog|MPos:59.304,0.000,0.000|FS:300,0|Pn:PT>
    status_re = re.compile(r"<(\w+)\|(.+?)>")

    # eg. [MSG:INFO: Z Axis driver test passed]
    log_re = re.compile(r"\[MSG:(\w+:)?\s*?(\w.+)\]")

    # eg. [INI: io.1=in,low,pu]
    ini_re = re.compile(r"\[INI:(.+?)\]")

    # eg. [GC:G0 G55 G17 G21 G90 G94 M5 M9 T0 F0 S0]
    mode_re = re.compile(r"\[GC:(.+?)\]")

    def __init__(self, rx_pin=board.D6, tx_pin=board.D7, baudrate: int=115200) -> None:
        self.uart = busio.UART(rx_pin, tx_pin, baudrate=baudrate)

    def send_message(self, message: str) -> None:
        self.uart.write(message.encode())

    def read_message(self) -> str | None:
        msg = self.uart.readline()
        if msg:
            return msg.decode().strip()
        return None

    def parse_message(self):
        pass

    def parse_status_report(self, message: str) -> dict:
        pass

    def parse_input(self, input: str) -> str | None:
        return None

    def parse_grbl_message(self, message: str) -> dict:
        return {}

    def parse_position(self, axes_message:str) -> Tuple(str, Any) | None:
        kind, axes = axes_message.split(":")
        if kind in ('MPos', 'WCO'):
            return kind, Position(*map(Decimal, axes.split(",")))
        return None

    def handle_status(self, status: dict):
        pass

    def handle_log(self, log: dict):
        pass

    def handle_ini(self, ini: dict):
        pass

    def listen(self):

        while True:
            data = self.read_message()
            if not data:
                continue

            if match := self.status_re.match(data):
                states, message = match.groups()
                for partial in message.split("|"):
                    kind, mantissa = partial.split(":")
                    if kind in ('MPos', 'WCO'):
                        print(f"{kind} >> {mantissa}")
                    elif kind in ('F', 'FS'):
                        print(f"FS >> {mantissa}")
                    elif kind == 'Pn':
                        print(f"Pn >> {mantissa}")
                    elif kind == 'Err':
                        print(f"Err >> {mantissa}")
                    elif kind == 'Ov':
                        print(f"Ov >> {mantissa}")
                    elif kind == 'Ln':
                        print(f"Ln >> {mantissa}")
                    else:
                        print(f"unknown >> {kind}:{mantissa}")
            elif match := self.log_re.match(data):
                print(f"log >> {match.groups()}")
            elif match := self.ini_re.match(data):
                print(f"ini >> {match.groups()}")
            elif match := self.mode_re.match(data):
                print(f"mode >> {Mode.from_string(match.group(1))}")
            else:
                print(f"unknown >> {data}")

