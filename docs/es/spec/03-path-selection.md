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

## 6. El procedimiento de verificación (PS-13…PS-19)

### 6.1 El procedimiento y su certificado

- **PS-13 (el procedimiento es una función pura de tres entradas declaradas).**
  `[claim-critical]` La construcción de circuitos DEBE (MUST) poder expresarse
  como una función determinista
  ```
      verify(sample, map, corroboration, n, k)  ->  (circuits, certificate)
  ```
  de exactamente tres entradas del lado del cliente, y nada más:
  - **`sample`** — la muestra de gossip verificada de relés del cliente (Parte 2,
    contada bajo PS-10: *solo los relés verificados de forma independiente*);
  - **`map`** — el mapa de inferencia de la Parte 8, nombrado por su hash `H` y
    que porta su propia tasa de error medida `e` (ID-12);
  - **`corroboration`** — un número por relé `c_j ∈ [0,1]` que declara con qué
    independencia está corroborado el AS/jurisdicción inferido del relé (PS-15).
  La salida son `n` circuitos **y** un **certificado de disjunción** (PS-14).
  Ningún paso puede leer la ubicación autodeclarada del relé (GR-3, PS-4), un
  directorio de confianza (I-3), ni la verdad de base (no hay ninguna que leer —
  ese es todo el problema). Una implementación conforme que no pueda expresar su
  selección como esta función pura no puede emitir un certificado comprobable y
  es no conforme: un implementador con esta especificación y las mismas tres
  entradas DEBE (MUST) poder reconstruir la misma decisión de
  circuitos-y-certificado (I-1).

- **PS-14 (qué contiene el certificado — y cómo es comprobable por máquina).**
  `[claim-critical]` El certificado es un registro en CBOR canónico (codificación
  de la Parte 0) que porta **exactamente** los campos que una segunda parte
  necesita para **recomputarlo y confirmarlo**, y ningún campo que pida ser
  creído:
  1. **`map_hash`** — el `H` contra el que se computó el certificado (ID-2). El
     certificado carece de sentido sin él: *"disjunto por AS"* no es nunca una
     afirmación autónoma, solo *"disjunto por AS bajo el mapa `H`"*.
  2. **`map_error`** — el par `(mismap_rate, unknown_rate)` que el mapa envió
     (ID-12), copiado al pie de la letra para que el verificador no tenga que
     volver a medirlo. Su suma es el error por consulta `e` usado más abajo.
  3. **`circuits`** — para cada uno de los `n` circuitos, los IDs de los relés
     (huellas de clave GR-2) en guardia/intermedio/salida, y para los **pivotes**
     (guardia y salida — las dos posiciones que un adversario a nivel de AS
     correlaciona, PS-3) el `(AS, jurisdicción)` **creído** que el mapa asignó, o
     `unknown`.
  4. **`corroboration`** — el `c_j` por pivote usado (PS-15), para que el
     verificador recompute con las mismas reducciones.
  5. **`class`** — la clase de disjunción alcanzada, una de `as` / `node` / `none`
     (orden de PS-2), es decir, la propiedad *más fuerte* que el conjunto
     realmente satisface bajo el mapa, no la solicitada.
  6. **`confidence`** — un número en `[0,1]` (PS-16), la cota inferior conservadora
     sobre la probabilidad de que la afirmación de `class` se sostenga dadas las
     barras de error del mapa y la corroboración.
  7. **`steering_flag`** — el veredicto del detector de PS-12 sobre la **muestra
     alcanzable completa** del cliente (PS-17), y la razón de supervivencia de la
     reserva que lo respalda.
  Un verificador **que posee el mismo mapa `H`** DEBE (MUST) poder: (a) volver a
  consultar el `(AS, jurisdicción)` de cada pivote en `H` y confirmar que coincide
  con el campo 3; (b) recomputar `class` a partir de esas consultas mediante la
  prueba de disjunción de PS-2; (c) recomputar `confidence` a partir de los campos
  2, 4, 5 y 7 mediante la fórmula de PS-16 **tal como se declara**; y (d) confirmar
  que el registro es internamente consistente. Si cualquier recómputo discrepa, el
  certificado es **inválido** y DEBE (MUST) rechazarse (se computó contra un mapa
  distinto, o está falsificado). El certificado no vincula ninguna firma: igual
  que el mapa mismo (ID-11), **la reproducción, no la firma, es el árbitro.**

  **Qué puede y qué no puede volver a derivar el verificador — enunciado con
  honestidad (hallazgo de una revisión hostil).** Dos campos son *entradas que el
  cliente originario midió*, no magnitudes que un verificador remoto pueda
  recomputar solo a partir de `H`: `steering_flag`/`pool_survival` son funciones de
  la **muestra de gossip alcanzable completa de ese cliente** (PS-17), que no es un
  campo del certificado; y cada `c_j` es la **medición de corroboración de ese
  cliente** (PS-15), tampoco rederivable a partir de `H`. Así que el certificado es
  comprobable **relativo a sus entradas declaradas** — un verificador confirma que
  la confianza se sigue del `map_error`, la `corroboration` y el `steering_flag`
  declarados mediante la fórmula de PS-16 — pero **no** es una prueba
  incondicional: un cliente que **miente** sobre su propio `c_j` al alza, u omite
  una bandera de direccionamiento que su muestra habría levantado, produce un
  certificado que recomputa *de forma consistente* y aun así es erróneo. Las
  defensas contra eso no están en el certificado sino en la red: un cliente
  independiente sobre el mismo `H` y una muestra solapada deriva un certificado
  **distinto**, y la divergencia se difunde por gossip como una anomalía (PS-19,
  ID-10) exactamente igual que se difunde una divergencia de mapa. El certificado
  elimina el *silencioso* "disjunto por AS: sí"; no hace que la confianza de un
  cliente mentiroso se autodemuestre. Este es un límite declarado (§6.6), no uno
  oculto.

