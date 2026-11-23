# SALTAMUNDOS · Cuaderno 03 · Fotogramas clave con personajes consistentes (Kaggle, GPU T4)
# Modelo: Qwen-Image-Edit-2509 (Apache 2.0) + Lightning 4 pasos (Apache 2.0), en ComfyUI.
# Recibe hasta 3 imágenes de referencia (las hojas oficiales) y coloca a los personajes en cada escena.
# Requisitos: sesión GPU T4 x2, Internet ON, y el dataset "saltamundos-hojas" añadido (Add Input).
# 1) Instala (~5 min)  2) Descarga modelos (~20 GB, ~5 min)  3) PRUEBA: 6 planos x 2 versiones.

import os, sys, glob, json, time, subprocess, urllib.request, uuid, shutil
os.environ["MPLBACKEND"] = "Agg"

COMFY = "/tmp/comfy"                     # fuera de /kaggle/working (límite de 20 GB)
OUT = "/kaggle/working/fotogramas"
os.makedirs(OUT, exist_ok=True)


def sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True)
    if r.returncode != 0:
        print(r.stdout[-2000:]); print(r.stderr[-2000:]); raise SystemExit(f"❌ Falló: {cmd}")


# ---------- 1. Hojas oficiales (dataset subido) ----------
ELEGIDAS = {"tomi": "tomi_giro_2_", "tomi_caras": "tomi_expresiones_1_", "lia": "lia_giro_2_",
            "lia_caras": "lia_expresiones_1_", "pipo": "pipo_giro_1_", "pipo_caras": "pipo_expresiones_2_"}
REF = {}
for k, pref in ELEGIDAS.items():
    m = glob.glob(f"/kaggle/input/**/{pref}*.png", recursive=True)
    if not m:
        raise SystemExit(f"❌ No encuentro la hoja '{pref}*.png'. ¿Has añadido el dataset saltamundos-hojas con 'Add Input'?")
    REF[k] = m[0]
print("✔ Hojas oficiales encontradas:", ", ".join(REF))

# ---------- 2. ComfyUI + modelos ----------
t0 = time.time()
if not os.path.isdir(COMFY):
    sh(f"git clone -q --depth 1 https://github.com/comfyanonymous/ComfyUI.git {COMFY}")
    sh(f"git clone -q --depth 1 https://github.com/city96/ComfyUI-GGUF.git {COMFY}/custom_nodes/ComfyUI-GGUF")
    req = [l for l in open(f"{COMFY}/requirements.txt").read().split("\n") if l and not l.startswith(("torch", "#"))]
    open("/tmp/req.txt", "w").write("\n".join(req))
    sh(f"{sys.executable} -m pip install -q -r /tmp/req.txt -r {COMFY}/custom_nodes/ComfyUI-GGUF/requirements.txt")

HF = "https://huggingface.co"
MODELOS = {
    "unet/qwen_edit_2509_Q4_K_M.gguf": f"{HF}/QuantStack/Qwen-Image-Edit-2509-GGUF/resolve/main/Qwen-Image-Edit-2509-Q4_K_M.gguf",
    "text_encoders/Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf": f"{HF}/unsloth/Qwen2.5-VL-7B-Instruct-GGUF/resolve/main/Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf",
    "text_encoders/Qwen2.5-VL-7B-Instruct-mmproj-F16.gguf": f"{HF}/unsloth/Qwen2.5-VL-7B-Instruct-GGUF/resolve/main/mmproj-F16.gguf",
    "vae/qwen_image_vae.safetensors": f"{HF}/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors",
    "loras/qwen_edit_2509_lightning_4steps.safetensors": f"{HF}/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors",
}
for rel, url in MODELOS.items():
    dst = f"{COMFY}/models/{rel}"
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        sh(f"curl -sSfL -o {dst}.part '{url}' && mv {dst}.part {dst}")
print(f"✔ ComfyUI y modelos listos en {(time.time()-t0)/60:.1f} min")

for k, p in REF.items():
    shutil.copy(p, f"{COMFY}/input/ref_{k}.png")

# ---------- 3. Servidor ComfyUI ----------
srv = subprocess.Popen([sys.executable, "main.py", "--port", "8188", "--disable-auto-launch"], cwd=COMFY,
                       stdout=open("/tmp/comfy.log", "w"), stderr=subprocess.STDOUT)


def api(path, data=None):
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request("http://127.0.0.1:8188" + path, data=body, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=60).read())


for _ in range(200):
    try:
        api("/system_stats"); break
    except Exception:
        time.sleep(3)
else:
    print(open("/tmp/comfy.log").read()[-3000:]); raise SystemExit("❌ ComfyUI no arrancó")

ESTILO = ("3D animated children's cartoon, premium feature-film CGI quality, soft global illumination, warm subsurface "
          "skin, big glossy expressive eyes, vibrant pastel-bright colors, cheerful cozy mood, 16:9 cinematic frame")
NOMBRES = {"tomi": "Tomi (the baby boy with golden-blond curly hair and mint-green overalls)",
           "lia": "Lia (the girl with two curly hair puffs and the purple polka-dot dress)",
           "pipo": "Pipo (the corgi puppy with the red bandana)"}


