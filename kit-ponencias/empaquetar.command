#!/bin/bash
# Crea un ZIP del kit para instalarlo en otra Mac. NUNCA incluye .env (tus contraseñas), ni el entorno
# de Python, ni respaldos, ni audios de prueba.
cd "$(dirname "$0")"
n=$(basename "$PWD")
destino="$HOME/Desktop/kit-ponencias-$(date +%Y%m%d).zip"
cd ..
rm -f "$destino"
zip -qr "$destino" "$n" \
  -x "$n/.env" "$n/.venv/*" "$n/_respaldo-sesion/*" "$n/kit/swift/ocr" "$n/kit/swift/ventanas" \
     '*/__pycache__/*' '*.DS_Store' "$n/borradores/*/audio/*" "$n/borradores/*/*/audio/*" \
     "$n/borradores/*/*/txt/*" "$n/borradores/*/*/libros-txt/*" '*.mp3' '*.mp4' '*.wav' '*.mkv'
if unzip -l "$destino" | grep -qE '/\.env$|/\.venv/'; then rm -f "$destino"; echo "✗ El ZIP incluía .env; lo borré."; exit 1; fi
echo "✓ $destino ($(du -h "$destino" | cut -f1))"
osascript -e "display dialog \"Listo: kit-ponencias en tu Escritorio.\n\nEn la otra Mac: descomprímelo, haz clic derecho en instalar.command → Abrir, y sigue LEEME.md. Las contraseñas NO van incluidas: se ponen en el .env de esa Mac.\" buttons {\"OK\"} with title \"Kit Ponencias\"" >/dev/null
open -R "$destino"
