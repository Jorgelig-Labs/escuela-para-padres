# -*- coding: utf-8 -*-
# Ilustraciones vectoriales de la serie "Entre nosotros" (mismo estilo: plano, redondeado, sin rostros).
# Paleta: crema/amarillo cálido, morado, navy. Cada función devuelve un <svg> listo para incrustar.
NAVY, PUR, PURD, PURL, YEL, YELD, CREAM, LAV, ORA = "#1B1740", "#5B3FB0", "#3B1580", "#7A5AD8", "#F7D84A", "#F5C518", "#FFF6DC", "#EFE6FA", "#F08A1C"

def teen_room(i="a"):
    """Adolescente de espaldas en su cuarto, audífonos, puerta cerrada, lámpara cálida."""
    return f'''<svg viewBox="0 0 880 540" width="880" height="540" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="glow{i}" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{YEL}" stop-opacity=".75"/><stop offset="1" stop-color="{YEL}" stop-opacity="0"/></radialGradient></defs>
<rect width="880" height="540" fill="#FFE9A9"/>
<rect y="410" width="880" height="130" fill="{PURD}"/>
<circle cx="120" cy="285" r="190" fill="url(#glow{i})"/>
<rect x="640" y="40" width="190" height="372" rx="10" fill="#2A2160"/>
<rect x="662" y="64" width="146" height="150" rx="8" fill="none" stroke="#3B3085" stroke-width="6"/>
<rect x="662" y="236" width="146" height="152" rx="8" fill="none" stroke="#3B3085" stroke-width="6"/>
<circle cx="668" cy="232" r="9" fill="{YELD}"/>
<rect x="215" y="58" width="76" height="100" rx="8" fill="{PUR}"/><circle cx="253" cy="96" r="16" fill="{YEL}"/><rect x="226" y="124" width="54" height="8" rx="4" fill="{LAV}"/>
<rect x="318" y="92" width="64" height="84" rx="8" fill="{NAVY}"/><path d="M350 112 l7 15 16 2 -12 11 3 16 -14 -8 -14 8 3 -16 -12 -11 16 -2z" fill="{YEL}"/>
<rect x="52" y="338" width="130" height="86" rx="10" fill="{PUR}"/>
<rect x="104" y="296" width="26" height="44" rx="6" fill="{NAVY}"/><path d="M78 296 L156 296 L140 238 L94 238 Z" fill="{YELD}"/>
<rect x="160" y="340" width="540" height="120" rx="34" fill="{PUR}"/>
<path d="M430 372 C 500 352 560 392 700 366 L700 460 L430 460 Z" fill="{YELD}"/>
<rect x="184" y="316" width="120" height="52" rx="26" fill="{LAV}"/>
<ellipse cx="380" cy="372" rx="96" ry="30" fill="{PURD}"/>
<rect x="326" y="228" width="108" height="150" rx="52" fill="{PURL}"/>
<circle cx="380" cy="208" r="46" fill="{NAVY}"/>
<path d="M334 210 C 334 150 426 150 426 210" fill="none" stroke="{YELD}" stroke-width="11" stroke-linecap="round"/>
<rect x="322" y="196" width="19" height="40" rx="9" fill="{YELD}"/><rect x="419" y="196" width="19" height="40" rx="9" fill="{YELD}"/>
</svg>'''

