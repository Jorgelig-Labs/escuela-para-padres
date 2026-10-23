# -*- coding: utf-8 -*-
"""Carga una especificación y la deja en el formato que entiende la plantilla.

Acepta dos formatos de beat:
  · SIMPLE (el que escriben los guionistas): {"tipo", "seg", "palabra", "texto", "visual", "libro_id"?}
    `visual` es una descripción en español; aquí se traduce a ilustración/ícono por palabras clave y se puede
    forzar con los campos opcionales «icono», «ilustracion», «chip», «libro».
  · AVANZADO (ver README.md): {"tipo", "ancla", "desfase", "lineas"/"grupos"/"filas"/"items", "icono", ...}
Un archivo puede mezclar beats de los dos formatos.
"""
import json
import re

import plantilla
from plantilla import norm, sin_etiqueta

ILUS_ROTACION = ["mesa_tazas", "sillon_atardecer", "escritorio_libro", "camino_amanecer", "cuarto_adolescente"]
ICONOS_KW = [  # (regex sobre texto sin acentos, ícono)
    (r"candado|cortina", "candado"), (r"escudo|proteg", "escudo"), (r"oreja|oido|escuch", "oido"),
    (r"libreta|lapiz|anota", "libreta"), (r"libro|portada|capitulo", "libro"), (r"reloj|arena|contador|minut", "reloj"),
    (r"burbuja|chat|mensaje|dialogo|conversa", "chat"), (r"corazon|amor|carino", "corazon"), (r"foco|bombilla|ilumina", "bombilla"),
    (r"lupa", "lupa"), (r"paraguas", "paraguas"), (r"vela|llama|encendid", "llama"), (r"casa|hogar|ventana", "casa"),
    (r"brujula|rumbo", "brujula"), (r"\bsol\b", "sol"), (r"nube", "nube"), (r"volante|timon", "timon"), (r"corona", "corona"),
    (r"interrogacion|pregunta", "pregunta"), (r"puerta", "puerta_icono"), (r"celular|telefono|pantalla|movil", "celular"),
    (r"balanza", "balanza"), (r"regalo", "regalo"), (r"mochila", "mochila"), (r"\bglobo\b", "globo"),
    (r"\bmanos?\b|gesto", "mano"), (r"pausa", "pausa"), (r"flecha", "flecha"), (r"estrella", "estrella"),
    (r"palomita|check|lista", "check"),
]
ILUS_KW = [
    (r"cuarto|recamara|dormitorio|pasillo|habitacion", "cuarto_adolescente"), (r"mesa|taza|cocina|cafe", "mesa_tazas"),
    (r"sillon|sofa|atardecer|juntos", "sillon_atardecer"), (r"escritorio|lampara|lectura|libro abierto|estudio", "escritorio_libro"),
    (r"camino|sendero|amanecer", "camino_amanecer"),
]


