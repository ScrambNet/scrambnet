# Especificación de ScrambNet — Parte 1: Paquete de parte
> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../../en/spec/01-share-packet.md)).

**Estado: BORRADOR (DRAFT).** Los tamaños provisionales se marcan con `(s)`. Atácalos por número de requisito.

## 1. Alcance

El paquete de parte es la única unidad que cruza la superposición: lleva una parte de
un mensaje a través de un circuito de cebolla. Todo en esta parte sirve a dos objetivos:
el umbral incondicional (I-2) y la uniformidad del cable (I-4).

## 2. Estratificación

```
mensaje en texto en claro
  └─ AEAD extremo a extremo (clave de par precompartida, SP-1a)  [computacional]
       └─ división de Shamir: n partes, umbral k           [umbral incondicional]
            └─ cifrado de cebolla por parte, circuito propio, formato Sphinx
                 └─ transporte camaleón (Parte 4)
```

- **SP-1.** El remitente DEBE (MUST) aplicar el cifrado extremo a extremo *antes* de la dispersión, y
  la dispersión DEBE (MUST) aplicarse al texto cifrado extremo a extremo. Con menos de `k`
  partes el adversario no aprende nada sobre el texto cifrado de forma incondicional
  (Shamir); con `k` partes o más aún se enfrenta al AEAD extremo a extremo. El
  umbral incondicional y el cinturón computacional se componen; ninguno reemplaza al
  otro. El cinturón se demuestra de extremo a extremo en `poc/e2e.py`
  (cifrar → dividir → reconstruir → descifrar, fallo cerrado ante manipulación).
- **SP-1a (establecimiento de la clave de contenido, y la consecuencia poscuántica).**
  La clave AEAD extremo a extremo DEBE (MUST) derivarse del **secreto simétrico de par
  precompartido** `kpair` que lleva la tarjeta de contacto (Parte 6, RZ-2), mediante un KDF
  separado por etiqueta: `content_key = HKDF-BLAKE2s(kpair, "e2e-content")`, distinta de la
  clave de etiqueta de SP-7 y de la clave de box-id derivadas del mismo `kpair`. NO DEBE
  (MUST NOT) haber ningún acuerdo de clave asimétrico en la ruta de contenido. Esta es una
  elección deliberada con una consecuencia portante: un adversario `≥k` que lo registra todo
  y que dispone en el futuro de un computador cuántico a gran escala aún no puede leer el
  contenido, porque no existe ninguna transcripción de Diffie-Hellman que Shor pueda romper
  —solo un secreto simétrico que las partes ya comparten, y Grover le cuesta al AEAD, como
  mucho, reducir a la mitad la fuerza de su clave (de ahí que se RECOMIENDE (RECOMMENDED)
  una clave derivada de ≥256 bits allí donde el margen importa). Por tanto, "harvest now,
  decrypt later" («cosechar ahora, descifrar después») queda derrotado en **ambos** niveles:
  por debajo de `k` mediante Shamir (incondicional), en `k` o por encima mediante un AEAD
  simétrico bajo una clave precompartida (sin suposición de clave pública que cosechar). El
  coste honesto es el **arranque (bootstrap)**: `kpair` debe llegar primero al destinatario
  por un canal confidencial previo (el intercambio fuera de banda de la tarjeta de contacto,
  Parte 6). Cualquier suposición residual de clave pública o PQ-KEM vive ahí, en el
  intercambio de la tarjeta —no en la ruta de contenido—, y llevar un intercambio de tarjeta
  que sea él mismo poscuántico es una elección ortogonal y estratificada, no una condición
  previa para el umbral incondicional. La suite AEAD es ChaCha20-Poly1305 (suite `0x01`); `msg_nonce` (SP-7)
  es el nonce del AEAD, lo que vincula las dos capas y hace que un nonce reutilizado sea
  doblemente fatal (colisión de etiqueta de SP-7 *y* pérdida de confidencialidad del AEAD
  —ver SP-7).
- **SP-2.** Parámetros de dispersión por defecto para mensajería: `n = 4`, `k = 3` (s).
  Los perfiles de transferencia masiva PUEDEN (MAY) usar la IDA de Rabin en lugar de Shamir, y DEBEN (MUST)
  etiquetarse como computacionales en la interfaz del cliente, porque la IDA no tiene umbral
  incondicional (OP-3).