def table_mugs(i="b"):
    """Mesa de cocina de noche con dos tazas y dos sillas vacías: invitación a platicar."""
    return f'''<svg viewBox="0 0 880 540" width="880" height="540" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="glow{i}" cx="50%" cy="30%" r="60%"><stop offset="0" stop-color="{YEL}" stop-opacity=".8"/><stop offset="1" stop-color="{YEL}" stop-opacity="0"/></radialGradient></defs>
<rect width="880" height="540" fill="{NAVY}"/>
<rect x="590" y="60" width="200" height="190" rx="14" fill="#2A2160"/><circle cx="700" cy="130" r="28" fill="{YEL}"/><circle cx="672" cy="122" r="26" fill="#2A2160"/>
<circle cx="630" cy="90" r="4" fill="{LAV}"/><circle cx="745" cy="200" r="4" fill="{LAV}"/><circle cx="620" cy="190" r="3" fill="{LAV}"/>
<rect x="590" y="154" width="200" height="8" fill="{NAVY}" opacity=".5"/><rect x="688" y="60" width="8" height="190" fill="{NAVY}" opacity=".5"/>
<rect x="436" y="0" width="8" height="120" fill="{YELD}"/>
<path d="M440 120 L520 120 L560 540 L320 540 L360 120 Z" fill="url(#glow{i})"/>
<path d="M392 128 C 392 90 488 90 488 128 Z" fill="{YELD}" transform="translate(0 0)"/>
<rect x="150" y="370" width="580" height="26" rx="12" fill="{PUR}"/>
<rect x="190" y="396" width="26" height="144" rx="8" fill="{PURD}"/><rect x="664" y="396" width="26" height="144" rx="8" fill="{PURD}"/>
<rect x="40" y="300" width="64" height="130" rx="22" fill="{PURD}"/><rect x="40" y="410" width="120" height="26" rx="12" fill="{PURD}"/><rect x="60" y="436" width="18" height="104" rx="6" fill="{PURD}"/>
<rect x="776" y="300" width="64" height="130" rx="22" fill="{PURD}"/><rect x="720" y="410" width="120" height="26" rx="12" fill="{PURD}"/><rect x="802" y="436" width="18" height="104" rx="6" fill="{PURD}"/>
<g><rect x="290" y="316" width="86" height="58" rx="16" fill="{CREAM}"/><path d="M376 330 C 410 330 410 362 376 362" fill="none" stroke="{CREAM}" stroke-width="10"/><rect x="290" y="316" width="86" height="14" rx="7" fill="{YEL}"/></g>
<g><rect x="504" y="316" width="86" height="58" rx="16" fill="{CREAM}"/><path d="M504 330 C 470 330 470 362 504 362" fill="none" stroke="{CREAM}" stroke-width="10"/><rect x="504" y="316" width="86" height="14" rx="7" fill="{YEL}"/></g>
<path d="M322 300 C 306 278 338 270 322 246 M352 300 C 336 278 368 270 352 246" fill="none" stroke="{LAV}" stroke-width="6" stroke-linecap="round" opacity=".7"/>
<path d="M536 300 C 520 278 552 270 536 246 M566 300 C 550 278 582 270 566 246" fill="none" stroke="{LAV}" stroke-width="6" stroke-linecap="round" opacity=".7"/>
</svg>'''

def sofa_sunset(i="c"):
    """Papá y adolescente de espaldas en el sillón, mirando un atardecer: cercanía."""
    return f'''<svg viewBox="0 0 880 540" width="880" height="540" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="sky{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{YEL}"/><stop offset="1" stop-color="{ORA}"/></linearGradient></defs>
<rect width="880" height="540" fill="{LAV}"/>
<rect x="150" y="50" width="580" height="330" rx="22" fill="url(#sky{i})"/>
<circle cx="440" cy="270" r="74" fill="#FFF6DC"/>
<path d="M150 330 C 260 270 340 330 440 300 S 640 270 730 320 L730 380 L150 380 Z" fill="{PUR}"/>
<path d="M150 360 C 280 320 380 370 500 340 S 660 330 730 352 L730 380 L150 380 Z" fill="{PURD}"/>
<rect x="436" y="50" width="8" height="330" fill="{LAV}" opacity=".85"/><rect x="150" y="212" width="580" height="8" fill="{LAV}" opacity=".85"/>
<rect x="150" y="50" width="580" height="330" rx="22" fill="none" stroke="{LAV}" stroke-width="14"/>
<rect x="0" y="470" width="880" height="70" fill="{PURD}"/>
<rect x="120" y="318" width="640" height="196" rx="60" fill="{PUR}"/>
<rect x="150" y="300" width="580" height="120" rx="44" fill="{PURL}"/>
<rect x="104" y="360" width="86" height="150" rx="40" fill="{PUR}"/><rect x="690" y="360" width="86" height="150" rx="40" fill="{PUR}"/>
<rect x="268" y="236" width="130" height="190" rx="62" fill="{NAVY}"/>
<circle cx="333" cy="206" r="54" fill="{NAVY}"/><path d="M290 214 C 292 160 376 160 378 214 C 360 196 310 196 290 214Z" fill="#2A2160"/>
<rect x="418" y="288" width="104" height="140" rx="50" fill="{YELD}"/>
<circle cx="470" cy="262" r="42" fill="#2A2160"/>
<path d="M378 292 C 410 276 450 290 486 300 L 486 338 C 440 330 408 336 378 336 Z" fill="{NAVY}"/>
</svg>'''

