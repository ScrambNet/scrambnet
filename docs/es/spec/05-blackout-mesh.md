# Especificación de ScrambNet — Parte 5: Apagón y diversidad de enlaces en malla mixta

> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../../en/spec/05-blackout-mesh.md)).

**Estado: BORRADOR (DRAFT), y un riesgo de investigación declarado.** Este es el mayor
diseño sin escribir del proyecto, y esta parte devuelve —en la medida en que el roadmap lo
permite— un resultado *parcial*: un modelo sólido de red mixta y una idea genuinamente
portante (dispersión por pasarelas independientes, como propiedad de *disponibilidad*),
envuelta alrededor de residuos que nombra a plena fuerza y no pretende cerrar. No compromete
**ninguna pila de malla concreta** y no hace **ninguna afirmación de anonimato para la capa
de radio**; es una parte de postura y modelo, exactamente como lo es la Parte 4. Los valores
de hombre de paja se marcan con `(s)`.

Lee primero el §3 (la evaluación de realismo) —es la columna vertebral, y dice la cosa mucho
mayor que esta parte rehúsa afirmar. La única afirmación positiva portante es estrecha: *la
dispersión a través de pasarelas independientes extiende I-3 a la salida del vecindario
físico como una propiedad de disponibilidad, y a nada en la malla se le permite mover el
techo del contenido I-2* (BL-16) —la malla es tan independiente del techo como la Parte 4
mantiene el transporte (CT-16). Esta parte es el peldaño L4 al que el CT-18a de la Parte 4
hace la transferencia, y se mantiene coherente con esa concesión (BL-17): cuando no hay
vecino, no se entrega nada.

## 1. El modelo de red mixta y los roles

- **BL-1 (la malla es una capa, no un modo). [normativo]** Un nodo conforme DEBE (MUST)
  tratar los enlaces de radio locales y los enlaces de internet como tipos de enlace que
  coexisten *en todo momento*, no como un "modo de apagón" en el que se entra al perder la
  infraestructura. Perder el enlace ascendente DEBE (MUST) ser un cambio de *ruta* (un salto
  más hacia una pasarela), nunca un cambio de protocolo, de identidad, ni de postura de
  seguridad. Un diseño con un "modo de malla" distinto que el usuario conmuta es no conforme
  a este encuadre (OP-6).
- **BL-2 (roles, por la realidad del hardware). [normativo]** Un nodo DEBE (MUST)
  autoclasificarse, a partir de su capacidad de radio real, como exactamente uno de: **hoja**
  (un teléfono: concurrencia STA+AP o Wi-Fi Aware, atado a la batería, sin root), **troncal**
  (un PC/SBC de doble radio ejecutando 802.11s de verdad, store-and-forward continuo), o
  **pasarela** (una troncal o una hoja que en ese momento sostiene un enlace ascendente y lo
  anuncia). Los roles se derivan de la capacidad y varían en el tiempo —una pasarela que
  pierde su enlace ascendente pasa a ser troncal u hoja— nunca un nivel fijo.
- **BL-3 (el opt-in es una precondición de cualquier enlace de radio). [normativo]** Un nodo
  NO DEBE (MUST NOT) originar, retransmitir ni hacer de pasarela de tráfico alguno sobre un
  enlace de radio local sin un opt-in previo, explícito e informado *específico de la
  participación en la malla* y distinto de cualquier opt-in de retransmisión, porque la
  visibilidad de la malla es física (BL-18) y porta una identidad de capa de radio que el
  overlay no puede rotar (BL-18a). El silencio, o heredar el opt-in de retransmisión, es no
  conforme.
- **BL-4 (presupuesto honesto de batería y almacenamiento). [normativo]** Un nodo hoja DEBE
  (MUST) exponer, antes del opt-in, el costo de batería y almacenamiento en que realmente
  incurrirá (hombre de paja: una cuota acotada de store-and-forward y un horario de radio con
  ciclo de trabajo), y NO DEBE (MUST NOT) prometer una disponibilidad continua de grado
  troncal que no pueda sostener con batería. El presupuesto concreto es OP-6 abierto y DEBE
  (MUST) declararse, no adivinarse (BL-20).

## 2. Dispersión por pasarelas independientes, direccionamiento, acarreo y mezcla

### 2.1 Dispersión por pasarelas independientes (la idea portante, como disponibilidad)

