# Especificación de ScrambNet — Parte 6: Rendezvous y entrega
> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../../en/spec/06-rendezvous.md)).

**Estado: BORRADOR (DRAFT).** Valores provisionales marcados con `(s)`. Las cuestiones de metadatos de recuperación y
economía que esta parte abre son OP-9 y están deliberadamente sin resolver.

## 1. Alcance

Cómo un mensaje llega a alguien que no está — y no debe estar — en el mapa de nadie.
Los destinatarios no tienen ubicaciones de red; tienen **tarjetas de contacto** y
**dead-drops**. El remitente deposita partes; el destinatario las recupera desde
detrás de sus propios circuitos. Nadie entrega nunca *a* una persona.

## 2. Nadie hace gossip sobre personas

- **RZ-1.** Un destinatario NO DEBE (MUST NOT) ser descubrible a través del gossip. Solo los relés
  publican registros (Parte 2). Cualquier cosa que haga consultable la participación de una persona
  es un defecto (compárese con L0: no hay lista de usuarios porque no hay
  momento en que un usuario se dé de alta).

## 3. Tarjetas de contacto

- **RZ-2.** Una tarjeta de contacto es **por relación**: la tarjeta dada al
  corresponsal A DEBE (MUST) ser no enlazable con la tarjeta dada al corresponsal B —
  clave de par distinta, buzones distintos. El compromiso de un corresponsal expone
  una relación, no el mundo del destinatario.
- **RZ-3.** Contenido de la tarjeta (CBOR canónico, como en la Parte 2):

| Clave | Nombre | Tipo | Notas |
|---|---|---|---|
| 0 | `v` | uint | versión de formato, `1` |
| 1 | `id` | bytes(32) | clave de identidad Ed25519 del destinatario |
| 2 | `kpair` | bytes(32) | secreto de par; todo lo de abajo deriva de él |
| 3 | `drops` | array | `d` registros de relé incrustados (registros completos de la Parte 2) |
| 4 | `validity` | uint | expiración unix; DEBERÍA seguir la expiración de los registros incrustados |

  Derivaciones (HKDF-BLAKE2s, suite 0x01): la clave de etiqueta SP-7 para este par es
  `K_tag = HKDF(kpair, "tag")`; los identificadores de buzón son
  `box_id(drop, epoch) = PRF(kpair, "box" ‖ drop_index ‖ epoch)` truncado a
  16 bytes, con `epoch = floor(unix_time / 86400)` (s). El índice del drop DEBE (MUST)
  entrar en la derivación: con un único id por época, dos drops confabulados podrían
  enlazar los buzones del par dentro de esa época.
- **RZ-4.** Las tarjetas viajan fuera de banda (código QR, cadena impresa, un amigo) o
  sobre un canal ScrambNet existente. Un contacto es el umbral, como en GR-10.

## 4. Drops y depósito

- **RZ-5.** El conjunto de drops tiene `d = n = 4` (s) relés, elegidos por el
  *destinatario*, que DEBERÍAN (SHOULD) ser mutuamente independientes en el mismo sentido que la selección
  de rutas exige (OP-1 también aplica a los drops). Las `n` partes de un mensaje
  DEBEN (MUST) depositarse en `n` drops distintos — SP-7 extendido al almacenamiento: ningún
  drop tiene nunca dos partes de nada.
- **RZ-6.** Un depósito es un paquete ordinario de la Parte 1 cuyo circuito termina en el
  drop. El texto en claro del salto final de `delta` es `box_id` (16 B) ‖ `slot`
  (1840 B); el slot es la carga útil de parte de la §4 de la Parte 1 con su pad final
  16 bytes más corto. El drop almacena el slot bajo `box_id` verbatim: no puede
  leer ni la semántica de la etiqueta ni el contenido de la parte (una parte < `k`, y SP-7
  hace las partes mutuamente no enlazables incluso a través de drops confabulados).
- **RZ-7.** Los depósitos son disparar-y-olvidar. El drop NO DEBE (MUST NOT) emitir respuesta alguna
  que distinga éxito, buzón desconocido o buzón lleno (uniformidad silenciosa, como
  GR-4). Reglas de almacenamiento: slots fijos de 1840 B, a lo sumo `64` (s) slots por buzón,
  expiración de slot `7` días (s), desalojo del más viejo primero. El tope acota el
  **almacenamiento**, no la **entrega** bajo inundación (flooding) — véase RZ-15.