def icon_lock(sz=300):
    return f'''<svg width="{sz}" height="{sz}" viewBox="0 0 200 200"><path d="M62 92 L62 66 C62 34 138 34 138 66 L138 92" fill="none" stroke="{PUR}" stroke-width="20" stroke-linecap="round"/><rect x="38" y="86" width="124" height="96" rx="26" fill="{YELD}"/><circle cx="100" cy="128" r="14" fill="{NAVY}"/><rect x="94" y="132" width="12" height="28" rx="6" fill="{NAVY}"/></svg>'''

def icon_shield(w=560):
    h = int(w * 1.14)
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 200 228"><path d="M100 8 L184 38 L184 112 C184 164 148 198 100 220 C52 198 16 164 16 112 L16 38 Z" fill="{PUR}"/><path d="M100 24 L168 48 L168 112 C168 154 140 182 100 202 Z" fill="{PURL}" opacity=".55"/><path d="M100 8 L184 38 L184 112 C184 164 148 198 100 220 C52 198 16 164 16 112 L16 38 Z" fill="none" stroke="{YELD}" stroke-width="8" stroke-linejoin="round"/></svg>'''

def icon_check(sz=120):
    return f'''<svg width="{sz}" height="{sz}" viewBox="0 0 160 160"><circle cx="80" cy="80" r="80" fill="{PUR}"/><path d="M42 84 L70 112 L120 52" fill="none" stroke="{YEL}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></svg>'''

def door_scene():
    """Puerta entreabierta con luz; la hoja se cierra con scaleX (id door-leaf, anclada a la izquierda)."""
    return f'''<svg width="560" height="780" viewBox="0 0 560 780" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="dl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{YEL}"/><stop offset="1" stop-color="{ORA}"/></linearGradient></defs>
<rect x="0" y="0" width="560" height="780" rx="30" fill="{NAVY}"/>
<rect x="30" y="30" width="500" height="720" rx="14" fill="url(#dl)" id="door-light"/>
<g id="door-leaf"><rect x="30" y="30" width="500" height="720" rx="14" fill="#2A2160"/>
<rect x="76" y="76" width="408" height="270" rx="14" fill="none" stroke="#3B3085" stroke-width="10"/>
<rect x="76" y="398" width="408" height="300" rx="14" fill="none" stroke="#3B3085" stroke-width="10"/>
<circle cx="470" cy="392" r="20" fill="{YELD}"/></g>
</svg>'''


# ───────────────────────── íconos extra (viewBox propio, se escalan por ancho) ─────────────────────────
def _icon(inner, vw, vh, w):
    h = round(w * vh / vw)
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {vw} {vh}" xmlns="http://www.w3.org/2000/svg">{inner}</svg>'

_HEART = "M50 88 C 10 58 0 36 0 24 C0 10 12 0 26 0 C 36 0 46 6 50 14 C 54 6 64 0 74 0 C 88 0 100 10 100 24 C 100 36 90 58 50 88 Z"

def icon_heart(w=420, fill="#E6D6FB"):
    return _icon(f'<path d="{_HEART}" fill="{fill}"/>', 100, 90, w)

