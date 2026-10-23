# -*- coding: utf-8 -*-
EGW = "Descarga gratuita: egwwritings.org"
NOSUST = "Este video no sustituye la lectura del libro."
LIB = {
 "el-hogar-cristiano": ("El hogar cristiano", "Elena G. de White", EGW, False),
 "conduccion-del-nino": ("Conducción del niño", "Elena G. de White", EGW, False),
 "la-educacion": ("La educación", "Elena G. de White", EGW, False),
 "los-5-lenguajes-del-amor": ("Los 5 lenguajes del amor de los jóvenes", "Gary Chapman", "Editorial Unilit", True),
 "edad-de-oportunidades": ("Edad de oportunidades", "Paul David Tripp", "P&R Publishing", True),
 "limites-con-los-adolescentes": ("Límites con los adolescentes", "John Townsend", "Editorial Vida", True),
 "crianza-llena-de-gracia": ("Crianza llena de gracia", "Tim Kimmel", "Caribe-Betania / Grupo Nelson", True),
 "manten-encendido-tu-amor": ("Mantén encendido tu amor", "Danny Silk", "Loving on Purpose (ed. en español)", True),
 "como-criar-jovenes-de-fe-solida": ("Cómo criar jóvenes de fe sólida", "Kara Powell y Chap Clark", "Editorial Vida", True),
}
T_C = "[cálido, cercano, ritmo ágil]"
T_F = "[firme, cálido, cierre]"
T_R = "[adolescente, casual, directo]"

def b(tipo, seg, palabra, texto, visual, **kw):
    d = {"tipo": tipo, "seg": seg, "palabra": palabra, "texto": texto, "visual": visual}
    d.update(kw)
    return d

def tarjeta(libro_id, seg, palabra):
    t, a, d, _ = LIB[libro_id]
    return b("tarjeta_libro", seg, palabra, f"{t} · {a} · {d}", "tarjeta de libro con portada tipográfica (sin foto), título, autor y dónde conseguirlo")

CAPS = []

