#!/bin/bash
# Videos de libros con voz en off (ElevenLabs), música y animación, a partir de guiones (especificaciones JSON).
source "$(dirname "$0")/kit/comun.sh"
cd "$KIT/kit/libros"

carpeta=$(osascript -e "POSIX path of (choose folder with prompt \"Elige la carpeta de guiones (por ejemplo specs/resumenes)\" default location (POSIX file \"$KIT/kit/libros/specs\"))" 2>/dev/null) || exit 0
carpeta=${carpeta%/}
ls "$carpeta"/*.json >/dev/null 2>&1 || fallo "Esa carpeta no tiene guiones (.json)."

total=0; malos=""
for f in "$carpeta"/*.json; do
  python3 -I generar.py "$f" --validar >/dev/null 2>&1 || malos="$malos $(basename "$f")"
  c=$(python3 -I generar.py "$f" --contar 2>/dev/null | sed -nE 's/.* ([0-9]+) por generar.*/\1/p')
  total=$((total + ${c:-0}))
done
[ -n "$malos" ] && fallo "Estos guiones tienen errores:$malos. Corre «python3 generar.py <guion> --validar» para ver el detalle."

r=$(elegir "Se van a generar $(ls "$carpeta"/*.json | wc -l | tr -d ' ') videos.\n\nCosto de voz: ~$total caracteres de ElevenLabs (los que ya se generaron antes no se vuelven a cobrar).\n\nTarda ~2 min por video." "Generar" "Cancelar")
[ "$r" = "Generar" ] || exit 0
secreto=$("$PY" -c "import sys; sys.path.insert(0,'$KIT/kit'); from config import secreto; secreto('ELEVENLABS_API_KEY','la voz en off')" 2>&1) || fallo "$secreto"

salida="$(carpeta_trabajo)/videos-libros/$(basename "$carpeta")"
notificar "Generando videos de libros…"
./producir.sh "$salida" "$carpeta"/*.json
codigo=$?
open "$salida"
if [ $codigo -eq 2 ]; then
  fallo "Se detuvo por un error de ElevenLabs (créditos o permisos). Lo hecho se conserva; al volver a correr, continúa donde se quedó."
fi
notificar "Videos de libros listos"
avisar "Listo. Los videos están en:\n$salida\n\nEl detalle de cada uno está en produccion.log."