def icon_heart_solid(w=420):
    return _icon(f'<path d="{_HEART}" fill="{PUR}"/><path d="M14 22 C 14 14 22 10 30 10" fill="none" stroke="{YEL}" stroke-width="6" stroke-linecap="round"/>', 100, 90, w)

def icon_book(w=420):
    return _icon(f'<path d="M100 40 C 70 18 36 18 12 28 L12 150 C 36 140 70 140 100 162 Z" fill="{PUR}"/><path d="M100 40 C 130 18 164 18 188 28 L188 150 C 164 140 130 140 100 162 Z" fill="{PURL}"/><path d="M100 54 C 74 38 44 38 26 44 L26 140 C 44 134 74 134 100 150 Z" fill="{CREAM}"/><path d="M100 54 C 126 38 156 38 174 44 L174 140 C 156 134 126 134 100 150 Z" fill="#fff"/><rect x="40" y="62" width="44" height="8" rx="4" fill="{LAV}"/><rect x="40" y="82" width="38" height="8" rx="4" fill="{LAV}"/><rect x="116" y="62" width="44" height="8" rx="4" fill="{LAV}"/><rect x="116" y="82" width="38" height="8" rx="4" fill="{LAV}"/><path d="M92 150 L92 188 L100 180 L108 188 L108 150 Z" fill="{YELD}"/>', 200, 200, w)

def icon_bulb(w=420):
    return _icon(f'<circle cx="100" cy="82" r="62" fill="{YEL}"/><path d="M70 62 C 78 46 98 40 112 44" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity=".8"/><rect x="70" y="136" width="60" height="26" rx="10" fill="{PUR}"/><rect x="78" y="164" width="44" height="18" rx="9" fill="{NAVY}"/><path d="M100 4 L100 -6 M20 82 L8 82 M192 82 L180 82" stroke="{YELD}" stroke-width="8" stroke-linecap="round"/>', 200, 190, w)

def icon_clock(w=420):
    return _icon(f'<circle cx="100" cy="100" r="86" fill="{CREAM}" stroke="{PUR}" stroke-width="18"/><path d="M100 50 L100 102 L136 122" fill="none" stroke="{NAVY}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/><circle cx="100" cy="100" r="9" fill="{YELD}"/>', 200, 200, w)

def icon_chat(w=420):
    return _icon(f'<path d="M30 20 L170 20 Q 192 20 192 42 L192 118 Q 192 140 170 140 L96 140 L58 176 L62 140 L30 140 Q 8 140 8 118 L8 42 Q 8 20 30 20 Z" fill="{PUR}"/><circle cx="62" cy="80" r="12" fill="{YEL}"/><circle cx="100" cy="80" r="12" fill="{YEL}"/><circle cx="138" cy="80" r="12" fill="{YEL}"/>', 200, 190, w)

def icon_star(w=420):
    return _icon(f'<path d="M100 10 L124 70 L190 76 L140 118 L156 184 L100 148 L44 184 L60 118 L10 76 L76 70 Z" fill="{YEL}" stroke="{YELD}" stroke-width="8" stroke-linejoin="round"/>', 200, 194, w)

def icon_ear(w=420):
    return _icon(f'<path d="M60 150 C 30 120 30 60 76 40 C 124 22 168 54 160 100 C 156 124 128 128 124 152 C 120 180 84 186 60 150 Z" fill="{PUR}"/><path d="M84 96 C 84 76 120 70 126 92 C 130 108 108 112 106 128" fill="none" stroke="{YEL}" stroke-width="12" stroke-linecap="round"/>', 200, 200, w)

