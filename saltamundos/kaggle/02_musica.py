# SALTAMUNDOS · Cuaderno 02 · Música y canciones (Kaggle, GPU T4)
# Modelo: ACE-Step 1.5 turbo (licencia MIT, uso comercial permitido, sin registro).
# Pega TODO en una celda de Kaggle (sesión nueva, GPU T4 x2, Internet ON) y pulsa ▶.
# 1) Instala (~8-12 min la primera vez)  2) PRUEBA RÁPIDA de 20 s  3) Genera 3 versiones de cada pista.

import subprocess, sys, os, json, time, glob, shutil
os.environ["MPLBACKEND"] = "Agg"  # Kaggle fija un backend de Jupyter que rompe matplotlib fuera del cuaderno

def sh(cmd, cwd=None):
    print(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True)
    if r.returncode != 0:
        print(r.stdout[-3000:]); print(r.stderr[-3000:])
        raise SystemExit(f"❌ Falló: {cmd}")
    return r.stdout

ACE = "/kaggle/working/ace"
OUT = "/kaggle/working/musica"
os.makedirs(OUT, exist_ok=True)

# ---------- 1. Instalación aislada (Python 3.12 + dependencias fijadas por ACE-Step) ----------
t0 = time.time()
sh(f"{sys.executable} -m pip install -q uv")
if not os.path.isdir(ACE):
    sh(f"git clone -q --depth 1 https://github.com/ace-step/ACE-Step-1.5.git {ACE}")
sh("uv sync --python 3.12", cwd=ACE)
print(f"✔ Instalado en {(time.time()-t0)/60:.1f} min")

# ---------- 2. Las canciones ----------
ESTILO = ("children's song, joyful nursery rhyme for toddlers, sweet clear cute young girl vocals singing in Spanish, "
          "kids choir on the chorus, ukulele, xylophone, marimba, glockenspiel, hand claps, soft bass, light playful drums, "
          "very catchy simple melody, bright major key, happy and warm, high quality studio production")