### 6.2 Corroboración: la entrada de confianza por relé

- **PS-15 (la corroboración por relé es acuerdo independiente, contada como en
  PS-10).** La entrada `c_j` de un relé **no** es una puntuación de confianza y NO
  DEBE (MUST NOT) provenir del relé ni de ninguna parte única. Es el grado en que
  el AS inferido del relé está **corroborado de forma independiente** — la misma
  disciplina de "contar solo los verificados de forma independiente" que PS-10
  aplica a las estimaciones de tamaño y GR-8 aplica al gossip:
  - `c_j = 0` — el AS del relé proviene del mapa `H` **y de nada más**; el cliente
    no tiene un segundo punto de observación. Este es el valor por defecto y el
    umbral conservador.
  - `c_j` sube hacia `1` a medida que puntos de observación **independientes, con
    fuentes mezcladas** (GR-8) concuerdan en el mismo AS inferido para ese relé: un
    segundo mapa construido de forma reproducible a partir de un conjunto de
    recolectores disjunto (ID-3a), una observación fuera de banda del prefijo
    anunciado del relé, un pivote de certificado difundido por un par que coincide.
    Valor provisional (s): `c_j = 1 − 2^(−v)` para `v` puntos de observación
    corroborantes independientes (un punto ⇒ 0.5, dos ⇒ 0.75, …), limitado por
    debajo de `1` porque ningún número finito de puntos de observación del overlay
    ve el rack (§6.6).
  Un relé que el mapa etiqueta como `unknown` tiene `c_j = 0` **y** aporta un
  AS-creído `unknown` ya conservador (PS-5): colisiona con todo, así que rara vez
  sobrevive hasta una posición de pivote, y cuando lo hace la fórmula de confianza
  ya lo trata como plenamente incierto (PS-16). La corroboración NO DEBE (MUST
  NOT) inferirse de *cuántos* pares reportan un valor antes de aplicar la mezcla de
  fuentes GR-8/PS-10 — un sybil no puede votar el AS de un relé hacia una
  corroboración alta por mera cantidad (se vincula a OP-2, exactamente como ID-9).

### 6.3 La fórmula de confianza

