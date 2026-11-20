# SALTAMUNDOS · Fichas y prompts de personajes (v2 — ajustada a las hojas oficiales)

**Referencias oficiales elegidas:** Tomi giro #2 + expresiones #1 · Lía giro #2 + expresiones #1 · Pipo giro #1 + expresiones #2.

Los prompts van en **inglés** porque los modelos de imagen y vídeo responden mejor en inglés.
**Regla de oro:** el bloque de **ESTILO** y el **ADN** de cada personaje se pegan **siempre idénticos** en cada prompt. Solo cambian la acción, el escenario y la cámara.

---

## 1. ESTILO GLOBAL (pegar al principio de TODOS los prompts)

```
3D animated children's cartoon, premium feature-film CGI quality, soft global illumination,
warm subsurface-scattered skin, rounded appealing shapes, big glossy expressive eyes with catchlights,
detailed fabric textures, vibrant high-saturation but pleasant pastel-bright palette, clean bright
environment, gentle rim light, shallow depth of field, cheerful and cozy mood, 16:9
```

## NEGATIVO (si el modelo lo admite)

```
realistic photo, uncanny, creepy, scary, dark, horror, distorted face, extra fingers, missing fingers,
deformed hands, asymmetric eyes, teeth showing too much, adult proportions, text, watermark, logo,
blurry, low quality, grainy, harsh shadows, desaturated, gritty
```

---

## 2. ADN DE LOS PERSONAJES (no cambiar jamás)

### TOMI (bebé, 18 meses, protagonista)
```
TOMI, an 18-month-old baby boy, chubby toddler proportions (head about 1/3 of body height),
fluffy golden-blond curly hair, big round hazel eyes,
rosy round cheeks, two small front baby teeth,
fair warm skin, wearing mint-green overalls (#7FD8BE) with a yellow sun patch on the chest (#FFD23F),
white t-shirt underneath, chunky orange sneakers (#FF8C42)
```

### LÍA (hermana, 4 años)
```
LIA, a 4-year-old girl, warm brown skin, dark curly hair in two high round puffs tied with
coral pom-pom hair ties (#FF6F59), big dark-brown eyes with long lashes, dimpled smile,
wearing a purple dress (#9B5DE5) with white polka dots, sparkly yellow sandals (#FFE066)
```

### PIPO (mascota, cachorro corgi)
```
PIPO, a small fluffy corgi puppy, orange and cream fur (#F4A259 / #FFF3E0),
white chest and muzzle, big upright pointy ears,
shiny black eyes, short legs, fluffy tail, wearing a red bandana around its neck (#E63946)
```

---

## 3. HOJAS DE PERSONAJE (primera generación, la base de la consistencia)

### 3.1 Hoja de giro (turnaround) — una por personaje
```
[ESTILO GLOBAL], character turnaround sheet of [ADN DEL PERSONAJE], full body, four views
side by side on a seamless light cream background: front view, three-quarter view, side profile,
back view, neutral relaxed standing pose, same character identical in every view,
even soft studio lighting, model sheet
```

### 3.2 Hoja de expresiones — una por personaje
```
[ESTILO GLOBAL], expression sheet of [ADN DEL PERSONAJE], head and shoulders, 3x2 grid on a
light cream background: big happy smile, surprised wide eyes, laughing with eyes closed,
curious head tilt, sleepy yawning, proud cheering, same character identical in every panel
```

### 3.3 Foto de grupo (referencia de escala entre personajes)
```
[ESTILO GLOBAL], [ADN TOMI] sitting in the center, [ADN LIA] standing on the left with her hand
on Tomi's shoulder, [ADN PIPO] on the right wagging its tail, all three smiling at the camera,
correct relative scale (Lia about twice Tomi's height, Pipo as tall as sitting Tomi),
sunny colorful meadow background softly blurred
```

**Proceso:** se generan 8 variantes de cada hoja → eliges la mejor → esa imagen pasa a ser la **referencia oficial**. Todo lo demás se genera a partir de ella (edición con referencia + imagen→vídeo), nunca desde cero.

---

## 4. PLANTILLA DE PLANO (cada fila del guion se convierte en esto)

**Imagen clave (fotograma inicial):**
```
[ESTILO GLOBAL], [ADN de los personajes que salen], [ACCIÓN de la fila del guion],
[ESCENARIO del mundo], [CÁMARA: plano/ángulo], [LUZ del mundo]
```

**Movimiento (imagen → vídeo, clip de 2–4 s):**
```
[ACCIÓN en presente, un solo movimiento claro], [movimiento de cámara], smooth natural motion,
cheerful, consistent character, no morphing
```

### Ejemplo real: fila 1:17–1:19 de «¡Verdurita, Sí!»
- **Imagen:** `[ESTILO GLOBAL], [ADN TOMI], Tomi glowing with a soft green aura, crouching and about to jump, giant smiling vegetables in a bright magical vegetable garden, low-angle medium shot, warm golden sunlight`
- **Movimiento:** `Tomi jumps very high into the air with arms raised and lands softly, camera tilts up following him, smooth natural motion, cheerful, consistent character, no morphing`

---

## 5. MUNDOS (bloque de escenario reutilizable)

| Mundo | Prompt |
|---|---|
| Prado (desfile) | `rolling meadow of colorful flowers at sunrise, soft pastel sky, floating soap bubbles` |
| Huerto | `magical vegetable garden with giant shiny vegetables that have cute closed-mouth smiling eyes, butterflies, warm sunlight` |
| Baño | `bright cozy bathroom with colorful tiles, bathtub full of rainbow foam bubbles, rubber ducks, window with golden light` |
| Sonrisa | `magical bathroom mirror revealing soft white tooth-shaped hills and minty foam clouds, playful and clean` |
| Estrellas | `cozy child bedroom whose ceiling opens to a soft lilac night sky, smiling sleeping moon, glowing stars like fireflies, pastel lavender and warm gold` |

---

## 6. Portal-burbuja (elemento de marca)
```
a giant iridescent soap-bubble portal with swirling rainbow reflections and sparkles,
soft glowing edge, magical and friendly
```