# ---------------- R00 ----------------
CAPS.append(dict(id="R00-reto-7-dias", tema="El reto familiar de siete días",
 libros=["el-hogar-cristiano","conduccion-del-nino","los-5-lenguajes-del-amor","edad-de-oportunidades","manten-encendido-tu-amor"],
 segmentos=[
  ("gancho","marisol",f"[cálido, enérgico, ritmo ágil] Siete días. Siete pasos pequeños para acercarte a tu adolescente. Un día a la vez."),
  ("d1","marisol",f"{T_C} Día uno: escucha una conversación completa, sin interrumpir."),
  ("d2","marisol",f"{T_C} Día dos: pregunta por algo que de verdad le interese."),
  ("d3","marisol",f"{T_C} Día tres: reconoce algo positivo de tu adolescente."),
  ("d4","marisol",f"{T_C} Día cuatro: compartan una actividad sin pantallas."),
  ("d5","marisol",f"{T_C} Día cinco: valida una emoción antes de aconsejar."),
  ("d6","marisol",f"{T_C} Día seis: reconoce un error tuyo y ofrece una disculpa, si corresponde."),
  ("d6m","mario","[papá, sincero, bajito] Me equivoqué. Perdóname."),
  ("d7","marisol",f"{T_C} Día siete: pregúntale qué podrías hacer para escucharlo mejor."),
  ("d7m","mario","[papá, abierto, tranquilo] ¿Qué puedo hacer para escucharte mejor?"),
  ("cierre","marisol",f"{T_F} Si un día no sale como esperabas, no pasa nada: sigue con el siguiente. Guarda este video y compártelo con tu familia."),
  ("libros","marisol",f"{T_C} Estos libros te acompañan: El hogar cristiano, Conducción del niño, Los 5 lenguajes del amor de los jóvenes, Edad de oportunidades y Mantén encendido tu amor."),
 ],
 beats=[
  b("titular","gancho","Siete","El reto familiar de siete días","siete círculos que se encienden uno a uno sobre fondo crema"),
  b("dia","d1","uno","Día 1 · Escucha una conversación completa, sin interrumpir.","número 1 grande, icono de oreja; etiqueta de libro: El hogar cristiano, cap. 30",libro_id="el-hogar-cristiano"),
  b("dia","d2","dos","Día 2 · Pregunta por algo que realmente le interese.","número 2, icono de signo de pregunta; etiqueta de libro: Edad de oportunidades · Tripp",libro_id="edad-de-oportunidades"),
  b("dia","d3","tres","Día 3 · Reconoce algo positivo de tu adolescente.","número 3, icono de estrella; etiqueta de libro: Los 5 lenguajes del amor de los jóvenes · Chapman",libro_id="los-5-lenguajes-del-amor"),
  b("dia","d4","cuatro","Día 4 · Compartan una actividad sin pantallas.","número 4, celular tachado y mesa de juego de mesa; etiqueta de libro: El hogar cristiano, cap. 30",libro_id="el-hogar-cristiano"),
  b("dia","d5","cinco","Día 5 · Valida una emoción antes de aconsejar.","número 5, icono de corazón con globo de diálogo; etiqueta de libro: Mantén encendido tu amor · Silk",libro_id="manten-encendido-tu-amor"),
  b("dia","d6","seis","Día 6 · Reconoce un error tuyo y ofrece una disculpa, si corresponde.","número 6, icono de mano tendida; etiqueta de libro: Conducción del niño",libro_id="conduccion-del-nino"),
  b("reaccion","d6m","perdóname","Perdóname.","palabra grande que entra de golpe, tono suave"),
  b("dia","d7","siete","Día 7 · Pregúntale qué podrías hacer para escucharlo mejor.","número 7, icono de oreja con signo de pregunta; etiqueta de libro: El hogar cristiano, cap. 30",libro_id="el-hogar-cristiano"),
  b("accion","cierre","siguiente","Si un día no sale como esperabas, sigue con el siguiente.","siete círculos, uno vacío que se vuelve a llenar"),
  tarjeta("el-hogar-cristiano","libros","hogar"),
  tarjeta("conduccion-del-nino","libros","Conducción"),
  tarjeta("los-5-lenguajes-del-amor","libros","lenguajes"),
  tarjeta("edad-de-oportunidades","libros","Edad"),
  tarjeta("manten-encendido-tu-amor","libros","Mantén"),
  b("tarjeta_libro","libros","amor",NOSUST,"línea final de la tarjeta de cierre"),
 ],
 fuentes=["Días 1–7: el reto familiar de siete días (tema propio del canal; siete pasos prácticos, sin afirmaciones de libros).",
  "Etiqueta de libro por día, sin afirmaciones nuevas: El hogar cristiano cap. 30 «El compañerismo en la familia» (PDF oficial egwwritings); Conducción del niño (cap. 48 «Las reacciones de los hijos» y sección «La confesión puede ser necesaria», PDF oficial); Edad de oportunidades (editorial P&R); Los 5 lenguajes del amor de los jóvenes (reseña de editorial, cinco lenguajes); Mantén encendido tu amor (descripción de editorial)."]))

