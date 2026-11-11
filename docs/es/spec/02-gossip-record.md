# Especificación de ScrambNet — Parte 2: Registro de gossip
> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../../en/spec/02-gossip-record.md)).

**Estado: BORRADOR (DRAFT).** Valores provisionales marcados con `(s)`. Las cuestiones de sybil/eclipse en las que esta
parte se apoya son OP-2 y están deliberadamente abiertas.

## 1. Alcance

El registro de gossip es el descriptor autofirmado por el que un relé existe. No hay
directorio, ni autoridad, ni registro (I-3): un relé es el conjunto de registros
que firma, y el mapa de la red es la muestra verificable que tenga cada cliente.

## 2. Formato del registro

- **GR-1.** Un registro es un mapa CBOR canónico (RFC 8949 §4.2.1), de a lo sumo
  `1024` bytes (s) codificados. Los registros mayores DEBEN (MUST) descartarse sin leer.
- **GR-2.** Campos (claves enteras; las claves desconocidas DEBEN (MUST) ignorarse por compatibilidad
  hacia adelante, pero están cubiertas por la firma):

| Clave | Nombre | Tipo | Notas |
|---|---|---|---|
| 0 | `v` | uint | versión de formato, `1` |
| 1 | `id` | bytes(32) | clave pública de identidad Ed25519 — el nombre del relé |
| 2 | `onion` | bytes(32) | clave X25519 para handshakes de circuito; DEBE rotar ≤ 7 días (s) |
| 3 | `addrs` | array | puntos finales: pares `[transport-id uint, blob bytes]` |
| 4 | `bw` | uint | ancho de banda sostenido declarado, kB/s — una *afirmación*, ver GR-7 |
| 5 | `created` | uint | tiempo unix, DEBE redondearse hacia abajo a la hora (GR-5) |
| 6 | `expiry` | uint | tiempo unix, DEBE ser ≤ `created` + 7 días (s) |
| 7 | `sig` | bytes(64) | Ed25519 sobre la entrada de firma de la §2A (GR-24); el perfil de codificación y verificación es la §2A |

- **GR-3.** Un relé NO DEBE (MUST NOT) publicar afirmaciones geográficas o jurisdiccionales sobre
  sí mismo. Los clientes infieren el AS y la jurisdicción a partir de `addrs` con sus propios datos
  (OP-1); la ubicación autodeclarada es una superficie de ataque, no información.
- **GR-4.** La validez de la firma, el tope de tamaño, la expiración y el redondeo de marca de tiempo DEBEN (MUST) todos
  comprobarse antes de que un registro se almacene o reenvíe; los fallos se descartan
  en silencio — ningún error que distinga «malformado» de «expirado» puede ser
  observable por el remitente del registro.
- **GR-5.** El redondeo de `created` existe para frenar el fingerprinting de relés por deriva de
  reloj. Los clientes DEBEN (MUST) tratar dos registros con el mismo `id` como un solo relé y
  conservar solo el `created` más fresco.

## 2A. Codificación canónica y perfil de verificación

GR-1 nombra «CBOR canónico (RFC 8949 §4.2.1)» y GR-4 exige la validez de la firma antes
de almacenar o reenviar, pero §4.2.1 deja abiertas elecciones de codificación y la
verificación Ed25519 diverge célebremente entre bibliotecas (Chalkias et al.,
*Taming the Many EdDSAs*; la escisión ZIP-215 frente a RFC 8032). Para una red I-1
cualquiera de las dos lagunas es fatal: dos nodos que discrepan sobre los bytes canónicos de
un registro, o sobre si una firma es válida, rechazan los registros válidos del otro (una
partición) o se escinden ante un registro fabricado (una vista-escindida relevante para la
seguridad que alimenta las amenazas de equivocación ID-8/ID-10 y de steering PS-17). Esta
sección fija ambas al byte. Todas las de GR-21..GR-28 son constituyentes de la «validez de la
firma» tal como GR-4 usa el término y DEBEN (MUST) imponerse antes de que un registro se
almacene o reenvíe, con el fallo silencioso y uniforme de GR-4. Todo el perfil se vuelve
comprobable mecánicamente mediante los vectores `records` (GR-30) y se demuestra en
`poc/gossip.py`, cuyo Ed25519 se contrasta bit a bit contra una biblioteca independiente.

- **GR-21 (forma más corta, longitud definida, solo cuatro tipos).** Todo entero y toda
  longitud en un registro DEBE (MUST) usar la cabecera CBOR más corta (serialización
  preferida, RFC 8949 §4.2.1): un decodificador DEBE (MUST) rechazar cualquier cabecera que no
  sea la más corta (p. ej. `0x18 0x0a` para `10`). Todos los mapas, arrays y cadenas de bytes
  DEBEN (MUST) ser de longitud definida; los ítems de longitud indefinida DEBEN (MUST)
  rechazarse. Los únicos tipos mayores CBOR permitidos en cualquier lugar de un registro son
  entero sin signo (mayor 0), cadena de bytes (mayor 2), array (mayor 4) y mapa (mayor 5) —
  exactamente los que usa GR-2. Los enteros negativos, las cadenas de texto, los flotantes, las
  etiquetas, los valores simples (incluidos `false`/`true`/`null`) y cualquier otro tipo mayor
  o cabecera DEBEN (MUST) rechazarse. Esto, con GR-21a, hace la canonicalización **total**:
  toda cadena de bytes o bien decodifica a exactamente un registro o bien se rechaza (I-1).
