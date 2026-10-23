# -*- coding: utf-8 -*-
from lib import *

ACC = "firme, cálido, práctico"
CIE = "cálido, sereno, cierre"

# ------------------------------------------------------------------ 9
libro(9, "habla-claro-con-tus-hijos", "Habla claro con tus hijos sobre el sexo", "Josh y Dottie McDowell", "Editorial Unilit", True,
 segs=[
  ("gancho", "mario", "papá, bajito, dudoso", "No sé ni cómo empezar esa plática."),
  ("intro", "marisol", CAL, "Si te pasa, no estás solo. Hoy: Habla claro con tus hijos sobre el sexo, de Josh y Dottie McDowell. Es un libro delicado, así que este video es breve y práctico. Y un consejo: antes de dárselo a tu hijo, hojéalo tú."),
  ("porque", "marisol", CAL, "Los McDowell escribieron esta guía desde su experiencia criando a cuatro hijos. La pensaron para los papás a quienes esta conversación les resulta incómoda."),
  ("i1", "marisol", CAL, "Idea uno: ubica el tema dentro de tu fe. Según la editorial, el libro ayuda a ver el sexo dentro de una visión bíblica de la relación con Dios, y no como un tema aparte."),
  ("i2", "marisol", CAL, "Idea dos: conoce el momento de tu hijo. El libro te ayuda a juzgar su madurez emocional y espiritual, y a reconocer los momentos naturales para enseñar."),
  ("i3", "marisol", CAL, "Idea tres: habla con apertura, cuidando sus sentimientos. Es decir: decir las cosas claras, sin avergonzarlo."),
  ("i4", "marisol", CAL, "Idea cuatro: forma su visión del mundo. Vivimos rodeados de contenido sexual. El libro busca que tu hijo tenga una mirada formada en casa, y no solo en internet."),
  ("accion", "marisol", ACC, "Esta semana no hace falta la gran conversación. Hojea el libro tú primero. Después busca un momento natural, como un trayecto en el auto, y pregúntale qué ha escuchado sobre el tema. Y escucha sin reaccionar."),
  ("cierre", "marisol", CIE, "Habla claro con tus hijos sobre el sexo, de Josh y Dottie McDowell, en español de Editorial Unilit. " + NOSUST),
 ],
 beats=[
  ("reaccion", "gancho", "cómo empezar", "«No sé ni cómo empezar esa plática.»", "burbuja de diálogo en blanco"),
  ("titular", "intro", "Habla claro con tus hijos sobre el sexo", "Habla claro con tus hijos sobre el sexo · Josh y Dottie McDowell", "portada genérica de libro"),
  ("ilustracion", "intro", "hojéalo tú", "Antes de dárselo a tu hijo, hojéalo tú", "libro abierto con palomita"),
  ("ilustracion", "porque", "cuatro hijos", "Una guía desde la experiencia de criar a 4 hijos", "cuatro siluetas de sillas, sin rostros"),
  ("titular", "i1", "dentro de tu fe", "1 · Dentro de tu fe", "ícono de cruz sencilla sobre un libro"),
  ("titular", "i2", "el momento de tu hijo", "2 · Conoce su momento", "ícono de reloj con hoja"),
  ("ideas", "i2", "madurez", "Su madurez emocional y espiritual\nMomentos naturales para enseñar", "reloj y hoja que crece"),
  ("titular", "i3", "con apertura", "3 · Hablar claro, cuidando sus sentimientos", "burbuja de diálogo con corazón"),
  ("titular", "i4", "visión del mundo", "4 · Forma su visión del mundo", "ícono de ventana a un paisaje"),
  ("ideas", "i4", "formada en casa", "Una mirada formada en casa, no solo en internet", "casa con ventana luminosa"),
  ("accion", "accion", "Hojea el libro", "Hojea el libro tú primero", "libro abierto"),
  ("accion", "accion", "qué ha escuchado", "Pregunta qué ha escuchado. Escucha sin reaccionar.", "ícono de oído y auto en trayecto"),
  ("tarjeta_libro", "cierre", "Habla claro con tus hijos sobre el sexo", "Habla claro con tus hijos sobre el sexo\nJosh y Dottie McDowell\nEditorial Unilit\nEste video no sustituye la lectura del libro.", "portada genérica de libro"),
 ],
 fuentes=["Harvest House Publishers (descripción del original) y reseñas: guía desde la experiencia de criar cuatro hijos, visión bíblica, madurez del hijo, momentos de enseñanza, visión del mundo."])