- **PS-16 (la confianza es una cota inferior conservadora de mal-etiquetado
  independiente).** `[claim-critical]` Sean los **pivotes** de un conjunto de
  circuitos los relés distintos en la guardia o la salida a lo largo de los `n`
  circuitos (como mucho `2n`, menos tras deduplicar). La disjunción afirmada se
  sostiene **solo si ningún pivote está mal etiquetado** de una forma que convierta
  una pareja creída-distinta en una verdaderamente colisionante. El mapa envía el
  error por consulta `e = mismap_rate + unknown_rate` (ID-12); la corroboración
  reduce la probabilidad de mal-etiquetado **efectiva** de un pivote a
  ```
      p_j = e · (1 − c_j).
  ```
  Tratando los mal-etiquetados por pivote como **independientes**, la `confidence`
  del certificado para `class = as` es el producto
  ```
      confidence  =  Π_j ( 1 − e · (1 − c_j) )       sobre los pivotes j,
  ```
  bajada a `0` por la compuerta de direccionamiento de PS-17. Para `class = node`,
  la disjunción no depende del mapa en absoluto (la identidad del nodo está
  vinculada por GR-2, no inferida), así que `confidence = 1 − (compuerta PS-17)`.
  Para `class = none`, `confidence = 0` por definición: no se afirma disjunción
  alguna, así que ninguna se atestigua.

  **La suposición de independencia, nombrada y justificada como conservadora.** Los
  mal-etiquetados reales de pivotes **no** son independientes: un prefijo BGP
  erróneo en el mapa mal etiqueta de golpe a todo relé bajo él (correlación
  positiva). Asumimos la independencia de todos modos, y es **conservadora en la
  dirección que importa** para una *cota inferior*: el producto `Π(1 − p_j)` cuenta
  de menos el caso *correlacionado* en que varios pivotes comparten una causa de
  mal-etiquetado — cuando los mal-etiquetados están correlacionados, la probabilidad
  de que *al menos uno* de los pivotes sea erróneo es **menor** que la que implica
  el producto independiente, así que la verdadera probabilidad de "todos los
  pivotes correctos" es **mayor** que nuestra cota. El producto es por tanto un
  umbral sobre la confianza, es decir, nunca sobredeclara la seguridad. Donde la
  independencia nos haría ser demasiado confiados es ante una causa *honesta*
  compartida (un AS correcto gigantesco), que no amenaza la disjunción; la causa
  compartida adversarial — un mapa que colapsa la reserva — no la maneja este
  producto en absoluto sino la compuerta de PS-17, que baja la confianza a 0 con
  independencia del producto. Así que las dos formas de fallo quedan separadas con
  limpieza: **error de mapa aleatorio/correlacionado → el producto (conservador);
  estructura de mapa adversarial → la compuerta (umbral duro).**

  Fundamentación (no agitada con las manos). Contra `poc/network_sim.py`, sin
  corroboración (`c_j = 0`, así que `p_j = e`), `1 − confidence` acota por arriba la
  tasa de colisión de AS-real **observada** de los pivotes en cada nivel de error —
  p. ej. en `e = 0.2`, `1 − confidence ≈ 0.83` frente a un fallo de disjunción real
  observado de `≈ 0.18`: pesimista, que es la dirección correcta para un umbral de
  seguridad, nunca optimista. La corroboración lo recupera de forma monótona (en
  `e = 0.2`, la confianza media sube `0.17 → 0.43 → 0.84 → 0.99` a medida que un
  `c_j` uniforme va `0 → 0.5 → 0.9 → 1.0`). Un cliente conforme DEBERÍA (SHOULD)
  presentar este pesimismo honesto en lugar de estrechar la cota con un modelo que
  asuma más de lo que las tres entradas declaradas justifican — un umbral defendible
  vence a la falsa precisión (PS-11).

### 6.4 Robustez frente a PS-12, por construcción

