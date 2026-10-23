#!/bin/bash
# Video completo editado: diapositiva grande, ponente en recuadro chico y subtítulos.
source "$(dirname "$0")/kit/comun.sh"

dir=$(elegir_analisis "Elige la carpeta del análisis")
tam=$(elegir "¿Qué versión quieres?" "Ligera (WhatsApp / web)" "Alta calidad")
mkdir -p "$dir/videos"
dur=$("$PY" -c "import json; print(json.load(open('$dir/meta.json'))['duracion'])")
echo "[{\"video\": [0, $dur]}]" > "$dir/edl_completo.json"
alta="$dir/videos/video-completo-alta.mp4"

notificar "Creando el video completo. Tarda ~10 min por hora de video."
"$KIT/kit/vigilante.sh" "$dir/render.log" "$PY" "$CAPS" render "$dir" "$dir/edl_completo.json" "$alta" \
  || fallo "El video se detuvo. Si fue por memoria, cierra otras apps y vuelve a intentar."
final="$alta"
if [ "$tam" != "Alta calidad" ]; then
  # Objetivo 280 MB: cabe en WhatsApp y en el límite de 300 MB por archivo de Cloudflare R2.
  kbps=$(awk -v d="$dur" 'BEGIN { v = int(280*8*1024/d) - 96; if (v > 2500) v = 2500; print v }')
  final="$dir/videos/video-completo.mp4"
  echo "Comprimiendo a ~280 MB (${kbps} kbps)… tarda un rato"
  cd "$dir/videos"
  "$KIT/kit/vigilante.sh" "$dir/render.log" ffmpeg -v error -y -i "$alta" -c:v libx264 -preset medium -tune stillimage \
    -b:v ${kbps}k -pass 1 -passlogfile x264 -an -f null /dev/null && \
  "$KIT/kit/vigilante.sh" "$dir/render.log" ffmpeg -v error -y -i "$alta" -c:v libx264 -preset medium -tune stillimage \
    -b:v ${kbps}k -maxrate $((kbps*2))k -bufsize $((kbps*4))k -pass 2 -passlogfile x264 \
    -c:a aac -b:a 96k -ac 2 -movflags +faststart "$final" || fallo "No pude comprimir el video."
  rm -f x264*.log x264*.mbtree
fi
notificar "Video completo listo"
open -R "$final"