- **GR-21a (la forma de las claves 0–7 está fijada, no solo su tipo CBOR).** Un campo cuyo
  valor es un tipo compuesto es una ambigüedad de canonicalización a menos que su forma interna
  esté fijada: dos implementaciones se escindirían, de otro modo, ante un registro con firma
  válida cuyo campo compuesto una lee como bien formado y la otra no (la clave 3 `addrs` es el
  caso vivo — nunca se cripto-decodifica, así que ninguna comprobación posterior rescata la
  escisión). Por tanto, las formas de las claves conocidas DEBEN (MUST) imponerse como un
  predicado de rechazo, no tratarse como convención: la clave 0 `v` y la clave 4 `bw`, la clave
  5 `created`, la clave 6 `expiry` DEBEN (MUST) ser enteros sin signo (GR-21); la clave 1 `id`
  y la clave 2 `onion` DEBEN (MUST) ser cadenas de bytes de exactamente 32 bytes; la clave 7
  `sig` DEBE (MUST) ser una cadena de bytes de exactamente 64 bytes; la clave 3 `addrs`
  DEBE (MUST) ser un array (que PUEDE (MAY) estar vacío) cada uno de cuyos elementos DEBE (MUST)
  ser un array de exactamente dos ítems, el ítem 0 un entero sin signo (el id de transporte) y
  el ítem 1 una cadena de bytes de longitud `≤ N_addr = 256` (s) (el blob de punto final).
  Cualquier otra forma de una clave conocida DEBE (MUST) rechazarse como un fallo de
  canonicalización (GR-23/GR-29). Las claves desconocidas ≥ 8 están firmadas-pero-ignoradas
  (GR-2) y PUEDEN (MAY) llevar cualquier valor legal según GR-21 de cualquier forma; solo las
  claves 0–7 tienen la forma fijada.
- **GR-22 (orden ascendente de claves enteras, totalmente fijado para las claves desconocidas).**
  Las claves del mapa DEBEN (MUST) ser enteros sin signo codificados en la forma más corta
  (GR-21) y DEBEN (MUST) aparecer en orden numérico estrictamente ascendente. Como las claves
  son enteros sin signo en forma más corta, el orden bytewise-lexicográfico de la clave
  codificada de RFC 8949 §4.2.1 **coincide exactamente con el orden numérico ascendente para
  todos los valores de clave** (una cabecera de un byte `0x00`–`0x17` siempre ordena antes que
  cualquier cabecera multibyte, y dentro de un ancho fijo el orden big-endian es el orden
  numérico); la sutileza «bytewise ≠ numérico más allá de 23» de §4.2.1 existe solo para las
  codificaciones que no son la más corta, que GR-21 prohíbe. Las claves desconocidas ≥ 8 se
  permiten por compatibilidad hacia adelante (GR-2) y DEBEN (MUST) ordenarse por esta misma
  regla ascendente-numérica. Las claves DEBEN (MUST) ser únicas; un mapa que contenga la misma
  clave dos veces DEBE (MUST) rechazarse (el clásico eludir-la-firma donde dos analizadores
  discrepan sobre cuál duplicado gana). Hay así exactamente un orden de claves legal para
  cualquier conjunto de claves, conocidas o desconocidas (I-1).
- **GR-23 (verificar sobre los bytes recibidos; la codificación en el cable DEBE (MUST) ser ya
  canónica).** Un verificador DEBE (MUST) exigir que los bytes del registro recibido sean la
  codificación canónica definida por GR-21/GR-21a/GR-22 y DEBE (MUST) rechazar cualquier
  registro cuyos bytes recibidos no sean canónicos — orden de claves erróneo, cabecera que no es
  la más corta, longitud indefinida, un tipo no permitido, una clave duplicada, un campo
  conocido mal formado (GR-21a), un ítem de nivel superior que no es un mapa (mayor 5), o
  cualquier byte final tras el mapa de nivel superior. (Como todo contenedor es de longitud
  definida, GR-21, el único lugar donde pueden aparecer «bytes finales» es tras el ítem de nivel
  superior; una implementación NO DEBE (MUST NOT) inventar una comprobación de bytes-finales-
  internos que rechazaría un registro canónico.) El verificador NO DEBE (MUST NOT)
  re-canonicalizar y luego verificar sobre los bytes re-codificados; verifica la firma sobre
  **exactamente los bytes recibidos** (GR-24). Esto es lo que hace total la máxima de GR-2 «las
  claves desconocidas están cubiertas por la firma pero se ignoran para la semántica»: la
  canonicalización se define sobre el mapa **completo**, incluidas las claves desconocidas, el
  orden de las desconocidas está fijado (GR-22), y un verificador nunca necesita reproducir la
  codificación que un firmante dio a una clave que no entiende — solo comprueba que los bytes
  que recibió son ellos mismos canónicos. Un nodo que tolera un registro no canónico en el cable
  donde otro nodo lo rechaza es un defecto I-1.
- **GR-24 (la entrada de firma es byte-exacta y está separada por dominio).** El mensaje firmado
  para la clave 7 de GR-2 es

  ```
  "ScrambNet-gossip-v1" ‖ 0x00 ‖ canon( record without key 7 )
  ```

  donde la etiqueta es exactamente los 19 bytes ASCII `ScrambNet-gossip-v1`, `0x00` es un único
  byte separador, y `canon(record without key 7)` es la codificación canónica
  GR-21/GR-21a/GR-22 del mapa del registro con **la clave 7 omitida por completo** — el conteo
  de la cabecera del mapa refleja las claves restantes (p. ej. 7, no 8), y la clave 7 está
  ausente, **no** presente-con-un-valor-vacío — incluida toda clave desconocida ≥ 8 en orden
  ascendente. La etiqueta-más-separador es un prefijo de separación de dominio (que coincide con
  la convención de etiqueta suite-`0x01` de `"e2e-content"`/`"box"`/`"tag"`) que DEBE (MUST)
  estar presente, de modo que la firma de un registro nunca pueda reinterpretarse como una firma
  sobre el mensaje de otro protocolo u otra versión. La firma es Ed25519 puro (RFC 8032, sin
  pre-hash) sobre estos bytes exactos. Para verificar, un nodo reconstruye esta entrada de firma
  a partir del registro canónico recibido (GR-23) con la clave 7 eliminada y comprueba la firma
  de la clave 7 contra ella bajo la clave pública `A = id` (GR-28). Esta es la única definición
  de la entrada de firma; la fila de la clave 7 de GR-2 se remite a ella.
