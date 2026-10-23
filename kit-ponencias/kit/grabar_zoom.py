#!/usr/bin/env python3
"""Graba una reunión de Zoom (video + audio de Zoom) con OBS, aunque no seas anfitrión.

  grabar_zoom.py start     prepara la escena y empieza a grabar
  grabar_zoom.py ajustar   vuelve a encuadrar si moviste o maximizaste la ventana de Zoom
  grabar_zoom.py stop      detiene y dice dónde quedó el archivo
  grabar_zoom.py status    ¿está grabando? ¿cuánto lleva?
  grabar_zoom.py list      monitores y ventanas de Zoom que ve la Mac

Cómo encuadra (lo que funcionó en la práctica): OBS captura la **aplicación Zoom** en el monitor donde
está su ventana más grande, y la escena se recorta exactamente a esa ventana; así no se graba el resto de
la pantalla, aunque haya otras apps en ese monitor. La captura «por ventana» de OBS falla con Zoom
(«Invalid target window ID»), por eso no se usa. El recorte va en píxeles reales del monitor (×2 en
Retina, ×1 en monitores normales).

La contraseña de obs-websocket va en `.env` (OBS_PASSWORD). El lienzo se pone en 1920×1080 para que el
recuadro del ponente no salga diminuto.
"""
import logging
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import KIT, ajustes, secreto  # noqa: E402

try:
    import obsws_python as obs
except ImportError:
    sys.exit("Falta obsws-python. Corre instalar.command otra vez.")

CFG = ajustes()
SCENE = CFG["obs"]["escena"]
LIENZO = CFG["obs"]["lienzo"]
ZOOM_BUNDLE = "us.zoom.xos"
VIDEO, AUDIO = "Zoom - Video", "Zoom - Audio"
HELPER = os.path.join(KIT, "kit", "swift", "ventanas")


def client():
    logging.getLogger("obsws_python").setLevel(logging.CRITICAL)  # sin tracebacks: el mensaje va abajo
    pwd = secreto("OBS_PASSWORD", "conectarse a OBS (Herramientas → Configuración de WebSocket)")
    try:
        return obs.ReqClient(host=os.environ.get("OBS_HOST", "localhost"),
                             port=int(os.environ.get("OBS_PORT", "4455")), password=pwd, timeout=5)
    except Exception as e:
        sys.exit(f"No pude conectarme con OBS ({e}).\n¿Está abierto OBS y activado el servidor WebSocket? "
                 "¿La contraseña de .env es la misma que la de OBS?")


def escanear():
    """Monitores y ventanas de Zoom según macOS. No se le pregunta a OBS por la lista de ventanas:
    esa consulta tumba a OBS con las fuentes de ScreenCaptureKit."""
    if not os.path.exists(HELPER):
        sys.exit("Falta el ayudante de ventanas. Corre instalar.command otra vez.")
    monitores, ventanas = [], []
    for linea in subprocess.run([HELPER], capture_output=True, text=True).stdout.splitlines():
        p = linea.split("|")
        if p[0] == "DISPLAY":
            x, y, w, h = map(int, p[2].split(","))
            monitores.append({"uuid": p[1], "x": x, "y": y, "w": w, "h": h, "escala": float(p[3]),
                              "main": p[4] == "main=true"})
        elif p[0] == "WINDOW":
            x, y, w, h = map(int, p[3].split(","))
            ventanas.append({"id": int(p[1]), "titulo": p[2], "x": x, "y": y, "w": w, "h": h,
                             "layer": int(p[4])})
    return monitores, ventanas


