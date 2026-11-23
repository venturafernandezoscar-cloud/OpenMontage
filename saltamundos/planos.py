#!/usr/bin/env python3
"""SALTAMUNDOS · Lista de planos del Episodio 01, sincronizada con las canciones reales.

Cada línea de la letra (tiempos de audio/canciones/*.json) se parte en 1-2 planos.
Cada plano lleva: personajes de referencia, escena (fotograma clave) y movimiento (para Wan 2.2).
Los estribillos repetidos cambian de decorado y el estribillo final reutiliza planos (`reusar`).
Uso: python3 planos.py  ->  planos.json
"""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
T, L, P = "tomi", "lia", "pipo"

# ---------------- MUNDOS ----------------
PRADO = "a rolling meadow of colorful flowers at sunrise with floating soap bubbles, soft pastel sky"
HUERTO = "a magical vegetable garden with giant shiny appetizing vegetables (no faces, no eyes on the vegetables), butterflies, warm golden sunlight"
GIRASOL = "a bright sunflower field with giant pumpkins, blue sky, warm sunlight"
BANO = "a bright cozy bathroom with colorful tiles and a bathtub filled with fluffy white soap foam and floating iridescent soap bubbles (no plastic balls), golden window light"
PATIO = "a backyard at dusk with glowing fluorescent soap bubbles floating in the air, fairy lights"
SONRISA = "a bright cozy bathroom with a big mirror and a small step stool, minty foam, colorful toothbrushes"
DIENTES = "a magical world of soft white tooth-shaped hills and minty foam clouds, playful and clean, seen through a mirror"
NOCHE = "a cozy child bedroom whose ceiling opens to a soft lilac night sky with a smiling sleeping moon and glowing stars like fireflies, pastel lavender and warm gold light"


def s(refs, escena, mov, mundo=None):
    return {"refs": refs, "escena": escena + (f", {mundo}" if mundo else ""), "movimiento": mov}


# ---------------- DESFILE (instrumental, 45 s, tiempos fijos) ----------------
DESFILE = [  # (t0, t1, plano)
    (0, 2, s([], "three colorful soap bubbles (mint green, purple and orange) slowly falling from the sky over the meadow, wide shot", "bubbles drift down gently, camera cranes down", PRADO)),
    (2, 4, s([T, "tomi_caras"], "the mint-green bubble pops and Tomi sits on the grass looking surprised, medium shot", "bubble bursts into sparkles, Tomi blinks surprised", PRADO)),
    (4, 6, s([T, "tomi_caras"], "Tomi looks at his hands and claps happily, close-up", "Tomi claps his hands twice and giggles", PRADO)),
    (6, 8, s([T], "Tomi crawls fast toward the camera, low ground-level shot", "Tomi crawls quickly toward camera, camera dollies back", PRADO)),
    (8, 10, s([T], "Tomi stands up wobbly and does a proud triumphant pose, low angle", "Tomi stands up, wobbles, then raises both arms proudly", PRADO)),
    (10, 12, s([L], "the purple bubble lands and Lia spins out of it like a ballerina, medium shot", "Lia twirls around once, dress flaring", PRADO)),
    (12, 14, s([L], "Lia does three little hops, her hair puffs bouncing, full body", "Lia hops three times happily", PRADO)),
    (14, 16, s([L, "lia_caras"], "Lia raises her index finger with a bright 'I know!' face and a little sparkle star appears, close-up", "Lia raises her finger and smiles, a sparkle pops", PRADO)),
    (16, 18, s([L], "Lia waves at the camera with both hands, front view", "Lia waves both hands at camera", PRADO)),
    (18, 20, s([], "an orange soap bubble bouncing on the grass without popping", "the bubble bounces three times", PRADO)),
    (20, 22, s([P], "the orange bubble pops and Pipo lands on his bottom looking surprised, low shot", "Pipo plops down and tilts his head", PRADO)),
    (22, 24, s([P], "Pipo playfully turns his head to look back at his small fluffy tail, normal corgi tail, three-quarter view", "Pipo turns around in a circle chasing his tail", PRADO)),
    (24, 26, s([P, "pipo_caras"], "Pipo, a bit dizzy, stops and tilts his head at the camera, close-up", "Pipo stops, wobbles dizzily and tilts his head", PRADO)),
    (26, 28, s([T, L, P], "Tomi, Lia and Pipo meet in the middle of the meadow and look at each other, wide shot", "the three walk toward each other and stop", PRADO)),
    (28, 30, s([T, L, P], "Tomi, Lia and Pipo share a big group hug with heart-shaped bubbles around them, medium shot", "they hug and heart bubbles float up", PRADO)),
    (30, 34, s([T, L, P], "Tomi, Lia and Pipo dance together clapping, spinning and jumping, full body", "they clap, spin and jump in rhythm, camera circles around", PRADO)),
    (34, 38, s([T, L, P], "Tomi, Lia and Pipo dance in a circle of flowers that sway with them, top-down", "they dance in a circle while flowers sway", PRADO)),
    (38, 41, s([T, L], "Tomi rubs his rumbling tummy and Lia points far away at a glowing vegetable garden, medium shot", "Tomi rubs his tummy, Lia points into the distance", PRADO)),
    (41, 45, s([T, L, P], "Tomi, Lia and Pipo run toward a giant iridescent soap-bubble portal opening in the meadow, wide shot from behind", "they run toward the swirling bubble portal, camera follows", PRADO)),
]