- **GR-25 (una ecuación de verificación: RFC 8032 sin cofactor).** La verificación de la firma
  DEBE (MUST) usar la ecuación sin cofactor de RFC 8032 `[S]·B = R + [k]·A`, donde
  `k = SHA-512(R ‖ A ‖ M) mod L`, `B` es el punto base de Ed25519, `M` es la entrada de firma de
  GR-24, y `R`, `A`, `S` se toman de la firma y de `id`. Las implementaciones NO DEBEN (MUST
  NOT) usar la ecuación de verificación con cofactor (multiplicada por `[8]`, estilo ZIP-215), y
  NO DEBEN (MUST NOT) usar una biblioteca cuyo conjunto de aceptación difiera de este perfil a
  menos que se envuelva para coincidir exactamente. ScrambNet verifica los registros de uno en
  uno (GR-4), así que el motivo de la verificación por lotes para una ecuación con cofactor no
  aplica; se requiere una única ecuación fijada para que cada nodo coincida bit a bit en la
  validez (I-1). Esta prohibición prohíbe solo la *ecuación de verificación* con cofactor `[8]`;
  **no** prohíbe las multiplicaciones escalares que GR-28 usa para la pertenencia al subgrupo.
- **GR-26 (escalar canónico S).** Un registro DEBE (MUST) rechazarse a menos que `0 ≤ S < L`,
  donde `L = 2^252 + 27742317777372353535851937790883648493` es el orden del grupo Ed25519. Una
  firma con `S ≥ L` (un escalar no reducido) es la clásica maleabilidad de Ed25519 y DEBE (MUST)
  rechazarse incluso si la aritmética comprobase de otro modo, de modo que ninguna segunda
  codificación de la misma firma sea aceptada por una biblioteca y rechazada por otra (I-1).
- **GR-27 (codificaciones canónicas de puntos para R y A).** Las codificaciones de 32 bytes de
  `R` (de la firma) y `A` (el `id`) DEBEN (MUST) ser canónicas: la coordenada y codificada
  DEBE (MUST) satisfacer `y < p` (`p = 2^255 − 19`), y una codificación con `y ≥ p`, o con el
  bit de signo puesto en la codificación no canónica de `x = 0`, DEBE (MUST) rechazarse. Una
  codificación de punto no canónica es un segundo nombre para un punto y es exactamente una
  entrada sobre la que las bibliotecas divergen; rechazarla mantiene total el conjunto de
  aceptación (I-1).
- **GR-28 (`id` es la clave pública; A y R DEBEN (MUST) ser de orden primo — probado por `[L]·P`,
  no una blacklist).** La clave 1 `id` de GR-2 **es** la clave pública Ed25519 `A` y el nombre
  del relé: la verificación la usa directamente, sin directorio ni búsqueda de clave (I-3, sin
  autoridad). Un registro DEBE (MUST) rechazarse a menos que tanto `A` como `R` decodifiquen
  (GR-27) a puntos del **subgrupo grande de orden primo** — equivalentemente, ninguno puede ser
  un punto de orden pequeño ni de orden mixto. Esta pertenencia DEBE (MUST) probarse como
  `[L]·P = 𝒪` (la identidad) **y** `P ≠ 𝒪`, calculada por multiplicación escalar por el orden
  del grupo `L`: la primera condición admite solo la identidad y los puntos de orden `L` (como
  `L` es primo, ningún orden en {2,4,8} lo divide), y la condición `P ≠ 𝒪` rechaza entonces la
  identidad misma. Una **blacklist** de codificaciones de orden pequeño **NO DEBE (MUST NOT)**
  usarse como la prueba: admite puntos de orden mixto (orden `2L`/`4L`/`8L`, que no están entre
  las ocho codificaciones de orden pequeño), y un `A` o `R` de orden mixto es precisamente una
  entrada sobre la que las ecuaciones con cofactor y sin cofactor divergen — así que una
  implementación de solo-blacklist aceptaría una firma que un nodo conforme rechaza (I-1). Tras
  GR-26/GR-27/GR-28 el conjunto de aceptación es el único conjunto estricto que todo nodo
  conforme calcula idénticamente. Un registro cuyo `id` no es un punto canónico válido de orden
  primo no tiene firmante verificable y DEBE (MUST) descartarse en silencio (GR-4).
- **GR-29 (estas son comprobaciones de GR-4; el fallo es silencioso y uniforme).** GR-21 hasta
  GR-28 son constituyentes de la «validez de la firma» tal como GR-4 usa el término. Un nodo
  DEBE (MUST) realizarlas antes de almacenar o reenviar un registro, y DEBE (MUST) descartar un
  registro que falle en silencio sin distinción observable — por error, respuesta o tiempo —
  entre un fallo de canonicalización, un campo mal formado, una firma inválida, un punto
  erróneo, una violación del tope de tamaño (GR-1), la expiración o un fallo de redondeo de
  marca de tiempo (GR-4/GR-5). El descarte silencioso uniforme es la propiedad al estilo de I-4
  que GR-4 ya exige; la disciplina de trabajo constante que la hace sostenerse frente a un
  observador de tiempos es un DEBE (MUST), impuesta como exige RI-1b de la Parte 9 (un descarte
  cuyo trabajo delata su razón no es conforme), no un mejor esfuerzo.
- **GR-29a (orden de comprobación: un registro se prueba a sí mismo antes de poder afectar al
  estado).** Las comprobaciones DEBEN (MUST) aplicarse en este orden: (1) el tope de tamaño de
  GR-1 (un registro mayor que el tope se descarta sin leer); (2) la codificación canónica y la
  forma del campo (GR-21/GR-21a/GR-22/GR-23) y la validez de la firma (GR-24..GR-28); (3) solo
  entonces el registro puede participar en la deduplicación y la frescura de GR-5. Un registro
  que falla (1) o (2) NO DEBE (MUST NOT) desalojar, reemplazar ni afectar de otro modo a ningún
  registro almacenado. Sin este orden, un relé que deduplica antes de verificar puede ser
  inducido a descartar un registro honesto y firmado en favor de uno falsificado que porta un
  `created` mayor (que luego falla la verificación y se descarta, habiendo ya desalojado el
  registro bueno) — una denegación de servicio que GR-5 invitaría de otro modo.
