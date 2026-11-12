# Especificación de ScrambNet — Parte 4: Transportes camaleón
> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../../en/spec/04-chameleon-transports.md)).

**Estado: BORRADOR (DRAFT), y la parte con más probabilidad de pudrirse.** Esta parte
enuncia un modelo de amenazas del transporte y una evaluación honesta de realismo. No
compromete ningún mecanismo exterior y no promete ninguna victoria en la carrera
armamentística de la censura. Lee primero el §1 y la evaluación de realismo (§8): entre
ambos dicen la única cosa estrecha que esta parte está dispuesta a afirmar, y la cosa mucho
mayor que rechaza. Los valores de hombre de paja se marcan con `(s)`.

Las capas de arquitectura L1 (camaleón) y L3 (transportes efímeros) viven aquí; el
transporte es la cosa que lleva los bytes de una parte más allá de un censor. Esta parte se
archiva bajo OP-7 (alcanzabilidad y arranque), y depende —en lugar de resolver— del problema
de arranque sin contacto (OP-7, GR-10).

## 1. La decisión, en dos frases

- **Esta parte no afirma que ScrambNet gane ni sostenga la carrera armamentística de la
  censura.** Afirma lo contrario acerca de su propia importancia: el techo de confidencialidad
  y dispersión (I-2) **no** depende en absoluto de la capa de transporte. Un transporte compra
  *alcanzabilidad* —la capacidad de llevar los bytes de una parte a un relé— y a la
  alcanzabilidad se le permite fallar, bajando por la escalera de degradación de la
  arquitectura (L1→L2→L3→L4) y, en un apagón total sin vecino de malla, hasta cero, **sin que
  el techo del contenido se mueva jamás** (CT-16).
- **La afirmación honesta y defendible es por tanto estrecha y no debe ensancharse:** *no
  hacemos imposible perder la carrera del transporte; hacemos que perderla sea no catastrófico
  para la confidencialidad.* Un censor puede cortar la alcanzabilidad a cero; un censor sigue
  sin poder leer el contenido por debajo de `k` partes, porque esa protección nunca viajó sobre
  el transporte (CT-16, CT-18, CT-18a).

Todo lo que sigue es el modelo de amenazas que justifica esta afirmación estrecha y la
evaluación de realismo (§8) que es su columna vertebral —la sección más importante de la parte,
no un apéndice.

## 2. El modelo de amenazas del transporte (lo que el censor de 2026 hace realmente)

- **CT-1 (declara lo que resistes; el silencio es una concesión). [normativo]** Una
  descripción de transporte conforme DEBE (MUST) enunciar cuáles de las capacidades de
  adversario CT-2…CT-7a afirma resistir y cuáles concede. Una capacidad no declarada se trata
  como concedida (la regla de completitud I-1, para transportes) —un transporte que no nombra un
  ataque no se ha defendido de él.
- **CT-2 (DPI pasivo / fingerprinting de protocolo).** El censor clasifica flujos por firmas de
  byte y de estructura sin leer el contenido; el trabajo del camaleón es no presentar ninguna
  firma distintiva propia (CT-8).
- **CT-3 (cotejo de huella TLS). [normativo]** El censor saca la huella del ClientHello TLS. La
  línea base de 2026 es **JA4 / JA4+** (FoxIO), no el retirado JA3: JA4 **ordena** las suites de
  cifrado y las extensiones antes de hashear e ignora GREASE, así que es robusto frente a la
  *aleatorización* del orden de extensiones que los navegadores de uso general ahora hacen. Una
  imitación conforme DEBE (MUST) por tanto coincidir con el *conjunto* de suites de cifrado del
  objetivo, el *conjunto* de extensiones, ALPN, supported-versions y el *patrón* de GREASE —no
  meramente con su orden, que JA4 ya no distingue. (Una imitación que solo aleatoriza el orden no
  está por ello oculta.)
- **CT-4 (inspección de SNI / ECH).** El censor lee el SNI en claro para aprender el nombre de
  destino. ECH puede ocultarlo, pero solo condicionalmente (CT-11).
- **CT-5 (sondeo activo / conexión de vuelta).** El censor se conecta a un extremo sospechoso y
  comprueba si se comporta como lo que dice ser; la supervivencia requiere CT-10.
