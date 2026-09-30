from drowsiness_detector.monitor import DrowsinessMonitor, State


def make():
    return DrowsinessMonitor(ear_threshold=0.25, frames_threshold=3)


def test_open_eyes_are_alert():
    assert make().update(0.35) is State.ALERT


def test_alarm_only_after_consecutive_frames():
    m = make()
    assert m.update(0.10) is State.EYES_CLOSED
    assert m.update(0.10) is State.EYES_CLOSED
    assert m.update(0.10) is State.DROWSY


def test_blink_resets_counter():
    m = make()
    m.update(0.10)
    m.update(0.10)
    assert m.update(0.35) is State.ALERT
    assert m.closed_frames == 0
    assert m.update(0.10) is State.EYES_CLOSED


def test_face_lost_keeps_counter():
    m = make()
    m.update(0.10)
    assert m.face_lost() is State.NO_FACE
    assert m.closed_frames == 1
