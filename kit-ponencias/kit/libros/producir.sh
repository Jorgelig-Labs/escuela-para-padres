#!/bin/bash
# producir.sh <carpeta_salida> <spec.json…>
# Genera en serie (voz → armado → render) y deja un registro. Se detiene en el primer error de ElevenLabs
# (créditos o permisos) para no seguir gastando. Los videos que ya existen en la salida se saltan.
cd "$(dirname "$0")"
salida=$1; shift
mkdir -p "$salida"
registro="$salida/produccion.log"
for spec in "$@"; do
  id=$(python3 -I -c "import json,sys; print(json.load(open(sys.argv[1]))['id'])" "$spec")
  destino="$salida/$id.mp4"
  [ -f "$destino" ] && { echo "$(date '+%H:%M') = $id (ya existe)" >> "$registro"; continue; }
  echo "$(date '+%H:%M') ▶ $id" >> "$registro"
  if out=$(python3 -I generar.py "$spec" --salida "$destino" </dev/null 2>&1); then
    echo "$out" | grep -E "LISTO|TOTAL" | sed "s/^/   /" >> "$registro"
  else
    echo "$out" | tail -5 | sed "s/^/   ✗ /" >> "$registro"
    if echo "$out" | grep -qiE "ElevenLabs|4[0-9][0-9]|crédit|quota|credit"; then
      echo "$(date '+%H:%M') ■ detenido: error de ElevenLabs (revisa créditos o permisos)" >> "$registro"
      exit 2
    fi
  fi
done
echo "$(date '+%H:%M') ✓ terminado" >> "$registro"