# ------------------------------------------------------------------ 10
libro(10, "padres-confiados", "Padres confiados", "Jim Burns", "Editorial Vida", True,
 segs=[
  ("gancho", "rewe", ADO, "Siempre reaccionas igual."),
  ("papa", "mario", "papá, exasperado, a la defensiva", "¡Es que no sé de dónde me sale!"),
  ("intro", "marisol", CAL, "Buena pregunta. Hoy: Padres confiados, de Jim Burns. Un libro para papás con buenas intenciones, pero con frustraciones diarias."),
  ("porque", "marisol", CAL, "Según la editorial, los conflictos constantes nos desgastan. Y a veces nadie nos enseñó lo básico de ser papás. Burns, que ha acompañado familias por más de veinte años, lo cuenta con la historia de una pareja, Mark y Becky, que intenta criar hijos normales."),
  ("i1", "marisol", CAL, "Idea uno: cuida tu propia vida. El libro habla de reabastecer vidas demasiado ocupadas, y de equilibrar el cuidado de ti con el de tu familia."),
  ("i2", "marisol", CAL, "Idea dos: vence los patrones familiares negativos. Es parte del subtítulo del libro. Mira lo que repites de tu propia familia, y decide qué cambias."),
  ("i3", "marisol", CAL, "Idea tres: crea un hogar lleno de gracia. El libro trata la disciplina y la calidez en casa como cosas que van juntas."),
  ("i4", "marisol", CAL, "Idea cuatro: comunica tus valores. Con ejercicios y preguntas al final de cada tema, te ayuda a armar un plan familiar en vez de improvisar."),
  ("accion", "marisol", ACC, "Esta semana, dos cosas. Una: anota una reacción que repites aunque no te gusta, y pregúntate de dónde la aprendiste. Dos: escribe con tu pareja dos valores que quieren que se vean en casa."),
  ("cierre", "marisol", CIE, "Padres confiados, de Jim Burns, en español de Editorial Vida. " + NOSUST),
 ],
 beats=[
  ("titular", "gancho", "igual", "Siempre reaccionas igual.", "ícono de flecha circular que se repite"),
  ("reaccion", "papa", "no sé de dónde", "«¡Es que no sé de dónde me sale!»", "ícono de signo de interrogación sobre un pecho"),
  ("titular", "intro", "Padres confiados", "Padres confiados · Jim Burns", "portada genérica de libro"),
  ("ilustracion", "porque", "Mark y Becky", "La historia de Mark y Becky", "dos siluetas de pareja con maletín y mochila, sin rostros"),
  ("titular", "i1", "cuida tu propia vida", "1 · Cuida tu propia vida", "batería que se recarga"),
  ("ideas", "i1", "reabastecer", "Reabastecer vidas demasiado ocupadas\nEquilibrar tu cuidado y el de tu familia", "agenda llena y una pausa"),
  ("titular", "i2", "patrones familiares", "2 · Rompe patrones negativos", "cadena con un eslabón roto"),
  ("ideas", "i2", "decide qué cambias", "Mira lo que repites\nDecide qué cambias", "árbol genealógico estilizado"),
  ("titular", "i3", "hogar lleno de gracia", "3 · Un hogar lleno de gracia", "casa con corazón"),
  ("ideas", "i3", "calidez", "Disciplina y calidez, juntas", "dos manos entrelazadas"),
  ("titular", "i4", "comunica tus valores", "4 · Comunica tus valores", "ícono de lista con estrella"),
  ("accion", "accion", "anota una reacción", "Anota una reacción que repites: ¿de dónde la aprendí?", "libreta con lápiz"),
  ("accion", "accion", "dos valores", "Dos valores para tu casa, con tu pareja", "dos íconos de valor: corazón y estrella"),
  ("tarjeta_libro", "cierre", "Padres confiados", "Padres confiados\nJim Burns\nEditorial Vida\nEste video no sustituye la lectura del libro.", "portada genérica de libro"),
 ],
 fuentes=["Google Books MX (descripción de Editorial Vida y subtítulo en español).", "HomeWord (descripción, historia de Mark y Becky, más de veinte años de consejería)."])

