# -*- coding: utf-8 -*-
"""Motor de plantilla de videos de libros (vertical 1080x1920 y horizontal 1920x1080) -> proyecto HyperFrames.

Entrada: especificación en formato AVANZADO (ver README.md; `simple.py` traduce el formato simple a este) y los
json de voz con timestamps por carácter. Salida: <proyecto>/index.html (+ assets).
Cada tipo de beat está implementado una sola vez con el look del piloto aprobado (R01 v4); el formato horizontal
reacomoda lo mismo: ilustración a la izquierda, texto a la derecha.
"""
import html
import json
import os
import re
import shutil
import subprocess
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
import ilus

E = html.escape
NAVY, PUR, PURD, YEL, YELD, CREAM, LAV, ORA = "#1B1740", "#5B3FB0", "#3B1580", "#F7D84A", "#F5C518", "#FFF6DC", "#EFE6FA", "#F08A1C"
COLORES = {"navy": NAVY, "morado": PUR, "amarillo": YEL, "blanco": "#fff", "naranja": ORA, "crema": CREAM}
LEAD, OV = 0.2, 0.22
MUS_HI, MUS_LO = 0.34, 0.16
TIPOS = ("titular", "reaccion", "cita", "icono", "ilustracion", "tarjeta_libro", "lista", "accion_hoy", "accion", "ideas", "dia")
EFECTOS = ("subir", "golpe", "desenfoque", "letras", "cruce", "ninguno")
ROTULOS_DEF = {"rewe": "Adolescente", "mario": "Papá"}
ROTULO_COLOR = {"rewe": PUR, "mario": ORA}
# Lo que se DICE y lo que se LEE no siempre es igual: en pantalla y subtítulos se escribe la forma de la izquierda.
PRONUNCIACION_DEF = {"egwwritings.org": "e ge doble u writings punto org", "P&R": "P y R"}
SIN_AUDIO_S_POR_PALABRA = 0.32

GEO = {
    "vertical": dict(W=1080, H=1920, res="portrait", zy0=200, zy1=1030, fsk=1.0,
                     cap=dict(left=70, top=1050, w=940, h=270, fs=80, pal=4, car=26), who_top=1008,
                     ilus_w=740, door_h=697, icon_w=440, icon_wc=340, circ=640,
                     panel=(60, 230, 960, 700), card_w=920, card_x=80, card_top=215, text_after_card=480),
    "horizontal": dict(W=1920, H=1080, res="landscape", zy0=70, zy1=730, fsk=0.9,
                       cap=dict(left=160, top=790, w=1600, h=130, fs=66, pal=7, car=44), who_top=738,
                       ilus_w=860, door_h=600, icon_w=500, icon_wc=400, circ=600,
                       panel=(140, 70, 1640, 660), card_w=800, card_x=100, card_top=None, text_after_card=None),
}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


def sin_etiqueta(texto):
    """Quita la etiqueta de tono [..] del inicio (se manda a ElevenLabs, pero no se lee ni se subtitula)."""
    t = texto.lstrip()
    if t.startswith("[") and "]" in t:
        return t[t.index("]") + 1:].lstrip()
    return texto


def libro_de(spec, ref):
    if isinstance(ref, dict):
        return ref
    L = spec["libros"]
    if isinstance(ref, int):
        return L[ref] if 0 <= ref < len(L) else None
    return next((l for l in L if l.get("id") == ref or l.get("libro_id") == ref or l["titulo"] == ref), None)


def lineas_de(b):
    out = list(b.get("lineas", []))
    for g in b.get("grupos", []):
        out += g.get("lineas", []) if isinstance(g, dict) else g
    if b.get("encabezado"):
        out.append(b["encabezado"])
    out += b.get("items", [])
    return out


# ───────────────────────── palabras con tiempo ─────────────────────────
def words_of(al, off, texto):
    ch = al["characters"]
    st = al["character_start_times_seconds"]
    en = al["character_end_times_seconds"]
    k = 0
    if texto.lstrip().startswith("["):
        j = "".join(ch).find("]")
        k = j + 1 if j >= 0 else 0
    out, cur = [], None
    for i in range(k, len(ch)):
        c = ch[i]
        if c.isspace():
            if cur:
                out.append(cur)
                cur = None
            continue
        if cur is None:
            cur = {"t": c, "s": st[i] + off, "e": en[i] + off}
        else:
            cur["t"] += c
            cur["e"] = en[i] + off
    if cur:
        out.append(cur)
    return out


def words_sin_audio(texto, off):
    out, t = [], off
    for w in sin_etiqueta(texto).split():
        out.append({"t": w, "s": t, "e": t + SIN_AUDIO_S_POR_PALABRA})
        t += SIN_AUDIO_S_POR_PALABRA
    return out


def aplicar_pronunciacion(words, mapa):
    """Une varias palabras dichas («e ge doble u writings punto org») en la forma escrita («egwwritings.org»)."""
    for escrito, dicho in mapa.items():
        toks = [norm(x) for x in dicho.split()]
        if not toks:
            continue
        i, out = 0, []
        while i < len(words):
            if [norm(w["t"]) for w in words[i:i + len(toks)]] == toks:
                tail = words[i + len(toks) - 1]["t"]
                punct = re.search(r"[.,;:!?»)]+$", tail)
                out.append({"t": escrito + (punct.group(0) if punct else ""), "s": words[i]["s"], "e": words[i + len(toks) - 1]["e"]})
                i += len(toks)
            else:
                out.append(words[i])
                i += 1
        words = out
    return words


def groups_of(words, maxp, maxc):
    gs, cur = [], []

    def flush():
        nonlocal cur
        if cur:
            gs.append(cur)
            cur = []
    for i, w in enumerate(words):
        if cur and (len(cur) >= maxp or len(" ".join(x["t"] for x in cur + [w])) > maxc):
            flush()
        cur.append(w)
        gap = (words[i + 1]["s"] - w["e"]) if i + 1 < len(words) else 9
        if w["t"][-1] in ".?!:;" or gap > 0.4 or (w["t"][-1] == "," and len(cur) >= 2):
            flush()
    flush()
    return gs


# ───────────────────────── validación del formato avanzado ─────────────────────────
def validar(spec, carpeta_spec=None):
    err = []
    if not spec.get("id") or not re.fullmatch(r"[A-Za-z0-9_-]+", str(spec["id"])):
        err.append("«id» es obligatorio y solo admite letras, números, guion y guion bajo.")
    if spec.get("formato") not in GEO:
        err.append(f"«formato» debe ser «vertical» u «horizontal» (tiene «{spec.get('formato')}»).")
    nombres = [s.get("nombre") for s in spec["segmentos"]]
    if not nombres:
        err.append("Faltan «segmentos».")
    if len(set(nombres)) != len(nombres):
        err.append("Hay nombres de segmento repetidos.")
    for s in spec["segmentos"]:
        for k in ("nombre", "voz", "texto"):
            if not s.get(k):
                err.append(f"Un segmento no tiene «{k}»: {s}")
        if s.get("texto") and not s["texto"].lstrip().startswith("["):
            err.append(f"Segmento «{s.get('nombre')}»: el texto debe empezar con una etiqueta de tono, p. ej. [cálido, cercano].")
    if not spec["beats"]:
        err.append("Faltan «beats».")
    for i, b in enumerate(spec["beats"]):
        if b.get("tipo") not in TIPOS:
            err.append(f"beat {i}: «tipo» debe ser uno de {', '.join(TIPOS)} (tiene «{b.get('tipo')}»).")
        if "ancla" not in b and i > 0:
            err.append(f"beat {i}: falta «ancla» (cuándo empieza).")
        if b.get("ilustracion") and b["ilustracion"] not in ilus.ILUSTRACIONES:
            err.append(f"beat {i}: ilustración «{b['ilustracion']}» no existe. Opciones: {', '.join(ilus.ILUSTRACIONES)}.")
        if b.get("icono") and b["icono"] not in ilus.ICONOS:
            err.append(f"beat {i}: ícono «{b['icono']}» no existe. Opciones: {', '.join(ilus.ICONOS)}.")
        if b.get("svg") and carpeta_spec and not os.path.exists(os.path.join(carpeta_spec, b["svg"])):
            err.append(f"beat {i}: no existe el archivo svg «{b['svg']}».")
        if "libro" in b and not libro_de(spec, b["libro"]):
            err.append(f"beat {i}: «libro» {b['libro']!r} no está en «libros» (usa el número 0, 1… o el título).")
        for L in lineas_de(b):
            if isinstance(L, dict) and L.get("efecto") and L["efecto"] not in EFECTOS:
                err.append(f"beat {i}: efecto «{L['efecto']}» no válido. Opciones: {', '.join(EFECTOS)}.")
    for l in spec["libros"]:
        for k in ("titulo", "autor", "donde"):
            if not l.get(k):
                err.append(f"Un libro no tiene «{k}»: {l}")
    if err:
        raise SystemExit("La especificación tiene errores:\n - " + "\n - ".join(err))


