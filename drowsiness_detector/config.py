"""Configurações e constantes do detector."""

from dataclasses import dataclass

# Índices dos landmarks do MediaPipe Face Mesh usados no cálculo do EAR.
# Ordem: canto externo, 2 pontos superiores, canto interno, 2 pontos inferiores.
LEFT_EYE = (33, 160, 158, 133, 153, 144)
RIGHT_EYE = (362, 385, 387, 263, 373, 380)


@dataclass(frozen=True)
class Settings:
    """Parâmetros ajustáveis do detector."""

    ear_threshold: float = 0.25   # abaixo disso, o olho é considerado fechado
    frames_threshold: int = 15    # frames consecutivos para disparar o alarme
    buzzer_pin: int = 18          # GPIO (BCM) do buzzer; pino físico 12
    max_read_failures: int = 50   # falhas seguidas de leitura antes de abortar