- **CT-6 (clasificación estadística pasiva de la forma del flujo). [normativo,
  declara-residuo]** El censor clasifica flujos por *estadísticas*, no por bytes: tiempos,
  volumen, dirección, estructura de ráfagas, **y entropía** —y el conjunto de características es
  abierto y lo elige el adversario, incluidos clasificadores aprendidos (ML). En particular, la
  **detección de "tráfico totalmente cifrado" de alta entropía** bloquea flujos que parecen
  *demasiado aleatorios* sin sondeo y sin coincidencia de huella (observado en el GFW desde
  finales de 2021). Esto tiene una consecuencia contraintuitiva de la que depende el resto de la
  parte: **la cobertura aleatorizada o de alta entropía es una señal *más brillante*, no más
  tenue** —la cobertura más segura se parece a un protocolo real muy común, nunca a ruido. CT-6
  no puede cerrarse con mimetismo a nivel de byte (CT-8); sus respuestas honestas están en otras
  capas (CT-12, CT-15).
- **CT-6a (detección de TLS-en-TLS / cifrado anidado). [normativo, declara-residuo]** Un
  transporte que tuneliza el propio tráfico de partes ya cifrado y uniforme por I-4 de ScrambNet
  *dentro* de un flujo TLS externo imitado deja patrones característicos de tamaño de registro y
  de tiempos —un flujo TLS que *lleva otro handshake TLS*— que el DPI puede marcar aun cuando el
  handshake externo sea perfecto a nivel de byte (limpio en CT-3/CT-4). Este es el ataque
  estelar contra la evasión anidada y DEBE (MUST) declararse: una imitación puede ser perfecta en
  el handshake y aun así ser atrapada en la estructura del flujo. Es un residuo que el mimetismo
  de bytes no puede cerrar (pertenece a CT-12); nombrarlo lo exige CT-1.
- **CT-7 (enumeración de extremos —bloquear lo que se conoce). [normativo]** El censor descubre y
  bloquea extremos/puentes conocidos al por mayor. La dispersión (CT-15) y la distribución de
  puentes por grafo social (arquitectura L2, Lox) elevan el costo; el mimetismo no aborda la
  enumeración en absoluto.
- **CT-7a (descubrimiento de extremos —la línea del frente del arranque, declarada abierta).**
  Distinto de CT-7: *cómo un usuario censurado obtiene en primer lugar un extremo no bloqueado,
  más rápido de lo que el censor lo enumera.* Este es el problema de distribución de puentes
  (Lox / grafo social) y se reduce a **OP-7 (arranque sin contacto), que está abierto.** La
  Parte 4 no lo resuelve; lo cruza por referencia (GR-10, OP-7), y cualquier afirmación de que
  los extremos son descubribles de forma fiable es una promesa sin respaldo que esta parte se
  niega a hacer.
- **CT-7b (lista blanca de protocolos —el caso límite).** El censor permite solo una lista de
  permitidos de protocolos/destinos y descarta el resto (observado: la lista blanca de la red
  nacional de Irán, 2025–2026). Contra esto, la imitación de un destino *permitido* es la única
  jugada, e incluso ella falla cuando el censor acepta el costo colateral (§8, CT-14) —hasta un
  apagón total, donde ningún transporte alcanza nada (CT-18a).

## 3. Disciplina de imitación (la cinta sin fin, hecha normativa)

- **CT-8 (ninguna firma estática de proyecto; imita tal como está desplegado). [normativo]** Un
  transporte camaleón NO DEBE (MUST NOT) presentar una firma de cable estática y específica del
  proyecto, y DEBE (MUST) imitar un protocolo objetivo *tal como está realmente desplegado*, no
  uno idealizado. Una pila hecha a mano o congelada es ella misma una huella y es no conforme.
- **CT-9 (la cláusula de deriva de uTLS). [normativo]** Una imitación al estilo uTLS DEBE (MUST)
  seguir el ClientHello *actualmente desplegado* del objetivo y DEBE (MUST) declarar la versión
  del objetivo que imita (CT-20). Frente a JA4 (CT-3) el distinguidor es la divergencia en los
  *conjuntos* de cifrado y de extensiones, ALPN, supported-versions y el patrón de GREASE —estos
  derivan con cada versión del navegador, así que una imitación congelada en la versión N se
  convierte en un distinguidor una vez que la población real se mueve a N+1. Esta es una **cinta
  sin fin de mantenimiento sin estado terminal**: no hay versión en la que el trabajo esté hecho
  (§8). El techo NO DEBE (MUST NOT) depender de mantenerle el paso (CT-16).