## 5. Recuperación

- **RZ-8.** El destinatario sondea cada uno de sus drops sobre sus propios circuitos.
  El conocimiento de `box_id` autoriza la recuperación (es derivado de un secreto e
  inadivinable); los slots se borran por expiración, no por obtención (la semántica de
  borrado-por-obtención es territorio de OP-9: un adversario que roba un `box_id` no debe
  poder comerse el correo en silencio).
- **RZ-9 (disciplina de sondeo).** El sondeo DEBE (MUST) seguir un calendario independiente de
  la actividad del usuario: cadencia fija con jitter (hombre de paja: cada `15` minutos ±
  `5` uniforme), continuando cuando el usuario está inactivo, con sondeos señuelo a ids de buzón
  señuelo a la misma cadencia. Una respuesta de recuperación es siempre exactamente `b = 8`
  (s) slots, rellenada con slots falsos indistinguibles de los reales. El
  drop aprende la cadencia de sondeo y los tiempos de depósito de un buzón dentro de una época —
  ese es el residuo de diseño, acotado por RZ-10 y ahora tarificado en RZ-16: la
  independencia del calendario DEBE (MUST) ser estricta (RZ-16a) y el coste de señuelos/bytes
  está cuantificado (RZ-16b).
- **RZ-10 (épocas).** `box_id` rota por época. Un drop NO DEBE (MUST NOT) poder
  enlazar los buzones del mismo par a través de épocas; nada en el protocolo de recuperación
  puede llevar un valor estable a través de épocas.

## 6. Renovación y fallo

- **RZ-11.** Una tarjeta se renueva en banda: el destinatario deposita la siguiente tarjeta
  (nuevo `kpair`, nuevos drops) en los buzones existentes del par como un mensaje ordinario,
  antes de que se agote `validity`. Si todos los drops de un par están muertos o la
  tarjeta ha expirado, el par reintercambia fuera de banda: un contacto es el
  umbral, otra vez.
- **RZ-12.** Cualquiera que tenga una tarjeta puede llenar sus buzones. El tope por buzón (RZ-7)
  acota el daño de la inundación (flooding) **al almacenamiento de una relación**, pero no la
  **entrega** de esa relación — RZ-15 muestra que un inundador de clase teléfono deniega la
  recuperación dentro de un periodo de sondeo, y que la tarificación de depósitos (puzzles de
  cliente) no puede cerrar la brecha; la defensa suficiente (control de admisión de depósitos) es
  un residual OP-9 sin resolver. Los incentivos de almacenamiento del drop siguen abiertos (OP-9).

## 7. Derivación de claves y fronteras de época

- **RZ-13 (una sola disciplina de KDF).** Cada clave e identificador que un par deriva de `kpair` DEBE (MUST) provenir de una sola disciplina: HKDF-BLAKE2s con una etiqueta distinta y vinculante al propósito. En concreto: la clave de contenido es `HKDF(kpair, "e2e-content")` (SP-1a), la clave de etiqueta SP-7 es `HKDF(kpair, "tag")`, y el identificador de buzón es `box_id = HKDF(kpair, "box" ‖ drop_index ‖ epoch)` truncado a `BOX_ID_BYTES`. Ningún valor se deriva por BLAKE2s con clave en crudo sobre `kpair` ni por ninguna segunda construcción — un borrador anterior derivaba `box_id` de ese modo, lo que este requisito retira. La separación por etiquetas significa que la captura o debilidad de una clave derivada no le dice nada al adversario sobre sus hermanas, y toda la relación queda gobernada por una única derivación auditable (el argumento de separación de claves `SA-4`, Parte 7, depende exactamente de esto).
- **RZ-13a (ancho de box_id).** `BOX_ID_BYTES = 16` (128 bits) (s). Un drop ve solo este manejador opaco, nunca `kpair`; 128 bits es seguro frente a colisiones para el número de buzones `(pair, drop, epoch)` que cualquier red realista sostiene y mantiene la carga útil `box_id ‖ slot` dentro de un `delta`.
- **RZ-14 (gracia en la frontera de época UTC).** Como `box_id` rota por época UTC (RZ-10), un remitente que deposita a las 23:59 (época `E`) y un destinatario que sondea a las 00:01 (época `E+1`) direccionarían buzones distintos y el destinatario perdería el correo en silencio. Para evitarlo, un destinatario que sondea dentro de una ventana de gracia de una frontera de época DEBE (MUST) sondear los buzones de **ambas** épocas adyacentes: la época actual siempre, la época anterior si está dentro de la ventana de gracia tras una frontera, y la época siguiente si está dentro de la ventana de gracia antes de una. La ventana de gracia DEBE (MUST) exceder el peor caso de desfase de reloj entre remitente/destinatario más la latencia de depósito a sondeo (hombre de paja: `EPOCH_GRACE_SECONDS = 3600` (s)), y `SLOT_TTL_EPOCHS` (RZ-7) DEBE (MUST) mantener un buzón legible al menos una época más allá de la suya, para que el buzón extra siga conteniendo el correo. Los remitentes depositan bajo el único `epoch_of(now)`; la gracia es una regla de lectura del lado del destinatario. Demostrado en `poc/rendezvous.py` (`epochs_to_poll`, test `test_deposit_before_boundary_polled_after_boundary`).