# ---------------- CANCIONES: planos por línea (1 o 2 por línea) ----------------
VERDURITA = [
    [s([T, L, P], "Tomi, Lia and Pipo land on a giant bouncy lettuce leaf and look around amazed, wide shot", "they bounce softly on the leaf and look around", HUERTO)],   # intro (antes de la 1ª línea)
    [s([T, "tomi_caras"], "Tomi rubs his tummy with a funny hungry face, close-up", "Tomi rubs his tummy and pouts", HUERTO),
     s([T, "tomi_caras"], "Tomi opens and closes his mouth 'nom nom nom', extreme close-up", "Tomi chomps the air three times", HUERTO)],
    [s([T], "a giant rainbow lollipop shines among the plants, Tomi reaches out his hand toward it, medium shot", "Tomi slowly reaches for the lollipop and freezes", HUERTO)],
    [s([L], "Lia arrives holding a bright shiny carrot, three-quarter medium shot", "Lia walks in holding up the carrot", HUERTO),
     s([L, "lia_caras"], "Lia bites the carrot, little orange crumbs flying in slow motion, close-up", "Lia takes a crunchy bite", HUERTO)],
    [s([T, L], "Lia hands the carrot to Tomi who bites it with full cheeks and a big smile, two-shot", "Tomi bites the carrot and smiles with full cheeks", HUERTO)],
    [s([T], "Tomi glows with a soft green aura and jumps very high, low angle", "Tomi jumps high into the air with arms raised", HUERTO)],      # estribillo 1
    [s([L], "Lia lifts a giant pumpkin with one finger as a funny gag, full body", "Lia lifts the giant pumpkin effortlessly", HUERTO),
     s([T, L, P], "Tomi, Lia and Pipo put their hands on their hearts and smile, front view", "they place hands on hearts and smile", HUERTO)],
    [s([T], "Tomi leaps up among fluffy clouds toward a smiling sun", "Tomi floats up between clouds, camera tilts up", HUERTO)],
    [s([T, L, P], "Tomi, Lia and Pipo dance clapping with heart-shaped bubbles around, medium shot", "they clap and spin, heart bubbles float", HUERTO)],
    [s([P], "Pipo sniffs and pops his head out of the leaves holding a broccoli floret (no face on the broccoli), low ground shot", "Pipo sniffs and pokes out his head", HUERTO),
     s([P], "the broccoli grows into a little tree and Pipo sits under it, low angle", "the broccoli grows into a tree above Pipo", HUERTO)],
    [s([L], "Lia opens a pea pod and three peas jump out, close-up of hands", "three peas pop out one by one", HUERTO)],
    [s([T, "tomi_caras"], "Tomi brings a broccoli floret to his mouth with a doubtful face, close-up", "Tomi hesitates, looking at the broccoli", HUERTO)],
    [s([T, "tomi_caras"], "Tomi's eyes light up with delight and he claps asking for more, front view", "Tomi's eyes light up and he claps happily", HUERTO)],
    [s([T, L, P], "Tomi, Lia and Pipo bounce on giant pumpkins like trampolines, wide shot", "they bounce up and down on pumpkins", GIRASOL)],   # estribillo 2
    [s([T, L], "Tomi and Lia run hand in hand through tall sunflowers, side tracking shot", "they run through the sunflowers, camera tracks sideways", GIRASOL)],
    [s([T], "Tomi jumps over a giant pumpkin toward the sun, low angle", "Tomi leaps over the pumpkin", GIRASOL)],
    [s([T, L, P], "Tomi, Lia and Pipo strike a happy pose with arms up among sunflowers, front", "they jump and pose with arms up", GIRASOL)],
    [s([T, L], "a giant red tomato rolls past Tomi and Lia, the scene tinted warm red", "a tomato rolls by, the children laugh", HUERTO),
     s([P], "orange carrots pop up out of the ground around Pipo, low shot", "carrots pop out of the soil", HUERTO)],
    [s([], "broccoli trees sway in the breeze", "broccoli trees sway", HUERTO),
     s([L], "Lia in her purple dress stands next to a giant eggplant of the same color and laughs", "Lia laughs, comparing her dress with the eggplant", HUERTO)],
    [s([P], "a corn cob pops popcorn that rains on Pipo", "popcorn pops and rains on Pipo", HUERTO),
     s([T, L, P], "Tomi, Lia and Pipo look at a plate full of rainbow vegetables with amazement, top-down", "they lean over the shiny rainbow plate", HUERTO)],
    [s([T, L], "a rainbow lollipop reappears and Lia breaks off a tiny piece for Tomi, medium two-shot", "Lia breaks off a tiny piece and gives it to Tomi", HUERTO)],
    [s([L, "lia_caras"], "Lia raises her index finger with a wise smile while a giant bubble portal opens in the sky behind her", "Lia raises her finger, the portal swirls open", HUERTO)],
    [{"reusar": 5}], [{"reusar": 7}], [{"reusar": 13}], [{"reusar": 8}],     # estribillo final: montaje de los mejores planos
    [s([T, L, P], "Tomi, Lia and Pipo jump into the swirling bubble portal in slow motion, Tomi winks at the camera", "they leap into the portal in slow motion", HUERTO)],  # cola
]

