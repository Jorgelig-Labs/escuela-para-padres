# -*- coding: utf-8 -*-
# Utilidades para escribir y validar las 36 capsulas. Los guiones viven en lib01.py ... lib12.py
import json, os, re, unicodedata, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # la carpeta de specs de este grupo
# Textos de referencia para verificar citas (locales, no se versionan): borradores/libros-videos/02-series del kit
KIT = os.path.abspath(os.path.join(HERE, *[".."] * 5))
SRC02 = os.environ.get("KIT_TEXTOS_SERIES", os.path.join(KIT, "borradores", "libros-videos", "02-series"))

EGW = "Elena G. de White"
EGW_DONDE = "Descarga gratuita: egwwritings.org"
LIBROS = {
 1: dict(libro_id="el-hogar-cristiano", titulo="El hogar cristiano", autor=EGW, donde=EGW_DONDE, corto="El hogar cristiano", derechos=False),
 2: dict(libro_id="conduccion-del-nino", titulo="Conducción del niño", autor=EGW, donde=EGW_DONDE, corto="Conducción del niño", derechos=False),
 3: dict(libro_id="la-educacion", titulo="La educación", autor=EGW, donde=EGW_DONDE, corto="La educación", derechos=False),
 4: dict(libro_id="mente-caracter-y-personalidad", titulo="Mente, carácter y personalidad", autor=EGW, donde=EGW_DONDE, corto="Mente, carácter y personalidad", derechos=False),
 5: dict(libro_id="los-5-lenguajes-del-amor", titulo="Los 5 lenguajes del amor de los jóvenes", autor="Gary Chapman", donde="Editorial Unilit", corto="Los 5 lenguajes del amor", derechos=True),
 6: dict(libro_id="edad-de-oportunidades", titulo="Edad de oportunidades", autor="Paul David Tripp", donde="P&R Publishing", corto="Edad de oportunidades", derechos=True),
 7: dict(libro_id="limites-con-los-adolescentes", titulo="Límites con los adolescentes", autor="John Townsend", donde="Editorial Vida", corto="Límites con los adolescentes", derechos=True),
 8: dict(libro_id="crianza-llena-de-gracia", titulo="Crianza llena de gracia", autor="Tim Kimmel", donde="Caribe-Betania / Grupo Nelson", corto="Crianza llena de gracia", derechos=True),
 9: dict(libro_id="habla-claro-con-tus-hijos", titulo="Habla claro con tus hijos sobre el sexo", autor="Josh y Dottie McDowell", donde="Editorial Unilit", corto="Habla claro con tus hijos", derechos=True),
 10: dict(libro_id="padres-confiados", titulo="Padres confiados", autor="Jim Burns", donde="Editorial Vida", corto="Padres confiados", derechos=True),
 11: dict(libro_id="manten-encendido-tu-amor", titulo="Mantén encendido tu amor", autor="Danny Silk", donde="Loving on Purpose / Buena Semilla", corto="Mantén encendido tu amor", derechos=True),
 12: dict(libro_id="como-criar-jovenes-de-fe-solida", titulo="Cómo criar jóvenes de fe sólida", autor="Kara Powell y Chap Clark", donde="Editorial Vida", corto="Jóvenes de fe sólida", derechos=True),
}
# Pronunciacion para el generador de voz: lo que aparece en el texto -> como se dice
PRON_BASE = {"egwwritings.org": "E G W writings punto org", "P&R": "P y R"}

NOSUST = "Este video no sustituye la lectura del libro."
VOCES = {"marisol", "rewe", "mario"}
TIPOS = {"titular", "reaccion", "cita", "icono", "ilustracion", "tarjeta_libro", "accion"}
PROHIBIDAS = ["junta", "charla", "reunión", "reunion", "presentación", "presentacion", "denny", "perales", "ponente", "conferencia", "diapositiva"]

CAPS = []  # lista de dicts


def C(libro, ep, tema, segs, beats, fuentes):
    CAPS.append(dict(libro=libro, ep=ep, tema=tema, segs=segs, beats=beats, fuentes=fuentes))


