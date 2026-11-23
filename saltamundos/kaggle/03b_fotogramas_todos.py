# SALTAMUNDOS · Cuaderno 03b · TODOS los fotogramas clave del Episodio 01 (Kaggle, GPU T4 x2)
# Modelo: Qwen-Image-Edit-2509 (Apache 2.0) + Lightning 4 pasos (Apache 2.0), en ComfyUI.
# Recibe hasta 3 imágenes de referencia (las hojas oficiales) y coloca a los personajes en cada escena.
# Requisitos: sesión GPU T4 x2, Internet ON, y el dataset "saltamundos-hojas" añadido (Add Input).
# Usa las 2 GPU a la vez. Si se corta, vuelve a pulsar ▶: retoma donde lo dejó (no repite planos hechos).
# Activa Session options → Persistence → Files only para conservar las imágenes entre sesiones.

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
    # se respeta el torch con CUDA que ya trae Kaggle; el resto (torchsde incluido) se instala
    req = [l for l in open(f"{COMFY}/requirements.txt").read().split("\n")
           if l and not l.startswith("#") and l.split("=")[0].split(">")[0].strip() not in ("torch", "torchvision", "torchaudio")]
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


# ---------- 3. Dos servidores ComfyUI (uno por GPU) ----------
import threading
PUERTOS = [8188, 8189]
srvs = [subprocess.Popen([sys.executable, "main.py", "--port", str(pt), "--cuda-device", str(i), "--disable-auto-launch",
                          "--output-directory", f"/tmp/comfy_out{i}"], cwd=COMFY,
                         stdout=open(f"/tmp/comfy{i}.log", "w"), stderr=subprocess.STDOUT) for i, pt in enumerate(PUERTOS)]


def api(pt, path, data=None):
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(f"http://127.0.0.1:{pt}" + path, data=body, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=60).read())


for i, pt in enumerate(PUERTOS):
    for _ in range(200):
        try:
            api(pt, "/system_stats"); break
        except Exception:
            time.sleep(3)
    else:
        print(open(f"/tmp/comfy{i}.log").read()[-3000:]); raise SystemExit("ComfyUI no arranco")

ESTILO = ("3D animated children's cartoon, premium feature-film CGI quality, soft global illumination, warm subsurface "
          "skin, big glossy expressive eyes, vibrant pastel-bright colors, cheerful cozy mood, 16:9 cinematic frame")
NOMBRES = {"tomi": "Tomi (the baby boy with a thick fluffy mop of golden-blond curls covering his whole head, mint-green overalls with a yellow sun patch)",
           "lia": "Lia (the girl with two curly hair puffs and the purple polka-dot dress)",
           "pipo": "Pipo (the corgi puppy with the red bandana)"}


def flujo(refs, escena, seed, prefijo, ancho=1024, alto=576):
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



def generar(gpu, refs, escena, seed, nombre):
    pt = PUERTOS[gpu]
    r = api(pt, "/prompt", {"prompt": flujo(refs, escena, seed, nombre), "client_id": uuid.uuid4().hex})
    if r.get("node_errors"):
        raise RuntimeError(f"Error en el flujo: {r['node_errors']}")
    pid = r["prompt_id"]
    while True:
        h = api(pt, f"/history/{pid}")
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                raise RuntimeError(open(f"/tmp/comfy{gpu}.log").read()[-1500:])
            im = [i for o in h[pid]["outputs"].values() for i in o.get("images", [])][0]
            shutil.copy(os.path.join(f"/tmp/comfy_out{gpu}", im.get("subfolder", ""), im["filename"]), f"{OUT}/{nombre}.png")
            return
        time.sleep(2)


