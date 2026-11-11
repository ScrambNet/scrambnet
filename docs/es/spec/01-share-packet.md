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
  └─ AEAD extremo a extremo (claves del destinatario)      [computacional]
       └─ división de Shamir: n partes, umbral k           [umbral incondicional]
            └─ cifrado de cebolla por parte, circuito propio, formato Sphinx
                 └─ transporte camaleón (Parte 4)
```

- **SP-1.** El remitente DEBE (MUST) aplicar el cifrado extremo a extremo *antes* de la dispersión, y
  la dispersión DEBE (MUST) aplicarse al texto cifrado extremo a extremo. Con menos de `k`
  partes el adversario no aprende nada sobre el texto cifrado de forma incondicional
  (Shamir); con `k` partes o más aún se enfrenta al AEAD extremo a extremo. El
  umbral incondicional y el cinturón computacional se componen; ninguno reemplaza al
  otro.
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
