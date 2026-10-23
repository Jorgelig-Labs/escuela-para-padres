#!/usr/bin/env python3
"""Análisis y edición de grabaciones de Zoom: diapositivas, transcripción, cápsulas y resumen.

  capsulas.py analizar VIDEO --out DIR --nombre "Nombre del ponente" [--modelo small]
      (o --ponente t,x,y,w,h para dar el recuadro a mano; sin ninguno de los dos, va sin recuadro)
      layout de Zoom por segundo (diapositiva, ponente seguido por apariencia) · cambios de
      diapositiva · transcripción (whisper con prompt de vocabulario, cacheada) → capitulos.json,
      indice.md y revisar.md (palabras de baja confianza)

  capsulas.py indices DIR      tras editar DIR/correcciones.json ({"mal": "bien"}) regenera todo;
                               render también aplica las correcciones a los subtítulos

  capsulas.py render DIR EDL.json SALIDA.mp4
      EDL = lista de segmentos:
        {"video": [ini, fin]}                         corte en vivo con layout limpio
        {"still": seg_diapositiva, "audio": [ini, fin]} audio transpuesto sobre la diapositiva fija
      opciones por segmento: "titulo", "subtitulo", "subtitulos": true|false, "ponente": true|false
      Un segmento se parte solo donde cambia el layout de Zoom; el audio va de corrido.

  capsulas.py capitulos DIR CARPETA_SALIDA        una cápsula por capítulo
  capsulas.py ponente VIDEO --nombre "…"          solo prueba la detección del recuadro del ponente

Layout de salida (1920×1080, nada tapa la diapositiva):
  diapositiva 1536×864 arriba a la izquierda · columna derecha de 384 px con el título y, abajo, el
  ponente a su tamaño aparente original (sin la etiqueta de Zoom, con su nombre limpio) · franja
  inferior de 216 px para subtítulos.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import KIT, ajustes  # noqa: E402

CFG = ajustes()
OCR = os.path.join(KIT, "kit", "swift", "ocr")
VIGILANTE = os.path.join(KIT, "kit", "vigilante.sh")

W, H = 1920, 1080
SLIDE_W, SLIDE_H = 1536, 864
COL_W = W - SLIDE_W                      # 384
BAND_Y = SLIDE_H                         # franja de subtítulos
PIP_MAX = 2.0     # el ponente es una miniatura de Zoom: nunca se agranda más de esto
ETIQUETA = 0.21   # franja inferior del recuadro de Zoom con el nombre (se recorta y se dibuja limpia)
MARGEN, NOMBRE_H = 24, 34
BG, COL_BG, ACENTO = (18, 18, 24), (28, 26, 40), (91, 63, 176)
FONT_B = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_R = "/System/Library/Fonts/Supplemental/Arial.ttf"
FPS = 30
VENC = ["-c:v", "h264_videotoolbox", "-b:v", "6M", "-pix_fmt", "yuv420p", "-r", str(FPS)]
AENC = ["-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]
PROMPT = "{contexto} {titulo}. {subtitulo}. Ponente: {ponente}."


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"Falló: {' '.join(cmd[:6])}…\n{r.stderr[-1500:]}")
    return r.stdout


def probe(video):
    out = json.loads(sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                         "stream=width,height:format=duration", "-of", "json", video]))
    s = out["streams"][0]
    return s["width"], s["height"], float(out["format"]["duration"])


# ---------------------------------------------------------------- análisis de layout

def frames(video, fps, w, h):
    """Cuadros RGB a `fps` por segundo, en streaming (no carga el video en memoria)."""
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={fps}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    size = w * h * 3
    i = 0
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield i / fps, np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        i += 1
    p.wait()


def slide_box(f):
    """Caja de la diapositiva compartida, por la geometría de Zoom: está rodeada por el gris de
    separación de la ventana (≈ RGB 21,20,23). Se buscan las columnas/filas que son casi todas ese
    gris — el hueco hacia el chat o el borde de la ventana — y se fija 16:9."""
    g = f.mean(axis=2)
    h, w = g.shape
    gap = (g > 10) & (g < 30)
    band = gap[int(h * 0.25):int(h * 0.85)]
    col_gap = band.mean(axis=0) > 0.97
    # borde izquierdo: primera columna que no es separador
    x0 = int(np.argmax(~col_gap[: w // 4])) if (~col_gap[: w // 4]).any() else 0
    # borde derecho: primer separador a partir de la mitad (hueco hacia el chat o borde de ventana)
    right = np.where(col_gap[w // 2:])[0]
    x1 = int(right[0] + w // 2) if len(right) else w
    # borde superior: última fila separador entre la tira de participantes y la diapositiva
    row_gap = gap[:, x0:x1].mean(axis=1) > 0.97
    tops = np.where(row_gap[int(h * 0.08):int(h * 0.35)])[0]
    if not len(tops):
        return None
    y0 = int(tops[-1] + h * 0.08) + 1
    bw = x1 - x0
    bh = int(round(bw * 9 / 16))
    if bw < w * 0.4 or y0 + bh > h + 4:
        return None
    return [x0, y0, bw // 2 * 2, min(bh, h - y0) // 2 * 2]


def _norm(a):
    a = a - a.mean(axis=(-2, -1), keepdims=True)
    return a / (np.sqrt((a ** 2).sum(axis=(-2, -1), keepdims=True)) + 1e-6)


class Ponente:
    """Sigue el recuadro del ponente en la tira de participantes por su apariencia (no por el borde
    verde de Zoom, que marca a quien hable y casi no se distingue en 720p). Se le da una referencia
    una vez (`--ponente t,x,y,w,h`) y la busca en cada cuadro con correlación normalizada."""

    def __init__(self, ref_rgb):
        self.h, self.w = ref_rgb.shape[:2]
        self.ref = _norm(self._gray(ref_rgb))
        self.box = None

    @staticmethod
    def _gray(rgb):
        g = np.asarray(Image.fromarray(rgb).convert("L"), float)
        return g[::2, ::2]  # media resolución basta y es 4× más rápido

    def find(self, f, top):
        strip = self._gray(f[:top])
        th, tw = self.ref.shape
        if strip.shape[0] < th or strip.shape[1] < tw:
            return self.box
        win = np.lib.stride_tricks.sliding_window_view(strip, (th, tw))[::1, ::2]
        score = (_norm(win) * self.ref).sum(axis=(-2, -1))
        iy, ix = np.unravel_index(score.argmax(), score.shape)
        if score[iy, ix] > 0.45:
            self.box = [int(ix * 2 * 2), int(iy * 2), self.w // 2 * 2, self.h // 2 * 2]
        return self.box


def _sin_acentos(s):
    import unicodedata
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def recuadro_por_nombre(f, nombre, top):
    """Encuentra el recuadro del ponente en la tira de participantes de Zoom por su nombre: el OCR de
    macOS (Vision) ubica la etiqueta; el ancho sale de la distancia entre etiquetas vecinas (todos los
    recuadros miden igual) y la orilla se ajusta al salto de brillo más fuerte. Se deja fuera el borde
    verde de «quien habla»."""
    h, w = f.shape[:2]
    tmp = tempfile.mktemp(suffix=".png")
    Image.fromarray(f[:top]).resize((w * 2, top * 2)).save(tmp)
    salida = subprocess.run([OCR, tmp], capture_output=True, text=True).stdout
    os.remove(tmp)
    filas = []
    for l in salida.splitlines():
        p = l.split("|")
        if len(p) == 5:
            filas.append((p[0], int(p[1]) / 2, int(p[2]) / 2, int(p[3]) / 2, int(p[4]) / 2))
    # El OCR se equivoca en alguna letra (lee «Parales» por «Perales»): se acepta el parecido más alto ≥ 0.7
    from difflib import SequenceMatcher
    buscado = _sin_acentos(nombre).strip()
    def parecido(texto):
        t = _sin_acentos(texto).strip(" •*/|.-")
        return max(SequenceMatcher(None, buscado, t).ratio(),
                   max((SequenceMatcher(None, buscado, t[i:i + len(buscado)]).ratio()
                        for i in range(max(1, len(t) - len(buscado) + 1))), default=0))
    mio = sorted(((parecido(r[0]), r) for r in filas
                  if not any(k in r[0].lower() for k in ("screen", "pantalla"))), key=lambda x: -x[0])
    if not mio or mio[0][0] < 0.7:
        return None
    _, lx, ly, lw, lh = mio[0][1]
    abajo = ly + lh
    xs = sorted(r[1] for r in filas if abs(r[2] + r[4] - abajo) < 5)
    pasos = [b - a for a, b in zip(xs, xs[1:]) if b - a > 40]
    paso = float(np.median(pasos)) if pasos else 110 * w / 1280
    tw = round(paso - 3)
    th = round(tw * 9 / 16)
    g = f.mean(axis=2)
    x0, y1 = int(lx) - 2, int(abajo) + 2
    y0 = y1 - th
    cols = [g[max(y0, 0):y1, x].mean() for x in range(max(x0 - 8, 1), min(x0 + 11, w))]
    x0 = max(x0 - 8, 1) + int(np.argmax(np.diff(cols))) + 1
    rws = [g[y, x0:x0 + tw].mean() for y in range(max(y0 - 8, 1), min(y0 + 11, top))]
    y0 = max(y0 - 8, 1) + int(np.argmax(np.diff(rws))) + 1
    x0, y0, tw, th = x0 + 3, y0 + 3, tw - 6, th - 6
    if x0 < 0 or y0 < 0 or x0 + tw > w or y0 + th > top + 4:
        return None
    return [x0, y0, tw // 2 * 2, th // 2 * 2]


def buscar_ponente(video, nombre, out=None):
    """Prueba en varios momentos del video hasta encontrar el recuadro; devuelve (t, x, y, w, h)."""
    w, h, dur = probe(video)
    for frac in (0.1, 0.2, 0.3, 0.5, 0.7, 0.05, 0.85):
        t = round(dur * frac, 1)
        f = cuadro(video, t, w, h)
        sb = slide_box(f)
        if not sb:
            continue
        box = recuadro_por_nombre(f, nombre, sb[1])
        if box:
            if out:
                x, y, bw, bh = box
                Image.fromarray(f[y:y + bh, x:x + bw]).resize((bw * 4, bh * 4)).save(f"{out}/ponente_detectado.png")
            return [t] + box
    return None


def thumb(f, box, size=(64, 36)):
    x, y, w, h = box
    return np.asarray(Image.fromarray(f[y:y + h, x:x + w]).convert("L").resize(size), float)


def cuadro(video, t, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", video, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)


def analizar_layout(video, out, ponente, fps=1.0):
    w, h, dur = probe(video)
    tracker = None
    if ponente:
        t, x, y, pw, ph = ponente
        ref = cuadro(video, t, w, h)[y:y + ph, x:x + pw]
        Image.fromarray(ref).save(f"{out}/ponente_ref.png")
        tracker = Ponente(ref)
    samples = []
    prev, last_box = None, None
    changes = [0.0]
    os.makedirs(f"{out}/diapositivas", exist_ok=True)
    for t, f in frames(video, fps, w, h):
        sb = slide_box(f)
        if sb and last_box and abs(sb[0] - last_box[0]) < 12 and abs(sb[2] - last_box[2]) < 12:
            sb = last_box  # estabilizar
        sb = sb or last_box
        if sb is None:
            continue
        spk = tracker.find(f, sb[1]) if tracker else None
        samples.append({"t": t, "slide": sb, "speaker": spk})
        th = thumb(f, sb)
        layout_changed = last_box is not None and sb != last_box
        if prev is not None and not layout_changed and np.abs(th - prev).mean() > 14 and t - changes[-1] >= 4:
            changes.append(t)
        if t == changes[-1]:
            x, y, bw, bh = sb
            Image.fromarray(f[y:y + bh, x:x + bw]).save(f"{out}/diapositivas/d{len(changes):03d}.jpg", quality=88)
        prev, last_box = th, sb
    return samples, changes, dur


def _cerca(a, b, tol=10):
    if a is None or b is None:
        return a is b
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def _hist(img):
    a = np.asarray(img.convert("RGB").resize((160, 90))).reshape(-1, 3) // 32
    a = a[a.sum(1) > 1]  # sin negro puro (barras)
    h = np.bincount(a[:, 0] * 64 + a[:, 1] * 8 + a[:, 2], minlength=512).astype(float)
    return h / h.sum()


def _barra_negra(img):
    g = np.asarray(img.convert("L"))
    return (g[:, : g.shape[1] // 20] < 30).mean() > 0.9


def quitar_duplicadas(out, changes):
    """Une diapositivas consecutivas que son la misma. Pasa cuando el ponente sale un momento del modo
    presentación: Zoom encoge la pantalla compartida (barra negra a un lado) y parece otra diapositiva.
    Criterio: mismos colores (histograma ≥0.89) y una de las dos con barra negra, o ≥0.95 sin más."""
    d = f"{out}/diapositivas"
    imgs = [Image.open(f"{d}/d{i + 1:03d}.jpg") for i in range(len(changes))]
    orig = list(imgs)
    keep = [0]
    for i in range(1, len(imgs)):
        j = keep[-1]
        # contra la inmediata anterior (aunque se haya unido): barra → normal → barra es una cadena
        p = orig[i - 1]
        sim = np.minimum(_hist(orig[i]), _hist(p)).sum()
        if sim >= 0.95 or (sim >= 0.89 and (_barra_negra(orig[i]) or _barra_negra(p))):
            # conservar la versión sin barra
            if _barra_negra(imgs[j]) and not _barra_negra(imgs[i]):
                imgs[j] = imgs[i]
            continue
        keep.append(i)
    for f in os.listdir(d):
        os.remove(f"{d}/{f}")
    for n, i in enumerate(keep):
        imgs[i].save(f"{d}/d{n + 1:03d}.jpg", quality=88)
    return [changes[i] for i in keep]


def tramos_layout(samples, k=5):
    """Corta donde cambia de verdad la caja de la diapositiva o la posición del ponente. Cada muestra
    toma la moda de sus ±k vecinas (ignora parpadeos) y movimientos de ≤10 px no abren tramo."""
    keys = [(tuple(s["slide"]), tuple(s["speaker"]) if s["speaker"] else None) for s in samples]
    tramos = []
    for i, s in enumerate(samples):
        sl, spk = Counter(keys[max(0, i - k):i + k + 1]).most_common(1)[0][0]
        if tramos and _cerca(tramos[-1]["slide"], list(sl)) and _cerca(tramos[-1]["speaker"], list(spk) if spk else None):
            continue
        tramos.append({"t": s["t"], "slide": list(sl), "speaker": list(spk) if spk else None})
    for i, tr in enumerate(tramos):
        if tr["speaker"] is None:
            near = [x["speaker"] for x in tramos[i::-1] + tramos[i:] if x["speaker"]]
            tr["speaker"] = near[0] if near else None
    return tramos


# ---------------------------------------------------------------- transcripción

def transcribir(video, out, modelo, prompt):
    """Whisper con un prompt de vocabulario (nombres propios y términos de la charla: es lo que más
    corrige) y sin condicionar en el texto previo, que en audios largos provoca bucles."""
    js = f"{out}/transcripcion.{modelo}.json"
    if os.path.exists(js):
        return json.load(open(js))
    wav = f"{out}/audio.wav"
    if not os.path.exists(wav):
        sh(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav])
    cmd = ["nice", "-n", "15", VIGILANTE, f"{out}/whisper.log", 
        "whisper", wav, "--model", modelo, "--language", "es", "--device", "cpu", "--fp16", "False",
        "--threads", str(CFG["whisper_hilos"]), "--beam_size", "5", "--condition_on_previous_text", "False",
        "--initial_prompt", prompt, "--word_timestamps", "True", "--output_format", "json",
        "--output_dir", out, "--verbose", "False"]
    subprocess.run(cmd, check=True)
    os.replace(f"{out}/audio.json", js)
    return json.load(open(js))


PUNT = ".,;:¿?¡!«»\"'…"


def _clave(w):
    return w.strip().strip(PUNT).lower()


def _bordes(w):
    s = w.strip()
    core = s.strip(PUNT)
    i = s.find(core) if core else len(s)
    return s[:i], s[i + len(core):]


def corregir(tr, reglas):
    """Aplica `correcciones.json` ({"mal": "bien"}) sobre las palabras con tiempo. Compara sin
    mayúsculas ni puntuación y la conserva; una frase de varias palabras (aunque cruce de un segmento de
    whisper a otro) se funde en una sola entrada que va del inicio de la primera al fin de la última.
    Así un arreglo llega a los subtítulos sin volver a transcribir."""
    reglas = sorted(([_clave(x) for x in k.split()], v) for k, v in reglas.items())
    reglas.sort(key=lambda r: -len(r[0]))
    ws = [(n, w) for n, s in enumerate(tr["segments"]) for w in s.get("words", [])]
    claves = [_clave(w["word"]) for _, w in ws]
    out, i = [], 0
    while i < len(ws):
        for pat, rep in reglas:
            n = len(pat)
            if claves[i:i + n] == pat:
                seg, first = ws[i]
                last = ws[i + n - 1][1]
                sp = first["word"][:len(first["word"]) - len(first["word"].lstrip())]
                out.append((seg, {**first, "word": sp + _bordes(first["word"])[0] + rep + _bordes(last["word"])[1],
                                  "end": last["end"], "probability": 1.0}))
                i += n
                break
        else:
            out.append(ws[i])
            i += 1
    for n, s in enumerate(tr["segments"]):
        s["words"] = [w for k, w in out if k == n]
        s["text"] = "".join(w["word"] for w in s["words"])
    return tr


def cargar_transcripcion(dir_, path):
    tr = json.load(open(path))
    cf = f"{dir_}/correcciones.json"
    return corregir(tr, json.load(open(cf))) if os.path.exists(cf) else tr


def palabras(tr):
    return [w for s in tr["segments"] for w in s.get("words", [])]


def texto_entre(tr, a, b):
    return " ".join(w["word"].strip() for w in palabras(tr) if a <= w["start"] < b)


def lineas_subtitulo(tr, a, b, max_chars=58, max_dur=4.0):
    """Agrupa palabras en líneas cortas con su tiempo (relativo a `a`)."""
    out, cur = [], []
    for w in palabras(tr):
        if w["end"] <= a or w["start"] >= b:
            continue
        cur.append(w)
        txt = " ".join(x["word"].strip() for x in cur)
        if len(txt) > max_chars or cur[-1]["end"] - cur[0]["start"] > max_dur or txt.endswith((".", "?", "!")):
            out.append((max(cur[0]["start"], a) - a, min(cur[-1]["end"], b) - a, txt))
            cur = []
    if cur:
        out.append((max(cur[0]["start"], a) - a, min(cur[-1]["end"], b) - a, " ".join(x["word"].strip() for x in cur)))
    return out


# ---------------------------------------------------------------- render

def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if draw.textlength(test, font=fnt) <= width:
            cur = test
        else:
            lines.append(cur)
            cur = word
    return lines + [cur] if cur else lines


def pip_geom(lay):
    """Recuadro del ponente sin la etiqueta de Zoom, escalado igual que la diapositiva (o sea, al tamaño
    aparente que tenía en la grabación; más grande solo se pixelea), abajo y al centro de la columna.
    Devuelve (recorte en la fuente, (ancho, alto, x, y) en la salida)."""
    px, py, pw, ph = lay["speaker"]
    ph -= round(ph * ETIQUETA)
    f = min(SLIDE_W / lay["slide"][2], PIP_MAX)
    ow, oh = round(pw * f) // 2 * 2, round(ph * f) // 2 * 2
    return (px, py, pw, ph), (ow, oh, SLIDE_W + (COL_W - ow) // 2, SLIDE_H - MARGEN - NOMBRE_H - oh)


def fondo(path, titulo, subtitulo, pip=None, nombre=""):
    """Lienzo base: fondo, título en la columna derecha, marco y nombre del ponente."""
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([SLIDE_W, 0, W, SLIDE_H], fill=COL_BG)
    if pip:
        ow, oh, x, y = pip
        d.rectangle([x - 3, y - 3, x + ow + 2, y + oh + 2], fill=ACENTO)
        if nombre:
            fn = font(FONT_B, 22)
            d.text((x + ow / 2 - d.textlength(nombre, font=fn) / 2, y + oh + 8), nombre, font=fn,
                   fill=(235, 232, 245))
    y = 40
    for line in wrap(d, titulo, font(FONT_B, 34), COL_W - 48):
        d.text((SLIDE_W + 24, y), line, font=font(FONT_B, 34), fill=(255, 255, 255))
        y += 44
    y += 16
    for line in wrap(d, subtitulo, font(FONT_R, 24), COL_W - 48):
        d.text((SLIDE_W + 24, y), line, font=font(FONT_R, 24), fill=(190, 186, 210))
        y += 32
    d.rectangle([0, BAND_Y, W, H], fill=(10, 10, 14))
    im.save(path)


def png_subtitulo(path, text):
    im = Image.new("RGBA", (W, H - BAND_Y), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fnt = font(FONT_B, 46)
    lines = wrap(d, text, fnt, W - 160)[:2]
    total = len(lines) * 58
    y = (im.height - total) // 2
    for line in lines:
        tw = d.textlength(line, font=fnt)
        d.text(((W - tw) / 2, y), line, font=fnt, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
        y += 58
    im.save(path)


def layout_en(tramos, t):
    cur = tramos[0]
    for tr in tramos:
        if tr["t"] <= t:
            cur = tr
    return cur


def subtitulos_concat(tr, a, b, tmp, tag):
    """Todos los subtítulos de [a, b] como UNA entrada (lista ffconcat de PNG con duración), en vez de
    un overlay por línea: en un video de 45 min serían cientos de entradas."""
    lineas = lineas_subtitulo(tr, a, b)
    if not lineas:
        return None
    blank = f"{tmp}/blank.png"
    if not os.path.exists(blank):
        Image.new("RGBA", (W, H - BAND_Y), (0, 0, 0, 0)).save(blank)
    rows, t = ["ffconcat version 1.0"], 0.0
    for k, (t0, t1, txt) in enumerate(lineas):
        t0 = max(t0, t)
        if t1 - t0 < 0.05:
            continue
        if t0 > t:
            rows += [f"file '{blank}'", f"duration {t0 - t:.3f}"]
        p = f"{tmp}/sub{tag}_{k}.png"
        png_subtitulo(p, txt)
        rows += [f"file '{p}'", f"duration {t1 - t0:.3f}"]
        t = t1
    rows += [f"file '{blank}'", f"duration {max(b - a - t, 0.05):.3f}", f"file '{blank}'"]
    lst = f"{tmp}/subs{tag}.txt"
    open(lst, "w").write("\n".join(rows) + "\n")
    return lst


def render_pieza(video, meta, seg, a, b, tmp, tag):
    """Video (sin audio) de [a, b] con un solo layout de Zoom."""
    lay = layout_en(meta["tramos"], a)
    pip = pip_geom(lay) if lay["speaker"] and seg.get("ponente", True) else None
    bg = f"{tmp}/bg{tag}.png"
    fondo(bg, seg.get("titulo", meta["titulo"]), seg.get("subtitulo", meta["subtitulo"]),
          pip and pip[1], meta.get("ponente_nombre", ""))
    # -framerate en las imágenes fijas: la primera entrada marca el ritmo del overlay
    inputs = ["-framerate", str(FPS), "-loop", "1", "-i", bg]
    if "still" in seg:
        # Audio transpuesto: la diapositiva fija del momento indicado, con el ponente en vivo de [a, b]
        still = f"{tmp}/still{tag}.png"
        ts = seg["still"]
        cx, cy, cw, ch = layout_en(meta["tramos"], ts)["slide"]
        sh(["ffmpeg", "-v", "error", "-y", "-ss", str(ts), "-i", video, "-frames:v", "1",
            "-vf", f"crop={cw}:{ch}:{cx}:{cy}", still])
        inputs += ["-framerate", str(FPS), "-loop", "1", "-i", still, "-ss", str(a), "-t", str(b - a), "-i", video]
        fc = f"[1:v]scale={SLIDE_W}:{SLIDE_H}:flags=lanczos[s];[0:v][s]overlay=0:0[v0]"
        live = 2
    else:
        sx, sy, sw, sh_ = lay["slide"]
        inputs += ["-ss", str(a), "-t", str(b - a), "-i", video]
        fc = f"[1:v]crop={sw}:{sh_}:{sx}:{sy},scale={SLIDE_W}:{SLIDE_H}:flags=lanczos[s];[0:v][s]overlay=0:0[v0]"
        live = 1
    last = "v0"
    if pip:
        (px, py, pw, ph), (ow, oh, x, y) = pip
        fc += f";[{live}:v]crop={pw}:{ph}:{px}:{py},scale={ow}:{oh}:flags=lanczos[p];[v0][p]overlay={x}:{y}[v1]"
        last = "v1"
    if seg.get("subtitulos", True):
        lst = subtitulos_concat(meta["transcripcion"], a, b, tmp, tag)
        if lst:
            n = inputs.count("-i")
            inputs += ["-f", "concat", "-safe", "0", "-i", lst]
            fc += f";[{n}:v]format=rgba[sb];[{last}][sb]overlay=0:{BAND_Y}:eof_action=pass[v2]"
            last = "v2"
    out = f"{tmp}/pz{tag}.mp4"
    sh(["nice", "-n", "10", "ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc,
        "-map", f"[{last}]", "-an", "-t", f"{b - a:.3f}", *VENC, out])
    return out


def render_segmento(video, meta, seg, tmp, idx):
    """Un segmento del EDL. Se parte en piezas donde cambia el layout de Zoom (el ponente se mueve de
    lugar en la tira), pero el audio va de corrido, con fundido solo en los cortes del EDL."""
    a, b = seg.get("video") or seg["audio"]
    cortes = [a] + [t["t"] for t in meta["tramos"] if a < t["t"] < b] + [b]
    piezas = [render_pieza(video, meta, seg, x, y, tmp, f"{idx}_{k}")
              for k, (x, y) in enumerate(zip(cortes, cortes[1:]))]
    lst = f"{tmp}/piezas{idx}.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in piezas))
    d = b - a
    out = f"{tmp}/seg{idx:03d}.mp4"
    sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
        "-ss", str(a), "-t", f"{d:.3f}", "-i", video, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
        "-af", f"afade=t=in:d=0.15,afade=t=out:st={max(d - 0.25, 0):.2f}:d=0.25", *AENC,
        "-t", f"{d:.3f}", out])
    return out


def render(dir_, edl, salida):
    meta = json.load(open(f"{dir_}/meta.json"))
    meta["transcripcion"] = cargar_transcripcion(dir_, meta["transcripcion_path"])
    video = meta["video"]
    with tempfile.TemporaryDirectory() as tmp:
        parts = [render_segmento(video, meta, seg, tmp, i) for i, seg in enumerate(edl)]
        lst = f"{tmp}/lista.txt"
        open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
        sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
            "-movflags", "+faststart", salida])
    print(f"✓ {salida}")


# ---------------------------------------------------------------- comandos

def cmd_analizar(a):
    os.makedirs(a.out, exist_ok=True)
    print("1/3 layout y diapositivas…", flush=True)
    if a.ponente:
        ponente = [float(v) if i == 0 else int(v) for i, v in enumerate(a.ponente.split(","))]
    elif a.nombre:
        ponente = buscar_ponente(a.video, a.nombre, a.out)
        print(f"    ponente «{a.nombre}»: " + (f"recuadro {ponente[1:]} (ver ponente_detectado.png)" if ponente
              else "no lo encontré en la tira de Zoom; el video irá sin su recuadro"), flush=True)
    else:
        ponente = None
    samples, changes, dur = analizar_layout(a.video, a.out, ponente)
    json.dump(samples, open(f"{a.out}/layout.json", "w"))
    changes = quitar_duplicadas(a.out, changes)
    tramos = tramos_layout(samples)
    print(f"    {len(changes)} diapositivas · {len(tramos)} tramos de layout", flush=True)
    print(f"2/3 transcripción ({a.modelo})…", flush=True)
    transcribir(a.video, a.out, a.modelo, a.prompt or PROMPT.format(
        contexto=CFG["contexto_transcripcion"], titulo=a.titulo, subtitulo=a.subtitulo,
        ponente=a.nombre or "el ponente"))
    meta = {"video": os.path.abspath(a.video), "duracion": dur, "tramos": tramos, "cambios": changes,
            "transcripcion_path": os.path.abspath(f"{a.out}/transcripcion.{a.modelo}.json"),
            "titulo": a.titulo, "subtitulo": a.subtitulo, "ponente_nombre": a.nombre}
    json.dump(meta, open(f"{a.out}/meta.json", "w"), ensure_ascii=False, indent=1)
    print("3/3 capítulos…", flush=True)
    indices(a.out)


def indices(dir_):
    """capitulos.json, indice.md y revisar.md con la transcripción ya corregida."""
    meta = json.load(open(f"{dir_}/meta.json"))
    tr = cargar_transcripcion(dir_, meta["transcripcion_path"])
    bounds = meta["cambios"] + [meta["duracion"]]
    caps = [{"n": i + 1, "ini": round(t0, 1), "fin": round(t1, 1),
             "diapositiva": f"diapositivas/d{i + 1:03d}.jpg", "texto": texto_entre(tr, t0, t1)}
            for i, (t0, t1) in enumerate(zip(bounds, bounds[1:]))]
    json.dump(caps, open(f"{dir_}/capitulos.json", "w"), ensure_ascii=False, indent=1)
    with open(f"{dir_}/indice.md", "w") as f:
        f.write(f"# {meta['titulo']}\n\n")
        for c in caps:
            f.write(f"## {c['n']}. {mmss(c['ini'])}–{mmss(c['fin'])}\n\n![]({c['diapositiva']})\n\n{c['texto']}\n\n")
    # Palabras con baja confianza de whisper, con contexto: la lista para validar a mano
    ws = palabras(tr)
    dudosas = [k for k, w in enumerate(ws) if w.get("probability", 1) < 0.4]
    with open(f"{dir_}/revisar.md", "w") as f:
        f.write(f"# Revisar transcripción — {len(dudosas)} palabras dudosas de {len(ws)}\n\n"
                "Corrige en `correcciones.json` ({\"mal\": \"bien\"}) y vuelve a correr `capsulas.py indices DIR`.\n\n")
        for k in dudosas:
            ctx = " ".join(("**" + w["word"].strip() + "**") if j == k else w["word"].strip()
                           for j, w in enumerate(ws[max(k - 6, 0):k + 7], max(k - 6, 0)))
            f.write(f"- `{mmss(ws[k]['start'])}` ({ws[k]['probability']:.2f}) {ctx}\n")
    print(f"✓ {dir_}/indice.md · {dir_}/revisar.md ({len(dudosas)} dudosas)")


def mmss(t):
    m, s = divmod(int(t), 60)
    return f"{m}:{s:02d}"


def cmd_capitulos(a):
    caps = json.load(open(f"{a.dir}/capitulos.json"))
    os.makedirs(a.salida, exist_ok=True)
    for c in caps:
        if c["fin"] - c["ini"] < a.min:
            continue
        render(a.dir, [{"video": [c["ini"], c["fin"]], "subtitulo": f"Parte {c['n']}"}],
               f"{a.salida}/capsula_{c['n']:02d}.mp4")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    an = sp.add_parser("analizar")
    an.add_argument("video")
    an.add_argument("--out", required=True)
    an.add_argument("--modelo", default=CFG["whisper_modelo"])
    an.add_argument("--titulo", default="Ponencia")
    an.add_argument("--subtitulo", default="")
    an.add_argument("--ponente", default="",
                    help="t,x,y,w,h — un cuadro (segundos) y el recuadro del ponente en él")
    an.add_argument("--nombre", default="", help="nombre del ponente, se dibuja bajo su recuadro")
    an.add_argument("--prompt", default="", help="vocabulario para whisper (por omisión, título y temas)")
    pn = sp.add_parser("ponente", help="prueba la detección del recuadro del ponente por su nombre")
    pn.add_argument("video")
    pn.add_argument("--nombre", required=True)
    pn.add_argument("--out", default=".")
    ix = sp.add_parser("indices", help="regenera capítulos, índice y revisar.md tras corregir")
    ix.add_argument("dir")
    rn = sp.add_parser("render")
    rn.add_argument("dir")
    rn.add_argument("edl")
    rn.add_argument("salida")
    cp = sp.add_parser("capitulos")
    cp.add_argument("dir")
    cp.add_argument("salida")
    cp.add_argument("--min", type=float, default=20)
    a = p.parse_args()
    if a.cmd == "analizar":
        cmd_analizar(a)
    elif a.cmd == "ponente":
        r = buscar_ponente(a.video, a.nombre, a.out)
        print(",".join(str(v) for v in r) if r else "No encontré al ponente")
        sys.exit(0 if r else 1)
    elif a.cmd == "indices":
        indices(a.dir)
    elif a.cmd == "render":
        render(a.dir, json.load(open(a.edl)), a.salida)
    else:
        cmd_capitulos(a)


if __name__ == "__main__":
    main()
