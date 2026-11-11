# Especificación de ScrambNet — Parte 3: Construcción de circuitos y selección de rutas

**Estado: BORRADOR (DRAFT), y la parte menos asentada de la especificación.** Es
el muro portante de la seguridad *operativa* (el contenido garantizado por I-2
se sostiene sin ella, pero la protección frente a la correlación y toda la
historia de los k-caminos viven aquí). Los valores provisionales se marcan con
`(s)`. El problema de la verificación de la disjunción es OP-1 y está
abiertamente sin resolver; esta parte enuncia el objetivo y un primer mecanismo
que atacar.

## 1. Alcance y por qué esto es difícil

La dispersión (Parte 1) hace que el contenido sea incondicionalmente seguro por
debajo de `k` partes capturadas. Esa garantía solo es *operativamente* real si
los `n` circuitos de las partes son genuinamente disjuntos — de lo contrario un
único punto de observación del adversario ve `k` partes y el umbral garantizado,
aunque matemáticamente intacto, nunca se alcanza. Esta parte decide cómo un
cliente, que posee únicamente su propia muestra de gossip verificable (Parte 2)
y ningún mapa de confianza, selecciona `n` circuitos sobre los que un adversario
no pueda apostarse a bajo coste. Todo lo que sigue debe sostenerse frente a
relés que mienten sobre todo salvo lo que sus firmas vinculan (GR-2).

## 2. Objetivos de disjunción

- **PS-1.** Los `n` circuitos de un mensaje DEBEN (MUST) ser *disjuntos por
  nodo*: ningún relé aparece en dos de ellos. Este es el umbral mínimo, siempre
  imponible si la muestra es lo bastante grande.
- **PS-2.** El cliente DEBERÍA (SHOULD) buscar además, en orden decreciente de
  valor y creciente de dificultad: **disjunción por AS** (ninguna pareja de
  circuitos comparte un sistema autónomo en la guardia o en la salida), luego
  **disjunción por jurisdicción** (ninguna pareja comparte una jurisdicción
  legal). Cada nivel que no pueda cumplir DEBE (MUST) comunicarse al usuario, no
  omitirse en silencio (PS-9).
- **PS-3.** Dentro de un mismo circuito, la guardia, el nodo intermedio y la
  salida DEBEN (MUST) ser distintos por nodo, y DEBERÍAN (SHOULD) ser distintos
  por AS. Un circuito cuya guardia y salida comparten un AS es un regalo a la
  correlación extremo a extremo y NO DEBE (MUST NOT) usarse cuando exista
  cualquier alternativa.

## 3. Inferencia sin autodeclaración

- **PS-4.** GR-3 prohíbe a los relés declarar su ubicación, así que el cliente
  infiere el AS y la jurisdicción de cada relé a partir de sus `addrs` usando su
  *propio* conjunto de datos (por ejemplo, un mapa IP-a-AS refrescado
  periódicamente), nunca a partir de nada que el relé diga. La distribución del
  conjunto de datos DEBE (MUST) a su vez obedecer I-3: ninguna fuente
  autoritativa única (los diseños candidatos son OP-1).
- **PS-5.** La inferencia es incierta, y el cliente DEBE (MUST) tratarla como
  tal: cuando el AS o la jurisdicción de un relé es desconocida, cuenta como
  *potencialmente compartida* con cualquier otra desconocida — la suposición
  conservadora, nunca la optimista.

## 4. Guardias

- **PS-6.** Cada cliente mantiene un pequeño conjunto de **relés de guardia**
  (valor provisional: una guardia primaria por posición del circuito, rotada en
  una cadencia de meses, no de minutos), siguiendo la lógica de las guardias de
  Tor: rotar los puntos de entrada deprisa multiplica la probabilidad de
  terminar sacando uno hostil. Las guardias DEBEN (MUST) elegirse disjuntas por
  AS entre sí, de modo que los `n` circuitos no se canalicen a través de un
  único AS en la entrada.
