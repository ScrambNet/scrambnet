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

## 5. El handshake de circuito (no existe — es Sphinx)

La suite una vez nombró `Noise_XK_25519_ChaChaPoly_BLAKE2s` como un «handshake de
circuito» que nada especificaba, un defecto I-1: un implementador hostil no podía
construir un nodo interoperable, porque no había transcripción que construir. **La
resolución es borrar la línea.** Sphinx ya realiza el acuerdo de clave por salto que
un circuito necesita, así que un handshake Noise separado es un vestigio —muy
probablemente heredado del linaje de los «handshakes Noise» de WireGuard sin notar
que Sphinx ya se había comido el trabajo. Esta sección registra esa decisión y
especifica, de forma normativa, el handshake que Sphinx *es*, de modo que I-1 se
cumple por especificación, no por un segundo protocolo.

**La decisión, en un párrafo.** `alpha` (SP-3, 32 B, X25519) es un *efímero de
cliente por paquete*; cada relé deriva el secreto de salto a partir de `alpha` y de su
clave estática `onion` (GR-2 clave 2). Eso es Diffie-Hellman efímero–estático por
salto, forward-secret *con granularidad de época* (CH-6), autenticado al relé mediante
la firma Ed25519 del registro de gossip —exactamente lo que un circuito necesita y
todo lo que necesita. Un segundo handshake `Noise_XK` con estado volvería a ejecutar el
mismo DH, añadiría viajes de ida y vuelta que una parte dispersada de un solo disparo no
puede permitirse, pondría un segundo formato de cable en el enlace que I-4 tendría
entonces que blanquear, y compraría **una** propiedad de la que Sphinx carece: ocultar
la clave estática del *iniciador*. El cliente de circuito de ScrambNet **no tiene clave
estática alguna** (es anónimo por construcción), así que esa propiedad es vacua. `XK`
autentica maquinaria para una clave que no existe. Reemplazar Sphinx con XK (más viajes
de ida y vuelta por menos), o usar XK para un canal lateral (todo flujo con estado
cliente↔relé —gossip GR-6, sondeo GR-12/GR-13— se tuneliza deliberadamente *a través*
de Sphinx para que el cliente permanezca sin nombre, así que ningún canal de ese tipo
quiere una sesión directa) fracasan ambos a la inspección. La especificación mejora al
borrar la línea.

```
  THE "HANDSHAKE" IS THE SPHINX HEADER. NOTHING ELSE EXISTS.

  cliente (sin clave estática)     guardia G        medio M           salida X
  ─────────────────────     ───────          ────────          ──────
   por paquete: elige UN efímero x ; alpha_0 = x·B   (B = base X25519)
        │
        │  paquete de parte  [ alpha_0 | beta | gamma | delta ]   (SP-3)
        │────────────────────────▶│
        │     G: s_G = DH(alpha_0, onion_G) ─► clave de salto; pela una capa beta
        │     G: alpha_1 = blind(alpha_0)   (re-aleatorización Sphinx)
        │                          │────────────────▶│
        │                          │  M: s_M = DH(alpha_1, onion_M) ─► clave de salto
        │                          │                  │──────────▶│
        │                          │                  │  X: s_X = DH(alpha_2, onion_X)
        ▼                          ▼                  ▼           ▼
   SIN RTT de handshake. SIN segundo formato de cable. SIN mensaje Noise. El DH es
   efímero(cliente)·estático(relé) en CADA salto, llevado enteramente en `alpha`.

   Lo que Noise XK habría añadido, y por qué se borra:
      → e ; ← e,ee,s,es ; → s,se   (RTT extra, el relé nombra una sesión, y el
      tercer mensaje lleva la estática del INICIADOR que XK existe para ocultar —que
      nuestro cliente sin clave no tiene, así que no hay nada que enviar ni razón para ejecutarlo)
```

- **CH-1 (borrar el vestigio).** La suite `0x01` **no** tiene handshake Noise; la
  fila de la tabla de suites de la Parte 0 se elimina. Una implementación NO DEBE (MUST NOT)
  emitir, esperar ni negociar ningún mensaje de handshake Noise en un circuito; un
  paquete que no es un paquete de parte de la Parte 1 no forma parte de este protocolo.
  *Atácalo nombrando una operación de circuito que la cabecera Sphinx no pueda realizar
  —una revisión hostil lo intentó y no encontró ninguna.*