- **BL-5 (las partes DEBERÍAN salir por pasarelas independientes). [normativo]** Cuando las
  `n` partes de un mensaje (SP-2) atraviesan la malla local hacia un enlace ascendente, un
  cliente conforme DEBERÍA (SHOULD) enrutarlas de modo que salgan por pasarelas *distintas*,
  extendiendo I-3 (ningún punto único) a la salida del vecindario físico. Una pasarela que
  lleve `k` de las `n` partes es un punto único y DEBE (MUST) evitarse donde ≥2 pasarelas
  independientes-*estimadas* (BL-6) sean alcanzables. En un apagón profundo la estimación de
  independencia puede estar vacía (BL-6); entonces BL-5 degrada a BL-7 **por defecto**, no
  como un caso límite. El beneficio que se afirma aquí es **disponibilidad**, no
  inobservabilidad (§3): el fallo, el bloqueo o la captura sybil de ninguna pasarela única
  mata la entrega —este es el veredicto CT-15 para los transportes, en espacio de malla.
- **BL-6 (qué puede significar "independiente" en la capa de radio —enunciado, no resuelto).
  [normativo, declara-residuo]** Un cliente conforme NO DEBE (MUST NOT) tratar las pasarelas
  como independientes sobre la base de *autodeclaración* (GR-3, en espacio de radio).
  "Independiente" solo puede estimarse a partir de señales *observables, no autodeclaradas*
  —ASes de enlace ascendente distintos *donde un mapa de AS (Parte 8) sea alcanzable*,
  próximos saltos de radio distintos, dirección física distinta— cada una de las cuales es
  débil, falsificable o **no disponible dentro de un apagón** (el mapa de AS, la señal más
  fuerte, suele ser lo primero que desaparece). El significado honesto de "pasarela
  independiente" es por tanto una **estimación de confianza acotada**, no un hecho verificado
  (§4b); un cliente DEBE (MUST) presentarlo como tal y NO DEBE (MUST NOT) afirmar
  independencia de pasarela verificada. Véase BL-21 —este es el problema recurrente de la
  independencia en espacio de radio.
- **BL-7 (demasiado pocas —o cero— pasarelas independientes degrada, nunca falla en abierto).
  [normativo]** Donde menos de dos pasarelas independientes-estimadas sean alcanzables, un
  cliente NO DEBE (MUST NOT) empujar silenciosamente `k` partes por una sola como si la
  dispersión se sostuviera; DEBE (MUST) retener las partes para una salida independiente
  posterior (acotada por el TTL de BL-12), repartirlas en el tiempo, o exponer que la salida
  física es un punto único para este mensaje (BL-19). El techo (I-2) no se ve afectado en
  ningún caso (BL-16).

### 2.2 Direccionamiento sin alcanzabilidad global

- **BL-8 (los nombres sobreviven; las rutas globales no). [normativo]** El `id` Ed25519 del
  relé/destinatario (Parte 2) y el `box_id`/rendezvous de la Parte 6 DEBEN (MUST) seguir
  siendo los nombres estables dentro de un apagón; lo que se rompe es la *alcanzabilidad*
  global, no el nombrado. Un nodo NO DEBE (MUST NOT) depender de un DHT alcanzable ni de
  ninguna ruta global para la selección del próximo salto en la malla.
- **BL-9 (próximo salto sin un DHT —el menú y sus costos).** En ausencia de una ruta global,
  un próximo salto de malla se elige mediante un método local de costo acotado: inundación
  epidémica hacia cualquier enlace ascendente (barato, sin conocimiento del destino, alto
  costo de radio); un *gradiente* de alcanzabilidad donde los vecinos anuncian alcanzabilidad
  *hacia una pasarela* —nunca hacia el destinatario nombrado, lo que sería un selector
  (I-4/SP-7); o acarreo físico (store-and-forward hasta que una pasarela entre en alcance).
  Esta cláusula nombra el menú; la elección es un hombre de paja (BL-20), y toda opción DEBE
  (MUST) preservar SP-7 (ninguna enlazabilidad entre rutas sobre los bytes) e I-4 (BL-15).
