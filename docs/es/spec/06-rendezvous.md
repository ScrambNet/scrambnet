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
  expiración de slot `7` días (s), desalojo del más viejo primero.

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
  ese es el residuo de diseño, acotado por RZ-10 y atacado en OP-9.
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
  acota el daño de la inundación a una relación; la tarificación de depósitos (¿puzzles de
  cliente?) y la economía de almacenamiento del drop están abiertas (OP-9).

## 7. Derivación de claves y fronteras de época

- **RZ-13 (una sola disciplina de KDF).** Cada clave e identificador que un par deriva de `kpair` DEBE (MUST) provenir de una sola disciplina: HKDF-BLAKE2s con una etiqueta distinta y vinculante al propósito. En concreto: la clave de contenido es `HKDF(kpair, "e2e-content")` (SP-1a), la clave de etiqueta SP-7 es `HKDF(kpair, "tag")`, y el identificador de buzón es `box_id = HKDF(kpair, "box" ‖ drop_index ‖ epoch)` truncado a `BOX_ID_BYTES`. Ningún valor se deriva por BLAKE2s con clave en crudo sobre `kpair` ni por ninguna segunda construcción — un borrador anterior derivaba `box_id` de ese modo, lo que este requisito retira. La separación por etiquetas significa que la captura o debilidad de una clave derivada no le dice nada al adversario sobre sus hermanas, y toda la relación queda gobernada por una única derivación auditable (el argumento de separación de claves `SA-4`, Parte 7, depende exactamente de esto).
- **RZ-13a (ancho de box_id).** `BOX_ID_BYTES = 16` (128 bits) (s). Un drop ve solo este manejador opaco, nunca `kpair`; 128 bits es seguro frente a colisiones para el número de buzones `(pair, drop, epoch)` que cualquier red realista sostiene y mantiene la carga útil `box_id ‖ slot` dentro de un `delta`.
- **RZ-14 (gracia en la frontera de época UTC).** Como `box_id` rota por época UTC (RZ-10), un remitente que deposita a las 23:59 (época `E`) y un destinatario que sondea a las 00:01 (época `E+1`) direccionarían buzones distintos y el destinatario perdería el correo en silencio. Para evitarlo, un destinatario que sondea dentro de una ventana de gracia de una frontera de época DEBE (MUST) sondear los buzones de **ambas** épocas adyacentes: la época actual siempre, la época anterior si está dentro de la ventana de gracia tras una frontera, y la época siguiente si está dentro de la ventana de gracia antes de una. La ventana de gracia DEBE (MUST) exceder el peor caso de desfase de reloj entre remitente/destinatario más la latencia de depósito a sondeo (hombre de paja: `EPOCH_GRACE_SECONDS = 3600` (s)), y `SLOT_TTL_EPOCHS` (RZ-7) DEBE (MUST) mantener un buzón legible al menos una época más allá de la suya, para que el buzón extra siga conteniendo el correo. Los remitentes depositan bajo el único `epoch_of(now)`; la gracia es una regla de lectura del lado del destinatario. Demostrado en `poc/rendezvous.py` (`epochs_to_poll`, test `test_deposit_before_boundary_polled_after_boundary`).

## 8. Lo que esta parte no decide

La minimización de metadatos de recuperación (recuperación más lista que el sondeo, trucos
al estilo PIR y sus costes reales), la semántica de borrado, la tarificación de depósitos, los incentivos
del drop (OP-9); la verificación de la independencia del conjunto de drops (OP-1); el sondeo sobre
la malla durante el apagón (OP-6). Existen issues numeradas para cada uno.
