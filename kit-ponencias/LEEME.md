# Kit Ponencias

Graba una conferencia de Zoom (aunque no seas el anfitrión) y conviértela en:

- **un video completo editado**: la presentación en grande, el ponente en un recuadro chico como el
  intérprete de las noticias, y subtítulos;
- **cápsulas cortas por tema**, con el mismo formato;
- **el índice y la transcripción** de lo que se dijo en cada diapositiva.

Todo se maneja con doble clic. No hace falta saber programar.

> **Antes de empezar, ten a la mano dos cosas que el kit no puede adivinar:**
> 1. La **contraseña de OBS**, que creas tú en el paso 2.
> 2. Una **llave de ElevenLabs**, solo si vas a hacer videos con voz en off. Para grabar y analizar no
>    hace falta.
>
> Las dos se guardan en el archivo `.env`, en tu Mac. **Nunca compartas ese archivo.**

---

## Paso 1 · Instalar (una sola vez, 10 a 30 min)

1. Copia la carpeta `kit-ponencias` a tu Mac, por ejemplo a *Documentos*.
2. Haz **clic derecho** sobre `instalar.command`, elige **Abrir** y vuelve a presionar **Abrir**.
   Mac lo pide así solo la primera vez, porque el archivo no viene de la App Store.
3. Se abre una ventana negra (la Terminal) que va diciendo qué instala.
   - Si te pide la **contraseña de tu Mac**, escríbela y presiona Enter. Mientras tecleas no se ven los
     caracteres; es normal.
   - Si aparece una ventana de Apple para instalar las **herramientas de línea de comandos**, presiona
     *Instalar* y espera a que termine.
4. Al final se abre el archivo `.env`. Déjalo abierto: lo vas a llenar en el paso 2.

Lo que se instala: Homebrew, ffmpeg (video), whisper (transcripción), Python, Node y OBS (grabación).

## Paso 2 · Configurar OBS (una sola vez)

1. Abre **OBS**. Si pregunta por el asistente de configuración automática, elige *Cancelar*.
2. Menú **Herramientas → Configuración del servidor WebSocket**:
   - Marca **Habilitar servidor WebSocket**.
   - Marca **Habilitar autenticación** y presiona **Generar contraseña**.
   - Presiona **Mostrar información de conexión** y copia la contraseña.
   - Pégala en `.env` después de `OBS_PASSWORD=` y guarda con ⌘S.
3. Dale permiso a OBS para grabar la pantalla: **Configuración del Sistema → Privacidad y seguridad →
   Grabación de pantalla y audio del sistema**, activa **OBS** y reabre OBS si lo pide.

## Paso 3 · Grabar la reunión

1. Entra a la reunión de Zoom.
   - **Agranda la ventana de Zoom**, o maximízala, en el monitor que quieras.
   - Cuando el ponente comparta su presentación, deja la vista donde se ve **la presentación grande y la
     tira de participantes arriba**. Así el kit encuentra al ponente.
2. Doble clic en **`1 Grabar reunión de Zoom.command`**.
   - Se abre OBS y empieza a grabar **solo la ventana de Zoom, con su audio**. Tu micrófono, las
     notificaciones y las demás apps no se graban.
   - Si mueves o agrandas la ventana de Zoom, presiona **Reencuadrar**.
3. Al terminar la reunión, presiona **Detener grabación**. Se abre la carpeta con el archivo.

Ocupa de 5 a 10 GB por hora. Revisa que tengas espacio libre.

## Paso 4 · Analizar la grabación (cerca de 1 hora por hora de video)

Doble clic en **`2 Analizar grabación.command`** y contesta lo que te pregunta:

| Pregunta | Ejemplo | Para qué sirve |
|---|---|---|
| Archivo | la grabación del paso 3 | |
| Título | ¿Por qué ya no me cuenta nada? | Va en el video y en la carpeta |
| Subtítulo | Cómo volver a entrar al mundo de tu adolescente | Opcional |
| Tema y nombres propios | Crianza de adolescentes; Elena G. de White, Gary Chapman | Opcional. Ayuda a que la transcripción escriba bien los nombres |
| Nombre del ponente | **tal como sale en su recuadro de Zoom** | Para encontrar su recuadro |
| Minuto de inicio | 11:07 | Quita la sala de espera y lo que se grabó antes de empezar |
| Minuto final | (vacío) | Quita lo que sobra al final |

