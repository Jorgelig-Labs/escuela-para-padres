# -*- coding: utf-8 -*-
from lib import *
import lib
def S(n):
    return [s for (k, _, s) in lib.LIBROS if k == n][0]
def app(n, sid, extra):
    for seg in S(n)["segmentos"]:
        if seg[0] == sid:
            seg[2] = seg[2] + " " + extra; return
    raise KeyError((n, sid))
def ins(n, after, i, voz, tag, text):
    segs = S(n)["segmentos"]
    for k, seg in enumerate(segs):
        if seg[0] == after:
            segs.insert(k + 1, [i, voz, f"[{tag}] {text}"]); return
    raise KeyError((n, after))
def bt(n, tipo, seg, palabra, texto, visual):
    S(n)["beats"].insert(-1, dict(tipo=tipo, seg=seg, palabra=palabra, texto=texto, visual=visual))
RES = "firme, cálido, resumen"

# 1
app(1, "porque", "Es cuando más cambian, y cuando más fácil es dar por hecho que ya se las arreglan solos.")
ins(1, "i4", "resumen", "marisol", RES, "En resumen: confidente, paciente, firme con ternura, y con una voz que da calma. Cosas pequeñas que, en casa, pesan mucho.")
bt(1, "ideas", "resumen", "confidente", "Confidente\nPaciente\nFirme con ternura\nVoz que da calma", "cuatro íconos en fila")
# 2
ins(2, "i4", "resumen", "marisol", RES, "En resumen: amor y deber juntos, corrección sin tormenta, un molde distinto para cada hijo, y la humildad de empezar por uno mismo.")
bt(2, "ideas", "resumen", "amor y deber", "Amor + deber\nSin tormenta\nUn molde por hijo\nEmpezar por uno", "cuatro íconos en fila")
app(2, "i3", "Por ejemplo: uno responde a una mirada firme. Otro necesita una conversación a solas.")
# 3
app(3, "porque", "Es una pregunta que vale oro con un adolescente.")
app(3, "i1", "Piénsalo: ¿qué pasa el día que ya no estás tú vigilando?")
ins(3, "i2", "teen2", "rewe", "adolescente, tranquilo, sincero", "Cuando confían en mí, me dan más ganas de no fallarles.")
bt(3, "reaccion", "teen2", "no fallarles", "«Cuando confían en mí, me dan más ganas de no fallarles.»", "ícono de corazón con palomita")
ins(3, "i4", "resumen", "marisol", RES, "En resumen: guía sin aplastar, confía en vez de sospechar, pide en vez de ordenar, y cuando te desesperes, calla y respira.")
bt(3, "ideas", "resumen", "guía", "Guía sin aplastar\nConfía, no sospeches\nPide, no ordenes\nSilencio antes que crítica", "cuatro íconos en fila")
# 4
ins(4, "i4", "resumen", "marisol", RES, "En resumen: enséñale a pensar, evita las prohibiciones rígidas, deja que decida mientras estás cerca, y cuida tu paciencia.")
bt(4, "ideas", "resumen", "enséñale a pensar", "Enséñale a pensar\nSin prohibiciones rígidas\nQue decida contigo cerca\nCuida tu paciencia", "cuatro íconos en fila")
# 5
app(5, "porque", "Esa influencia se puede usar bien, o desperdiciar.")
app(5, "i1", "Por ejemplo: si pasa horas en el celular, antes de quitárselo pregúntate qué está buscando ahí.")
app(5, "i2", "Tú quizá demuestras amor con regalos. Él quizá necesita que lo mires a los ojos.")
ins(5, "i4", "resumen", "marisol", RES, "En resumen: ponte en su lugar, aprende los cinco lenguajes, descubre el suyo, y no sueltes el cariño cuando falle.")
bt(5, "ideas", "resumen", "ponte en su lugar", "Ponte en su lugar\nAprende los cinco lenguajes\nDescubre el suyo\nAma también cuando falla", "cuatro íconos en fila")
app(5, "accion", "Sin presión y sin examen. Solo observa.")
# 6
app(6, "i1", "Cuando lo ves así, un portazo deja de ser el final de la plática. Se vuelve una pista.")
app(6, "i2", "Por ejemplo: preguntar por su música, sus amigos, lo que le preocupa. Sin sermón. Solo curiosidad.")
app(6, "i3", "Por eso, ante un mal gesto, pregúntate qué hay detrás.")
ins(6, "i4", "papa", "mario", "papá, honesto, bajito", "Hijo… creo que me pasé. Perdóname.")
bt(6, "reaccion", "papa", "me pasé", "«Hijo… creo que me pasé. Perdóname.»", "burbuja cálida con corazón")
ins(6, "papa", "resumen", "marisol", RES, "En resumen: aprovecha en vez de sobrevivir, conecta, mira el corazón, y empieza por ti.")
bt(6, "ideas", "resumen", "aprovecha", "Aprovecha, no sobrevivas\nConecta\nMira el corazón\nEmpieza por ti", "cuatro íconos en fila")
app(6, "accion", "Pequeño y constante.")
# 7
ins(7, "papa", "teen", "rewe", "adolescente, resignado, bajando la guardia", "Ok… pero al menos me escuchaste.")
bt(7, "reaccion", "teen", "me escuchaste", "«Ok… pero al menos me escuchaste.»", "burbuja que se suaviza")
app(7, "i2", "Por ejemplo: si llegas tarde otra vez, este fin de semana no hay salida. Y lo cumples. Eso es una consecuencia realista.")
app(7, "i3", "Es decir: poco a poco, la decisión pasa de tus manos a las suyas.")
app(7, "i4", "Aquí el libro baja a lo concreto.")
ins(7, "i4", "resumen", "marisol", RES, "En resumen: cariño y firmeza juntos, consecuencias que puedas sostener, y un hijo que aprende a hacerse cargo de su vida. No necesitas una regla nueva por día. Con un límite bien puesto, empiezas.")
bt(7, "ideas", "resumen", "cariño y firmeza", "Cariño y firmeza\nConsecuencias sostenibles\nÉl se hace cargo\nUn límite bien puesto", "cuatro íconos en fila")
app(7, "accion", "Y si se lo toma mal, es normal. Un límite no necesita aplausos. Necesita constancia.")
# 8
app(8, "intro", "Pensado para papás que quieren criar sin vivir con miedo.")
app(8, "porque", "Pregúntate: ¿mi hijo sabe que puede equivocarse conmigo y seguir seguro?")
app(8, "i1", "Por ejemplo: si tu hijo se aísla, quizá no le falta disciplina. Quizá le falta sentirse seguro.")
app(8, "i2", "Tal vez tu hijo es callado y tú eres el que habla. O es intenso y tú eres tranquilo. No tiene que ser tu copia.")
app(8, "i3", "¿Qué pasa en tu casa cuando alguien dice una verdad incómoda?")
app(8, "i4", "Equivocarse no es el final de la conversación. Es el inicio.")
ins(8, "i4", "resumen", "marisol", RES, "En resumen: un amor seguro, y libertad para ser diferente, para ser sincero y para equivocarse. Esos son los capítulos que vale la pena recorrer.")
bt(8, "ideas", "resumen", "un amor seguro", "Amor seguro\nLibertad para ser diferente\nLibertad para ser sincero\nLibertad para equivocarse", "cuatro íconos en fila")
# 9
app(9, "porque", "Si la plática te da pena, es normal. A muchos papás nos pasa. Pero tu hijo ya recibe mensajes, de todos lados. La pregunta es si también los recibirá de ti.")
app(9, "i1", "Pregúntate: ¿mi hijo sabe qué pienso yo de este tema, o solo lo que ha visto en internet?")
app(9, "i2", "No todos los hijos están listos al mismo tiempo. Observa, y aprovecha lo natural: una película, una noticia, una pregunta suya.")
app(9, "i3", "Una respuesta honesta y tranquila vale más que una plática perfecta.")
ins(9, "i4", "resumen", "marisol", RES, "En resumen: tu fe como marco, su momento como guía, claridad con cuidado, y una mirada formada en casa. Empieza por hojear el libro.")
bt(9, "ideas", "resumen", "tu fe como marco", "Tu fe como marco\nSu momento como guía\nClaridad con cuidado\nMirada formada en casa", "cuatro íconos en fila")
app(9, "accion", "Y si se pone incómodo, no pasa nada. Que se note que la puerta queda abierta.")
# 10
app(10, "porque", "Si te suena familiar, este libro es para ti.")
app(10, "i1", "Un papá agotado reacciona peor. Cuidar de ti también es cuidar de ellos.")
app(10, "i2", "Quizá gritas como gritaban en tu casa. O callas como callaban. Verlo es el primer paso para elegir otra cosa.")
app(10, "i3", "Gracia sin reglas se vuelve caos. Reglas sin gracia, se vuelven guerra. El libro busca las dos.")
app(10, "i4", "Cuando no hay plan, cada conflicto se resuelve con el humor del día. Con valores claros, tú y tu pareja responden parecido.")
ins(10, "i4", "resumen", "marisol", RES, "En resumen: cuídate, mira tus patrones, une gracia con disciplina, y ponle palabras a tus valores. No tienes que ser perfecto. Solo ir un paso adelante de tu última reacción.")
bt(10, "ideas", "resumen", "cuídate", "Cuídate\nMira tus patrones\nGracia + disciplina\nPon palabras a tus valores", "cuatro íconos en fila")
app(10, "accion", "Sin culpa. Solo curiosidad. Ver el patrón ya es cambiarlo un poco.")
# 11
app(11, "intro", "Por eso lo traemos hoy.")
app(11, "i1", "Piensa en un adolescente que se encierra en su cuarto. ¿Será que pone distancia para no salir lastimado?")
app(11, "i2", "Tú no puedes controlar su cuarto, sus amigos ni su estado de ánimo. Sí puedes controlar tu tono, tu pausa y tu siguiente frase.")
app(11, "i3", "Por ejemplo: «Así no puedo hablar contigo. Cuando estemos tranquilos, seguimos.» No es un castigo. Es un límite.")
ins(11, "i3", "teen", "rewe", "adolescente, bajando la guardia", "Ok… luego hablamos.")
bt(11, "reaccion", "teen", "luego hablamos", "«Ok… luego hablamos.»", "burbuja que se suaviza")
ins(11, "teen", "resumen", "marisol", RES, "En resumen: conecta aunque cueste, hazte cargo de ti, y pon límites que cuiden, no que alejen.")
bt(11, "ideas", "resumen", "conecta aunque cueste", "Conecta aunque cueste\nHazte cargo de ti\nLímites que cuidan", "tres íconos en fila")
app(11, "accion", "Una sola vez basta para empezar.")
# 12
app(12, "i1", "Para conversar, ayudan las preguntas abiertas: ¿qué piensas tú? ¿qué te preocupa?")
app(12, "i2", "Piensa: ¿qué otros adultos de confianza conoce tu hijo? ¿A quién admira? Quizá puedes invitarlos a comer.")
app(12, "i3", "Pregúntate: ¿mi hijo sabe quién es, más allá de sus notas o su equipo?")
app(12, "i4", "Si tu hijo tiene catorce, la universidad parece lejana. Pero los puentes se construyen antes de cruzar.")
ins(12, "i4", "resumen", "marisol", RES, "En resumen: conversa, rodéalo de otros adultos, ayúdalo a saber quién es, y prepara el puente. No es una sola plática. Es un camino.")
bt(12, "ideas", "resumen", "conversa", "Conversa\nOtros adultos\nIdentidad\nUn puente", "cuatro íconos en fila")
