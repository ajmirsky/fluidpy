import asyncio
import re
try:
    import logging
except ImportError:
    import adafruit_logging as logging

from fluidpy.udecimal import DecimalNumber as Decimal

logger = logging.getLogger(__name__)

VALID_STATES = ('Idle', 'Run', 'Hold', 'Jog', 'Alarm', 'Door', 'Check', 'Home', 'Sleep')

class BufferInterface:

    def read(self, n: int) -> bytes:
        raise NotImplementedError

    def write(self, buffer: bytes) -> int:
        raise NotImplementedError

    def readline(self) -> bytes:
        raise NotImplementedError

class FluidParseError(Exception):
    pass

class InvalidStateError(Exception):
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
        """x value of the position"""
        self.y: Decimal = y if isinstance(y, Decimal) else Decimal(str(y))
        """y value of the position"""
        self.z: Decimal = z if isinstance(z, Decimal) else Decimal(str(z))
        """z value of the position"""
        self.a: Decimal = a if isinstance(a, Decimal) else Decimal(str(a))
        """a value of the position"""
        self.b: Decimal = b if isinstance(b, Decimal) else Decimal(str(b))
        """b value of the position"""
        self.c: Decimal = c if isinstance(c, Decimal) else Decimal(str(c))
        """c value of the position"""

    def __repr__(self) -> str:
        return f"Position(x={self.x}, y={self.y}, z={self.z}, a={self.a}, b={self.b}, c={self.c})"

class Mode:
    PLANES = ('XY', 'XZ', 'YZ')
    FEED_RATE_MODES = ('INVERSE', 'UNITS/MIN', 'UNITS/REV')
    COOLANT = ('MIST', 'FLOOD', 'OFF')
    SPINDLE_STATES = ('CW', 'CCW', 'STOP')


    def __init__(self,
                 is_rapid: bool = False,
                 wco_index: int = 0,
                 plane: str = 'XY',
                 is_inches: bool = False,
                 is_absolute: bool = False,
                 spindle_state: str = 'OFF',
                 feed_rate_mode: str = 'UNITS/MIN', # INVERSE (G93), UNITS/MIN (G94), UNITS/REV (G95)
                 coolant: str = 'FLOOD',
                 tool_number: int = 0,
                 feed_rate: Decimal = Decimal(0),
                 spindle_speed: Decimal = Decimal(0),
                 ):
        self.is_rapid = is_rapid
        """rapid mode (G0), feed rate mode (G1)"""
        self.wco_index = wco_index
        """work coordinate offset of `0` (G53), `1` (G54), `2` (G55), etc"""
        self.plane = plane
        """`'XY'` (G17), `'XZ'` (G18), `'YZ'` (G19)"""
        self.is_inches = is_inches
        """inches (G20), mm (G21)"""
        self.is_absolute = is_absolute
        """absolute (G90), relative (G91)"""
        self.feed_rate_mode = feed_rate_mode
        """`'INVERSE'` (G93), `'UNITS/MIN'` (G94), `'UNITS/REV'` (G95)"""
        self.coolant = coolant
        """`'MIST'` (M7), `'FLOOD'` (M8), `'OFF'` (M9)"""
        self.tool_number = tool_number
        """tool number 0-9"""
        self.feed_rate = feed_rate
        """feed rate"""
        self.spindle_speed = spindle_speed
        """spindle speed"""
        self.spindle_state = spindle_state
        """`'CW'` (M3), `'CCW'` (M4), `'STOP'` (M5)"""

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
                raise FluidParseError(f"unknown mode: {mode}")

        return cls(**params)


