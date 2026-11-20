# Saltamundos · Episodio 01

Canal infantil 3D original (Tomi, Lía y Pipo). Plan de producción y piezas listas:

- `BIBLIA_EPISODIO_01.md`: guion técnico segundo a segundo (10 min, 4 canciones).
- `PERSONAJES_PROMPTS.md`: fichas y prompts de personajes (referencias oficiales elegidas).
- `kaggle/`: cuadernos para la GPU gratuita de Kaggle (01 hojas de personaje, 02 música) y cliente ComfyUI/Wan 2.2.
- `audio/`: jingle sintetizado (`jingle.py`), canciones elegidas (`canciones/*.mp3`) y su alineación palabra a palabra (`*.json`, `alinear.py`).
- `fisicas/`: escenas de física con react-three-rapier (`npm install && node render.mjs <escena>`; las salidas `.mov` no se versionan, se regeneran).
- `montaje/montar.py`: montaje final FFmpeg (1080p60, karaoke ASS, capas, -14 LUFS).