- **CH-2 (el handshake de circuito es la cabecera Sphinx).** El acuerdo de clave por
  salto DEBE (MUST) ser la construcción Sphinx de SP-3/SP-4: para cada salto `i`, el relé
  calcula `s_i = X25519(alpha_i, onion_i)` donde `alpha_i` es el elemento de grupo
  cegado que recibe y `onion_i` es su clave estática (GR-2 clave 2). Todas las claves de
  salto (cifrador de flujo de la información de enrutamiento, el MAC `gamma`, el AEAD
  `delta`) DEBEN (MUST) derivarse de `s_i` mediante HKDF-BLAKE2s con etiquetas fijas
  distintas (`"sphinx-rho"`, `"sphinx-mu"`, `"sphinx-delta"` —bytes exactos bloqueados por
  vectores bajo roadmap 3.2). No hay ningún otro acuerdo de clave en la capa de circuito.
- **CH-3 (el iniciador es sin clave, por construcción).** Un cliente de circuito NO DEBE (MUST NOT)
  poseer ni presentar ninguna clave estática de largo plazo en la ruta del circuito. Su
  único secreto asimétrico es el **escalar efímero por paquete** `x` detrás de `alpha_0`,
  que DEBE (MUST) muestrearse de nuevo desde un CSPRNG por paquete (aplica roadmap 3.1 —el
  forward secrecy de abajo es exactamente tan fuerte como este RNG) y destruirse tras
  construir el paquete. Sin clave estática de cliente, ningún patrón de ocultación del
  iniciador tiene nada que ocultar; `XK`/`IK`/`KK` son todos inaplicables a la ruta del
  circuito (CH-7).
- **CH-4 (autenticación estática del relé, sin firma de handshake).** Un cliente DEBE (MUST)
  obtener la clave estática `onion` de cada relé *solo* de un registro de gossip cuya firma
  Ed25519 (GR-2 clave 7) sobre la codificación canónica —que cubre la clave 2— haya
  verificado (GR-4). La autenticación del relé es **fuera de línea y transferible**: una vez,
  cuando el registro se valida, no interactivamente por circuito. NO DEBE (MUST NOT) haber una
  firma del relé dentro del circuito (sería un selector y una huella de cable, I-4). El límite
  honesto: un cliente autentica *la clave*, no una *identidad más allá de esa firma* —el residuo
  de sybil/eclipse vive en la Parte 2 (OP-2, GR-19a/GR-20a), no aquí.
- **CH-5 (rotación de la clave estática — la ventana de exposición de ≤7 días).** Un relé DEBE (MUST)
  rotar su clave estática `onion` al menos cada `7 days` (s), y DEBE (MUST) poner a cero la
  mitad privada de una clave retirada una vez pasado el período de gracia en vuelo; un relé que
  retiene estáticas viejas agranda su propia ventana de exposición y no es conforme. Los clientes
  DEBEN (MUST) rechazar un registro cuyo `expiry` exceda `created + 7 days` (GR-2 clave 6). El
  techo de rotación se impone en ambos extremos y es el techo de la ventana de compromiso
  estático (CH-6).
- **CH-5a (la brecha `ee`, y la corrección que no es XK).** Una revisión hostil nombró la única
  propiedad que cuesta el borrado: como el DH de salto es efímero(cliente)·**estático**(relé), un
  adversario que registra el tráfico de enlace de un relé y luego se apodera de su estática `onion`
  *dentro de la época viva* puede recalcular los secretos por salto de esa época y recuperar la
  **enlazabilidad** de un salto durante hasta 7 días de paquetes registrados (nunca contenido —CH-6).
  Un `ee` de Noise negaría incluso eso. Esto es una regresión real respecto a un handshake
  *interactivo completo*, pero **no** es razón para mantener `XK` (cuya ocultación del iniciador no
  la cierra) y es cerrable sin un handshake: un despliegue que juzgue la ventana demasiado ancha
  DEBE (MUST) o bien (a) **acortar la rotación** por debajo de 7 días (CH-5 es un techo, no un
  objetivo), o bien (b) añadir una **pre-clave de relé `ee` opcional** —una pre-clave efímera de
  vida corta publicada en el registro de gossip, mezclada en el secreto de salto a **cero** viajes
  de ida y vuelta extra— rotada y destruida de modo que un apoderamiento tardío de la estática no
  rinda nada durante su tiempo de vida. El campo de registro de la pre-clave y su rotación
  pertenecen a GR-2 si un despliegue la adopta; CH-5a solo resuelve que la brecha es real, acotada
  a la enlazabilidad, y cerrable sin el handshake borrado.
