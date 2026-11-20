# Cliente mínimo de ComfyUI + flujo Wan 2.2 TI2V-5B Turbo (imagen -> clip de vídeo).
# Lo usan los cuadernos de Kaggle; aquí se prueba en CPU a tamaño mini.
import json, os, time, uuid, urllib.request, shutil

NEG = ("blurry, low quality, distorted face, deformed hands, extra fingers, morphing, flicker, text, watermark, "
       "static frame, overexposed, ugly, scary")


def flujo_wan(imagen, prompt, frames, seed, ancho=1280, alto=704, unet="wan_turbo.gguf",
              clip="umt5.gguf", vae="wan2.2_vae.safetensors", prefijo="plano", pasos=4):
    return {
        "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": unet}},
        "2": {"class_type": "CLIPLoaderGGUF", "inputs": {"clip_name": clip, "type": "wan"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": vae}},
        "4": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": 8.0}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": NEG}},
        "7": {"class_type": "LoadImage", "inputs": {"image": imagen}},
        "8": {"class_type": "ImageScale", "inputs": {"image": ["7", 0], "upscale_method": "lanczos",
                                                     "width": ancho, "height": alto, "crop": "center"}},
        "9": {"class_type": "Wan22ImageToVideoLatent", "inputs": {"vae": ["3", 0], "width": ancho, "height": alto,
                                                                  "length": frames, "batch_size": 1,
                                                                  "start_image": ["8", 0]}},
        "10": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["5", 0], "negative": ["6", 0],
                                                    "latent_image": ["9", 0], "seed": seed, "steps": pasos, "cfg": 1.0,
                                                    "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["3", 0]}},
        "12": {"class_type": "SaveImage", "inputs": {"images": ["11", 0], "filename_prefix": prefijo}},
    }


class Comfy:
    def __init__(self, url="http://127.0.0.1:8188"):
        self.url = url

    def _req(self, path, data=None):
        body = json.dumps(data).encode() if data is not None else None
        r = urllib.request.Request(self.url + path, data=body, headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(r, timeout=60).read())

    def esperar_servidor(self, segundos=600):
        t0 = time.time()
        while time.time() - t0 < segundos:
            try:
                self._req("/system_stats"); return True
            except Exception:
                time.sleep(3)
        raise RuntimeError("ComfyUI no arrancó")

    def ejecutar(self, flujo, salida_dir, timeout=7200):
        """Lanza el flujo, espera y devuelve la lista de imágenes generadas (rutas)."""
        r = self._req("/prompt", {"prompt": flujo, "client_id": uuid.uuid4().hex})
        if r.get("node_errors"):
            raise RuntimeError(f"Error en el flujo: {r['node_errors']}")
        pid, t0 = r["prompt_id"], time.time()
        while time.time() - t0 < timeout:
            h = self._req(f"/history/{pid}")
            if pid in h:
                st = h[pid].get("status", {})
                if st.get("status_str") == "error":
                    msgs = [m for m in st.get("messages", []) if m[0] == "execution_error"]
                    raise RuntimeError(f"ComfyUI falló: {msgs[-1][1].get('exception_message') if msgs else st}")
                files = []
                for out in h[pid]["outputs"].values():
                    for im in out.get("images", []):
                        files.append(os.path.join(salida_dir, im.get("subfolder", ""), im["filename"]))
                return sorted(files)
            time.sleep(2)
        raise TimeoutError("El plano tardó demasiado")