## 3. Formato de cable

- **SP-3.** Todo paquete en todo enlace DEBE (MUST) tener exactamente `P = 2048` bytes (s).
- **SP-4.** Cada byte del paquete DEBE (MUST) ser indistinguible de aleatorio
  uniforme para un observador sin las claves pertinentes, en cada salto (propiedad
  Sphinx; I-4). En particular no hay versión, suite, longitud,
  contador de saltos ni índice de parte en claro.

Disposición (tamaños hombre de paja, máximo de 3 saltos):

| Campo | Tamaño (s) | Visible para |
|---|---|---|
| `alpha` — elemento de grupo Sphinx (X25519) | 32 B | todos (uniforme) |
| `beta` — información de enrutamiento Sphinx, 3 × 48 B, rellenada | 144 B | pelado por salto |
| `gamma` — MAC por salto | 16 B | salto actual |
| `delta` — carga útil, envuelta en AEAD por salto | 1856 B | tramo salida → destinatario |

- **SP-5.** Los relés DEBEN (MUST) mantener una caché de repetición de valores `gamma` vistos por época
  de clave y DEBEN (MUST) descartar las repeticiones en silencio (defensa de repetición Sphinx estándar).
- **SP-6.** Los relés DEBEN (MUST) emitir paquetes en lotes de tamaño constante con
  jitter definido por la implementación en modo rápido, y DEBEN (MUST) seguir la estrategia de mezcla
  (stop-and-go o mezcla Poisson, por determinar) en modo paranoico. La elección de estrategia es
  territorio de OP-5 y deliberadamente sin resolver aquí.

## 4. Carga útil de la parte (dentro de `delta`, al final del circuito)

Descifrada solo por el destinatario:

| Campo | Tamaño (s) | Notas |
|---|---|---|
| `tag` | 16 B | etiqueta PRF con clave del destinatario, ver SP-7 |
| `index` | 1 B | índice de parte `1..n` |
| `params` | 1 B | `k`, `n` empaquetados (4 bits cada uno) |
| `share` | 1792 B | bytes de la parte de Shamir |
| `pad` | resto | aleatorio |

- **SP-7 (sin enlazabilidad entre rutas).** Dos partes del mismo mensaje NO DEBEN (MUST NOT)
  llevar ningún valor igual o correlacionable observable por nadie salvo el
  destinatario. La pertenencia al conjunto de partes se señaliza solo por `tag`:
  `tag = PRF(K_r, msg_nonce ‖ index)` donde `K_r` es una clave en poder del destinatario y
  `msg_nonce` se transporta dentro de la capa extremo a extremo. Un relé de salida, o una
  coalición de salidas, NO DEBE (MUST NOT) poder decir si dos paquetes pertenecen al
  mismo mensaje. Este requisito es portante: sin él, la dispersión
  se degrada a una comodidad de enumeración para el adversario.
- **SP-7a (integridad de la parte: residuo de fallo cerrado aceptado).** El `tag` dice
  *a qué* mensaje afirma pertenecer un paquete; **no** autentica los bytes de la
  `share` ni el byte de `params` (`k,n`). La reconstrucción de Shamir no tiene integridad
  propia, así que un salto hostil o una salida que invierta bits en una parte —o mienta
  sobre `k,n`— produce un candidato de texto en claro coherente-pero-erróneo que Shamir no
  puede detectar. Esto se **atrapa una capa más arriba**: el AEAD extremo a extremo (SP-1a)
  falla su etiqueta ante cualquier reconstrucción corrupta y el destinatario descarta el
  mensaje en lugar de actuar sobre basura (demostrado en `poc/dispersal.py`, test
  `test_tampered_share_fails_closed`). El residuo es, por tanto, **no una pérdida de
  confidencialidad sino una denegación de servicio dirigida**: un único punto de observación
  malicioso en una de las `n` rutas de parte puede hacer que un mensaje concreto no logre
  reconstruirse, al coste de un solo bit invertido. El veredicto para este borrador es
  **aceptar y documentar** ese residuo en lugar de añadir un MAC por parte, por dos razones:
  (1) un autenticador por parte gastaría bytes de carga útil e introduciría una segunda clave
  que gestionar sin eliminar la DoS —un salto que puede corromper una parte puede igualmente
  *descartarla*, y `n−k` de tales pérdidas ya se toleran por diseño—; (2) el AEAD ya hace que
  el fallo sea seguro (fallo cerrado), así que la cuestión abierta es la disponibilidad, no el
  secreto. Las mitigaciones honestas son la redundancia (margen `n−k`), la disjunción de rutas
  de modo que ningún punto de observación único se sitúe en `k` de las `n` rutas (OP-1), y el
  reintento por rutas nuevas. Una revisión futura PUEDE (MAY) añadir un enlace por parte
  opcional para perfiles críticos en disponibilidad; deliberadamente no se exige aquí. `k,n`
  está bloqueado por vectores (orden de nibbles, vectores de la Parte 3 §3.2) de modo que una
  implementación no puede discrepar *accidentalmente*, solo una parte maliciosa puede mentir.
