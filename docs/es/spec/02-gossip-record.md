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
| 7 | `sig` | bytes(64) | Ed25519 sobre la codificación canónica con la clave 7 ausente |

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

## 5. Lo que esta parte no decide

La resistencia a sybil/eclipse más allá de GR-8/GR-9 (OP-2), el protocolo de sondeo (GR-7),
el arranque sin contactos (OP-7). Existen issues numeradas para cada uno.