BURBUJAS = [
    [s([T], "Tomi crawls along a sunny hallway toward the bathroom door, ground-level shot", "Tomi crawls toward the door, camera follows", None)],
    [s([T], "Tomi walks wobbly toward the bathtub, medium side shot", "Tomi toddles toward the tub", BANO),
     s([T], "Tomi's little feet stomp in three tiny puddles on the tiles, close-up", "little feet splash in puddles", BANO)],
    [s([L], "Lia turns the faucet with both hands, three-quarter shot", "Lia turns the tap", BANO),
     s([], "water gushes into the bathtub with sparkling splashes, slow motion close-up", "water fills the tub with splashes", BANO)],
    [s([P], "Pipo trots in with a yellow rubber duck in his mouth, low shot", "Pipo trots in carrying the duck", BANO),
     s([P], "Pipo squeezes the rubber duck, close-up", "Pipo squeaks the duck three times", BANO)],
    [s([T, L], "Lia lifts Tomi into the bathtub full of foam, Tomi raises his arms with joy", "Lia lifts Tomi into the foamy tub", BANO)],
    [s([T, "tomi_caras"], "Tomi blows and five giant soap bubbles come out, close-up", "Tomi blows a stream of big bubbles", BANO),
     s([], "giant soap bubbles rise toward a window with golden light", "bubbles float upward, camera cranes up", BANO)],
    [s([T, L], "Tomi and Lia clap and more bubbles appear, two-shot", "they clap and bubbles burst out", BANO),
     s([], "a macro shot of rainbow-colored soap bubbles with shallow depth of field", "bubbles shimmer with rainbow colors", BANO)],
    [s([T, "tomi_caras"], "a bubble pops on Tomi's nose and he goes cross-eyed, extreme close-up", "a bubble pops on his nose, he goes cross-eyed and giggles", BANO),
     s([T], "a bubble pops on Tomi's feet sticking out of the foam, close-up", "a bubble pops on his toes", BANO)],
    [s([T, L], "Tomi and Lia sway left and right in the bath counting on their fingers, front", "they sway and count one, two, three on fingers", BANO)],
    [s([T, "tomi_caras"], "Tomi rubs his cheeks with a yellow sponge, eyes closed, close-up", "Tomi scrubs his cheeks in circles", BANO)],
    [s([T, L], "Lia shapes Tomi's foamy hair into a funny little horn while he giggles, two-shot", "Lia styles foam on his head, Tomi giggles", BANO)],
    [s([P], "wet Pipo shakes himself, water drops flying in slow motion, wide shot", "Pipo shakes off water in slow motion", BANO)],
    [s([T, L, P], "Tomi and Lia soaked with open mouths while Pipo spins happily, wide shot", "they laugh while Pipo spins", BANO)],
    [s([T, L, P], "Tomi, Lia and Pipo blow glowing bubbles in the backyard at dusk, wide shot", "glowing bubbles float around them", PATIO)],    # estribillo 2
    [s([T, L], "Tomi and Lia chase glowing bubbles, top-down shot", "they chase glowing bubbles", PATIO)],
    [s([T], "a glowing bubble pops on Tomi's nose, close-up", "the bubble pops, Tomi laughs", PATIO)],
    [s([T, L, P], "Tomi, Lia and Pipo count to three with fingers under fairy lights, front", "they count on their fingers and cheer", PATIO)],
    [s([L], "Lia tips a basket of rubber ducks from above the bathtub, low angle", "Lia tips the basket over", BANO)],   # puente (la física añade los patitos)
    [{"reusar": 6}], [{"reusar": 8}], [{"reusar": 5}], [{"reusar": 7}],
    [s([T, L, P], "Lia wraps Tomi in a duck hooded towel, all three wave goodbye sleepily, warm light", "they wave, Tomi yawns", BANO)],
    [s([T, L, P], "Tomi, Lia and Pipo jump into a glowing bubble portal wrapped in towels, laughing", "they hop into the portal", BANO)],  # cola
]

