#!/bin/bash
# Funciones compartidas por los .command: rutas, ventanas de diálogo y avisos.
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
PY="$KIT/.venv/bin/python"
CAPS="$KIT/kit/capsulas.py"

if [ ! -x "$PY" ]; then
  osascript -e 'display alert "Falta instalar el kit" message "Primero haz doble clic en «instalar.command»." as critical' >/dev/null
  exit 1
fi

carpeta_trabajo() { "$PY" -c "import sys; sys.path.insert(0,'$KIT/kit'); from config import ajustes; print(ajustes()['carpeta_trabajo'])"; }

# preguntar "Pregunta" "valor por omisión" → imprime lo que escribió el usuario (sale si cancela)
preguntar() {
  osascript -e "text returned of (display dialog \"$1\" default answer \"$2\" with title \"Kit Ponencias\")" 2>/dev/null || exit 0
}
# elegir "Mensaje" "Opción A" "Opción B" … → imprime el botón elegido (máximo 3)
elegir() {
  local msg=$1; shift
  local botones; botones=$(printf '"%s", ' "$@"); botones=${botones%, }
  osascript -e "button returned of (display dialog \"$msg\" buttons {$botones} default button 1 with title \"Kit Ponencias\")" 2>/dev/null || exit 0
}
elegir_video() {
  osascript -e "POSIX path of (choose file with prompt \"$1\" default location (path to movies folder))" 2>/dev/null || exit 0
}
elegir_analisis() {
  local d
  d=$(osascript -e "POSIX path of (choose folder with prompt \"$1\" default location (POSIX file \"$(carpeta_trabajo)\"))" 2>/dev/null) || exit 0
  d=${d%/}
  if [ ! -f "$d/meta.json" ]; then
    osascript -e 'display alert "Esa carpeta no es un análisis" message "Elige la carpeta que creó «2 Analizar grabación» (tiene un archivo meta.json)." as warning' >/dev/null
    exit 1
  fi
  echo "$d"
}
avisar() { osascript -e "display dialog \"$1\" buttons {\"OK\"} default button 1 with title \"Kit Ponencias\"" >/dev/null 2>&1; }
notificar() { osascript -e "display notification \"$1\" with title \"Kit Ponencias\" sound name \"Glass\"" >/dev/null 2>&1; }
fallo() { osascript -e "display alert \"Algo falló\" message \"$1\" as critical" >/dev/null 2>&1; exit 1; }

# mm:ss o hh:mm:ss → segundos (vacío → vacío)
a_segundos() {
  [ -z "$1" ] && return
  echo "$1" | awk -F: '{ s=0; for (i=1;i<=NF;i++) s=s*60+$i; print s }'
}
slug() {
  "$PY" -c 'import re, sys, unicodedata
t = unicodedata.normalize("NFKD", sys.argv[1]).encode("ascii", "ignore").decode().lower()
print((re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:50]) or "ponencia")' "$1"
}