PLANOS = json.loads(r"""[["00_desfile_00", [], "three colorful soap bubbles (mint green, purple and orange) slowly falling from the sky over the meadow, wide shot, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_01", ["tomi", "tomi_caras"], "the mint-green bubble pops and Tomi sits on the grass looking surprised, medium shot, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_02", ["tomi", "tomi_caras"], "Tomi looks at his hands and claps happily, close-up, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_03", ["tomi"], "Tomi crawls fast toward the camera, low ground-level shot, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_04", ["tomi"], "Tomi stands up wobbly and does a proud triumphant pose, low angle, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_05", ["lia"], "the purple bubble lands and Lia spins out of it like a ballerina, medium shot, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_06", ["lia"], "Lia does three little hops, her hair puffs bouncing, full body, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_07", ["lia", "lia_caras"], "Lia raises her index finger with a bright 'I know!' face and a little sparkle star appears, close-up, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_08", ["lia"], "Lia waves at the camera with both hands, front view, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_09", [], "an orange soap bubble bouncing on the grass without popping, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_10", ["pipo"], "the orange bubble pops and Pipo lands on his bottom looking surprised, low shot, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_11", ["pipo"], "Pipo chases his own tail in circles, top-down view, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_12", ["pipo", "pipo_caras"], "Pipo, a bit dizzy, stops and tilts his head at the camera, close-up, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_13", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo meet in the middle of the meadow and look at each other, wide shot, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_14", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo share a big group hug with heart-shaped bubbles around them, medium shot, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_15", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo dance together clapping, spinning and jumping, full body, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_16", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo dance in a circle of flowers that sway with them, top-down, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_17", ["tomi", "lia"], "Tomi rubs his rumbling tummy and Lia points far away at a glowing vegetable garden, medium shot, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["00_desfile_18", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo run toward a giant iridescent soap-bubble portal opening in the meadow, wide shot from behind, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"], ["01_verdurita_00", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo land on a giant bouncy lettuce leaf and look around amazed, wide shot, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_01a", ["tomi", "tomi_caras"], "Tomi rubs his tummy with a funny hungry face, close-up, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_01b", ["tomi", "tomi_caras"], "Tomi opens and closes his mouth 'nom nom nom', extreme close-up, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_02", ["tomi"], "a giant rainbow lollipop shines among the plants, Tomi reaches out his hand toward it, medium shot, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_03a", ["lia"], "Lia arrives holding a bright shiny carrot, three-quarter medium shot, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_03b", ["lia", "lia_caras"], "Lia bites the carrot, little orange crumbs flying in slow motion, close-up, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_04", ["tomi", "lia"], "Lia hands the carrot to Tomi who bites it with full cheeks and a big smile, two-shot, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_05", ["tomi"], "Tomi glows with a soft green aura and jumps very high, low angle, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_06a", ["lia"], "Lia lifts a giant pumpkin with one finger as a funny gag, full body, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_06b", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo put their hands on their hearts and smile, front view, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_07", ["tomi"], "Tomi leaps up among fluffy clouds toward a smiling sun, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_08", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo dance clapping with heart-shaped bubbles around, medium shot, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_09a", ["pipo"], "Pipo sniffs and pops his head out of the leaves holding a broccoli, low ground shot, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_09b", ["pipo"], "the broccoli grows into a little tree and Pipo sits under it, low angle, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_10", ["lia"], "Lia opens a pea pod and three peas jump out, close-up of hands, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_11", ["tomi", "tomi_caras"], "Tomi brings a broccoli floret to his mouth with a doubtful face, close-up, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_12", ["tomi", "tomi_caras"], "Tomi's eyes light up with delight and he claps asking for more, front view, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_13", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo bounce on giant pumpkins like trampolines, wide shot, a bright sunflower field with giant pumpkins, blue sky, warm sunlight"], ["01_verdurita_14", ["tomi", "lia"], "Tomi and Lia run hand in hand through tall sunflowers, side tracking shot, a bright sunflower field with giant pumpkins, blue sky, warm sunlight"], ["01_verdurita_15", ["tomi"], "Tomi jumps over a giant pumpkin toward the sun, low angle, a bright sunflower field with giant pumpkins, blue sky, warm sunlight"], ["01_verdurita_16", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo strike a happy pose with arms up among sunflowers, front, a bright sunflower field with giant pumpkins, blue sky, warm sunlight"], ["01_verdurita_17a", ["tomi", "lia"], "a giant red tomato rolls past Tomi and Lia, the scene tinted warm red, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_17b", ["pipo"], "orange carrots pop up out of the ground around Pipo, low shot, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_18a", [], "broccoli trees sway in the breeze, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_18b", ["lia"], "Lia in her purple dress stands next to a giant eggplant of the same color and laughs, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_19a", ["pipo"], "a corn cob pops popcorn that rains on Pipo, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_19b", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo look at a plate full of rainbow vegetables with amazement, top-down, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_20", ["tomi", "lia"], "a rainbow lollipop reappears and Lia breaks off a tiny piece for Tomi, medium two-shot, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_21", ["lia", "lia_caras"], "Lia raises her index finger with a wise smile while a giant bubble portal opens in the sky behind her, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["01_verdurita_26", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo jump into the swirling bubble portal in slow motion, Tomi winks at the camera, a magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm golden sunlight"], ["02_burbujas_00", ["tomi"], "Tomi crawls along a sunny hallway toward the bathroom door, ground-level shot"], ["02_burbujas_01a", ["tomi"], "Tomi walks wobbly toward the bathtub, medium side shot, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_01b", ["tomi"], "Tomi's little feet stomp in three tiny puddles on the tiles, close-up, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_02a", ["lia"], "Lia turns the faucet with both hands, three-quarter shot, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_02b", [], "water gushes into the bathtub with sparkling splashes, slow motion close-up, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_03a", ["pipo"], "Pipo trots in with a yellow rubber duck in his mouth, low shot, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_03b", ["pipo"], "Pipo squeezes the rubber duck, close-up, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_04", ["tomi", "lia"], "Lia lifts Tomi into the bathtub full of foam, Tomi raises his arms with joy, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_05a", ["tomi", "tomi_caras"], "Tomi blows and five giant soap bubbles come out, close-up, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_05b", [], "giant soap bubbles rise toward a window with golden light, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_06a", ["tomi", "lia"], "Tomi and Lia clap and more bubbles appear, two-shot, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_06b", [], "a macro shot of rainbow-colored soap bubbles with shallow depth of field, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_07a", ["tomi", "tomi_caras"], "a bubble pops on Tomi's nose and he goes cross-eyed, extreme close-up, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_07b", ["tomi"], "a bubble pops on Tomi's feet sticking out of the foam, close-up, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_08", ["tomi", "lia"], "Tomi and Lia sway left and right in the bath counting on their fingers, front, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_09", ["tomi", "tomi_caras"], "Tomi rubs his cheeks with a yellow sponge, eyes closed, close-up, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_10", ["tomi", "lia"], "Lia shapes Tomi's foamy hair into a funny little horn while he giggles, two-shot, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_11", ["pipo"], "wet Pipo shakes himself, water drops flying in slow motion, wide shot, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_12", ["tomi", "lia", "pipo"], "Tomi and Lia soaked with open mouths while Pipo spins happily, wide shot, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_13", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo blow glowing bubbles in the backyard at dusk, wide shot, a backyard at dusk with glowing fluorescent soap bubbles floating in the air, fairy lights"], ["02_burbujas_14", ["tomi", "lia"], "Tomi and Lia chase glowing bubbles, top-down shot, a backyard at dusk with glowing fluorescent soap bubbles floating in the air, fairy lights"], ["02_burbujas_15", ["tomi"], "a glowing bubble pops on Tomi's nose, close-up, a backyard at dusk with glowing fluorescent soap bubbles floating in the air, fairy lights"], ["02_burbujas_16", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo count to three with fingers under fairy lights, front, a backyard at dusk with glowing fluorescent soap bubbles floating in the air, fairy lights"], ["02_burbujas_17", ["lia"], "Lia tips a basket of rubber ducks from above the bathtub, low angle, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_22", ["tomi", "lia", "pipo"], "Lia wraps Tomi in a duck hooded towel, all three wave goodbye sleepily, warm light, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["02_burbujas_23", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo jump into a glowing bubble portal wrapped in towels, laughing, a bright cozy bathroom with colorful tiles and a bathtub full of rainbow foam bubbles, rubber ducks, golden window light"], ["03_cepillo_00", ["tomi"], "Tomi climbs onto his little step stool and looks at the mirror, over-the-shoulder shot, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_01", ["tomi", "tomi_caras"], "Tomi licks his lips happily remembering a candy, close-up, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_02", ["tomi", "tomi_caras"], "Tomi smiles wide at the mirror showing his two little teeth, close-up through the mirror, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_03", [], "tiny cute purple sticky blobs with funny faces dance on two white baby teeth, macro shot, a magical world of soft white tooth-shaped hills and minty foam clouds, playful and clean, seen through a mirror"], ["03_cepillo_04", ["lia"], "Lia arrives holding two colorful toothbrushes up like superheroes, low angle, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_05", ["tomi"], "Tomi brushes his teeth up and down with a mint toothbrush, front view through mirror, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_06", ["tomi", "lia"], "Tomi and Lia brush their teeth side to side in sync, two-shot, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_07", ["tomi", "tomi_caras"], "Tomi brushes in little circles with minty foam clouds around, close-up, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_08", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo show big shiny smiles with sparkles, medium shot, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_09", ["pipo"], "Pipo appears with a toothbrush in his mouth wagging his tail, low shot, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_10", ["lia", "pipo"], "Lia gently brushes Pipo's teeth and Pipo smiles with shiny teeth, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_11", [], "a pea-sized dab of toothpaste squeezed onto a toothbrush next to a green pea, macro top-down, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_12", ["tomi", "lia"], "Tomi and Lia brush counting one, two, three, front view, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_13", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo brush their teeth dancing on soft white tooth-shaped hills, a magical world of soft white tooth-shaped hills and minty foam clouds, playful and clean, seen through a mirror"], ["03_cepillo_14", ["tomi", "lia"], "Tomi and Lia slide down a minty foam cloud laughing, a magical world of soft white tooth-shaped hills and minty foam clouds, playful and clean, seen through a mirror"], ["03_cepillo_15", ["tomi"], "Tomi holds up his toothbrush like a magic wand, sparkles everywhere, a magical world of soft white tooth-shaped hills and minty foam clouds, playful and clean, seen through a mirror"], ["03_cepillo_16", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo jump with big shiny smiles among sparkles, a magical world of soft white tooth-shaped hills and minty foam clouds, playful and clean, seen through a mirror"], ["03_cepillo_17", ["tomi", "tomi_caras"], "Tomi gargles with puffed cheeks holding a colorful cup, close-up, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_18", ["tomi"], "Tomi leans over the sink and spits, the little purple blobs slide down the drain like a water slide, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_19", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo wave goodbye to the tiny friendly purple blobs at the drain, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["03_cepillo_24", ["tomi", "tomi_caras"], "Tomi shows his shiny smile to the camera and winks while a bubble portal to the night opens behind him, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"], ["04_buenas_noches_00", [], "a bubble portal slowly opens in Tomi's bedroom at sunset, wide shot, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_01", [], "a sleepy sun yawns and sets behind the hills while the smiling moon rises and stars light up one by one, view through the window, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_02", ["tomi", "lia"], "Lia helps Tomi put on blue star pajamas, Tomi hugs his soft sleeve, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_03", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo sway sleepily on a cloud-like bed while stars float down, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_04", [], "silhouettes of the meadow, the vegetable garden and the bathtub projected softly on the starry ceiling, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_05", ["tomi", "tomi_caras"], "Tomi closes one eye and then the other, extreme close-up, soft light, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_06", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo wave very softly to the camera from the bed, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_07", ["lia"], "Lia opens a storybook and glowing fish and stars swim out into the room, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_08", ["tomi", "lia", "pipo"], "Pipo curls into a ball, then Pipo, Tomi and Lia yawn one after another, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_13", ["tomi", "lia", "pipo"], "Lia hugs Tomi and Pipo joins in, a heart of light glows above them, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_14", ["tomi", "lia"], "Tomi switches off his moon-shaped lamp while Lia puts a finger to her lips 'shhh', a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_15", ["tomi", "lia", "pipo"], "Tomi, Lia and Pipo sleep peacefully, the camera far away through the window showing the starry sky, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"], ["04_buenas_noches_19", [], "a shooting star crosses the night sky leaving a sparkle shaped like a portal, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"]]""")
pendientes = [p for p in PLANOS if not os.path.exists(f"{OUT}/{p[0]}.png")]
print(f"\n{len(PLANOS)} planos en total, {len(pendientes)} pendientes. Generando con 2 GPU...")
t0, hechos, fallos, lock = time.time(), [0], [], threading.Lock()