## 8. Economía y metadatos de recuperación, tarificados (OP-9)

El ítem 4.3 del roadmap puso números a las dos cuestiones OP-9 que RZ-7/RZ-9 dejaron abiertas —
inundación (flooding) y metadatos de sondeo — con el simulador `poc/dropecon_sim.py`
(`test_dropecon_sim.py` fija las cifras). El resultado honesto es que una de las dos defensas
que el proyecto esperaba **no** se sostiene; el §9 lo lleva como un residual declarado en lugar
de ocultarlo.

- **RZ-15 (inundación: ni el tope ni un puzzle defienden la *entrega*; es un
  residual declarado). [normativo]** El tope por buzón de RZ-7 acota el **almacenamiento** a
  `BOX_CAP × SLOT_BYTES = 115 KiB` por buzón `(pair, drop, epoch)`, un techo
  independiente del presupuesto del atacante. **No** acota la **entrega**. Como un
  sondeo devuelve solo los `B_SLOTS = 8` slots supervivientes más viejos (RZ-8) y los depósitos
  desalojan al más viejo primero (RZ-7), un atacante que entierra un slot honesto fresco detrás
  de `≥ 8` slots basura más nuevos deniega su recuperación **sin siquiera alcanzar el tope** —
  y el simulador muestra que un inundador de **clase teléfono** (`2 × 10⁶ H/s`) hace esto en
  `~17 s`, muy dentro de un sondeo `POLL_PERIOD = 900 s`, con toda dureza de puzzle utilizable.
  Un puzzle de proof-of-work del lado del depósito no rescata esto: ninguna dureza
  `z` es a la vez disuasoria de botnets y asequible para un teléfono — la brecha ARM-vs-GPU es
  de `~25 000×`, así que con `z = 20` (el último punto asequible para teléfono, `0.52 s/depósito`)
  una sola GPU todavía rellena un buzón `~1.7 × 10⁸` veces/hora, mientras que forzar a una GPU
  a `1 s/depósito` le cuesta al teléfono `~9.5 horas/depósito`. Un puzzle PUEDE (MAY) exigirse
  con dureza baja (`z ≤ 20` (s)) como un reductor de velocidad frente al rellenado trivial, pero **no**
  se depende de él. La dispersión `n = 4, k = 3` solo eleva el listón a inundar
  `≥ n − k + 1 = 2` de los drops de un par a la vez. **La inundación de entrega, por tanto, no tiene
  defensa suficiente en esta parte:** necesita un control de **admisión** de depósitos
  que el proyecto aún no ha diseñado (una dirección candidata, no una decisión: un
  token de admisión por relación derivado de la tarjeta, de modo que solo un poseedor de tarjeta
  deposite y solo a una tasa acotada). Hasta que eso exista, la inundación de entrega es un
  residual OP-9 declarado, cuantificado en el §9.