- **SP-7b (sin `tag` igual entre drops coludidos, y propiedad del nonce).** La propiedad que debe
  cumplirse: ningún par de paquetes que una coalición de drops pueda ver lleva un `tag` igual a
  menos que el remitente haya reutilizado un par `(msg_nonce, index)`. *Argumento:*
  `tag = PRF(K_r, msg_nonce ‖ index)` con `msg_nonce` unos 8 bytes fijos e `index` un byte fijo, de
  modo que la entrada de la PRF es una codificación de anchura fija e inequívoca de
  `(msg_nonce, index)` —la aplicación `(msg_nonce, index) ↦ entrada` es inyectiva. Una PRF BLAKE2s
  con clave da salidas iguales solo ante entradas iguales (salvo una colisión de ~`2^-128`), así que
  etiquetas iguales implican un `(msg_nonce, index)` igual. Las `n` partes de un mensaje comparten un
  mismo `msg_nonce` pero usan índices *distintos* `1..n`, de ahí entradas distintas, de ahí etiquetas
  distintas: una coalición de drops no puede distinguir dos partes de un mensaje de dos paquetes sin
  relación. Dos mensajes *diferentes* colisionan un `tag` solo si reutilizan un `msg_nonce`. Por tanto
  **la propiedad del nonce es un DEBE (MUST)**: un remitente NO DEBE (MUST NOT) reutilizar un
  `msg_nonce` bajo un mismo `kpair`. La reutilización es doblemente fatal —colisiona las etiquetas de
  SP-7 (haciendo enlazable un conjunto de partes) *y*, porque `msg_nonce` es el nonce del AEAD
  (SP-1a), destruye la confidencialidad de ChaCha20-Poly1305 (un bloc de un solo uso usado dos veces,
  fijado por `test_nonce_reuse_is_detectable_catastrophe`). Un contador de mensajes por `kpair`
  estrictamente creciente satisface esto; la marca de nivel máximo (high-water mark) del contador DEBE
  (MUST) sobrevivir a los reinicios. En la capa de almacenamiento, un drop DEBE (MUST) descartar un
  redepósito de un `(box_id, slot)` ya almacenado (repetición) y desaloja primero el más antiguo bajo
  el tope por buzón (RZ-7), de modo que un depósito repetido ni multiplica ni desplaza correo honesto
  más allá del tope declarado.
- **SP-8.** Un mensaje que no llena la carga útil de la parte (`1792` bytes, menos
  el prefijo de longitud de 2 bytes) DEBE (MUST) rellenarse con bytes aleatorios antes de dividirse;
  un mensaje que la excede se fragmenta en una capa por encima de esta
  (diseño de fragmentación por determinar, interactúa con OP-4). El precio honesto de Shamir: cada
  parte es tan larga como el secreto, así que una dispersión (n, k) transmite ×`n` el
  volumen de texto cifrado (OP-3).
- **SP-9 (temporización).** El remitente NO DEBE (MUST NOT) emitir las `n` partes como una ráfaga
  simultánea. Las partes DEBERÍAN (SHOULD) emitirse con un retardo aleatorizado por parte; la
  distribución y su coste en latencia son OP-4 y están sin resolver. Los clientes PUEDEN (MAY)
  emitir partes señuelo (paquetes con `tag` aleatorio) a una tasa configurable.

## 5. Lo que esta parte no decide

La selección de rutas y la imposición de la disjunción (OP-1), los parámetros de mezcla (OP-5),
la fragmentación (SP-8), la economía de los señuelos (SP-9) están abiertos a propósito. Cada uno tiene una
issue numerada; discute allí, con números.
