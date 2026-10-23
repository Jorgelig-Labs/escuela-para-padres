# Videos de libros (módulo 6)

```
export KIT_COLA_RENDER=/ruta/a/cola_render.sh      # opcional; si no, usa kit/vigilante.sh
python3 generar.py specs/pruebas/resumen-prueba-16x9.json            # voz -> armado -> render -> -16 LUFS
python3 generar.py <spec.json> --validar     # revisa anclas y maquetación sin gastar voz ni renderizar
python3 generar.py <spec.json> --contar      # caracteres de voz que faltan por generar
python3 generar.py <spec.json> --sin-voz     # solo caché de voz;  --solo-html: arma sin renderizar
```
La llave `ELEVENLABS_API_KEY` se lee de `kit-ponencias/.env`. Trabajo en `<carpeta del spec>/_trabajo/<id>/`;
`gasto.csv` queda junto al spec; salida por omisión `_trabajo/<id>/<id>.mp4` (o `--salida`).

## Especificación (JSON)
Raíz: `id`, `formato` (`vertical` 1080x1920 | `horizontal` 1920x1080), `segmentos` (`[nombre, voz, "[tono] texto"]`, voces
`marisol|rewe|mario`; `pausa` opcional como 4.º valor), libro(s) (`titulo`, `autor`, `donde`, `derechos` en la raíz o lista `libros`),
`presupuesto_caracteres` (opcional), `pronunciacion` (`{"egwwritings.org": "e ge doble u writings punto org"}`: se dice una cosa y se
escribe otra), `marca` (texto de la franja inferior), `cierre` (opcional).

Beats SIMPLES (los que escriben los guionistas): `{"tipo","seg","palabra","texto","visual"}`. Tipos: `titular`, `reaccion`, `cita`,
`icono`, `ilustracion`, `tarjeta_libro`, `ideas`, `accion`, `dia`. El beat entra en la palabra (`palabra`, una o varias) del segmento
`seg`; el primero siempre empieza en 0. `texto`: `\n` o ` · ` separan líneas; `*palabra*` marca con pincelada; `1 · TEXTO` pone número.
`visual` se traduce por palabras clave a ícono/ilustración (candado, oído, reloj, puerta, mesa, cuarto, camino…); se puede forzar con
`icono` / `ilustracion` (ver `ilus.py`). La última `tarjeta_libro` del último segmento (o la de «no sustituye…») arranca la tarjeta final;
«Este video no sustituye la lectura del libro.» sale si algún libro tiene `derechos: true`.

Beats AVANZADOS (ver `specs/R01.json`, el piloto aprobado): `{"tipo","ancla":"s2:palabra","desfase", "lineas"/"grupos"/"filas"/"items", ...}`.
