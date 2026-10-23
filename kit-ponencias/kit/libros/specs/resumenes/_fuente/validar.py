import os
# -*- coding: utf-8 -*-
import json, re, glob, sys
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # la carpeta de specs de este grupo
IDS = "el-hogar-cristiano conduccion-del-nino la-educacion mente-caracter-y-personalidad los-5-lenguajes-del-amor edad-de-oportunidades limites-con-los-adolescentes crianza-llena-de-gracia habla-claro-con-tus-hijos padres-confiados manten-encendido-tu-amor como-criar-jovenes-de-fe-solida".split()
PROH = re.compile(r"\bjunta\b|charla|reuni[oó]n|presentaci[oó]n|bibliograf|denny|perales|diapositiva|ponente|\bvimos\b|reto de siete|d[ií]a (tres|cuatro|seis)|libro (uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce)\b", re.I)
TIPOS = {"titular","reaccion","cita","icono","ilustracion","tarjeta_libro","ideas","accion"}
VOCES = {"marisol","rewe","mario"}
tot = 0; totw = 0; err = 0
for i, f in enumerate(sorted(glob.glob(D + "/*.json")), 1):
    s = json.load(open(f, encoding="utf-8"))
    problemas = []
    txt = {}
    for sid, voz, t in s["segmentos"]:
        if voz not in VOCES: problemas.append(f"voz {voz}")
        if not re.match(r"^\[[^\]]+\] \S", t): problemas.append(f"sin etiqueta {sid}")
        txt[sid] = re.sub(r"^\[.*?\]\s*", "", t)
    voz_txt = " ".join(txt.values())
    ch = sum(len(v) for v in txt.values()); w = len(voz_txt.split())
    tot += ch; totw += w
    if not 320 <= w <= 440: problemas.append(f"palabras {w} fuera de 320-440")
    if s["libro_id"] != IDS[i-1]: problemas.append("libro_id")
    if s["derechos"] != (i >= 5): problemas.append("derechos")
    if PROH.search(json.dumps(s["segmentos"], ensure_ascii=False) + json.dumps(s["beats"], ensure_ascii=False)): problemas.append("PROHIBIDA: " + PROH.search(json.dumps(s["segmentos"], ensure_ascii=False) + json.dumps(s["beats"], ensure_ascii=False)).group(0))
    if len(s["beats"]) < 12: problemas.append("pocos beats")
    for b in s["beats"]:
        if b["tipo"] not in TIPOS: problemas.append("tipo " + b["tipo"])
        if b["seg"] not in txt: problemas.append("seg " + b["seg"]); continue
        if b["palabra"] not in txt[b["seg"]]: problemas.append(f"palabra huerfana '{b['palabra']}' en {b['seg']}")
    last = list(txt.values())[-1]
    if i >= 5:
        if not last.endswith("Este video no sustituye la lectura del libro."): problemas.append("cierre sin NOSUST")
        for q in re.findall(r"«([^»]+)»", voz_txt):
            if len(q.split()) > 25: problemas.append("cita >25")
    else:
        if "egw" not in last.lower() and "e ge doble u" not in last: problemas.append("cierre EGW sin egwwritings")
    print(f"{i:02d} {s['libro_id']:36s} palabras={w:4d} chars={ch:5d} ~{w/187*60:5.0f}s beats={len(s['beats'])} segs={len(s['segmentos'])}", "OK" if not problemas else problemas)
    err += len(problemas)
print("TOTAL chars voz:", tot, "palabras:", totw, "problemas:", err)