PISTAS = [
 {"id": "01_verdurita", "bpm": 120, "key": "C major", "dur": 130, "caption": ESTILO + ", bouncy and energetic, crunchy food sound vibe",
  "lyrics": """[Intro]

[Verse 1]
Tomi tiene hambre, ñam, ñam, ñam
Ve una piruleta, ¿y la va a tomar?
Lía trae zanahoria, crunch, crunch, crunch
Naranja y crujiente, ¡qué rica está!

[Chorus]
¡Verdurita, sí! ¡Verdurita, sí!
Me hace fuerte, me hace feliz
Brócoli, guisantes, ¡salto hasta el sol!
¡Verdurita, sí! ¡Con todo mi corazón!

[Verse 2]
Pipo encuentra un brócoli, ¡un arbolito es!
Lía come guisantes, ¡uno, dos y tres!
Tomi prueba un trocito, ¿le gustará?
Mmm... ¡otra vez!

[Chorus]
¡Verdurita, sí! ¡Verdurita, sí!
Me hace fuerte, me hace feliz
Brócoli, guisantes, ¡salto hasta el sol!
¡Verdurita, sí! ¡Con todo mi corazón!

[Bridge]
Rojo, el tomate, naranja, la zanahoria
Verde, el brócoli, morada, la berenjena
Amarillo, el maíz, ¡un arcoíris en mi plato!

[Pre-Chorus]
¿Y los caramelos? ¡Un poquito nada más!
¡De vez en cuando, y a saltar!

[Chorus - key change up]
¡Verdurita, sí! ¡Verdurita, sí!
Me hace fuerte, me hace feliz
Brócoli, guisantes, ¡salto hasta el sol!
¡Verdurita, sí! ¡Con todo mi corazón!

[Outro]"""},
 {"id": "02_burbujas", "bpm": 120, "key": "G major", "dur": 105, "caption": ESTILO + ", splashy bath time fun",
  "lyrics": """[Intro]

[Verse 1]
Tomi va al baño, chap, chap, chap
Lía abre el agua, splash, splash, splash
Pipo trae el pato, cuac, cuac, cuac
¡La bañera está lista ya!

[Chorus]
Burbujas, burbujas, suben al sol
Burbujas, burbujas, de todo color
¡Pop! en la nariz, ¡pop! en los pies
¡Burbujas, burbujas, una, dos y tres!

[Verse 2]
Tomi se lava la carita así
Lía le lava el pelito, ji, ji, ji
Pipo se sacude, shh, shh, shh
¡Y todos mojados, ja, ja, ja!

[Chorus]
Burbujas, burbujas, suben al sol
Burbujas, burbujas, de todo color
¡Pop! en la nariz, ¡pop! en los pies
¡Burbujas, burbujas, una, dos y tres!

[Bridge]
¡Patitos al agua! Uno, dos, tres, cuatro... ¡y cinco!

[Chorus]
Burbujas, burbujas, suben al sol
Burbujas, burbujas, de todo color
¡Pop! en la nariz, ¡pop! en los pies
¡Burbujas, burbujas, una, dos y tres!

[Outro]
Ya estamos limpios, ¡adiós, a dormir!"""},
 {"id": "03_cepillo", "bpm": 118, "key": "F major", "dur": 120, "caption": ESTILO + ", shaker maracas rhythm like a toothbrush",
  "lyrics": """[Intro]

[Verse 1]
Tomi comió un dulce, ¡qué rico fue!
Pero en sus dientes, ¿qué es lo que ves?
Azuquitos pegajosos, ji, ji, ji
¡Lía trae el cepillo, ya están aquí!

[Chorus]
Cepillo, cepillo, arriba y abajo, chuf, chuf
Cepillo, cepillo, de lado a lado, chuf, chuf
Circulitos, circulitos, ¡brillan como el sol!
¡Una sonrisa grande, grande, como mi corazón!

[Verse 2]
Pipo quiere cepillo, guau, guau, guau
Lía le enseña cómo, ¡mira qué bien!
Un poquito de pasta, como un guisante es
¡Y a contar cepillando: uno, dos y tres!

[Chorus]
Cepillo, cepillo, arriba y abajo, chuf, chuf
Cepillo, cepillo, de lado a lado, chuf, chuf
Circulitos, circulitos, ¡brillan como el sol!
¡Una sonrisa grande, grande, como mi corazón!

[Bridge]
Agua en la boquita, gluglú, gluglú
Escupe en el lavabo, ptú, ptú, ptú
¿Y los azuquitos? ¡Adiós, adiós!

[Chorus - key change up]
Cepillo, cepillo, arriba y abajo, chuf, chuf
Cepillo, cepillo, de lado a lado, chuf, chuf
Circulitos, circulitos, ¡brillan como el sol!
¡Una sonrisa grande, grande, como mi corazón!

[Outro]"""},
 {"id": "04_buenas_noches", "bpm": 80, "key": "D major", "dur": 105,
  "caption": ("gentle children's lullaby, soft sweet young girl vocals singing in Spanish, whispery kids choir, "
              "ukulele arpeggios, music box, celesta, warm pad, calm, dreamy, soothing bedtime song, slow, high quality"),
  "lyrics": """[Intro - music box]

[Verse 1]
Ya se esconde el sol, la luna sale ya
Tomi se pone el pijama, ¡qué suave está!

[Chorus]
Buenas noches, Saltamundos, a soñar
Mañana otro mundo nos va a esperar
Cierra los ojitos, uno, dos
Buenas noches, buenas noches, adiós

[Verse 2]
Lía lee un cuento de estrellas y de mar
Pipo se acurruca, ya empieza a bostezar

[Chorus]
Buenas noches, Saltamundos, a soñar
Mañana otro mundo nos va a esperar
Cierra los ojitos, uno, dos
Buenas noches, buenas noches, adiós

[Bridge]
Un abrazo grande, un besito al final
La lucecita se apaga... shhh

[Chorus - softer]
Buenas noches, Saltamundos, a soñar
Mañana otro mundo nos va a esperar
Cierra los ojitos, uno, dos
Buenas noches, buenas noches, adiós

[Outro - music box fades]"""},
 {"id": "05_desfile", "bpm": 120, "key": "C major", "dur": 45, "instrumental": True,
  "caption": ("instrumental children's theme, bouncy and magical, ukulele, xylophone, marimba, glockenspiel sparkles, "
              "hand claps, kids giggles, playful pizzicato, bright major key, catchy whistleable melody, no vocals"),
  "lyrics": "[Instrumental]"},
 {"id": "06_jingle", "bpm": 120, "key": "C major", "dur": 10,
  "caption": ("short catchy children's TV channel jingle, cheerful kids choir chanting the channel name, xylophone, bells, "
              "bouncy, sparkling, very short logo sting"),
  "lyrics": "[Chorus]\n¡Sal-ta-mun-dos!\n¡Sal-ta-mun-dos!"},
]
json.dump(PISTAS, open(f"{OUT}/pistas.json", "w"), ensure_ascii=False, indent=1)