# ───────────────────────── ilustraciones nuevas (880x540, planas, sin rostros) ─────────────────────────
def desk_book(i="d"):
    """Escritorio cálido con lámpara, libro abierto y taza: lectura tranquila."""
    return f'''<svg viewBox="0 0 880 540" width="880" height="540" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="glow{i}" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{YEL}" stop-opacity=".8"/><stop offset="1" stop-color="{YEL}" stop-opacity="0"/></radialGradient></defs>
<rect width="880" height="540" fill="#FFE9A9"/>
<circle cx="190" cy="250" r="210" fill="url(#glow{i})"/>
<rect x="560" y="50" width="250" height="210" rx="12" fill="{LAV}"/><rect x="574" y="64" width="222" height="182" rx="6" fill="#CFE3FF"/><rect x="680" y="64" width="10" height="182" fill="{LAV}"/><rect x="574" y="148" width="222" height="10" fill="{LAV}"/>
<circle cx="740" cy="110" r="26" fill="{YEL}"/>
<rect x="0" y="400" width="880" height="140" fill="{PURD}"/>
<rect x="60" y="388" width="760" height="30" rx="14" fill="{PUR}"/>
<rect x="120" y="330" width="22" height="60" rx="6" fill="{NAVY}"/><path d="M84 330 L178 330 L158 250 L104 250 Z" fill="{YELD}"/><rect x="100" y="388" width="62" height="14" rx="7" fill="{NAVY}"/>
<path d="M300 380 C 340 346 400 346 440 366 C 480 346 540 346 580 380 L 580 388 L 300 388 Z" fill="{PURL}"/>
<path d="M440 366 C 400 330 340 326 296 346 L296 382 C 340 362 400 366 440 388 Z" fill="#fff"/>
<path d="M440 366 C 480 330 540 326 584 346 L584 382 C 540 362 480 366 440 388 Z" fill="{CREAM}"/>
<rect x="326" y="352" width="86" height="7" rx="3" fill="{LAV}"/><rect x="326" y="368" width="72" height="7" rx="3" fill="{LAV}"/><rect x="468" y="352" width="86" height="7" rx="3" fill="{LAV}"/><rect x="468" y="368" width="72" height="7" rx="3" fill="{LAV}"/>
<g><rect x="660" y="334" width="80" height="56" rx="16" fill="{CREAM}"/><path d="M740 346 C 772 346 772 378 740 378" fill="none" stroke="{CREAM}" stroke-width="10"/><rect x="660" y="334" width="80" height="14" rx="7" fill="{YEL}"/></g>
<path d="M684 318 C 668 296 700 288 684 266 M712 318 C 696 296 728 288 712 266" fill="none" stroke="{PURL}" stroke-width="6" stroke-linecap="round" opacity=".6"/>
</svg>'''

def road_sunrise(i="e"):
    """Camino que sube hacia un amanecer: un paso a la vez."""
    return f'''<svg viewBox="0 0 880 540" width="880" height="540" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="sky{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{LAV}"/><stop offset=".55" stop-color="{YEL}"/><stop offset="1" stop-color="{ORA}"/></linearGradient></defs>
<rect width="880" height="540" fill="url(#sky{i})"/>
<circle cx="440" cy="268" r="92" fill="#FFF6DC"/>
<circle cx="440" cy="268" r="130" fill="#FFF6DC" opacity=".35"/>
<path d="M0 330 C 120 270 240 300 360 318 L 360 540 L 0 540 Z" fill="{PUR}"/>
<path d="M880 320 C 760 262 640 296 520 316 L 520 540 L 880 540 Z" fill="{PUR}"/>
<path d="M0 400 C 140 350 260 380 380 392 L 380 540 L 0 540 Z" fill="{PURD}"/>
<path d="M880 392 C 740 344 620 376 500 390 L 500 540 L 880 540 Z" fill="{PURD}"/>
<path d="M400 318 L 480 318 L 640 540 L 240 540 Z" fill="#FFE9A9"/>
<path d="M440 330 L 440 350 M440 372 L 440 400 M440 428 L 440 468 M440 496 L 440 540" stroke="{ORA}" stroke-width="10" stroke-linecap="round"/>
<rect x="676" y="236" width="12" height="130" rx="5" fill="{NAVY}"/><path d="M688 244 L 770 244 L 788 262 L 770 280 L 688 280 Z" fill="{NAVY}"/>
</svg>'''