# ---------------- R01 (piloto aprobado, sin cambios de texto) ----------------
CAPS.append(dict(id="R01-por-que-dejan-de-contar", tema="Por qué dejan de contarnos",
 libros=["el-hogar-cristiano","los-5-lenguajes-del-amor"],
 segmentos=[
  ("gancho","rewe","[adolescente, casual, directo] No todo lo que pienso tengo que contarlo."),
  ("privacidad","marisol","[cálido, cercano, ritmo ágil] A veces es solo privacidad. Y eso es crecer. Pero otras veces, se está protegiendo. De una reacción que ya se imagina: un regaño, una crítica, una comparación, o una plática que termina mal."),
  ("papa","mario","[papá, molesto, tajante] ¿Otra vez con lo mismo? ¡Te lo he dicho mil veces!"),
  ("cierra","rewe","[adolescente, apagado, bajito] Mejor no le cuento nada."),
  ("libros","marisol","[cálido, cercano, ritmo ágil] Elena de White lo dice en El hogar cristiano: los hijos no se animan a confiar cuando saben que enseguida vendrán severas reprensiones. Y Gary Chapman habla de cómo amar a tu hijo y apoyarlo cuando falla."),
  ("accion","marisol","[firme, cálido, cierre] No buscamos culpables. Buscamos qué hacer diferente. Para hoy: elige una reacción que no vas a repetir esta semana."),
 ],
 beats=[
  b("titular","gancho","contarlo","¿Por qué dejan de contarnos?","cuarto de adolescente visto de espaldas, ventana y cama, sin rostro"),
  b("icono","privacidad","privacidad","PRIVACIDAD","candado grande que se cierra; chip «es parte de crecer»"),
  b("icono","privacidad","protegiendo","SE PROTEGE","escudo que entra desde el costado"),
  b("reaccion","privacidad","regaño","REGAÑO","panel azul marino, palabra amarilla que cruza en whip"),
  b("reaccion","privacidad","crítica","CRÍTICA","misma palabra en whip, puntos de progreso 2 de 4"),
  b("reaccion","privacidad","comparación","COMPARACIÓN","misma palabra en whip, puntos de progreso 3 de 4"),
  b("reaccion","privacidad","termina","PLÁTICA QUE TERMINA MAL","dos líneas, puntos de progreso 4 de 4"),
  b("reaccion","papa","mil","¡MIL VECES!","panel que se inunda de naranja, palabra con sacudida"),
  b("ilustracion","cierra","nada","Mejor no le cuento nada.","puerta de recámara que se cierra, la luz se apaga"),
  tarjeta("el-hogar-cristiano","libros","Elena"),
  b("cita","libros","severas","Severas reprensiones","palabras SEVERAS / REPRENSIONES en impacto sobre comillas amarillas"),
  tarjeta("los-5-lenguajes-del-amor","libros","Chapman"),
  b("titular","accion","culpables","No buscamos culpables","la palabra CULPABLES tachada con una raya naranja"),
  b("accion","accion","reacción","Elige UNA reacción que no vas a repetir esta semana.","mesa con una taza y una nota; sin rostros"),
  b("tarjeta_libro","accion","semana",NOSUST,"línea final de la tarjeta de cierre"),
 ],
 fuentes=["HC cap. 71 «El don del habla», sección «Como perdió un padre la confianza de sus hijos» (PDF oficial egwwritings): «Estos no son estimulados a darle su confianza… porque saben que a continuación Vd. expresará severas reprensiones»",
  "Los 5 lenguajes del amor de los jóvenes: descripción de editorial (temas «anger and independence» y «Supporting and loving your teen when he or she fails»)"]))

# ---------------- R02 ----------------
CAPS.append(dict(id="R02-que-experimenta-cuando-habla", tema="Qué experimenta cuando decide hablar contigo",
 libros=["el-hogar-cristiano","crianza-llena-de-gracia"],
 segmentos=[
  ("gancho","rewe","[adolescente, vacilante, bajito] Le voy a contar. A ver cómo reacciona."),
  ("pregunta","marisol",f"{T_C} Solemos preguntar: ¿por qué no me habla? Cambia la pregunta: ¿qué vive cuando sí lo intenta? ¿Atención o prisa? ¿Comprensión o sermón? Cada vez que se anima, decide si vale la pena volver a hacerlo."),
  ("papa","mario","[papá, distraído, apurado] Ajá. Dime rápido, que estoy ocupado."),
  ("cierra","rewe","[adolescente, apagado, bajito] Mejor luego. No era nada."),
  ("libros","marisol",f"{T_C} Elena de White, en El hogar cristiano, habla de los niños, pero el principio aplica: no hieras corazones sensibles tratando con indiferencia lo que para ellos tiene gran importancia. Y Tim Kimmel, en Crianza llena de gracia, propone que los hijos necesitan amor seguro, un propósito y una esperanza sólida."),
  ("accion","marisol",f"{T_F} Para hoy: cuando te cuente algo, aunque parezca pequeño, deja lo que tengas en las manos, míralo y espera un segundo antes de responder."),
 ],
 beats=[
  b("titular","gancho","reacciona","¿Qué vive cuando decide hablar contigo?","pasillo de casa con una puerta entreabierta y luz cálida, sin rostros"),
  b("reaccion","pregunta","prisa","ATENCIÓN o PRISA","dos palabras, una se apaga y la otra se agranda"),
  b("reaccion","pregunta","sermón","COMPRENSIÓN o SERMÓN","misma mecánica, whip lateral"),
  b("icono","pregunta","volver","¿Vale la pena volver?","puerta entreabierta con un rayo de luz que se ensancha o se cierra"),
  b("ilustracion","papa","ocupado","Ajá. Dime rápido.","mesa con celular y reloj, manos ocupadas; sin rostros"),
  b("ilustracion","cierra","nada","No era nada.","puerta que se cierra despacio"),
  tarjeta("el-hogar-cristiano","libros","Elena"),
  b("cita","libros","indiferencia","No tratar con indiferencia lo que para ellos es importante","comillas amarillas, INDIFERENCIA tachada"),
  tarjeta("crianza-llena-de-gracia","libros","Kimmel"),
  b("icono","libros","esperanza","Amor seguro · Propósito · Esperanza","tres iconos simples (candado de corazón, brújula, sol) que entran en secuencia"),
  b("accion","accion","segundo","Deja lo que tengas en las manos. Míralo. Espera un segundo.","manos que sueltan un celular sobre la mesa; contador de un segundo"),
  b("tarjeta_libro","accion","responder",NOSUST,"línea final de la tarjeta de cierre"),
 ],
 fuentes=["HC cap. 30 «El compañerismo en la familia», sección «El estímulo y el elogio» (PDF oficial): «La madre no debe herir sus corazones sensibles tratando con indiferencia asuntos que, si bien son baladíes para ella, tienen gran importancia para ellos» (el texto habla de los niños; la cápsula lo dice como principio, no como cita)",
  "Crianza llena de gracia: resumen de editorial y reseñas (Publishers Weekly; OverDrive; Google Books id 1E3hAwAAQBAJ): amor seguro, propósito significativo, esperanza sólida"]))

