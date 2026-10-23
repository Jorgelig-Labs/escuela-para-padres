# Entre nosotros

Un espacio en español para crecer en familia: videos breves, ideas para conversar y libros para profundizar. Los videos son el contenido principal; las lecturas los acompañan con acceso al PDF completo o a una muestra cuando está disponible.

El sitio funciona con HTML, CSS y JavaScript, sin framework en el navegador. El contenido se mantiene en JSON y en una ficha Markdown por libro. Se publica con Cloudflare Workers + Static Assets; los archivos multimedia se sirven desde un bucket privado de R2.

## Desarrollo local

Requiere Node.js 22.22.2+, 24.15.0+ o 26+, y npm.

```sh
npm ci
npm run dev
```

Abre `http://127.0.0.1:4173`. Al editar `public/` o `content/`, se regenera el sitio; recarga el navegador para ver los cambios. Puedes usar `PORT=4174 npm run dev` para cambiar el puerto.

```sh
npm run build          # Genera dist/ y los manifiestos de .generated/
npm test               # Pruebas en serie
npm run preview:file   # Vista local en artifacts/preview.html, sin servidor
```

Los MP4 y PDF no están incluidos en Git. Un clon limpio puede compilar el front y ejecutar las pruebas sin ellos. Para reproducir los originales localmente o subirlos, restaura los archivos en las rutas de `content/videos.json` y de `documents[].file` de cada libro. El preflight de subida exige todos los originales publicados; no descarga medios automáticamente.

En producción, el lector busca cada PDF en R2 y recurre a su fuente oficial si no encuentra el respaldo. La vista previa en archivo usa los originales locales y no comprueba R2 ni los encabezados HTTP.

## Contenido

```text
content/videos.json     Videos, grupos, duración, episodios y referencias
content/site.json       Textos de la portada y video destacado
content/questions.json  Preguntas para conversar en familia
content/libros/*.md      Metadatos y referencias de cada libro
```

`npm run build` valida estas fuentes y produce `dist/catalog.json`. No edites los archivos generados. Las rutas son relativas a esta carpeta, por lo que el sitio también puede vivir en `sitio/` dentro de un repositorio que incluya herramientas de producción.

### Videos

Solo se muestran, sirven y suben entradas con `status: "published"`. `draft` o la ausencia de estado las deja fuera de la publicación. Dar de alta un video no lo sube a R2: esa operación ocurre en el despliegue.

El front ofrece tres accesos: **Cápsulas**, **Ideas de los libros** (Para hoy, Resúmenes y Series) y **Series por episodios**. La clasificación sale de `group`; el campo `order` ordena dentro de cada colección. No se deduce el tipo por el nombre del archivo.

Los temas visibles se pueden combinar con la colección, el libro y la búsqueda. Cada serie ocupa una tarjeta con sus episodios publicados en orden, duración y guardado individual. Las búsquedas y Guardados muestran solo los episodios que coinciden e indican cuántos son. Los filtros se conservan en la URL (`group`, `topic`, `book`, `q`, `type`), por ejemplo `/?type=video&group=serie&book=el-hogar-cristiano#biblioteca`. No se necesitan entradas adicionales en el JSON para construir estas colecciones.

```json
{
  "id": "una-idea-para-hoy",
  "type": "video",
  "status": "published",
  "group": "refuerzo",
  "title": "Una idea para hoy",
  "author": "Autor de la referencia",
  "topic": "Familia",
  "description": "Una acción pequeña para practicar en casa.",
  "duration": 64.2,
  "file": "videos-libros/refuerzo/idea.mp4",
  "poster": "/assets/idea.jpg",
  "orientation": "vertical",
  "label": "Para hoy",
  "note": "Narración con voz generada.",
  "book": "el-hogar-cristiano",
  "order": 100
}
```

Las rutas de MP4 aceptan hasta tres subcarpetas, con letras, números, guiones y guiones bajos, sin rutas absolutas ni `..`. Los posters van en `public/assets/`. `duration` usa segundos y admite decimales.

- `book` relaciona un video con una referencia. El libro muestra sus videos y cada video enlaza al libro.
- `orientation` admite `horizontal` y `vertical`. Los verticales usan proporción 9:16 y permiten pantalla completa.
- Las series usan `group: "serie"`, `series` como identificador común, `episode` y `of`. El reproductor ordena los episodios, permite avanzar o retroceder y sugiere el siguiente al terminar, sin reproducción automática.
- `note` describe las características reales del contenido. No se añaden atribuciones ni subtítulos de manera automática.
- `site.featuredVideo` selecciona un ID publicado. Si no está disponible, se usa el primer publicado; si no hay ninguno, aparece un estado de preparación.

Los metadatos públicos deben tener sentido por sí solos: títulos descriptivos, autoría correcta y fuentes de lectura verificadas.

### Libros

Cada Markdown comienza con un bloque JSON estricto entre líneas `---`. El cuerpo Markdown es documentación para edición: no se copia al sitio ni se ofrece como descarga a sus visitantes.

