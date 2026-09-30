# Detector de Sonolência

Sistema em Python que monitora o rosto de uma pessoa por câmera e **aciona um alarme sonoro quando detecta olhos fechados por tempo prolongado**. Feito para rodar em um **Raspberry Pi** com câmera e buzzer na GPIO, mas também funciona em PC com webcam.

> Projeto desenvolvido como parte de um trabalho de conclusão de curso (TCC).

## Como funciona

1. A câmera captura os frames e o **MediaPipe Face Mesh** localiza 468+ pontos do rosto.
2. Para cada olho, calcula-se o **EAR (Eye Aspect Ratio)**, razão entre a abertura vertical e a largura do olho:

   ```
   EAR = (‖p2 − p6‖ + ‖p3 − p5‖) / (2 · ‖p1 − p4‖)
   ```

   Olho aberto tem EAR em torno de 0,3; ao fechar, o valor cai para perto de 0.
3. Se o EAR médio dos dois olhos ficar abaixo do limiar por N frames seguidos, o estado vira **sonolência** e o buzzer é acionado em pulsos.
4. Ao abrir os olhos, o alarme para imediatamente.

Técnica original: Soukupová & Čech (2016), *Real-Time Eye Blink Detection using Facial Landmarks*.

## Hardware (opcional)

| Item | Detalhe |
|------|---------|
| Placa | Raspberry Pi |
| Câmera | Módulo CSI (ex.: OV5647) ou webcam USB |
| Buzzer | Buzzer **ativo** na protoboard |

Ligação: positivo do buzzer na **GPIO 18 (pino físico 12)** e negativo em um pino **GND** (ex.: pino físico 14). O pino pode ser trocado com `--pin`.

## Instalação

```bash
git clone https://github.com/Th-SoTi/drowsiness-detector.git
cd drowsiness-detector
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
# Raspberry Pi, sem tela, buzzer na GPIO 18
python -m drowsiness_detector

# PC com webcam, mostrando o vídeo e sem GPIO
python -m drowsiness_detector --display --no-buzzer

# Câmera de celular via stream (ex.: DroidCam)
python -m drowsiness_detector --camera http://192.168.0.10:4748/video --display --no-buzzer
```

| Opção | Padrão | Descrição |
|-------|--------|-----------|
| `--camera` | `0` | Índice da câmera ou URL de stream |
| `--ear-threshold` | `0.25` | EAR abaixo do qual o olho é considerado fechado |
| `--frames` | `15` | Frames consecutivos para disparar o alarme |
| `--pin` | `18` | GPIO (BCM) do buzzer |
| `--no-buzzer` | — | Usa alarme virtual (mensagem no terminal) |
| `--display` | — | Abre janela com vídeo; `q` para sair |
| `--light` | — | Desativa refinamento de íris para poupar CPU |

Sem `--display`, encerre com `Ctrl+C`. Se a GPIO não estiver disponível, o programa avisa e usa o alarme virtual automaticamente.

## Estrutura

```
drowsiness_detector/
├── config.py     # constantes e parâmetros
├── ear.py        # cálculo do EAR
├── monitor.py    # máquina de estados (alerta / olhos fechados / sonolência)
├── alarm.py      # buzzer GPIO e alarme virtual
└── main.py       # captura, detecção e CLI
tests/            # testes unitários (pytest)
```

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

## Limitações e próximos passos

- O limiar de EAR é fixo; o ideal seria **calibrar por pessoa** (formato dos olhos varia).
- Óculos, pouca luz e ângulo do rosto afetam a precisão.
- Considera apenas olhos fechados; poderia incluir bocejo e inclinação da cabeça.
- É um protótipo acadêmico: **não substitui sistemas certificados de segurança veicular**.

## Licença

[MIT](LICENSE) © Soti
