#!/bin/bash
# Graba la reunión de Zoom abierta (video y audio de Zoom) con OBS, sin ser anfitrión.
source "$(dirname "$0")/kit/comun.sh"
cd "$KIT"

open -ga OBS || fallo "No encontré OBS. Instálalo con instalar.command."
echo "Esperando a OBS…"
for i in $(seq 1 20); do
  "$PY" kit/grabar_zoom.py status >/dev/null 2>&1 && break
  sleep 1
done
salida=$("$PY" kit/grabar_zoom.py start 2>&1) || fallo "$salida"
echo "$salida"

while true; do
  r=$(elegir "● GRABANDO la reunión de Zoom.\n\nDeja Zoom abierto en la vista con la presentación. Si mueves o agrandas la ventana de Zoom, presiona «Reencuadrar».\n\nCuando termine la reunión, presiona «Detener grabación»." "Detener grabación" "Reencuadrar")
  if [ "$r" = "Reencuadrar" ]; then
    "$PY" kit/grabar_zoom.py ajustar
  else
    break
  fi
done
fin=$("$PY" kit/grabar_zoom.py stop 2>&1)
echo "$fin"
archivo=$(echo "$fin" | sed -n 's/.*guardada en: //p')
[ -n "$archivo" ] && open -R "$archivo"
avisar "Listo. $fin\n\nSiguiente paso: «2 Analizar grabación»."
