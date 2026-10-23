#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera un video de libro a partir de una especificación JSON: voz -> armado -> render -> normalizado.

  python3 generar.py <spec.json>                 # todo
  python3 generar.py <spec.json> --validar       # sin gastar ni renderizar: revisa anclas, texto y maquetación
  python3 generar.py <spec.json> --contar        # cuántos caracteres de voz faltan por generar
  python3 generar.py <spec.json> --sin-voz       # usa solo la voz en caché (falla si falta algún segmento)
  python3 generar.py <spec.json> --solo-html     # arma el proyecto pero no renderiza
Opciones: --cola RUTA  --salida ARCHIVO.mp4  --calidad standard|draft|high
La cola de render: --cola > variable KIT_COLA_RENDER > kit/vigilante.sh (mismo uso: <log> <comando…>).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plantilla
import simple
import voz


def tail(path, n=6):
    try:
        return "".join(open(path, encoding="utf-8", errors="ignore").readlines()[-n:])
    except OSError:
        return ""


def cola_render(arg):
    c = arg or os.environ.get("KIT_COLA_RENDER") or os.path.join(os.path.dirname(HERE), "vigilante.sh")
    if not os.path.exists(c):
        sys.exit(f"No encuentro la cola de render «{c}». Usa --cola o define KIT_COLA_RENDER.")
    return c


def main():
    ap = argparse.ArgumentParser(description="Generador de videos de libros")
    ap.add_argument("spec")
    ap.add_argument("--validar", action="store_true")
    ap.add_argument("--contar", action="store_true")
    ap.add_argument("--sin-voz", action="store_true")
    ap.add_argument("--solo-html", action="store_true")
    ap.add_argument("--cola")
    ap.add_argument("--salida")
    ap.add_argument("--calidad", default="standard")
    a = ap.parse_args()

    spec_path = os.path.abspath(a.spec)
    carpeta = os.path.dirname(spec_path)
    spec = simple.cargar(spec_path)
    plantilla.validar(spec, carpeta)
    vid = str(spec["id"])
    trabajo = os.path.join(carpeta, "_trabajo", vid)
    audio, proyecto = os.path.join(trabajo, "audio"), os.path.join(trabajo, "proyecto")
    csv = os.path.join(carpeta, "gasto.csv")
    segs = spec["segmentos"]
    cfg = voz.cargar_voz_cfg()

    # ── validación / conteo (no gastan nada)
    info = plantilla.construir(spec, audio, proyecto, carpeta, seco=True)
    for av in info["avisos"]:
        print("aviso:", av)
    pend = voz.pendientes(segs, audio, cfg)
    print(f"{vid}: {len(spec['beats'])} beats, formato {spec['formato']}, voz estimada ~{info['voz_hasta']:.0f}s, "
          f"{voz.caracteres(segs)} caracteres de voz en total, {voz.caracteres(pend)} por generar ({len(pend)} segmentos)")
    if a.contar:
        return
    if a.validar:
        print("especificación OK")
        return

    # ── voz
    if a.sin_voz and pend:
        sys.exit("Faltan en caché: " + ", ".join(s["nombre"] for s in pend) + ". Quita --sin-voz para generarlos.")
    try:
        gastado = voz.generar(segs, audio, csv, vid, spec.get("presupuesto_caracteres"))
    except voz.ErrorVoz as e:
        sys.exit(f"ERROR DE VOZ: {e}")

    # ── armado
    os.makedirs(trabajo, exist_ok=True)
    info = plantilla.construir(spec, audio, proyecto, carpeta)
    json.dump(info, open(os.path.join(trabajo, "info.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for av in info["avisos"]:
        print("aviso:", av)
    print(f"proyecto armado: {proyecto} (duración {info['total']}s)")
    if a.solo_html:
        return

    # ── render por la cola compartida (un render a la vez, con vigilante de RAM)
    raw = os.path.join(trabajo, f"{vid}-raw.mp4")
    log = os.path.join(trabajo, "render.log")
    hf = shutil.which("hyperframes")
    cmd_hf = [hf] if hf else ["npx", "--yes", "hyperframes@0.8.188"]
    cmd = [cola_render(a.cola), log] + cmd_hf + ["render", "-w", "2", "-q", a.calidad, "-o", raw, "."]
    print("render:", " ".join(os.path.basename(x) if i == 0 else x for i, x in enumerate(cmd[:2])), "…")
    with open(log, "a", encoding="utf-8") as lf:
        r = subprocess.run(cmd, cwd=proyecto, stdout=lf, stderr=subprocess.STDOUT)
    if r.returncode != 0 or not os.path.exists(raw):
        sys.exit(f"El render terminó con código {r.returncode} (3 = detenido por poca memoria). Últimas líneas de {log}:\n{tail(log)}")

    # ── normalizado a -16 LUFS
    salida = os.path.abspath(a.salida or spec.get("salida") or os.path.join(trabajo, f"{vid}.mp4"))
    if not a.salida and spec.get("salida") and not os.path.isabs(spec["salida"]):
        salida = os.path.abspath(os.path.join(carpeta, spec["salida"]))
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", raw, "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-c:a", "aac", "-b:a", "160k",
                    "-movflags", "+faststart", salida], check=True)
    d = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", salida]).decode().strip()
    print(f"LISTO: {salida} ({float(d):.1f}s) · caracteres de voz cobrados en esta corrida: {gastado}")


if __name__ == "__main__":
    main()