- **GR-30 (la conformidad se define por los vectores records).** Una implementación conforme
  DEBE (MUST) reproducir la codificación canónica y la entrada de firma de cada vector de
  registro positivo (hoja de ruta 3.2, sección `records` de `vectors.json`) byte a byte,
  DEBE (MUST) verificar cada vector positivo, y DEBE (MUST) rechazar cada vector negativo **por
  la cláusula GR específica que el vector nombra**. Aceptar un registro que un vector marca como
  «rechazar», rechazar un vector positivo, o rechazar un vector negativo por la razón
  equivocada, es no-conformidad: es exactamente la divergencia (un registro que un nodo acepta y
  otro rechaza, o viceversa) que esta sección existe para prevenir (I-1). La conformidad de
  vectores certifica el acuerdo sobre el predicado de aceptar/rechazar; no certifica el tiempo
  (GR-29, cf. RI-1b).

## 3. Intercambio y muestreo

- **GR-6.** Los registros viajan sobre circuitos establecidos y sobre la malla local
  (Parte 5), montados en lotes de tamaño fijo: un lote de gossip son `8` registros (s)
  rellenados a tamaño constante, intercambiados a lo sumo una vez por par cada `10` minutos (s).
  Un nodo responde a una solicitud de muestra con una muestra uniforme de sus registros almacenados;
  NO DEBE (MUST NOT) responder con una muestra sesgada por la identidad del solicitante (la
  palanca de eclipse obvia).
- **GR-7.** `bw` es una afirmación. Los clientes DEBERÍAN (SHOULD) verificar las afirmaciones por sondeo
  aleatorizado sobre circuitos que no revelan al sondeador, y DEBERÍAN (SHOULD) ponderar la selección de rutas
  por el ancho de banda verificado, no por el declarado. El diseño del sondeo está abierto (OP-2).
- **GR-8 (mezcla de fuentes).** La muestra almacenada de un cliente DEBE (MUST) mezclar registros de
  clases de fuente independientes — como mínimo: puente del grafo social (estilo Lox),
  intercambio de gossip y sondeo directo — y NO DEBE (MUST NOT) permitir que ninguna clase
  exceda una fracción configurable (hombre de paja 1/2) de la muestra. Esta es la
  defensa de eclipse hasta que OP-2 produzca algo más fuerte.
- **GR-9.** Las nuevas identidades son baratas por diseño (sin registro), así que nada en
  esta parte puede suponer resistencia a sybil a partir del coste de identidad. Todo mecanismo que
  necesite resistencia a sybil debe obtenerla de recursos verificados (ancho de banda,
  tiempo de actividad de larga duración observado por el cliente mismo) o del grafo social — nunca
  del registro solo.

## 4. Arranque

- **GR-10.** Un cliente nuevo DEBE (MUST) poder arrancar desde una sola línea de puente
  fuera de banda (un código QR, una cadena impresa, un mensaje de un amigo) que contenga
  un registro más una pista de transporte. El arranque sin contactos es OP-7 y está abierto.

## 5. El protocolo de sondeo de ancho de banda (cerrando GR-7)

GR-7 dice que `bw` es una afirmación y que DEBERÍA (SHOULD) verificarse mediante «sondeo
aleatorizado sobre circuitos que no revelan al sondeador», y luego declara abierto el diseño del
sondeo. Esta sección es ese diseño. El sondeo responde exactamente a una pregunta — *¿qué
throughput puedo yo, este cliente, empujar a través de este relé ahora mismo sobre un circuito
que no me nombra?* — y la responde solo para el cliente que pregunta. **No** hay ningún número de
ancho de banda publicado, compartido o autoritativo: las autoridades de ancho de banda de Tor son
precisamente el asignador central que I-3 nos niega (PS-10, GR-9), así que cada cliente deriva su
propia cifra verificada y pondera su propia selección de rutas (PS-7) por ella.

### 5.1 La medición, y de qué es función pura

- **GR-11 (el ancho de banda verificado es una automedición por cliente, nunca una cifra
  publicada).** `[claim-critical]` El ancho de banda verificado de un cliente para el relé `R`,
  escrito `vbw(R)`, DEBE (MUST) calcularse como una función determinista de entradas que el
  cliente observó **él mismo**:
  ```
      vbw(R, epoch) = probe(circuits_through_R, bytes_sent, timestamps_seen)
  ```
  y de nada que un relé, un par o cualquier tercero afirme. `vbw` es una variable
  local, no un valor de red: dos clientes honestos sondeando el mismo `R` derivarán
  valores **diferentes** de `vbw(R)` (sus rutas, su congestión, su momento), y
  esto es correcto — no hay un verdadero escalar «ancho de banda de `R`» en el que ponerse de acuerdo, solo
  *throughput que un cliente dado logró sobre una ruta dada en un momento dado* (GR-18).
  Un cliente DEBE (MUST) tratar la afirmación `bw` de un relé no sondeado como el **valor por defecto
  de bajo ancho de banda** (PS-7), nunca como su cifra; una afirmación que el cliente no ha medido
  por sí mismo tiene peso cero en la selección.

- **GR-12 (el sondeo es un ida y vuelta sellado sobre un circuito — nunca se nombra al
  sondeador).** `[claim-critical]` Un sondeo DEBE (MUST) transportarse como tráfico de circuito ordinario:
  el cliente construye un circuito cuyo **relé medido `R` es el salto intermedio**, envía
  un tren acotado de celdas con forma de paquete de cuota (Parte 1: `P = 2048` bytes fijos,
  SP-3) dirigidas a través de `R`, y mide el throughput de ida y vuelta del tren
  conforme regresa por el mismo circuito. `R` ve llegar una celda de su predecesor
  y salir hacia su sucesor — exactamente lo que ve para el tráfico realmente retransmitido — y
  **no puede ver al cliente**: el sondeador se sitúa al menos un salto más allá de la vista de `R`,
  como en cualquier circuito Sphinx (SP-4). El sondeo NO DEBE (MUST NOT) usar ningún tipo de celda, bandera, longitud
  o cadencia que lo distinga del tráfico de usuario retransmitido (I-4, y GR-13
  más abajo). Un relé que pudiera distinguir un sondeo de una carga útil podría aprobar el sondeo y
  fallar la carga útil; así que, por construcción, no se le puede dar la oportunidad.

