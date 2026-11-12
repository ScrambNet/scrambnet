# Especificación de ScrambNet — Parte 10: Compilación reproducible y cadena de suministro
> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../../en/spec/10-reproducible-build.md)).

**Estado: BORRADOR (DRAFT).** Esta parte decide cómo una parte obtiene un **binario**
de ScrambNet en el que puede confiar *sin confiar en quien lo compiló*, bajo I-3 —ninguna
autoridad— frente a un proyecto cuyos contribuyentes son **seudónimos** y por tanto no
portan ninguna identidad que un usuario pudiera verificar. Es el análogo en software de la
Parte 8: allí, un *mapa* se confía porque se reconstruye a partir de entradas públicas;
aquí, un *binario* se confía porque se reconstruye a partir de código fuente público. Los
valores de hombre de paja se marcan con `(s)`.

La Parte 9 dice *qué debe hacer el código del nodo*; esta parte dice *cómo ese código se
convierte en un binario que puedes verificar que estás ejecutando*. Lee primero el §1 y el
§10: entre ambos dicen qué compra esta parte (reproducción, no firma, como árbitro) y qué
admite que no puede comprar (una puerta trasera en código fuente fielmente reproducido; un
compilador que miscompila de forma reproducible; y, para el usuario que no puede
reconstruir, una reducción a OP-2 —la misma reducción con la que termina la Parte 8).

Esta parte decide la reproducibilidad como el **ancla** de confianza. **No** decide *quién
firma una versión ni cómo se eligen y reemplazan los firmantes* —eso es el ítem 4.1 (OP-8),
una parte aparte. La costura entre ambos es el §9, y refleja los ID-11/ID-11a de la Parte 8
por citación.

## 1. La decisión, en dos frases

- **No hay autoridad de versión.** Un binario de ScrambNet es un **artefacto
  reproducible, direccionado por contenido** que cualquier parte reconstruye byte a byte a
  partir de código fuente público etiquetado y entradas públicas fijadas; dos partes
  concuerdan en que un binario es honesto no porque una parte confiable lo firmara, sino
  porque computaron el **mismo `BLAKE2s`** (RB-1, RB-9). Un binario bendecido por un
  conjunto fijo de firmantes sería una autoridad de versión con otro nombre, e I-3 lo
  prohíbe.
- **La concordancia es por reproducción; las firmas solo *localizan* una compilación, nunca
  la *autorizan*; la confianza en una compilación que el usuario no puede reproducir por sí
  mismo se reduce a corroboración-por-cuenta, que es OP-2.** Esta es la forma honesta y se
  enuncia por delante, no se entierra: para la parte con una máquina de compilación, la
  reproducción carga toda la confianza; para el teléfono que no puede reconstruir —el
  usuario modal— la confianza descansa en una cuenta de reproductores independientes,
  exactamente como el cliente no reconstructor de la Parte 8 descansa en un quórum difundido
  por gossip (RB-7b, §10).

Así que el resultado honesto es el mismo que la Parte 8 alcanzó para el mapa: **reprodúcelo
tú mismo y la confianza es libre de autoridad; no puedes reproducirlo, y vuelves a un quórum
de corroboración sujeto a OP-2.** Todo lo que sigue hace concreto "reprodúcelo tú mismo, y
detecta a cualquiera que mintió", y el §10 es el residual que ninguna cantidad de
construcción elimina.

## 2. Alcance y la trampa que esta parte evita

Un proyecto seudónimo no puede pedir al usuario que confíe en sus autores —no hay autor en
quien confiar. El diseño "sin confianza" ingenuo es un binario firmado por los mantenedores
del proyecto; eso reimporta precisamente la autoridad que I-3 niega. La trampa: un firmante
que puede distribuir sigilosamente un binario malicioso bajo una clave confiable es el
interruptor de apagado que el ítem 4.1 existe para evitar. Así que la confianza no debe
fluir a través de *quién firmó*; fluye a través de *¿se reconstruye?*.

- **RB-1 (ninguna autoridad de versión; la reproducción es el árbitro). [normativo]** Ningún
  paso de obtención o validación de una compilación DEBE (MUST) requerir confiar en que una
  parte concreta la compiló, firmó o bendijo. Las únicas operaciones confiables son (a)
  recomputar `BLAKE2s`, y (b) reconstruir el artefacto a partir de código fuente etiquetado y
  entradas fijadas y comparar. Todo elemento de diseño que no pueda ser reemplazado por un
  sustituto no confiable que realice (a) o (b) es un defecto bajo I-3 y DEBE (MUST)
  eliminarse o declararse en el §10. (La operación (b), reconstruir-y-comparar, es confiable
  **módulo** el residual de la cadena de herramientas: ejecutar la compilación ejecuta el
  compilador fijado, al que RB-3b declara un residual de "trusting-trust" —reconstruir reduce
  la confianza al compilador, no la elimina. RB-1 es la afirmación de las dos operaciones,
  leída con esa referencia cruzada, no sin ella.)