def trabajador(gpu):
    while True:
        with lock:
            if not pendientes: return
            nombre, refs, escena = pendientes.pop(0)
        try:
            generar(gpu, refs, escena, 11, nombre)
            with lock:
                hechos[0] += 1
                print(f"OK {nombre}  [{hechos[0]} hechos, {(time.time()-t0)/60:.0f} min]", flush=True)
        except Exception as e:
            with lock:
                fallos.append(nombre); print(f"FALLO {nombre}: {str(e)[-300:]}", flush=True)


hilos = [threading.Thread(target=trabajador, args=(g,)) for g in (0, 1)]
for h in hilos: h.start()
for h in hilos: h.join()
for s_ in srvs: s_.terminate()

# Hojas de contacto ligeras (miniaturas) para revisar sin colgar el navegador
from PIL import Image, ImageDraw
from IPython.display import Image as IImage, display, Markdown
for grupo in ["00_desfile", "01_verdurita", "02_burbujas", "03_cepillo", "04_buenas_noches"]:
    fs = sorted(glob.glob(f"{OUT}/{grupo}_*.png"))
    if not fs: continue
    W, H, C = 320, 180, 4
    hoja = Image.new("RGB", (W * C, (H + 22) * ((len(fs) + C - 1) // C)), "white")
    d = ImageDraw.Draw(hoja)
    for i, f in enumerate(fs):
        x, y = (i % C) * W, (i // C) * (H + 22)
        hoja.paste(Image.open(f).convert("RGB").resize((W, H)), (x, y + 22))
        d.text((x + 4, y + 4), os.path.basename(f)[:-4], fill="black")
    ruta = f"/kaggle/working/CONTACTO_{grupo}.jpg"
    hoja.save(ruta, quality=80)
    display(Markdown(f"### {grupo}")); display(IImage(ruta))
print(f"\nTERMINADO: {hechos[0]} nuevos, {len(fallos)} fallos {fallos if fallos else ''}")