Los metadatos incluyen `id`, `title`, `author`, `topic`, `description`, `publisher`, `year`, `pages`, `order`, `palette` y `links`. Los enlaces usan HTTPS y `kind: "read" | "download" | "purchase"`.

`access` distingue `complete` (libro completo), `sample` (muestra parcial) y `purchase` (referencia sin lectura gratuita). Los enlaces comerciales aparecen como referencias secundarias, nunca como la acción principal.

Para un PDF disponible, `documents` contiene `id`, `label`, `file` y `source`. La fuente debe pertenecer a uno de los proveedores oficiales admitidos por el generador. El botón **Leer libro** abre el lector con selector de tomo o edición; **Abrir PDF** permite usar el visor del dispositivo. Los originales de las lecturas disponibles se respaldan sin modificaciones.

## Cloudflare

Configura la cuenta en `.env` local o en las variables de tu terminal:

```sh
CLOUDFLARE_ACCOUNT_ID=tu_account_id
# Solo para autenticación por API token:
CLOUDFLARE_API_TOKEN=tu_token
```

Se admiten también `CLOUDFLARE_R2_ACCOUNT_ID` y `CLOUDFLARE_API`. El script consulta `../.env`, después `.env` local y por último el entorno de la terminal. Si mueves esta carpeta, comprueba la ruta de `../.env`; se recomienda una configuración local excluida de Git o variables de entorno.

### Sesión de Wrangler

```sh
npm run cf:login
npm run cf:check:oauth
npm run deploy:oauth -- --dry-run  # Calcula qué subiría sin modificar Cloudflare
npm run deploy:oauth              # Sube cambios y publica el sitio
```

OAuth evita que un API token anterior oculte la sesión de Wrangler. OAuth no está limitado a este proyecto: para limitar recursos concretos se necesita un token con el alcance apropiado. No publiques tokens ni archivos de sesión.

Para usar API token: `npm run cf:check` y `npm run deploy`. El chequeo confirma lectura de R2 y Workers; los permisos de escritura se comprueban al subir y desplegar. La cuenta debe tener R2 habilitado y permisos de edición sobre los recursos de destino. El dominio personalizado se declara en `wrangler.jsonc`; requiere una zona activa en la misma cuenta y los permisos correspondientes de zona/rutas.

### Subidas incrementales

El despliegue consulta la lista paginada de objetos de R2 y compara el tamaño y el hash MD5 local con el ETag remoto de las subidas simples de Wrangler. **Los archivos idénticos se omiten**, incluidos los PDF. Un reemplazo del mismo tamaño se detecta por su contenido. Los hashes se calculan por bloques, secuencialmente, sin cargar los videos completos en memoria.

El flujo no necesita un manifiesto local: si una subida se interrumpe, el siguiente intento consulta R2 y omite lo que ya se subió. Los objetos ajenos al catálogo no se borran. Un ETag multipart o desconocido se trata conservadoramente como un objeto por subir. Si falla el listado remoto, el proceso se detiene; no asume que el bucket está vacío.

Antes de subir, todos los originales deben existir y respetar el límite de Wrangler de 300 MiB por archivo. Si cambian durante el proceso, se detiene el despliegue.

```sh
npm run deploy:oauth -- --dry-run  # Solo plan remoto; no sube ni despliega
npm run deploy:oauth -- --force    # Fuerza resubir todos los originales publicados
npm run media:upload -- --oauth   # PDF y videos, sin publicar el Worker
npm run books:backup:oauth        # Solo PDF
```

Referencias: [listar objetos R2](https://developers.cloudflare.com/api/resources/r2/subresources/buckets/subresources/objects/methods/list/), [subidas y ETags](https://developers.cloudflare.com/r2/objects/upload-objects/), [autorización de Workers](https://developers.cloudflare.com/workers/authorization/), [dominios personalizados](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/).

### Empaquetar sin publicar

```sh
npm run build
npx wrangler deploy --dry-run
```

El Worker sirve exclusivamente los medios del catálogo publicado: `/media/<ruta>` para MP4 y `/pdf/<id>.pdf` para lecturas. Admite GET, HEAD, rangos HTTP y validación con ETag. El bucket no necesita acceso público.

## Repositorio público

Se incluyen código, metadatos, posters y pruebas. `.gitignore` excluye originales de video/PDF, pilotos, secretos, cachés, artefactos generados y documentos internos. Las fichas de `content/libros/` sí forman parte del sitio; `/libros/` contiene los PDF locales excluidos.

No se incluyen herramientas de generación de videos en esta carpeta. Pueden convivir en una carpeta hermana dentro del mismo repositorio. Las entradas se mantienen desde el flujo editorial y no desde la interfaz pública.

## Estructura

```text
public/                 Interfaz, lector, posters y encabezados
content/                Contenido editable
scripts/build.mjs       Validación y generación del sitio
scripts/dev.mjs         Servidor local con soporte de rangos
scripts/preview.mjs     Vista previa sin servidor
scripts/cloudflare.mjs  Autenticación, planificación, subida y despliegue
scripts/uploads.mjs     Comparación incremental con R2
worker.mjs              Entrega de medios publicados y PDF
tests/                 Pruebas de datos, navegación, lectura y subidas
```
