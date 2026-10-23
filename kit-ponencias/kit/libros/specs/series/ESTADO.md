# ESTADO guiones de series (36 capsulas), 2026-10-23

## Hecho
- 36 JSON en esta carpeta: NN-<libro_id>-Kde3.json (id: serie-<libro_id>-Kde3), formato EXACTO del encargo
  (segmentos como tripletas [nombre, voz, "[tono] texto"], beats {tipo, seg, palabra, texto, visual}).
- Fuente editable: ./_fuente/ (lib01.py ... lib12.py + base.py). Regenerar y validar: `python3 _fuente/base.py --write`
  (valida 140-190 palabras de voz, citas <=25 palabras presentes en fuentes verificadas, anclas, cierres, palabras prohibidas).
- Citas de libros 5-12 re-verificadas en vivo contra Google Books / muestra oficial de Tripp: _fuente/fuentes/verificadas.txt.
- Campos extra: titulo_corto, etiqueta ("<Titulo corto> · N/3"), tema, pronunciacion (opcional; el generador ya trae
  PRONUNCIACION_DEF para egwwritings.org y P&R, asi que "pronunciacion" de estos JSON se puede ignorar o borrar).

## PENDIENTE (no hecho: se acabo el presupuesto de contexto)
- CONVERTIDOR al formato del generador: kit/libros/generar.py (plantilla.validar) NO acepta los beats de estos JSON:
  exige en cada beat «ancla» ("seg:palabra", el primero puede ser 0), «lineas»/«grupos» con texto "A *RESALTADA*|B",
  y visuales de las listas ilus.ICONOS / ilus.ILUSTRACIONES; ademas pide «libros»:[{titulo,autor,donde,derechos}],
  «marca», y «cierre»: false en 1/3 y 2/3 (el cierre con tarjeta del libro se genera solo desde «libros»).
  Prueba hecha: `python3 -I generar.py <spec> --validar` sobre 05-...-3de3 => "falta «ancla»" en los 9 beats.
  Mapeo sugerido por beat: ancla=f"{seg}:{palabra.lower()}" (primer beat ancla 0); titular/reaccion -> lineas en mayusculas con
  la palabra ancla entre *; cita -> libro:0 + comilla:true + lineas (sin «»); accion -> tipo "accion_hoy" con lineas
  ["*PARA_HOY*", texto sin "Para hoy:"]; icono/ilustracion -> palabra clave de «visual» mapeada a ilus.ICONOS/ILUSTRACIONES;
  tarjeta_libro (ep 3) -> «cierre»: {"ancla": "tarjeta"} en vez de beat; ep 1 y 2 -> «cierre»: false.
  Salida sugerida: ./gen/<mismo nombre>.json y validar los 36 con --validar (no gasta ElevenLabs).
- Revisar que las palabras ancla sean palabras completas del segmento (el generador compara por palabra, no por subcadena).