- **PS-7.** La selección de guardias se pondera por el ancho de banda
  *verificado* (GR-7), nunca por el declarado; un relé con una afirmación no
  verificable se trata como de ancho de banda bajo, no alto.

## 5. Redes pequeñas: degrada, y dilo

- **PS-8.** Cuando la muestra verificada del cliente no puede suministrar `n`
  circuitos disjuntos por AS, DEBE (MUST) replegarse en un orden fijo —
  disjuntos por AS → disjuntos por nodo → extracciones independientes — y NO
  DEBE (MUST NOT) proceder en silencio como si la propiedad más fuerte se
  cumpliera. Los parámetros PUEDEN (MAY) reducirse (modo red pequeña: `n = 2, k
  = 2` con disjunción en la medida de lo posible) cuando no se alcanza el tamaño
  viable estimado.
- **PS-9.** El cliente DEBE (MUST) exponer el nivel de disjunción realmente
  alcanzado para un mensaje, en términos que un no experto lea correctamente: la
  multitud hoy es pequeña; esto es lo que estás comprando. El contenido
  garantizado (I-2) y el nivel de correlación son enunciados separados y DEBEN
  (MUST) mostrarse por separado.
- **PS-10 (estimación de tamaño resistente a sybil).** La estimación del tamaño
  viable DEBE (MUST) contar solo los relés verificados de forma independiente y
  la diversidad de AS observada, nunca el recuento bruto de registros, de modo
  que un adversario no pueda inflar la red con sybils para engañar a los
  clientes y que usen parámetros plenos cuya diversidad es falsa (se vincula a
  OP-2).
- **PS-11 (la disjunción creída no es disjunción real).** La protección que
  construye un cliente solo es tan buena como su conjunto de datos de inferencia,
  y el cliente DEBE (MUST) tratar la tasa de error del conjunto de datos como un
  parámetro de seguridad de primera clase, no como un detalle de implementación.
  El simulador (`poc/network_sim.py`, §1) separa la *verdad de base* — que el
  adversario explota — de la *creencia* del cliente, y barre la tasa de error de
  inferencia: a medida que el error crece, la selección disjunta por AS se vuelve
  en parte ilusoria y tanto la tasa de ruptura de contenido como la fuga de
  vinculación crecen de forma monótona. Dos consecuencias son normativas:
  (a) para el error de inferencia **aleatorio** (ruido, un mapa meramente
  inexacto), el error erosiona la **vinculación mucho más rápido que el
  contenido** — una ruptura de contenido todavía requiere que el adversario esté
  en `≥ k` circuitos a la vez, así que el umbral incondicional se sostiene
  mientras los metadatos se degradan primero; la interfaz NO DEBE (MUST NOT)
  presentar una cifra baja de ruptura de contenido como si acotara también la
  vinculación. Esta asimetría se sostiene **solo para el error aleatorio**; un
  mapa *elegido adversarialmente* no es ruido (ver PS-12);
  (b) una **muestra de gossip**
  más fina (PS-10, I-3) fuerza el repliegue antes: un cliente que conoce
  demasiado pocos relés no puede construir circuitos disjuntos por AS en absoluto
  y cae a `none`, donde la tasa de ruptura se dispara (§2). La estimación de
  tamaño viable (PS-10) DEBE (MUST) por tanto contabilizar la muestra
  *alcanzable*, no la red entera. Las cifras de error cero y vista completa son
  el mejor caso; un cliente conforme DEBE (MUST) presentar el nivel alcanzado
  (PS-9) a partir de su vista real, ruidosa y parcial.