- **RZ-16 (metadatos de sondeo: dos fugas, dos palancas). [normativo]** La observación intra-época
  de un drop que perfila (acotada a través de épocas por RZ-10) se descompone
  en dos fugas con dos defensas independientes, y el simulador tarifica ambas.
  - **RZ-16a (fuga del patrón de actividad — defendida gratis por la independencia estricta).
    [normativo]** Si el destinatario *reaccionó* a un depósito es la única
    fuga identificadora de usuario, y se defiende haciendo el calendario de sondeo
    **estrictamente independiente** de los depósitos y de la actividad del usuario (RZ-9): el calendario
    NO DEBE (MUST NOT) ser adelantado, disparado ni remodelado por un depósito o un evento de app, de modo
    que la latencia `deposit → next-poll` permanezca en la media por paradoja de la inspección propia del
    calendario (`≈ 467 s` para `POLL_PERIOD = 900, POLL_JITTER = 300`)
    y no esté correlacionada con el tiempo de depósito. Un drop detecta una violación no por la
    media (demasiado burda — un calendario medio reactivo todavía se lee casi independiente en la
    media) sino por la **cola** `P[latency < 60 s]`, que el simulador muestra
    subiendo desde el ruido en la independencia hasta una señal clara en una fracción reactiva del
    `5 %`. Esta defensa es **obligatoria y gratuita en bytes**.
  - **RZ-16b (fuga de qué buzón — defendida por señuelos a un coste real en bytes). [normativo]**
    Cuál de varios buzones sostenidos es el real del destinatario se defiende por sondeos
    señuelo a un multiplicador `r` (s: `r = 1`), una cuestión que la no enlazabilidad de RZ-2/RZ-10
    ya responde en gran medida, así que la privacidad marginal por byte es baja. Cada sondeo
    viaja sobre Sphinx — `B_SLOTS + 1 = 9` paquetes de `2048 B` sobre el salto de entrada
    medido, `~18.4 KiB`, no los bytes de slot en crudo — así que a través de `d = 4` drops a la
    cadencia de RZ-9 el coste permanente es `~212 MB/mes` con `r = 0` (antes del
    lado de depósito/envío) y `~425 MB/mes` con el `r = 1` por defecto. `r = 0` es un
    modo de bajos datos explícito. Demostrado en `poc/dropecon_sim.py` (Escenario B).

## 9. Lo que esta parte no decide (el residual OP-9 declarado)

La minimización de metadatos de recuperación (recuperación más lista que el sondeo, trucos
al estilo PIR y sus costes reales), la semántica de borrado, y los incentivos del drop (por qué
un relé almacena el ruido de un desconocido) siguen genuinamente abiertos (OP-9); la verificación
de la independencia del conjunto de drops (OP-1); el sondeo sobre la malla durante el apagón (OP-6).
Existen issues numeradas para cada uno. Tres resultados del §8 se llevan abiertamente como
residuales declarados, con los números que los prueban:

- **La inundación de entrega no tiene defensa suficiente aquí.** Ni el tope de RZ-7
  (solo-almacenamiento) ni un puzzle de proof-of-work (no existe dureza
  asequible para teléfono y disuasoria de botnets — la brecha ARM-vs-GPU de `~25 000×`) detienen a un
  atacante que entierra correo honesto más allá de la ventana de recuperación de 8 slots en `~17 s`, muy
  dentro de un sondeo de 900 s, con hardware de clase teléfono (RZ-15). Necesita un control de
  admisión que el proyecto aún no ha construido; hasta entonces es un residual declarado.
- **El suelo de perfilado intra-época es real.** La independencia estricta (RZ-16a)
  elimina la única fuga identificadora de usuario, pero un drop todavía aprende la cadencia pública
  de RZ-9 y los tiempos de depósito en los buzones que sostiene; los señuelos alcanzan solo la
  cuestión de qué buzón (RZ-16b). Un drop multi-buzón confabulado también puede correlacionar
  marcas de tiempo de *depósito* a través de sus buzones incluso bajo independencia de sondeo perfecta —
  la no enlazabilidad de RZ-2/RZ-10 cubre identificadores, no la *temporización* de depósito.
- **La línea base de sondeo de RZ-9 es pesada para el objetivo móvil.** Incluso con los señuelos
  apagados (`r = 0`), el sondeo obligatorio de cadencia fija a través de `d = 4` drops cuesta
  `~212 MB/mes` (RZ-16b) — el precio de la defensa del patrón de actividad, pagado en
  bytes, antes de que se envíe ningún mensaje.
