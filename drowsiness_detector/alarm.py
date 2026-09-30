"""Alarmes: buzzer físico (GPIO) ou saída no terminal."""

import logging
import threading
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)


class Alarm(ABC):
    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    def close(self) -> None:
        self.stop()


class ConsoleAlarm(Alarm):
    """Alarme virtual, usado quando não há buzzer/GPIO disponível."""

    def __init__(self) -> None:
        self._active = False

    def start(self) -> None:
        if not self._active:
            self._active = True
            log.warning("[BEEP VIRTUAL] Alarme ativado")

    def stop(self) -> None:
        self._active = False


class BuzzerAlarm(Alarm):
    """Buzzer ativo na GPIO, acionado em pulsos por uma thread própria."""

    ON_TIME = 0.3
    OFF_TIME = 0.1

    def __init__(self, pin: int) -> None:
        from gpiozero import Buzzer  # importado aqui: só existe no Raspberry Pi

        self._buzzer = Buzzer(pin)
        self._running = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running.is_set():
            return
        self._running.set()
        self._thread = threading.Thread(target=self._pulse, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running.clear()
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None
        self._buzzer.off()

    def close(self) -> None:
        self.stop()
        self._buzzer.close()  # libera o pino

    def _pulse(self) -> None:
        while self._running.is_set():
            self._buzzer.on()
            self._running.wait(self.ON_TIME)
            self._buzzer.off()
            self._running.wait(self.OFF_TIME)


def create_alarm(pin: int, use_buzzer: bool = True) -> Alarm:
    """Cria o buzzer físico; se indisponível, cai para o alarme virtual."""
    if use_buzzer:
        try:
            return BuzzerAlarm(pin)
        except Exception as exc:  # ImportError, erros de GPIO, etc.
            log.warning("Buzzer indisponível (%s). Usando alarme virtual.", exc)
    return ConsoleAlarm()
