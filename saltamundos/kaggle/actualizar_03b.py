#!/usr/bin/env python3
"""Mete la lista de planos actual (planos.json) dentro del cuaderno 03b."""
import json, os, re
AQUI = os.path.dirname(os.path.abspath(__file__))
pl = [p for p in json.load(open(f"{AQUI}/../planos.json")) if "reusar" not in p]
compact = json.dumps([[p["id"], p["refs"], p["escena"]] for p in pl], ensure_ascii=False)
f = f"{AQUI}/03b_fotogramas_todos.py"
s = open(f).read()
s, n = re.subn(r'PLANOS = json\.loads\(r""".*?"""\)', lambda m: f'PLANOS = json.loads(r"""{compact}""")', s, flags=re.S)
assert n == 1
open(f, "w").write(s)
print(f"✅ 03b actualizado con {len(pl)} planos")