```
  EL SONDEO SOBRE UN CIRCUITO  (R es medido; el sondeador nunca está en la vista de R)

   cliente (sondeador)    guardia G       relé R  (bajo prueba)         cola T
   ───────────────────    ─────────       ──────────────────           ──────
        │                    │                  │                      │
        │  construir circuito  C = [ G , R , T ]  (R es el salto INTERMEDIO)  │
        │───────────────────▶│                  │                      │
        │     tren de N celdas de tamaño fijo, indistinguibles de      │
        │     paquetes de cuota realmente retransmitidos (SP-3/SP-4, I-4)  │
        │════════════════════╪═════════════════▶│═════════════════════▶│
        │                    │                  │   T devuelve el tren │
        │◀═══════════════════╪══════════════════╪══════════════════════│
        │   medir: bytes_acked / (t_last − t_first)  = la muestra de   │
        │          throughput de este sondeo para R, ESTA ruta, ESTE momento │
        │                    │                  │                      │
      vbw(R) ← agregado robusto de muchas muestras así a lo largo del tiempo (GR-16) │

   Lo que R ve:  celdas de G  →  celdas a T.   Idéntico a transportar tráfico
   real.  R NO ve «cliente», NO ve «esto es un sondeo», y no puede
   comportarse bien solo-cuando-lo-observan porque no puede saber que lo observan.
   El coste lo PAGA el sondeador: envía N·P bytes que no recuperará
   como trabajo útil (GR-14).  R no puede ser forzado a inundar a una víctima, porque el
   tren regresa al SONDEADOR, nunca a un tercero nombrado por el atacante (GR-15).
```

### 5.2 Las cinco propiedades que el sondeo debe tener

- **GR-13 (indistinguibilidad — un relé no puede comportarse bien solo cuando lo observan).**
  `[claim-critical]` La propiedad anti-trampas es la uniformidad en el cable (I-4): **el tráfico de
  sondeo DEBE (MUST) ser byte a byte e instante a instante indistinguible del
  tráfico realmente retransmitido que se le pide transportar a un relé**, de modo que el relé no pueda
  condicionar su reenvío a «¿me están midiendo?». Concretamente, las celdas de sondeo
  DEBEN (MUST) ser paquetes de cuota completos de la Parte 1 (`P = 2048` bytes, SP-3), DEBEN (MUST) emitirse bajo
  la misma disciplina de agrupamiento/jitter que usa un emisor real (SP-6, SP-9), y NO DEBEN (MUST NOT)
  llevar ningún marcador específico de sondeo. Un relé que infra-sirva el tráfico real y
  sobre-sirva los sondeos tendría que distinguirlos; I-4 le niega la información
  para hacerlo. El `vbw(R)` medido es por tanto una cota inferior de lo que `R` *reenviaría*
  para el tráfico real de este cliente, porque `R` no puede distinguir ambos —
  que es justo el punto: *ataca esto encontrando un bit sobre el que el relé pueda condicionarse.*

- **GR-14 (el sondeo le cuesta al sondeador una cantidad acotada y prepagada).** Un solo
  sondeo de `R` DEBE (MUST) enviar a lo sumo `B_probe` bytes (hombre de paja: `B_probe = 1 MiB`
  repartido a lo largo de `≥ τ` segundos, `τ = 4 s` (s)) y DEBE (MUST) estar limitado en tasa a lo sumo a un
  sondeo en vuelo por relé objetivo y a lo sumo `Q` sondeos concurrentes en total por
  cliente (hombre de paja `Q = 8` (s)). El sondeador gasta bytes reales que no recupera
  como trabajo útil; este es el coste que hace al sondeo autolimitante. Un cliente NO DEBE (MUST
  NOT) sondear un relé más a menudo que una vez por `T_probe` (hombre de paja: horas, no
  minutos (s)) — el ancho de banda cambia lentamente en relación con lo rápido que envejece una medición,
  así que re-sondear con frecuencia compra poco y cuesta linealmente (GR-16).

- **GR-15 (el sondeo no puede convertirse en un amplificador de DoS).** `[claim-critical]` El
  relé medido DEBE (MUST) devolver tráfico de sondeo únicamente **al sondeador, por el mismo
  circuito por el que llegó** — nunca a ninguna dirección que las celdas del sondeador pudieran nombrar.
  Como el salto de cola `T` devuelve el tren por `C` al cliente que construyó
  `C`, un sondeo es un **bucle cerrado**: el trabajo que un sondeo induce está acotado por lo que el
  sondeador mismo envió (factor de amplificación ≤ 1 por construcción, no por política), y
  no hay ningún campo en el que un atacante pudiera escribir la dirección de una víctima para que `R`
  la inunde. Esta es la diferencia estructural respecto a cualquier diseño de «pídele al relé que envíe un
  flujo de prueba a la dirección X», que sería un reflector y está **prohibido**:
  un sondeo NO DEBE (MUST NOT) aceptar un destino que no termine él mismo. Una
  implementación que permita al sondeo apuntar a un tercero no es conforme.

- **GR-16 (un sondeo mide un instante-de-ruta; `vbw` es un agregado robusto de muchos).**
  Un solo sondeo es una muestra de *una ruta en un instante*, contaminada por la
  capacidad propia de la guardia y de la cola, por el tráfico cruzado y por la congestión en cualquier punto de
  `C`. Por tanto, un cliente DEBE (MUST) (a) sondear `R` a través de **varios circuitos independientes**
  (guardias y colas distintas, con fuentes mezcladas según GR-8 donde sea posible), (b) atribuir a
  `R` el **máximo throughput sostenido observado** a lo largo de esos circuitos en una
  ventana (el máximo, porque el cuello de botella de cualquier circuito individual es una cota *inferior* de
  `R` — la ruta más rápida aísla mejor la capacidad propia de `R`), y (c) tratar el
  resultado como una **estimación con una confianza que decae con la edad** (hombre de paja:
  semivida de unas pocas épocas (s)). `vbw(R)` DEBE (MUST) tener un umbral conservador: un
  único sondeo no corroborado cuenta como bajo, no como alto (disciplina PS-7).