- **CH-6 (el enunciado del forward secrecy, con precisión).** `[claim-critical]` Un adversario que
  compromete la clave privada **estática** `onion` del relé `R` en el instante `T` (y nada más —los
  efímeros nunca salieron de los clientes y fueron destruidos, CH-3):
  (a) **el tráfico pasado está a salvo entre épocas** —los paquetes cuyo salto en `R` usó una
  estática anterior, rotada-y-destruida, no son descifrables (la clave ya no está, CH-5; el
  logaritmo discreto del efímero del cliente ya no está, CH-3); el forward secrecy es con
  granularidad de época, siendo la rotación de ≤7 días esa granularidad. (b) **Dentro de la época
  viva, la exposición es la *enlazabilidad* de un salto, nunca contenido** —para los paquetes
  enviados mientras la estática apoderada estaba viva, el adversario recalcula `s_i` para los saltos
  en `R` y pela la capa de `R`, aprendiendo el predecesor/sucesor de `R`, es decir, los metadatos que
  un relé malicioso ya ve. No rinde **ningún** contenido: incondicional por debajo de `k` (I-2, Parte
  7), y por encima de `k` el AEAD extremo a extremo se cifra a partir de una `kpair` simétrica
  precompartida sin ninguna transcripción DH que la clave apoderada pueda tocar (SP-1a). Una estática
  apoderada compra *la enlazabilidad de un salto sobre los paquetes de una época* —exactamente la
  correlación guardia+salida que el diseño de dispersión/disjunción ya trata como *mitigada, no
  eliminada*; comprometer la estática no mueve al adversario más allá de lo que *operar* ese relé ya
  hace.
- **CH-7 (la ocultación del iniciador no es necesaria; el salto tiene forma `N`, no `XK`).**
  `[claim-critical]` ¿Necesita el cliente la propiedad de estática-de-iniciador-oculta de XK? **No**,
  de forma dispositiva: el cliente no tiene clave estática de iniciador (CH-3), así que la propiedad es
  vacua. En el vocabulario de Noise, el salto de un solo disparo es un acuerdo unidireccional, de
  iniciador-efímero, respondedor-de-estática-conocida —la forma de Noise `N` (`→ e, es`), no de `XK`.
  El circuito no usa ningún mensaje Noise literal (CH-2: es Sphinx, que subsume esta forma); los dos
  mensajes que XK añade más allá de `N` no llevan nada y existen solo para autenticar una clave que no
  tenemos. La ocultación del iniciador ya la provee de forma más fuerte Sphinx (uniformidad de SP-4; el
  cliente nunca es un extremo que un relé pueda nombrar, GR-12). Reemplazamos la ocultación del
  iniciador de XK por *«el iniciador es anónimo y sin clave»*, que no necesita ningún patrón para
  ocultar lo que no está ahí.
- **CH-8 (las sesiones relé↔relé, si acaso, quedan fuera de esta parte y no son `XK`).** Un futuro canal
  de control o de emparejamiento que necesite una sesión con estado, bidireccional y mutuamente
  autenticada entre dos partes **nombradas** (p. ej., cifrado de enlace relé-a-relé) es un documento
  separado y DEBE (MUST) satisfacer igualmente I-4 (CH-9). Incluso ahí `XK` es incorrecto: las estáticas
  de ambos relés son **públicas** en sus registros de gossip, así que no hay nada que ocultar y encaja un
  patrón de estática-ya-conocida (`IK`/`KK`). Esta sección no especifica tal canal; solo impide
  reimportar `XK` por reflejo.
- **CH-9 (I-4 por no tener un segundo formato de cable).** `[claim-critical]` La capa de circuito no
  pone nada en el cable salvo paquetes de parte de la Parte 1, cada byte uniforme (SP-4). **No** hay
  ningún mensaje de handshake Noise que uniformizar —el resultado I-4 más limpio, logrado por *no tener*
  un segundo protocolo. Una transcripción Noise XK tiene estructura reconocible (patrón de longitud de
  mensaje, campos de clave pública `e`/`s`); mantener XK habría *añadido* un requisito de ofuscación que
  el borrado elimina. Cualquier futuro canal de sesión (CH-8) hereda esta obligación en su propio
  documento.

**Lo que la sección 5 no decide.** Los parámetros de Sphinx en sí (grupo, cegado, MAC, etiquetas HKDF
exactas y encadenamiento) son §3 y los vectores del roadmap 3.2; CH-2 los referencia. Poscuántico: la
suite `0x02` puede reemplazar el DH de salto X25519 por un KEM PQ —la *forma* del forward secrecy de CH-6
no cambia (efímero + rotación estática de ≤7 días), cambia la primitiva, y el umbral de contenido de I-2
es PQ-seguro en todo caso (SP-1a). El canal relé↔relé (CH-8) y el campo opcional de pre-clave `ee` (CH-5a)
se dejan a partes futuras. CH-4 autentica una *clave que un registro firmó*, no una identidad más allá de
ella: el residuo de gossip/eclipse es de la Parte 2 (OP-2).

## 6. Lo que esta parte no decide

La selección de rutas y la imposición de la disjunción (OP-1), los parámetros de mezcla (OP-5),
la fragmentación (SP-8), la economía de los señuelos (SP-9) están abiertos a propósito. Cada uno tiene una
issue numerada; discute allí, con números.