# ───────────────────────── constructor ─────────────────────────
class Constructor:
    def __init__(self, spec, audio_dir, proyecto, base_dir, assets_dir, carpeta_spec, seco=False):
        self.spec, self.G = spec, GEO[spec["formato"]]
        self.W, self.Hh = self.G["W"], self.G["H"]
        self.audio_dir, self.proyecto, self.base_dir, self.assets_dir = audio_dir, proyecto, base_dir, assets_dir
        self.carpeta_spec, self.seco = carpeta_spec, seco
        self.H, self.TL, self.n = [], [], 0
        self.seg, self.voice_end, self.avisos = {}, 0.0, []
        self.horiz = spec["formato"] == "horizontal"

    def A(self, x): self.H.append(x)
    def T(self, x): self.TL.append(x)
    def uid(self, p="e"):
        self.n += 1
        return f"{p}{self.n}"

    def aviso(self, m):
        self.avisos.append(m)

    # ───────── voz
    def tiempos_voz(self):
        mapa = dict(PRONUNCIACION_DEF)
        mapa.update(self.spec.get("pronunciacion", {}))
        if not self.seco:
            os.makedirs(os.path.join(self.proyecto, "assets", "voz"), exist_ok=True)
        t = LEAD
        for s in self.spec["segmentos"]:
            n = s["nombre"]
            if self.seco:
                words = words_sin_audio(s["texto"], t)
                d = (words[-1]["e"] - t + 0.2) if words else 1.0
            else:
                mp3 = os.path.join(self.audio_dir, f"{n}.mp3")
                js = json.load(open(os.path.join(self.audio_dir, f"{n}.json"), encoding="utf-8"))
                d = dur(mp3)
                shutil.copy(mp3, os.path.join(self.proyecto, "assets", "voz", f"{n}.mp3"))
                words = words_of(js["alignment"], t, s["texto"])
            words = aplicar_pronunciacion(words, mapa)
            self.seg[n] = dict(s=t, e=t + d, d=d, v=s["voz"], words=words)
            t = t + d + float(s.get("pausa", 0))
        self.voice_end = self.seg[self.spec["segmentos"][-1]["nombre"]]["e"]

    def palabra(self, ref, seg_ctx=None, donde=""):
        """'s2:palabra', 's2:dos palabras', 's2:palabra@2', 's2:palabra@ultima' o solo 'palabra' (segmento de contexto)."""
        if ":" in ref:
            sn, w = ref.split(":", 1)
        else:
            sn, w = seg_ctx, ref
        if sn not in self.seg:
            raise SystemExit(f"{donde}: el segmento «{sn}» no existe (ancla «{ref}»).")
        occ = 1
        if "@" in w:
            w, o = w.rsplit("@", 1)
            occ = -1 if o in ("ultima", "última", "last") else int(o)
        words = self.seg[sn]["words"]
        toks = [norm(x) for x in w.split() if norm(x)]
        ns = [norm(x["t"]) for x in words]
        hits = [i for i in range(len(ns) - len(toks) + 1) if ns[i:i + len(toks)] == toks] if toks else []
        if not hits and toks:                       # tolerancia: misma raíz (regañar ~ regaño)
            hits = [i for i in range(len(ns) - len(toks) + 1)
                    if all(ns[i + k] and (ns[i + k].startswith(toks[k][:5]) or toks[k].startswith(ns[i + k][:5])) and len(ns[i + k]) >= 4
                           for k in range(len(toks)))]
            if hits:
                self.aviso(f"{donde}: «{w}» no está exacta en «{sn}»; usé «{words[hits[0]]['t']}».")
        if not hits:
            vistas = " ".join(x["t"] for x in words[:16])
            raise SystemExit(f"{donde}: no hay «{w}» en el segmento «{sn}». Empieza así: {vistas} …")
        if occ > len(hits):
            raise SystemExit(f"{donde}: «{w}» aparece {len(hits)} vez/veces en «{sn}», pediste la {occ}.")
        return words[hits[-1] if occ == -1 else hits[occ - 1]]["s"]

    def resolver(self, ancla, desfase=None, t_beat=None, seg_ctx=None, donde=""):
        """ancla -> segundos. Desfase por omisión: segmento -0.1, palabra -0.12, fin +0.45; número/inicio/beat 0."""
        if isinstance(ancla, (int, float)):
            return float(ancla) + (desfase or 0)
        a = str(ancla)
        if a == "inicio":
            base, d0 = 0.0, 0.0
        elif a == "fin":
            base, d0 = self.voice_end, 0.45
        elif a == "beat":
            if t_beat is None:
                raise SystemExit(f"{donde}: «beat» solo se usa dentro de las líneas de un beat.")
            base, d0 = t_beat, 0.0
        elif a in self.seg:
            base, d0 = self.seg[a]["s"], -0.1
        else:
            base, d0 = self.palabra(a, seg_ctx, donde), -0.12
        return base + (d0 if desfase is None else desfase)

    # ───────── texto
    @staticmethod
    def parse(t):
        lines = []
        for raw in t.split("|"):
            runs = []
            for k, p in enumerate(raw.split("*")):
                units = [u.replace("_", " ") for u in p.split()]
                if units:
                    runs.append((k % 2 == 1, units))
            lines.append(runs)
        return lines

    @staticmethod
    def est_ancho(lines, fs):
        mx = 0
        for runs in lines:
            txt = " ".join(" ".join(u) for _, u in runs)
            letras = [c for c in txt if c.isalpha()]
            k = 0.6 if letras and all(c.isupper() for c in letras) else 0.52
            mx = max(mx, len(txt) * fs * k)
        return mx

    def romper(self, t, fs, fit):
        """Parte un texto largo en renglones balanceados (respetando *marca*) hasta que quepa en `fit`."""
        if "|" in t or self.est_ancho(self.parse(t), fs) <= fit or len(t.replace("*", "").split()) <= 3:
            return t                      # cabe, ya trae renglones, o son ≤3 palabras (se reduce en vez de partir)
        toks = []
        for i, part in enumerate(t.split("*")):
            for w in part.split():
                toks.append((w, i % 2 == 1))
        total = sum(len(w) + 1 for w, _ in toks)

        def pinta(line):
            out, prev = [], False
            for w, b in line:
                if b != prev:
                    out.append("*")
                    prev = b
                out.append(("" if out and out[-1] == "*" else " ") + w if out else w)
            if prev:
                out.append("*")
            return "".join(out).replace("* ", " *").replace("  ", " ")
        mejor = t
        for n in range(2, 9):
            target, out, cur, cl = total / n, [], [], 0
            for w, b in toks:
                if cur and cl + len(w) > target and len(out) < n - 1:
                    out.append(cur)
                    cur, cl = [], 0
                cur.append((w, b))
                cl += len(w) + 1
            out.append(cur)
            cand = "|".join(pinta(l) for l in out)
            mejor = cand
            if self.est_ancho(self.parse(cand), fs) <= fit:
                break
        return mejor

    def preparar_linea(self, L, fit_w, efecto_def):
        if isinstance(L, str):
            L = {"t": L}
        fs = float(L.get("tam", 110)) * self.G["fsk"]
        t = self.romper(L["t"], fs, fit_w)
        lines = self.parse(t)
        w = self.est_ancho(lines, fs)
        if w > fit_w:
            fs *= fit_w / w
        color = L.get("color", "navy")
        return dict(L=L, lines=lines, fs=fs, h=len(lines) * fs * 1.06, efecto=L.get("efecto", efecto_def),
                    color=COLORES.get(color, color))

    def altura_grupo(self, pls):
        return sum(p["h"] + (0.14 * p["fs"] if i else 0) for i, p in enumerate(pls))

    def emitir_linea(self, p, y, colx, colw, t0, seg_ctx, donde, cruce_dir=1):
        L, fs = p["L"], p["fs"]
        lid = self.uid("ln")
        unidades = sum(len(u) for runs in p["lines"] for _, u in runs)
        anc, des = L.get("ancla"), L.get("desfase")
        paso = float(L.get("paso", 0.09))
        pick = lambda x, k: (x[k] if k < len(x) else None) if isinstance(x, list) else x
        tiempos = []
        for k in range(unidades):
            a, d = pick(anc, k), pick(des, k)
            if anc is None:
                a = "beat"
            if k > 0 and (a is None or (not isinstance(anc, list) and not isinstance(des, list))):
                tiempos.append(tiempos[-1] + paso)            # un ancla para toda la línea: se escalonan con «paso»
            else:
                if a is None:
                    a = "beat"
                if d is None:
                    d = 0 if (str(a) in self.seg or a == "beat") else -0.08
                tiempos.append(self.resolver(a, d, t0, seg_ctx, donde))
        ef = p["efecto"]
        if ef == "ninguno":
            tiempos = [t0] * unidades
        h = [f'<div id="{lid}" class="ctr" style="left:{colx}px;width:{colw}px;top:{y:.0f}px;font-size:{fs:.1f}px;color:{p["color"]}">']
        k = 0
        for runs in p["lines"]:
            h.append('<span class="ln">')
            for brush, units in runs:
                inner, k_ini = [], k
                for u in units:
                    uid_ = f"{lid}_{k}"
                    tt = tiempos[k]
                    if ef == "letras":
                        letras = "".join(f'<span class="kl" id="{uid_}_{i}">{E(c)}</span>' for i, c in enumerate(u))
                        inner.append(f'<span class="lt" style="margin:0 .09em">{letras}</span>')
                        for i in range(len(u)):
                            self.T(f"tl.fromTo('#{uid_}_{i}',{{y:70,opacity:0}},{{y:0,opacity:1,duration:.35,ease:'expo.out'}},{tt + i * .025:.2f});")
                    else:
                        inner.append(f'<span class="kw"><span class="kwi" id="{uid_}">{E(u)}</span></span>')
                        if ef == "subir":
                            self.T(f"tl.fromTo('#{uid_}',{{yPercent:115,opacity:0}},{{yPercent:0,opacity:1,duration:.55,ease:'expo.out'}},{tt:.2f});")
                        elif ef == "golpe":
                            self.T(f"tl.fromTo('#{uid_}',{{scale:1.45,opacity:0,filter:'blur(10px)'}},{{scale:1,opacity:1,filter:'blur(0px)',duration:.5,ease:'expo.out'}},{tt:.2f});")
                        elif ef == "desenfoque":
                            self.T(f"tl.fromTo('#{uid_}',{{opacity:0,filter:'blur(12px)'}},{{opacity:1,filter:'blur(0px)',duration:.3,ease:'power2.out'}},{tt:.2f});")
                    k += 1
                if brush:
                    bid = f"{lid}_b{k_ini}"
                    mc = L.get("marca_color")
                    st = f' style="color:{COLORES.get(mc, mc)}"' if mc else ""
                    h.append(f'<span class="brush"><span class="bar" id="{bid}"></span><span class="tx"{st}>{"".join(inner)}</span></span>')
                    self.T(f"tl.fromTo('#{bid}',{{scaleX:0}},{{scaleX:1,duration:.5,ease:'power3.out'}},{tiempos[k_ini] + (.2 if ef == 'ninguno' else .1):.2f});")
                else:
                    h.append("".join(inner))
            h.append("</span>")
        h.append("</div>")
        self.A("".join(h))
        if ef == "cruce":
            self.whipin(f"#{lid}", tiempos[0], cruce_dir, 320)
        if L.get("sacudir"):
            self.shake(f"#{lid}", tiempos[0] + (0.4 if L["sacudir"] is True else float(L["sacudir"])))
        extra = []
        if L.get("tachar"):
            d = 0.45 if L["tachar"] is True else float(L["tachar"])
            sid = self.uid("tk")
            wd = min(colw * .95, self.est_ancho(p["lines"], fs) + 60)
            self.A(f'<div id="{sid}" class="abs" style="left:{colx + (colw - wd) / 2:.0f}px;top:{y + fs * 0.615:.0f}px;width:{wd:.0f}px;height:{max(10, fs * .12):.0f}px;border-radius:8px;background:{ORA};transform-origin:0 50%"></div>')
            self.T(f"tl.fromTo('#{sid}',{{scaleX:0}},{{scaleX:1,duration:.3,ease:'power3.out'}},{tiempos[0] + d:.2f});")
            extra.append(sid)
        return lid, min(tiempos), extra

    # ───────── efectos sueltos
    def shake(self, sel, t0):
        f = 1 / 30
        self.T(f"tl.to('{sel}',{{x:9,y:-4,duration:{f:.3f},ease:'power2.out'}},{t0:.2f});tl.to('{sel}',{{x:-6,y:3,duration:{f:.3f}}});tl.to('{sel}',{{x:0,y:0,duration:{f:.3f}}});")

    def whipin(self, sel, t, direction=1, dx=300):
        self.T(f"tl.fromTo('{sel}',{{x:{direction * dx},opacity:0,filter:'blur(14px)'}},{{x:0,opacity:1,filter:'blur(0px)',duration:.32,ease:'power4.out'}},{t:.2f});")

    def swapout(self, sel, t, direction=-1, dx=240, dur_=.2):
        self.T(f"tl.to('{sel}',{{x:{direction * dx},opacity:0,filter:'blur(12px)',duration:{dur_},ease:'power3.in'}},{t:.2f});")

    def pop(self, sel, t0, d=.5, frm=.3, ease="back.out(1.6)"):
        self.T(f"tl.fromTo('{sel}',{{scale:{frm},opacity:0}},{{scale:1,opacity:1,duration:{d},ease:'{ease}'}},{t0:.2f});")

    # ───────── visuales
    def visual(self, b, bi):
        G = self.G
        if b.get("numero") is not None:
            w_ = b.get("tam_visual") or (G["icon_wc"] * (1.0 if self.horiz else 0.9))
            num = E(str(b["numero"]))
            fs_n = 130 if len(num) == 1 else 100
            svg = (f'<svg width="{round(w_)}" height="{round(w_)}" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">'
                   f'<circle cx="100" cy="100" r="98" fill="{PURD}"/><circle cx="100" cy="100" r="82" fill="{PUR}"/>'
                   f'<text x="100" y="{100 + fs_n * 0.35:.0f}" font-size="{fs_n}" font-weight="900" fill="{YEL}" text-anchor="middle" font-family="Nunito, sans-serif">{num}</text></svg>')
            return dict(kind="icono", svg=svg, w=round(w_), h=round(w_), box=False, circ=False)
        if b.get("ilustracion"):
            fn, vw, vh = ilus.ILUSTRACIONES[b["ilustracion"]]
            if b["ilustracion"] == "puerta":
                h_ = b.get("tam_visual") or G["door_h"]
                w_ = h_ * vw / vh
            else:
                w_ = b.get("tam_visual") or G["ilus_w"]
                h_ = w_ * vh / vw
            return dict(kind="ilus", svg=fn(f"v{bi}"), w=round(w_), h=round(h_), box=True)
        if b.get("svg"):
            raw = open(os.path.join(self.carpeta_spec, b["svg"]), encoding="utf-8").read()
            m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', raw)
            vw, vh = (float(m.group(1)), float(m.group(2))) if m else (880.0, 540.0)
            w_ = b.get("tam_visual") or G["ilus_w"]
            for _ in range(2):
                raw = re.sub(r'(<svg[^>]*?)\s(width|height)="[^"]*"', r"\1", raw)
            return dict(kind="ilus", svg=raw, w=round(w_), h=round(w_ * vh / vw), box=True)
        if b.get("icono"):
            fn, ratio = ilus.ICONOS[b["icono"]]
            circ = bool(b.get("circulo"))
            w_ = b.get("tam_visual") or (G["icon_wc"] if circ else G["icon_w"])
            return dict(kind="icono", svg=fn(round(w_)), w=round(w_), h=round(w_ * ratio), box=False, circ=circ)
        return None

    def emitir_visual(self, vid, v, x, y, t0, entrada):
        cls, extra = ("pic", "") if v["box"] else ("abs", "")
        self.A(f'<div id="{vid}" class="{cls}" style="left:{x:.0f}px;top:{y:.0f}px;width:{v["w"]}px;height:{v["h"]}px">{v["svg"]}</div>')
        if entrada == "subir":
            self.T(f"tl.fromTo('#{vid}',{{y:90,opacity:0}},{{y:0,opacity:1,duration:.6,ease:'expo.out'}},{t0 + .03:.2f});")
        elif entrada == "derecha":
            self.T(f"tl.fromTo('#{vid}',{{x:140,opacity:0,filter:'blur(10px)'}},{{x:0,opacity:1,filter:'blur(0px)',duration:.5,ease:'power4.out'}},{t0 + .05:.2f});")
        elif entrada == "pop":
            self.pop(f"#{vid}", t0 + .15, .55, .2)
        elif entrada == "quieta":
            self.T(f"tl.fromTo('#{vid}',{{scale:1.05}},{{scale:1,duration:1.6,ease:'power2.out'}},{t0:.2f});")

    def tarjeta(self, cid, libro, x, y, w, t_in):
        k = 1.08 if self.horiz else 1
        tfs = (60 if len(libro["titulo"]) <= 24 else 54) * k
        self.A(f'<div id="{cid}" class="card" style="left:{x}px;top:{y:.0f}px;width:{w}px"><div class="bt" style="font-size:{tfs:.0f}px">{E(libro["titulo"])}</div><div class="ba" style="font-size:{40 * k:.0f}px">{E(libro["autor"])}</div></div>')
        self.whipin(f"#{cid}", t_in, 1, 260)

    def alto_tarjeta(self, libro, w, donde=False):
        k = 1.08 if self.horiz else 1
        tfs, afs = (60 if len(libro["titulo"]) <= 24 else 54) * k, 40 * k
        disp = w - 58 - 76
        n = max(1, -(-int(len(libro["titulo"]) * tfs * 0.52) // disp))
        h = 52 + n * tfs * 1.1 + 6 + afs * 1.36
        if donde:
            nd = max(1, -(-int(len(libro["donde"]) * 38 * 0.5) // disp))
            h += 6 + nd * 38 * 1.36
        return h

    # ───────── escenas
    def escena(self, sid, s, e, z, last=False):
        self.A(f'<div id="{sid}" class="scene clip" data-start="{s:.2f}" data-duration="{e - s:.2f}" data-track-index="1" data-layout-allow-overflow style="z-index:{z}"><div id="{sid}-in" class="in">')
        if not last:
            self.T(f"tl.to('#{sid}-in',{{opacity:0,filter:'blur(9px)',duration:{OV - .02:.2f},ease:'power2.in'}},{e - OV:.2f});")

    def fin_escena(self):
        self.A("</div></div>")

    def grupos_de(self, b):
        tipo = b["tipo"]
        if b.get("items"):
            grupos = []
            if b.get("encabezado"):
                grupos.append(dict(lineas=[dict(b["encabezado"])], sal="izquierda"))
            for it in b["items"]:
                it = dict(it, efecto=it.get("efecto", "cruce"), color=it.get("color", "amarillo"))
                grupos.append(dict(lineas=[it], sal="cruce"))
            return grupos
        gl = b.get("grupos")
        if gl is None:
            gl = [dict(lineas=b.get("lineas", []))] if b.get("lineas") else []
        out = []
        for g in gl:
            if not isinstance(g, dict):
                g = dict(lineas=g)
            out.append(dict(lineas=list(g.get("lineas", [])), sal=g.get("salida", "izquierda")))
        return out

    def emitir_beat(self, sid, bi, b, t0, t1, ctx):
        G, spec, W, horiz = self.G, self.spec, self.W, self.horiz
        tipo = b["tipo"]
        seg_ctx = ctx["seg_ctx"]
        donde = f"beat {bi} ({tipo})"
        ef_def = "golpe" if tipo == "reaccion" else "subir"
        en_panel = bool(b.get("panel") or b.get("continua"))
        zy0, zy1 = G["zy0"], G["zy1"]
        zmid = (zy0 + zy1) / 2
        grupos = self.grupos_de(b)
        vis = None if en_panel else self.visual(b, bi)
        libro = None if en_panel or "libro" not in b else libro_de(spec, b["libro"])
        comilla = bool(b.get("comilla", False)) and not en_panel
        filas = b.get("filas") if not en_panel else None
        split = bool(vis or libro or (filas and b.get("icono")))
        px, py, pw, ph = G["panel"]
        if en_panel:
            colx, colw, fit = px + 20, pw - 40, pw - 40
        elif horiz:
            colx, colw, fit = (980, 880, 840) if split else (160, 1600, 1560)
        else:
            colx, colw, fit = 0, W, 980
        pls_g = [[self.preparar_linea(L, fit, ef_def) for L in g["lineas"]] for g in grupos]
        hmax = max((self.altura_grupo(p) for p in pls_g), default=0)
        chip = b.get("chip")
        chip_h = 90 if (chip and not en_panel) else 0
        y_text = None            # None = centrar verticalmente
        # ----- visual / tarjeta
        if vis:
            if horiz:
                vx = 500 - vis["w"] / 2
                vy = b.get("visual_y", zmid - vis["h"] / 2)
            else:
                modo = b.get("posicion_visual") or ("arriba" if vis["kind"] == "icono" else "abajo")
                vx = (W - vis["w"]) / 2
                if hmax == 0:
                    vy = b.get("visual_y", zy0 + (zy1 - zy0 - vis["h"]) / 2)
                elif modo == "arriba":
                    vy = b.get("visual_y", 240 if vis.get("circ") else 215)
                    y_text = vy + vis["h"] + 50
                else:
                    vy = b.get("visual_y", 1000 - vis["h"])
                    y_text = 215
            if vis.get("circ"):
                cd = G["circ"]
                cx_ = vx + vis["w"] / 2
                cy_ = (vy + vis["h"] / 2) if horiz else (200 + cd / 2)
                cid = self.uid("circ")
                self.A(f'<div id="{cid}" class="abs" style="left:{cx_ - cd / 2:.0f}px;top:{cy_ - cd / 2:.0f}px;width:{cd}px;height:{cd}px;border-radius:50%;background:{LAV}"></div>')
                self.T(f"tl.fromTo('#{cid}',{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.7,ease:'expo.out'}},{t0 + .1:.2f});")
            vid = self.uid("vis")
            entrada = b.get("entrada_visual") or ("pop" if vis["kind"] == "icono" else "subir")
            self.emitir_visual(vid, vis, vx, vy, t0, entrada)
            if b.get("cerrar_en") and b.get("ilustracion") == "puerta":
                tcl = self.resolver(b["cerrar_en"], 0, t0, seg_ctx, donde)
                self.T(f"tl.fromTo('#door-leaf',{{scaleX:.3,svgOrigin:'30 390'}},{{scaleX:1,svgOrigin:'30 390',duration:.5,ease:'power4.in'}},{tcl - .35:.2f});")
                self.T(f"tl.to('#door-light',{{opacity:0,duration:.35,ease:'power2.in'}},{tcl - .1:.2f});")
                self.shake(f"#{vid}", tcl + .15)
        elif libro:
            cw = G["card_w"]
            ch = self.alto_tarjeta(libro, cw)
            if horiz:
                cy = zmid - ch / 2
            elif hmax == 0:
                cy = zmid - ch / 2
            else:
                cy = G["card_top"]
                y_text = max(G["text_after_card"], cy + ch + 30)
            t_l = self.resolver(b["libro_ancla"], b.get("libro_desfase"), t0, seg_ctx, donde) if "libro_ancla" in b else t0 + .05
            self.tarjeta(self.uid("bk"), libro, G["card_x"], cy, cw, t_l)
        elif filas:
            self.emitir_filas(b, filas, t0, seg_ctx, donde, colx, colw)
        if comilla:
            qid = self.uid("qm")
            fsq = 560 if horiz else 640
            qx, qw = (colx, colw) if (split or not horiz) else (0, W)
            self.A(f'<div id="{qid}" class="abs" style="left:{qx}px;top:{(zmid - 330) if horiz else 330:.0f}px;width:{qw}px;text-align:center;font-weight:900;font-size:{fsq}px;line-height:1;color:{YEL};opacity:0">“</div>')
            self.T(f"tl.fromTo('#{qid}',{{opacity:0,scale:.6}},{{opacity:.6,scale:1,duration:.6,ease:'expo.out'}},{t0 + .2:.2f});")
        if b.get("decoracion"):
            fn, ratio = ilus.ICONOS[b["decoracion"]]
            dw = 460 if horiz else 420
            ymid_t = (y_text + hmax / 2) if y_text is not None else zmid
            did = self.uid("dec")
            self.A(f'<div id="{did}" class="abs" style="left:{colx + (colw - dw) / 2:.0f}px;top:{ymid_t - dw * ratio / 2:.0f}px;width:{dw}px;height:{dw * ratio:.0f}px">{fn(dw)}</div>')
            self.pop(f"#{did}", t0 + .25, .6, .4, "expo.out")
        # ----- grupos de texto
        exits, y_after0 = [], None
        for gi, (g, pls) in enumerate(zip(grupos, pls_g)):
            gid = self.uid("g")
            self.A(f'<div id="{gid}" class="abs" style="left:0;top:0;width:{W}px;height:{self.Hh}px">')
            gh = self.altura_grupo(pls)
            if en_panel:
                y = py + ph / 2 - 20 - gh / 2
            elif y_text is not None:
                y = y_text
            else:
                y = zmid - (gh + chip_h) / 2
            ids, tf = [], None
            for pi, p in enumerate(pls):
                if pi:
                    y += 0.14 * p["fs"]
                lid, tp, extra = self.emitir_linea(p, y, colx, colw, t0, seg_ctx, donde, cruce_dir=(1 if gi % 2 == 0 else -1))
                ids += [lid] + extra
                tf = tp if tf is None else min(tf, tp)
                y += p["h"]
            if gi == 0:
                y_after0 = y
            self.A("</div>")
            exits.append((gid, ids, tf, g["sal"]))
        for gi in range(len(exits) - 1):
            gid, ids, tf, sal = exits[gi]
            tn = exits[gi + 1][2]
            if sal == "cruce":
                self.swapout(f"#{ids[0]}", tn - .12, -1 if gi % 2 == 0 else 1)
            elif sal == "arriba":
                self.T(f"tl.to('#{gid}',{{opacity:0,y:-30,filter:'blur(10px)',duration:.2,ease:'power2.in'}},{tn - .08:.2f});")
            else:
                self.swapout(f"#{gid}", tn - .14, -1, 260, .22)
        if chip:
            cid = self.uid("chip")
            tc = self.resolver(chip.get("ancla", "beat"), chip.get("desfase", 0), t0, seg_ctx, donde)
            if en_panel:
                self.A(f'<div id="{cid}" class="chip" style="left:{px}px;width:{pw}px;top:{py + 62}px"><span style="color:{YEL};font-size:{40 if horiz else 44}px;padding:6px 20px">{E(chip["texto"])}</span></div>')
                self.T(f"tl.fromTo('#{cid}',{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4,ease:'power3.out'}},{tc:.2f});")
                ctx["fade"].append(f"#{cid}")
            else:
                ytop = (y_after0 + 28) if (exits and y_after0 is not None and hmax) else (zmid - 40)
                self.A(f'<div id="{cid}" class="chip" style="left:{colx}px;width:{colw}px;top:{ytop:.0f}px"><span style="background:{PURD};color:#fff;font-size:{50 if horiz else 56}px;padding:12px 40px;letter-spacing:.04em;text-transform:none">{E(chip["texto"])}</span></div>')
                self.T(f"tl.fromTo('#{cid}',{{y:40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:'back.out(1.5)'}},{tc:.2f});")
        if b.get("pill"):                               # etiqueta de libro bajo el texto (beats «dia»)
            pid = self.uid("pill")
            ytop = (y_after0 + 34) if (y_after0 is not None and hmax) else zmid + 40
            self.A(f'<div id="{pid}" class="chip" style="left:{colx}px;width:{colw}px;top:{ytop:.0f}px"><span style="background:{LAV};color:{PURD};font-size:{36 if horiz else 38}px;padding:12px 32px;letter-spacing:.02em;text-transform:none;line-height:1.2">{E(b["pill"])}</span></div>')
            self.T(f"tl.fromTo('#{pid}',{{y:30,opacity:0}},{{y:0,opacity:1,duration:.5,ease:'power3.out'}},{t0 + .5:.2f});")
        if b.get("puntos") and b.get("items"):
            n = len(b["items"])
            tis = [e_[2] for e_ in exits[len(exits) - n:]]
            for i in range(n):
                did = self.uid("pd")
                x = px + pw / 2 - (n - 1) * 40 + i * 80 - 18
                self.A(f'<div id="{did}" class="abs" style="left:{x:.0f}px;top:{py + ph - 80}px;width:36px;height:36px;border-radius:50%;background:#fff;opacity:.28"></div>')
                self.T(f"tl.to('#{did}',{{opacity:1,backgroundColor:'{YEL}',duration:.2,ease:'power2.out'}},{tis[i] - .05:.2f});")
                ctx["fade"].append(f"#{did}")
        if exits and b.get("items"):
            ctx["fade"].append(f"#{exits[-1][1][0]}")
        elif exits and en_panel and exits[-1][1]:
            ctx["fade"].append(f"#{exits[-1][0]}")

    def emitir_filas(self, b, filas, t0, seg_ctx, donde, colx, colw):
        """Lista de ideas: tarjetas blancas con palomita que entran una a una, ancladas a la palabra de cada una."""
        G, horiz = self.G, self.horiz
        n = len(filas)
        fs = (46 if n >= 4 else 54) * (0.9 if horiz else 1)
        if b.get("icono"):
            fn, ratio = ilus.ICONOS[b["icono"]]
            if horiz:
                iw = 420
                ico = self.uid("ico")
                self.A(f'<div id="{ico}" class="abs" style="left:{500 - iw / 2:.0f}px;top:{(G["zy0"] + G["zy1"]) / 2 - iw * ratio / 2:.0f}px;width:{iw}px;height:{iw * ratio:.0f}px">{fn(iw)}</div>')
                self.pop(f"#{ico}", t0 + .1, .5, .3)
        wcol = colw if horiz else 920
        x0 = colx if horiz else 80
        cid = self.uid("filas")
        self.A(f'<div id="{cid}" class="abs" style="left:{x0}px;top:{G["zy0"]}px;width:{wcol}px;height:{G["zy1"] - G["zy0"]}px;display:flex;flex-direction:column;justify-content:center;gap:{16 if horiz else 20}px">')
        for i, f in enumerate(filas):
            rid = self.uid("fila")
            self.A(f'<div id="{rid}" class="fila" style="font-size:{fs:.0f}px"><span class="ck">{ilus.icon_check(round(fs * 1.1))}</span><span class="ft">{E(f["texto"])}</span></div>')
            tt = self.resolver(f.get("ancla", "beat"), f.get("desfase", -0.1), t0, seg_ctx, donde)
            self.whipin(f"#{rid}", tt, 1, 260)
        self.A("</div>")

    def panel_inicio(self, b, t0):
        px, py, pw, ph = self.G["panel"]
        col = COLORES.get(b["panel"], b["panel"])
        self.A(f'<div id="panel" class="abs" style="left:{px}px;top:{py}px;width:{pw}px;height:{ph}px;border-radius:60px;background:{col}"></div>')
        self.T(f"tl.fromTo('#panel',{{clipPath:'circle(0% at 50% 50%)'}},{{clipPath:'circle(120% at 50% 50%)',duration:.6,ease:'power2.inOut'}},{t0:.2f});")

    # ───────── cierre
    def alto_card_final(self, l, w):
        if w >= 900:
            return 330 if len(l["titulo"]) > 24 else 262
        disp = w - 76 - 20
        n = max(1, -(-int(len(l["titulo"]) * 57 * 0.52) // disp))
        nd = max(1, -(-int(len(l["donde"]) * 38 * 0.5) // disp))
        return 48 + n * 57 * 1.1 + 6 + 44 * 1.36 + 6 + nd * 38 * 1.36 + 10

    def cierre(self, t0):
        spec, W, horiz = self.spec, self.W, self.horiz
        c = spec.get("cierre") or {}
        libros = spec["libros"]
        self.A(f'<div id="e0" class="ctr navyt" style="left:0;width:{W}px;top:{100 if horiz else 215}px;font-size:{84 if horiz else 76}px">{E(c.get("titulo", "Para leer más"))}</div>')
        self.T(f"tl.fromTo('#e0',{{y:40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:'expo.out'}},{t0 + .1:.2f});")
        n = len(libros)
        cw = min(820, int((1720 - 40 * (n - 1)) / max(n, 1))) if horiz else 920
        x0 = (W - (n * cw + 40 * (n - 1))) / 2 if horiz else 80
        y = 270 if horiz else 330
        hmax = 0
        for i, l in enumerate(libros):
            hh = self.alto_card_final(l, cw)
            hmax = max(hmax, hh)
            tfs = (60 if len(l["titulo"]) > 24 else 68) * (0.95 if horiz else 1)
            xx = (x0 + i * (cw + 40)) if horiz else 80
            self.A(f'<div id="ec{i}" class="card" style="left:{xx:.0f}px;top:{y}px;width:{cw}px;padding:24px 38px"><div class="bt" style="font-size:{tfs:.0f}px">{E(l["titulo"])}</div><div class="ba" style="font-size:44px">{E(l["autor"])}</div><div class="bq" style="font-size:38px">{E(l["donde"])}</div></div>')
            self.T(f"tl.fromTo('#ec{i}',{{x:{200 if i % 2 == 0 else -200},opacity:0,filter:'blur(10px)'}},{{x:0,opacity:1,filter:'blur(0px)',duration:.5,ease:'power4.out'}},{t0 + .3 + i * .35:.2f});")
            if not horiz:
                y += hh + 30
        if any(l.get("derechos") for l in libros):
            ytop = (270 + hmax + 50) if horiz else y + 20
            self.A(f'<div id="ns" class="abs" style="left:{0 if horiz else 80}px;top:{ytop:.0f}px;width:{W if horiz else 920}px;text-align:center"><span style="display:inline-block;background:{LAV};color:{PURD};font-weight:900;font-size:{44 if horiz else 40}px;padding:16px 36px;border-radius:50px;line-height:1.2">Este video no sustituye la lectura del libro.</span></div>')
            self.T(f"tl.fromTo('#ns',{{y:30,opacity:0}},{{y:0,opacity:1,duration:.5,ease:'power3.out'}},{t0 + 1.1:.2f});")

    # ───────── armado
    def construir(self):
        spec, G = self.spec, self.G
        self.tiempos_voz()
        beats = spec["beats"]
        tb, ctxseg = [], []
        for i, b in enumerate(beats):
            anc = b.get("ancla", 0)
            sc = anc.split(":")[0] if isinstance(anc, str) and anc.split(":")[0] in self.seg else None
            if sc is None:
                sc = ctxseg[-1] if ctxseg else spec["segmentos"][0]["nombre"]
            ctxseg.append(sc)
            tb.append(0.0 if i == 0 else self.resolver(anc, b.get("desfase"), None, sc, f"beat {i}"))
        # los beats van en orden de tiempo (si la especificación los lista desordenados, se reordenan)
        orden = [0] + sorted(range(1, len(tb)), key=lambda i: (tb[i], i))
        if orden != list(range(len(tb))):
            self.aviso("los beats no venían en orden de tiempo; los reordené.")
            beats = spec["beats"] = [beats[i] for i in orden]
            tb, ctxseg = [tb[i] for i in orden], [ctxseg[i] for i in orden]
        # separación mínima entre beats: si dos quedan pegados, el segundo se corre (con aviso)
        for i in range(1, len(tb)):
            if tb[i] < tb[i - 1] + 0.7:
                self.aviso(f"beat {i} ({beats[i]['tipo']}) caía a {tb[i] - tb[i - 1]:.2f}s del anterior; lo corrí a +0.7s.")
                tb[i] = tb[i - 1] + 0.7
        cier = spec.get("cierre", {})
        con_cierre = bool(spec["libros"]) and cier is not False
        cier = cier if isinstance(cier, dict) else {}
        if con_cierre:
            t_cierre = (self.resolver(cier["ancla"], cier.get("desfase"), None, None, "cierre") if cier.get("ancla") is not None
                        else self.voice_end + 0.45)
            t_cierre = max(t_cierre, tb[-1] + 1.5)
            TOTAL = round(max(t_cierre + float(cier.get("segundos", 5.0)), self.voice_end + 3.0), 2)
        else:
            t_cierre, TOTAL = None, round(self.voice_end + 0.5, 2)
        if tb[-1] > TOTAL - 0.8:
            raise SystemExit(f"El último beat empieza en {tb[-1]:.2f}s y el video termina en {TOTAL:.2f}s. Revisa las anclas.")
        self.fondo(TOTAL)
        escenas = []
        for i, b in enumerate(beats):
            if b.get("continua") and escenas:
                escenas[-1].append(i)
            else:
                escenas.append([i])
        siguiente = lambda k: tb[escenas[k + 1][0]] if k + 1 < len(escenas) else t_cierre
        for k, idx in enumerate(escenas):
            puerta = beats[idx[-1]].get("salida") == "puerta"
            ultimo = (k + 1 == len(escenas)) and not con_cierre
            s = tb[idx[0]]
            e = TOTAL if ultimo else siguiente(k) + (0.55 if puerta else OV)
            sid = f"b{k}"
            self.escena(sid, s, e, (k + 1) * 10 + (15 if puerta else 0), last=ultimo)
            ctx = dict(fade=[], seg_ctx=None)
            for i in idx:
                b = beats[i]
                ctx["seg_ctx"] = ctxseg[i]
                t1 = tb[i + 1] if i + 1 < len(beats) else TOTAL
                if b.get("panel") and not b.get("continua"):
                    self.panel_inicio(b, tb[i])
                if b.get("continua"):
                    if b.get("panel"):
                        col = COLORES.get(b["panel"], b["panel"])
                        self.T(f"tl.to('#panel',{{backgroundColor:'{col}',duration:.4,ease:'power2.inOut'}},{tb[i]:.2f});")
                    if ctx["fade"]:
                        self.T(f"tl.to({json.dumps(ctx['fade'])},{{opacity:0,duration:.18,ease:'power2.in'}},{tb[i] - .02:.2f});")
                    ctx["fade"] = []
                self.emitir_beat(sid, i, b, tb[i], t1, ctx)
            if puerta:
                self.T(f"tl.to('#{sid}-in',{{clipPath:'inset(0% 0% 0% 100%)',duration:.5,ease:'power3.inOut'}},{siguiente(k) + .05:.2f});")
            self.fin_escena()
        if con_cierre:
            self.escena("bfin", t_cierre, TOTAL, (len(escenas) + 1) * 10, last=True)
            self.cierre(t_cierre)
            self.fin_escena()
        self.subtitulos_y_audio(TOTAL)
        if not self.seco:
            self.escribir(TOTAL)
        return TOTAL, tb

    def fondo(self, TOTAL):
        marca = self.spec.get("marca", "")
        if not self.horiz:
            self.A(f"""<div id="blob1" class="abs" style="left:-230px;top:120px;width:640px;height:640px;border-radius:50%;background:{LAV}"></div>
<div id="blob2" class="abs" style="left:700px;top:820px;width:560px;height:560px;border-radius:50%;background:{LAV};opacity:.7"></div>
<svg class="abs" style="left:0;top:1600px;z-index:2" width="1080" height="320" viewBox="0 0 1080 320"><path d="M0 80 C 180 20, 360 30, 540 80 S 900 140, 1080 60 L1080 320 L0 320 Z" fill="{PUR}"/><path d="M0 170 C 200 120, 380 130, 560 180 S 900 230, 1080 160 L1080 320 L0 320 Z" fill="{PURD}"/></svg>
<div class="abs" style="left:0;top:1780px;width:1080px;text-align:center;z-index:3;font-weight:900;font-size:44px;letter-spacing:.14em;color:{CREAM};text-transform:uppercase">{E(marca)}</div>""")
        else:
            self.A(f"""<div id="blob1" class="abs" style="left:-220px;top:40px;width:640px;height:640px;border-radius:50%;background:{LAV}"></div>
<div id="blob2" class="abs" style="left:1500px;top:380px;width:560px;height:560px;border-radius:50%;background:{LAV};opacity:.7"></div>
<svg class="abs" style="left:0;top:910px;z-index:2" width="1920" height="170" viewBox="0 0 1080 320" preserveAspectRatio="none"><path d="M0 80 C 180 20, 360 30, 540 80 S 900 140, 1080 60 L1080 320 L0 320 Z" fill="{PUR}"/><path d="M0 170 C 200 120, 380 130, 560 180 S 900 230, 1080 160 L1080 320 L0 320 Z" fill="{PURD}"/></svg>
<div class="abs" style="left:0;top:1022px;width:1920px;text-align:center;z-index:3;font-weight:900;font-size:32px;letter-spacing:.14em;color:{CREAM};text-transform:uppercase">{E(marca)}</div>""")
        self.T(f"tl.to('#blob1',{{x:60,y:40,duration:{TOTAL},ease:'sine.inOut'}},0);tl.to('#blob2',{{x:-60,y:-50,duration:{TOTAL},ease:'sine.inOut'}},0);")

    def subtitulos_y_audio(self, TOTAL):
        G, spec = self.G, self.spec
        cp, segs = G["cap"], spec["segmentos"]
        rot = dict(ROTULOS_DEF)
        rot.update(spec.get("etiquetas_voz", {}))
        for s in segs:
            v = s["voz"]
            if rot.get(v):
                s_ = self.seg[s["nombre"]]
                self.A(f'<div id="who_{s["nombre"]}" class="chip clip" data-start="{s_["s"] - .05:.2f}" data-duration="{s_["d"] + .25:.2f}" data-track-index="4" style="left:0;width:{self.W}px;top:{G["who_top"]}px;z-index:20"><span style="background:{ROTULO_COLOR.get(v, PURD)};color:#fff;font-size:34px;padding:8px 28px">{E(rot[v])}</span></div>')
                self.T(f"tl.fromTo('#who_{s['nombre']}',{{opacity:0,y:14}},{{opacity:1,y:0,duration:.25,ease:'power2.out'}},{s_['s'] - .05:.2f});")
        gi = 0
        for s in segs:
            n = s["nombre"]
            gs = groups_of(self.seg[n]["words"], cp["pal"], cp["car"])
            for k, g in enumerate(gs):
                s0 = g[0]["s"] - .05
                e0 = (gs[k + 1][0]["s"] - .03) if k + 1 < len(gs) else min(self.seg[n]["e"] + .15, g[-1]["e"] + .2)
                e0 = max(e0, s0 + .3)
                spans = " ".join(f'<span class="w" id="w{gi}_{j}">{E(w["t"])}</span>' for j, w in enumerate(g))
                self.A(f'<div id="cg{gi}" class="cap clip" data-start="{s0:.2f}" data-duration="{e0 - s0:.2f}" data-track-index="3" style="z-index:30"><div id="cgi{gi}"><p>{spans}</p></div></div>')
                self.T(f"tl.fromTo('#cgi{gi}',{{opacity:0,y:18}},{{opacity:1,y:0,duration:.14,ease:'power2.out'}},{s0:.2f});")
                for j, w in enumerate(g):
                    self.T(f"tl.set('#w{gi}_{j}',{{backgroundColor:'rgba(247,216,74,1)'}},{w['s']:.2f});")
                    nxt = g[j + 1]["s"] if j + 1 < len(g) else w["e"] + .1
                    self.T(f"tl.set('#w{gi}_{j}',{{backgroundColor:'rgba(247,216,74,0)'}},{max(nxt, w['e']):.2f});")
                gi += 1
        for s in segs:
            s_ = self.seg[s["nombre"]]
            self.A(f'<audio id="voz-{s["nombre"]}" src="assets/voz/{s["nombre"]}.mp3" class="clip" data-start="{s_["s"]:.2f}" data-duration="{s_["d"]:.2f}" data-track-index="5" data-volume="1"></audio>')
        pts = [{"t": 0, "v": 0}, {"t": .25, "v": MUS_LO}]
        merged = []
        for s in segs:
            s_, e_ = self.seg[s["nombre"]]["s"], self.seg[s["nombre"]]["e"]
            if merged and s_ - merged[-1][1] < 0.75:
                merged[-1][1] = e_
            else:
                merged.append([s_, e_])
        for s_, e_ in merged:
            pts += [{"t": round(max(.3, s_ - .3), 2), "v": MUS_HI if s_ > 1 else MUS_LO}, {"t": round(s_ - .05, 2), "v": MUS_LO},
                    {"t": round(e_ + .1, 2), "v": MUS_LO}, {"t": round(e_ + .6, 2), "v": MUS_HI}]
        pts += [{"t": round(TOTAL - 2.2, 2), "v": MUS_HI}, {"t": round(TOTAL, 2), "v": 0}]
        pts = [{"t": a, "v": c} for a, c in sorted({(p["t"], p["v"]) for p in pts})]
        auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": pts}]})
        fx = json.dumps({"version": 1, "nodes": [{"type": "peaking", "id": "m1", "params": {"frequency": 1600, "gain": -4, "q": 1}}]})
        self.A(f"<audio id=\"musica\" src=\"assets/musica.mp3\" class=\"clip\" data-start=\"0\" data-duration=\"{TOTAL}\" data-track-index=\"6\" data-volume=\"1\" data-audio-group=\"music\" data-automation='{auto}' data-fx-chain='{fx}'></audio>")

    def css(self):
        W, Hh, cp = self.W, self.Hh, self.G["cap"]
        return f"""
@font-face{{font-family:"Nunito";font-weight:700;src:url("assets/fonts/nunito-700.woff2") format("woff2");}}
@font-face{{font-family:"Nunito";font-weight:800;src:url("assets/fonts/nunito-800.woff2") format("woff2");}}
@font-face{{font-family:"Nunito";font-weight:900;src:url("assets/fonts/nunito-900.woff2") format("woff2");}}
:root{{--navy:{NAVY};--pur:{PUR};--purd:{PURD};--yel:{YEL};--yeld:{YELD};--cream:{CREAM};--lav:{LAV};--ora:{ORA}}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{Hh}px;overflow:hidden;background:var(--cream);font-family:'Nunito',sans-serif;color:var(--navy)}}
#root{{position:relative;width:{W}px;height:{Hh}px;overflow:hidden;background:var(--cream)}}
.abs{{position:absolute}}
.scene{{position:absolute;left:0;top:0;width:{W}px;height:{Hh}px}}
.in{{position:absolute;left:0;top:0;width:{W}px;height:{Hh}px}}
.ctr{{position:absolute;text-align:center;font-weight:900;line-height:1.02;letter-spacing:-.01em}}
.ln{{display:block;white-space:nowrap}}
.kw{{display:inline-block;overflow:hidden;vertical-align:top;padding:.22em .03em .14em;margin:-.2em .09em -.12em}}
.kwi{{display:inline-block;will-change:transform}}
.kl{{display:inline-block}}
.lt{{display:inline-block;white-space:nowrap}}
.navyt{{color:var(--navy)}}
.brush{{position:relative;display:inline-block;padding:0 .18em}}
.brush .bar{{position:absolute;left:0;right:0;top:30%;bottom:0;background:var(--yel);border-radius:.28em;transform-origin:0 50%;z-index:0}}
.brush .tx{{position:relative;z-index:1}}
.brush .tx .kw{{margin:-.2em .09em -.12em}}
.card{{position:absolute;background:#fff;border-radius:34px;box-shadow:0 14px 34px rgba(69,22,121,.17);border-left:20px solid var(--pur);padding:26px 38px}}
.card .bt{{font-weight:900;color:var(--navy);line-height:1.1}} .card .ba{{font-weight:800;color:var(--pur);margin-top:6px}} .card .bq{{font-weight:700;color:#6b5f8f;margin-top:6px}}
.fila{{display:flex;align-items:center;gap:.4em;background:#fff;border-radius:30px;box-shadow:0 10px 26px rgba(69,22,121,.15);padding:.42em .7em .42em .5em;font-weight:800;color:var(--navy);line-height:1.2;border-left:14px solid var(--pur)}}
.fila .ck{{flex:none;display:flex}} .fila .ft{{flex:1}}
.pic{{position:absolute;overflow:hidden;border-radius:44px;box-shadow:0 18px 40px rgba(59,21,128,.22);background:#fff}}
.pic svg{{display:block;width:100%;height:100%}}
.chip{{position:absolute;text-align:center}}
.chip span{{display:inline-block;font-weight:900;letter-spacing:.1em;text-transform:uppercase;border-radius:50px}}
.cap{{position:absolute;left:{cp['left']}px;top:{cp['top']}px;width:{cp['w']}px;height:{cp['h']}px;display:flex;align-items:center;justify-content:center;text-align:center;font-weight:900;font-size:{cp['fs']}px;line-height:1.18;color:var(--navy)}}
.cap p{{width:{cp['w']}px}}
.cap .w{{display:inline-block;padding:0 .08em;border-radius:.26em;background-color:rgba(247,216,74,0)}}
"""

    def escribir(self, TOTAL):
        G, W, Hh = self.G, self.W, self.Hh
        doc = f"""<!doctype html>
<html lang="es" data-resolution="{G['res']}">
<head><meta charset="UTF-8"><meta name="viewport" content="width={W}, height={Hh}">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<title>{E(str(self.spec['id']))}</title><style>{self.css()}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{Hh}">
{chr(10).join(self.H)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(self.TL)}
window.__timelines = window.__timelines || {{}};
window.__timelines['main'] = tl;
</script>
</body></html>
"""
        A = os.path.join(self.proyecto, "assets")
        os.makedirs(os.path.join(A, "fonts"), exist_ok=True)
        for f in ("hyperframes.json", "package.json", "meta.json"):
            shutil.copy(os.path.join(self.base_dir, f), self.proyecto)
        for f in os.listdir(os.path.join(self.assets_dir, "fonts")):
            shutil.copy(os.path.join(self.assets_dir, "fonts", f), os.path.join(A, "fonts", f))
        shutil.copy(os.path.join(self.assets_dir, "musica.mp3"), os.path.join(A, "musica.mp3"))
        open(os.path.join(self.proyecto, "index.html"), "w", encoding="utf-8").write(doc)


def construir(spec, audio_dir, proyecto, carpeta_spec, seco=False):
    """Arma el proyecto HyperFrames. seco=True: sin audio ni archivos; solo valida anclas y maquetación."""
    if not seco:
        os.makedirs(proyecto, exist_ok=True)
    c = Constructor(spec, audio_dir, proyecto, os.path.join(HERE, "base"), os.path.join(HERE, "assets"), carpeta_spec, seco)
    total, tb = c.construir()
    info = {"total": total, "voz_hasta": round(c.voice_end, 2), "beats": [round(x, 2) for x in tb], "avisos": c.avisos,
            "seg": {k: {"s": round(v["s"], 2), "e": round(v["e"], 2), "v": v["v"]} for k, v in c.seg.items()}}
    return info
