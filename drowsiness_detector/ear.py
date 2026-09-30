"""Cálculo do Eye Aspect Ratio (EAR).

Referência: Soukupová & Čech (2016), "Real-Time Eye Blink Detection using
Facial Landmarks".

    EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)

O valor cai perto de zero quando o olho fecha.
"""

from math import dist
from typing import Sequence


def eye_aspect_ratio(landmarks: Sequence, indices: Sequence[int]) -> float:
    """Calcula o EAR de um olho.

    Args:
        landmarks: sequência de pontos com atributos ``x`` e ``y``
            (ex.: ``face_landmarks.landmark`` do MediaPipe).
        indices: 6 índices na ordem [p1, p2, p3, p4, p5, p6].
    """
    p1, p2, p3, p4, p5, p6 = ((landmarks[i].x, landmarks[i].y) for i in indices)
    horizontal = dist(p1, p4)
    if horizontal == 0:
        return 0.0
    return (dist(p2, p6) + dist(p3, p5)) / (2.0 * horizontal)