- **PS-12 (un mapa hostil no debe dirigir la selección hacia el adversario).**
  `[claim-critical]` Un mapa *elegido adversarialmente* no es error aleatorio, y
  la asimetría de PS-11(a) **no** protege contra él. Un mapa que el adversario
  controla tiene dos palancas sobre la selección disjunta por AS: dar a los
  propios relés colocados juntos del adversario ASes falsos *distintos* (de modo
  que nunca se excluyan entre sí), y dar a los relés *honestos* ASes falsos *que
  colisionan* (de modo que, una vez que el circuito 1 elige un relé honesto, todo
  otro relé honesto parezca compartir AS y quede filtrado). La reserva de
  candidatos honestos colapsa entonces tras la primera extracción y el cliente
  selecciona los circuitos 2…`n` casi por completo entre relés del adversario —
  dejando al adversario en la guardia **y** en la salida de `≥ k` circuitos de
  forma **determinista**, una ruptura de *contenido*, mientras el cliente todavía
  cree que logró la disjunción por AS y no levanta ninguna advertencia de
  repliegue. Demostrado contra `poc/network_sim.py`: un mapa de direccionamiento
  lleva la tasa de ruptura de contenido de ~0 % al **100 % con ~15 %** de
  propiedad del adversario (frente a una tasa de un solo dígito bajo para un mapa
  honesto al 35 %). Así que **un mal mapa SÍ PUEDE alcanzar el contenido, no solo
  la vinculación** (esto corrige una exageración anterior; la ID-8a de la Parte 8
  se corrige para coincidir). Las defensas que un cliente conforme DEBE (MUST)
  aplicar:
  1. **No dejar que el mapa por sí solo colapse la reserva honesta.** Un cliente
     NO DEBE (MUST NOT) construir un conjunto de circuitos en el que más de una
     fracción acotada de los circuitos dependa, para su supuesta disjunción mutua,
     de relés que el cliente no puede corroborar como distintos de forma
     *independiente* (mezcla de fuentes GR-8, PS-10 "cuenta solo los verificados
     de forma independiente"). Si la selección creída-disjunta extrajera los
     circuitos 2…`n` de una reserva que el mapa ha vuelto sospechosamente pequeña,
     el cliente DEBE (MUST) tratar eso como una condición de repliegue/anomalía
     (PS-8, PS-9), no como un éxito.
  2. **Un mapa que implica una estructura de AS inverosímil es en sí una
     anomalía.** Un mapa bajo el cual la *muestra honesta alcanzable* del cliente
     colapsa a uno o unos pocos ASes mientras el resto moldeado por el adversario
     es máximamente diverso es una firma de direccionamiento; el cliente DEBERÍA
     (SHOULD) difundirlo por gossip como una anomalía del mapa (Parte 8 ID-10) y
     replegarse.
  3. **La reconstrucción es la defensa real.** Un mapa de direccionamiento no es
     reproducible a partir de entradas públicas (Parte 8 ID-5a); un cliente que
     reconstruye, o que concuerda con un par honesto que lo hizo, lo rechaza.
     Hasta entonces el cliente DEBE (MUST) tratar las afirmaciones de disjunción
     de un mapa no verificado como no verificadas, no como logradas (PS-9).
  El residual honesto permanece: dentro de la ventana de eclipse de un cliente
  que ha aceptado un mapa de direccionamiento no verificado y aún no puede
  reconstruir, el umbral incondicional del contenido puede caer. Esto está acotado
  por el margen `k`/`n` y por las defensas anteriores, no por una afirmación de
  que no puede ocurrir.

## 6. Lo que esta parte no decide

La distribución sin confianza del conjunto de datos de disjunción, y la
verificación formal de que un conjunto elegido es tan disjunto como se afirma
(OP-1); los umbrales honestos de tamaño viable y si `n = 2, k = 2` merece
siquiera la pena ejecutarse (OP-3); la economía de la rotación de guardias; la
selección de rutas sobre la malla de apagón, donde AS y jurisdicción no
significan nada (OP-6). `poc/network_sim.py` es el valor provisional ejecutable
detrás de esta parte — ataca su modelo, luego este texto.
