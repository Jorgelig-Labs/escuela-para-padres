# Kit Ponencias · documentación técnica

La guía para usuarios es `LEEME.md`. Este documento es para quien mantiene o extiende el kit.

## Estructura

```text
kit-ponencias/
├── instalar.command                 instala dependencias, crea .venv, compila ayudantes, crea .env
├── 1 Grabar reunión de Zoom.command OBS: start → diálogo (Reencuadrar / Detener) → stop
├── 2 Analizar grabación.command     recorte opcional (-c copy) + capsulas.py analizar
├── 3 Crear video completo.command   capsulas.py render con EDL [0, duración] + x264 2 pasadas (opcional)
├── 4 Crear cápsulas por tema.command capsulas.py capitulos
├── 5 Corregir transcripción.command  edita correcciones.json + capsulas.py indices
├── .env.example → .env              SECRETOS (OBS_PASSWORD, ELEVENLABS_API_KEY…). .env está en .gitignore
├── config.json                      AJUSTES no secretos (carpeta de trabajo, whisper, contexto, OBS)
├── requirements.txt                 obsws-python, websocket-client, pillow, numpy (versiones fijas)
├── kit/
│   ├── config.py      lee .env (sin dependencias) y config.json; secreto() sale con un mensaje claro
│   ├── capsulas.py    análisis, transcripción, correcciones y render (el motor)
│   ├── grabar_zoom.py control de OBS por obs-websocket v5
│   ├── vigilante.sh   corre un comando y lo detiene si la memoria se agota
│   ├── comun.sh       diálogos de osascript para los .command
│   └── swift/         ventanas.swift (monitores y ventanas de Zoom) · ocr.swift (Vision)
└── borradores/        pipelines de videos de libros en piloto (ver borradores/README.md)
```

Requisitos: macOS 13 o superior (ScreenCaptureKit y Vision), Apple Silicon o Intel, ~10 GB libres para
dependencias y modelos, y de 5 a 10 GB por hora de grabación con el lienzo de 1080p (4.6 GB/h a 720p).

## Secretos y ajustes

| Clave | Dónde | Uso |
|---|---|---|
| `OBS_PASSWORD` | `.env` | contraseña de obs-websocket (`grabar_zoom.py`) |
| `OBS_HOST`, `OBS_PORT` | `.env` (opcional) | `localhost` y `4455` por omisión |
| `ELEVENLABS_API_KEY` | `.env` | voz y música de los videos de libros (`borradores/`) |
| `VIGILANTE_SWAP_MB`, `VIGILANTE_LIBRE` | `.env` (opcional) | umbrales del vigilante: 300 MB de swap y 5 % libre |
| `carpeta_trabajo` | `config.json` | `~/Movies/Kit-Ponencias` |
| `whisper_modelo`, `whisper_hilos` | `config.json` | `small` y 5. `medium` no cabe con 16 GB y el navegador abierto |
| `contexto_transcripcion` | `config.json` | prompt de vocabulario para whisper; ponle el tema y los nombres propios |
| `obs.lienzo`, `obs.escena` | `config.json` | lienzo de 1920×1080. Con 1280×720 el ponente queda en 98×52 px |

Las variables de la terminal tienen prioridad sobre `.env`. Ningún secreto se escribe en el código ni en
los logs.

## Grabación (`kit/grabar_zoom.py`)

- **Fuente de video:** `screen_capture` de OBS (ScreenCaptureKit) con `type: 2` (aplicación),
  `application: us.zoom.xos` y `display_uuid` del monitor que contiene el centro de la ventana de Zoom más
  grande en la capa 0. **No se usa `type: 1` (ventana):** OBS 32 rechaza los IDs de ventana de Zoom con
  «Invalid target window ID».
- **Recorte:** la captura de aplicación entrega el monitor completo, así que el ítem de la escena se
  recorta a la ventana. El recorte se calcula en píxeles reales: `(ventana − monitor) × escala`, con la
  escala sacada de `CGDisplayCopyDisplayMode` (2 en Retina, 1 en monitores normales). Luego se ajusta al
  lienzo con `OBS_BOUNDS_SCALE_INNER`.
- **Audio:** `sck_audio_capture` con `type: 1`, la aplicación Zoom.
- **No llames a `GetInputPropertiesListPropertyItems`** sobre fuentes de ScreenCaptureKit: tumba a OBS. Por
  eso las ventanas se listan con `kit/swift/ventanas`, que usa `CGWindowList` (el dueño puede ser `zoom.us`,
  `Zoom` o `Zoom Workplace`).
- Subcomandos: `start`, `ajustar`, `stop`, `status` y `list`.

## Análisis (`capsulas.py analizar`)

