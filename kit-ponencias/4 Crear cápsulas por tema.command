#!/bin/bash
# Una cápsula por diapositiva o tema (capítulo), con el mismo formato del video completo.
source "$(dirname "$0")/kit/comun.sh"

dir=$(elegir_analisis "Elige la carpeta del análisis")
min=$(preguntar "Duración mínima de cada cápsula, en segundos (los temas más cortos se saltan):" "20")
notificar "Creando cápsulas…"
"$KIT/kit/vigilante.sh" "$dir/render.log" "$PY" "$CAPS" capitulos "$dir" "$dir/capsulas" --min "${min:-20}" \
  || fallo "Las cápsulas se detuvieron. Si fue por memoria, cierra otras apps y vuelve a intentar."
notificar "Cápsulas listas"
open "$dir/capsulas"
avisar "Cápsulas listas en la carpeta «capsulas».\n\nOjo: revisa si alguna incluye voces de otras personas (papás, maestros) antes de publicarla. El archivo indice.md tiene lo que se dice en cada tema."
