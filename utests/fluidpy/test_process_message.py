from fluidpy.fluidnc import FluidNC

MESSAGES = {
    'idle': "<Idle|MPos:3.000,0.000,0.000|FS:0,0|Pn:PT|Bf:15,128>",
    'jog': "<Jog|MPos:2.932,0.000,0.000|FS:7,0|Pn:PT|Ln:99999>",
    'alarm': "<Alarm|MPos:3.000,0.000,0.000|FS:0,100|Pn:PT|Ov:100,100,100|A:S>",
    'log': "[MSG:DBG: ModbusVFD: setState:3 SpindleSpeed:100]",
    'mode': "[GC:G0 G54 G17 G21 G90 G94 M5 M9 T0 F0 S100]",
    'exp_id': "[EXP:ID]",
    'exp_io': "[EXP:io.2=out]",
    'version': "Grbl 4.0 [FluidNC v4.0.0-pre2 (v4_plus-40f72c3d) (wifi) '$' for help]",
    'error': 'error:x',
    'ok': 'ok',
    'alarm2': "ALARM:10",
    'var_value': "$x=val",
    'line': '$Nx=line',
    'g_c': '[GC:]',
    'help': '[HLP:]',
    'g_54': '[G54:]',
    'g_55': '[G55:]',
    'g_56': '[G56:]',
    'g_57': '[G57:]',
    'g_58': '[G58:]',
    'g_59': '[G59:]',
    'g_28': '[G28:]',
    'g_30': '[G30:]',
    'g_92': '[G92:]',
    'tl0': '[TLO:]',
    'prb': '[PRB:]',
    'ver': '[VER:]',
    'echo': '[echo:]',
    'mode2': '>G54G20:ok'
}

VERSIONS = [
    "Grbl 4.0 [FluidNC v4.0.0-pre2 (v4_plus-40f72c3d) (wifi) '$' for help]",
    "Grbl 4.0 FluidNC v4.0.0-pre2 (rs485_little_endian-4a6b95e6-dirty) https://github.com/bdring/FluidNC]"
]


"""
<Idle|MPos:3.000,0.000,0.000|FS:0,0|Pn:PT|Bf:15,128>
FluidNC v4.0.0-pre2 (rs485_little_endian-4a6b95e6-dirty) https://github.com/bdring/FluidNC
ALARM:10
$x=val
$Nx=line
[MSG:]
[GC:]
[HLP:]
[G54:]
[G55:]
[G56:]
[G57:]
[G58:]
[G59:]
[G28:]
[G30:]
[G92:]
[TLO:]
[PRB:]
[VER:]
[echo:]
>G54G20:ok
ok
error:x"""


def test_jog_message(fnc: FluidNC):
    fnc.process_message(MESSAGES['jog'])
    fnc.handle_position.assert_called_once()

def test_idle_message(fnc: FluidNC):
    fnc.process_message(MESSAGES['idle'])
    fnc.handle_machine_state.assert_called_once()
    fnc.handle_position.assert_called_once()
    fnc.handle_overrides.assert_not_called()

def test_alarm_message(fnc: FluidNC):
    fnc.process_message(MESSAGES['alarm'])
    fnc.handle_position.assert_called_once()
    fnc.handle_feed.assert_called_once()
    fnc.handle_spindle.assert_called_once()
    fnc.handle_triggers.assert_called_once()
    fnc.handle_overrides.assert_called_once()
    fnc.handle_accessory_state.assert_called_once()

def test_log_message(fnc: FluidNC):
    fnc.process_message(MESSAGES['log'])
    fnc.handle_log.assert_called_once()

def test_machine_mode_message(fnc: FluidNC):
    fnc.process_message(MESSAGES['mode'])
    fnc.handle_mode.assert_called_once()

def test_exp_id_message(fnc: FluidNC):
    fnc.process_message(MESSAGES['exp_id'])
    fnc.handle_exp_id.assert_called_once()

def test_exp_io_message(fnc: FluidNC):
    fnc.process_message(MESSAGES['exp_io'])
    fnc.handle_exp_io.assert_called_once()


def test_all_messages(fnc: FluidNC):

    # run all the messages
    for msg in MESSAGES.values():
        fnc.process_message(msg)

    # make sure each handler was called at least once
    for name, mock in fnc.mocks.items():
        try:
            mock.assert_called()
        except AssertionError as a:
            raise AssertionError(f"'{name}' was not called") from a