# ---------- 3. Script que corre dentro del entorno de ACE-Step ----------
GEN = r'''
import json, os, sys, time, shutil
sys.path.insert(0, os.getcwd())
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music

# La T4 (pre-Ampere) haría que ACE-Step use float16, que se desborda (NaN) en canciones largas.
# Forzamos bfloat16 (mismo rango que float32; PyTorch lo emula en la T4: algo más lento pero estable).
if os.environ.get("ACE_FP16") != "1":
    import acestep.gpu_config as _g
    import acestep.core.generation.handler.memory_utils as _m
    _g.cuda_supports_bfloat16 = lambda *a, **k: True
    _m.cuda_supports_bfloat16 = lambda *a, **k: True

OUT, modo = sys.argv[1], sys.argv[2]
pistas = json.load(open(os.path.join(OUT, "pistas.json")))
dit = AceStepHandler()
msg, ok = dit.initialize_service(project_root=os.getcwd(), config_path="acestep-v15-turbo",
                                 device="cuda", offload_to_cpu=False)
if not ok: sys.exit("DiT: " + msg)
print("DiT: dtype " + str(dit.dtype), flush=True)
llm = LLMHandler()
usar_lm = os.environ.get("ACE_SIN_LM") != "1"
if usar_lm:
    try:
        msg, ok = llm.initialize(checkpoint_dir=os.path.join(os.getcwd(), "checkpoints"),
                                 lm_model_path=os.environ.get("ACE_LM", "acestep-5Hz-lm-1.7B"),
                                 backend="pt", device="cuda", offload_to_cpu=True)
    except Exception as e:
        ok, msg = False, repr(e)
    if not ok:
        print("AVISO: el planificador LM no cargó, sigo solo con DiT: " + str(msg)[:300], flush=True)
        usar_lm = False

trabajos = []
if modo == "prueba":
    p = dict(pistas[4]); p["id"], p["dur"] = "00_prueba", 60
    trabajos = [(p, 7)]
else:
    VARIANTES = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    trabajos = [(p, 100 + v) for p in pistas for v in range(VARIANTES)]

for p, seed in trabajos:
    t0 = time.time()
    params = GenerationParams(task_type="text2music", thinking=usar_lm, caption=p["caption"], lyrics=p["lyrics"],
                              instrumental=p.get("instrumental", False), vocal_language="es", bpm=p["bpm"],
                              keyscale=p["key"], timesignature="4", duration=p["dur"],
                              inference_steps=8, shift=3.0, seed=seed, use_cot_caption=False)
    cfg = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[seed], audio_format="wav")
    tmp = os.path.join(OUT, "_tmp"); os.makedirs(tmp, exist_ok=True)
    r = generate_music(dit, llm, params, cfg, save_dir=tmp)
    if not r.success:
        print(f"FALLO {p['id']} seed {seed}: {r.error or r.status_message}", flush=True); continue
    dst = os.path.join(OUT, f"{p['id']}_v{seed-100+1 if seed >= 100 else 0}.wav")
    shutil.move(r.audios[0]["path"], dst)
    print(f"OK {os.path.basename(dst)}  ({time.time()-t0:.0f} s)", flush=True)
'''
open(f"{ACE}/gen_saltamundos.py", "w").write(GEN)

def generar(modo, *extra):
    p = subprocess.Popen(["uv", "run", "--python", "3.12", "python", "gen_saltamundos.py", OUT, modo, *extra],
                         cwd=ACE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    cola = []
    for line in p.stdout:
        cola = (cola + [line])[-40:]
        if line.startswith(("OK ", "FALLO", "DiT:", "AVISO")) or "Downloading" in line:
            print(line.rstrip(), flush=True)
    if p.wait() != 0:
        print("".join(cola)); raise SystemExit("❌ La generación ha fallado (arriba, las últimas líneas).")

from IPython.display import Audio, display, Markdown

# ---------- 4. PRUEBA RÁPIDA (60 s) ----------
print("\n▶ PRUEBA RÁPIDA (descarga modelos ~10 GB la primera vez)...")
t0 = time.time(); generar("prueba")
print(f"✔ Prueba OK en {(time.time()-t0)/60:.1f} min. Escúchala:")
display(Audio(f"{OUT}/00_prueba_v0.wav"))

# ---------- 5. TANDA COMPLETA: 3 versiones de cada pista ----------
print("\n▶ TANDA COMPLETA (6 pistas x 3 versiones)...")
t0 = time.time(); generar("todo", "3")
print(f"✔ Terminado en {(time.time()-t0)/60:.1f} min\n")
for p in PISTAS:
    display(Markdown(f"### {p['id']}"))
    for f in sorted(glob.glob(f"{OUT}/{p['id']}_v*.wav")):
        display(Markdown(f"**{os.path.basename(f)}**")); display(Audio(f))
shutil.make_archive("/kaggle/working/saltamundos_musica", "zip", OUT)
print("🎉 Escucha cada versión y dime cuál te gusta más de cada canción (p. ej. 01_verdurita_v2).")
