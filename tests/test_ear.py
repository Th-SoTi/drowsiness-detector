from types import SimpleNamespace

from drowsiness_detector.ear import eye_aspect_ratio

IDX = (0, 1, 2, 3, 4, 5)


def pts(coords):
    return [SimpleNamespace(x=x, y=y) for x, y in coords]


def test_open_eye_has_high_ear():
    # p1..p6: olho com largura 4 e abertura vertical 2 -> EAR = 0.5
    lm = pts([(0, 0), (1, 1), (3, 1), (4, 0), (3, -1), (1, -1)])
    assert abs(eye_aspect_ratio(lm, IDX) - 0.5) < 1e-9


def test_closed_eye_has_zero_ear():
    lm = pts([(0, 0), (1, 0), (3, 0), (4, 0), (3, 0), (1, 0)])
    assert eye_aspect_ratio(lm, IDX) == 0.0


def test_degenerate_eye_does_not_divide_by_zero():
    lm = pts([(1, 1)] * 6)
    assert eye_aspect_ratio(lm, IDX) == 0.0
