# -*- coding: utf-8 -*-
"""Voz en off con ElevenLabs y caché por segmento.

- Un segmento solo se vuelve a generar si cambió su texto, su voz (id), el modelo o los ajustes de voz.
- Cada llamada suma el header `character-cost` en `gasto.csv` (junto a la especificación).
- Cualquier error 4xx (créditos, permisos, límite) detiene todo y se reporta: nunca se reintenta en bucle.
  Solo los errores de red o 5xx se reintentan, 2 veces.
- La llave sale de kit-ponencias/.env vía kit/config.py (`secreto`). Nunca se imprime.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


class ErrorVoz(Exception):
    pass


def cargar_voz_cfg():
    return json.load(open(os.path.join(HERE, "voz.json"), encoding="utf-8"))


def _firma(cfg, voz):
    return {"voice_id": cfg["voces"][voz]["voice_id"], "modelo": cfg["modelo"], "settings": cfg["voice_settings"]}


def en_cache(seg, audio_dir, cfg):
    """True si el mp3 y su json existen y siguen vigentes para este texto/voz/modelo/ajustes."""
    mp3 = os.path.join(audio_dir, f"{seg['nombre']}.mp3")
    js = os.path.join(audio_dir, f"{seg['nombre']}.json")
    if not (os.path.exists(mp3) and os.path.exists(js)):
        return False
    try:
        d = json.load(open(js, encoding="utf-8"))
    except Exception:
        return False
    if d.get("text") != seg["texto"] or d.get("voz") != seg["voz"] or "alignment" not in d:
        return False
    f = d.get("firma")           # los json copiados del piloto no la traen: cuentan como vigentes
    return f is None or f == _firma(cfg, seg["voz"])


def pendientes(segs, audio_dir, cfg):
    return [s for s in segs if not en_cache(s, audio_dir, cfg)]


def caracteres(segs):
    """Lo que cobra ElevenLabs: el texto completo, etiqueta de tono incluida."""
    return sum(len(s["texto"]) for s in segs)


def _llamar(seg, i, segs, cfg, key):
    body = {"text": seg["texto"], "model_id": cfg["modelo"], "voice_settings": cfg["voice_settings"]}
    if i > 0:
        body["previous_text"] = segs[i - 1]["texto"][-300:]
    if i < len(segs) - 1:
        body["next_text"] = segs[i + 1]["texto"][:300]
    url = (f"https://api.elevenlabs.io/v1/text-to-speech/{cfg['voces'][seg['voz']]['voice_id']}"
           f"/with-timestamps?output_format=mp3_44100_128")
    for intento in range(3):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                     headers={"xi-api-key": key, "Content-Type": "application/json"})
        try:
            r = urllib.request.urlopen(req, timeout=180)
            return int(r.headers.get("character-cost", len(seg["texto"]))), json.loads(r.read())
        except urllib.error.HTTPError as e:
            cuerpo = e.read()[:300].decode("utf-8", "ignore")
            if 400 <= e.code < 500:      # créditos, permisos, límite: no se reintenta
                raise ErrorVoz(f"ElevenLabs respondió {e.code} en el segmento «{seg['nombre']}»: {cuerpo}\n"
                               f"Se detuvo. Revisa créditos y permisos de la llave (Text to Speech) y vuelve a correr: "
                               f"lo ya generado quedó en caché.")
            err = f"{e.code} {cuerpo}"
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            err = str(e)
        if intento == 2:
            raise ErrorVoz(f"Falló la llamada a ElevenLabs en «{seg['nombre']}» tras 3 intentos: {err}")
        time.sleep(5 * (intento + 1))


def generar(segs, audio_dir, csv_path, video_id, presupuesto=None):
    """Genera lo que falte. Devuelve los caracteres cobrados en esta corrida."""
    cfg = cargar_voz_cfg()
    os.makedirs(audio_dir, exist_ok=True)
    for s in segs:
        if s["voz"] not in cfg["voces"]:
            raise ErrorVoz(f"Segmento «{s['nombre']}»: la voz «{s['voz']}» no existe. Opciones: {', '.join(cfg['voces'])}")
    pend = pendientes(segs, audio_dir, cfg)
    if not pend:
        print("voz: todo en caché (0 caracteres)")
        return 0
    a_gastar = caracteres(pend)
    if presupuesto is not None and a_gastar > presupuesto:
        raise ErrorVoz(f"Presupuesto excedido: faltan {a_gastar} caracteres de voz y el máximo es {presupuesto}. "
                       f"Acorta la narración o sube `presupuesto_caracteres` en la especificación.")
    sys.path.insert(0, os.path.dirname(HERE))          # kit/config.py
    from config import secreto
    key = secreto("ELEVENLABS_API_KEY", "generar la voz en off de los videos")
    if not os.path.exists(csv_path):
        open(csv_path, "w", encoding="utf-8").write("video,segmento,voz,caracteres_header,caracteres_texto,fecha\n")
    total = 0
    for i, s in enumerate(segs):
        if s not in pend:
            continue
        cost, d = _llamar(s, i, segs, cfg, key)
        open(os.path.join(audio_dir, f"{s['nombre']}.mp3"), "wb").write(base64.b64decode(d["audio_base64"]))
        json.dump({"text": s["texto"], "voz": s["voz"], "alignment": d["alignment"], "cost": cost,
                   "firma": _firma(cfg, s["voz"])},
                  open(os.path.join(audio_dir, f"{s['nombre']}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        open(csv_path, "a", encoding="utf-8").write(
            f"{video_id},{s['nombre']},{s['voz']},{cost},{len(s['texto'])},{time.strftime('%F %T')}\n")
        total += cost
        print(f"voz: {s['nombre']} ({s['voz']}) {len(s['texto'])} car., cobrado {cost}")
    print(f"voz: TOTAL esta corrida {total} caracteres")
    return total