- **BL-10 (la entrega sigue corriendo a través de los buzones de la Parte 6, nunca a un
  dispositivo nombrado). [normativo]** El trabajo de la malla termina en el *enlace
  ascendente*: una vez que las partes alcanzan internet reingresan al overlay y se entregan a
  buzones muertos dispersos (Parte 6) exactamente como antes. La malla NO DEBE (MUST NOT)
  intentar entregar directamente a un *dispositivo* destinatario nombrado —eso haría que la
  entrega apuntara a una persona, violando el contrato de la Parte 6 (RZ-1). El caso
  genuinamente todo-local (remitente, buzón y destinatario todos dentro de la malla, sin
  enlace ascendente) se atiende con que el **buzón** del destinatario sea también alcanzable
  por la malla —depósito y sondeo corren ambos sobre la malla *hacia un buzón*, nunca hacia
  el dispositivo del destinatario— que es el ítem abierto que la Parte 6 §9 lista como
  "sondeo sobre la malla durante el apagón (OP-6)." Enrutar a un dispositivo destinatario
  nombrado sigue prohibido como selector.

### 2.3 Store-and-forward y el veredicto del encuadre

- **BL-11 (la validez de Sphinx, no los bytes, es la restricción sobre el acarreo largo).
  [normativo, declara-residuo]** El paquete Sphinx de 2048 bytes (SP-3) es autocontenido en
  *bytes* pero no en *validez*: su seguridad por salto se vincula a la época `onion` de ≤7
  días de un relé (CH-5) y a la caché de replay por época (SP-5, SP-7b). Un paquete acarreado
  durante horas o días a través de enlaces intermitentes PUEDE (MAY) sobrevivir a la época
  que supuso su primer salto, o llegar después de que el estado de replay haya rotado o se
  haya perdido entre reinicios. Un diseño conforme DEBE (MUST) enunciar esto y NO DEBE (MUST
  NOT) suponer que un paquete Sphinx es acarreable indefinidamente sin cambios.
- **BL-12 (el veredicto: el apagón necesita su propio sobre de store-and-forward).
  [normativo]** A causa de BL-11, y porque el store-and-forward necesita campos para los que
  el paquete fijo de 2048 bytes no tiene sitio (un tiempo de vida acotado, fragmentación y
  reensamblado para enlaces intermitentes, señalización de custodia por salto), el veredicto
  de este borrador es que **el acarreo en apagón necesita su propio encuadre exterior** —un
  bundle al estilo DTN (arte previo: RFC 4838/5050) que *envuelve* el paquete Sphinx interior
  sin cambiarlo, está él mismo rellenado a longitud fija, y cuyos metadatos están protegidos
  por AEAD, nunca en claro. El paquete interior queda intacto; el sobre es nuevo y vive solo
  en los enlaces de apagón. Este es un veredicto de hombre de paja (BL-20), revocado solo por
  un argumento que cierre BL-11, que este borrador no tiene.
- **BL-13 (el sobre no debe convertirse en un selector —y hereda el residuo de anidamiento de
  CT-6a). [normativo, declara-residuo]** El TTL del sobre, el índice de fragmento y los
  campos de custodia son exactamente los metadatos en claro que I-4 prohíbe; DEBEN (MUST)
  vivir dentro de una trama protegida por AEAD, de tamaño fijo y de apariencia uniforme
  (disciplina SP-4), y NO DEBEN (MUST NOT) permitir que un observador de radio enlace dos
  fragmentos de un mensaje, ni dos partes de un mensaje, mejor de lo que SP-7 ya permite en
  el overlay. **Residuo honesto, heredado de la Parte 4:** envolver un paquete interior
  uniforme por I-4 dentro de un bundle exterior recrea la **superficie de estructura anidada
  de CT-6a** en espacio de radio —una trama exterior de tamaño fijo cuyo tamaño, tiempos o
  fragmentación pueden delatar que lleva una *segunda* unidad fija, y la uniformidad por capa
  **no** hace el anidamiento indetectable para un observador de RF. Este es un residuo
  declarado, no cerrado por el encuadre. Es sobrevivible solo en el sentido en que todo aquí
  lo es: el adversario de RF del apagón es *local*, así que la detección del anidamiento
  cuesta *observabilidad-de-participación* —que BL-18 ya concede que se pierde— y **no** toca
  el techo del contenido I-2.

### 2.4 Mezcla de capa de radio frente a la pasarela sybil

