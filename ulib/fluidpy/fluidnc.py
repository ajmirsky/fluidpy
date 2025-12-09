import re
try:
    import logging
except ImportError:
    import adafruit_logging as logging

from fluidpy.udecimal import DecimalNumber as Decimal

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

VALID_STATES = ('Idle', 'Run', 'Hold', 'Jog', 'Alarm', 'Door', 'Check', 'Home', 'Sleep')

class BufferInterface:

    def read(self, n: int) -> bytes:
        raise NotImplementedError

    def write(self, buffer: bytes) -> int:
        raise NotImplementedError

    def readline(self) -> bytes:
        raise NotImplementedError

class FluidParseException(Exception):
    pass

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
    SPINDLE_STATES = ('CW', 'CCW', 'STOP')


    def __init__(self,
                 is_rapid: bool = False, # rapid mode (G0), feed rate mode (G1),
                 wco_index: int = 0, # G54, G55, etc
                 plane: str = 'XY', # XY (G17), XZ (G18), YZ (G19),
                 is_inches: bool = False, # inches (G20), mm (G21),
                 is_absolute: bool = False, # absolute (G90), relative (G91),
                 spindle_state: str = 'OFF',  # CW (M3), CCW (M4), STOP (M5)
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
            elif mode in ("M3", "M4", "M5"):
                params['spindle_state'] = cls.SPINDLE_STATES[int(mode[1:]) - 3]
            elif mode in ("M7", "M8", "M9"):
                params['coolant'] = cls.COOLANT[int(mode[1:]) - 7]
            elif mode in ("G93", "G94", "G95"):
                params['feed_rate_mode'] = cls.FEED_RATE_MODES[int(mode[1:]) - 93]
            elif mode.startswith("T"):
                params['tool_number'] = int(mode[1:])
            elif mode.startswith("F"):
                params['feed_rate'] = Decimal(mode[1:])
            elif mode.startswith("S"):
                params['spindle_speed'] = Decimal(mode[1:])
            else:
                raise FluidParseException(f"unknown mode: {mode}")

        return cls(**params)


class FluidNC:
    version_re = re.compile(r"Grbl 4\.0 \[FluidNC (([A-Za-z0-9]+(\.[A-Za-z0-9]+)+)-[A-Za-z0-9]+)")

    # eg. <Jog|MPos:59.304,0.000,0.000|FS:300,0|Pn:PT>
    status_re = re.compile(r"<(\w+)\|(.+?)>")

    # eg. [MSG:INFO: Z Axis driver test passed]
    log_re = re.compile(r"\[MSG:(\w+:)?\s*?(\w.+)\]")

    # eg. [INI: io.1=in,low,pu]
    ini_re = re.compile(r"\[INI:(.+?)\]")

    # [EXP:ID] or [EXP:io.2=out]
    exp_re = re.compile(r"\[EXP:(.+?)\]")

    # eg. [GC:G0 G55 G17 G21 G90 G94 M5 M9 T0 F0 S0]
    mode_re = re.compile(r"\[GC:(.+?)\]")

    def __init__(self, io: BufferInterface) -> None:
        self.io = io

    def send_message(self, message: str) -> None:
        self.io.write(message.encode())

    def send_bytes(self, command: bytes) -> None:
        self.io.write(command)

    def read_message(self) -> str | None:
        msg = self.io.readline()
        if msg:
            return msg.decode().strip()
        return None

    def is_state_valid(self, state: str) -> bool:
        if 'Door' in state:
            return True
        elif 'Hold' in state:
            return True
        return state in VALID_STATES

    def is_valid_trigger(self, trigger: str) -> bool:
        # `X Y Z A B C` XYZABC limit pins, respectively
        # P the probe pin.
        # T the tool setter pin
        # D H R S the door, hold, soft-reset, and cycle-start pins, respectively
        for char in trigger:
            if char not in 'XYZABCDHTRS':
                return False
        return True

    def parse_position(self, axes_message:str):
        kind, axes = axes_message.split(":")
        if kind in ('MPos', 'WCO'):
            return kind, Position(*map(Decimal, axes.split(",")))
        return None

    # ------------------------------------------

    def handle_exp_id(self):
        self.send_message("(EXP,fluidpy)")

    def handle_exp_io(self, io_name: str, io_mode: str):
        self.send_bytes(bytes([0xB2,]))

    def handle_machine_state(self, state: str):
        logger.info(f"machine state >> {state}")

    def handle_position(self, kind: str, position: Position):
        logger.info(f"{kind} >> {position}")

    def handle_mode(self, mode: Mode):
        logger.info(f"mode >> {mode}")

    def handle_log(self, level: str, message: str):
        logger.info(f"{level} >> {message}")

    def handle_version(self, version: str):
        logger.info(f"version >> {version}")

    def handle_feed(self, feed_rate: Decimal):
        logger.info(f"feed >> {feed_rate}")

    def handle_spindle(self, spindle_speed: Decimal):
        logger.info(f"spindle >> {spindle_speed}")

    def handle_ini(self, ini: dict):
        pass

    # TODO : handle_x, handle_y, handle_z, handle_a, handle_b, handle_c etc (maybe?)
    def handle_triggers(self, triggers: str):
        # `X Y Z A B C` XYZABC limit pins, respectively
        # `P` > the probe pin.
        # `T` > the tool setter pin
        # `D H R S` > the door, hold, soft-reset, and cycle-start pins, respectively
        logger.info(f"Trigger: {triggers}")

    def handle_overrides(self, feed: Decimal, rapid: Decimal, spindle: Decimal):
        logger.info(f"Overrides >> feed: {feed}, rapid: {rapid}, spindle: {spindle}")

    def handle_line_number(self, line_number: int):
        logger.info(f"Line number >> {line_number}")

    # ------------------------------------------

    def listen(self):
        print("Listening...")

        while True:
            data = self.read_message()
            if not data:
                continue
            self.process_message(data)

    async def alisten(self):
        print("Listening...")
        while True:
            data = self.read_message()

    def process_message(self, message: str) -> None:

        # logger.debug(f"Received: {data}")
        # if "EXP:ID" in message:
        #     self.handle_exp_id()
        #
        #     logger.debug("EXP received")
        #     if message == "[EXP:ID]":
        #         self.send_message("(EXP,fluidpy)")
        #     elif 'EXP:io' in message:
        #         self.io.write(bytes([0xB2,]))
        #         logger.debug(f"ack sent for {message}")

        if match := self.exp_re.match(message):
            exp = match.group(1)
            if exp == "ID":
                self.handle_exp_id()
            elif 'io' in exp:
                self.handle_exp_io(*exp.split("="))
            else:
                raise FluidParseException(f"unknown exp: {exp}")
        elif match := self.status_re.match(message):
            state, message = match.groups()
            if self.is_state_valid(state):
                self.handle_machine_state(state)
            else:
                logger.warning(f"Invalid state: {state}")
            for partial in message.split("|"):
                kind, mantissa = partial.split(":")
                if kind in ('MPos', 'WCO'):
                    parsed_position = self.parse_position(partial)
                    self.handle_position(*parsed_position)
                elif kind in ('F', 'FS'):
                    feed, speed = map(Decimal, mantissa.split(","))
                    self.handle_feed(feed)
                    self.handle_spindle(speed)
                elif kind == 'Pn':
                    self.handle_triggers(mantissa)
                elif kind == 'Err':
                    print(f"Err >> {mantissa}")
                elif kind == 'Ov':
                    self.handle_overrides(*map(Decimal, mantissa.split(",")))
                elif kind == 'Ln':
                    self.handle_line_number(int(mantissa))
                elif kind == 'Bf':
                    print(f"Bf >> {mantissa}")
                else:
                    raise FluidParseException(f"unknown status: {kind}:{mantissa}")
        elif match := self.version_re.match(message):
            self.send_message("$Report/Interval=200")
            self.handle_version(match.group(1))
        elif match := self.log_re.match(message):
            level, message = match.groups()
            self.handle_log(level, message)
        elif match := self.ini_re.match(message):
            print(f"ini >> {match.groups()}")
        elif match := self.mode_re.match(message):
            mode = Mode.from_string(match.group(1))
            self.handle_mode(mode)
        else:
            raise FluidParseException(f"unknown >> {message}")