- **PS-17 (la compuerta de direccionamiento baja la confianza — con la señal
  correcta, sobre la muestra alcanzable COMPLETA).** `[claim-critical]` Antes de
  reportar el producto de PS-16, el procedimiento DEBE (MUST) aplicar el detector de
  la defensa 2 de PS-12 (`detect_steering`) a la **muestra de gossip alcanzable
  completa** del cliente, no a los `2n` pivotes elegidos — la estructura vive en la
  *población* y ha desaparecido de los pivotes para cuando estos se extraen
  (comprobar solo los pivotes atrapa un mapa de direccionamiento en solo ~la mitad
  de los mensajes). **La señal debe ser la que el adversario no puede evitar.** Una
  primera versión de este detector se fijaba en "un único AS-creído gigante que
  retiene la reserva honesta colapsada, rodeado de singletons", y una revisión
  hostil **la evadió** colapsando la reserva honesta en *unos pocos* ASes falsos en
  lugar de uno gigante — sin AS gigante, detector en silencio, contenido roto en
  ~30 % de los mensajes. La señal correcta y portante es la **fracción anómala de
  singletons**: para hacer que sus relés colocados juntos parezcan disjuntos por AS
  el adversario DEBE (MUST) dar a cada uno un AS falso distinto, es decir,
  convertirlos en singletons, y una red real tiene muy pocos ASes singleton. El
  detector DEBE (MUST) por tanto dispararse cuando los relés singleton superan una
  pequeña fracción de la muestra **y** los relés no singleton se ubican en
  demasiado pocos ASes abarrotados como para construir `n` circuitos disjuntos (la
  segunda cláusula impide que el *ruido* de inferencia, que también produce
  singletons, lo haga saltar). Medido contra `poc/network_sim.py`
  (`make_steering_map(honest_groups=g)` / el `detect_steering` corregido): esto
  atrapa el régimen de direccionamiento **efectivo** (`g = 1…5`, una ruptura de
  contenido del 10–100 %) al ~100 % con **0 %** de falsos positivos en mapas
  honestos incluso con error de inferencia de hasta 0.4. Por lo tanto:
  - Si el detector se dispara sobre la muestra alcanzable, el certificado DEBE
    (MUST) fijar `steering_flag = true`, `class = none` y `confidence = 0`, y el
    cliente DEBE (MUST) tratar el resultado como la condición de repliegue/anomalía
    de PS-12 (difundirlo por gossip, ID-10; degradar y decirlo, PS-8/PS-9) — NO
    DEBE (MUST NOT) emitir un certificado `as`.
  - **Residual declarado:** un mapa de direccionamiento *marginal* que reparte la
    reserva honesta a lo largo de suficientes ASes falsos (`g ≥ 8`) como para
    construir circuitos genuinamente disjuntos escapa al detector — pero ahí su
    ruptura de contenido es solo ~5 %, indistinguible de una red legítima pequeña,
    y acotada por el margen `k`/`n` y la confianza de PS-16, no por una afirmación
    de que no puede ocurrir (§6.6).

- **PS-18 (precondición de colapso de la reserva — defensa 1 de PS-12, plegada
  como entrada de confianza).** `[claim-critical]` Con independencia del detector
  estructural, el procedimiento DEBE (MUST) computar la **razón de supervivencia de
  la reserva honesta**: la fracción de la muestra alcanzable y corroborada de forma
  independiente (PS-10, PS-15 con `c_j > 0`) que permanece como candidata de
  *AS-creído-distinto* **después** de extraer el primer circuito. Un certificado NO
  DEBE (MUST NOT) afirmar `class = as` cuando los circuitos `2…n` se extrajeron de
  una reserva que el mapa colapsó por debajo de una fracción acotada (valor
  provisional (s): supervivencia `< 1/n` de la muestra honesta corroborada), porque
  entonces la disjunción mutua afirmada del conjunto descansa sobre relés que el
  cliente no puede corroborar como distintos de forma *independiente* — exactamente
  la defensa 1 de PS-12. En ese caso el procedimiento DEBE (MUST) o bien bajar
  `class` a `node` (descartando por completo la afirmación dependiente del mapa) o
  fijar la condición de anomalía como en PS-17. **La confianza es BAJA exactamente
  cuando PS-12 dice que al cliente lo están dirigiendo:** la compuerta la anula ante
  la firma estructural, y la precondición de supervivencia despoja la afirmación
  `as` cuando la reserva es sospechosamente delgada — de modo que un mapa de
  direccionamiento no puede ganarse un certificado `as` de alta confianza por
  ninguna de las dos palancas (ASes adversarios falsos-distintos o ASes honestos
  falsos-colisionantes). Esta es la propiedad innegociable, y está verificada, no
  aseverada: la misma compuerta que las pruebas de PS-12 muestran que convierte una
  ruptura de contenido del 100 % en un repliegue del 100 % lleva la confianza del
  certificado a 0 en el 100 % de los mapas de direccionamiento.

### 6.5 Un certificado trabajado

Entradas: `n = 4`, `k = 3`; una muestra sana; mapa `H = 0x9f2c…a17b` que envía
`map_error = (0.04, 0.03)` así que `e = 0.07`; los 8 pivotes (4 guardias + 4
salidas) — 6 corroborados por un punto de observación independiente extra
(`c_j = 0.5`), 2 apoyándose solo en el mapa (`c_j = 0.0`); el detector de
direccionamiento **no** se dispara sobre la muestra alcanzable. Entonces
`p_j = 0.035` para los seis y `0.07` para los dos, y
`confidence = (1−0.035)^6 · (1−0.07)^2 = 0.698`.