- **BL-14 (la pasarela sybil es un eclipse físico; la respuesta es parcial). [normativo,
  declara-residuo]** Un nodo que anuncia "tengo enlace ascendente" atrae el tráfico del
  vecindario, y una pasarela sybil (o coalición) es un *eclipse físico* —la instancia de
  capa de radio del residuo de eclipse de la Parte 2 (OP-2). La respuesta parcial es (i)
  mezcla de origen en la capa de radio (BL-15) de modo que una pasarela no pueda atribuir
  trivialmente una parte a su vecino originante *en la capa de trama*, compuesta con (ii)
  dispersión por pasarelas independientes (BL-5) de modo que ninguna pasarela única vea `k`.
  Una descripción conforme DEBE (MUST) declarar esta respuesta **parcial**: eleva el costo
  del sybil, no elimina el eclipse, y se reduce a OP-1/OP-2 recurriendo en la capa de radio
  (BL-6, BL-21).
- **BL-15 (la mezcla de origen en la capa de radio es una medida de disponibilidad/anti-eclipse,
  no de ocultación del origen). [normativo]** El tráfico sobre un enlace de radio local DEBE
  (MUST) satisfacer I-4 ante un observador de radio sobre los bytes (tramas uniformes de
  tamaño fijo, BL-13) y DEBERÍA (SHOULD) aplicar mezcla de origen de modo que el remitente
  inmediato de una parte a nivel de trama no quede, por la trama, marcado como su originante.
  Esto **no** es la defensa de muestreo de directorio GR-8 (GR-8 mezcla la *muestra
  almacenada* de un cliente entre clases de origen contra el eclipse del mapa —un mecanismo
  distinto contra un adversario distinto) y NO DEBE (MUST NOT) tomar prestado su nombre ni
  sus garantías. Y NO DEBE (MUST NOT) presentarse como ocultación del originante *físico*: un
  adversario local con radiogoniometría conoce el emisor físico de una transmisión con
  independencia del contenido de la trama (BL-18), así que la mezcla de origen de radio
  compra *costo anti-eclipse frente a una pasarela sybil*, nunca anonimato de origen —la
  misma disciplina enlazabilidad-vs-disponibilidad que CT-15a impone para los transportes.

## 3. La evaluación honesta de realismo (la columna vertebral)

*(Escrita en la voz de §residuo de las Partes 4, 8 y 11. Esta es la parte, no un apéndice.)*

**Lo que es genuinamente diseñable, y real.** Tres cosas. Primera, el *modelo de red mixta*
(BL-1): tratar la radio y la internet como tipos de enlace coexistentes de modo que perder un
enlace ascendente sea un salto más, no un mundo distinto, es limpio, construible y respaldado
por arte previo (Briar, Reticulum, Yggdrasil/cjdns, Freifunk demuestran piezas). Segunda —la
idea que gana al paradigma su sustento— *dispersión por pasarelas independientes* (BL-5): la
debilidad fatal clásica de toda malla con pasarela es que la pasarela lo ve todo, y ScrambNet
la responde con el mecanismo que define toda la red, repartiendo las `n` partes entre
pasarelas de modo que ninguna salida física única vea `k`. Tercera, la *guarda de invariante*
(BL-16): mantener el techo I-2 totalmente independiente de si la malla se forma no es
meramente diseñable, está forzado, y es la misma disciplina que la Parte 4 aplica a los
transportes. Estas tres son sólidas.

**Pero la buena idea es una idea de *disponibilidad*, y debe venderse como nada más.** La
dispersión por pasarelas independientes hace poco por el *quién* o el *dónde* en el modelo de
amenazas de apagón caliente, porque dos residuos y una fuga de identidad la socavan como
mecanismo de anonimato: no puedes verificar la independencia de las pasarelas en un apagón
(BL-6), el emisor es localizable físicamente (BL-18), y la capa de radio porta una identidad
que el overlay no puede rotar (BL-18a). Lo que la dispersión *sí* entrega, y entrega
genuinamente, es disponibilidad: el fallo, el bloqueo o la captura sybil de ninguna pasarela
única mata la entrega, y eso se sostiene incluso cuando toda propiedad de anonimato ha
colapsado. Este es exactamente el veredicto CT-15 para los transportes multicobertura
—disponibilidad sí, camuflaje no— y la parte lo fija ahí (BL-16). Vendida como anonimato
sería una sobreafirmación; vendida como disponibilidad es una propiedad real, no vacua.

**Lo que es solo parcial.** El problema de la pasarela sybil / eclipse físico (BL-14). La
mezcla de origen en la capa de radio más la dispersión por pasarelas independientes eleva el
costo de un eclipse sybil; no lo elimina. Una coalición de pasarelas que controle `k` de las
salidas alcanzables en una pequeña malla de vecindario eclipsa a un remitente exactamente
como lo hace una coalición de relés en el overlay —OP-1 y OP-2 recurriendo en espacio de
radio, no una defensa nueva. "Parcial" es la palabra correcta.