1. **Layout a 1 fps** (`frames()` en streaming, sin cargar el video en memoria):
   - `slide_box`: encuentra la caja de la diapositiva por las columnas y filas del gris de separación de
     Zoom (≈ RGB 21,20,23) y fuerza 16:9.
   - **Ponente:** `buscar_ponente` prueba en varios momentos del video. El OCR de Vision (`kit/swift/ocr`,
     sobre la tira al doble de tamaño) ubica su etiqueta con coincidencia aproximada (difflib ≥ 0.7, porque
     el OCR lee «Parales» por «Perales»).
     - El ancho del recuadro es la distancia entre etiquetas vecinas menos 3 px, y el alto, ancho × 9/16.
     - La orilla se ajusta al salto de brillo más fuerte y se recortan 3 px por lado para dejar fuera el
       borde verde de «quien habla».
     - Ese recorte queda como plantilla. La clase `Ponente` lo sigue en cada cuadro por correlación
       normalizada a media resolución (umbral 0.45), y así lo encuentra aunque Zoom lo cambie de lugar.
     - Con `--ponente t,x,y,w,h` se da el recuadro a mano. Sin nombre ni recuadro, el video sale sin PiP.
   - **Cambios de diapositiva:** diferencia de miniaturas de 64×36 mayor que 14, con 4 s mínimo entre
     cambios.
   - `quitar_duplicadas` une diapositivas consecutivas iguales: histograma ≥ 0.95, o ≥ 0.89 si una de las
     dos trae barra negra lateral, que aparece cuando el ponente sale del modo presentación.
   - `tramos_layout` agrupa los segundos con la misma caja y el mismo ponente, con moda de vecinos y una
     tolerancia de 10 px.
2. **Transcripción:** whisper (`brew openai-whisper`) en CPU, en español, con `--beam_size 5`,
   `--condition_on_previous_text False` (evita bucles en audios largos), `--initial_prompt` armado con
   `contexto_transcripcion`, el título y el ponente, y `--word_timestamps`. Corre bajo `nice` y el
   vigilante. Se cachea en `transcripcion.<modelo>.json`.
3. **Índices** (`capsulas.py indices DIR`, que también se corre al final de `analizar`): `capitulos.json`,
   `indice.md` y `revisar.md`, este último con las palabras de probabilidad < 0.4 y su contexto.
   - `correcciones.json` ({"mal": "bien"}) se aplica sobre la lista corrida de palabras con tiempo, aunque
     una frase cruce dos segmentos de whisper. Compara sin mayúsculas ni puntuación y conserva la
     puntuación.

Rendimiento medido (Mac mini M4, 16 GB): layout ~3 min por 45 min de video; whisper `small` con 5 hilos
~1.1× tiempo real y 1.7 GB de RAM; `medium` se queda sin memoria si Chrome está abierto.

Archivos de `DIR`: `meta.json`, `layout.json`, `capitulos.json`, `indice.md`, `revisar.md`,
`transcripcion.*.json`, `audio.wav`, `diapositivas/`, `ponente_ref.png` y `ponente_detectado.png`.

## Render (`capsulas.py render DIR EDL.json SALIDA.mp4`)

**EDL:** una lista de segmentos.

```json
[
  {"video": [0, 2697.6], "titulo": "…", "subtitulo": "…"},
  {"still": 2680, "audio": [2697.6, 2773.1], "ponente": false, "subtitulo": "Cierre"}
]
```

- `video`: corte en vivo con el layout limpio.
- `still` + `audio`: **audio transpuesto**, es decir, la diapositiva fija del segundo `still` con el audio
  de otro tramo.
- Opciones por segmento: `titulo`, `subtitulo`, `subtitulos` (true/false) y `ponente` (true/false, para
  quitar el PiP cuando ya habla otra persona).

**Layout de salida** (1920×1080):
- diapositiva de 1536×864 arriba a la izquierda;
- columna derecha de 384 px con el título y el ponente abajo, al **tamaño aparente original** (el mismo
  factor que la diapositiva, con tope de 2×), sin la etiqueta de Zoom y con su nombre dibujado debajo;
- franja de 216 px abajo para los subtítulos.

Agrandar la miniatura del ponente solo la pixela; para un ponente grande hay que grabar con un lienzo de
1080p y la vista «lado a lado» de Zoom.

**Implementación:**
- Cada segmento se parte en piezas donde cambia el tramo de layout. Las piezas salen solo con video y el
  audio del segmento va de corrido, con fundido de 0.15 s y 0.25 s solo en los cortes del EDL.
- Todos los subtítulos de una pieza entran como una sola entrada (lista ffconcat de PNG con su duración)
  y no como un overlay por línea.