# ───────────────────────── más íconos (planos, redondeados) ─────────────────────────
def icon_lupa(w=420):
    return _icon(f'<circle cx="84" cy="84" r="58" fill="{LAV}" stroke="{PUR}" stroke-width="18"/><path d="M60 64 C 66 52 80 46 92 48" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/><path d="M126 126 L180 180" stroke="{NAVY}" stroke-width="22" stroke-linecap="round"/>', 200, 200, w)

def icon_paraguas(w=420):
    return _icon(f'<path d="M12 100 C 12 44 56 12 100 12 C 144 12 188 44 188 100 C 170 88 150 88 134 100 C 120 88 108 88 100 100 C 92 88 80 88 66 100 C 50 88 30 88 12 100 Z" fill="{PUR}"/><path d="M100 12 C 80 40 80 80 100 100 C 120 80 120 40 100 12 Z" fill="{PURL}"/><path d="M100 100 L100 164 C 100 184 70 184 70 164" fill="none" stroke="{NAVY}" stroke-width="12" stroke-linecap="round"/>', 200, 190, w)

def icon_llama(w=420):
    return _icon(f'<path d="M100 8 C 120 50 164 70 164 122 C 164 160 134 188 100 188 C 66 188 36 160 36 122 C 36 90 56 74 66 52 C 78 66 80 78 84 86 C 94 62 94 34 100 8 Z" fill="{ORA}"/><path d="M100 80 C 112 104 136 114 136 138 C 136 158 120 172 100 172 C 80 172 64 158 64 138 C 64 120 78 112 86 96 C 92 104 94 108 96 112 C 100 100 100 92 100 80 Z" fill="{YEL}"/>', 200, 196, w)

def icon_casa(w=420):
    return _icon(f'<path d="M100 14 L190 92 L170 92 L170 180 L30 180 L30 92 L10 92 Z" fill="{PUR}"/><rect x="82" y="116" width="36" height="64" rx="8" fill="{YEL}"/><rect x="132" y="104" width="22" height="22" rx="5" fill="{LAV}"/><rect x="46" y="104" width="22" height="22" rx="5" fill="{LAV}"/><path d="M100 14 L190 92 L10 92 Z" fill="{PURD}"/>', 200, 190, w)

def icon_brujula(w=420):
    return _icon(f'<circle cx="100" cy="100" r="88" fill="{CREAM}" stroke="{PUR}" stroke-width="16"/><path d="M100 36 L124 100 L100 164 L76 100 Z" fill="{LAV}"/><path d="M100 36 L124 100 L76 100 Z" fill="{ORA}"/><circle cx="100" cy="100" r="9" fill="{NAVY}"/>', 200, 200, w)

def icon_sol(w=420):
    rays = "".join(f'<rect x="94" y="6" width="12" height="34" rx="6" fill="{YELD}" transform="rotate({a} 100 100)"/>' for a in range(0, 360, 45))
    return _icon(f'{rays}<circle cx="100" cy="100" r="46" fill="{YEL}"/>', 200, 200, w)

def icon_nube(w=420):
    return _icon(f'<path d="M50 150 C 20 150 12 110 44 102 C 40 66 84 50 106 76 C 124 50 170 66 164 104 C 196 104 196 150 160 150 Z" fill="{PURL}"/><path d="M60 124 C 70 112 84 110 92 116" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round" opacity=".5"/>', 200, 170, w)

def icon_timon(w=420):
    spokes = "".join(f'<rect x="94" y="14" width="12" height="62" rx="6" fill="{NAVY}" transform="rotate({a} 100 100)"/>' for a in range(0, 360, 60))
    return _icon(f'{spokes}<circle cx="100" cy="100" r="62" fill="none" stroke="{PUR}" stroke-width="16"/><circle cx="100" cy="100" r="18" fill="{YELD}"/>', 200, 200, w)