- **CT-9a (prefiere un objetivo de alta población —por razones de conjunto de anonimato, no
  económicas). [normativo]** Un despliegue conforme DEBERÍA (SHOULD) imitar un objetivo de alta
  población y rápido movimiento (el TLS de un navegador de uso general) en lugar de uno de nicho,
  por dos razones *mecánicas*: la gran manada es un mejor conjunto de anonimato (más flujos reales
  entre los que esconderse), y un objetivo de parcheo rápido acorta la ventana de obsolescencia de
  CT-9. Esta cláusula **no** hace ninguna afirmación económica de que la manada sea "demasiado cara
  de bloquear" —esa apuesta es CT-13, declarada refutable, y el registro de 2026 (un censor nacional
  bloqueó la mayor manada de ECH, §8) muestra que puede perderse.

## 4. Supervivencia al sondeo activo

- **CT-10 (sobrevive a un sondeo de conexión de vuelta; el silencio es en sí mismo una huella).
  [normativo]** Un extremo camaleón DEBE (MUST) sobrevivir a un sondeo activo: DEBE (MUST)
  completar un handshake *real* y válido del protocolo que imita y servir un comportamiento de
  cobertura plausible a un sondeador no autenticado (p. ej. una terminación TLS real que
  proxea hacia contenido de apariencia real), revelando el servicio encubierto solo a un cliente
  que prueba un secreto precompartido. El modelo moderno es terminar-TLS-real-y-proxear-a-un-
  sitio-real, **no** el modelo más antiguo de quedarse-en-silencio: *quedarse en silencio ante un
  sondeador no autenticado es en sí mismo un comportamiento detectable* (timeouts característicos,
  umbrales de aceptación de bytes, manejo de reenvíos) y es no conforme.
- **CT-10a (el secreto precompartido es una línea de puente —su distribución está abierta).
  [normativo]** El secreto que distingue a un cliente real de un sondeador en CT-10 es una **línea
  de puente**, y **su distribución es OP-7 / GR-10, declarada abierta.** CT-10 supone un secreto ya
  entregado; **no** resuelve la entrega. La resistencia al sondeo y el arranque son problemas
  separados, y confundirlos (suponer que el secreto está ya de algún modo en todas partes) es el
  error que CT-7a prohíbe.
- **CT-10b (el costo adelgaza el fondo de operadores).** El contenido de cobertura real, los
  certificados reales y la terminación real son una carga operativa permanente por extremo. Elevar
  ese listón es exactamente lo que encoge el fondo de operadores voluntarios —que es el problema de
  mantenimiento sostenido (§8) con sombrero operativo.

## 5. Postura sobre ECH (sin sobreafirmación)

- **CT-11 (ECH es oportunista y acotado por disponibilidad, nunca un techo). [normativo]** Una
  descripción conforme NO DEBE (MUST NOT) presentar ECH (Encrypted Client Hello) como una defensa
  del SNI resuelta. Enuncia: (a) ECH oculta el SNI solo donde el proveedor de fronting lo despliega,
  el cliente lo soporta, **y la consulta de DNS cifrado que lleva la configuración de ECH tiene
  éxito** —bloquea o degrada ese DNS y ECH silenciosamente no se activa, que es el modo de fallo
  real de 2026; (b) el despliegue del lado del servidor en 2026 es una porción *minoritaria pero
  creciente*, concentrada en unos pocos grandes proveedores de fronting, no en la larga cola, así
  que "el SNI está oculto" es falso para la mayoría de los destinos la mayor parte del tiempo; (c)
  **"bloquear ECH por completo" es una respuesta de censor observada** (un censor nacional
  bloqueando conexiones ECH a un proveedor importante desde finales de 2024), que ECH por
  construcción no puede contrarrestar. ECH es una mejora oportunista, no una garantía. *(La
  especificación de ECH es el trabajo de ESNI/ECH del grupo de trabajo TLS del IETF; esta parte no
  fija ningún número de RFC publicado, que aún no estaba confirmado en el momento de redactar —cita
  el documento actual, no un número que puede estar equivocado.)*