- Las imágenes fijas van con `-framerate 30`, porque la primera entrada marca el ritmo del overlay.
- Video con h264_videotoolbox a 6 Mbps y audio AAC a 160 kbps. Las piezas se unen con el demuxer concat
  (`-c copy`).
- `3 Crear video completo` comprime a ~280 MB con libx264 en dos pasadas (`-tune stillimage`). Eso
  respeta el límite de 300 MiB por objeto de `wrangler r2 object put`.

Este ffmpeg no trae los filtros `subtitles` ni `drawtext`: los textos se dibujan con Pillow (Arial de
macOS).

## Videos de libros (`kit/libros/`, módulo 6)

- `generar.py <spec.json>`: voz (ElevenLabs `/with-timestamps`, `eleven_v4`, con caché por segmento según
  texto, voz, modelo y ajustes) → armado de un proyecto HyperFrames (`plantilla.py`, `ilus.py`) → render por la
  cola (`KIT_COLA_RENDER`, si no `kit/vigilante.sh`) → loudnorm a -16 LUFS.
  - Opciones: `--validar` y `--contar` (no gastan), `--sin-voz`, `--solo-html`, `--salida`.
  - Si ElevenLabs responde 4xx, se detiene sin reintentar. El gasto queda en `gasto.csv`, junto al spec.
- `producir.sh <salida> <specs…>`: produce en serie, salta lo que ya existe y deja `produccion.log`.
- `simple.py` traduce el formato simple de beats (`tipo/seg/palabra/texto/visual`) al formato avanzado de la
  plantilla (ver `specs/R01.json`, el piloto aprobado). `tope_linea()` limita el tamaño de las líneas que no
  se parten (reacciones y listas) al ancho útil del formato.
- Specs de este proyecto: `specs/refuerzo/` (12, vertical), `specs/resumenes/` (12, horizontal) y
  `specs/series/` (36, vertical). Su fuente editable está en `specs/*/_fuente/`.
- Estilo aprobado: el piloto R01, regenerable con `generar.py specs/R01.json` (ver `specs/R01.json`).

## Comandos sin los .command

```sh
cd kit-ponencias
.venv/bin/python kit/grabar_zoom.py list
.venv/bin/python kit/capsulas.py ponente VIDEO --nombre "Nombre en Zoom" --out /tmp
.venv/bin/python kit/capsulas.py analizar VIDEO --out DIR --titulo "…" --nombre "…" [--modelo small]
.venv/bin/python kit/capsulas.py indices DIR
.venv/bin/python kit/capsulas.py render DIR edl.json salida.mp4
.venv/bin/python kit/capsulas.py capitulos DIR DIR/capsulas --min 20
kit/vigilante.sh registro.log <cualquier comando pesado>
```

Para copiar una grabación que todavía se está escribiendo, sin interrumpirla:
`ffmpeg -ss 667 -i grabando.mkv -c copy copia.mp4`. El mensaje «File ended prematurely» es normal.

## Verificación hecha (23 oct 2026)

- `.venv` nuevo desde `requirements.txt`; los ayudantes de Swift compilan y `grabar_zoom.py list` ve los 3
  monitores con su escala.
- Sin `OBS_PASSWORD` sale un mensaje claro. Con OBS cerrado, otro mensaje claro, sin traceback.
- `analizar` de un fragmento de 90 s con `tiny`: 69 s en total. El ponente se encuentra por nombre y se
  generan los índices y `revisar.md`.
- `render` de una cápsula de 62 s: 23 s.
- `grep` de rutas personales, contraseñas y referencias al evento en `kit/`, `*.command` y `config.json`:
  sin resultados.
- Recorte de `2 Analizar grabación`: con `-ss 667 -t 30` sobre la grabación real salen 30.07 s.
- `slug()` genera `por-que-ya-no-me-cuenta-nada`. El `iconv` de macOS fallaba con «¿», por eso el slug
  usa Python.
- `empaquetar.command` crea un ZIP de 5.5 MB sin `.env`, `.venv` ni respaldos.
- **Falta probar, y hay que hacerlo antes de entregar el kit:**
  - `grabar_zoom.py start`/`ajustar` con OBS abierto y una ventana de Zoom. Se reescribió con la misma
    configuración que funcionó en vivo el 22 oct (captura de app, `display_uuid` y recorte por ventana),
    pero el código nuevo, que saca la escala del monitor y fija el lienzo en 1080p, todavía no ha corrido.
    Prueba: abre OBS y Zoom, corre `ajustar` y revisa en OBS que se vea solo la ventana de Zoom.
  - La instalación desde cero en otra Mac: Homebrew, OBS por cask y los permisos de grabación de
    pantalla.
  - Los diálogos de los `.command`: solo se revisó su sintaxis con `bash -n`.
