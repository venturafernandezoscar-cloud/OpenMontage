#!/usr/bin/env python3
"""SALTAMUNDOS · Jingle de la intro (5,00 s exactos), sintetizado nota a nota.

Sincronía con la intro (BIBLIA §2):
  0,00–0,80  caen 5 burbujas            -> "boing" grave + xilófono Do-Mi-Sol-Do-Mi (una nota por burbuja)
  0,80–1,50  Tomi sonríe a cámara       -> brillo de glockenspiel
  1,50–3,50  4 sílabas SAL-TA-MUN-DOS   -> xilófono Sol-Do-Mi-Sol↑ + "boing" en cada caída
  3,50–4,40  Lía y Pipo + logo          -> CAMPANILLA característica (Do agudo) + acorde
  4,40–5,00  la "O" nos traga           -> "fuuup" ascendente que termina en la tónica
Uso: python3 jingle.py salida.wav
"""
import sys
import numpy as np
import wave

SR = 48000
DUR = 5.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)


def nota(n):  # nombre -> Hz
    idx = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    return 440.0 * 2 ** ((idx[n[0]] + 12 * (int(n[-1]) - 4)) / 12)


def poner(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    s = sig[: max(0, N - i)] * gain
    L[i:i + len(s)] += s * np.sqrt(0.5 * (1 - pan))
    R[i:i + len(s)] += s * np.sqrt(0.5 * (1 + pan))


def xilofono(f, d=1.2):
    t = np.arange(int(d * SR)) / SR
    # parciales de barra de madera afinada (1, 3.9, 9.2) con caídas rápidas
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 6)
         + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 18)
         + 0.12 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 40))
    golpe = rng.standard_normal(len(t)) * np.exp(-t * 900) * 0.25  # mazo
    att = np.minimum(1, t / 0.002)
    return (s + golpe) * att


def glock(f, d=2.5):
    t = np.arange(int(d * SR)) / SR
    parc = [(1, 1, 2.2), (2.76, 0.4, 4), (5.40, 0.2, 7), (8.93, 0.1, 11)]
    s = sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t * k) for p, a, k in parc)
    return s * np.minimum(1, t / 0.001)


def campanilla(f, d=3.0):
    # campana brillante: glockenspiel + octava + leve trémolo = firma sonora del canal
    t = np.arange(int(d * SR)) / SR
    s = glock(f, d) + 0.5 * glock(f * 2, d) * np.exp(-t * 1.5)
    return s * (1 + 0.08 * np.sin(2 * np.pi * 6 * t))


def boing(f0, d=0.45):
    t = np.arange(int(d * SR)) / SR
    f = f0 * (1.6 * np.exp(-t * 18) + 1) * (1 + 0.04 * np.sin(2 * np.pi * 28 * t))
    fase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(fase) * np.exp(-t * 7) * np.minimum(1, t / 0.003)


def fuup(t0, d, f_end):
    t = np.arange(int(d * SR)) / SR
    k = t / d
    f = f_end * 0.25 * (4 ** k)                          # glissando que sube dos octavas
    sine = np.sin(2 * np.pi * np.cumsum(f) / SR) * (k ** 1.5)
    ruido = rng.standard_normal(len(t))
    # ruido filtrado que se aclara (filtro de 1 polo con corte creciente)
    out = np.zeros(len(t)); y = 0.0
    a = np.exp(-2 * np.pi * (300 + 2200 * k) / SR)
    for i in range(len(t)):
        y = a[i] * y + (1 - a[i]) * ruido[i]; out[i] = y
    env = np.sin(np.pi * np.minimum(k, 0.999)) ** 0.7
    return 0.9 * sine * env + 0.35 * out * env


def pad(fs, d, t0):
    t = np.arange(int(d * SR)) / SR
    env = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.6)
    s = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for f in fs)
    poner(s * env * 0.05, t0, 0.0)


# 0,00–0,80: burbujas
poner(boing(nota("C3")), 0.00, 0, 0.5)
for k, (t, n) in enumerate(zip([0.00, 0.10, 0.20, 0.30, 0.40], ["C5", "E5", "G5", "C6", "E6"])):
    poner(xilofono(nota(n)), t + 0.08, pan=-0.6 + 0.3 * k, gain=0.55)
# 0,80–1,50: Tomi sonríe -> destellos
for k, n in enumerate(["G6", "C7", "E7"]):
    poner(glock(nota(n), 1.2), 0.85 + k * 0.06, pan=0.3, gain=0.18)
pad([nota("C4"), nota("E4"), nota("G4")], 3.6, 0.8)
# 1,50–3,50: SAL-TA-MUN-DOS (Sol-Do-Mi-Sol agudo), cada sílaba cae con rebote
for k, (t, n) in enumerate(zip([1.50, 2.00, 2.50, 3.00], ["G4", "C5", "E5", "G5"])):
    poner(xilofono(nota(n), 1.4), t, pan=[-0.4, -0.1, 0.1, 0.4][k], gain=0.85)
    poner(xilofono(nota(n) * 2, 0.8), t, pan=[-0.4, -0.1, 0.1, 0.4][k], gain=0.25)
    poner(boing(nota(n) / 2, 0.3), t, pan=0, gain=0.22)
# 3,50: campanilla característica + acorde de llegada
poner(campanilla(nota("C6")), 3.50, 0, 0.6)
for n in ["C5", "E5", "G5", "C6"]:
    poner(xilofono(nota(n), 1.5), 3.50, 0, 0.22)
# 4,40–5,00: fuuup que termina en la tónica (Do)
poner(fuup(4.40, 0.60, nota("C6")), 4.40, 0, 0.35)

# reverb corta (sala brillante)
ir_t = np.arange(int(0.9 * SR)) / SR
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 6)
ir /= np.sqrt((ir ** 2).sum())
wet_L = np.convolve(L, ir)[:N]; wet_R = np.convolve(R, ir[::-1].copy())[:N]
L2, R2 = L + 0.25 * wet_L, R + 0.25 * wet_R
# fundido final muy corto para no cortar en seco
fade = np.ones(N); fade[-int(0.03 * SR):] = np.linspace(1, 0, int(0.03 * SR))
st = np.stack([L2 * fade, R2 * fade], 1)
st /= np.abs(st).max() / 0.89  # pico -1 dBFS
out = sys.argv[1] if len(sys.argv) > 1 else "jingle.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print(f"✅ {out}  ({N/SR:.2f} s)")
