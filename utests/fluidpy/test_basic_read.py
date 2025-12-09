
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



"""
log >> ('INFO:', 'Kinematic system: Cartesian')
log >> ('INFO:', 'Connecting to STA SSID:Verizon_YP3QZF')
log >> ('INFO:', 'Connecting.')
log >> ('INFO:', 'Connecting..')
log >> ('INFO:', 'Connecting...')
log >> ('INFO:', 'Connected - IP is 192.168.1.154')
log >> ('INFO:', 'WiFi on')
log >> ('INFO:', 'Start mDNS with hostname:http://fluiddev.local/')
log >> ('INFO:', 'HTTP started on port 80')
log >> ('INFO:', 'Telnet started on port 23')
log >> ('INFO:', 'ModbusVFD Spindle Tx:gpio.15 Rx:gpio.16 RTS:gpio.14 Baud:9600')
log >> ('INFO:', 'Probe gpio.2:pu')
log >> ('INFO:', 'Toolsetter gpio.33:pu')
log >> ('DBG:', 'Y Neg Limit 0')
log >> ('DBG:', 'Y Pos Limit 0')
log >> ('DBG:', 'X Neg Limit 0')
log >> ('DBG:', 'X Pos Limit 0')
log >> ('DBG:', 'Toolsetter 1')
log >> ('DBG:', 'Z Neg Limit 0')
log >> ('DBG:', 'Probe 1')
log >> ('WARN:', 'Input pin(s) active on startup:PT')
log >> ('DBG:', 'ModbusVFD: setState:5 SpindleSpeed:0')
log >> ('DBG:', 'setSpeed 0')
log >> ('INFO:', 'Syncing to 0')
log >> ('INFO:', 'Synced speed to 0')
unknown >> Grbl 4.0 [FluidNC v4.0.0-pre2 (rs485_frame_alignment-d66a4e17) (wifi) '$' for help]
log >> ('DBG:', 'RS485 Tx:  01 06 80 00 08 02 26 0B')
log >> ('DBG:', 'RS485 Rx: ')
log >> ('INFO:', 'RS485 No response')
log >> ('DBG:', 'RS485 Tx:  01 06 80 00 08 02 26 0B')
log >> ('DBG:', 'RS485 Rx: ')
log >> ('INFO:', 'RS485 No response')
log >> ('DBG:', 'RS485 Tx:  01 06 80 00 08 02 26 0B')
log >> ('DBG:', 'RS485 Rx: ')
log >> ('INFO:', 'RS485 No response')
log >> ('DBG:', 'RS485 Tx:  01 06 80 00 08 02 26 0B')
log >> ('DBG:', 'RS485 Rx: ')
log >> ('INFO:', 'RS485 No response')
log >> ('DBG:', 'RS485 Tx:  01 06 80 00 08 02 26 0B')
log >> ('DBG:', 'RS485 Rx: ')
log >> ('INFO:', 'RS485 No response')
4594.719: DEBUG - Received: <Jog|MPos:2.932,0.000,0.000|FS:7,0|Pn:PT>
MPos >> 2.932,0.000,0.000
FS >> 7,0
Pn >> PT
4594.818: DEBUG - Received: <Jog|MPos:2.999,0.000,0.000|FS:0,0|Pn:PT>
MPos >> 2.999,0.000,0.000
FS >> 0,0
Pn >> PT
4594.838: DEBUG - Received: <Idle|MPos:3.000,0.000,0.000|FS:0,0|Pn:PT>
MPos >> 3.000,0.000,0.000
FS >> 0,0
Pn >> PT
4608.553: DEBUG - Received: [MSG:DBG: ModbusVFD: setState:3 SpindleSpeed:100]
log >> ('DBG:', 'ModbusVFD: setState:3 SpindleSpeed:100')
4608.559: DEBUG - Received: [MSG:DBG: set_mode 3]
log >> ('DBG:', 'set_mode 3')
4608.563: DEBUG - Received: [MSG:INFO: Syncing to -1]
log >> ('INFO:', 'Syncing to -1')
4608.619: DEBUG - Received: [GC:G0 G54 G17 G21 G90 G94 M5 M9 T0 F0 S100]
unknown mode: G94
unknown mode: M5
mode >> Mode(is_rapid=True, wco_index=1, plane=XY, is_inches=False, is_absolute=True, feed_rate_mode=UNITS/MIN, coolant=OFF, tool_number=0, feed_rate=0, spindle_speed=100)
4608.775: DEBUG - Received: [MSG:DBG: RS485 Tx:  01 06 80 00 09 02 27 9B]
log >> ('DBG:', 'RS485 Tx:  01 06 80 00 09 02 27 9B')
4608.875: DEBUG - Received: [MSG:DBG: RS485 Rx: ]
log >> ('DBG:', 'RS485 Rx: ')
4608.879: DEBUG - Received: [MSG:INFO: RS485 No response]
log >> ('INFO:', 'RS485 No response')
4609.141: DEBUG - Received: [MSG:DBG: RS485 Tx:  01 06 80 00 09 02 27 9B]
log >> ('DBG:', 'RS485 Tx:  01 06 80 00 09 02 27 9B')
4609.242: DEBUG - Received: [MSG:DBG: RS485 Rx: ]
log >> ('DBG:', 'RS485 Rx: ')
4609.246: DEBUG - Received: [MSG:INFO: RS485 No response]
log >> ('INFO:', 'RS485 No response')
4609.506: DEBUG - Received: [MSG:DBG: RS485 Tx:  01 06 80 00 09 02 27 9B]
log >> ('DBG:', 'RS485 Tx:  01 06 80 00 09 02 27 9B')
4609.607: DEBUG - Received: [MSG:DBG: RS485 Rx: ]
log >> ('DBG:', 'RS485 Rx: ')
4609.611: DEBUG - Received: [MSG:INFO: RS485 No response]
log >> ('INFO:', 'RS485 No response')
4609.873: DEBUG - Received: [MSG:DBG: RS485 Tx:  01 06 80 00 09 02 27 9B]
log >> ('DBG:', 'RS485 Tx:  01 06 80 00 09 02 27 9B')
4609.973: DEBUG - Received: [MSG:DBG: RS485 Rx: ]
log >> ('DBG:', 'RS485 Rx: ')
4609.977: DEBUG - Received: [MSG:INFO: RS485 No response]
log >> ('INFO:', 'RS485 No response')
4610.238: DEBUG - Received: [MSG:DBG: RS485 Tx:  01 06 80 00 09 02 27 9B]
log >> ('DBG:', 'RS485 Tx:  01 06 80 00 09 02 27 9B')
4610.338: DEBUG - Received: [MSG:DBG: RS485 Rx: ]
log >> ('DBG:', 'RS485 Rx: ')
4610.342: DEBUG - Received: [MSG:INFO: RS485 No response]
log >> ('INFO:', 'RS485 No response')
4610.854: DEBUG - Received: [MSG:DBG: RS485 Tx:  01 03 80 18 00 01 2D CD]
log >> ('DBG:', 'RS485 Tx:  01 03 80 18 00 01 2D CD')
4610.955: DEBUG - Received: [MSG:DBG: RS485 Rx: ]
log >> ('DBG:', 'RS485 Rx: ')
4610.959: DEBUG - Received: [MSG:INFO: RS485 No response]
log >> ('INFO:', 'RS485 No response')
4611.219: DEBUG - Received: [MSG:DBG: RS485 Tx:  01 03 80 18 00 01 2D CD]
log >> ('DBG:', 'RS485 Tx:  01 03 80 18 00 01 2D CD')
4611.320: DEBUG - Received: [MSG:DBG: RS485 Rx: ]
log >> ('DBG:', 'RS485 Rx: ')
4611.324: DEBUG - Received: [MSG:INFO: RS485 No response]
log >> ('INFO:', 'RS485 No response')
4611.557: DEBUG - Received: [MSG:ERR: ModbusVFD: spindle did not reach device units 4294967295. Reported value is 0]
log >> ('ERR:', 'ModbusVFD: spindle did not reach device units 4294967295. Reported value is 0')
4611.563: DEBUG - Received: [MSG:INFO: ALARM: Spindle Control]
log >> ('INFO:', 'ALARM: Spindle Control')
4611.566: DEBUG - Received: ALARM:10
unknown >> ALARM:10
4611.570: DEBUG - Received: <Alarm|MPos:3.000,0.000,0.000|FS:0,100|Pn:PT|Ov:100,100,100|A:S>
MPos >> 3.000,0.000,0.000
FS >> 0,100
Pn >> PT
Ov >> 100,100,100
partial >> A:S
4611.578: DEBUG - Received: [GC:G0 G54 G17 G21 G90 G94 M3 M9 T0 F0 S100]
unknown mode: G94
unknown mode: M3
mode >> Mode(is_rapid=True, wco_index=1, plane=XY, is_inches=False, is_absolute=True, feed_rate_mode=UNITS/MIN, coolant=OFF, tool_number=0, feed_rate=0, spindle_speed=100)
4611.590: DEBUG - Received: [MSG:DBG: RS485 Tx:  01 03 80 18 00 01 2D CD]
log >> ('DBG:', 'RS485 Tx:  01 03 80 18 00 01 2D CD')
4611.686: DEBUG - Received: [MSG:DBG: RS485 Rx: ]
log >> ('DBG:', 'RS485 Rx: ')
4611.689: DEBUG - Received: [MSG:INFO: RS485 No response]
log >> ('INFO:', 'RS485 No response')
4611.951: DEBUG - Received: [MSG:DBG: RS485 Tx:  01 03 80 18 00 01 2D CD]
log >> ('DBG:', 'RS485 Tx:  01 03 80 18 00 01 2D CD')
4612.051: DEBUG - Received: [MSG:DBG: RS485 Rx: ]
log >> ('DBG:', 'RS485 Rx: ')
"""