- **CT-11a (degrada, no filtres). [normativo]** Donde ECH no esté disponible o esté bloqueado, un
  transporte conforme DEBE (MUST) degradar al siguiente peldaño de la escalera (puentes efímeros L2)
  en lugar de recaer en un flujo distinguible de SNI en claro. La ruta de degradación, no ECH, es la
  garantía.

## 6. El residuo de correlación de flujo

- **CT-12 (el mimetismo no puede vencer la forma del flujo; dilo). [normativo, declara-residuo]**
  NO DEBE (MUST NOT) afirmarse que el mimetismo a nivel de byte vence la correlación de forma de
  flujo (CT-6), la detección de TLS anidado (CT-6a), ni a un observador pasivo global que
  correlaciona entrada y salida. Los tiempos, el volumen, la dirección, la estructura de ráfagas y
  el anidamiento se filtran a través de una imitación perfecta. Estos son residuos que el mimetismo
  *no puede* cerrar y DEBEN (MUST) declararse, no ocultarse. Las únicas respuestas honestas están en
  otras capas —la dispersión reparte la forma de un mensaje entre coberturas (CT-15, una propiedad de
  *disponibilidad*, no de ocultación de forma) y la mezcla en modo paranoico (arquitectura L2)
  intercambia latencia por resistencia de forma— nunca la imitación misma. Los ataques de oráculo de
  sitio web y de confirmación del lado de entrada se reducen a este mismo residuo de correlación y a
  la fila del adversario global pasivo que el modelo de amenazas ya declara fuera del alcance del modo
  rápido.

## 7. Dispersión de partes sobre coberturas diversas (el veredicto normativo)

- **CT-15 (el veredicto: la diversidad ayuda a la disponibilidad, perjudica la inobservabilidad;
  compra lo primero, paga y declara lo segundo). [normativo]** Llevar las `n` partes de un mensaje
  sobre *distintos tipos de cobertura* (una en TLS, una en WebRTC, una en malla) es una decisión de
  dos caras, resuelta así:
  (a) NO DEBE (MUST NOT) suponerse que mejora la **inobservabilidad** —`n` coberturas son `n`
  huellas que acertar (CT-3), `n` cintas sin fin (CT-9), y un daño genuinamente nuevo: una
  **superficie de correlación entre coberturas**. Un adversario que ve un flujo TLS, un flujo WebRTC
  y una ráfaga de malla que están correlacionados en tiempo/volumen (CT-6) puede enlazarlos como las
  partes de un mismo mensaje *sin romper ninguna imitación individual* —la diversidad no atenúa esa
  señal, puede brillarla más;
  (b) está permitida y valorada **estrictamente como una medida de disponibilidad**: ningún bloqueo
  de una sola cobertura mata la entrega (`k < n` ya compra esto), y la enumeración de extremos (CT-7)
  ahora debe tener éxito contra las coberturas *individualmente* —lo que eleva el costo del censor
  contra un censor que bloquea coberturas *de una en una*, y no proporciona **ningún** beneficio
  contra una lista blanca de protocolos (CT-7b) ni un apagón total (CT-18a), que bloquean todas las
  coberturas en un solo acto.
- **CT-15a (véndelo como alcanzabilidad, nunca como camuflaje). [normativo]** Un cliente conforme
  NO DEBE (MUST NOT) presentar la dispersión multicobertura al usuario como *camuflaje más fuerte*;
  PUEDE (MAY) presentarla como *alcanzabilidad más fuerte*. Confundir ambas es el mismo error de
  categoría enlazabilidad-vs-contenido que ID-12a prohíbe para el mapa, reenunciado para
  transportes: la multicobertura mejora una propiedad de disponibilidad y no mejora una propiedad de
  mimetismo.
- **CT-15b (el conjunto mínimo de coberturas queda abierto; las afirmaciones acotadas por lo que
  realmente se ejecuta). [normativo]** La Parte 4 **no** obliga a un conjunto mínimo de coberturas
  —obligar a `n` coberturas obliga a `n` cintas sin fin de mantenimiento que el proyecto puede no
  ser capaz de dotar de personal (§8). Un cliente con un conjunto de coberturas abierto/no
  especificado NO DEBE (MUST NOT) afirmar ninguna propiedad de disponibilidad *cuantitativa* (ningún
  "resiste la enumeración a través de N coberturas" sin una N enunciada y realmente ejecutada);
  PUEDE (MAY) afirmar solo el *cualitativo* "ningún bloqueo de una sola cobertura mata la entrega", y
  solo cuando realmente ejecuta ≥2 coberturas independientes con `k < n`. Si exigir ≥2 coberturas
  para el valor por defecto de entrega dispersa es una decisión del dueño (§8).

