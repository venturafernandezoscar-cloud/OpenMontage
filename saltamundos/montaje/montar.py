#!/usr/bin/env python3
"""SALTAMUNDOS · Sistema de montaje final (FFmpeg).

Uso:
    python3 montar.py episodio.json            # render final
    python3 montar.py episodio.json --preview  # 540p rápido para revisar

Qué hace, en orden:
  1. Normaliza cada clip: escala/recorta a 16:9, 60 fps, duración EXACTA en fotogramas
     (los cortes caen siempre en el compás), fundidos opcionales.
  2. Une los clips sin recomprimir (concat).
  3. Mezcla música + efectos de sonido (foley) en su segundo exacto.
  4. Normaliza el audio a -14 LUFS / -1 dBTP en dos pasadas (estándar YouTube).
  5. Quema subtítulos karaoke (ASS): letra grande redondeada, borde grueso,
     la palabra cantada se rellena en amarillo y la línea entra con rebote.
  6. Exporta H.264 1080p60 (o 4K) y verifica duración, fps y sonoridad.
"""
import argparse, json, math, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")


def run(cmd, capture=False):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit(f"FFmpeg falló: {' '.join(cmd[:6])} ...")
    return r.stderr if capture else None


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type,width,height,r_frame_rate",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


# ---------------------------------------------------------------- vídeo
def normalizar_clip(c, i, tmp, W, H, fps):
    frames = round(c["duration"] * fps)
    src = c["file"]
    is_img = src.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    vf = [f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos",
          f"crop={W}:{H}", "setsar=1", f"fps={fps}"]
    if is_img and c.get("kenburns", True):
        # zoom suave para que una imagen fija no parezca congelada
        vf = [f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase", f"crop={W*2}:{H*2}",
              f"zoompan=z='min(1+0.0008*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={frames}:s={W}x{H}:fps={fps}", "setsar=1"]
    # duración exacta: rellena congelando el último fotograma si el clip es corto
    vf += [f"tpad=stop_mode=clone:stop={frames}", f"trim=end_frame={frames}", "setpts=PTS-STARTPTS"]
    inp = ["-loop", "1", "-i", src] if is_img else ["-i", src]
    # capas con transparencia (escenas de física, logo...) encima del clip, en su segundo exacto
    graph = [f"[0:v]{','.join(vf)}[b0]"]
    last = "b0"
    for k, ov in enumerate(c.get("overlays", []), start=1):
        inp += ["-itsoffset", str(ov.get("t", 0)), "-i", ov["file"]]
        graph.append(f"[{k}:v]scale={W}:{H}:flags=lanczos,fps={fps},format=rgba[o{k}]")
        graph.append(f"[{last}][o{k}]overlay=eof_action=pass:format=auto[b{k}]")
        last = f"b{k}"
    post = []
    fi, fo = c.get("fade_in", 0), c.get("fade_out", 0)
    col = c.get("fade_color", "white")
    if fi:
        post.append(f"fade=t=in:st=0:d={fi}:color={col}")
    if fo:
        post.append(f"fade=t=out:st={c['duration']-fo}:d={fo}:color={col}")
    post.append("format=yuv420p")
    graph.append(f"[{last}]{','.join(post)}[v]")
    out = os.path.join(tmp, f"seg_{i:04d}.mp4")
    run(["ffmpeg", "-y", "-v", "error", *inp, "-filter_complex", ";".join(graph), "-map", "[v]", "-an",
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "medium", "-crf", "14",
         "-r", str(fps), "-video_track_timescale", str(fps * 1000), out])
    return out, frames


# ---------------------------------------------------------------- audio
def mezclar_audio(ep, total, tmp):
    inputs, filt, labels = [], [], []
    for k, s in enumerate([{"file": ep["music"], "t": ep.get("music_offset", 0), "gain": 0}] + ep.get("sfx", [])):
        inputs += ["-i", s["file"]]
        ms = int(round(s["t"] * 1000))
        recorte = f"atrim=start={s['desde']},asetpts=PTS-STARTPTS," if s.get("desde") else ""
        filt.append(f"[{k}:a]{recorte}aresample=48000,aformat=channel_layouts=stereo,"
                    f"volume={s.get('gain', 0)}dB,adelay={ms}|{ms}[a{k}]")
        labels.append(f"[a{k}]")
    filt.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:dropout_transition=0,"
                f"apad,atrim=0:{total}[mix]")
    mix = os.path.join(tmp, "mix.wav")
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt),
         "-map", "[mix]", "-c:a", "pcm_s24le", mix])
    # loudnorm en dos pasadas
    err = run(["ffmpeg", "-hide_banner", "-i", mix, "-af",
               "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"], capture=True)
    m = json.loads(err[err.rindex("{"):err.rindex("}") + 1])
    norm = os.path.join(tmp, "mix_norm.wav")
    run(["ffmpeg", "-y", "-v", "error", "-i", mix, "-af",
         f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
         f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
         f":offset={m['target_offset']}:linear=true,aresample=48000",
         "-c:a", "pcm_s24le", norm])
    return norm