**Lo que no está resuelto —declarado a plena fuerza, tres residuos.**

*Primero, la verificación de independencia de pasarelas (BL-6, BL-21).* No puedes verificar a
partir de nada que una pasarela autodeclare que dos pasarelas son independientes, y dentro de
un apagón es peor que en el overlay: el mapa de AS (Parte 8) que permitiría a un cliente
*inferir* independencia a partir de datos no autodeclarados es él mismo a menudo inalcanzable
—la única herramienta que desaparece exactamente cuando se la necesita, así que la estimación
puede estar casi vacía en un apagón profundo (BL-5 degrada a BL-7 por defecto). Esto no es un
huérfano de la Parte 5: el modelo de amenazas lo nombra como una cara del problema recurrente
más profundo del proyecto —verificar la independencia de una parte sin confiar en su
autodeclaración— compartido con los relés (OP-1), los firmantes de releases (OP-8), y los
autores de dependencias (OP-2/RB). La respuesta honesta es la misma que allí: un *residuo
acotado y declarado* que alimenta una *estimación* de confianza con un error adjunto (al
estilo ID-12), no una comprobación criptográfica. La Parte 5 no llega a ser donde esto se
resuelve finalmente.

*Segundo, e irreduciblemente, la localizabilidad física (BL-18).* Un nodo de malla en un
apagón caliente es un transmisor de radio en un lugar físico, y **ningún overlay oculta un
emisor de radio a un adversario con un radiogoniómetro.** Esto es categóricamente más difícil
que cualquier otra cosa de la especificación, porque toda otra amenaza en ScrambNet es un
adversario *remoto* razonando sobre bytes, y esta es un adversario *local* con una antena
—presente precisamente porque impuso el apagón. Todo el edificio criptográfico opera sobre
*lo que los bytes revelan*; la localizabilidad no trata de los bytes en absoluto, es el hecho
electromagnético de la transmisión. La parte no debe prometer que la malla preserva el
anonimato, y no lo hace.

*Tercero —la fuga que el overlay trabaja más duro por prevenir y que la radio deshace
(BL-18a).* La localizabilidad es *dónde estás*; la identidad es *quién eres*, y la capa de
radio filtra ambas. Una radio Wi-Fi/802.11s emite identificadores persistentes de capa 2 que
el overlay de ScrambNet nunca toca —una dirección MAC (y el peering 802.11s puede requerir
una estable), IDs de servicio y dispositivo de Wi-Fi Direct/Aware, huellas de probe-request
y, frente a un adversario capaz, una *huella RF de hardware* (imperfecciones del oscilador)
que sobrevive por completo a la aleatorización de MAC. Así que toda la historia del overlay
—rotar `id`, `box_id` por época, tarjetas por relación (RZ-2), inenlazabilidad de partes
SP-7— se asienta *encima* de un seudónimo de capa 2 que un sniffer local lee directamente, y
la rotación del overlay no puede rotarlo. Y la *topología misma de la malla* es un mapa RF
observable: quién retransmite a quién es visible en el aire incluso bajo tramas uniformes.
Este es el único residuo que el primer borrador de esta parte omitió; se nombra aquí a plena
fuerza porque es posiblemente peor que la localizabilidad —no solo eres hallable mientras
transmites, sino que portas un seudónimo de radio estable cada vez que te unes.

**¿Puede la malla preservar los invariantes que hereda? Parcialmente, y he aquí el libro
mayor honesto.** **I-2 (techo del contenido):** preservado limpiamente —el techo nunca
cabalgó la malla más de lo que cabalgó el transporte (BL-16); esta es la afirmación más
fuerte y verdadera que hace la parte. **I-4 (uniformidad de cable) y SP-7 (inenlazabilidad de
partes):** preservados **solo en la capa de bytes** —una trama uniforme sigue siendo una
emisión detectable (BL-18), y dos partes de un mensaje emitidas desde el *mismo dispositivo
físico en la misma ventana* están correlacionadas por radiogoniometría y tiempos (la radio
reenlaza lo que el overlay desenlaza); la parte NO DEBE (MUST NOT) afirmar que la
inenlazabilidad de bytes heredada sobrevive a la capa de RF. **I-3 (ningún punto único):**
*extendido*, como una propiedad de disponibilidad de mejor esfuerzo, mediante la dispersión
por pasarelas independientes (BL-5) —pero solo en la medida en que la estimación de BL-6 sea
fiable, que es el residuo no resuelto. Así que: I-2 preservado, I-4/SP-7
preservados-solo-sobre-los-bytes, I-3 extendido-pero-estimado. Ese es el libro mayor, y es
antitriunfal a propósito.