def encuadre():
    """Monitor y recorte de la ventana de reunión (la de Zoom más grande en la capa normal)."""
    monitores, ventanas = escanear()
    normales = [v for v in ventanas if v["layer"] == 0]
    if not normales:
        sys.exit("No veo ninguna ventana de Zoom abierta. Entra a la reunión y vuelve a intentar.")
    v = max(normales, key=lambda v: v["w"] * v["h"])
    cx, cy = v["x"] + v["w"] / 2, v["y"] + v["h"] / 2
    m = next((m for m in monitores if m["x"] <= cx < m["x"] + m["w"] and m["y"] <= cy < m["y"] + m["h"]),
             next(m for m in monitores if m["main"]))
    e = m["escala"]
    recorte = {
        "cropLeft": max(0, round((v["x"] - m["x"]) * e)),
        "cropTop": max(0, round((v["y"] - m["y"]) * e)),
        "cropRight": max(0, round((m["x"] + m["w"] - v["x"] - v["w"]) * e)),
        "cropBottom": max(0, round((m["y"] + m["h"] - v["y"] - v["h"]) * e)),
    }
    return m, v, recorte


def preparar(c):
    if not c.get_record_status().output_active:
        c.set_video_settings(numerator=30, denominator=1, base_width=LIENZO[0], base_height=LIENZO[1],
                             out_width=LIENZO[0], out_height=LIENZO[1])
    if SCENE not in [s["sceneName"] for s in c.get_scene_list().scenes]:
        c.create_scene(SCENE)
    entradas = {i["inputName"] for i in c.get_input_list().inputs}
    m, v, recorte = encuadre()
    video = {"type": 2, "application": ZOOM_BUNDLE, "display_uuid": m["uuid"], "show_cursor": False}
    if VIDEO not in entradas:
        c.create_input(SCENE, VIDEO, "screen_capture", video, True)
    else:
        c.set_input_settings(VIDEO, video, True)
    if AUDIO not in entradas:
        # type 1 = audio de una aplicación: solo el sonido de Zoom, no notificaciones ni música
        c.create_input(SCENE, AUDIO, "sck_audio_capture", {"type": 1, "application": ZOOM_BUNDLE}, True)
    item = c.get_scene_item_id(SCENE, VIDEO).scene_item_id
    c.set_scene_item_transform(SCENE, item, {
        **recorte, "boundsType": "OBS_BOUNDS_SCALE_INNER", "boundsWidth": LIENZO[0],
        "boundsHeight": LIENZO[1], "positionX": 0, "positionY": 0, "alignment": 5})
    c.set_current_program_scene(SCENE)
    carpeta = c.get_record_directory().record_directory
    if not os.path.isdir(carpeta):
        carpeta = os.path.join(CFG["carpeta_trabajo"], "grabaciones")
        os.makedirs(carpeta, exist_ok=True)
        c.set_record_directory(carpeta)
    print(f"Encuadre: ventana «{v['titulo'] or 'Zoom'}» {v['w']}×{v['h']} en el monitor "
          f"{m['w']}×{m['h']} (escala {m['escala']:g}).")
    return carpeta


def main():
    cmd = next((a for a in sys.argv[1:] if a in ("start", "stop", "status", "list", "ajustar")), "status")
    if cmd == "list":
        monitores, ventanas = escanear()
        for i, m in enumerate(monitores, 1):
            print(f"Monitor {i}: {m['w']}×{m['h']} en {m['x']},{m['y']} escala {m['escala']:g}"
                  f"{' (principal)' if m['main'] else ''}")
        for v in ventanas:
            print(f"Ventana de Zoom «{v['titulo']}» {v['w']}×{v['h']} en {v['x']},{v['y']} capa {v['layer']}")
        if not ventanas:
            print("(No hay ventanas de Zoom abiertas.)")
        return
    c = client()
    if cmd == "start":
        carpeta = preparar(c)
        if not c.get_record_status().output_active:
            c.start_record()
            time.sleep(2)
        print(f"● Grabando Zoom (video y audio). Los archivos se guardan en {carpeta}")
    elif cmd == "ajustar":
        preparar(c)
        print("Encuadre actualizado.")
    elif cmd == "stop":
        if not c.get_record_status().output_active:
            print("No había una grabación en curso.")
            return
        print(f"■ Grabación guardada en: {c.stop_record().output_path}")
    else:
        s = c.get_record_status()
        print(f"Grabando: {'sí' if s.output_active else 'no'} · duración {s.output_timecode}")


if __name__ == "__main__":
    main()