CEPILLO = [
    [s([T], "Tomi climbs onto his little step stool and looks at the mirror, over-the-shoulder shot", "Tomi climbs up and looks at the mirror", SONRISA)],
    [s([T, "tomi_caras"], "Tomi licks his lips happily remembering a candy, close-up", "Tomi licks his lips and smiles", SONRISA)],
    [s([T, "tomi_caras"], "Tomi smiles wide at the mirror showing his two little teeth, close-up through the mirror", "Tomi grins at the mirror, camera zooms in", SONRISA)],
    [s([], "tiny cute purple sticky blobs with funny faces dance on two white baby teeth, macro shot", "the little purple blobs wiggle and giggle", DIENTES)],
    [s([L], "Lia arrives holding two colorful toothbrushes up like superheroes, low angle", "Lia raises the toothbrushes heroically", SONRISA)],
    [s([T], "Tomi brushes his teeth up and down with a mint toothbrush, front view through mirror", "Tomi brushes up and down", SONRISA)],
    [s([T, L], "Tomi and Lia brush their teeth side to side in sync, two-shot", "they brush side to side together", SONRISA)],
    [s([T, "tomi_caras"], "Tomi brushes in little circles with minty foam clouds around, close-up", "Tomi brushes in circles, foam puffs", SONRISA)],
    [s([T, L, P], "Tomi, Lia and Pipo show big shiny smiles with sparkles, medium shot", "they smile wide and sparkles twinkle", SONRISA)],
    [s([P], "Pipo appears with a toothbrush in his mouth wagging his tail, low shot", "Pipo wags his tail holding a toothbrush", SONRISA)],
    [s([L, P], "Lia gently brushes Pipo's teeth and Pipo smiles with shiny teeth", "Lia brushes Pipo's teeth, he smiles", SONRISA)],
    [s([], "a pea-sized dab of toothpaste squeezed onto a toothbrush next to a green pea, macro top-down", "toothpaste squeezes out", SONRISA)],
    [s([T, L], "Tomi and Lia brush counting one, two, three, front view", "they brush and count", SONRISA)],
    [s([T, L, P], "Tomi, Lia and Pipo brush their teeth dancing on soft white tooth-shaped hills", "they brush and dance on the hills", DIENTES)],   # estribillo 2
    [s([T, L], "Tomi and Lia slide down a minty foam cloud laughing", "they slide down the foam cloud", DIENTES)],
    [s([T], "Tomi holds up his toothbrush like a magic wand, sparkles everywhere", "Tomi waves the toothbrush, sparkles fly", DIENTES)],
    [s([T, L, P], "Tomi, Lia and Pipo jump with big shiny smiles among sparkles", "they jump and smile", DIENTES)],
    [s([T, "tomi_caras"], "Tomi gargles with puffed cheeks holding a colorful cup, close-up", "Tomi gargles with puffed cheeks", SONRISA)],
    [s([T], "Tomi leans over the sink and spits, the little purple blobs slide down the drain like a water slide", "Tomi spits, blobs slide away", SONRISA)],
    [s([T, L, P], "Tomi, Lia and Pipo wave goodbye to the tiny friendly purple blobs at the drain", "they wave bye-bye", SONRISA)],
    [{"reusar": 5}], [{"reusar": 6}], [{"reusar": 7}], [{"reusar": 8}],
    [s([T, "tomi_caras"], "Tomi shows his shiny smile to the camera and winks while a bubble portal to the night opens behind him", "Tomi winks, the portal opens", SONRISA)],
]