def icon_corona(w=420):
    return _icon(f'<path d="M20 150 L8 54 L58 98 L100 28 L142 98 L192 54 L180 150 Z" fill="{YEL}" stroke="{YELD}" stroke-width="8" stroke-linejoin="round"/><rect x="20" y="150" width="160" height="22" rx="8" fill="{YELD}"/><circle cx="8" cy="54" r="9" fill="{ORA}"/><circle cx="100" cy="28" r="9" fill="{ORA}"/><circle cx="192" cy="54" r="9" fill="{ORA}"/>', 200, 180, w)

def icon_pregunta(w=420):
    return _icon(f'<circle cx="100" cy="100" r="92" fill="{PUR}"/><path d="M68 78 C 68 40 132 40 132 78 C 132 104 100 106 100 130" fill="none" stroke="{YEL}" stroke-width="20" stroke-linecap="round"/><circle cx="100" cy="162" r="12" fill="{YEL}"/>', 200, 200, w)

def icon_puerta(w=420):
    return _icon(f'<rect x="38" y="12" width="124" height="176" rx="12" fill="{NAVY}"/><rect x="52" y="26" width="96" height="70" rx="8" fill="none" stroke="#3B3085" stroke-width="6"/><rect x="52" y="108" width="96" height="66" rx="8" fill="none" stroke="#3B3085" stroke-width="6"/><circle cx="138" cy="102" r="8" fill="{YELD}"/>', 200, 200, w)

def icon_celular(w=420):
    return _icon(f'<rect x="52" y="8" width="96" height="184" rx="22" fill="{NAVY}"/><rect x="62" y="30" width="76" height="130" rx="8" fill="{LAV}"/><circle cx="100" cy="176" r="7" fill="{YELD}"/><rect x="76" y="58" width="48" height="10" rx="5" fill="{PUR}"/><rect x="76" y="80" width="36" height="10" rx="5" fill="{PURL}"/>', 200, 200, w)

def icon_balanza(w=420):
    return _icon(f'<rect x="94" y="20" width="12" height="150" rx="6" fill="{NAVY}"/><rect x="50" y="170" width="100" height="14" rx="7" fill="{NAVY}"/><path d="M26 56 L174 44" stroke="{NAVY}" stroke-width="10" stroke-linecap="round"/><path d="M8 110 L44 58 L80 110 Z M8 110 C 8 134 80 134 80 110 Z" fill="{YEL}"/><path d="M120 100 L156 48 L192 100 Z M120 100 C 120 124 192 124 192 100 Z" fill="{PUR}"/>', 200, 192, w)

def icon_libreta(w=420):
    return _icon(f'<rect x="34" y="14" width="124" height="172" rx="14" fill="{PUR}"/><rect x="48" y="14" width="110" height="172" rx="12" fill="{CREAM}"/><rect x="62" y="48" width="78" height="9" rx="4" fill="{LAV}"/><rect x="62" y="72" width="62" height="9" rx="4" fill="{LAV}"/><rect x="62" y="96" width="70" height="9" rx="4" fill="{LAV}"/><path d="M150 150 L186 62 L202 70 L166 158 L148 164 Z" fill="{YELD}" transform="translate(-10 0)"/><path d="M148 164 L152 150 L166 158 Z" fill="{NAVY}" transform="translate(-10 0)"/>', 200, 200, w)

def icon_regalo(w=420):
    return _icon(f'<rect x="24" y="80" width="152" height="104" rx="12" fill="{PUR}"/><rect x="14" y="56" width="172" height="36" rx="10" fill="{PURL}"/><rect x="88" y="56" width="24" height="128" fill="{YEL}"/><path d="M100 56 C 70 56 50 20 76 16 C 96 14 100 40 100 56 C 100 40 104 14 124 16 C 150 20 130 56 100 56 Z" fill="none" stroke="{YEL}" stroke-width="12" stroke-linejoin="round"/>', 200, 190, w)

