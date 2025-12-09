from fluidpy.fluidnc import FluidNC

def test_jog_message(fnc: FluidNC):
    msg = "<Jog|MPos:2.932,0.000,0.000|FS:7,0|Pn:PT>"
    fnc.process_message(msg)
    fnc.handle_position.assert_called_once()

def test_idle_message(fnc: FluidNC):
    msg = "<Idle|MPos:3.000,0.000,0.000|FS:0,0|Pn:PT>"
    fnc.process_message(msg)
    fnc.handle_machine_state.assert_called_once()
    fnc.handle_position.assert_called_once()
    fnc.handle_overrides.assert_not_called()

def test_alarm_message(fnc: FluidNC):
    msg = "<Alarm|MPos:3.000,0.000,0.000|FS:0,100|Pn:PT|Ov:100,100,100|A:S>"
    fnc.process_message(msg)
    fnc.handle_position.assert_called_once()
    fnc.handle_feed.assert_called_once()
    fnc.handle_spindle.assert_called_once()
    fnc.handle_triggers.assert_called_once()
    fnc.handle_overrides.assert_called_once()

def test_log_message(fnc: FluidNC):
    msg = "[MSG:DBG: ModbusVFD: setState:3 SpindleSpeed:100]"
    fnc.process_message(msg)
    fnc.handle_log.assert_called_once()

def test_machine_mode_message(fnc: FluidNC):
    msg = "[GC:G0 G54 G17 G21 G90 G94 M5 M9 T0 F0 S100]"
    fnc.process_message(msg)
    fnc.handle_mode.assert_called_once()

def test_exp_id_message(fnc: FluidNC):
    msg = "[EXP:ID]"
    fnc.process_message(msg)
    fnc.handle_exp_id.assert_called_once()

def test_exp_io_message(fnc: FluidNC):
    msg = "[EXP:io.2=out]"
    fnc.process_message(msg)
    fnc.handle_exp_io.assert_called_once()