NOCHES = [
    [s([], "a bubble portal slowly opens in Tomi's bedroom at sunset, wide shot", "the portal glows softly, camera cranes slowly", NOCHE)],
    [s([], "a sleepy sun yawns and sets behind the hills while the smiling moon rises and stars light up one by one, view through the window", "the sun sets, the moon rises, stars switch on", NOCHE)],
    [s([T, L], "Lia helps Tomi put on blue star pajamas, Tomi hugs his soft sleeve", "Lia helps Tomi into pajamas, he hugs his sleeve", NOCHE)],
    [s([T, L, P], "Tomi, Lia and Pipo sway sleepily on a cloud-like bed while stars float down", "they sway gently as stars drift down", NOCHE)],
    [s([], "silhouettes of the meadow, the vegetable garden and the bathtub projected softly on the starry ceiling", "dreamy shapes glow on the ceiling", NOCHE)],
    [s([T, "tomi_caras"], "Tomi closes one eye and then the other, extreme close-up, soft light", "Tomi slowly closes his eyes", NOCHE)],
    [s([T, L, P], "Tomi, Lia and Pipo wave very softly to the camera from the bed", "they wave goodnight gently", NOCHE)],
    [s([L], "Lia opens a storybook and glowing fish and stars swim out into the room", "glowing fish and stars float out of the book", NOCHE)],
    [s([T, L, P], "Pipo curls into a ball, then Pipo, Tomi and Lia yawn one after another", "contagious yawns, one after another", NOCHE)],
    [{"reusar": 3}], [{"reusar": 4}], [{"reusar": 5}], [{"reusar": 6}],
    [s([T, L, P], "Lia hugs Tomi and Pipo joins in, a heart of light glows above them", "they hug, a glowing heart appears", NOCHE)],
    [s([T, L], "Tomi switches off his moon-shaped lamp while Lia puts a finger to her lips 'shhh'", "click, the lamp turns off; Lia says shhh", NOCHE)],
    [s([T, L, P], "Tomi, Lia and Pipo sleep peacefully, the camera far away through the window showing the starry sky", "camera slowly pulls back through the window", NOCHE)],
    [{"reusar": 1}], [{"reusar": 4}], [{"reusar": 3}],
    [s([], "a shooting star crosses the night sky leaving a sparkle shaped like a portal", "a shooting star streaks across the sky", NOCHE)],
]

CANCIONES = [("01_verdurita", "01_verdurita_v1", VERDURITA), ("02_burbujas", "02_burbujas_v2", BURBUJAS),
             ("03_cepillo", "03_cepillo_v3", CEPILLO), ("04_buenas_noches", "04_buenas_noches_v2", NOCHES)]


def construir():
    out = []
    for t0, t1, p in DESFILE:
        out.append({"id": f"00_desfile_{len(out):02d}", "cancion": "05_desfile_v2", "t0": t0, "t1": t1, **p})
    for cid, audio, guion in CANCIONES:
        al = json.load(open(f"{AQUI}/audio/canciones/{audio}.json"))
        dur = float(os.popen(f"ffprobe -v error -show_entries format=duration -of csv=p=0 {AQUI}/audio/canciones/{audio}.mp3").read())
        lin = al["lineas"]
        # tramos: [intro] + 1 por línea (en el orden del guion) + [cola]
        cortes = [0.0] + [l["start"] for l in lin] + [lin[-1]["end"] + 0.3]
        tramos = [(cortes[i], cortes[i + 1]) for i in range(len(cortes) - 1)] + [(lin[-1]["end"] + 0.3, dur)]
        assert len(guion) == len(tramos), f"{cid}: guion {len(guion)} vs tramos {len(tramos)}"
        base = len(out)
        for k, ((a, b), planos) in enumerate(zip(tramos, guion)):
            n = len(planos)
            for j, p in enumerate(planos):
                ta, tb = a + (b - a) * j / n, a + (b - a) * (j + 1) / n
                pid = f"{cid}_{k:02d}{'ab'[j] if n > 1 else ''}"
                if "reusar" in p:
                    ref = [x for x in out[base:] if x["id"].startswith(f"{cid}_{p['reusar']:02d}")][0]
                    out.append({"id": pid, "cancion": audio, "t0": round(ta, 3), "t1": round(tb, 3), "reusar": ref["id"]})
                else:
                    out.append({"id": pid, "cancion": audio, "t0": round(ta, 3), "t1": round(tb, 3), **p})
    return out


if __name__ == "__main__":
    pl = construir()
    json.dump(pl, open(f"{AQUI}/planos.json", "w"), ensure_ascii=False, indent=1)
    nuevos = [p for p in pl if "reusar" not in p]
    print(f"✅ planos.json: {len(pl)} planos ({len(nuevos)} fotogramas nuevos, {len(pl)-len(nuevos)} reutilizados)")
    largos = [p["id"] for p in pl if p["t1"] - p["t0"] > 5.5]
    print("planos de más de 5,5 s (se partirán al animar):", largos)