**Coherencia con CT-18a.** La Parte 4 concedió que en un cierre total sin vecino de malla, la
entrega es cero y el techo está intacto-e-inútil. La Parte 5 es el peldaño *por debajo* de esa
concesión —lo que haces *cuando sí hay* un vecino— y no la revierte. Extiende la
alcanzabilidad una capa más abajo; no hace la entrega garantizada (BL-17). La afirmación
honesta no es "la comunicación siempre pasa por la malla" —es: *cuando existen un vecino de
malla y una pasarela, un mensaje puede cruzar la ciudad a la velocidad de un autobús; cuando
no existe ninguno, el secreto se queda en casa, sin entregar y sin exponer; y en cualquier
caso, transmitir en la malla es un acto localizable físicamente e identificable por radio que
el overlay no puede ocultar.*

Este es un ítem XL / de riesgo de investigación, y devuelve, en la medida en que el roadmap
lo permite, un resultado *parcial*: un modelo sólido de red mixta y una idea genuina de
disponibilidad, alrededor de residuos (independencia de pasarelas, localizabilidad física,
identidad de radio) nombrados a plena fuerza y no afirmados como cerrados.

## 4. Los dos veredictos razonados

**(a) ¿Sobrevive el paquete Sphinx de 2048 bytes a un store-and-forward de horas, o necesita
el apagón su propio encuadre? → Necesita su propio encuadre (BL-11, BL-12).** El paquete está
bien en *bytes* pero falla en *validez y función* por tres cuentas independientes: (1) su
seguridad por salto se vincula a una época `onion` de ≤7 días (CH-5), que un acarreo de días
puede sobrevivir, llegando a una clave rotada y puesta a cero; (2) SP-5/SP-7b requieren un
estado de replay por época que sobreviva a los reinicios, y los nodos de radio intermitentes
pierden energía y cachés exactamente a lo largo del horizonte de horas; (3) el diseño fijo de
2048 bytes (SP-3) no tiene campo de sobra para el TTL, la fragmentación y la señalización de
custodia que los enlaces intermitentes necesitan, y no puede hacer crecer uno en claro (I-4).
La resolución limpia es un bundle exterior al estilo DTN que envuelve el paquete interior sin
cambiarlo (BL-12/BL-13), con el residuo de anidamiento declarado de CT-6a. Este es un
veredicto de hombre de paja, revocado solo cerrando BL-11.

**(b) ¿Puede verificarse la independencia de pasarelas en la capa de radio? → No; es un
residuo declarado que alimenta una estimación de confianza acotada (BL-6, BL-21).**
"Independiente" tendría que establecerse sin confiar en lo que la pasarela dice (GR-3, en
espacio de radio), y toda señal disponible es débil o ha desaparecido: ASes de enlace
ascendente distintos necesitan el mapa de la Parte 8, *inalcanzable dentro del mismo apagón
donde la independencia importa más*; la dirección física distinta es falsificable y burda; el
próximo salto de radio distinto prueba topología, no independencia de salida. No hay
comprobación criptográfica de que dos pasarelas tengan enlaces ascendentes independientes —el
mismo muro con el que OP-1 choca para la disyunción de relés y OP-8 para la jurisdicción del
firmante. Así que la arquitectura honesta es idéntica a la del mapa de AS (ID-12): no afirmar
verificación, producir una estimación de confianza acotada a partir de observables no
autodeclarados (que puede estar casi vacía en un apagón profundo), adjuntar la incertidumbre,
exponerla (BL-19), y dejar que la dispersión (BL-5) y el reparto en el tiempo (BL-7) acoten
—no eliminen— el daño cuando la estimación esté equivocada.

## 5. Las guardas de invariante y de honestidad

