# SALTAMUNDOS · Cuaderno 01 · Hojas de personaje (Kaggle, GPU T4)
# Modelo: Z-Image-Turbo (licencia Apache 2.0, uso comercial permitido, sin registro).
# Pega TODO esto en una celda de Kaggle y pulsa Ejecutar. Tarda ~40-70 min.

import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U",
                "diffusers", "transformers", "accelerate", "bitsandbytes"], check=True)

import os, torch, time, shutil
from PIL import Image, ImageDraw, ImageFont
from IPython.display import display
from diffusers import ZImagePipeline
from diffusers.quantizers import PipelineQuantizationConfig

VARIANTES = 4          # imágenes por hoja (sube a 8 si sobra tiempo)
OUT = "/kaggle/working/hojas"
os.makedirs(OUT, exist_ok=True)

ESTILO = ("3D animated children's cartoon, premium feature-film CGI quality, soft global illumination, "
          "warm subsurface-scattered skin, rounded appealing shapes, big glossy expressive eyes with catchlights, "
          "detailed fabric textures, vibrant high-saturation but pleasant pastel-bright palette, clean bright "
          "environment, gentle rim light, cheerful and cozy mood")

ADN = {
 "tomi": ("TOMI, an 18-month-old baby boy, chubby toddler proportions (head about 1/3 of body height), "
          "fluffy golden-blond curly hair, big round hazel eyes, "
          "rosy round cheeks, two small front baby teeth, fair warm skin, "
          "wearing mint-green overalls with a yellow sun patch on the chest, white t-shirt underneath, "
          "chunky orange sneakers"),
 "lia":  ("LIA, a 4-year-old girl, warm brown skin, dark curly hair in two high round puffs tied with "
          "coral pom-pom hair ties, big dark-brown eyes with long lashes, dimpled smile, "
          "wearing a purple dress with white polka dots, sparkly yellow sandals"),
 "pipo": ("PIPO, a small fluffy corgi puppy, orange and cream fur, white chest and muzzle, "
          "big upright pointy ears, shiny black eyes, short legs, fluffy tail, "
          "wearing a red bandana around its neck"),
}

HOJAS = []
for k, adn in ADN.items():
    HOJAS.append((f"{k}_giro", 1344, 768,
        f"{ESTILO}. Character turnaround model sheet of {adn}. Full body, four views side by side on a seamless "
        f"light cream background: front view, three-quarter view, side profile, back view. Neutral relaxed standing "
        f"pose, the same character identical in every view, even soft studio lighting."))
    HOJAS.append((f"{k}_expresiones", 1024, 1024,
        f"{ESTILO}. Expression sheet of {adn}. Head and shoulders, 3x2 grid on a light cream background: "
        f"big happy smile, surprised wide eyes, laughing with eyes closed, curious head tilt, sleepy yawning, "
        f"proud cheering. The same character identical in every panel."))
HOJAS.append(("grupo", 1344, 768,
    f"{ESTILO}. {ADN['tomi']} sitting in the center; {ADN['lia']} standing on the left with her hand on Tomi's "
    f"shoulder; {ADN['pipo']} on the right wagging its tail. All three smiling at the camera, correct relative scale "
    f"(Lia about twice Tomi's height, Pipo as tall as sitting Tomi), sunny colorful flower meadow background softly blurred."))

# ---- Cargar modelo (Z-Image-Turbo: abierto, sin registro, licencia Apache 2.0) ----
# Comprimido a 4 bits para que quepa en la memoria de la T4 (16 GB)
quant = PipelineQuantizationConfig(
    quant_backend="bitsandbytes_4bit",
    quant_kwargs={"load_in_4bit": True, "bnb_4bit_quant_type": "nf4", "bnb_4bit_compute_dtype": torch.bfloat16},
    components_to_quantize=["transformer", "text_encoder"])
pipe = ZImagePipeline.from_pretrained("Tongyi-MAI/Z-Image-Turbo", torch_dtype=torch.bfloat16,
                                      quantization_config=quant)
pipe.to("cuda")
try:
    pipe.vae.enable_tiling()
except Exception:
    pass

# ---- Generar ----
def hoja_de_contacto(nombre, imgs):
    w, h = 512, int(512 * imgs[0].height / imgs[0].width)
    sheet = Image.new("RGB", (w * len(imgs), h + 60), "white")
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except Exception:
        font = ImageFont.load_default()
    for i, im in enumerate(imgs):
        sheet.paste(im.resize((w, h)), (i * w, 60))
        d.text((i * w + 10, 8), f"{nombre}  #{i+1}", fill="black", font=font)
    return sheet

t0 = time.time()
for nombre, W, H, prompt in HOJAS:
    imgs = []
    for v in range(VARIANTES):
        seed = 1000 + v
        img = pipe(prompt, width=W, height=H, num_inference_steps=9, guidance_scale=0.0, generator=torch.Generator("cpu").manual_seed(seed)).images[0]
        img.save(f"{OUT}/{nombre}_{v+1}_seed{seed}.png")
        imgs.append(img)
        print(f"✔ {nombre} #{v+1}  ({(time.time()-t0)/60:.1f} min)")
    contacto = hoja_de_contacto(nombre, imgs)
    contacto.save(f"{OUT}/_CONTACTO_{nombre}.jpg", quality=90)
    display(contacto)

shutil.make_archive("/kaggle/working/saltamundos_hojas", "zip", OUT)
print("\n🎉 TERMINADO. Haz pantallazo de cada hoja de contacto y dime el número que más te guste de cada una.")