# ------------------------------------------------------------------ 11
libro(11, "manten-encendido-tu-amor", "Mantén encendido tu amor", "Danny Silk", "Loving on Purpose / Buena Semilla", True,
 segs=[
  ("gancho", "rewe", ADO, "Si me controlas, me alejo."),
  ("intro", "marisol", CAL, "Hoy: Mantén encendido tu amor, de Danny Silk. Una aclaración: no es un libro solo de adolescentes. Habla de relaciones en general, pero sus ideas de conexión y límites aplican muy bien en casa."),
  ("porque", "marisol", CAL, "El subtítulo resume su propuesta: conexión, comunicación y límites. Las reseñas lo describen como un enfoque distinto. En lugar de controlar al otro, cada quien se hace responsable de sí mismo. Esa idea cabe perfecto en la crianza de un adolescente."),
  ("i1", "marisol", CAL, "Idea uno: conexión. Según una reseña, el autor sostiene que fuimos diseñados para conectar, pero muchas personas mantienen distancia para evitar que las lastimen. Y esa distancia nos quita poder para cambiar las cosas."),
  ("i2", "marisol", CAL, "Idea dos: poder no es controlar al otro. Es hacerte responsable de quién eres y de cómo respondes. Para un papá, significa que lo único que puedes dirigir del todo, eres tú."),
  ("i3", "marisol", CAL, "Idea tres: los límites. Según las reseñas, la persona con dominio propio pone límites sanos, y esos límites ayudan al otro a hacerse responsable también. No son un muro. Cuidan la relación."),
  ("accion", "marisol", ACC, "Esta semana, cuando tu hijo te haga enojar, haz una pausa y pregúntate: ¿qué necesito controlar, a él o a mí? Y busca un momento en que, aunque estés molesto, tu tono diga:"),
  ("papa", "mario", "papá, molesto pero sereno, cálido", "Estoy molesto. Pero sigo aquí."),
  ("cierre", "marisol", CIE, "Mantén encendido tu amor, de Danny Silk, en ediciones en español de Loving on Purpose y Buena Semilla. " + NOSUST),
 ],
 beats=[
  ("titular", "gancho", "controlas", "Si me controlas, me alejo.", "ícono de hilo tenso que se suelta"),
  ("titular", "intro", "Mantén encendido tu amor", "Mantén encendido tu amor · Danny Silk", "portada genérica de libro con llama"),
  ("ideas", "porque", "conexión, comunicación y límites", "Conexión\nComunicación\nLímites", "tres íconos: cable, burbuja, cerca"),
  ("titular", "i1", "conexión", "1 · Diseñados para conectar", "dos cables que encajan"),
  ("ideas", "i1", "distancia", "Distancia por miedo a que nos lastimen\nNos quita poder para cambiar las cosas", "muro bajo entre dos casas"),
  ("titular", "i2", "poder no es controlar", "2 · Poder ≠ controlar al otro", "ícono de volante en la mano propia"),
  ("ideas", "i2", "quién eres", "Responsable de quién eres y de cómo respondes", "espejo"),
  ("titular", "i3", "los límites", "3 · Límites que cuidan la relación", "cerca con puerta"),
  ("ideas", "i3", "ayudan al otro", "Límites sanos, no muros\nAyudan al otro a hacerse responsable", "puerta abierta con cerca baja"),
  ("accion", "accion", "pausa", "Pausa: ¿lo controlo a él o me controlo a mí?", "ícono de pausa"),
  ("reaccion", "papa", "sigo aquí", "«Estoy molesto. Pero sigo aquí.»", "ícono de corazón encendido"),
  ("tarjeta_libro", "cierre", "Mantén encendido tu amor", "Mantén encendido tu amor\nDanny Silk\nLoving on Purpose / Buena Semilla\nEste video no sustituye la lectura del libro.", "portada genérica de libro"),
 ],
 fuentes=["Reseña de Craig Owens (craigtowens.com, 2015) para conexión, poder y límites.", "Subtítulo y descripción de la edición en español (conexión, comunicación, límites)."])

