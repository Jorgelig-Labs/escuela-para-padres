"""Configuración del kit: secretos en `.env`, ajustes en `config.json`. Nada queda escrito en el código.

  .env          OBS_PASSWORD, ELEVENLABS_API_KEY…  (privado, nunca se comparte ni se sube)
  config.json   modelo de whisper, carpeta de trabajo, contexto de la transcripción, voces…
"""
import json
import os
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(KIT, ".env")
CONFIG_PATH = os.path.join(KIT, "config.json")


def _cargar_env():
    """Lee `.env` (CLAVE=valor, una por línea, # para comentarios) sin dependencias. Lo que ya venga
    en el entorno de la terminal tiene prioridad."""
    if not os.path.exists(ENV_PATH):
        return
    for linea in open(ENV_PATH, encoding="utf-8"):
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, v = linea.split("=", 1)
        v = v.strip().strip('"').strip("'")
        if v:
            os.environ.setdefault(k.strip(), v)


_cargar_env()


def secreto(nombre, para):
    """Devuelve un secreto del `.env` o termina con un mensaje claro (sin traceback)."""
    v = os.environ.get(nombre, "").strip()
    if not v:
        sys.exit(f"Falta {nombre} en {ENV_PATH}.\n"
                 f"Se necesita para {para}. Abre el archivo .env, pega el valor después de "
                 f"{nombre}= y guarda. (Si no existe .env, copia .env.example y renómbralo.)")
    return v


def ajustes():
    base = {
        "carpeta_trabajo": "~/Movies/Kit-Ponencias",
        "whisper_modelo": "small",
        "whisper_hilos": 5,
        "contexto_transcripcion": "Conferencia en español.",
        "obs": {"lienzo": [1920, 1080], "escena": "Kit Ponencias"},
    }
    if os.path.exists(CONFIG_PATH):
        base.update(json.load(open(CONFIG_PATH, encoding="utf-8")))
    base["carpeta_trabajo"] = os.path.expanduser(base["carpeta_trabajo"])
    return base
