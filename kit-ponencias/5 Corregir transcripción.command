#!/bin/bash
# Corrige palabras mal transcritas. Los subtítulos de los videos que crees después ya salen corregidos.
source "$(dirname "$0")/kit/comun.sh"

dir=$(elegir_analisis "Elige la carpeta del análisis")
c="$dir/correcciones.json"
if [ ! -f "$c" ]; then
  cat > "$c" <<'EOF'
{
  "palabra mal escrita": "palabra correcta",
  "frase que se oyó mal": "frase correcta"
}
EOF
fi
open "$dir/revisar.md"
open -e "$c"
avisar "Se abrieron dos archivos:\n\n• revisar.md: palabras dudosas, con el minuto donde aparecen.\n• correcciones.json: escribe ahí cada arreglo entre comillas, «\"mal\": \"bien\",», uno por renglón (el último sin coma). No importan mayúsculas ni signos.\n\nGuarda correcciones.json (⌘S) y luego presiona OK."
"$PY" -c "import json; json.load(open('$c'))" 2>/dev/null || fallo "correcciones.json tiene un error de formato (revisa comillas y comas)."
"$PY" "$CAPS" indices "$dir" || fallo "No pude aplicar las correcciones."
avisar "Correcciones aplicadas. Vuelve a crear el video o las cápsulas para que salgan con los subtítulos corregidos."
