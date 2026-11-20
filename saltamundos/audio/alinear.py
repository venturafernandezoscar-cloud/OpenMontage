#!/usr/bin/env python3
"""Alinea la letra conocida con la canción: tiempo de inicio/fin de cada palabra cantada.
1) faster-whisper transcribe con marcas por palabra (sesgado con la letra real).
2) Se emparejan las palabras transcritas con la letra oficial (difflib) y los huecos se interpolan.
Uso: python3 alinear.py cancion.mp3 letra.txt salida.json
"""
import sys, json, re, unicodedata, difflib, subprocess
import numpy as np
from faster_whisper import WhisperModel

audio, letra_path, out = sys.argv[1:4]
letra = open(letra_path, encoding="utf-8").read()


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-zñ0-9]", "", w)


# letra -> líneas (sin etiquetas [Chorus]) -> palabras
lineas = [l.strip() for l in letra.splitlines() if l.strip() and not l.strip().startswith("[")]
palabras = []  # (texto_original, indice_linea)
for i, l in enumerate(lineas):
    for w in l.split():
        if norm(w):
            palabras.append((w, i))

model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
pcm = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", audio, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                                    capture_output=True, check=True).stdout, np.float32)
segs, _ = model.transcribe(pcm, language="es", word_timestamps=True, vad_filter=False, beam_size=5,
                           initial_prompt=" ".join(lineas[:12]), condition_on_previous_text=False)
wh = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words if norm(w.word)]

a = [norm(w) for w, _ in palabras]
b = [norm(w) for w, _, _ in wh]
t_ini = [None] * len(a); t_fin = [None] * len(a)
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        t_ini[blk.a + k] = wh[blk.b + k][1]; t_fin[blk.a + k] = wh[blk.b + k][2]
emparejadas = sum(x is not None for x in t_ini)

# interpolación de huecos entre palabras emparejadas
idx = [i for i, x in enumerate(t_ini) if x is not None]
for i in range(len(a)):
    if t_ini[i] is None:
        prev = max([j for j in idx if j < i], default=None)
        nxt = min([j for j in idx if j > i], default=None)
        if prev is not None and nxt is not None:
            f = (i - prev) / (nxt - prev)
            t_ini[i] = t_fin[prev] + f * (t_ini[nxt] - t_fin[prev])
        elif prev is not None:
            t_ini[i] = t_fin[prev] + 0.3 * (i - prev)
        else:
            t_ini[i] = max(0.0, t_ini[nxt] - 0.3 * (nxt - i))
        t_fin[i] = t_ini[i] + 0.25

res = []
for i, l in enumerate(lineas):
    ws = [(palabras[k][0], t_ini[k], t_fin[k]) for k in range(len(palabras)) if palabras[k][1] == i]
    if ws:
        res.append({"text": l, "start": round(ws[0][1], 3), "end": round(ws[-1][2], 3),
                    "words": [[w, round(s, 3), round(e, 3)] for w, s, e in ws]})
json.dump({"audio": audio, "lineas": res, "emparejadas": emparejadas, "total": len(a),
           "whisper": [[w, round(s, 3), round(e, 3)] for w, s, e in wh]},
          open(out, "w"), ensure_ascii=False, indent=1)
print(f"✅ {out}: {emparejadas}/{len(a)} palabras emparejadas ({100*emparejadas/len(a):.0f}%)")
