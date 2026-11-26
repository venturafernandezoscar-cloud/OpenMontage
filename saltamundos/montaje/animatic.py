#!/usr/bin/env python3
"""SALTAMUNDOS · Animatic del Episodio 01 (maqueta con imágenes fijas).

Construye el episodio completo con la escaleta de la BIBLIA usando los fotogramas clave
(movimiento de cámara suave en cada imagen), las canciones elegidas, el jingle, el karaoke
sincronizado palabra a palabra y las escenas de física. Genera episodio_animatic.json y llama a montar.py.
Uso: python3 animatic.py [--preview]
"""
import json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
FOTOS = os.path.join(RAIZ, "fotogramas_jpg")
FIS = "/home/user/saltamundos/fisicas/salida"          # escenas de física renderizadas (.mov con transparencia)
CANC = os.path.join(RAIZ, "audio", "canciones")
JINGLE = os.path.join(RAIZ, "audio", "jingle_saltamundos.wav")

planos = json.load(open(os.path.join(RAIZ, "planos.json")))
por_id = {p["id"]: p for p in planos}


def foto(pid):
    p = por_id.get(pid, {})
    if "reusar" in p:
        pid = p["reusar"]
    f = os.path.join(FOTOS, pid + ".jpg")
    return f if os.path.exists(f) else None


def dur_audio(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)


clips, sfx, lyrics = [], [], []
t = 0.0


def bloque_imagenes(lista, inicio_audio=0.0):
    """lista: [(pid, t0, t1)] relativa al audio del bloque; rellena huecos con la imagen anterior."""
    global t
    base = t
    ultimo = None
    for pid, a, b in lista:
        f = foto(pid) or ultimo
        if f is None:
            continue
        clips.append({"file": os.path.relpath(f, AQUI), "duration": round(b - a, 3)})
        ultimo = f
        t = base + b
    return base


def letra(cancion_json, offset, desde=0.0, hasta=1e9, corrimiento=0.0):
    al = json.load(open(cancion_json))
    for ln in al["lineas"]:
        if ln["start"] < desde - 0.01 or ln["start"] >= hasta:
            continue
        ws = ln["words"]
        palabras = []
        for i, (w, s, e) in enumerate(ws):
            fin = ws[i + 1][1] if i + 1 < len(ws) else e
            palabras.append([w, max(0.08, fin - s)])
        lyrics.append({"start": round(offset + ln["start"] - corrimiento, 3), "words": palabras,
                       "end": round(offset + ln["end"] - corrimiento + 0.35, 3)})


# 1) INTRO 5 s (provisional: Tomi + los tres; la intro definitiva «Pipo salta las letras» se hará con GPU)
sfx.append({"file": JINGLE, "t": t, "gain": 0})
bloque_imagenes([("00_desfile_01", 0, 1.3), ("00_desfile_13", 1.3, 3.6), ("00_desfile_15", 3.6, 5.0)])

# 2) DESFILE sin palabras (45 s)
desfile = [p for p in planos if p["id"].startswith("00_desfile_")]
inicio = t
sfx.append({"file": os.path.join(CANC, "05_desfile_v2.mp3"), "t": inicio, "gain": 0})
bloque_imagenes([(p["id"], p["t0"], p["t1"]) for p in desfile])
clips[len(clips) - len(desfile)]["overlays"] = [{"file": os.path.join(FIS, "burbujas_intro.mov"), "t": 0.0}]

SALTOS = [("00_desfile_18", "salto al huerto"), ("02_burbujas_23", "salto a casa"),
          ("03_cepillo_24", "salto a la noche"), ("04_buenas_noches_19", "salto")]
CANCIONES = ["01_verdurita_v1", "02_burbujas_v2", "03_cepillo_v3", "04_buenas_noches_v2"]
for k, audio in enumerate(CANCIONES):
    # salto entre mundos (portal) con el jingle de marca
    sfx.append({"file": JINGLE, "t": t, "gain": -3})
    clips.append({"file": os.path.relpath(foto(SALTOS[k][0]), AQUI), "duration": 5.0, "fade_out": 0.5})
    t += 5.0
    cid = audio.rsplit("_v", 1)[0]
    mp3 = os.path.join(CANC, audio + ".mp3")
    sfx.append({"file": mp3, "t": t, "gain": 0})
    letra(os.path.join(CANC, audio + ".json"), t)
    lst = [(p["id"], p["t0"], p["t1"]) for p in planos if p["cancion"] == audio]
    n0 = len(clips)
    base = bloque_imagenes(lst)
    # física: plato arcoíris en «¡un arcoíris en mi plato!» y patitos en el puente de Burbujas
    for i, (pid, a, b) in enumerate(lst):
        if pid == "01_verdurita_19b":
            clips[n0 + i]["overlays"] = [{"file": os.path.join(FIS, "plato_arcoiris.mov"), "t": 0.0}]
        if pid == "02_burbujas_17":
            clips[n0 + i]["overlays"] = [{"file": os.path.join(FIS, "patitos.mov"), "t": 0.0}]
    t = base + dur_audio(mp3)
    clips[-1]["duration"] = round(clips[-1]["duration"] + (t - (base + lst[-1][2])), 3)

# 3) REMEZCLA bailable: estribillo final de «¡Verdurita, Sí!» con los mejores planos
v_al = json.load(open(os.path.join(CANC, "01_verdurita_v1.json")))
desde = v_al["lineas"][21]["start"] - 0.3
mp3 = os.path.join(CANC, "01_verdurita_v1.mp3")
hasta = dur_audio(mp3)
sfx.append({"file": mp3, "t": t, "gain": 0, "desde": desde})
letra(os.path.join(CANC, "01_verdurita_v1.json"), t, desde=desde, corrimiento=desde)
mejores = ["01_verdurita_05", "01_verdurita_08", "02_burbujas_12", "01_verdurita_13", "03_cepillo_13",
           "02_burbujas_13", "01_verdurita_07", "00_desfile_15", "03_cepillo_16", "01_verdurita_26"]
paso = (hasta - desde) / len(mejores)
for i, pid in enumerate(mejores):
    clips.append({"file": os.path.relpath(foto(pid), AQUI), "duration": round(paso, 3)})
t += hasta - desde

# 4) PANTALLA FINAL (20 s): los tres saludan + jingle
sfx.append({"file": JINGLE, "t": t + 0.5, "gain": -2})
clips.append({"file": os.path.relpath(foto("04_buenas_noches_06"), AQUI), "duration": 20.0, "fade_out": 1.5})
t += 20.0

# la pista de "música" es un silencio del largo total; todo lo demás entra como efectos en su segundo exacto
silencio = os.path.join(AQUI, "_silencio.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-t", f"{t:.3f}", silencio], check=True)
ep = {"fps": 30, "output": "../salida/episodio01_animatic.mp4", "music": "_silencio.wav", "sfx": sfx, "clips": clips, "lyrics": lyrics}
for s in ep["sfx"]:
    s["file"] = os.path.relpath(s["file"], AQUI)
for c in clips:
    for ov in c.get("overlays", []):
        ov["file"] = os.path.relpath(ov["file"], AQUI)
json.dump(ep, open(os.path.join(AQUI, "episodio_animatic.json"), "w"), ensure_ascii=False, indent=1)
os.makedirs(os.path.join(RAIZ, "salida"), exist_ok=True)
print(f"Animatic: {len(clips)} planos, {len(lyrics)} líneas de karaoke, duración {t/60:.1f} min")
subprocess.run([sys.executable, os.path.join(AQUI, "montar.py"), os.path.join(AQUI, "episodio_animatic.json"), *sys.argv[1:]], check=True)