```
disjointness-certificate (canonical CBOR; shown as a record):
  map_hash      : 0x9f2c3e...a17b
  map_error     : { mismap: 0.04, unknown: 0.03 }         # e = 0.07 (ID-12)
  class         : "as"                                     # el más fuerte cumplido, PS-2
  confidence    : 0.698                                    # producto PS-16, compuerta=1
  steering_flag : false                                    # PS-17, chequeo de vista completa
  pool_survival : 0.61                                     # PS-18, > 1/n = 0.25 OK
  circuits:
    - { guard: 4a1f.., mid: 7c02.., exit: e9d3..,
        pivots:[{as:3356, jur:"US", c:0.5},{as:1299, jur:"SE", c:0.5}] }
    - { guard: b17c.., mid: 02aa.., exit: 55f1..,
        pivots:[{as:3320, jur:"DE", c:0.5},{as:9002, jur:"GB", c:0.0}] }
    - { guard: cc90.., mid: 1d44.., exit: a7e8..,
        pivots:[{as:6830, jur:"NL", c:0.5},{as:2914, jur:"JP", c:0.5}] }
    - { guard: 3e5b.., mid: f108.., exit: 9b22..,
        pivots:[{as:174,  jur:"US", c:0.0},{as:8075, jur:"IE", c:0.5}] }
```
Leído correctamente (PS-9): *"Estos 4 circuitos son disjuntos por AS **bajo el
mapa `H`**, que admite una tasa de error del 7 %; dado con qué independencia está
corroborado el AS de cada relé, hay al menos un **70 % de probabilidad** de que la
disjunción por AS sea real y no un artefacto de un mal-etiquetado. No es una
garantía, y no dice nada sobre un centro de datos que el mapa no puede ver
(§6.6)."* Si el detector de direccionamiento se hubiera disparado, cada número de
arriba se reemplazaría por `class: none, confidence: 0, steering_flag: true` y una
advertencia de repliegue — no hay certificado de alta confianza para un cliente
dirigido.

```
  EL FLUJO DE PRODUCIR-CIRCUITOS-Y-CERTIFICADO

   sample (PS-10)      map H + e (ID-12)      corroboration c_j (PS-15)
        │                   │                        │
        └─────────┬─────────┴───────────┬────────────┘
                  ▼                      ▼
        ┌───────────────────┐   ┌─────────────────────────────┐
        │ detect_steering    │   │ selección disjunta AS-creído│
        │ sobre muestra      │   │ (orden PS-2: as→node→none)  │
        │ COMPLETA           │   │  + superv. reserva (PS-18,  │
        │ (PS-17, defensa 2) │   │     defensa 1)              │
        └─────────┬─────────┘   └──────────────┬──────────────┘
                  │                            │ n circuitos + pivotes
      ¿dispara?   │                            ▼
         ┌────────┴────────┐                   ▼
       sí                no        ┌────────────────────────────┐
         │                 └──────▶ │ confidence = Π(1−e(1−c_j))  │ PS-16
         ▼                         │ class = el más fuerte cumpl.│
  class=none, conf=0               └──────────────┬─────────────┘
  steering_flag=true                              ▼
  → repliegue + gossip       ┌─────────────────────────────────────┐
    (PS-8/9, ID-10)          │ CERTIFICADO {map_hash, map_error,    │
                             │  circuits, corroboration, class,     │
                             │  confidence, steering_flag}          │
                             └──────────────┬──────────────────────┘
                                            ▼
                   un verificador con el MISMO H recomputa y confirma
                   (la reproducción es el árbitro — sin firma, ID-11)
```

- **PS-19 (el certificado es para el usuario y el par, ambos).** La `confidence`
  y la `class` DEBEN (MUST) gobernar la superficie de honestidad de PS-9 que el
  usuario lee (*la multitud está así de disjunta hoy, con esta certeza*), y el
  certificado DEBE (MUST) ser difundible por gossip de modo que un par que posea
  el mismo `H` pueda rederivarlo (PS-14) y de modo que una divergencia — dos
  clientes, el mismo `H` y muestra, un certificado distinto — se atrape y se
  difunda por gossip como una anomalía (ID-10), la misma señal inmune que la Parte
  8 usa para la divergencia de mapas. La interfaz NO DEBE (MUST NOT) citar
  `confidence` como si acotara la vinculación: acota la afirmación de disjunción de
  **contenido**; los metadatos se degradan más rápido (PS-11(a)), y una confianza
  alta en `class = as` no significa una fuga de vinculación baja.

### 6.6 Lo que esto no resuelve