## 8. La evaluación honesta de realismo (la columna vertebral)

*(Esta sección es la parte, no un apéndice. Está escrita en la voz de §residuo de las Partes 8 y
11.)*

**Esta parte no compromete ningún mecanismo exterior y no debe fingir que sí.** Es un veredicto
sobre dónde el proyecto es frágil, enunciado a plena fuerza: **la capa de transporte es la capa más
débil y con más probabilidad de pudrirse del proyecto, y la postura honesta es decirlo y diseñar de
modo que el techo nunca dependa de ella.**

**La cinta sin fin de deriva de uTLS (CT-9).** Una imitación congelada en una versión de navegador
se convierte en un distinguidor en el momento en que la población real avanza —una manada más
pequeña y más obsoleta es una señal *más brillante*, no más tenue. No hay versión en la que el
trabajo esté hecho. Frente a JA4 el orden ya no importa, pero los *conjuntos* de cifrado/extensiones
aún derivan con cada versión, así que la cinta sin fin es más lenta de lo que era frente a JA3 pero no
se detiene. El proyecto no llega a ganar esto; llega a correr sobre ella o a bajarse de ella, y CT-16
es la decisión de hacer sobrevivible el bajarse.

**La realidad de ECH en 2026 (CT-11).** ECH oculta el SNI solo donde el proveedor, el cliente *y la
consulta de DNS cifrado* tienen éxito todos, y en 2026 eso es una minoría de destinos. "Bloquear ECH
por completo" ya ha sido usado por un censor nacional contra el mayor proveedor de fronting, lo cual
ECH no puede contrarrestar. ECH es una mejora oportunista acotada por el despliegue; el techo es la
ruta de degradación, nunca ECH.

**El argumento económico y sus contraejemplos (CT-13/CT-14).** "Bloquearme cuesta más de lo que
rinde" es un disuasivo real y una garantía falsa. El registro de 2026 ha repetido contraejemplos de
censores pagando grandes costos colaterales antes que permitir la evasión: un regulador nacional
bloqueando ECH a un proveedor importante (desde finales de 2024); una **lista blanca de protocolos**
de red nacional permitiendo solo una lista de permitidos corta (Irán, 2025–2026); y **apagones
totales de internet** durante disturbios (Irán, mediados de 2025 y de nuevo a principios de 2026).
Cada uno es un censor eligiendo el control sobre el comercio. La apuesta económica es probabilística:
funciona contra un censor que valora el costo colateral y falla contra uno que ha mostrado que no lo
hará. Enunciamos esto en lugar de agitar las manos sobre la economía como asunto resuelto. *(Estos se
citan como categorías de comportamiento observado; una redacción conforme debería adjuntar fechas y
jurisdicciones y DEBE (MUST) descartar cualquier contraejemplo que no pueda respaldar —un contraejemplo
equivocado es peor que ninguno, CT-14.)*

**La pregunta incómoda, respondida (el residuo declarado central).** *¿Tiene un proyecto voluntario
seudónimo la capacidad de mantenimiento sostenido que una carrera armamentística de transporte exige?*
Tor tiene personal remunerado, un ecosistema financiado de transportes conectables y años de memoria
institucional, y *aun así* pierde rondas frente a censores decididos. Un proyecto seudónimo, sin lista
—uno que por diseño (I-3, y la gobernanza de las Partes 10/11) rechaza la coordinación central que le
permitiría empujar una actualización de transporte a todos a la vez— tiene **menos** de esa capacidad,
no más. La respuesta honesta es por tanto **no, no de forma fiable.** La carrera armamentística de
transporte recompensa exactamente el mantenimiento financiado, coordinado y ligado a identidad al que
el proyecto ha renunciado por razones de principio. Deberíamos esperar que la capa de mimetismo se
quede atrás.

