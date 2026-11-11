# Especificación de ScrambNet — Parte 0: Convenciones y estructura
> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../../en/spec/00-overview.md)).

**Estado: BORRADOR (DRAFT).** Todo número de esta especificación es un hombre de paja que atacar,
no una decisión. Atácalo a través de las issues; cámbialo a través de PRs.

## Cómo leer esta especificación

- Las palabras clave **MUST** (DEBE), **MUST NOT** (NO DEBE), **SHOULD** (DEBERÍA),
  **SHOULD NOT** (NO DEBERÍA), **MAY** (PUEDE) se interpretan como se describe en el RFC 2119.
- Los requisitos están numerados y son estables: `SP-n` (paquete de parte, Parte 1), `GR-n`
  (registro de gossip, Parte 2), `PS-n` (selección de rutas, Parte 3), `RZ-n` (rendezvous, Parte 6),
  `SA-n` (argumento de seguridad, Parte 7), `ID-n` (conjunto de datos de inferencia, Parte 8). Las issues y PRs hacen referencia a los requisitos por número.
- Las referencias `OP-n` apuntan a la lista de problemas abiertos en
  [threat-model.md](../threat-model.md#problemas-abiertos).
- Una implementación conforme implementa todo MUST de toda parte que declara.

## Invariantes de diseño

Estos cuatro invariantes mandan sobre todo lo demás en la especificación. Una propuesta que viole
uno de ellos se rechaza sin importar lo que compre.

- **I-1 (Kerckhoffs).** La especificación es completa: un implementador hostil con
  este documento y ningún otro conocimiento DEBE (MUST) poder construir un nodo interoperable,
  igualmente seguro. Si un detalle debe permanecer secreto para que el sistema funcione, el
  detalle es un defecto.
- **I-2 (Umbral incondicional).** La confidencialidad del contenido del mensaje frente a un
  adversario que posee menos de `k` partes NO DEBE (MUST NOT) depender de ninguna hipótesis
  computacional. Las capas por encima de la dispersión PUEDEN (MAY) ser computacionales; el umbral no.
- **I-3 (Ningún punto único).** Ningún paso del protocolo puede requerir una parte, clave o dirección
  que no pueda ser reemplazada por un sustituto no confiable. Esto incluye el descubrimiento,
  las actualizaciones y el arranque.
- **I-4 (Uniformidad).** Todo lo observable en el cable por una parte sin las
  claves pertinentes DEBE (MUST) ser indistinguible de bytes aleatorios uniformes de longitud
  fija. Sin versiones en claro, ni banderas, ni longitudes.

## Suite criptográfica

Los identificadores de suite son de un byte, negociados en ninguna parte: la suite es fija por época
de red y se transporta implícitamente por la versión del paquete (I-4 prohíbe la negociación en
claro). Suite `0x01` (hombre de paja):

| Papel | Primitiva |
|---|---|
| Handshake de circuito | Patrón Noise `XK`, `Noise_XK_25519_ChaChaPoly_BLAKE2s` |
| Intercambio de claves | X25519 |
| AEAD | ChaCha20-Poly1305 |
| Hash / KDF / PRF | BLAKE2s / HKDF-BLAKE2s |
| Firmas (registros de gossip) | Ed25519 |
| Formato de paquete | Parámetros Sphinx (Danezis–Goldberg 2009), Parte 1 |
| Dispersión | Esquema de Shamir sobre GF(2^8), por byte |

Justificación: rápido sin aceleración por hardware (un anonimato que solo corre en un portátil
nuevo no es para quienes más lo necesitan), nada exótico, toda primitiva tiene
una década de ataques públicos a sus espaldas. Nota poscuántica: por I-2 el umbral de
confidencialidad ya sobrevive a un adversario cuántico; un handshake PQ (suite `0x02`) es una
actualización planificada, no una emergencia.

## Convenciones de codificación

- Todos los enteros son sin signo, en orden de red (big-endian).
- Tamaños fijos en todas partes donde un campo cruza el cable (I-4). Los datos de longitud variable
  existen solo dentro de cargas útiles protegidas por AEAD, prefijadas en longitud con 2 bytes.
- Los registros de gossip usan CBOR canónico (RFC 8949 §4.2.1) — Parte 2.

## Partes

1. [Parte 1 — Paquete de parte](01-share-packet.md): la unidad de tamaño fijo que lleva
   una parte de un mensaje a través de un circuito.
2. [Parte 2 — Registro de gossip](02-gossip-record.md): el descriptor de relé autofirmado
   y las reglas para intercambiarlos y muestrearlos.
3. [Parte 3 — Construcción de circuitos y selección de rutas](03-path-selection.md):
   objetivos de disjunción, inferencia sin autodeclaración, guardias y el
   repliegue para redes pequeñas (OP-1).
4. [Parte 6 — Rendezvous y entrega](06-rendezvous.md): tarjetas de contacto,
   dead-drops dispersos y recuperación por sondeo.
5. [Parte 7 — El argumento de seguridad para I-2](07-security-argument.md): la demostración de que
   cualesquiera `k−1` partes son independientes del secreto, las dos condiciones sobre las que
   descansa (aleatoriedad de los coeficientes, separación de claves), y un enunciado honesto de
   lo que no se demuestra.
6. [Parte 8 — El conjunto de datos de inferencia](08-inference-dataset.md): cómo un
   cliente obtiene el mapa de IP-a-AS y jurisdicción gruesa del que la Parte 3
   infiere, sin autoridad — un artefacto reproducible y direccionado por contenido,
   un registro de transparencia sin permisos, confianza-en-el-primer-uso declarada,
   y la tasa de error que el mapa admite y alimenta al simulador (distribución de
   OP-1, planificación 2.3).

Planificadas, aún no redactadas: Parte 4 — transportes camaleón; Parte 5 — encuadre
del modo apagón.