# ------------------------------------------------------------------ 12
libro(12, "como-criar-jovenes-de-fe-solida", "Cómo criar jóvenes de fe sólida", "Kara Powell y Chap Clark", "Editorial Vida", True,
 segs=[
  ("gancho", "rewe", ADO, "¿Puedo dudar sin que se enojen?"),
  ("intro", "marisol", CAL, "Hoy: Cómo criar jóvenes de fe sólida, de Kara Powell y Chap Clark. En inglés se llama Sticky Faith."),
  ("porque", "marisol", CAL, "La editorial lo dice así: «Casi la mitad de los jóvenes que se gradúan de secundaria tienen fuertes luchas con su fe.» El libro se apoya en un estudio del Instituto Fuller sobre la transición a la universidad, y busca darle a los papás una estrategia sencilla para que la fe de sus hijos dure."),
  ("i1", "marisol", CAL, "Idea uno: conversaciones. Uno de los capítulos se llama conversaciones sobre la fe sólida. La fe se transmite hablando, no solo asistiendo a la iglesia."),
  ("i2", "marisol", CAL, "Idea dos: una red de relaciones. Otro capítulo habla de una red de relaciones consolidada. Tu hijo necesita, además de ti, otros adultos y amigos que lo acompañen en su camino de fe."),
  ("i3", "marisol", CAL, "Idea tres: identidad. El libro dedica un capítulo a una identidad inalterable. Un joven que sabe quién es, tiene dónde apoyarse cuando llegan las dudas."),
  ("i4", "marisol", CAL, "Idea cuatro: un puente para salir de casa. Con ese título, otro capítulo trata la transición a la universidad y a la vida adulta. Justo donde el estudio vio más luchas."),
  ("accion", "marisol", ACC, "Esta semana, dos cosas. Una: pregúntale qué piensa sobre algo de la fe, y no lo corrijas. Solo di: cuéntame más. Dos: comparte tú una duda, o un momento difícil de tu propia fe. Los jóvenes escuchan distinto cuando es de adulto a persona."),
  ("cierre", "marisol", CIE, "Cómo criar jóvenes de fe sólida, de Kara Powell y Chap Clark, en español de Editorial Vida. " + NOSUST),
 ],
 beats=[
  ("titular", "gancho", "dudar", "¿Puedo dudar sin que se enojen?", "burbuja con signo de interrogación"),
  ("titular", "intro", "Cómo criar jóvenes de fe sólida", "Cómo criar jóvenes de fe sólida · Kara Powell y Chap Clark", "portada genérica de libro con raíces"),
  ("cita", "porque", "Casi la mitad", "«Casi la mitad de los jóvenes que se gradúan de secundaria tienen fuertes luchas con su fe.» — Descripción de Editorial Vida", "ícono de círculo dividido a la mitad"),
  ("titular", "i1", "conversaciones", "1 · Conversaciones sobre la fe", "dos burbujas de diálogo"),
  ("titular", "i2", "red de relaciones", "2 · Una red de relaciones", "red de puntos conectados"),
  ("ideas", "i2", "otros adultos", "Otros adultos que lo acompañen\nAmistades que sostienen", "círculo de siluetas, sin rostros"),
  ("titular", "i3", "identidad", "3 · Una identidad firme", "árbol con raíces profundas"),
  ("ideas", "i3", "dónde apoyarse", "Una identidad que no se mueve\nDónde apoyarse cuando llegan las dudas", "ancla"),
  ("titular", "i4", "un puente", "4 · Un puente para salir de casa", "puente entre una casa y un campus"),
  ("accion", "accion", "cuéntame más", "Pregunta qué piensa. No corrijas: «cuéntame más»", "burbuja de diálogo abierta"),
  ("accion", "accion", "una duda", "Comparte una duda tuya", "ícono de signo de interrogación compartido"),
  ("tarjeta_libro", "cierre", "Cómo criar jóvenes de fe sólida", "Cómo criar jóvenes de fe sólida\nKara Powell y Chap Clark\nEditorial Vida\nEste video no sustituye la lectura del libro.", "portada genérica de libro"),
 ],
 fuentes=["Google Books MX (descripción y capítulos de la edición en español de Editorial Vida).", "Fuller Youth Institute (College Transition Project, 'casi la mitad')."])