**Y por eso nada portante se apoya en ella.** La capacidad de mantenimiento para ganar una carrera
armamentística de transporte es exactamente lo que no tenemos y exactamente lo que el techo no
requiere. Esperamos que la capa de mimetismo se quede atrás; la arquitectura es una apuesta a que
puede —la misma apuesta que la arquitectura ya hace por el cinturón de cebolla ("si toda esta capa
computacional cae algún día, la red no se vuelve legible —se vuelve menos conveniente") y que las
Partes 10/11 hacen por las actualizaciones (rechaza el push, paga la latencia, enúncialo). Esto es
pesimismo honesto sobre una capacidad que nos falta, convertido en la justificación de diseño que hace
el déficit no catastrófico —no derrotismo.

**El fondo de la escalera, concedido (CT-18a).** La escalera de degradación L1→L2→L3→L4 tiene un
fondo, y el fondo tiene un fondo. En un **apagón total sin vecino físico de malla al alcance**, ningún
transporte alcanza nada y **ningún mensaje se entrega —punto final.** No hacemos *eso* sobrevivible. El
techo del contenido I-2 sigue sosteniéndose (nada se *revela*; lo que no puede enviarse no puede
leerse), pero la alcanzabilidad es cero, y el techo en ese punto está *intacto e inútil*:
confidencialidad perfecta de un mensaje que no puede salir del dispositivo. La afirmación honesta no es
"la comunicación siempre pasa" —es "la confidencialidad nunca depende del transporte, y cuando el
transporte muere el secreto muere con él sin entregar, no expuesto." Un nodo de malla en un apagón
caliente es en sí mismo un acto físicamente localizable (Parte 5, OP-6), así que incluso el último
peldaño es un opt-in explícito y peligroso, no una garantía.

## 9. La guarda de invariante

- **CT-16 (el techo no depende de ganar la carrera; confidencialidad ≠ disponibilidad).
  [normativo]** Ninguna garantía de confidencialidad o dispersión (I-2) DEBE (MUST) depender de que
  ningún transporte camaleón tenga éxito, de que una imitación se mantenga actual (CT-9), de que ECH
  esté disponible (CT-11), ni de que el argumento económico se sostenga (CT-14). Los transportes
  compran **alcanzabilidad solamente**. I-2 garantiza **confidencialidad** (el contenido por debajo
  de `k` es ilegible), una propiedad de *entregado-vs-no-entregado* que calla sobre si algo se
  entrega —**no** una garantía de legible-vs-ilegible de la entrega. El fallo del transporte DEBE
  (MUST) degradar bajando por la escalera (L1→L2→L3→L4), y en el fondo hasta alcanzabilidad cero
  (CT-18a), **nunca** comprometiendo el contenido por debajo de `k`. Un diseño en el que perder la
  carrera del transporte pierde el techo es no conforme.
- **CT-17 (minimiza la dependencia; no prometas ganar). [normativo]** Una postura conforme DEBE
  (MUST) minimizar la dependencia del techo respecto del mimetismo en lugar de prometer sostenerlo.
  Donde el mimetismo y la degradación respondan ambos a una amenaza, la parte DEBE (MUST) preferir la
  ruta de degradación como la garantía y tratar la imitación como la conveniencia (la propia máxima de
  la arquitectura: todo lo que puede expirar es una conveniencia).
- **CT-18 (el techo declarado: ninguna afirmación de victoria en la carrera armamentística).
  [normativo]** La Parte 4 NO DEBE (MUST NOT) afirmar que ScrambNet gana ni sostiene la carrera
  armamentística de la censura. La única afirmación que hace es la de CT-16: a la capa de transporte
  *se le permite perder* sin que el techo pierda. Todo texto, interfaz o README que afirme
  invencibilidad a nivel de transporte, una victoria "sostenible" en la carrera armamentística, o
  ECH-como-resuelto es no conforme y DEBE (MUST) corregirse —incluida la fila de censor nacional del
  modelo de amenazas, que esta parte revisa para separar la *alcanzabilidad* (disputada, puede llegar
  a cero) del *contenido* (protegido incondicionalmente, independiente del transporte).
- **CT-18a (el caso terminal se enuncia, no se oculta). [normativo]** Una redacción conforme DEBE
  (MUST) enunciar el caso terminal de CT-18 explícitamente: en un apagón total sin alcance de malla,
  la alcanzabilidad es cero y ningún mensaje se entrega; el techo del contenido se sostiene pero es
  inútil para ese mensaje no entregado. "Hacemos sobrevivible perder la carrera del transporte *para
  la confidencialidad*, no para la entrega" es la afirmación exacta, y nada puede redactarse para
  implicar que la entrega está garantizada.

## 10. Superficie de honestidad operativa

- **CT-19 (expón la postura del transporte honestamente). [normativo]** Un cliente conforme DEBE
  (MUST) exponer su postura de transporte actual en la superficie de honestidad existente (PS-9): qué
  cobertura está usando, si ECH está *realmente* en efecto (no meramente intentado), y que la
  alcanzabilidad del transporte —a diferencia del techo I-2— no porta **ninguna** garantía y puede
  fallar hasta cero. El mensaje que la interfaz enuncia: *tu techo del contenido se sostiene; tu
  capacidad de alcanzar la red no.*
- **CT-20 (declara la obsolescencia de la imitación). [normativo]** Un despliegue conforme DEBERÍA
  (SHOULD) declarar cuán actual es su objetivo de imitación (CT-9), el análogo de transporte de la
  tasa de error medida del mapa (ID-12), de modo que el usuario y el simulador puedan tratar una
  imitación desactualizada como la huella que es en lugar de confiar silenciosamente en ella.

## 11. Requisitos introducidos aquí

- **CT-1 / CT-2 / CT-3 / CT-4 / CT-5** — declara-lo-que-resistes; DPI pasivo; fingerprinting TLS JA4
  (conjuntos + GREASE, no orden); inspección de SNI/ECH; sondeo activo.
- **CT-6 / CT-6a** — clasificación estadística/de entropía/ML de flujo pasiva (la aleatoriedad es una
  señal más brillante); detección anidada de TLS-en-TLS —ambos residuos que el mimetismo no puede
  cerrar.
- **CT-7 / CT-7a / CT-7b** — enumeración de extremos vs *descubrimiento* de extremos (la línea del
  frente de arranque OP-7, declarada abierta); lista blanca de protocolos.
- **CT-8 / CT-9 / CT-9a** — ninguna firma estática; la cinta sin fin de deriva de uTLS; prefiere un
  objetivo de alta población por razones de conjunto de anonimato, no una promesa económica.
- **CT-10 / CT-10a / CT-10b** — sobrevive a un sondeo con cobertura real (el silencio es una huella);
  el secreto precompartido es una línea de puente cuya distribución es OP-7; el costo adelgaza el
  fondo de operadores.
- **CT-11 / CT-11a** — ECH es oportunista, dependiente del DNS, con bloqueo-de-ECH observado, no un
  techo; degrada en lugar de filtrar SNI en claro.
- **CT-12** — el mimetismo no puede vencer forma-de-flujo/anidamiento/correlación; las respuestas
  están en otras capas, nunca la imitación.
- **CT-15 / CT-15a / CT-15b** — la dispersión multicobertura ayuda a la disponibilidad, perjudica la
  inobservabilidad, añade una superficie de correlación entre coberturas; véndela como alcanzabilidad
  no como camuflaje; afirmaciones acotadas por las coberturas realmente ejecutadas.
- **CT-16 / CT-17 / CT-18 / CT-18a** — el techo nunca depende del transporte; confidencialidad ≠
  disponibilidad; ninguna afirmación de victoria en la carrera armamentística; el caso terminal de
  alcanzabilidad-cero enunciado, no oculto.
- **CT-19 / CT-20** — postura de transporte honesta en PS-9; obsolescencia de imitación declarada.

CT-16 y CT-18 son las dos portantes: el techo no depende de ganar la carrera del transporte, y la
parte no hace ninguna afirmación de que la carrera esté ganada. La capa de transporte es la que el
proyecto espera perder rondas, y está arquitectada de modo que perderlas cueste *alcanzabilidad*,
nunca *confidencialidad* —hasta el caso terminal donde la alcanzabilidad es cero y el secreto no
entregado sigue siendo un secreto (CT-18a). Rompe esta parte nombrando una capacidad de censor que
CT-2…CT-7b omita, una cláusula que prometa ganar o sostener la carrera armamentística más allá de
CT-18, un lugar donde se haga que el techo I-2 dependa de que un transporte tenga éxito, o una forma
en que la dispersión multicobertura se venda como camuflaje más allá de CT-15a. Esa es la invitación,
en la voz de la casa.
