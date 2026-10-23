#!/bin/bash
# Instala todo lo que necesita el Kit Ponencias en una Mac (Apple Silicon o Intel).
# Se puede correr las veces que quieras: lo que ya está instalado se salta.
set -e
cd "$(dirname "$0")"
KIT="$(pwd)"
paso() { printf '\n\033[1;35m▶ %s\033[0m\n' "$1"; }
alto() { osascript -e "display alert \"Instalación detenida\" message \"$1\" as critical" >/dev/null 2>&1; echo "✗ $1"; exit 1; }

echo "════════════════════════════════════════════"
echo "  Kit Ponencias · instalación"
echo "  Tarda de 10 a 30 minutos la primera vez."
echo "  Si te pide tu contraseña de la Mac, escríbela"
echo "  (no se ven los caracteres al teclear) y Enter."
echo "════════════════════════════════════════════"

paso "1/7 Herramientas de desarrollo de Apple (para el reconocimiento de texto y de ventanas)"
if ! xcode-select -p >/dev/null 2>&1; then
  xcode-select --install || true
  osascript -e 'display dialog "Se abrió una ventana de Apple para instalar las «herramientas de línea de comandos». Presiona Instalar, espera a que termine y luego presiona OK aquí." buttons {"OK"} with title "Kit Ponencias"' >/dev/null
  xcode-select -p >/dev/null 2>&1 || alto "Faltan las herramientas de Apple. Vuelve a abrir instalar.command cuando terminen de instalarse."
fi

paso "2/7 Homebrew (instalador de programas)"
if ! command -v brew >/dev/null 2>&1; then
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)"; done
fi
if ! command -v brew >/dev/null 2>&1; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)"; done
fi
command -v brew >/dev/null 2>&1 || alto "No se pudo instalar Homebrew."

paso "3/7 ffmpeg (video), whisper (transcripción), Python y Node"
brew install ffmpeg openai-whisper python node

paso "4/7 OBS (grabación de pantalla)"
if [ ! -d "/Applications/OBS.app" ]; then brew install --cask obs; else echo "OBS ya está instalado."; fi

paso "5/7 Entorno de Python del kit"
PYBASE="$(brew --prefix python)/bin/python3"
[ -x .venv/bin/python ] || "$PYBASE" -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt

paso "6/7 Ayudantes de macOS (ventanas de Zoom y lectura de nombres)"
swiftc -O kit/swift/ventanas.swift -o kit/swift/ventanas
swiftc -O kit/swift/ocr.swift -o kit/swift/ocr

paso "7/7 Modelo de transcripción y permisos de los atajos"
modelo=$(.venv/bin/python -c "import sys; sys.path.insert(0,'kit'); from config import ajustes; print(ajustes()['whisper_modelo'])")
if [ ! -f "$HOME/.cache/whisper/$modelo.pt" ]; then
  echo "Descargando el modelo «$modelo» (una sola vez)…"
  ffmpeg -v error -y -f lavfi -i anullsrc=r=16000:cl=mono -t 1 /tmp/kit-silencio.wav
  whisper /tmp/kit-silencio.wav --model "$modelo" --language es --fp16 False --output_dir /tmp --output_format txt >/dev/null 2>&1 || true
fi
chmod +x ./*.command kit/*.sh
xattr -dr com.apple.quarantine . 2>/dev/null || true
mkdir -p "$(.venv/bin/python -c "import sys; sys.path.insert(0,'kit'); from config import ajustes; print(ajustes()['carpeta_trabajo'])")"

if [ ! -f .env ]; then cp .env.example .env; fi
echo
echo "✓ Instalación completa."
osascript -e 'display dialog "Instalación completa.\n\nFalta un paso tuyo: se va a abrir el archivo .env para que pegues la contraseña de OBS (y la llave de ElevenLabs, si vas a hacer videos de libros). Guarda con ⌘S.\n\nDespués sigue la guía «LEEME.md» para darle permisos a OBS." buttons {"Abrir .env"} with title "Kit Ponencias"' >/dev/null
open -e .env