# ---------------- R03 ----------------
CAPS.append(dict(id="R03-tres-necesidades", tema="Tres necesidades: autonomía, privacidad y seguridad emocional",
 libros=["la-educacion","el-hogar-cristiano"],
 segmentos=[
  ("gancho","rewe",f"{T_R} Quiero decidir yo. No todo te lo cuento. Y necesito saber cómo vas a reaccionar."),
  ("tres","marisol",f"{T_C} Son tres necesidades. Autonomía: decidir por sí mismo. Privacidad: no todo se cuenta. Y seguridad emocional: saber cómo vas a reaccionar. Casi siempre, lo que sabemos de un hijo es lo que él decide contarnos."),
  ("papa","mario","[papá, invasivo, apurado] ¿Con quién hablabas? ¡A ver, enséñame ese celular!"),
  ("cierra","marisol",f"{T_C} Así se aprieta, a la vez, la autonomía, la privacidad y la seguridad. Y la puerta se va cerrando."),
  ("libros","marisol",f"{T_C} Elena de White, en La educación: «Hágase sentir a los jóvenes que se les tiene confianza, y pocos serán los que no traten de mostrarse dignos de ella.» Y El hogar cristiano dedica todo un capítulo a «La seguridad mediante el amor»."),
  ("accion","marisol",f"{T_F} Para hoy: elige una decisión pequeña, como su ropa o el orden de su tarea, y déjala en sus manos."),
 ],
 beats=[
  b("titular","gancho","decidir","Tres necesidades que debemos comprender","tres círculos vacíos que se van llenando, sobre fondo crema"),
  b("icono","tres","Autonomía","1 · AUTONOMÍA","volante o timón que gira solo"),
  b("icono","tres","Privacidad","2 · PRIVACIDAD","candado y cortina que se cierra"),
  b("icono","tres","emocional","3 · SEGURIDAD EMOCIONAL","paraguas sobre un corazón"),
  b("reaccion","papa","celular","¡ENSÉÑAME EL CELULAR!","pantalla de celular que se aleja de una mano que intenta agarrarla"),
  b("ilustracion","cierra","puerta","Y la puerta se va cerrando","puerta que se cierra despacio, luz que se reduce"),
  tarjeta("la-educacion","libros","educación"),
  b("cita","libros","confianza","«Hágase sentir a los jóvenes que se les tiene confianza»","comillas grandes amarillas, CONFIANZA en morado"),
  tarjeta("el-hogar-cristiano","libros","hogar"),
  b("icono","libros","seguridad","La seguridad mediante el amor","título de capítulo sobre una casa con luz en la ventana"),
  b("accion","accion","decisión","Deja que decida él una cosa pequeña.","mano que entrega unas llaves o un control; sin rostros"),
 ],
 fuentes=["ED cap. 34 «La disciplina» (PDF oficial): «Hágase sentir a los jóvenes que se les tiene confianza y pocos serán los que no traten de mostrarse dignos de ella» (21 palabras)",
  "HC cap. 31 «La seguridad mediante el amor» (título de capítulo, PDF oficial)",
  "Afirmación general «lo que sabemos de un hijo es lo que él decide contarnos»: planteamiento del tema; se quitó la atribución a investigadores concretos por no estar verificada en fuente de libro."]))