- **BL-16 (el techo es independiente del éxito de la malla —el análogo de CT-16). [normativo]**
  Ninguna garantía de confidencialidad o dispersión (I-2) DEBE (MUST) depender de que la
  malla se forme, de que una pasarela sea alcanzable, de que las pasarelas sean genuinamente
  independientes (BL-6), ni de que el sobre de apagón se entregue. La malla compra
  **alcanzabilidad solamente** —la misma palabra que la Parte 4 usa para los transportes. Un
  diseño en el que perder la malla pierde el techo es no conforme.
- **BL-17 (coherencia con CT-18a: el fondo sigue siendo un fondo, tres estados). [normativo]**
  La Parte 5 extiende la alcanzabilidad un peldaño por debajo de CT-18a y NO DEBE (MUST NOT)
  redactarse de modo que lo contradiga. Los tres estados, todos explícitos: (1) **ningún
  vecino en alcance** → CT-18a, entrega cero, techo intacto-e-inútil; (2) **vecino(s) en
  alcance pero ninguna pasarela alcanzable en ningún punto de la malla** → *también* entrega
  cero, alcanzada vía la malla en lugar de directamente —el store-and-forward PUEDE (MAY)
  retener partes contra una pasarela *futura* dentro del TTL de BL-12, pero esto NO DEBE (MUST
  NOT) presentarse como entrega; (3) **≥1 pasarela alcanzable** → dispersión BL-5/BL-7 o
  degradación. El estado (2) colapsa al mismo resultado que el (1); solo difiere la ruta. La
  Parte 5 hace la entrega *posible* una capa más abajo, nunca *probable* y nunca
  *garantizada*.
- **BL-18 (residuo de localizabilidad física —enunciado a plena fuerza, nunca resuelto).
  [normativo, declara-residuo]** Un nodo de malla que transmite en un apagón caliente es un
  **acto localizable físicamente**: un emisor de radio en un lugar, en el momento exacto en
  que el adversario local que impuso el apagón es más agresivo y más dispuesto a usar
  radiogoniometría y tácticas al estilo de IMSI-catcher. **Ningún overlay, mezcla, dispersión
  ni encuadre de esta especificación oculta esto, y esta parte NO DEBE (MUST NOT) afirmar ni
  dar a entender que lo hace.** Es la razón por la que la participación en la malla DEBE
  (MUST) ser un opt-in explícito, informado y por contexto (BL-3), y la razón por la que la
  afirmación honesta de esta parte es estrecha (§3).
- **BL-18a (residuo de identidad de capa de radio —declarado, no resuelto). [normativo,
  declara-residuo]** La participación en la malla expone identificadores persistentes de capa
  2 que el overlay no puede rotar: una dirección MAC (el peering 802.11s puede requerir una
  estable), IDs de dispositivo y servicio de Wi-Fi Direct/Aware, huellas de probe-request y
  —frente a un adversario capaz— una *huella RF de hardware* que sobrevive a la aleatorización
  de MAC. Cada uno es un seudónimo estable para el *dispositivo*, independiente de toda
  rotación del overlay (`id`, `box_id`, tarjetas RZ-2, SP-7). La aleatorización de MAC ayuda
  contra la primera clase y nada contra el fingerprinting de RF. La *topología* de la malla es
  igualmente un mapa RF observable —quién retransmite a quién es visible en el aire incluso
  bajo tramas uniformes. La parte NO DEBE (MUST NOT) dar a entender que la inenlazabilidad del
  overlay se extiende al emisor de radio. Esta es la segunda cara, junto a la independencia de
  pasarelas (BL-21), del problema recurrente de identidad/independencia en espacio de radio,
  declarado y no cerrado.
- **BL-19 (expón la postura de la malla honestamente —el análogo de CT-19). [normativo]** Un
  cliente conforme DEBE (MUST) exponer, en la superficie de honestidad existente (PS-9/CT-19):
  que un enlace de radio está en uso; que este enlace es *localizable físicamente* (BL-18)
  **e identificable por radio** (BL-18a); si su salida de pasarela es única o
  plural-e-independiente-*estimada* (BL-6/BL-7); y que la alcanzabilidad de la malla —a
  diferencia del techo I-2— no porta **ninguna** garantía y puede ser cero. El mensaje que la
  interfaz enuncia: *tu techo del contenido se sostiene; en la malla puedes ser localizado y
  tu dispositivo reconocido en el aire allí donde estás parado.*