- **GR-17 (los resultados de sondeo no se difunden por gossip como ancho de banda; solo se comparte la
  disciplina).** Un cliente NO DEBE (MUST NOT) publicar, difundir por gossip ni aceptar de un par un escalar
  «ancho de banda verificado de `R`» — eso reconstruiría la autoridad de ancho de banda que I-3
  prohíbe (una cifra reportada por un par es una afirmación no mejor que `bw` misma, GR-9). Lo que
  PUEDE (MAY) difundirse por gossip es la **alcanzabilidad/vitalidad** de un relé como una clase de fuente entre
  las clases de GR-8, y un cliente PUEDE (MAY) usar el acuerdo de un par de que un relé *existe y
  responde* como una posición corroborante (al estilo de PS-15), pero el **número de throughput
  que cada cliente usa para ponderar DEBE (MUST) ser el suyo propio** (GR-11). Los pares sybil pueden inflar
  *cuántos* reportes dicen «`R` es rápido», pero no pueden inflar lo que midió el propio
  sondeo del cliente — esta es la regla GR-9/PS-10 de «contar solo lo verificado» aplicada al
  ancho de banda.

### 5.3 Lo que un sondeo puede y no puede decirte (degradar honestamente)

- **GR-18 (un sondeo mide throughput, no honestidad, no ubicación, no identidad).**
  Un sondeo responde a *«¿puede esta ruta mover bytes?»* y nada más. NO DEBE (MUST NOT)
  leerse como evidencia de que:
  - **el relé es honesto** — un relé puede reenviar el tráfico de sondeo perfectamente y aun así
    registrar, retrasar o correlacionar el tráfico real; el throughput es ortogonal a la
    amenaza de correlación guardia+salida (modelo de amenaza), que la *disyunción* de rutas (Parte 3)
    aborda, no el ancho de banda;
  - **el relé está donde dice el mapa** — un sondeo cronometra un ida y vuelta; no
    localiza a `R` en un AS o jurisdicción (eso es el mapa de la Parte 8, PS-4, con su propio
    error declarado), y un sondeo rápido no dice nada sobre la coubicación (Parte 8 §10);
  - **el relé es una única parte distinta** — un operador sybil con capacidad real
    sondea *tan* rápido como lo es, porque realmente tiene el ancho de banda (ver §6: un
    adversario con recursos no es un sybil, es un adversario real caro).
  Un cliente conforme DEBE (MUST) presentar el ancho de banda verificado solo como lo que es — una
  estimación de throughput que decae en frescura, contaminada por la ruta, que el cliente midió
  él mismo — y NO DEBE (MUST NOT) dejar que un `vbw` alto sustituya a la disyunción (Parte 3) o
  a la diversidad (GR-8) en ninguna decisión de selección.

---

## 6. Sybil y eclipse, acotados (ajustando GR-8/GR-9)

Las identidades son gratis (GR-9), así que un adversario infla el conteo **bruto** de registros a
voluntad. Las defensas de abajo no detienen eso; acotan lo que la inflación *compra*,
y la cota es la curva que el simulador mide (§7.1).

### 6.1 La cota de eclipse de la mezcla de fuentes

- **GR-19 (el tope de GR-8 da una cota de eclipse declarada; el supuesto es la independencia de
  clases).** `[claim-critical]` Sea que el cliente mezcla su muestra a lo largo de `m`
  clases de fuente independientes (GR-8: como mínimo puente del grafo social, intercambio de
  gossip, sondeo directo — así que `m ≥ 3`), con el tope por clase de que **ninguna
  clase contribuye más de la fracción `f`** de la muestra almacenada (hombre de paja
  `f = 1/2` (s)). Sea que un adversario controla por completo `a` de esas `m` clases (cada
  registro entregado a través de una clase controlada es adversarial) y nada en
  las otras. Entonces la cuota del adversario en la muestra del cliente está acotada por
  ```
        A(a, f)  ≤  min( 1 ,  a · f ).
  ```
  Un **eclipse completo** — el adversario suministrando toda la vista del cliente, de modo que
  todo relé honesto sea invisible y la selección de rutas extraiga solo circuitos del adversario
  — requiere `A = 1`, de ahí que
  ```
        a  ≥  ⌈ 1 / f ⌉       clases bajo control total del adversario.
  ```
  Con el hombre de paja `f = 1/2`, **un eclipse completo requiere que el adversario posea al menos
  2 de las ≥3 clases**; poseer **una** clase cualquiera limita al adversario a `f = 1/2` de
  la muestra y un eclipse completo es **estructuralmente imposible** (las clases honestas
  siguen entregando ≥ `1 − f` de la vista). Esta es la cantidad exacta que GR-8 afirmó
  sin enunciar: el tope convierte «eclipse» de «poseer suficientes relés» en «poseer
  suficientes *clases independientes*», que es un problema estrictamente más difícil, y con
  recursos distintos.

- **GR-19a (nombra el supuesto, y dónde falla).** La cota de GR-19 se sostiene
  **solo si las clases son genuinamente independientes** — si comprometer la
  distribución de puentes del grafo social no le dice al adversario nada sobre, ni le da
  ningún control sobre, los pares de gossip o los objetivos de sondeo. **Falla** precisamente
  cuando una parte controla más de una clase a la vez:
  - un adversario que posee **tanto** el puente del grafo social **como** los pares de gossip
    controla `a = 2` clases y, con `f = 1/2`, alcanza `A = 1` — un eclipse completo que el
    tope no previene, porque el tope acota *por clase*, y dos clases que
    en secreto son una parte no son dos clases;
  - el fallo correlacionado (un proveedor de hosting, una jurisdicción, un monocultivo de
    software detrás de dos clases nominales) colapsa `m` hacia 1 en silencio.
  Por tanto, la protección del tope es **exactamente tan fuerte como la independencia de las
  clases**, y un cliente conforme DEBE (MUST) (a) obtener sus clases de
  orígenes de confianza demostrablemente distintos (un puente presentado por un amigo no es
  independiente del gossip si el amigo es el par de gossip), y (b) tratar una muestra
  en la que las clases *coinciden con demasiada perfección* en una vista inusual como la misma señal de
  anomalía que la Parte 8 usa para la divergencia de mapa (ID-10) y la Parte 3 usa para el steering
  (PS-17) — difúndela por gossip, no confíes en ella. La independencia es un **supuesto que el cliente
  debe mantener activamente**, no una propiedad que obtenga gratis por contar clases.

### 6.2 La cota de sybil

