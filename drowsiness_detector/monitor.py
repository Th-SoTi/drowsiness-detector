"""Lógica de decisão: transforma leituras de EAR em estados."""

from enum import Enum


class State(Enum):
    NO_FACE = "Rosto não detectado"
    ALERT = "Alerta"
    EYES_CLOSED = "Olhos fechados"
    DROWSY = "Sonolência detectada"


class DrowsinessMonitor:
    """Conta frames consecutivos com olhos fechados e decide o estado."""

    def __init__(self, ear_threshold: float, frames_threshold: int) -> None:
        self.ear_threshold = ear_threshold
        self.frames_threshold = frames_threshold
        self.closed_frames = 0

    def update(self, ear: float) -> State:
        """Processa uma leitura de EAR e retorna o estado atual."""
        if ear < self.ear_threshold:
            self.closed_frames += 1
            if self.closed_frames >= self.frames_threshold:
                return State.DROWSY
            return State.EYES_CLOSED
        self.closed_frames = 0
        return State.ALERT

    def face_lost(self) -> State:
        """Frame sem rosto: o contador é mantido, sem mudar o estado do alarme."""
        return State.NO_FACE