# ---------------- R04 ----------------
CAPS.append(dict(id="R04-mi-primera-reaccion", tema="La pregunta incómoda: mi primera reacción",
 libros=["la-educacion","manten-encendido-tu-amor"],
 segmentos=[
  ("gancho","marisol","[directo, cercano, ritmo ágil] Tu hijo te cuenta algo que no te gusta. ¿Cuál es tu primera reacción?"),
  ("i1","marisol",f"{T_C} Hay cuatro muy comunes. La del soberbio, que siempre tiene la razón."),
  ("m1","mario","[papá, soberbio, tajante] Yo sé lo que te conviene. Y no se discute."),
  ("i2","marisol",f"{T_C} La del dramático, que vive todo como una crisis."),
  ("m2","mario","[papá, dramático, exagerado] ¡Ay, no! ¡Esto es un desastre! ¿Qué va a ser de ti?"),
  ("i3","marisol",f"{T_C} La del alarmista, que anticipa lo peor."),
  ("m3","mario","[papá, alarmista, angustiado] Así empiezan los que acaban mal."),
  ("i4","marisol",f"{T_C} Y la del negligente, que lo deja para después."),
  ("m4","mario","[papá, negligente, distraído, sin mirar] Ahorita no. Luego lo vemos."),
  ("libros","marisol",f"{T_C} Elena de White, en La educación: cuando un padre se impacienta y corre peligro de hablar imprudentemente, es mejor que guarde silencio. Y Danny Silk, en Mantén encendido tu amor, habla de mantener el amor aun frente a los errores, el dolor y el miedo."),
  ("accion","marisol",f"{T_F} Para hoy: respira, cuenta hasta cinco y di solo esto: «Gracias por contármelo. Déjame pensarlo.»"),
 ],
 beats=[
  b("titular","gancho","reacción","¿Cuál es tu primera reacción?","signo de interrogación enorme sobre una mesa de cocina vacía, sin rostros"),
  b("reaccion","i1","soberbio","EL SOBERBIO · siempre tengo la razón","tarjeta azul marino con corona torcida"),
  b("reaccion","m1","discute","NO SE DISCUTE","palabras en impacto con sacudida"),
  b("reaccion","i2","dramático","EL DRAMÁTICO · todo es una crisis","tarjeta con rayo y máscara de teatro"),
  b("reaccion","m2","desastre","¡UN DESASTRE!","palabra que tiembla y crece"),
  b("reaccion","i3","alarmista","EL ALARMISTA · anticipa lo peor","tarjeta con sirena de alarma"),
  b("reaccion","m3","acaban","¿ASÍ ACABAN?","nubes oscuras que cubren la tarjeta"),
  b("reaccion","i4","negligente","EL NEGLIGENTE · lo deja para después","tarjeta con reloj de arena"),
  b("reaccion","m4","Luego","LUEGO LO VEMOS","la palabra se desvanece a la derecha"),
  tarjeta("la-educacion","libros","Elena"),
  b("cita","libros","silencio","Es mejor que guarde silencio","comillas amarillas, SILENCIO grande en morado"),
  tarjeta("manten-encendido-tu-amor","libros","Silk"),
  b("icono","libros","encendido","Mantener el amor encendido","vela o llama pequeña que resiste el viento"),
  b("accion","accion","cinco","Respira. Cuenta hasta cinco. «Gracias por contármelo.»","cuenta regresiva 1-5 sobre un círculo; luego la frase"),
  b("tarjeta_libro","accion","pensarlo",NOSUST,"línea final de la tarjeta de cierre"),
 ],
 fuentes=["ED cap. 34 «La disciplina», sección «Los frutos del dominio propio» (PDF oficial): «Cuando un padre o un maestro se impacienta, y corre peligro de hablar imprudentemente, es mejor que guarde silencio. En este hay un poder maravilloso»",
  "Mantén encendido tu amor: descripción de editorial (christianbook.com): amor que se mantiene «in the face of mistakes, pain, and fear»",
  "Las frases de Mario son ejemplos ilustrativos de cada estilo, no citas de libros."]))