def plano(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", re.sub(r"[̀-ͯ]", "", __import__("unicodedata").normalize("NFD", s.lower()))))


def primero(patrones, texto):
    """El patrón que aparece más temprano en el texto (lo primero que describe el guionista)."""
    t = plano(texto)
    mejor = None
    for rx, v in patrones:
        m = re.search(rx, t)
        if m and (mejor is None or m.start() < mejor[0]):
            mejor = (m.start(), v)
    return mejor[1] if mejor else None


# ───────────────────────── carga ─────────────────────────
def cargar(path):
    spec = json.load(open(path, encoding="utf-8"))
    return preparar(spec)


def preparar(spec):
    segs = []
    for s in spec.get("segmentos", []):
        if isinstance(s, (list, tuple)):
            s = {"nombre": s[0], "voz": s[1], "texto": s[2], **({"pausa": s[3]} if len(s) > 3 else {})}
        s = dict(s)
        s.setdefault("pausa", 0.35)
        segs.append(s)
    spec["segmentos"] = segs
    spec.setdefault("formato", "vertical")
    spec.setdefault("beats", [])
    if not spec.get("libros") and spec.get("titulo") and spec.get("autor"):      # libro en la raíz (resúmenes y series)
        spec["libros"] = [{k: spec[k] for k in ("libro_id", "titulo", "autor", "donde", "derechos") if k in spec}]
    spec.setdefault("libros", [])
    for l in spec["libros"]:
        l.setdefault("derechos", True)
    if "marca" not in spec:
        if spec.get("etiqueta"):
            spec["marca"] = spec["etiqueta"]
        elif spec.get("libro_id") and not spec.get("libros_tema"):
            spec["marca"] = "Resumen · " + (spec.get("titulo_corto") or spec.get("titulo", ""))
        else:
            spec["marca"] = "Entre nosotros"
    if any("seg" in b for b in spec["beats"]):
        spec["beats"], cierre = traducir(spec)
        if cierre is not None and not isinstance(spec.get("cierre"), dict):
            spec["cierre"] = cierre
    if spec.get("episodio") and spec.get("de") and int(spec["episodio"]) < int(spec["de"]):
        spec["cierre"] = False        # episodios 1 y 2 de una serie: sin tarjeta final
    return spec


# ───────────────────────── traducción simple -> avanzado ─────────────────────────
def partes(texto):
    out = []
    for linea in texto.split("\n"):
        out += [p.strip() for p in linea.split(" · ")]
    return [p for p in out if p]


def tam_largo(n, grande=122):
    return grande if n <= 24 else int(grande * 0.82) if n <= 44 else int(grande * 0.66) if n <= 80 else int(grande * 0.52)


def tope_linea(texto, formato, panel=False):
    """Tamaño máximo para que una línea que NO se parte quepa a lo ancho. Medido en renders reales de Nunito 900:
    ~0.72 em por carácter en mayúsculas y ~0.40 en minúsculas."""
    util = (840 if panel else 940) if formato == "vertical" else (1300 if panel else 1500)
    t = re.sub(r"[*_]", "", texto)
    em = 0.72 if t.upper() == t else 0.40
    return max(40, int(util / (max(len(t), 1) * em)))


def marcar(t):
    """Pincelada amarilla: si el texto no trae *marca*, va en la última palabra de 4+ letras."""
    if "*" in t:
        return t
    ws = t.split()
    for i in range(len(ws) - 1, -1, -1):
        if len(re.sub(r"\W", "", ws[i])) >= 4:
            ws[i] = "*" + ws[i].rstrip(".,;:!?¿¡»«") + "*" + ws[i][len(ws[i].rstrip(".,;:!?¿¡»«")):]
            break
    return " ".join(ws)


def chip_de(visual):
    m = re.search(r"chip\s+«(.+?)»", visual)
    return {"texto": m.group(1), "ancla": "beat", "desfase": 0.3} if m else None


class Trad:
    def __init__(self, spec):
        self.spec = spec
        self.segs = {s["nombre"]: s for s in spec["segmentos"]}
        self.ultimo_seg = spec["segmentos"][-1]["nombre"]
        mapa = dict(plantilla.PRONUNCIACION_DEF)
        mapa.update(spec.get("pronunciacion", {}))
        self.palabras = {}
        for n, s in self.segs.items():
            w = plantilla.aplicar_pronunciacion(plantilla.words_sin_audio(s["texto"], 0), mapa)
            self.palabras[n] = [x["t"] for x in w]
        self.rot = 0
        self.primer_accion = True

    # --- utilidades
    def ancla(self, b):
        p = (b.get("palabra") or "").strip()
        return f"{b['seg']}:{p}" if p else b["seg"]

    def ilustracion_de(self, b, rotar=False):
        if b.get("ilustracion"):
            return b["ilustracion"]
        v = b.get("visual", "")
        if b["tipo"] == "ilustracion" and re.search(r"puerta", plano(v)) and re.search(r"cierra|cerrar|entreabierta|abre|reduce", plano(v)):
            return "puerta"
        i = primero(ILUS_KW, v)
        if i:
            return i
        if rotar:
            self.rot += 1
            return ILUS_ROTACION[self.rot % len(ILUS_ROTACION)]
        return None

    def icono_de(self, b, usar_texto=True):
        if b.get("icono"):
            return b["icono"]
        return primero(ICONOS_KW, b.get("visual", "")) or (primero(ICONOS_KW, b.get("texto", "")) if usar_texto else None)

    def libro_ref(self, texto):
        p = partes(texto)
        t0 = norm(p[0]) if p else ""
        for l in self.spec["libros"]:
            if norm(l["titulo"]) == t0:
                return l
        return {"titulo": p[0], "autor": p[1] if len(p) > 1 else "", "donde": p[2] if len(p) > 2 else "", "derechos": True}

    def anclas_items(self, seg, items, palabra_inicio):
        """Ancla cada ítem de una lista a la palabra hablada que mejor lo representa (en orden)."""
        ws = self.palabras[seg]
        ns = [norm(w) for w in ws]
        ini = 0
        if palabra_inicio:
            toks = [norm(x) for x in palabra_inicio.split()]
            for i in range(len(ns) - len(toks) + 1):
                if ns[i:i + len(toks)] == toks:
                    ini = i
                    break
        out, pos = [], ini
        n = len(items)
        for k, it in enumerate(items):
            if k == 0:
                idx = ini
            else:
                toks = [norm(t) for t in re.findall(r"\w+", it) if len(norm(t)) >= 5]
                idx = None
                for j in range(pos + 1, len(ns)):
                    if any(ns[j] == t or ns[j].startswith(t[:5]) or t.startswith(ns[j][:5]) and len(ns[j]) >= 5 for t in toks):
                        idx = j
                        break
                if idx is None:                           # sin coincidencia: repartir lo que queda
                    idx = min(len(ns) - 1, pos + max(2, (len(ns) - pos) // (n - k + 1)))
            pos = idx
            k_occ = sum(1 for j in range(0, idx + 1) if ns[j] == ns[idx])
            out.append(f"{seg}:{ws[idx]}@{k_occ}")
        return out

    # --- traducción por tipo
    def paneles(self, beats):
        """Pre-pase: agrupa runs de `reaccion` con panel/whip en un solo beat «lista»."""
        out, i = [], 0
        while i < len(beats):
            b = beats[i]
            v = plano(b.get("visual", ""))
            if b["tipo"] == "reaccion" and re.search(r"panel|tarjeta", v) and "whip" in v and re.search(r"azul marino|navy", v):
                run = [b]
                j = i + 1
                while j < len(beats) and beats[j]["tipo"] == "reaccion" and re.search(r"misma|whip|puntos de progreso", plano(beats[j].get("visual", ""))) \
                        and not re.search(r"naranja", plano(beats[j].get("visual", ""))):
                    run.append(beats[j])
                    j += 1
                out.append({"_run": run})
                i = j
            else:
                out.append(b)
                i += 1
        return out

    def traducir(self, beats):
        beats = [dict(b) for b in beats]
        cierre = None
        res, pend_libro = [], None
        marcados = self.paneles(beats)
        k = 0
        while k < len(marcados):
            b = marcados[k]
            k += 1
            if "_run" in b:
                res.append(self.lista(b["_run"]))
                continue
            if "ancla" in b and "seg" not in b:                  # beat avanzado: pasa tal cual
                res.append(b)
                continue
            tipo = b["tipo"]
            if tipo == "tarjeta_libro":
                txt = b["texto"]
                if "no sustituye" in txt.lower() or b["seg"] == self.ultimo_seg:
                    if cierre is None:
                        cierre = {"ancla": self.ancla(b), "desfase": -0.1, "segundos": 4.0}
                    continue
                nb = dict(tipo="tarjeta_libro", ancla=self.ancla(b), libro=self.libro_ref(txt))
                sig = marcados[k] if k < len(marcados) else None
                if sig and "_run" not in sig and sig.get("seg") == b["seg"] and sig["tipo"] in ("cita", "icono") and not (sig["tipo"] == "icono" and " · " in sig["texto"] and not re.match(r"\s*\d+\s*·", sig["texto"])):
                    k += 1
                    inner = self.cita(sig, en_tarjeta=True) if sig["tipo"] == "cita" else self.icono(sig, en_tarjeta=True)
                    nb.update({x: inner[x] for x in ("lineas", "comilla", "chip") if x in inner})
                    nb["tipo"] = "cita" if sig["tipo"] == "cita" else "tarjeta_libro"
                res.append(nb)
                continue
            f = getattr(self, tipo, None)
            if f is None:
                raise SystemExit(f"beat «{tipo}» ({b.get('seg')}:{b.get('palabra')}): tipo desconocido en el formato simple.")
            nb = f(b)
            if nb:
                if nb.get("panel") and res and (res[-1].get("panel") or res[-1].get("continua")) and not nb.get("continua"):
                    nb["continua"] = True
                res.append(nb)
        for i in range(len(res) - 1):                      # panel que se recoge como puerta hacia una puerta que se cierra
            if (res[i].get("panel") or res[i].get("continua")) and res[i + 1].get("cerrar_en"):
                res[i]["salida"] = "puerta"
        return res, cierre

    def titular(self, b):
        p = partes(b["texto"])
        m = re.match(r"^(\d+)$", p[0]) if len(p) > 1 else None
        base = dict(tipo="titular", ancla=self.ancla(b))
        if m:
            base["numero"] = m.group(1)
            p = p[1:]
        main = marcar(p[0])
        lineas = [dict(t=main, tam=tam_largo(len(p[0])), marca_color="morado")]
        for extra in p[1:]:
            lineas.append(dict(t=extra, tam=54, color="morado", efecto="desenfoque", ancla="beat", desfase=0.5))
        base["lineas"] = lineas
        if not m:
            il = self.ilustracion_de(b)
            ic = None if il else self.icono_de(b, usar_texto=False)
            if il:
                base["ilustracion"] = il
            elif ic:
                base["icono"], base["tam_visual"] = ic, 300
        if b.get("chip"):
            base["chip"] = b["chip"]
        return base

    def icono(self, b, en_tarjeta=False):
        p = partes(b["texto"])
        base = dict(tipo="icono", ancla=self.ancla(b))
        if len(p) >= 2 and not re.match(r"^\d+$", p[0]) and "\n" not in b["texto"] and not en_tarjeta:
            return self.ideas(b)
        chip = chip_de(b.get("visual", ""))
        if len(p) >= 2 and re.match(r"^\d+$", p[0]):
            chip = {"texto": p[0], "ancla": "beat", "desfase": 0.45}
            p = p[1:]
        txt = " ".join(p)
        up = txt.upper() == txt
        lin = dict(t=marcar(txt), tam=tam_largo(len(txt), 120), marca_color="morado",
                   ancla=self.ancla(b), desfase=-0.05, efecto="letras" if (up and len(txt) <= 14 and " " not in txt) else "subir")
        base["lineas"] = [lin]
        if chip:
            base["chip"] = chip
        if en_tarjeta:
            return base
        ic = self.icono_de(b) or "estrella"
        base["icono"] = ic
        base["circulo"] = ic == "candado"
        if re.search(r"costado|lateral|entra desde", plano(b.get("visual", ""))):
            base["entrada_visual"] = "derecha"
        return base

    def reaccion(self, b):
        v = plano(b.get("visual", ""))
        p = partes(b["texto"])
        pc = None
        if re.search(r"panel|tarjeta|inunda", v):
            pc = "naranja" if "naranja" in v else "morado" if "morad" in v and "tarjeta" in v else "navy"
        seg_voz = self.segs[b["seg"]]["voz"]
        base = dict(tipo="reaccion", ancla=self.ancla(b))
        n = len(p[0])
        tam = 150 if n <= 14 else 120 if n <= 26 else 96
        tam = min(tam, tope_linea(p[0], self.spec["formato"], panel=bool(pc)))   # la reacción va en una sola línea
        color = "blanco" if pc == "navy" else ("navy" if pc == "naranja" else "navy")
        lin = dict(t=p[0], tam=tam, color=color, efecto="golpe", ancla=self.ancla(b), desfase=-0.05)
        if re.search(r"sacud|tiembl|impacto", v):
            lin["sacudir"] = 0.4
        base["lineas"] = [lin]
        for extra in p[1:]:
            base["lineas"].append(dict(t=extra, tam=max(48, int(tam * 0.42)), color="amarillo" if pc == "navy" else "blanco",
                                       efecto="desenfoque", ancla=self.ancla(b), desfase=0.3))
        if pc:
            base["panel"] = pc
            if pc == "naranja":
                base["salida"] = None
        else:
            ic = primero(ICONOS_KW, b.get("visual", ""))
            if b.get("icono") or (ic and n <= 40 and not re.search(r"palabra|impacto", v)):
                base["icono"], base["tam_visual"] = b.get("icono") or ic, 280
        if b.get("chip"):
            base["chip"] = b["chip"]
        return {k_: v_ for k_, v_ in base.items() if v_ is not None}

    def lista(self, run):
        items, dots = [], any("puntos de progreso" in plano(r.get("visual", "")) for r in run)
        for r in run:
            tam = 150 if len(r["texto"]) <= 12 else 118 if len(r["texto"]) <= 24 else 96
            items.append(dict(t=r["texto"], tam=min(tam, tope_linea(r["texto"], self.spec["formato"], panel=True)), ancla=self.ancla(r)))
        base = dict(tipo="lista", ancla=self.ancla(run[0]), desfase=-0.3, panel="navy", puntos=dots and len(items) > 1, items=items)
        ch = chip_de(run[0].get("visual", ""))
        if ch:
            base["chip"] = ch
        return base

    def cita(self, b, en_tarjeta=False):
        t = b["texto"].strip()
        ref = None
        if " — " in t:
            t, ref = [x.strip() for x in t.split(" — ", 1)]
        t = t.strip("«» ")
        palabras = t.split()
        corto = len(palabras) <= 3
        v = b.get("visual", "")
        caps = [norm(w) for w in re.findall(r"[A-ZÁÉÍÓÚÑ]{5,}", v)]
        if corto:
            up = [w.upper() for w in palabras]
            tam, ef = 130, "golpe"
            t = "|".join(up[:-1] + ["*" + up[-1].rstrip(".,;:!?") + "*"])
        else:
            tam = 84 if len(t) <= 70 else 64 if len(t) <= 130 else 52
            ef = "desenfoque"
            if caps:
                ws = t.split()
                hay = False
                for i, w in enumerate(ws):
                    if norm(w) in caps and not hay:
                        ws[i] = "*" + w.rstrip(".,;:!?»") + "*" + w[len(w.rstrip(".,;:!?»")):]
                        hay = True
                t = " ".join(ws)
        lin = dict(t=t, tam=tam, efecto=ef, ancla=self.ancla(b), desfase=-0.05, paso=0.07 if not corto else 0.1)
        if corto:
            lin["sacudir"] = 0.45
        lineas = [lin]
        if ref:
            lineas.append(dict(t=ref, tam=40, color="morado", efecto="desenfoque", ancla=self.ancla(b), desfase=0.9))
        out = dict(tipo="cita", ancla=self.ancla(b), comilla=True, lineas=lineas)
        return out

    def ilustracion(self, b):
        il = self.ilustracion_de(b, rotar=True)
        base = dict(tipo="ilustracion", ancla=self.ancla(b), ilustracion=il)
        if il == "puerta":
            base["visual_y"] = 210
            base["entrada_visual"] = "ninguna"
            if re.search(r"cierra|cerrar|reduce", plano(b.get("visual", ""))):
                base["cerrar_en"] = self.ancla(b)
        return base

    def accion(self, b):
        txt = b["texto"].strip()
        il = self.ilustracion_de(b, rotar=True)
        lineas = []
        if self.primer_accion and not re.match(r"(?i)(hoy|esta semana|para hoy)", txt):
            lineas.append(dict(t="*PARA_HOY*", tam=110, ancla="beat", desfase=0.2, marca_color="morado"))
        self.primer_accion = False
        lineas.append(dict(t=txt, tam=tam_largo(len(txt), 104), color="morado", ancla=self.ancla(b), desfase=-0.1, paso=0.06))
        return dict(tipo="accion_hoy", ancla=self.ancla(b), ilustracion=il, tam_visual=620 if self.spec["formato"] == "vertical" else None, lineas=lineas)

    def ideas(self, b):
        items = [x for x in partes(b["texto"])]
        if len(items) == 1:
            items = [items[0]]
        ans = self.anclas_items(b["seg"], items, (b.get("palabra") or "").strip())
        base = dict(tipo="ideas", ancla=self.ancla(b),
                    filas=[dict(texto=it, ancla=a, desfase=-0.1) for it, a in zip(items, ans)])
        ic = self.icono_de(b, usar_texto=False)
        if ic:
            base["icono"] = ic
        return base

    def dia(self, b):
        m = re.match(r"\s*D[ií]a\s+(\d+)\s*·\s*(.+)", b["texto"], re.S)
        num, txt = (m.group(1), m.group(2).strip()) if m else ("", b["texto"])
        pill = None
        mv = re.search(r"etiqueta de libro:\s*(.+)$", b.get("visual", ""))
        if mv:
            pill = mv.group(1).strip()
        elif b.get("libro_id"):
            l = next((x for x in self.spec["libros"] if x.get("libro_id") == b["libro_id"]), None)
            pill = f"{l['titulo']} · {l['autor']}" if l else None
        out = dict(tipo="dia", ancla=self.ancla(b), numero=num or None,
                   lineas=[dict(t=txt, tam=tam_largo(len(txt), 90), ancla=self.ancla(b), desfase=-0.05, paso=0.05)])
        if pill:
            out["pill"] = pill
        return {k: v for k, v in out.items() if v is not None}


def traducir(spec):
    return Trad(spec).traducir(spec["beats"])