class FluidNC:
    version_re = re.compile(r"\[FluidNC\s(v.+?)\s")

    # pin initialization
    # eg. [EXP:ID] or [EXP:io.2=out]
    exp_re = re.compile(r"\[EXP:(.+?)\]")

    # eg. [INI: io.1=in,low,pu]
    ini_re = re.compile(r"\[INI:(.+?)\]")

    # machine mode
    # eg. [GC:G0 G55 G17 G21 G90 G94 M5 M9 T0 F0 S0]
    mode_re = re.compile(r"\[GC:(.+?)\]")
    # eg. [G54:]
    mode_cmd_re = re.compile(r"\[G([0-9C]{1,2}):(.*)?\]")
    # >G54G20:ok
    mode_change_re = re.compile(r">((G[0-9]{1,2})+)(\:([a-z]+))?")

    # eg. machine status
    # <Jog|MPos:59.304,0.000,0.000|FS:300,0|Pn:PT>
    status_re = re.compile(r"<(\w+)\|(.+?)>")

    # log messages
    # eg. [MSG:INFO: Z Axis driver test passed]
    log_re = re.compile(r"\[MSG:(\w+:)?\s*?(\w.+)\]")

    # variable value messages
    # eg. $x=val
    var_re = re.compile(r"\$([a-zA-Z0-9\/]+?)=(.*)")

    # help and status messages
    help_re = re.compile(r"\[HLP:(.*?)\]")
    tlo_re = re.compile(r"\[TLO:(.*?)\]")
    prb_re = re.compile(r"\[PRB:(.*?)\]")
    ver_re = re.compile(r"\[VER:(.*?)\]")
    echo_re = re.compile(r"\[echo:(.*?)\]")


    def __init__(self, io: BufferInterface) -> None:
        self.io = io

    def send_message(self, message: str) -> None:
        """
        Send a string message to the controller.
        """
        self.io.write(message.encode())

    def send_bytes(self, command: bytes) -> None:
        """
        Send a bytes message to the controller.
        """
        self.io.write(command)

    def read_message(self) -> str | None:
        msg = self.io.readline()
        if msg:
            return msg.decode().strip()
        return None

    @staticmethod
    def is_state_valid(state: str) -> bool:
        if 'Door' in state:
            return True
        elif 'Hold' in state:
            return True
        return state in VALID_STATES

    @staticmethod
    def is_valid_trigger(trigger: str) -> bool:
        # `X Y Z A B C` XYZABC limit pins, respectively
        # P the probe pin.
        # T the tool setter pin
        # D H R S the door, hold, soft-reset, and cycle-start pins, respectively
        for char in trigger:
            if char not in 'XYZABCDHTRS':
                return False
        return True

    @staticmethod
    def parse_position(axes_message:str):
        kind, axes = axes_message.split(":")
        if kind in ('MPos', 'WCO'):
            return kind, Position(*map(Decimal, axes.split(",")))
        return None

    # ------------------------------------------

    def handle_exp_id(self) -> None:
        """
        Sends the expander id of 'fluidpy' to the controller.
        """.format(VALID_STATES)
        self.send_message("(EXP,fluidpy)")

    def handle_exp_io(self, io_name: str, io_mode: str) -> None:
        """
        Handle the initialization of an expander pin.
        Needs to acknowledge the pin initialization (0xB2) or failure (0xB3).

        Parameters:
            io_name: `io.1`, `io.2`, etc
            io_mode: comma seperated list of `[in|out|low|high|pu|pd]`

        Returns:
            None
        """
        self.send_bytes(bytes([0xB2,]))  # default response is ACK

    def handle_machine_state(self, state: str) -> None:
        """
        Parameters:
            state: one of one of `['Idle', 'Run', 'Hold', 'Jog', 'Alarm', 'Door', 'Check', 'Home', 'Sleep']`
        """
        logger.debug(f"machine state >> {state}")

    def handle_position(self, kind: str, position: Position) -> None:
        """
        Parameters:
            kind: `MPos` (machine position) or `WCO` (work coordinate offset)
            position: `Position` object with `x`, `y`, `z`, `a`, `b`, `c` attributes
        """
        logger.debug(f"{kind} >> {position}")

    def handle_mode(self, mode: Mode) -> None:
        """
        Parameters:
            mode: `Mode` object with attributes for `rapid`, `wco_index`, `plane`, `is_inches`, `is_absolute`, `feed_rate_mode`, `coolant`, `tool_number`, `feed_rate`, `spindle_speed`
        """
        logger.debug(f"mode >> {mode}")

    def handle_mode_command(self, mode_cmd: str, status: str = "None") -> None:
        """
        Parameters:
            mode_cmd: one of `G54`, `G55`, `G56`, `G57`, `G58`, `G59`, `G28`, `G30`, `G92`
        """
        logger.debug(f"mode command >> {mode_cmd} : {status}")

    def handle_log(self, level: str, message: str) -> None:
        """
        Parameters
            level: one of `DBG`, `INFO`, `WARN`, `ERROR`
            message: log message
        """
        level_str = level.replace(":", "").lower() if level else ""
        logger.debug(f"log ({level_str}) >> {message}")

    def handle_version(self, version: str) -> None:
        """
        Parameters
            version: X.Y.Z or X.Y.Z-abc
        """
        logger.debug(f"version >> {version}")

    def handle_feed(self, feed_rate: Decimal) -> None:
        """
        Parameters:
            feed_rate: in mm/min or inches/min
        """
        logger.debug(f"feed >> {feed_rate}")

    def handle_spindle(self, spindle_speed: Decimal) -> None:
        """
        Parameters:
            spindle_speed: in RPM
        """
        logger.debug(f"spindle >> {spindle_speed}")

    def handle_variable(self, variable: str, value: str) -> None:
        """
        Parameters:
            variable: name of the variable
            value: value of the variable
        """
        logger.debug(f"variable >> {variable} = {value}")

    def handle_help(self, message: str) -> None:
        """
        Parameters:
            message: help message
        """
        logger.debug(f"help >> {message}")

    def handle_tlo(self, message: str) -> None:
        """
        Parameters:
            message: tool length offset message
        """
        logger.debug(f"tool length offset >> {message}")

    def handle_prb(self, message: str) -> None:
        """
        Parameters:
            message: probe message
        """
        logger.debug(f"probe >> {message}")

    # def handle_ini(self, ini: dict):
    #     pass

    # TODO : handle_x, handle_y, handle_z, handle_a, handle_b, handle_c etc (maybe?)
    def handle_triggers(self, triggers: str) -> None:
        """
        Parameters:
            triggers:
                - `X Y Z A B C` XYZABC limit pins, respectively
                - `P` > the probe pin.
                -`T` > the tool setter pin
                - `D H R S` > the door, hold, soft-reset, and cycle-start pins, respectively
        """
        logger.debug(f"Trigger: {triggers}")

    def handle_overrides(self, feed: Decimal, rapid: Decimal, spindle: Decimal) -> None:
        """
        Parameters:
            feed: override percentage
            rapid: override percentage
            spindle: override percentage
        """
        logger.debug(f"Overrides >> feed: {feed}, rapid: {rapid}, spindle: {spindle}")

    def handle_line_number(self, line_number: int) -> None:
        """
        Parameters:
            line_number: current line number
        """
        logger.debug(f"Line number >> {line_number}")

    def handle_error(self, error: str) -> None:
        """
        Parameters:
            error: error message or code
        """
        logger.debug(f"Error >> {error}")

    def handle_ok(self, ok: str):
        """
        Parameters:
            ok: `'ok'`
        """
        logger.debug(f"Ok >> {ok}")

    def handle_buffer_size(self, size: int):
        """
        Parameters:
            size: current buffer size
        """
        logger.debug(f"Buffer size >> {size}")

    def handle_accessory_state(self, state: str):
        """
        Parameters:
            state: accessor state information
        """
        logger.debug(f"Accessory state >> {state}")

    def handle_alarm(self, alarm: str):
        """
        Parameters:
            alarm: alarm message or code
        """
        logger.debug(f"Alarm >> {alarm}")

    def handle_echo(self, message: str):
        """
        Parameters:
            message: echo'ed message
        """
        logger.debug(f"Echo >> {message}")

    # ------------------------------------------

    def listen(self, catch_exc: bool = True):
        print("Listening...")

        while True:
            data = None
            try:
                data = self.read_message()
            except UnicodeError as e:
                logger.warning(f"Unicode error: {e}")
            if not data:
                continue
            try:
                self.process_message(data)
            except FluidParseError as e:
                if not catch_exc:
                    logger.error(f"Fluid parse error: {e}")
                    raise e
                logger.warning(f"Fluid parse error: {e}")

    async def alisten(self, catch_exc: bool = True):
        print("Listening...")
        while True:
            data = None
            # TODO : create an async read message
            try:
                data = self.read_message()
            except UnicodeError as e:
                logger.warning(f"Unicode error: {e}")

            if not data:
                await asyncio.sleep(0)
                continue
            try:
                self.process_message(data)
            except FluidParseError as e:
                if not catch_exc:
                    logger.error(f"Fluid parse error: {e}")
                    raise e
                logger.warning(f"Fluid parse error: {e}")

    def process_message(self, message: str) -> None:

        if match := self.exp_re.match(message):
            exp = match.group(1)
            if exp == "ID":
                self.handle_exp_id()
            elif 'io' in exp:
                self.handle_exp_io(*exp.split("="))
            else:
                raise FluidParseError(f"unknown exp: {exp}")
        elif match := self.status_re.match(message):
            state, message = match.groups()
            if self.is_state_valid(state):
                self.handle_machine_state(state)
            else:
                raise InvalidStateError(f"Invalid state: {state}")
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
                    self.handle_error(mantissa)
                elif kind == 'Ov':
                    self.handle_overrides(*map(Decimal, mantissa.split(",")))
                elif kind == 'Ln':
                    self.handle_line_number(int(mantissa))
                elif kind == 'Bf':
                    self.handle_buffer_size(*map(int, mantissa.split(",")))
                elif kind == 'A':
                    self.handle_accessory_state(mantissa)
                else:
                    raise FluidParseError(f"unknown status: {kind}:{mantissa}")
        elif match := self.version_re.search(message):
            self.send_message("$Report/Interval=200")
            self.handle_version(match.group(1))
        elif match := self.ver_re.match(message):
            self.handle_version(match.group(1))
        elif match := self.log_re.match(message):
            level, message = match.groups()
            self.handle_log(level, message)
        elif match := self.ini_re.match(message):
            print(f"ini >> {match.groups()}")
        elif match := self.mode_re.match(message):
            mode = Mode.from_string(match.group(1))
            self.handle_mode(mode)
        elif match := self.mode_cmd_re.match(message):
            self.handle_mode_command(match.group(2))
        elif match := self.mode_change_re.match(message):
            status = "No Status" if len(match.groups()) < 4 else match.group(3)
            self.handle_mode_command(match.group(1), status)
        elif match := self.var_re.match(message):
            self.handle_variable(*match.groups())
        elif match := self.help_re.match(message):
            self.handle_help(match.group(1))
        elif match := self.tlo_re.match(message):
            self.handle_tlo(match.group(1))
        elif match := self.prb_re.match(message):
            self.handle_prb(match.group(1))
        elif match := self.echo_re.match(message):
            self.handle_echo(match.group(1))
        elif message.startswith("error"):
            self.handle_error(message)
        elif message.startswith("ok"):
            self.handle_ok(message)
        elif message.startswith("ALARM:"):
            self.handle_alarm(message[6:])
        else:
            raise FluidParseError(f"unknown >> {message}")

