#!/usr/bin/env python3
"""Da de alta en el catálogo del sitio (content/videos.json) los videos de libros ya producidos.

  alta_sitio.py <raíz del sitio> <grupo: refuerzo|resumenes|series> <carpeta de specs>

Por cada spec cuyo MP4 exista en <sitio>/videos-libros/<grupo>/<id>.mp4: saca un poster (vertical u horizontal,
nativo) a public/assets/libro-<id>.jpg y crea o actualiza su entrada con status "published". Los títulos y
autores salen del spec, que a su vez salen de la bibliografía verificada. No toca entradas de otros grupos.
"""
import glob
import json
import os
import re
import subprocess
import sys

sitio, grupo, specs = sys.argv[1], sys.argv[2], sys.argv[3]
GRUPO = {"refuerzo": "refuerzo", "resumenes": "resumen", "series": "serie"}[grupo]
fichas = {}
for f in glob.glob(f"{sitio}/content/libros/*.md"):
    m = json.loads(re.match(r"^---\n([\s\S]+?)\n---\n", open(f).read()).group(1))
    fichas[m["id"]] = m


def limpio(texto):
    return re.sub(r"^\[[^\]]*\]\s*", "", texto).strip()


def frase(texto, n=150):
    t = limpio(texto)
    return t if len(t) <= n else t[:t.rfind(" ", 0, n)].rstrip(",;:") + "…"


def orden(s, lid):
    """Rangos fijos por grupo: junta 1–99 · refuerzo 100–199 · resumen 200–299 · serie 300–399."""
    n_libro = fichas.get(lid, {}).get("order", 0)
    if GRUPO == "refuerzo":
        return 100 + int(re.sub(r"\D", "", s["id"].split("-")[0]) or 0)
    if GRUPO == "resumen":
        return 200 + n_libro
    return 300 + (n_libro - 1) * 3 + s["episodio"]


videos = json.load(open(f"{sitio}/content/videos.json"))
por_id = {v["id"]: v for v in videos}
nuevos = 0
for sp in sorted(glob.glob(f"{specs}/*.json")):
    s = json.load(open(sp))
    mp4 = f"{sitio}/videos-libros/{grupo}/{s['id']}.mp4"
    if not os.path.exists(mp4):
        continue
    vid = s["id"].lower()
    libros = s.get("libros") or [{k: s.get(k) for k in ("libro_id", "titulo", "autor", "donde", "derechos")}]
    lid = libros[0].get("libro_id") or s.get("libro_id")
    derechos = any(l.get("derechos") for l in libros)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", mp4]))
    vertical = s.get("formato") == "vertical"
    poster = f"public/assets/libro-{vid}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{min(dur * 0.3, 12):.1f}", "-i", mp4, "-frames:v", "1",
                    "-vf", "scale=540:960" if vertical else "scale=960:540", "-q:v", "3", f"{sitio}/{poster}"], check=True)
    narracion = next((t for _, voz, t in s["segmentos"] if voz == "marisol"), s["segmentos"][0][2])
    if GRUPO == "refuerzo":
        titulo = s.get("tema") or s["id"]
        autor = " · ".join(dict.fromkeys(l["autor"] for l in libros if l.get("autor")))
    elif GRUPO == "resumen":
        titulo = f"Resumen: {s['titulo']}"
        autor = s["autor"]
    else:
        corto = s.get("titulo_corto") or s["titulo"]
        titulo = f"{corto} · {s['episodio']}/{s['de']}"
        autor = s["autor"]
    e = por_id.get(vid, {"id": vid, "type": "video"})
    e.update({
        "title": titulo, "author": autor or "Entre nosotros",
        "topic": fichas.get(lid, {}).get("topic", "Crianza"),
        "description": (fichas.get(lid, {}).get("description") if GRUPO == "resumen" else None) or frase(narracion),
        "duration": round(dur, 1),
        "file": os.path.relpath(mp4, sitio), "poster": "/" + poster.replace("public/", ""),
        "label": {"refuerzo": "Para hoy", "resumen": "Resumen del libro", "serie": "Serie"}[GRUPO],
        "order": orden(s, lid),
        "status": "published", "group": GRUPO, "orientation": "vertical" if vertical else "horizontal",
        "note": "Narración con voz generada." + (" No sustituye la lectura del libro." if derechos else ""),
    })
    if lid in fichas:
        e["book"] = lid
    if GRUPO == "serie":
        e.update({"series": s.get("serie", lid), "episode": s["episodio"], "of": s["de"]})
    if vid not in por_id:
        videos.append(e)
        por_id[vid] = e
        nuevos += 1
open(f"{sitio}/content/videos.json", "w").write(json.dumps(videos, ensure_ascii=False, indent=2) + "\n")
print(f"{grupo}: {nuevos} nuevos, {sum(1 for v in videos if v.get('group') == GRUPO)} en total")