El certificado atestigua **consistencia frente a un conjunto de datos de confianza
acotada, no disjunción verdadera** (Parte 8 §10), y la honestidad de todo este
procedimiento está en decirlo en cada registro. Un adversario que coloca juntos
relés en un mismo rack mientras anuncia espacio de direcciones que los datos
públicos BGP/RIR atribuyen **verazmente** a ASes distintos es etiquetado como
disjunto por el mapa **correcto** — así que las consultas coinciden con `H`, el
detector de direccionamiento no se dispara (la estructura no es una firma de
direccionamiento, es la auténtica tabla de enrutamiento pública), la reserva no
colapsa, y los pivotes están bien corroborados **porque todo punto de observación
honesto concuerda con el mapa**. El procedimiento por tanto emite un **certificado
`as` de alta confianza que, no obstante, es erróneo**: `confidence` mide la
probabilidad de que el conjunto sea disjunto *bajo el mapa*, y aquí el mapa tiene
razón y el overlay aun así no puede ver el rack. Este es el residual de
co-ubicación de la Parte 8 §10, y es la única limitación que el certificado **no
puede** eliminar — ninguna cantidad de corroboración lo cierra, porque la
corroboración solo confirma el acuerdo *con los datos públicos*, y los datos
públicos mismos son lo que el adversario satisfizo. Su magnitud es exactamente la
brecha del simulador entre el AS creído y el verdadero en `infer_error = 0`: el
certificado lee 1.0, la realidad todavía puede colisionar, y solo elevar el margen
`k`/`n` — ningún campo del certificado — acota la pérdida. El don del certificado
es que nunca **oculta** esto: enuncia sus propias barras de error, se baja a sí
mismo a cero bajo direccionamiento (PS-17/18), y es comprobable por cualquiera que
tenga el mapa (PS-14). Convierte "disjunto por AS: sí" — una mentira — en "disjunto
por AS bajo el mapa `H` con error `e`, confianza `c`" — un enunciado verdadero cuyo
único punto ciego restante se nombra aquí y en ningún sitio se oculta.

Tres límites adicionales que una revisión hostil sacó a la luz, declarados aquí en
vez de disimulados:

- **El direccionamiento marginal escapa al detector.** Un mapa de direccionamiento
  que reparte la reserva honesta a lo largo de suficientes ASes falsos (`g ≥ 8`)
  construye circuitos genuinamente disjuntos y por tanto no hace saltar el detector
  de fracción de singletons (PS-17) — pero su ruptura de contenido es entonces solo
  ~5 %, el nivel de una red legítima pequeña, acotada por el margen `k`/`n` y la
  confianza de PS-16. El detector atrapa el régimen de direccionamiento *efectivo*
  (ruptura del 10–100 %), no todo mapa.
- **La confianza de un cliente mentiroso no se autodemuestra.** `confidence` es
  solo tan honesta como el `c_j` y el `steering_flag` que el cliente originario
  midió y puso en el certificado; un cliente que sobredeclara su propia
  corroboración, u omite una bandera, emite un certificado que recomputa de forma
  consistente y aun así es erróneo (PS-14). La captura es social, no aritmética: un
  cliente independiente sobre el mismo `H` deriva un certificado distinto, y la
  divergencia se difunde por gossip como una anomalía (PS-19). El certificado
  elimina la mentira *silenciosa*, no una *detectable*.
- **El producto de confianza acota las colisiones de parejas de pivotes, no toda
  colisión.** PS-16 mide la probabilidad de que una *pareja* de pivotes
  creída-disjunta sea verdaderamente colisionante. Un mal-etiquetado que colisiona
  un pivote con un salto *intermedio*, o confunde la jurisdicción con el AS, queda
  fuera del producto y debe atraparlo la prueba de disjunción de PS-2 sobre el
  circuito completo, no leerse del número de confianza.


## 7. Lo que esta parte no decide

La distribución sin confianza del conjunto de datos de disjunción, y la
verificación formal de que un conjunto elegido es tan disjunto como se afirma
(OP-1); los umbrales honestos de tamaño viable y si `n = 2, k = 2` merece
siquiera la pena ejecutarse (OP-3); la economía de la rotación de guardias; la
selección de rutas sobre la malla de apagón, donde AS y jurisdicción no
significan nada (OP-6). `poc/network_sim.py` es el valor provisional ejecutable
detrás de esta parte — ataca su modelo, luego este texto.