# ---------------------------------------------------------------- karaoke
def ass_time(t):
    cs = int(round(t * 100))
    return f"{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}"


def generar_ass(lyrics, W, H, path):
    s = H / 1080
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,Fredoka,{int(92*s)},&H003FD2FF,&H00FFFFFF,&H00E55D9B,&H64000000,-1,0,0,0,100,100,1,0,1,{8*s:.1f},{5*s:.1f},2,{int(120*s)},{int(120*s)},{int(70*s)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for ln in lyrics:
        start = ln["start"]
        words = ln["words"]               # [["Tomi", 0.5], ["va", 0.25], ...] duración cantada de cada palabra
        end = ln.get("end", start + sum(d for _, d in words) + 0.4)
        lead = 0.15                         # la línea aparece un poco antes de cantarse
        pop = r"{\fad(120,150)\fscx80\fscy80\t(0,140,\fscx108\fscy108)\t(140,260,\fscx100\fscy100)}"
        body = r"{\k%d}" % int(lead * 100) + " ".join(r"{\kf%d}%s" % (max(1, int(round(d * 100))), w)
                                                      for w, d in words)
        ev.append(f"Dialogue: 0,{ass_time(start-lead)},{ass_time(end)},Karaoke,,0,0,0,,{pop}{body}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(ev) + "\n")


# ---------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episodio")
    ap.add_argument("--preview", action="store_true", help="960x540 rápido")
    ap.add_argument("--4k", dest="uhd", action="store_true")
    a = ap.parse_args()
    ep = json.load(open(a.episodio))
    base = os.path.dirname(os.path.abspath(a.episodio))
    for c in ep["clips"]:
        c["file"] = os.path.join(base, c["file"])
    ep["music"] = os.path.join(base, ep["music"])
    for s in ep.get("sfx", []):
        s["file"] = os.path.join(base, s["file"])
    for c in ep["clips"]:
        for ov in c.get("overlays", []):
            ov["file"] = os.path.join(base, ov["file"])

    fps = ep.get("fps", 60)
    W, H = (960, 540) if a.preview else (3840, 2160) if a.uhd else (1920, 1080)
    out = os.path.join(base, ep.get("output", "episodio.mp4"))
    if a.preview:
        out = out.replace(".mp4", "_preview.mp4")

    tmp = tempfile.mkdtemp(prefix="montaje_")
    try:
        segs, total_frames = [], 0
        for i, c in enumerate(ep["clips"]):
            if "start" in c and abs(c["start"] * fps - total_frames) > 0.5:
                raise SystemExit(f"Clip {i} ({os.path.basename(c['file'])}) debería empezar en {c['start']}s "
                                 f"pero la suma de los anteriores da {total_frames/fps:.3f}s")
            seg, n = normalizar_clip(c, i, tmp, W, H, fps)
            segs.append(seg); total_frames += n
            print(f"  [{i+1}/{len(ep['clips'])}] {os.path.basename(c['file'])}  {n} fotogramas")
        total = total_frames / fps
        lst = os.path.join(tmp, "lista.txt")
        open(lst, "w").write("".join(f"file '{p}'\n" for p in segs))
        video = os.path.join(tmp, "video.mp4")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])

        print("  Audio: mezcla + -14 LUFS ...")
        audio = mezclar_audio(ep, total, tmp)

        ass = os.path.join(tmp, "karaoke.ass")
        generar_ass(ep.get("lyrics", []), W, H, ass)
        print("  Render final ...")
        run(["ffmpeg", "-y", "-v", "error", "-i", video, "-i", audio,
             "-vf", f"ass={ass}:fontsdir={FONTS}",
             "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
             "-preset", "veryfast" if a.preview else "slow", "-crf", "23" if a.preview else "17",
             "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(fps), "-g", str(fps // 2),
             "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart",
             "-t", f"{total:.3f}", out])

        # verificación
        info = probe(out)
        dur = float(info["format"]["duration"])
        v = next(s for s in info["streams"] if s["codec_type"] == "video")
        err = run(["ffmpeg", "-hide_banner", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"], capture=True)
        lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])
        tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])
        ok = abs(dur - total) < 0.05 and v["r_frame_rate"] == f"{fps}/1" and abs(lufs + 14) <= 1.0 and tp <= -0.5
        print(f"\n{'✅' if ok else '⚠️'} {out}\n   {v['width']}x{v['height']} @ {v['r_frame_rate']} fps · "
              f"{dur:.2f}s (esperado {total:.2f}s) · {lufs:.1f} LUFS · pico {tp:.1f} dBTP")
        if not ok:
            raise SystemExit("La verificación final no ha pasado.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