- **GR-20 (los sybils inflan el conteo bruto, nunca los recursos verificados ni las aristas reales).**
  `[claim-critical]` Como las identidades son gratis (GR-9), un adversario sybil fija el
  **conteo bruto de registros** en cualquier valor que le guste. Dos cantidades del lado del cliente que
  **no** puede inflar acotan el daño:
  1. **Ancho de banda verificado que no tiene.** `vbw` (GR-11) es la propia
     medición del cliente; un sybil de 10 000 identidades de ancho de banda cero mide como 10 000
     relés de ~0 de ancho de banda verificado y lleva ~0 peso de selección (PS-7). Para ganar
     *peso* el adversario debe realmente mover los bytes — ver GR-20a.
  2. **Aristas genuinas del grafo social.** Una clase de puente estilo Lox (GR-8) entrega confianza
     a lo largo de aristas *humanas*; un sybil puede acuñar identidades pero no las aristas que
     las presentan, así que la clase del grafo social admite sybils solo a la tasa a la que personas reales
     responden por ellos (que es la razón entera por la que esa clase existe).
  La consecuencia operativa es **PS-10, ahora cuantificada**: la estimación de tamaño viable
  DEBE (MUST) contar **solo relés verificados independientemente y diversidad de AS
  observada**, de modo que inflar el conteo bruto de `N` a `10N` sybils mueve la
  estimación de tamaño verificado en **0** (ninguno de los sybils pasa la verificación), y un
  cliente no puede ser engañado para tomar parámetros `n, k` completos cuya diversidad sea falsa. Lo que
  compra «contar solo lo verificado», en una línea: **el tamaño que impulsa la elección de parámetros
  es invariante bajo la inflación por sybil** — el adversario puede hacer que la red *parezca*
  arbitrariamente grande y no cambiar nada sobre lo que un cliente actúe.

- **GR-20a (un adversario con recursos no es un sybil — es un adversario real, caro y
  aceptado).** `[claim-critical]` La otra cara de GR-20 se enuncia
  honestamente: un adversario que **realmente tiene** el ancho de banda, el aval social
  y la diversidad de AS/jurisdicción **no** es derrotado por ninguna defensa de sybil,
  porque **no es un sybil** — es un adversario `k`-ruta genuino que pagó por
  sus posiciones. Este es el riesgo residual diseñado que el modelo de amenaza ya
  acepta (la fila `k`-ruta: «sube `n`, `k` a gusto»), no una brecha en esta parte.
  Las defensas de sybil elevan el coste del adversario de *gratis* (acuñar identidades) a
  *recursos reales proporcionales a la influencia buscada*; no hacen ni pueden hacer la
  influencia incompensable. Un cliente NO DEBE (MUST NOT) presentar «resistente a sybil» como «un adversario
  con recursos reales no puede ganar posición» — lo primero es cierto, lo segundo es falso
  y es una amenaza diferente, nombrada y aceptada.

---

## 7. Lo que esto no resuelve (OP-2 sigue abierto)

**OP-2 no se resuelve aquí, y ningún requisito de arriba afirma que sí.** Un asignador
central — la autoridad de ancho de banda de Tor, el snapshot firmado de Walking Onions — *sí*
resolvería tanto sybil como eclipse por decreto: publicaría una vista de confianza, y
los sybils no podrían inyectarse en ella ni podría un adversario alimentar a una víctima con una vista
privada de ella. I-3 prohíbe ese asignador, porque la parte que puede publicar la única
vista de confianza es también la parte que puede ser coaccionada, citada judicialmente o incautada para
publicar una *envenenada*, y un mecanismo de descubrimiento con ese único punto es el
interruptor de apagado que todo el proyecto rechaza. Habiéndolo rechazado, nos queda una
**cota, no una cura**:

- **No hay ningún mecanismo solo-de-overlay que haga el muestreo por gossip plenamente
  a prueba de sybil/eclipse.** Cada defensa de arriba es una *disciplina de verificación de recursos
  o de mezcla de fuentes del lado del cliente*, y cada una tiene una costura declarada:
  - la cota de eclipse (GR-19) se sostiene solo bajo la independencia de clases, y **colapsa
    cuando una parte posee ≥ `⌈1/f⌉` clases** (GR-19a) — un adversario lo bastante rico para
    ser el amigo que te entrega el puente **y** los pares con los que haces gossip te
    eclipsa, y el overlay no puede distinguir «dos clases» de «una parte llevando
    dos sombreros»;
  - la cota de sybil (GR-20) detiene la inflación *gratuita* pero no la posición *pagada*
    (GR-20a) — la verificación eleva el coste, no lo limita;
  - el sondeo de ancho de banda (§6) mide throughput, no honestidad ni ubicación (GR-18) —
    un relé puede sacar matrícula en cada sondeo y seguir siendo del adversario, y un sybil rápido con
    capacidad real es un adversario real (GR-20a). Un sondeo cierra la pregunta de *diseño* de
    GR-7; no cierra OP-2.
- **El arranque bajo eclipse es el residual duro.** Un cliente eclipsado desde su primer
  contacto (GR-10) ve solo clases del adversario, mide solo relés del adversario como
  «rápidos» y oye solo el acuerdo del adversario — todo mecanismo de corroboración de
  esta parte necesita *una posición honesta* para funcionar, y un adversario que suministra
  el mundo entero del cliente desde el primer paquete le niega esa posición. Esta es la
  misma forma que el arranque TOFU de la Parte 8 (ID-8): las defensas **detectan** una mala
  vista una vez que se alcanza una fuente honesta y hacen que mantener a un cliente eclipsado
  *para siempre* sea caro — no **previenen** el eclipse inicial. «Detectar y
  hacer caro el eclipse permanente», no «prevenir el eclipse», es la afirmación honesta, y es
  la afirmación que enuncia la interfaz.

**Lo que el diseño hace, precisamente, es acotar el ataque a lo largo de tres ejes:**
verificación de recursos (GR-11/GR-20: los sybils gratis no compran nada), mezcla de fuentes
(GR-19: el eclipse necesita ≥ `⌈1/f⌉` clases independientes, no solo muchos relés), y el
grafo social (GR-20: las aristas no se pueden acuñar). El residual que queda tras los
tres es: **un adversario con recursos reales, aval social real a lo largo de múltiples
clases genuinamente-independientes-en-apariencia, y la capacidad de suministrar la vista inicial entera
de un cliente nuevo puede inflar por sybil influencia que pagó y eclipsar a un cliente al que
rodea — y el overlay no puede, desde dentro, probar que está siendo rodeado.**
Ese residual es OP-2, y está abierto.