def flujo(refs, escena, seed, prefijo, ancho=1344, alto=768):
    pics = " ".join(f"Picture {i+1} shows {NOMBRES[r.split('_')[0]]}." for i, r in enumerate(refs))
    texto = (f"{pics} Keep each character exactly identical to the reference pictures: same face, hair, outfit and "
             f"colors. Create a new image: {escena}. {ESTILO}.")
    f = {
        "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": "qwen_edit_2509_Q4_K_M.gguf"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "qwen_edit_2509_lightning_4steps.safetensors", "strength_model": 1.0}},
        "3": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["2", 0], "shift": 3.0}},
        "4": {"class_type": "CFGNorm", "inputs": {"model": ["3", 0], "strength": 1.0}},
        "5": {"class_type": "CLIPLoaderGGUF", "inputs": {"clip_name": "Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf", "type": "qwen_image"}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "20": {"class_type": "EmptySD3LatentImage", "inputs": {"width": ancho, "height": alto, "batch_size": 1}},
    }
    pos = {"clip": ["5", 0], "prompt": texto, "vae": ["6", 0]}
    neg = {"clip": ["5", 0], "prompt": "", "vae": ["6", 0]}
    for i, r in enumerate(refs):
        f[str(10 + i)] = {"class_type": "LoadImage", "inputs": {"image": f"ref_{r}.png"}}
        pos[f"image{i+1}"] = [str(10 + i), 0]; neg[f"image{i+1}"] = [str(10 + i), 0]
    f["21"] = {"class_type": "TextEncodeQwenImageEditPlus", "inputs": pos}
    f["22"] = {"class_type": "TextEncodeQwenImageEditPlus", "inputs": neg}
    f["23"] = {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["21", 0], "negative": ["22", 0],
               "latent_image": ["20", 0], "seed": seed, "steps": 4, "cfg": 1.0, "sampler_name": "euler",
               "scheduler": "simple", "denoise": 1.0}}
    f["24"] = {"class_type": "VAEDecode", "inputs": {"samples": ["23", 0], "vae": ["6", 0]}}
    f["25"] = {"class_type": "SaveImage", "inputs": {"images": ["24", 0], "filename_prefix": prefijo}}
    return f


def generar(refs, escena, seed, nombre):
    r = api("/prompt", {"prompt": flujo(refs, escena, seed, nombre), "client_id": uuid.uuid4().hex})
    if r.get("node_errors"):
        raise SystemExit(f"❌ Error en el flujo: {r['node_errors']}")
    pid = r["prompt_id"]
    while True:
        h = api(f"/history/{pid}")
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                print(open("/tmp/comfy.log").read()[-3000:]); raise SystemExit("❌ ComfyUI falló (arriba el detalle)")
            im = [i for o in h[pid]["outputs"].values() for i in o.get("images", [])][0]
            dst = f"{OUT}/{nombre}.png"
            shutil.copy(os.path.join(COMFY, "output", im.get("subfolder", ""), im["filename"]), dst)
            return dst
        time.sleep(2)


# ---------- 4. PRUEBA: 6 planos representativos x 2 versiones ----------
PLANOS = json.loads(os.environ.get("SALTA_PLANOS", "null")) or [
    ["desfile_tomi", ["tomi", "tomi_caras"], "Tomi sits on a colorful flower meadow at sunrise, a soap bubble has just popped around him, he looks surprised and delighted straight at the camera, medium shot"],
    ["desfile_lia", ["lia", "lia_caras"], "Lia twirls like a ballerina on a colorful flower meadow with floating soap bubbles, joyful, full body shot"],
    ["desfile_pipo", ["pipo", "pipo_caras"], "Pipo happily chases his own tail in circles on a flower meadow, playful, top-down three-quarter view"],
    ["verdurita_zanahoria", ["tomi", "lia"], "in a magical vegetable garden with giant shiny smiling vegetables, Lia hands a bright orange carrot to Tomi who reaches for it with a big smile, warm golden sunlight, medium two-shot"],
    ["burbujas_banera", ["tomi", "lia", "pipo"], "Tomi sits in a bathtub full of rainbow foam bubbles blowing a big bubble, Lia kneels beside the tub laughing, Pipo holds a yellow rubber duck in his mouth, bright cozy bathroom with colorful tiles"],
    ["noches_cama", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo snuggle sleepily in a cozy bed under a blanket, Tomi in blue star pajamas yawning, soft lilac night sky with a smiling moon through the window, pastel lavender and warm gold light"],
]
from IPython.display import Image as IImage, display, Markdown
print(f"\n▶ PRUEBA: {len(PLANOS)} planos x 2 versiones")
t0 = time.time()
for nombre, refs, escena in PLANOS:
    for v, seed in enumerate([11, 22], start=1):
        p = generar(refs, escena, seed, f"{nombre}_v{v}")
        print(f"✔ {nombre}_v{v}  ({(time.time()-t0)/60:.1f} min)", flush=True)
    display(Markdown(f"### {nombre}"))
    for v in (1, 2):
        display(IImage(f"{OUT}/{nombre}_v{v}.png", width=640))
srv.terminate()
print("\n🎉 Mira cada plano y dime si los personajes se parecen a sus hojas (y qué versión prefieres).")
