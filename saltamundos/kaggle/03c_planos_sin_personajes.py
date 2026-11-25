# SALTAMUNDOS · Cuaderno 03c · Planos SIN personajes (Kaggle, GPU T4)
# Qwen-Image-Edit se inventaba niños cuando no le dábamos personajes de referencia.
# Estos 11 planos se hacen con Z-Image-Turbo (Apache 2.0), el mismo modelo de las hojas, que no inventa gente.
# Sobrescribe las imágenes malas en /kaggle/working/fotogramas. Tarda ~40 min.

import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U",
                "diffusers", "transformers", "accelerate", "bitsandbytes"], check=True)

import os, torch, time, gc
from PIL import Image, ImageDraw
from IPython.display import Image as IImage, display
from diffusers import ZImagePipeline
from diffusers.quantizers import PipelineQuantizationConfig

OUT = "/kaggle/working/fotogramas"
os.makedirs(OUT, exist_ok=True)
ESTILO = ("3D animated children's cartoon, premium feature-film CGI quality, soft global illumination, vibrant "
          "pastel-bright colors, cheerful cozy mood, 16:9 cinematic frame, no text, no people, no children")
PLANOS = [
 [
  "00_desfile_00",
  "three colorful soap bubbles (mint green, purple and orange) slowly falling from the sky over the meadow, wide shot, empty scene with no people, no children, no characters, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"
 ],
 [
  "00_desfile_09",
  "an orange soap bubble bouncing on the grass without popping, empty scene with no people, no children, no characters, a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"
 ],
 [
  "01_verdurita_18a",
  "broccoli trees sway in the breeze, empty scene with no people, no children, no characters, a magical vegetable garden with giant shiny appetizing vegetables (no faces, no eyes on the vegetables), butterflies, warm golden sunlight"
 ],
 [
  "02_burbujas_02b",
  "water gushes into the bathtub with sparkling splashes, slow motion close-up, empty scene with no people, no children, no characters, a bright cozy bathroom with colorful tiles and a bathtub filled with fluffy white soap foam and floating iridescent soap bubbles (no plastic balls), golden window light"
 ],
 [
  "02_burbujas_05b",
  "giant soap bubbles rise toward a window with golden light, empty scene with no people, no children, no characters, a bright cozy bathroom with colorful tiles and a bathtub filled with fluffy white soap foam and floating iridescent soap bubbles (no plastic balls), golden window light"
 ],
 [
  "02_burbujas_06b",
  "a macro shot of rainbow-colored soap bubbles with shallow depth of field, empty scene with no people, no children, no characters, a bright cozy bathroom with colorful tiles and a bathtub filled with fluffy white soap foam and floating iridescent soap bubbles (no plastic balls), golden window light"
 ],
 [
  "03_cepillo_11",
  "a pea-sized dab of toothpaste squeezed onto a toothbrush next to a green pea, macro top-down, empty scene with no people, no children, no characters, a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"
 ],
 [
  "04_buenas_noches_00",
  "a bubble portal slowly opens in a child's bedroom at sunset, wide shot, empty scene with no people, no children, no characters, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"
 ],
 [
  "04_buenas_noches_01",
  "a sleepy sun yawns and sets behind the hills while the smiling moon rises and stars light up one by one, view through the window, empty scene with no people, no children, no characters, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"
 ],
 [
  "04_buenas_noches_04",
  "silhouettes of the meadow, the vegetable garden and the bathtub projected softly on the starry ceiling, empty scene with no people, no children, no characters, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"
 ],
 [
  "04_buenas_noches_19",
  "a shooting star crosses the night sky leaving a sparkle shaped like a portal, empty scene with no people, no children, no characters, a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"
 ]
]

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


t0 = time.time()
for nombre, escena in PLANOS:
    img = pipe(f"{escena}. {ESTILO}", width=1024, height=576, num_inference_steps=9, guidance_scale=0.0,
               generator=torch.Generator("cpu").manual_seed(7)).images[0]
    img.save(f"{OUT}/{nombre}.png")
    print(f"OK {nombre}  ({(time.time()-t0)/60:.1f} min)", flush=True)

# liberar la GPU para el siguiente cuaderno
del pipe; gc.collect(); torch.cuda.empty_cache()

W, H, C = 320, 180, 4
hoja = Image.new("RGB", (W * C, (H + 22) * ((len(PLANOS) + C - 1) // C)), "white")
d = ImageDraw.Draw(hoja)
for i, (nombre, _) in enumerate(PLANOS):
    x, y = (i % C) * W, (i // C) * (H + 22)
    hoja.paste(Image.open(f"{OUT}/{nombre}.png").convert("RGB").resize((W, H)), (x, y + 22))
    d.text((x + 4, y + 4), nombre, fill="black")
hoja.save("/kaggle/working/CONTACTO_sin_personajes.jpg", quality=80)
display(IImage("/kaggle/working/CONTACTO_sin_personajes.jpg"))
print("TERMINADO")