def icon_mochila(w=420):
    return _icon(f'<path d="M74 40 C 74 14 126 14 126 40" fill="none" stroke="{NAVY}" stroke-width="14" stroke-linecap="round"/><rect x="36" y="36" width="128" height="152" rx="44" fill="{PUR}"/><rect x="62" y="104" width="76" height="56" rx="16" fill="{PURL}"/><rect x="62" y="120" width="76" height="8" fill="{PURD}"/><circle cx="100" cy="124" r="7" fill="{YEL}"/>', 200, 200, w)

def icon_globo(w=420):
    return _icon(f'<ellipse cx="100" cy="82" rx="62" ry="72" fill="{ORA}"/><path d="M92 150 L108 150 L100 162 Z" fill="{ORA}"/><path d="M100 162 C 88 178 112 184 100 198" fill="none" stroke="{NAVY}" stroke-width="6" stroke-linecap="round"/><path d="M62 52 C 68 40 80 32 92 30" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity=".7"/>', 200, 200, w)

def icon_mano(w=420):
    return _icon(f'<path d="M30 120 L30 70 C30 56 52 56 52 70 L52 40 C52 26 74 26 74 40 L74 32 C74 18 96 18 96 32 L96 44 C96 30 118 30 118 44 L118 100 L132 84 C142 74 158 84 150 98 C 140 128 128 170 90 176 C 60 180 34 156 30 120 Z" fill="{YEL}" stroke="{YELD}" stroke-width="8" stroke-linejoin="round"/>', 200, 200, w)

def icon_pausa(w=420):
    return _icon(f'<circle cx="100" cy="100" r="92" fill="{PUR}"/><rect x="62" y="58" width="26" height="84" rx="9" fill="{YEL}"/><rect x="112" y="58" width="26" height="84" rx="9" fill="{YEL}"/>', 200, 200, w)

def icon_flecha(w=420):
    return _icon(f'<circle cx="100" cy="100" r="92" fill="{PUR}"/><path d="M52 100 L140 100 M104 62 L142 100 L104 138" fill="none" stroke="{YEL}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>', 200, 200, w)

# ───────────────────────── registros para la especificación ─────────────────────────
ICONOS = {  # nombre -> (función(ancho) -> svg, relación alto/ancho, ancho por omisión con / sin círculo)
    "candado": (icon_lock, 1.0), "escudo": (icon_shield, 1.14), "check": (icon_check, 1.0),
    "corazon": (icon_heart_solid, 0.9), "corazon_fondo": (icon_heart, 0.9), "libro": (icon_book, 1.0),
    "bombilla": (icon_bulb, 0.95), "reloj": (icon_clock, 1.0), "chat": (icon_chat, 0.95),
    "estrella": (icon_star, 0.97), "oido": (icon_ear, 1.0),
}
ILUSTRACIONES = {  # nombre -> (función(id_único) -> svg, ancho, alto del viewBox)
    "cuarto_adolescente": (teen_room, 880, 540), "mesa_tazas": (table_mugs, 880, 540),
    "sillon_atardecer": (sofa_sunset, 880, 540), "puerta": (lambda i="": door_scene(), 560, 780),
    "escritorio_libro": (desk_book, 880, 540), "camino_amanecer": (road_sunrise, 880, 540),
}
ICONOS.update({
    "lupa": (icon_lupa, 1.0), "paraguas": (icon_paraguas, 0.95), "llama": (icon_llama, 0.98), "casa": (icon_casa, 0.95),
    "brujula": (icon_brujula, 1.0), "sol": (icon_sol, 1.0), "nube": (icon_nube, 0.85), "timon": (icon_timon, 1.0),
    "corona": (icon_corona, 0.9), "pregunta": (icon_pregunta, 1.0), "puerta_icono": (icon_puerta, 1.0),
    "celular": (icon_celular, 1.0), "balanza": (icon_balanza, 0.96), "libreta": (icon_libreta, 1.0),
    "regalo": (icon_regalo, 0.95), "mochila": (icon_mochila, 1.0), "globo": (icon_globo, 1.0), "mano": (icon_mano, 1.0),
    "pausa": (icon_pausa, 1.0), "flecha": (icon_flecha, 1.0),
})