### 7.1 Las cotas son las curvas del simulador

Estos requisitos son falsables, no retóricos: un modelo de sybil/eclipse está siendo
medido por `poc/sybil_sim.py` junto al barrido existente de `infer_error` de `network_sim.py` (el
simulador ya modela un `gossip_sample` parcial por cliente — la vista exacta que un
adversario de eclipse moldea — y ya separa la verdad de base de la creencia del cliente). Las cotas
del diseño son las curvas que DEBE (MUST) medir:

- **la curva de eclipse:** fracción de muestra del adversario `A` frente al número de clases controladas
  `a`, que DEBE (MUST) seguir `min(1, a·f)` de GR-19 y DEBE (MUST) mostrar el codo en
  `a = ⌈1/f⌉` (eclipse completo) — y DEBE (MUST) mostrar que en `a = 1` la vista honesta nunca
  cae por debajo de `1 − f`;
- **la curva de inflación por sybil:** estimación de tamaño verificado (PS-10) frente al conteo bruto de sybils,
  que DEBE (MUST) ser **plana** — la afirmación de GR-20 de que inflar el conteo bruto mueve la
  estimación verificada en cero es exactamente esta planitud, y una curva no plana falsea
  GR-20;
- **la interacción con la rotación:** probabilidad de eclipse frente a la tasa de rotación de la muestra, ya que un
  cliente que re-muestrea más rápido encuentra antes una posición honesta (la afirmación «detectar, hacer
  caro el eclipse permanente» es una tasa, y el simulador debe ponerle un número).

Si el simulador muestra la curva de eclipse batiendo `min(1, a·f)`, o la
curva de inflación por sybil subiendo, la cota es errónea y esta extensión está rota —
ataca el modelo, luego este texto. La única cosa que no puede convertirse en curva es el
eclipse en el primer contacto de un cliente sin ninguna posición honesta en absoluto: eso no tiene
medición interna al overlay, porque la víctima, por definición, no puede ver fuera
del mundo del adversario. Es el residual de OP-2, declarado, y es por lo que esta parte
dice *acotar*, no *resolver*.

---

## Requisitos introducidos aquí

- **GR-11** — el ancho de banda verificado es una automedición por cliente (`vbw`), nunca una
  cifra publicada o compartida; las afirmaciones no sondeadas cuentan como bajas.
- **GR-12** — el sondeo es un ida y vuelta sellado con el relé medido como el
  salto intermedio; el sondeador nunca está en la vista del relé.
- **GR-13** — indistinguibilidad: el tráfico de sondeo DEBE (MUST) ser idéntico en bytes y en tiempos
  al tráfico realmente retransmitido (I-4), de modo que un relé no pueda servir sondeos y matar de hambre las cargas útiles.
- **GR-14** — un sondeo le cuesta al sondeador un presupuesto de bytes acotado y prepagado, limitado en tasa
  por objetivo y en agregado.
- **GR-15** — el sondeo es un bucle cerrado (regresa solo al sondeador); no puede nombrar ningún
  destino de terceros, así que no puede amplificarse en un reflector de DoS.
- **GR-16** — `vbw` es un agregado robusto a lo largo de varios circuitos independientes, tomando
  el máximo throughput sostenido, con confianza que decae con la edad y un umbral conservador.
- **GR-17** — los números de throughput nunca se difunden por gossip como ancho de banda; solo la vitalidad/
  alcanzabilidad es una clase de fuente compartible — cada cliente pondera por su propia medición.
- **GR-18** — degradación honesta: un sondeo mide throughput, no honestidad, no
  ubicación, no identidad distinta.
- **GR-19** — el tope de GR-8 produce la cota de eclipse `A ≤ min(1, a·f)`; el eclipse completo
  necesita `a ≥ ⌈1/f⌉` clases controladas (≥2 con `f = 1/2`).
- **GR-19a** — la cota supone la independencia de clases y falla cuando una parte posee
  ≥ `⌈1/f⌉` clases; la independencia se mantiene, no es gratis.
- **GR-20** — los sybils inflan el conteo bruto de registros pero nunca el ancho de banda verificado ni las aristas
  sociales reales; la estimación de tamaño verificado (PS-10) es invariante bajo la inflación por sybil.
- **GR-20a** — un adversario con recursos no es un sybil sino un adversario `k`-ruta real, caro y
  aceptado; la verificación eleva el coste, no hace la posición incompensable.

GR-11 y GR-19 son los dos que cargan el peso: cada cliente mide su propio ancho de banda
(sin autoridad), y el tope de mezcla de fuentes convierte el eclipse de «poseer suficientes relés»
en «poseer suficientes clases independientes». Ambos son **acotados, no absolutos** — el
sondeo de GR-11 no puede leer la honestidad ni la ubicación (GR-18), y GR-19 colapsa cuando las clases
son en secreto una sola parte (GR-19a). OP-2 no se resuelve: no hay ningún mecanismo solo-de-overlay
que haga el muestreo por gossip plenamente a prueba de sybil/eclipse, y un cliente
eclipsado desde su primer contacto no tiene ninguna posición honesta para detectarlo. El diseño
acota el ataque desde la verificación de recursos, la mezcla de fuentes y el grafo social;
no lo elimina. Ese es el residual honesto, y las curvas del simulador
son donde se le obliga a cumplir sus propios números. Rómpelo del mismo modo que el resto de la especificación
se rompe: encuentra un bit de sondeo sobre el que un relé pueda condicionarse (derrotando GR-13), una forma en que el sondeo
nombre a una víctima (derrotando GR-15), un sybil que mueva la estimación de tamaño verificado
(derrotando GR-20), o un eclipse que bata `min(1, a·f)` bajo clases genuinamente
independientes (derrotando GR-19) — y habrás roto esta extensión.


## 8. Lo que esta parte no decide

La resistencia a sybil/eclipse más allá de GR-8/GR-9 (OP-2), el protocolo de sondeo (GR-7),
el arranque sin contactos (OP-7). Existen issues numeradas para cada uno.
