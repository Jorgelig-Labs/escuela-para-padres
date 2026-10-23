# -*- coding: utf-8 -*-
import json, re, os
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # la carpeta de specs de este grupo
EGW_VOZ = "e ge doble u writings punto org"
NOSUST = "Este video no sustituye la lectura del libro."
CAL = "cálido, cercano, ritmo ágil"
ADO = "adolescente, casual, directo"
LIBROS = []

def libro(n, slug, titulo, autor, donde, derechos, segs, beats, fuentes):
    segmentos = [[i, v, f"[{t}] {x}"] for (i, v, t, x) in segs]
    bs = [dict(tipo=a, seg=b, palabra=c, texto=d, visual=e) for (a, b, c, d, e) in beats]
    spec = dict(id=f"resumen-{slug}", formato="horizontal", libro_id=slug, titulo=titulo, autor=autor,
                donde=donde, derechos=derechos, segmentos=segmentos, beats=bs, fuentes=fuentes)
    LIBROS.append((n, slug, spec))

def emit():
    os.makedirs(OUT, exist_ok=True)
    for n, slug, spec in LIBROS:
        with open(f"{OUT}/{n:02d}-{slug}.json", "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=1)
