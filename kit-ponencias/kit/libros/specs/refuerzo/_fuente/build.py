# -*- coding: utf-8 -*-
import json, re, unicodedata, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from data2 import CAPS, LIB, NOSUST
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # la carpeta de specs de este grupo
def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ ]+", " ", s)
BAD = ["denny","perales","charla","junta","ponente","diapositiva","darling","caldwell","grabaci"]
tot = 0; problems = []
for c in CAPS:
    segs = {s[0]: s for s in c["segmentos"]}
    assert len(segs) == len(c["segmentos"]), c["id"]
    voz = 0; words = 0
    for n, v, t in c["segmentos"]:
        assert v in ("marisol", "rewe", "mario") and t.startswith("["), (c["id"], n)
        spoken = re.sub(r"^\[[^\]]*\]\s*", "", t); voz += len(spoken); words += len(spoken.split())
    tot += voz
    for bt in c["beats"]:
        if bt["seg"] not in segs: problems.append((c["id"], "seg?", bt["seg"])); continue
        if norm(bt["palabra"]).strip() not in norm(segs[bt["seg"]][2]): problems.append((c["id"], "palabra?", bt["seg"], bt["palabra"]))
    full = json.dumps(c, ensure_ascii=False).lower()
    for w in BAD:
        if w in full and not (w == "junta" and False): problems.append((c["id"], "prohibida", w))
    for q in re.findall(r"«([^»]+)»", " ".join(s[2] for s in c["segmentos"])):
        if len(q.split()) > 25: problems.append((c["id"], "cita larga", q))
    hasder = any(LIB[l][3] for l in c["libros"])
    if hasder and not any(b["texto"] == NOSUST for b in c["beats"]): problems.append((c["id"], "falta NOSUST"))
    libs = [{"libro_id": l, "titulo": LIB[l][0], "autor": LIB[l][1], "donde": LIB[l][2], "derechos": LIB[l][3]} for l in c["libros"]]
    d = {"id": c["id"], "formato": "vertical", "tema": c["tema"], "libros": libs,
         "segmentos": [list(s) for s in c["segmentos"]], "beats": c["beats"], "fuentes": c["fuentes"]}
    json.dump(d, open(f"{OUT}/{c['id']}.json", "w"), ensure_ascii=False, indent=1)
    print(f"{c['id']:42s} chars={voz:4d} palabras={words:3d} ~{words/185*60:3.0f}s beats={len(c['beats'])}")
print("TOTAL chars voz:", tot)
print("PROBLEMAS:", problems)