- **RB-2 (la reproducibilidad autoriza; las firmas solo localizan). [normativo]** Esta parte
  no decide nada sobre *quién firma una versión ni cómo se eligen y reemplazan los
  firmantes* —eso es el ítem 4.1. Una firma sobre una compilación, si existe en absoluto,
  DEBE (MUST) tratarse como un **localizador** ("una compilación con este `H_build` fue
  anunciada aquí, entonces, por esta mano seudónima"), nunca como una **autorización** ("esta
  es la compilación a ejecutar"). Un cliente conforme NO DEBE (MUST NOT) adoptar una
  compilación *porque* fue firmada; *qué* compilación adoptar es asunto del ítem 4.1 y es
  local al cliente y opcional. Vincular la honestidad de la compilación a un conjunto de
  firmantes reimporta la autoridad que I-3 prohíbe (la regla ID-11a, para software).
- **RB-2a (herramientas compartidas, no autoridad compartida).** Esta parte PUEDE (MAY)
  reutilizar la construcción de registro de transparencia de la Parte 8 (ID-6) y el canal de
  gossip GR-6 para publicar y difundir hashes de compilación (RB-14) —compartir *mecanismo*
  no cuesta nada (ID-11a). NO DEBE (MUST NOT) compartir con el mapa un conjunto de partes
  —**lista de firmantes o de anexadores del registro**— cuyo rol sea portante tanto para el
  mapa como para el código, porque ese conjunto sería el interruptor de apagado que I-3
  prohíbe, ahora capaz de voltear tanto la inferencia de geografía como el software. El
  registro compartido no introduce autoridad **porque** ambas partes encaminan la confianza a
  través de la reproducción, no del registro, y el registro permanece sin permisos (ID-7).

## 3. La cadena de herramientas, fijada por contenido

- **RB-3 (la cadena de herramientas se fija por contenido, no por nombre de canal).
  [normativo]** La compilación DEBE (MUST) fijar una cadena de herramientas *exacta* —una
  versión estable concreta (hombre de paja: `rust 1.xx.y` en `rust-toolchain.toml` con
  `channel = "1.xx.y"`, nunca `stable`/`latest`/`beta`/`nightly`)— **y** fijar los artefactos
  binarios de esa cadena por `BLAKE2s` en el manifiesto de compilación (RB-8). "La cadena de
  herramientas" es un conjunto de bytes con hash, no un nombre que un espejo pueda resolver de
  forma distinta. Un reconstructor obtiene la cadena de herramientas desde **cualquier**
  espejo y verifica los hashes (I-3: el distribuidor es reemplazable; los bytes están fijados
  —el patrón ID-3 aplicado al compilador).
- **RB-3a (fija toda la superficie de compilación).** La fijación DEBE (MUST) cubrir toda
  herramienta cuya salida alcanza el artefacto: `rustc`, `cargo`, las bibliotecas
  precompiladas `std`/`core` realmente enlazadas, el enlazador (hombre de paja: un `lld`/`mold`
  fijado (s), no el `ld` ambiente del host), la libc/sysroot, y cualquier herramienta que un
  `build.rs` invoque. Una herramienta dejada al host es una entrada no fijada y un peligro de
  determinismo (RB-6, RB-18).
- **RB-3b (el compilador es un binario obtenido —"trusting-trust" es un residual declarado).
  [normativo]** El `rustc` fijado es un *binario obtenido*, no algo que esta tubería compile a
  partir de código fuente. Confiar en él es un **residual declarado** (§10,
  "trusting-trust"): RB-3 fija *qué* bytes de compilador usa todo el mundo, así que todos los
  reconstructores comparten el *mismo* residual y cualquier *sustitución* es detectable por
  divergencia; **no** hace honesto al compilador. Fijar demuestra **procedencia**, no
  **honestidad** (véase RB-18). Una ruta de arranque-desde-código-fuente o de
  doble-compilación-diversa, si alguna vez se adopta, se nombra como trabajo futuro, no se
  requiere aquí.

## 4. La compilación hermética

La compilación es una **función pura del manifiesto a un artefacto idéntico byte a byte**. El
determinismo es todo el juego: si dos compiladores honestos pueden divergir, la igualdad de
hash (RB-9) deja de significar "mismo binario" y los compiladores honestos quedan marcados
como un ataque (RB-7, RB-15) —la lección de la Parte 8 (preámbulo de ID-4), no aprendida
aquí sería fatal.

```
  LA COMPILACIÓN ES UNA FUNCIÓN PURA DEL MANIFIESTO (RB-8)

  ┌──────────────────────── manifiesto (RB-8) ─────────────────────┐
  │  commit/tag fuente · hashes de cadena (RB-3) · hash de conten. │
  │  de cada dependencia (RB-5) · entorno fijo (RB-4b) · triple de │
  │  destino · SOURCE_DATE_EPOCH (derivado, RB-4b) · H_build esper.│
  └───────────────────────────┬────────────────────────────────────┘
                               ▼
            ┌────────────────────────────────────────┐
            │  COMPILACIÓN HERMÉTICA (fn pura, RB-4) │
            │  sin red (RB-4a), sin estado ambiente  │
            │  del host, entorno fijo (RB-4b), no    │
            │  determinismo eliminado según conjunto │
            │  de peligros fijado (RB-6, versionado  │
            │  por la cadena de herramientas)        │
            └───────────────────┬────────────────────┘
                               ▼
                 artefacto (para UN triple de destino)
                               │
                               ▼
              H_build = BLAKE2s(artifact)   ← el ÚNICO nombre de la
                                              compilación (RB-6a), definido
                                              por (fuente, manifiesto, triple
                                              de destino) — RB-6b

  Alice ─ mismo manif., mismo triple ─▶ H_A   Dos compiladores honestos concuerdan
  Bob   ─ mismo manif., mismo triple ─▶ H_B   por H_build igual. La reproducción es
                                               el árbitro (RB-7), no un firmante.
```

- **RB-4 (compilación hermética, sin conexión y sin estado ambiente). [normativo]** La
  compilación DEBE (MUST) ejecutarse con **ningún acceso a la red** y **ningún estado
  ambiente del host**: sin lectura de `$HOME`, variables de entorno del host (más allá de una
  lista de permitidos explícita, RB-4b), el reloj del sistema para cualquier valor embebido,
  nombres de usuario/grupo, nombre de host, conteo de CPU donde afectaría la salida, ni
  ninguna ruta fuera del sandbox. Sustratos conformes: una derivación pura al estilo
  Nix/`crane`, **o** un sandbox de contenedor/`bwrap` con el espacio de nombres de red
  eliminado y un entorno mínimo fijo. Esta parte especifica las **propiedades** y no obliga a
  ninguno de los sustratos (I-1: un implementador hostil construye un compilador conforme a
  partir de las propiedades); Nix y un contenedor en sandbox se nombran como los dos sustratos
  de referencia conformes. Una parte que adopta un sustrato DEBE (MUST) fijar *ese* también
  (una cadena de herramientas Nix es ella misma una fijación RB-3).
- **RB-4a (sin obtención de red en tiempo de compilación, jamás). [normativo]** La
  compilación NO DEBE (MUST NOT) obtener nada —ningún acceso a registro, ninguna resolución de
  dependencias git, ninguna descarga de `build.rs`, ninguna extracción de cadena de
  herramientas. Toda obtención ocurre *antes* del paso hermético, fijada por hash, y se
  entrega a través del manifiesto. Una compilación que *puede* alcanzar la red es no conforme
  aunque resulte no usarla, porque su determinismo depende entonces de un servidor (la
  prohibición de entradas-flotantes ID-4c, para software).
- **RB-4b (entorno fijo, declarado y derivado). [normativo]** El entorno de compilación DEBE
  (MUST) fijarse en, y solo en, el manifiesto: locale `C`/`C.UTF-8`, `TZ=UTC`, umask, la lista
  de permitidos de entorno, y `SOURCE_DATE_EPOCH`. `SOURCE_DATE_EPOCH` DEBE (MUST) **derivarse
  de forma determinista del commit etiquetado** (la fecha de committer de la etiqueta fijada),
  de modo que sea una función de una entrada fijada, no una aserción de manifiesto flotante
  que un compilador pudiera fijar a voluntad. Una fecha de committer falsificada no es una
  victoria silenciosa: cambia `H_build` y por tanto queda atrapada por divergencia (RB-7),
  exactamente como lo está cualquier otro cambio de entrada.

## 5. El árbol de dependencias

- **RB-5 (árbol de dependencias mínimo, auditado, vendorizado y fijado por contenido).
  [normativo]** Las dependencias DEBEN (MUST) ser (a) *minimizadas* —cada una justificada
  frente a no tenerla, porque cada crate es un autor no confiable en la cadena de confianza
  (RB-16, OP-10); (b) *vendorizadas* —el código fuente exacto de cada dependencia transitiva
  fijado en las entradas de compilación, no resuelto en vivo (RB-4a); y (c) *fijadas por
  contenido* —`Cargo.lock` commiteado, **y** cada crate adicionalmente fijado por `BLAKE2s` de
  su código fuente en el manifiesto (RB-8), sin confiar solo en la propia suma de comprobación
  del registro. Un registro que puede cambiar bytes bajo un nombre es una autoridad; el hash
  de contenido lo elimina y convierte al registro en un CDN reemplazable.
- **RB-5a (el lockfile es necesario, no suficiente).** `Cargo.lock` fija versiones y sumas de
  comprobación del registro; no hace por sí mismo que la *compilación* sea reproducible (la
  unificación de features, `cfg`, las diferencias de host aún muerden —RB-6) ni elimina la
  confianza en el registro. La fijación por contenido de RB-5 y la hermeticidad de RB-4
  cierran esa brecha. Una compilación que fija solo el lockfile es no conforme.
- **RB-5b (los scripts de compilación y los proc-macros son cómputo confiable, no datos
  inertes). [normativo]** Los scripts `build.rs` y las macros procedurales ejecutan código
  arbitrario *en tiempo de compilación*; DEBEN (MUST) ejecutarse dentro del sandbox RB-4 bajo
  las mismas reglas de sin-red/sin-ambiente, y están en alcance para la auditoría RB-16
  exactamente como lo está el código de ejecución. Un proc-macro que lee el reloj o la red es
  un peligro de determinismo y una superficie de cadena de suministro en uno.

## 6. Peligros de determinismo y cómo la compilación los fija

Cada peligro de abajo es un lugar donde dos compiladores honestos podrían producir bytes
diferentes. La compilación DEBE (MUST) eliminar cada uno; una compilación que no lo hace es
no conforme porque no puede soportar a RB-9, y su divergencia es mal interpretada por RB-7
como un ataque.

- **RB-6 (el conjunto de peligros es normativo, versionado por la cadena de herramientas).
  [normativo]** La compilación DEBE (MUST) eliminar cada peligro del **conjunto de peligros
  fijado** para la versión de cadena de herramientas en uso. Este conjunto es
  normativo-a-fecha-de-una-cadena-fijada, no para siempre (residual §10.7: el determinismo es
  un blanco móvil frente a la rotación de la cadena de herramientas), y el manifiesto DEBE
  (MUST) referenciar la versión del conjunto de peligros contra la que se compiló. El conjunto
  como mínimo DEBE (MUST) fijar:
  - **marcas de tiempo** — `SOURCE_DATE_EPOCH` del commit etiquetado (RB-4b); sin mtimes en
    ningún archivo emitido;
  - **rutas de compilación** — `--remap-path-prefix` a una raíz `/build` fija, de modo que
    ninguna ruta absoluta, `$HOME`, ni nombre de usuario quede embebido en la información de
    depuración o en las cadenas de pánico;
  - **paralelismo y ordenación** — el orden de codegen-unit, el orden de enlace, el orden de
    la tabla de símbolos, el orden de miembros de archivo, y cualquier orden de iteración de
    hash-map que alcance la salida DEBEN (MUST) hacerse deterministas (fijados u ordenados);
  - **derivación de `-C metadata` / `-C extra-filename`** — derivada de forma determinista de
    entradas fijadas, nunca de un valor que varíe con el host;
  - **locale/codificación** — `LC_ALL=C`;
  - **información de depuración y símbolos** — deterministas, o eliminados (stripped); si se
    conservan, deterministas;
  - **disposición aleatorizada y semillas** — `-Z randomize-layout` desactivado; cualquier
    codegen sembrado con RNG fijado;
  - **el encuadre del archivo/paquete** — un códec fijo a un nivel fijo, sin nombres de
    fichero, marcas de tiempo, ni uid/gid en los metadatos del contenedor (la regla de
    contenedor-canónico ID-4d, para el empaquetado de software).

  El análogo del peligro de decodificación no fijado de la Parte 8 (nota ID-4d §10) aplica
  aquí y se nombra, no se oculta: **el codegen dependiente de la versión de LLVM y la
  unificación de `cfg`/features dependiente del host** (admitida en RB-5a) son reproducibles
  solo *a fecha de la cadena de herramientas fijada y de la resolución de features fijada*;
  cada salto de versión de la cadena de herramientas es una obligación fresca de
  auditoría-de-determinismo (§10.7), no un pase libre.
- **RB-6a (el artefacto es direccionado por contenido; `H_build` es su único nombre).
  [normativo]** El artefacto de versión se direcciona por `H_build = BLAKE2s(artifact)` (el
  hash de la suite, Parte 0). `H_build` es el único nombre autoritativo de la compilación; una
  cadena de versión legible por humanos (`v1.2.3`) es una etiqueta de conveniencia y NO DEBE
  (MUST NOT) confiarse en lugar de `H_build` (la regla ID-2 "el hash es el único nombre"). La
  frescura —*qué* versión debería ejecutar un cliente— es una propiedad separada, portada por
  RB-8a, no por la cadena de versión.
- **RB-6b (`H_build` es por destino; la concordancia se define dentro de un triple).
  [normativo]** Una versión reproduce a bytes *diferentes* por destino
  (`aarch64-linux-android`, `x86_64-unknown-linux-gnu`, `armv7-…`, …) a partir del *mismo*
  código fuente, así que `H_build` es una función de **(código fuente etiquetado, manifiesto,
  triple de destino)**. El manifiesto DEBE (MUST) fijar el triple de destino; la concordancia
  (RB-9) se define **solo dentro de un triple fijo**; y RB-7/RB-15 DEBEN (MUST) comparar solo
  `H_build` de triple igual. Un cliente que compara su propio hash-de-triple con un hash
  publicado de triple diferente NO DEBE (MUST NOT) levantar una anomalía de divergencia de
  compilación —eso es un error de categoría, no un ataque. La parte también fija exactamente
  qué bytes cubre `H_build` para cada artefacto enviado (el binario del nodo, y por separado
  cualquier instalador o biblioteca), de modo que dos reconstructores hagan hash del mismo
  objeto.

## 7. Cómo dos partes concuerdan en que tienen el mismo binario

- **RB-7 (el procedimiento de un extraño de reconstruir-y-comparar). [normativo]** El
  procedimiento que una parte *sin relación con ningún contribuyente* ejecuta para obtener un
  artefacto idéntico a nivel de bit y verificarlo:
  1. obtén el código fuente etiquetado y el manifiesto (RB-8) desde **cualquier** espejo;
  2. verifica cada entrada contra su `BLAKE2s` del manifiesto (RB-3, RB-5);
  3. ejecuta la compilación hermética (RB-4) para el triple de destino (RB-6b);
  4. computa `H_build`;
  5. compara por igualdad de `BLAKE2s` con el hash publicado (RB-14) y con el hash de
     triple-igual de cualquier par.

  Un `H_build` igual es prueba del mismo binario; uno desigual es prueba de que difieren y
  DEBE (MUST) exponerse como una **divergencia de compilación** (RB-15), nunca reconciliarse
  silenciosamente. La disputa es resoluble por cualquiera sin apelación a autoridad:
  reconstruye y ve qué produce el código fuente público (el árbitro ID-5a, para software).
  Este es el criterio de "hecho" de 4.2: dos partes en máquinas diferentes producen artefactos
  idénticos en hash a partir del código fuente etiquetado mediante un procedimiento que no
  nombra ningún singleton confiable.
- **RB-7a (una versión que no reproduce se rechaza, no se parchea por encima).
  [normativo]** Un artefacto publicado cuyo `H_build` no puede reproducirse a partir de su
  manifiesto declarado no es, por definición, la compilación de ese código fuente: un
  verificador conforme que *puede* reconstruir DEBE (MUST) rechazarlo y DEBERÍA (SHOULD)
  difundir por gossip la discrepancia como una anomalía de compilación (RB-15). "Compila en la
  máquina del mantenedor pero en ninguna otra parte" es un fallo de reproducibilidad —un
  defecto— no un estado aceptable (la regla ID-5b, para software).
- **RB-7b (el cliente que no puede reconstruir —el usuario modal). [normativo]** Casi todos
  los usuarios reales ejecutan el cliente en un teléfono sin cadena de herramientas, sin
  disco, y sin ancho de banda para compilar el árbol de dependencias; *no* puede realizar la
  operación (b) de RB-1. Tal cliente DEBE (MUST) rastrear cada binario que ejecuta como
  **`reproducido-por-otros-no-verificado`** hasta que él (o un par con cuyo `H_build` luego
  concuerde) reconstruya, DEBE (MUST) tratar la corroboración como una cuenta de reproductores
  **verificados independientemente** bajo la regla RB-10 (nunca un conteo crudo de
  atestaciones), y la parte lo enuncia con claridad: **para el cliente no reconstructor, la
  confianza en la compilación no fluye de la reproducción —se reduce a
  corroboración-por-cuenta, que es OP-2**, exactamente como la confianza en el mapa de la
  Parte 8 se reduce a OP-2 para el cliente de mapa no reconstructor (§10, ID-5b/§10). El
  cliente DEBE (MUST) exponer este estado; NO DEBE (MUST NOT) presentar un binario no
  reconstruido como si el usuario lo hubiera verificado.

## 8. El manifiesto, la concordancia y la frescura

- **RB-8 (el manifiesto es la receta de reproducción). [normativo]** Toda versión DEBE
  (MUST) distribuir un **manifiesto**: el commit/tag fuente, los hashes de cadena de
  herramientas fijados (RB-3), el hash de contenido de cada dependencia (RB-5), el entorno
  fijo (RB-4b), el triple de destino (RB-6b), `SOURCE_DATE_EPOCH` (derivado, RB-4b), la
  versión del conjunto de peligros (RB-6), y el `H_build` esperado. El manifiesto —no un
  servidor, no una persona— define la compilación (el manifiesto ID-3, para software).
- **RB-8a (el manifiesto es canónico y direccionado por contenido; la frescura es un campo
  verificable). [normativo]** El manifiesto DEBE (MUST) tener una **serialización canónica**
  (reutiliza el perfil CBOR canónico de la Parte 2, GR-21..GR-30) y está él mismo direccionado
  por contenido mediante `manifest-hash = BLAKE2s(manifiesto canónico)`; de lo contrario dos
  partes honestas producen manifest-hashes diferentes para la misma receta y la corroboración
  de registro (RB-14) se parte sobre una diferencia de formato —la lección GR-21 no aprendida.
  El manifiesto DEBE (MUST) llevar un **índice de versión monótono** vinculado junto con la
  fecha de committer derivada, y la hoja del registro de transparencia (RB-13) DEBE (MUST)
  preservar ese orden, de modo que la *recencia* sea una propiedad verificable del artefacto.
  Esto cierra la brecha de costura con 4.1 que 4.1 no puede cerrar después (el esquema del
  manifiesto es un artefacto de 4.2): véase RB-9a.
- **RB-9 (la concordancia es igualdad de hash, nada más). [normativo]** Dos partes tienen el
  mismo binario **si y solo si** sus `H_build` de triple-igual son iguales (RB-6b). La
  comparación es una verificación de 32 bytes; no necesita firmante, ni quórum, ni autoridad
  (la regla ID-5, para software).
- **RB-9a (la reproducibilidad demuestra que-el-binario-coincide-con-el-fuente, no que-el-
  fuente-es-actual —el residual de frescura). [normativo]** `H_build` autentica *que los
  bytes coinciden con el código fuente*; no dice nada sobre *cuál código fuente es el que hay
  que ejecutar*. Un **ataque de downgrade reproducible** —alimentar a un cliente con una
  etiqueta antigua con una vulnerabilidad conocida, que reproduce perfectamente y pasa cada
  verificación RB de arriba— se derrota **solo** por una regla de frescura. Esta parte provee
  la entrada verificable para esa regla (el índice de versión monótono + la fecha derivada de
  RB-8a, ordenados en el registro, RB-13); la *política de adopción* que lo usa (rechaza un
  índice menor que uno ya visto; advierte ante la obsolescencia) es el ítem 4.1 y es local al
  cliente. El residual: la reproducibilidad por sí sola no derrota el downgrade; el campo de
  manifiesto que esta parte obliga es lo que hace *posible* derrotarlo para 4.1 (la época
  ID-4, para las versiones).

## 9. La costura de fusión con la gobernanza de actualizaciones (OP-8 / ítem 4.1)

Los firmantes de versiones y los publicadores de raíces del mapa parecen un solo mecanismo.
**Posición, reflejando el §9 de la Parte 8: mantenlos separados en la confianza, aunque
compartan herramientas.**

- **RB-10 (una atestación es una afirmación de reproducción, ponderada por re-reproducción
  independiente, no por quién la emitió). [normativo]** Una **atestación** (attestation) de
  compilación es una declaración *"reconstruí el manifiesto M para el triple T y obtuve
  `H_build`"* —un **reporte de reproducción**, no una autorización. Su peso proviene de ser
  **verificable independientemente** (cualquiera re-ejecuta RB-7 y la confirma o la refuta),
  no de la identidad del atestador: una atestación firmada con seudónimo y una sin firmar
  portan el **mismo** peso una vez que un tercero ha reproducido la afirmación; la firma solo
  *localiza* la afirmación (RB-2). La corroboración DEBE (MUST) seguir la disciplina de la
  Parte 2 exactamente: **cuenta solo las reproducciones verificadas independientemente, nunca
  un conteo crudo de atestaciones** (la regla GR-20 / PS-10 "cuenta solo las verificadas,
  nunca las crudas"). Y la parte concede lo que GR-19a ya demuestra: **la independencia de los
  reproductores no es verificable solo a partir de atestaciones** —no puedes distinguir 10 000
  reproductores de una sola parte que lleva 10 000 máscaras— así que una cuenta de
  reproductores es una señal *débil* que se reduce a OP-2, y la señal *fuerte* es la propia
  reconstrucción del cliente (RB-7). Un diseño en el que la aceptación de una atestación
  depende de la identidad del atestador, o en el que un conteo crudo de atestaciones no
  verificadas corrobora una compilación, es no conforme (RB-1, y es la autoridad de mayoría
  votable por sybil que RB-10 existe para prohibir).
- **RB-10a (formato canónico de atestación, deduplicación por reproductor). [normativo]** Las
  atestaciones cruzan el cable (RB-14) y alimentan un conteo (RB-10), así que DEBEN (MUST)
  tener una codificación canónica (reutiliza CBOR canónico, GR-21..GR-30) o dos atestadores
  honestos producen bytes no coincidentes y el conteo se rompe. Las atestaciones DEBEN (MUST)
  deduplicarse por `(identidad de reproducción, M, triple, H_build)`, y el peso es
  **por-reproductor-independiente, nunca por-cadena-de-bytes-de-atestación**, de modo que un
  adversario no pueda inflar la corroboración acuñando variantes distintas en bytes de una
  sola afirmación (relleno de formato).
- **RB-11 (la cadena de herramientas debe compilar de forma determinísticamente-usable; existe
  un vector de prueba entre hosts). [normativo]** Porque la cadena de herramientas fijada
  puede ella misma embeber no determinismo (codegen paralelo, `OUT_DIR`, triple de host en los
  metadatos), la parte DEBE (MUST) fijar las banderas y modos que la hacen producir salida
  idéntica a través de hosts (RB-6), y DEBE (MUST) existir un **vector de prueba de compilación
  entre hosts** (manifiesto → `H_build` esperado para un triple fijo) de modo que una segunda
  máquina demuestre que reproduce el artefacto idéntico (la regla de vector-de-prueba-del-mapa
  ID-4d; se vincula con el arnés de conformidad de roadmap 3.2). Este es el análogo RB del
  RI-1b de la Parte 9: *una prueba funcional que pasa demuestra que el binario se ejecuta, no
  que es idéntico a nivel de bit* —la reproducibilidad se verifica reconstruyendo-y-comparando,
  nunca se asume de "compiló".
- **RB-12 (los contribuyentes son seudónimos; la confianza fluye solo a través de la
  reproducibilidad). [normativo]** ScrambNet **no tiene claves de firma vinculadas a
  identidad** ni identidad de autor confiable. La confianza en un binario DEBE (MUST) derivar
  **enteramente** de (a) que el código fuente sea público y revisable (I-1) y (b) que el
  binario reproduzca a partir de ese código fuente (RB-7) —**nunca** de *quién* lo escribió,
  commiteó, etiquetó o firmó. Un paso que requiera una identidad de autor, mantenedor o
  firmante confiable para aceptar una compilación es no conforme tanto bajo RB-1 como bajo la
  regla de seudonimia del proyecto. Esta es la resolución de la tensión central de esta parte:
  *el autor es no confiable por construcción; el binario es confiable por reproducción.*
- **RB-12a (para qué sirven las claves de seudónimo —y la precondición sobre la que
  descansan).** Una clave de contribuyente, si se usa en absoluto, autentica *la continuidad
  de un seudónimo* y *localiza* trabajo (este commit, esta atestación, vino de la misma mano
  seudónima) —una conveniencia para el gossip y para el rol de localizador de 4.1 (RB-2),
  nunca una raíz de confianza-en-la-compilación. Perder, rotar o reemplazar tal clave NO DEBE
  (MUST NOT) invalidar ningún binario que aún reproduzca. Un poseedor de una clave
  comprometida no puede distribuir un binario malicioso-pero-reproducible que **sobreviva a un
  revisor honesto más un reproductor honesto** —pero esa protección es *su existencia*, no la
  clave: en ausencia de un revisor honesto del código fuente (I-1) y de un reproductor honesto
  que el cliente pueda alcanzar (RB-7/RB-10), la clave comprometida *sí puede* distribuir un
  binario malicioso a un cliente que ni revisa ni reconstruye (RB-7b). Así que la protección
  se reduce a I-1 (revisión) y OP-2 (alcanzabilidad de reproductor honesto); no es una
  propiedad incondicional de la clave. (Esto enuncia la precondición explícitamente, de modo
  que la afirmación no sea circular.)
- **RB-12b (la reproducibilidad demuestra que-el-binario-coincide-con-el-fuente, no dice nada
  sobre la honestidad-del-fuente).** La reproducibilidad y la revisión son **ejes
  ortogonales**. La reproducibilidad demuestra que el binario coincide con el código fuente;
  no dice nada sobre si el código fuente es honesto. La seudonimia (RB-12) elimina "un autor
  confiable dio fe del código fuente", así que la honestidad-del-fuente descansa en la
  **revisión pública (I-1)** y nada más. La parte enuncia esto con claridad para que ningún
  lector confunda "reproducible" con "seguro" o "revisado": una compilación fielmente
  reproducida de código fuente con puerta trasera es una reproducción fiel de una puerta
  trasera (§10, OP-10).
- **RB-13 (los hashes y manifiestos se publican en un registro sin permisos, ordenados por
  índice de versión).** Las tuplas de versión `(triple, H_build, manifest-hash,
  release-index, committer-date)` DEBERÍAN (SHOULD) anunciarse al mismo registro (o registros)
  de transparencia de solo-anexado sin permisos usado para los mapas (ID-6/ID-7), preservando
  la ordenación de RB-8a, de modo que los anuncios de compilación tengan marca de tiempo y la
  equivocación sea detectable con **ningún anexador privilegiado** (ID-7). El registro no
  *bendice* una compilación —la reproducción lo hace (RB-7)— hace detectable "binario
  diferente mostrado a gente diferente" y da a la frescura (RB-9a) un orden atestiguado. Por
  RB-2a la *construcción* del registro se comparte con el mapa; las *instancias/conjuntos*
  DEBERÍAN (SHOULD) permanecer independientes (ID-7b "múltiples registros, ninguno canónico")
  de modo que los dos dominios de disponibilidad no colapsen en un solo operador portante.
- **RB-14 (difunde por gossip la tupla de compilación; detecta la vista partida).
  [normativo]** Los clientes y reconstructores DEBERÍAN (SHOULD) difundir por gossip
  `(triple, H_build, manifest-hash, release-index)` por GR-6 bajo la mezcla de fuentes de GR-8,
  y exigir pruebas de consistencia del registro de transparencia, de modo que un adversario que
  sirve el binario X a Alice y el binario Y a Bob (mismo triple, índice igual o conflictivo)
  sea atrapado por cualquier parte que tenga ambos (la defensa de equivocación ID-7a, para
  compilaciones). Un registro que controla los anexados de compilación tras un conjunto de
  firmantes es no conforme (RB-2a/ID-7).
- **RB-15 (las anomalías de compilación se difunden por gossip, no se suprimen). [normativo]**
  Cuatro eventos son anomalías de compilación que todo verificador DEBE (MUST) difundir por
  gossip al detectarlas, comparando solo hashes de triple-igual (RB-6b): (a) un `H_build` que
  falla la reproducción a partir de su manifiesto (RB-7a); (b) un registro de transparencia que
  presenta raíces inconsistentes sobre los anuncios de compilación (equivocación demostrada);
  (c) una divergencia persistente de `H_build` de triple-igual frente a reproductores
  independientes; (d) una **regresión de índice de versión** —una etiqueta presentada con un
  índice menor que uno ya atestiguado para esa línea de versión (la firma del downgrade,
  RB-9a). Un verificador NO DEBE (MUST NOT) suprimir una anomalía para hacer que una versión
  parezca sana (la regla de señal inmune ID-10, para compilaciones).

## 10. Lo que esta parte no resuelve (el residual declarado)

Esta parte hace que dos partes que *ambas reconstruyen* concuerden de forma demostrable o
detecten de forma demostrable que difieren, y mueve la confianza de *quién lo compiló* a *¿se
reconstruye?* —una reducción real y grande, la correcta para un proyecto seudónimo. **No**
hace que el binario sea *seguro*. Las brechas son reales y se declaran, no se suavizan:

- **§10.1 — Una puerta trasera en una dependencia fijada se reproduce fielmente, no se
  atrapa.** Si un crate vendorizado contiene código hostil, cada reconstructor obtiene el
  binario malicioso idéntico y RB-7 *confirma* la coincidencia —la reproducción funciona
  exactamente como se diseñó y es ciega a la malicia. El binario refleja honestamente código
  fuente que está honestamente con puerta trasera. Las únicas defensas son **la revisión
  pública (I-1), la auditoría (RB-16), y minimizar la superficie de dependencias
  (RB-5/RB-17)** —procesos humanos que *acotan* la superficie, ninguno una verificación
  criptográfica libre de autoridad. **Este es el residual primario, no tiene sustituto no
  confiable, y es el problema recurrente del proyecto llevando una cuarta máscara —OP-10.** La
  propuesta de valor es honesta precisamente aquí: la reproducibilidad **no** defiende contra
  el ataque del mundo real más probable, y nunca pretendió hacerlo —pero cambia *qué tipo* de
  ataque se requiere. Sin ella, un atacante envenena **un binario para un destino**, de forma
  invisible e inatribuible. Con ella, un binario malicioso debe trazarse hasta **código fuente
  público** que **todo el mundo puede revisar** y que **reproduce idénticamente para todos**
  —forzando el ataque de "envenena el binario" (invisible, por destino) a "envenena el código
  fuente público o una dependencia pública" (revisable, universal, máximamente expuesto al
  único revisor honesto). Esa transformación es el valor de la parte; atrapar el código fuente
  envenenado es OP-10 e I-1, no la reproducibilidad.
- **§10.2 — Una cadena de herramientas comprometida que miscompila de forma reproducible.** Un
  `rustc`/LLVM con puerta trasera puede insertar comportamiento ausente del código fuente, de
  forma determinista, así que cada reconstructor reproduce el binario malo idéntico y la
  igualdad de `H_build` se sostiene. Fijar (RB-3) hace que todos compartan un compilador y hace
  *intercambiarlo* detectable; no hace honesto al compilador fijado. **Ningún sustituto no
  confiable** salvo arranque-desde-código-fuente o doble-compilación-diversa, que esta parte
  nombra como trabajo futuro (RB-3b), no un requisito actual.
- **§10.3 — "Trusting-trust" (Thompson).** El caso general del §10.2: un compilador que pone
  puertas traseras *y* propaga la puerta trasera a los compiladores que construye. Fijar los
  bytes del compilador no rompe el bucle; garantiza que todo el mundo está dentro del *mismo*
  bucle. Declarado, no resuelto. (Por esto RB-18 dice "cada byte de salida se traza hasta una
  entrada *fijada*" —procedencia— y explícitamente **no** "hasta una entrada honesta": un
  compilador con hash, fijado y con puerta trasera satisface la trazabilidad y sigue siendo
  malicioso.)
- **§10.4 — Reproducible ≠ seguro; reproducible ≠ revisado.** Una compilación perfectamente
  reproducible de código fuente de apariencia honesta pero sutilmente erróneo es perfectamente
  reproducible. La seudonimia (RB-12) significa que ningún autor confiable da fe del código
  fuente, así que la honestidad-del-fuente descansa enteramente en la revisión pública (I-1);
  la reproducibilidad y la revisión son ortogonales (RB-12b).
- **§10.5 — La corroboración-por-cuenta se reduce a OP-2; el cliente no reconstructor es el
  usuario modal.** "N reconstructores independientes obtuvieron `H_build`" es solo tan fuerte
  como la *independencia* de los N (RB-10, GR-19a). Una sola re-reproducción honesta refuta una
  afirmación falsa con certeza (más fuerte que el caso del mapa, porque el código fuente es
  determinista), pero un cliente que **no puede reconstruir** (RB-7b —el teléfono, es decir,
  casi todos los usuarios) se apoya en la cuenta de atestaciones, que es un quórum votable por
  sybil: un adversario acuña atestaciones seudónimas para un `H_build` malo, y un cliente
  **eclipsado** ve solo atestaciones del adversario y nunca encuentra un reproductor honesto.
  Así que para el cliente no reconstructor o eclipsado, "ninguna autoridad" significa "confía
  en el quórum de reproductores verificados", y eso se sostiene solo hasta donde lo haga
  **OP-2**. Esta parte **reduce** la autoridad de compilación a OP-2 para el no reconstructor;
  no la disuelve —la reducción idéntica con la que termina la Parte 8 (ID-1 → OP-2).
- **§10.6 — El árbitro está acotado por vivacidad; la garantía debe replicarse o es un
  singleton.** Reconstruir-y-comparar es el árbitro libre de autoridad **solo mientras las
  entradas fijadas sean aún obtenibles**. Los binarios de la cadena de herramientas y el árbol
  completo de crates son grandes y perecederos: un **crate retirado (yanked)** o una **versión
  de cadena de herramientas despublicada** hace `rebuild(manifest)` inejecutable, y entonces la
  única operación confiable desaparece —lo peor precisamente para las disputas forenses ("¿tenía
  v1.2 una puerta trasera?") que más la necesitan. Un despliegue conforme DEBERÍA (SHOULD)
  depositar en garantía los bytes de entrada fijados en un almacén direccionado por contenido
  **replicado a través del mismo conjunto de espejos sin permisos** que las compilaciones; una
  garantía de réplica única es direccionada por contenido (así que no puede *mentir*) pero es un
  **singleton de vivacidad** (puede *desaparecer*), e I-3 cubre la vivacidad. En ausencia de
  replicación, RB-7 se declara **acotado por vivacidad**, no incondicional (el residual de
  vivacidad ID-5a, para compilaciones).
- **§10.7 — El determinismo es un blanco móvil frente a la rotación de la cadena de
  herramientas.** Las nuevas versiones de `rustc`/LLVM introducen nuevas fuentes de no
  determinismo (nuevos pases paralelos, nuevos metadatos, nuevo comportamiento de `cfg`). El
  conjunto de peligros de RB-6 es **actual**, no cerrado; una cadena de herramientas fijada es
  reproducible *tal como se fijó*, pero cada salto de cadena de herramientas es una obligación
  fresca de auditoría-de-determinismo, y el manifiesto registra contra qué versión del conjunto
  de peligros se compiló (RB-6, RB-8). "Reproducible una vez" no significa "reproducible para
  siempre".
- **§10.8 — TOFU del primer binario: un primer binario malicioso miente sobre reproducirse a sí
  mismo.** El *primer* binario cliente de un usuario nuevo no puede reproducirse antes de usarse
  para el arranque (necesitas un cliente funcional para obtener el código fuente, la cadena de
  herramientas, y alcanzar los registros y pares). El primer binario se adopta por
  confianza-en-el-primer-uso exactamente como el primer mapa de la Parte 8 (ID-8) —y peor: un
  primer binario comprometido posee a partir de entonces todo el aparato de reproducción y
  gossip del usuario, así que puede **mentir sobre su propia reproducción** ("me reconstruí a mí
  mismo; `H_build` coincide"). Un cliente por tanto no puede verificar honestamente *su propia*
  reproducción; la confianza en el primer binario descansa en un **reproductor independiente
  fuera de banda** —una máquina/cadena de herramientas diferente en la que el usuario confía más
  que en el binario bajo prueba. Esta es la frontera de "trusting-trust" / host-comprometido
  (§10.9); es un residual declarado, enunciado aquí en lugar de tragado silenciosamente por
  "fuera de alcance".
- **§10.9 — Lo que esta parte ni siquiera intenta.** El compromiso en tiempo de ejecución de la
  máquina del usuario; una *compilación maliciosa de código fuente honesto por el propio
  usuario* en un host comprometido (la reproducción confirma la coincidencia; el host aún posee
  el proceso); y todo lo que está por encima de la frontera del artefacto —instalación, y
  *adopción* de actualizaciones (qué compilación ejecutar y cuándo), que es el ítem 4.1. La
  parte es solo-artefacto-idéntico-a-nivel-de-bit; nombra estos como fuera de alcance, no como
  resueltos.

El resumen honesto: las compilaciones reproducibles mueven la confianza de *quién lo compiló*
a *¿se reconstruye?* —real y grande. Pero son **silenciosas** sobre si el código fuente es
honesto (§10.1, §10.4), **ciegas** a una puerta trasera reproducible de compilador/dependencia
(§10.1, §10.2, §10.3), **acotadas por vivacidad** como árbitro (§10.6), **reducidas a OP-2**
para el cliente no reconstructor o eclipsado (§10.5) —el usuario modal (RB-7b)— y **TOFU** en
el primer binario (§10.8). Estos son el precio de rechazar una autoridad de versión. La
respuesta correcta es acotarlos —minimizar y auditar la base de cómputo confiable, replicar la
garantía, fomentar las reconstrucciones independientes, portar el índice de frescura— y
enunciarlos, no ocultarlos.

## 11. Higiene de cadena de suministro que acota el residual

- **RB-16 (la auditoría de dependencias y de la cadena de herramientas es obligatoria y está en
  alcance).** Porque la reproducción no puede ver una puerta trasera que cada reconstructor
  reproduce fielmente (§10.1), la parte DEBE (MUST) requerir un rastro de auditoría commiteado y
  revisable para el conjunto de dependencias y la cadena de herramientas (registros al estilo
  `cargo-vet`/`cargo-audit`, fijados por contenido), tratado como **evidencia de revisión (I-1),
  no como autoridad**. La auditoría reduce la superficie de ataque del §10.1; no la elimina, y la
  parte lo dice.
- **RB-17 (minimiza la base de cómputo confiable).** La parte DEBERÍA (SHOULD) requerir encoger
  activamente lo que debe ser confiado-y-auditado: menos dependencias (RB-5), menos
  `build.rs`/proc-macros (RB-5b), una superficie de cadena de herramientas más pequeña (RB-3a),
  `#![forbid(unsafe_code)]` donde sea factible —porque cada elemento de la base de cómputo
  confiable es un residual del §10.1 que la auditoría debe cubrir y la reproducción no puede.
  Nota honesta: "mínima" no es "pequeña" —un nodo real de async + cripto (un runtime async, una
  pila Sphinx/X25519, CBOR, …) arrastra *cientos* de crates transitivos, muchos con scripts de
  compilación, así que el residual de puerta-trasera-en-dependencia del §10.1 no es un caso
  esquinero sino la superficie de ataque **esperada**. Ese es el encuadre honesto de OP-10.
- **RB-18 (toda la cadena está fijada o no está fijada —y fijada significa procedencia, no
  honestidad). [normativo]** Una sola entrada no fijada en cualquier lugar —un componente de
  cadena de herramientas sin hash, una dependencia flotante, un `build.rs` que lee el host, una
  imagen base de contenedor obtenida por etiqueta— anula la afirmación de reproducibilidad para
  todo el artefacto, porque esa única entrada reintroduce un servidor o un host como parte
  confiable (RB-1). El manifiesto DEBE (MUST) ser **completo**: si un byte de salida no puede
  trazarse hasta una entrada *fijada*, la compilación es no conforme (la regla ID-4c, para
  software). **Esta es una afirmación de determinismo/procedencia, no una afirmación de
  confianza:** una entrada fijada puede ser maliciosa (§10.1, §10.2, §10.3); fijar hace la
  malicia idéntica para todos y cualquier *divergencia respecto a una entrada honesta*
  detectable —**no** hace honesta a la entrada. "Fijada" nunca significa "segura".

## 12. Requisitos introducidos aquí

- **RB-1 / RB-2 / RB-2a** — ninguna autoridad de versión, la reproducción es el árbitro; las
  firmas solo localizan, nunca autorizan; herramientas compartidas con el mapa, nunca autoridad
  compartida.
- **RB-3 / RB-3a / RB-3b** — cadena de herramientas fijada por contenido a través de toda la
  superficie de compilación; el compilador fijado es un residual declarado de "trusting-trust"
  (procedencia, no honestidad).
- **RB-4 / RB-4a / RB-4b** — compilación hermética, sin conexión y sin estado ambiente; sin
  obtención en tiempo de compilación; un entorno fijo con `SOURCE_DATE_EPOCH` **derivado** del
  commit etiquetado.
- **RB-5 / RB-5a / RB-5b** — árbol de dependencias mínimo, vendorizado y fijado por contenido; el
  lockfile es necesario-no-suficiente; los scripts de compilación y los proc-macros son cómputo
  confiable en sandbox.
- **RB-6 / RB-6a / RB-6b** — conjunto de peligros de no determinismo normativo y versionado por
  la cadena de herramientas; `H_build` es el único nombre; `H_build` es por-(fuente, manifiesto,
  triple de destino) y la concordancia es dentro de un triple.
- **RB-7 / RB-7a / RB-7b** — el reconstruir-y-comparar del extraño; rechaza lo irreproducible; el
  usuario modal no reconstructor rastrea `reproducido-por-otros-no-verificado` y se reduce a OP-2.
- **RB-8 / RB-8a / RB-9 / RB-9a** — el manifiesto es la receta, canónico y direccionado por
  contenido, portando un índice de versión monótono; la concordancia es igualdad de hash de
  triple-igual; el residual de frescura (downgrade reproducible) con el campo de manifiesto que
  4.1 necesita.
- **RB-10 / RB-10a** — una atestación es una afirmación de reproducción ponderada por
  re-reproducción independiente (cuenta solo las verificadas, nunca las crudas; la independencia
  es OP-2); formato canónico, deduplicación por reproductor.
- **RB-11 / RB-12 / RB-12a / RB-12b** — vector de prueba de compilación entre hosts; la confianza
  fluye solo a través de la reproducibilidad; las claves de seudónimo localizan, nunca fundan
  confianza (con la precondición hecha explícita, no circular); reproducibilidad ⊥ revisión.
- **RB-13 / RB-14 / RB-15** — registro sin permisos de tuplas de compilación ordenadas por índice
  de versión; gossip + detección de vista partida; cuatro anomalías obligatorias incluida la firma
  del downgrade.
- **RB-16 / RB-17 / RB-18** — auditoría obligatoria como evidencia de revisión; minimiza la TCB
  (que sigue siendo grande); toda la cadena fijada, donde fijada es procedencia, no honestidad.

RB-1 y RB-7 son los dos portantes: ninguna autoridad, y la reproducción es el árbitro. Ambos
están acotados, no son absolutos —RB-1 se reduce a OP-2 para el cliente que no reconstruye
(§10.5, el usuario modal), y RB-7 está acotado por vivacidad (§10.6). El residual más afilado,
enunciado y no oculto, es el §10.1: **la reproducibilidad no atrapa una dependencia con puerta
trasera, que es el ataque real más probable —fuerza el ataque hacia código fuente público,
revisable y universal, que es el objetivo, y atraparlo ahí es OP-10, no esta parte.** Rompe esta
parte nombrando un paso de compilación que necesite una parte confiable, un artefacto publicado
que no pueda reconstruirse a partir de su manifiesto, un peligro de determinismo que RB-6 pase por
alto, una forma en que una firma contrabandee de vuelta la autorización sorteando RB-2, o una
forma en que el cliente no reconstructor quede confiando en una mayoría que no es OP-2. Esa es la
invitación, en la voz de la Parte 8.