def sin_tag(t):
    return re.sub(r"^\s*\[[^\]]*\]\s*", "", t)


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[^a-z0-9ñ\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


_corpus = None
def corpus():
    global _corpus
    if _corpus is None:
        parts = []
        for f in glob.glob(os.path.join(SRC02, "libros-txt", "*.txt")) + [os.path.join(HERE, "fuentes", "tripp.txt"), os.path.join(HERE, "fuentes", "verificadas.txt")]:
            if os.path.exists(f):
                parts.append(open(f, encoding="utf-8", errors="ignore").read())
        _corpus = [norm(p) for p in parts]
    return _corpus


def voz_texto(c):
    return " ".join(sin_tag(s[2]) for s in c["segs"])


def nchars(c):
    return sum(len(sin_tag(s[2])) for s in c["segs"])


def nwords(t):
    return len(re.findall(r"\S+", t))


def cap_id(c):
    return "serie-%s-%dde3" % (LIBROS[c["libro"]]["libro_id"], c["ep"])


def a_spec(c):
    L = LIBROS[c["libro"]]
    d = {
     "id": cap_id(c), "formato": "vertical", "libro_id": L["libro_id"], "serie": L["libro_id"],
     "episodio": c["ep"], "de": 3,
     "titulo": L["titulo"], "autor": L["autor"], "donde": L["donde"], "derechos": L["derechos"],
     "titulo_corto": L["corto"], "etiqueta": "%s · %d/3" % (L["corto"], c["ep"]), "tema": c["tema"],
     "segmentos": [list(s) for s in c["segs"]],
     "beats": [dict(tipo=b[0], seg=b[1], palabra=b[2], texto=b[3], visual=b[4]) for b in c["beats"]],
     "fuentes": c["fuentes"],
    }
    pron = {k: v for k, v in PRON_BASE.items() if k in voz_texto(c)}
    if pron:
        d["pronunciacion"] = pron
    return d


def validar(c, verbose=True):
    errs = []
    L = LIBROS[c["libro"]]
    nm = [s[0] for s in c["segs"]]
    if len(set(nm)) != len(nm):
        errs.append("segmentos repetidos")
    for s in c["segs"]:
        if s[1] not in VOCES: errs.append("voz invalida " + s[1])
        if not re.match(r"^\s*\[[^\]]+\]\s*\S", s[2]): errs.append("sin etiqueta de tono en " + s[0])
    vt = voz_texto(c)
    n = nwords(vt)
    if n < 140 or n > 190: errs.append("palabras fuera de 140-190: %d" % n)
    low = norm(vt + " " + " ".join(b[3] + " " + b[4] for b in c["beats"]) + " " + c["tema"])
    for p in PROHIDAS_N:
        if re.search(r"\b" + p + r"\b", low): errs.append("palabra prohibida: " + p)
    if "voz con comillas inconsistentes" and vt.count("«") != vt.count("»"): errs.append("comillas")
    # citas
    for q in re.findall(r"«([^»]+)»", vt):
        w = nwords(q)
        if w > 25: errs.append("cita >25 palabras (%d): %s" % (w, q[:40]))
        nq = norm(q)
        if not any(nq in cp for cp in corpus()):
            errs.append("cita NO hallada en fuentes: " + q)
    # beats
    segtxt = {s[0]: norm(sin_tag(s[2])) for s in c["segs"]}
    for b in c["beats"]:
        if b[0] not in TIPOS: errs.append("tipo beat invalido " + b[0])
        if b[1] not in segtxt: errs.append("beat con seg inexistente " + b[1]); continue
        if norm(b[2]) not in segtxt[b[1]]: errs.append("palabra ancla '%s' no esta en seg %s" % (b[2], b[1]))
        for k in (3, 4):
            if not b[k].strip(): errs.append("beat vacio")
    # cierre
    last = c["segs"][-1]
    if c["ep"] in (1, 2):
        if not sin_tag(last[2]).startswith("Siguiente:"): errs.append("falta Siguiente:")
    else:
        if c["beats"][-1][0] != "tarjeta_libro": errs.append("el ultimo beat debe ser tarjeta_libro")
        if L["derechos"] and NOSUST not in last[2]: errs.append("falta frase de no sustituir")
    if sum(1 for b in c["beats"] if b[0] == "accion") != 1: errs.append("debe haber exactamente 1 beat accion")
    if nwords(sin_tag(c["segs"][0][2])) > 14: errs.append("gancho largo (>14 palabras)")
    if not c["segs"][-2][0].startswith("accion"): errs.append("el penultimo segmento debe ser 'accion'")
    if c["libro"] == 11 and c["ep"] == 1 and "relaciones en general" not in vt: errs.append("libro 11: falta decir que es de relaciones en general")
    if c["libro"] == 11 and c["ep"] == 3 and "relaciones en general" not in last[2]: errs.append("libro 11 3/3: tarjeta debe decir relaciones en general")
    return n, errs

PROHIDAS_N = [norm(p) for p in PROHIBIDAS]


def cargar():
    for f in sorted(glob.glob(os.path.join(HERE, "lib[0-9][0-9].py"))):
        exec(compile(open(f, encoding="utf-8").read(), f, "exec"), {"C": C, "EGW": EGW})


def main(escribir=False):
    cargar()
    total_chars = 0
    tot_err = 0
    for c in CAPS:
        n, errs = validar(c)
        chars = nchars(c)
        total_chars += chars
        marca = "OK " if not errs else "ERR"
        print("%s %02d-%d  %3d pal  %4d car  beats=%d  %s" % (marca, c["libro"], c["ep"], n, chars, len(c["beats"]), c["tema"]))
        for e in errs:
            print("      -", e); tot_err += 1
        if escribir and not errs:
            L = LIBROS[c["libro"]]
            fn = "%02d-%s-%dde3.json" % (c["libro"], L["libro_id"], c["ep"])
            with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
                json.dump(a_spec(c), f, ensure_ascii=False, indent=1)
    print("capsulas:", len(CAPS), "| caracteres de voz:", total_chars, "| errores:", tot_err)

if __name__ == "__main__":
    main(escribir="--write" in sys.argv)