Al terminar se abre la carpeta del análisis, dentro de *Películas → Kit-Ponencias*:

- `indice.md`: cada diapositiva con lo que se dijo mientras estaba en pantalla.
- `revisar.md`: palabras que la transcripción no entendió bien, con el minuto donde aparecen.
- `ponente_detectado.png`: el recuadro que encontró del ponente. Si no es él, revisa que el nombre esté
  escrito igual que en Zoom.
- `diapositivas/`: una imagen por diapositiva.

## Paso 5 · Corregir la transcripción (opcional, recomendado)

Doble clic en **`5 Corregir transcripción.command`** y elige la carpeta del análisis.

1. Se abren `revisar.md` y `correcciones.json`.
2. En `correcciones.json` escribe cada arreglo así, uno por renglón, con coma al final de cada renglón menos
   del último:

   ```json
   {
     "extirimenta": "experimenta",
     "maestra karen": "maestra Carmen"
   }
   ```

3. Guarda con ⌘S y presiona OK.

Los videos que crees después ya salen con los subtítulos corregidos.

## Paso 6 · Crear los videos

- **`3 Crear video completo.command`**: elige la carpeta del análisis y la versión.
  - **Ligera**: unos 280 MB, cabe en WhatsApp y en la web.
  - **Alta calidad**: unos 2.5 GB por hora.

  Tarda unos 10 min por hora de video, más la compresión.
- **`4 Crear cápsulas por tema.command`**: una cápsula por diapositiva o tema, que se guardan en la carpeta
  `capsulas`.

> **Privacidad:** si en la reunión hablaron papás, maestros u otras personas, sus voces y sus nombres
> quedan en el audio. Antes de publicar un video, revísalo: en `indice.md` está lo que se dice en cada
> tema. No publiques las intervenciones de otras personas sin su permiso.

## Si algo falla

| Mensaje | Qué hacer |
|---|---|
| «Falta OBS_PASSWORD en .env» | Haz el paso 2 y guarda `.env`. |
| «No pude conectarme con OBS» | Abre OBS y revisa que el WebSocket esté habilitado y que la contraseña sea la misma. |
| «No veo ninguna ventana de Zoom» | Entra a la reunión antes de grabar. |
| El video sale negro | Falta el permiso de grabación de pantalla para OBS (paso 2.3). |
| «vigilante: … detengo» | La Mac se quedó sin memoria. Cierra apps, sobre todo pestañas de Chrome, y vuelve a intentar. |
| «no lo encontré en la tira de Zoom» | El nombre no coincide con el de Zoom, o durante la grabación no se veía la tira de participantes. El video sale sin el recuadro del ponente. |
| Mac dice que no puede abrir el archivo | Clic derecho → **Abrir** (solo la primera vez). |

## Pasar el kit a otra Mac

1. Haz doble clic en **`empaquetar.command`**. En tu Escritorio se crea `kit-ponencias-AAAAMMDD.zip`, de
   unos 6 MB. **No incluye tus contraseñas** (`.env`).
2. En la otra Mac, descomprime el ZIP y sigue esta guía desde el paso 1. Las contraseñas de esa Mac se
   ponen en su propio `.env`.

## Paso 7 · Videos de libros con voz en off (opcional)

Para hacer videos animados con voz, música y subtítulos a partir de **guiones**: resúmenes de libros (16:9) o
cápsulas verticales para redes (9:16).

1. Necesitas la llave de ElevenLabs en `.env` (`ELEVENLABS_API_KEY=`).
2. Los guiones van en `kit/libros/specs/<grupo>/`, un archivo `.json` por video. El formato está en
   `kit/libros/README.md`. Puedes pedirle a Claude que los escriba a partir de un PDF o de tus notas.
3. Doble clic en **`6 Videos de libros.command`** y elige la carpeta de guiones. Antes de gastar te dice
   cuántos caracteres de voz va a costar.
4. Los videos quedan en *Películas → Kit-Ponencias → videos-libros*. Si se acaban los créditos, se detiene;
   cuando lo vuelvas a correr, continúa donde se quedó sin volver a cobrar lo ya hecho.

Voces: Marisol (narradora), Rewe (voz joven) y Mario (voz adulta), con el modelo `eleven_v4`. Se cambian en
`kit/libros/voz.json`.

## Para saber más

La documentación técnica está en `DOCUMENTACION.md`. Los pipelines anteriores, que ya no se usan, están en
`borradores/` como referencia.