- **BL-20 (pila concreta dejada abierta; afirmaciones acotadas por lo que se ejecuta).
  [normativo]** La Parte 5 **no** obliga a una pila de radio específica, método de enrutamiento
  (BL-9), dimensionamiento de TTL/fragmento (BL-12), ni presupuesto de batería (BL-4); estos
  son hombres de paja y decisiones del dueño. Un cliente con una pila de malla no especificada
  NO DEBE (MUST NOT) afirmar ninguna propiedad de disponibilidad de malla *cuantitativa*;
  PUEDE (MAY) afirmar solo la *cualitativa* "un nodo que pierde el enlace ascendente puede dar
  un salto más hacia una pasarela vecina, y las partes DEBERÍAN (SHOULD) salir por pasarelas
  independientes-estimadas", y solo donde realmente ejecuta ≥2 pasarelas
  independientes-estimadas con `k < n`.
- **BL-21 (el problema recurrente de independencia se declara, no se cierra). [normativo,
  declara-residuo]** Verificar la independencia de pasarelas sin un mapa alcanzable y con la
  ubicación autodeclarada (BL-6) es el **mismo problema que aparece para los relés (OP-1), los
  firmantes de releases (OP-8), y los autores de dependencias (OP-2/RB)** —verificar la
  independencia de una parte sin confiar en su autodeclaración— ahora llevando su máscara de
  capa de radio dentro de un apagón, donde el mapa de AS (Parte 8) es él mismo inalcanzable.
  La Parte 5 **no** lo resuelve; lo reduce a ese residuo recurrente declarado y alimenta una
  estimación de confianza acotada, exactamente como el mapa alimenta una con una tasa de error
  declarada (ID-12).

## 6. Requisitos introducidos aquí

- **BL-1 / BL-2 / BL-3 / BL-4** — la malla es una capa, no un modo; roles derivados de la
  capacidad y variables en el tiempo; opt-in explícito por contexto antes de cualquier enlace
  de radio; un presupuesto honesto de batería/almacenamiento.
- **BL-5 / BL-6 / BL-7** — dispersión por pasarelas independientes como disponibilidad;
  "independiente" es una estimación de confianza acotada, nunca autodeclarada y casi vacía en
  un apagón profundo; demasiado pocas/cero pasarelas degradan, nunca fallan en abierto.
- **BL-8 / BL-9 / BL-10** — los nombres sobreviven, las rutas no; próximo salto sin un DHT y
  sus costos; la entrega sigue corriendo a través de los buzones de la Parte 6, nunca a un
  dispositivo nombrado, y el caso todo-local se atiende con un buzón alcanzable por la malla.
- **BL-11 / BL-12 / BL-13** — la validez de Sphinx (no los bytes) acota el acarreo largo; el
  apagón necesita su propio sobre al estilo DTN; el sobre no debe ser un selector y hereda el
  residuo de anidamiento de CT-6a.
- **BL-14 / BL-15** — la pasarela sybil es un eclipse físico, respondido solo parcialmente; la
  mezcla de origen de radio es una medida de disponibilidad/anti-eclipse, **no** GR-8 y **no**
  ocultación del origen.
- **BL-16 / BL-17** — el techo es independiente de la malla; coherencia con CT-18a, los tres
  estados de entrega, el fondo sigue siendo un fondo.
- **BL-18 / BL-18a / BL-19** — localizabilidad física e identidad de radio, ambas declaradas a
  plena fuerza y nunca resueltas; postura de malla honesta en PS-9.
- **BL-20 / BL-21** — pila concreta dejada abierta; el problema recurrente de independencia
  declarado, no cerrado.

BL-16 y BL-18/BL-18a son los tres portantes: el techo no depende de la malla, y la malla no
puede ocultar que estás transmitiendo ni que tu dispositivo es reconocible en el aire. La
afirmación honesta es estrecha y con forma de disponibilidad: *la malla extiende la
alcanzabilidad un peldaño por debajo de un cierre y mantiene el techo del contenido que
hereda, pero no oculta al emisor, al dispositivo ni la topología, y no garantiza la entrega.*
Rompe esta parte nombrando un anonimato a nivel de malla que las cláusulas prometan más allá
de BL-18/BL-18a, un lugar donde se haga que el techo I-2 dependa del éxito de la malla más
allá de BL-16, una forma en que BL-17 se lea como que eleva "posible" a "probable", o una
fuga de capa de radio que BL-18/BL-18a omitan. Esa es la invitación, en la voz de la casa —y
en esta parte especialmente, la respuesta honesta a "¿resuelve el apagón?" es "en parte, y
aquí está exactamente dónde no lo hace".
