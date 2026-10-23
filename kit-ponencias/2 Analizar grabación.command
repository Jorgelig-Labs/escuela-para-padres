#!/bin/bash
# Analiza una grabación: diapositivas, recuadro del ponente y transcripción. Tarda ~1 h por hora de video.
source "$(dirname "$0")/kit/comun.sh"

video=$(elegir_video "Elige la grabación de la ponencia (MKV o MP4)")
titulo=$(preguntar "Título de la ponencia:" "")
[ -z "$titulo" ] && fallo "El título es obligatorio."
subtitulo=$(preguntar "Subtítulo (opcional):" "")
nombre=$(preguntar "Nombre del ponente TAL COMO SALE EN ZOOM (para encontrar su recuadro). Déjalo vacío si no hay video del ponente:" "")
tema=$(preguntar "Tema y nombres propios que se mencionan (opcional; ayuda a que la transcripción los escriba bien):" "")
ini=$(preguntar "¿En qué minuto empieza de verdad la ponencia? (mm:ss, por ejemplo 11:07). Vacío = desde el inicio:" "")
fin=$(preguntar "¿En qué minuto termina? (mm:ss). Vacío = hasta el final:" "")

dir="$(carpeta_trabajo)/$(slug "$titulo")"
mkdir -p "$dir"
fuente="$video"
if [ -n "$ini$fin" ]; then
  echo "Recortando la grabación (sin perder calidad)…"
  # Con -ss antes de -i el tiempo vuelve a empezar en 0, así que el final se da como duración (-t)
  args=()
  i0=$(a_segundos "${ini:-0}"); f0=$(a_segundos "$fin")
  args+=(-ss "$i0")
  [ -n "$fin" ] && args+=(-t "$(awk -v a="$i0" -v b="$f0" 'BEGIN { print b - a }')")
  ffmpeg -v error -y "${args[@]}" -i "$video" -c copy -movflags +faststart "$dir/grabacion-recortada.mp4" \
    || fallo "No pude recortar la grabación."
  fuente="$dir/grabacion-recortada.mp4"
fi

notificar "Analizando «$titulo». Puede tardar cerca de una hora; te aviso al terminar."
echo "Analizando… (puedes minimizar esta ventana, pero no la cierres)"
prompt=""
[ -n "$tema" ] && prompt="$tema. $titulo. $subtitulo. Ponente: ${nombre:-el ponente}."
"$PY" "$CAPS" analizar "$fuente" --out "$dir" --titulo "$titulo" --subtitulo "$subtitulo" --nombre "$nombre" --prompt "$prompt" \
  || fallo "El análisis se detuvo. Revisa el texto de esta ventana. Si dice «vigilante», la Mac se quedó sin memoria: cierra otras apps (sobre todo Chrome) y vuelve a intentar."

notificar "Análisis listo: «$titulo»"
open "$dir"
[ -f "$dir/ponente_detectado.png" ] && open "$dir/ponente_detectado.png"
avisar "Análisis listo.\n\n• indice.md: las diapositivas y lo que se dijo en cada una.\n• revisar.md: palabras que la transcripción no entendió bien (para corregir con «5 Corregir transcripción»).\n• ponente_detectado.png: el recuadro que encontré del ponente.\n\nSiguiente: «3 Crear video completo» o «4 Crear cápsulas por tema»."
