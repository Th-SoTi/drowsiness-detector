"""Ponto de entrada: captura, detecção e acionamento do alarme."""

import argparse
import logging
import time

from .alarm import create_alarm
from .config import LEFT_EYE, RIGHT_EYE, Settings
from .ear import eye_aspect_ratio
from .monitor import DrowsinessMonitor, State

log = logging.getLogger("drowsiness_detector")


def parse_args() -> argparse.Namespace:
    defaults = Settings()
    p = argparse.ArgumentParser(
        prog="drowsiness_detector",
        description="Detector de sonolência por visão computacional.",
    )
    p.add_argument("--camera", default="0",
                   help="índice da câmera (ex.: 0) ou URL de stream (ex.: http://IP:4748/video)")
    p.add_argument("--ear-threshold", type=float, default=defaults.ear_threshold,
                   help="EAR abaixo do qual o olho é considerado fechado")
    p.add_argument("--frames", type=int, default=defaults.frames_threshold,
                   help="frames consecutivos com olhos fechados para disparar o alarme")
    p.add_argument("--pin", type=int, default=defaults.buzzer_pin, help="GPIO (BCM) do buzzer")
    p.add_argument("--no-buzzer", action="store_true", help="não usar GPIO; alarme apenas no terminal")
    p.add_argument("--display", action="store_true", help="mostrar janela com vídeo (requer ambiente gráfico)")
    p.add_argument("--light", action="store_true",
                   help="desativa refinamento de íris do MediaPipe para economizar CPU")
    return p.parse_args()


def open_camera(source: str):
    import cv2

    return cv2.VideoCapture(int(source) if source.isdigit() else source)


def draw_overlay(cv2, frame, state: State, ear: float | None) -> None:
    color = {
        State.ALERT: (0, 200, 0),
        State.EYES_CLOSED: (0, 165, 255),
        State.DROWSY: (0, 0, 255),
        State.NO_FACE: (150, 150, 150),
    }[state]
    if ear is not None:
        cv2.putText(frame, f"EAR: {ear:.2f}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, state.value, (30, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)


def run(args: argparse.Namespace) -> int:
    import cv2
    import mediapipe as mp

    settings = Settings()
    monitor = DrowsinessMonitor(args.ear_threshold, args.frames)
    alarm = create_alarm(args.pin, use_buzzer=not args.no_buzzer)

    cap = open_camera(args.camera)
    if not cap.isOpened():
        log.error("Câmera não encontrada: %s", args.camera)
        alarm.close()
        return 1

    face_mesh = mp.solutions.face_mesh.FaceMesh(
        refine_landmarks=not args.light,
        max_num_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    log.info("Monitorando. Pressione Ctrl+C%s para encerrar.", " ou 'q' na janela" if args.display else "")
    previous_state: State | None = None
    failures = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                failures += 1
                if failures >= settings.max_read_failures:
                    log.error("Falha repetida ao ler a câmera. Encerrando.")
                    return 1
                time.sleep(0.1)
                continue
            failures = 0

            result = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            ear = None
            if result.multi_face_landmarks:
                lm = result.multi_face_landmarks[0].landmark
                ear = (eye_aspect_ratio(lm, LEFT_EYE) + eye_aspect_ratio(lm, RIGHT_EYE)) / 2.0
                state = monitor.update(ear)
            else:
                state = monitor.face_lost()

            if state is State.DROWSY:
                alarm.start()
            elif state is State.ALERT:
                alarm.stop()

            if state is not previous_state:  # loga só as mudanças de estado
                log.info("%s%s", state.value, f" (EAR {ear:.2f})" if ear is not None else "")
                previous_state = state

            if args.display:
                draw_overlay(cv2, frame, state, ear)
                cv2.imshow("Detector de sonolência", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        log.info("Encerrando pelo teclado.")
    finally:
        cap.release()
        face_mesh.close()
        alarm.close()
        if args.display:
            cv2.destroyAllWindows()
    log.info("Sistema encerrado.")
    return 0


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    raise SystemExit(run(parse_args()))


if __name__ == "__main__":
    main()
