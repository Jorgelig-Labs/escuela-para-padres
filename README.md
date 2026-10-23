# Escuela para padres · Entre nosotros

Biblioteca en línea para familias, con clips, libros y preguntas sobre la comunicación con hijos adolescentes,
más las herramientas con las que se produce su contenido en video.

| Carpeta | Qué es |
|---|---|
| [`sitio/`](sitio/) | Sitio web (Cloudflare Workers + R2): catálogo de videos y libros, lector de PDF. Ver `sitio/README.md`. |
| [`kit-ponencias/`](kit-ponencias/) | Kit para Mac que graba una ponencia de Zoom con OBS, la analiza (diapositivas, transcripción con whisper) y genera videos editados, cápsulas y videos de libros con voz en off. Ver `kit-ponencias/LEEME.md`. |

Los videos y los PDF no se versionan: viven en Cloudflare R2. Los secretos van en archivos `.env` locales
(hay un `.env.example` en cada carpeta).
