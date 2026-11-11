# Especificación de ScrambNet — Parte 8: El conjunto de datos de inferencia
> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../../en/spec/08-inference-dataset.md)).

**Estado: BORRADOR (DRAFT), y un riesgo de investigación declarado.** Esta parte
decide cómo un cliente obtiene el mapa de IP-a-AS (y jurisdicción gruesa) del que
la Parte 3 infiere (PS-4), bajo I-3 — ninguna autoridad — frente a relés y hosts
del conjunto de datos que mienten sobre todo salvo lo que un hash o una firma
vincula. Los valores de hombre de paja se marcan con `(s)`. El *uso* del mapa para
la verificación de disjunción es OP-1; su *distribución* es el ítem 2.3 de la
planificación.

La decisión principal se enuncia en el §1 y se defiende en el resto. Lee primero
el §1 y el §9 (el residual): entre ambos dicen qué compra esta parte y qué admite
que no puede comprar.

## 1. La decisión, en dos frases

- **No hay mapa canónico ni autoridad del mapa.** El conjunto de datos es un
  **artefacto reproducible, direccionado por contenido** que cualquier parte
  reconstruye byte a byte a partir de entradas públicas; dos clientes concuerdan no
  porque confíen en un firmante, sino porque computaron el **mismo hash** (ID-1,
  ID-5). Una raíz canónica firmada por un conjunto fijo sería una autoridad de
  directorio con otro nombre, e I-3 lo prohíbe.
- **La concordancia es por reproducción; la publicación es por un registro de
  transparencia de solo-anexado en el que cualquiera puede escribir; la confianza
  en la primera obtención es TOFU, declarada como tal.** El registro no *bendice*
  un mapa — lo marca temporalmente y hace detectable la equivocación (ID-6, ID-7).
  El primer mapa de un cliente recién llegado es un momento de confianza-en-el-
  primer-uso que el gossip posterior le permite **detectar** como malo, no
  **prevenir** (§7).

Así que el resultado honesto que la planificación señaló es el real: **mapa TOFU +
registro de transparencia + gossip de anomalías, no un mapa canónico.** Todo lo que
sigue es la construcción que hace concreto "reprodúcelo tú mismo, y detecta a
cualquiera que mintió", y el §9 es el residual que ninguna cantidad de construcción
elimina.

## 2. Alcance y la trampa que esta parte evita

La Parte 3 (PS-4, PS-5) exige que cada cliente infiera el AS y la jurisdicción
gruesa de un relé *a partir de sus `addrs`*, usando el conjunto de datos **propio**
del cliente, nunca la autodeclaración de un relé (GR-3). Esta parte trata solo de
**de dónde viene ese conjunto de datos y cómo dos clientes saben que tienen el
mismo** sin una parte confiable en ningún punto de la cadena — construcción,
publicación o arranque.

La trampa es sutil y debe nombrarse: el diseño "sin confianza" más fácil es una
instantánea canónica firmada, publicada por un pequeño conjunto de mantenedores.
Eso es exactamente la autoridad Walking-Onions que este proyecto se negó a sí mismo
para los relés (alcance de GR-1), ahora recolada para la geografía. Un firmante del
mapa que pueda distribuir sigilosamente un mapa que etiquete mal un bloque de ASes
puede hacer que los relés colocados juntos de un adversario *parezcan* disjuntos a
todos los clientes — un eclipse a granularidad de geografía que derrota a la Parte 3
tan seguramente como lo haría un directorio de relés malo. Así que el conjunto de
firmantes es la amenaza, y el diseño no debe tener uno con ese poder.

- **ID-1 (ninguna autoridad del mapa). [normativo]** Ningún paso de obtención,
  validación o actualización del conjunto de datos DEBE (MUST) requerir confiar en
  que una parte concreta produjo, firmó o bendijo el mapa; equivalentemente,
  obtener y validar el mapa DEBE (MUST) ser posible usando únicamente sustitutos no
  confiables. Las únicas operaciones confiables son: (a) recomputar un hash, y (b)
  reconstruir el artefacto a partir de entradas públicas y comparar. Todo elemento
  de diseño que no pueda ser reemplazado por un sustituto no confiable que realice
  (a) o (b) es un defecto bajo I-3 y DEBE (MUST) eliminarse o declararse en el §9.

## 3. Qué es el mapa

- **ID-2 (forma del artefacto).** El conjunto de datos es un único artefacto
  comprimido, el **mapa**, que contiene, para el espacio IPv4 e IPv6:
  - una tabla **prefijo-IP → AS-de-origen** (búsqueda por coincidencia del prefijo
    más largo), y
  - una tabla **AS → jurisdicción-gruesa**, donde "jurisdicción" es una etiqueta a
    **nivel de país** derivada de la asignación de los RIR, deliberadamente gruesa —
    una granularidad más fina es ruido que esta parte no fingirá resolver (§9).
  El mapa lleva una cabecera autodescriptiva: versión de formato `1`, la **época**
  (epoch) de la instantánea (ID-4), el manifiesto exacto de entradas (ID-3) y la
  versión de la herramienta de construcción. El artefacto se direcciona por `H =
  BLAKE2s(artifact)` (el hash de la suite, Parte 0); `H` es el único nombre del
  mapa. No hay ninguna cadena de versión legible por humanos en la que se pudiera
  confiar en lugar de `H`.
- **ID-2a (la búsqueda es total).** Toda búsqueda DEBE (MUST) devolver o bien un
  `(AS, jurisdicción)` concreto o bien el valor explícito **`unknown`**. `unknown`
  es una respuesta de primera clase, no un error, y la Parte 3 (PS-5) ya lo trata
  de forma conservadora (`unknown` comparte con todo). El mapa NO DEBE (MUST NOT)
  adivinar para evitar un `unknown`; una respuesta fabricada es peor que una laguna
  admitida, porque derrota silenciosamente a PS-5.

## 4. Cómo se construye el mapa (de forma reproducible, a partir de entradas públicas)

La construcción es una **función pura de entradas públicas nombradas a un artefacto
idéntico byte a byte**. El determinismo es todo el juego: si dos partes honestas
pueden divergir, la igualdad de hash (ID-5) deja de significar "mismo mapa" y el
diseño colapsa en necesitar una autoridad que deshaga los empates.

- **ID-3 (entradas públicas, fijadas por contenido). [normativo]** El mapa DEBE
  (MUST) construirse únicamente a partir de entradas que sean públicas,
  reproducibles y a su vez fijadas por contenido en el manifiesto del artefacto
  mediante sus propios hashes:
  - **Tablas de enrutamiento BGP** para el AS de origen: los colectores del proyecto
    **RouteViews** y los colectores **RIPE RIS** (volcados MRT `RIB`). Estos son los
    archivos BGP públicos estándar y multi-ventaja; usar varios colectores de ambos
    proyectos es en sí mismo una medida de diversidad (la vista de ningún colector
    único es autoritativa, ID-3a).
  - **Estadísticas de delegación de los RIR** para el mapeo AS → país: los ficheros
    **delegated-extended** publicados por los cinco RIR (ARIN, RIPE NCC, APNIC,
    LACNIC, AFRINIC). Estos dan los códigos de país de asignación para los números de
    AS y los bloques de direcciones sin que nadie se autodeclare.
  El manifiesto DEBE (MUST) listar cada fichero de entrada por su hash de contenido
  independiente de la URL y por su marca de tiempo declarada en origen, de modo que
  las entradas — no un servidor — definan la construcción. Una parte reconstruye
  obteniendo las entradas con esos hashes desde **cualquier** espejo (I-3: la fuente
  es reemplazable; los bytes están fijados).
- **ID-3a (resolución de origen multi-ventaja).** El AS de origen de un prefijo DEBE
  (MUST) resolverse a través de **todos** los colectores del manifiesto mediante una
  regla fija (ID-4b), no a partir de un solo colector. Un prefijo visto con orígenes
  conflictivos a través de puntos de ventaja se resuelve de forma determinista y,
  donde el conflicto es real (MOAS — AS de origen múltiple), se registra como un
  **conjunto**, que la Parte 3 trata como "posiblemente cualquiera de estos", es
  decir, compartido de forma conservadora (§9). El mapa NO DEBE (MUST NOT) elegir
  uno silenciosamente.

### 4.1 Peligros de determinismo y cómo la construcción los fija

Cada peligro de abajo es un lugar donde dos constructores honestos podrían producir
bytes diferentes. El procedimiento de construcción DEBE (MUST) eliminar cada uno;
una construcción que no lo hace es no conforme porque no puede soportar a ID-5.

- **ID-4 (época de la instantánea — temporización del volcado). [normativo]** Los
  datos BGP y de los RIR cambian continuamente, así que "el volcado actual" no es
  una función. La construcción DEBE (MUST) fijar un único **límite de época**: un
  instante UTC en una cadencia fija (hombre de paja: la instantánea de las **00:00
  UTC** en una cadencia **semanal (s)** — los commits de la Parte 0 ya usan UTC), y
  DEBE (MUST) usar, para cada colector/RIR del manifiesto, el **último volcado cuya
  marca de tiempo declarada en origen sea ≤ el límite de época**. Dos constructores
  que apuntan a la misma época seleccionan por tanto los mismos ficheros de entrada
  independientemente de cuándo se ejecuten. La época está en la cabecera del
  artefacto (ID-2) y en la preimagen de `H`.
- **ID-4a (orden).** Todas las tablas DEBEN (MUST) emitirse en un **orden total
  fijo**: prefijos ordenados por (familia de direcciones, dirección de red numérica,
  longitud de prefijo); entradas de AS por ASN numérico; jurisdicciones por su
  cadena fija de código de país. Ningún orden de iteración de mapa, orden de tabla
  hash u orden de fichero de entrada puede alcanzar la salida.
- **ID-4b (el desempate está especificado, no definido por la implementación).
  [normativo]** Todo lugar donde los datos son ambiguos DEBE (MUST) tener una regla
  escrita en esta parte, sin ningún "elige uno" dejado al implementador:
  - *AS de origen a través de los colectores:* toma el conjunto de orígenes
    observado; si es un único AS, emítelo; si son varios (MOAS), emite el conjunto
    completo ordenado ascendentemente. Nunca colapses un MOAS a un solo AS por
    popularidad — eso es una conjetura (§9).
  - *Prefijos superpuestos:* la semántica de coincidencia del prefijo más largo se
    preserva almacenando todos los prefijos; la búsqueda, no la construcción,
    resuelve la especificidad.
  - *Conflicto AS-a-país entre los RIR:* si los ficheros de delegación discrepan
    sobre el país de un AS, emite `unknown` para la jurisdicción de ese AS. Un
    desacuerdo entre registros públicos es exactamente un caso que el mapa no debe
    resolver por decreto.
- **ID-4c (entradas flotantes prohibidas).** La construcción NO DEBE (MUST NOT)
  consultar ninguna entrada que no esté en el manifiesto — ni DNS en vivo, ni WHOIS
  en tiempo de construcción, ni base de datos de geolocalización bajo una licencia
  que prohíba la redistribución o que no sea reproducible, ni feed comercial de
  inteligencia de IP. Cada byte de la salida se traza hasta una entrada pública con
  hash. (Esto descarta los feeds convenientes-pero-inverificables; su exactitud no
  vale la autoridad que reintroducen.)
- **ID-4d (contenedor canónico).** La compresión y el encuadre del artefacto DEBEN
  (MUST) ser deterministas (códec fijo, nivel fijo, sin marcas de tiempo ni nombres
  de fichero en los metadatos del contenedor). La construcción está especificada con
  suficiente rigor como para que una herramienta de construcción conforme sea ella
  misma reproducible (planificación 4.2), y DEBE (MUST) existir un **vector de prueba
  del mapa** entre implementaciones (un manifiesto de entradas → `H` esperado) de
  modo que una segunda implementación pueda demostrar que construye el artefacto
  idéntico (se vincula con la planificación 3.2).

## 5. Cómo dos clientes concuerdan en que tienen el mismo mapa

- **ID-5 (la concordancia es la igualdad de hash, nada más). [normativo]** Dos
  clientes tienen el mismo mapa **si y solo si** sus hashes de artefacto `H` son
  iguales. La comparación es una verificación de igualdad de 32 bytes; no necesita
  firmante, ni quórum, ni autoridad. Los clientes intercambian `H` por gossip
  (ID-8); un `H` igual es prueba del mismo mapa, un `H` desigual es prueba de que
  difieren y DEBE (MUST) reportarse al usuario como una **divergencia** (ID-9),
  nunca reconciliarse silenciosamente hacia ninguno de los dos lados.
- **ID-5a (la reconstrucción es el árbitro).** Cuando dos clientes tienen un `H`
  diferente para la misma época, la disputa es resoluble por **cualquiera**, sin
  apelación a autoridad: reconstruir a partir de las entradas del manifiesto (ID-3) y
  ver qué `H` producen realmente las entradas públicas. Un mapa cuyo `H` no puede
  reproducirse a partir de su manifiesto declarado no es, por definición, el mapa de
  esas entradas, y DEBE (MUST) rechazarse (ID-5b). Esta es la propiedad que permite
  que el sistema no tenga autoridad: *la verdad es la reproducibilidad, no la firma.*
- **ID-5b (rechaza lo irreproducible).** Un cliente que tiene las entradas (o las
  obtiene) y descubre que `H ≠ BLAKE2s(rebuild(manifest))` DEBE (MUST) descartar ese
  mapa y DEBERÍA (SHOULD) difundir por gossip la discrepancia como una anomalía
  (ID-10). Un cliente sin el ancho de banda para reconstruir PUEDE (MAY) aceptar un
  mapa en términos de TOFU/consenso (§6, §7) pero DEBE (MUST) rastrearlo como **no
  verificado** hasta que él (o un par con el que luego concuerde) reconstruya.

## 6. El registro de transparencia (y por qué no es la autoridad)

La igualdad de hash les dice a dos clientes que *difieren*; no defiende por sí sola
contra un adversario que alimenta a clientes **diferentes** con mapas
**diferentes** manteniendo a cada cliente internamente consistente — un **ataque de
vista partida (equivocación)**. El registro de transparencia existe exactamente para
esa amenaza y para nada más.

- **ID-6 (qué es el registro).** El registro es un **árbol de Merkle de solo-
  anexado** (estructura RFC 6962 / Certificate-Transparency: un árbol de Merkle
  sobre una secuencia de hojas, con pruebas de inclusión y pruebas de consistencia
  entre dos tamaños de árbol). Cada **hoja** es un anuncio de mapa: `(epoch, H,
  manifest-hash)`. El estado del registro se resume por su **cabecera de árbol
  firmada** — aquí, un **hash de raíz** a un tamaño de árbol. El registro demuestra
  dos cosas criptográficamente: que un `H` dado **está incluido** (prueba de
  inclusión) y que el registro **solo creció, nunca reescribió la historia** (prueba
  de consistencia). No demuestra nada sobre si `H` es un mapa *bueno* — la
  reproducción (ID-5a) hace eso.
- **ID-7 (quién puede anexar — sin permisos, así que no es una autoridad).
  [normativo]** **Cualquiera** PUEDE (MAY) anexar una hoja anunciando un mapa que
  construyó; no hay anexador privilegiado, ni lista de permitidos, ni conjunto de
  firmantes cuya firma haga oficial un mapa. El registro, por tanto, **no** es lo
  que se confía — es un **tablón de anuncios atestiguado y a prueba de
  manipulación**. Su único poder es hacer la equivocación *detectable*; **no tiene
  poder para elegir el mapa**, que es lo que lo mantiene fuera de la prohibición de
  I-3. Un registro que controlara los anexados tras un conjunto de firmantes SERÍA la
  autoridad de directorio que I-3 prohíbe, y tal diseño es no conforme (ID-1).
- **ID-7a (detección de equivocación mediante raíces difundidas por gossip).
  [normativo]** La defensa contra una vista partida **no** es confiar en el operador
  del registro; es **difundir por gossip las cabeceras de árbol firmadas del registro
  por el canal de gossip GR existente** (GR-6) y exigir **pruebas de consistencia**
  entre cualesquiera dos raíces que un cliente vea. Si un registro llegara a
  presentar dos cabeceras de árbol que no son extensiones consistentes una de la otra
  — la firma de la equivocación — cualquier cliente que observe ambas (directamente o
  vía una raíz difundida por un par) tiene **prueba criptográfica** de que el registro
  mintió, y DEBE (MUST) tratar ese registro como hostil (ID-10). Dado que las raíces
  se difunden ampliamente (GR-6 mezcla fuentes, GR-8), un registro no puede mostrarle
  al cliente A la raíz X y al cliente B la raíz Y por mucho tiempo sin que algún
  cliente tenga ambas y lo pille.
- **ID-7b (múltiples registros, ninguno canónico). [normativo]** **No hay un único
  registro.** Los clientes DEBEN (MUST) soportar **varios registros independientes**
  y tratar un mapa como corroborado-por-registro solo si aparece, con raíces
  difundidas consistentes, en un quórum configurable de los registros que el cliente
  vigila (hombre de paja: **≥2 de los registros de su conjunto (s)**). Esto elimina el
  último punto único: ningún operador de registro individual es portante, y el
  conjunto de registros de un cliente — como su muestra de relés — es diverso y
  reemplazable (lógica de GR-8 aplicada a los registros). Un registro que se apaga se
  rodea, exactamente como se rodea un relé que se apaga.
- **ID-7c (el registro almacena compromisos, no el mapa).** Las hojas llevan
  `(epoch, H, manifest-hash)` — decenas de bytes — nunca el artefacto. El mapa en sí
  se obtiene direccionado por contenido mediante `H` desde cualquier espejo o par
  (ID-8); el registro solo atestigua *qué* valores de `H` se anunciaron y *cuándo*,
  de modo que el almacenamiento del registro sigue siendo trivial y ningún registro
  se convierte en el cuello de botella de la distribución.

## 7. La paradoja del arranque, enunciada honestamente

Un cliente recién llegado no tiene ninguna muestra de relés que pueda evaluar ni
ningún mapa previo; debe obtener su **primer** mapa por rutas cuya disjunción
**todavía no puede verificar** (esa verificación necesita el mismísimo mapa que
está obteniendo). Esta es una genuina dependencia circular, y esta parte no finge
romperla.

- **ID-8 (el arranque es confianza-en-el-primer-uso, declarada). [normativo]** El
  primer mapa que obtiene un cliente recién llegado es una decisión **TOFU**. El
  cliente DEBE (MUST) obtenerlo por tantos canales **independientes** como tenga
  (hombre de paja: la línea de puentes fuera de banda de GR-10, más dos o más
  espejos públicos alcanzados por redes distintas (s)), DEBE (MUST) exigir el
  **mismo `H`** de todos ellos antes de aceptarlo provisionalmente, y DEBE (MUST)
  registrar el mapa como **no-verificado-TOFU** hasta que o bien (a) reconstruya a
  partir de las entradas (ID-5a) o bien (b) acumule raíces difundidas consistentes y
  concordancia de `H` con pares (ID-7a, ID-9) por encima de un umbral de confianza.
  El cliente DEBE (MUST) exponer este estado: *estás confiando en tu primer mapa;
  todavía no ha sido corroborado.*
- **ID-8a (cota de lo que un mal primer mapa le compra al adversario). [normativo]**
  Un adversario que controla toda la primera obtención de un cliente recién llegado
  puede entregarle un mapa que etiquete mal los ASes de modo que los relés colocados
  juntos parezcan disjuntos. La cota del daño es triple y DEBE (MUST) preservarse en
  el diseño:
  1. **El contenido sigue con umbral.** Incluso un mapa totalmente adversarial no
     puede bajar el umbral incondicional del contenido I-2: solo puede hacer que el
     cliente *juzgue mal la disjunción*, lo cual (según PS-11 y el simulador, §10)
     erosiona la **vinculación mucho más rápido que el contenido** — una ruptura de
     contenido sigue necesitando al adversario en ≥`k` circuitos a la vez. Un mal
     mapa es un ataque de metadatos, no un ataque de contenido. Esta asimetría es la
     razón individual más importante de que la paradoja del arranque sea
     sobrevivible.
  2. **Es temporal y detectable, no permanente.** En el momento en que el cliente
     difunde por gossip su raíz/`H` (ID-9) o reconstruye (ID-5a), un mapa que ningún
     par honesto ni entrada pública corrobora destaca. El adversario debe mantener al
     cliente eclipsado **para siempre** para mantener el mal mapa sin exponer — lo
     cual es el problema de eclipse OP-2, no una debilidad nueva que esta parte
     introduce.
  3. **No puede falsificar la reproducción.** El adversario puede distribuir un `H`
     malo, pero no puede hacer que las entradas públicas reconstruyan a ese `H`
     (ID-5a). Un cliente que alguna vez reconstruya, o que alguna vez se encuentre
     con un par que lo hizo, converge al mapa real.
- **ID-8b (detectar, no afirmar que se previene). [normativo]** Esta parte
  proporciona **detección de un mal arranque a posteriori**, no prevención de él. Un
  cliente conforme NO DEBE (MUST NOT) presentar un mapa TOFU como verificado, DEBE
  (MUST) reevaluarlo a medida que llega el gossip y (opcionalmente) acumular
  reconstrucción, y DEBE (MUST) advertir si la corroboración no llega dentro de una
  ventana configurable (hombre de paja: unas pocas épocas (s)). "No podemos prevenir
  un mal primer mapa; hacemos que mantenerlo sin detectar sea caro y, con el tiempo,
  imposible" es la afirmación honesta, y es la afirmación que la interfaz enuncia.

## 8. Convivir con ello: refresco y manejo de divergencias

- **ID-9 (frescura del mapa y gossip).** Los clientes DEBEN (MUST) refrescar hacia
  el mapa de la época actual (cadencia ID-4) y DEBEN (MUST) difundir por gossip su
  `(epoch, H)` actual y las raíces de registro que tienen por los lotes de GR-6,
  sujeto a la mezcla de fuentes de GR-8 de modo que ninguna clase individual de par
  pueda dominar la vista de un cliente sobre qué mapa es el actual (la misma defensa
  contra eclipse, reutilizada). Un cliente NO DEBE (MUST NOT) ponderar un mapa por
  cuántos pares lo reportan *antes* de aplicar la regla de GR-8/PS-10 de "cuenta solo
  las fuentes verificadas independientemente" — un sybil no puede votar un mal mapa
  hacia el consenso por mera cantidad (se vincula con OP-2).
- **ID-9a (la divergencia se muestra, no se oculta).** Cuando el `H` de un cliente
  difiere de un quórum corroborado (ID-7b) para la misma época, DEBE (MUST) tratar
  su propio mapa como sospechoso, intentar reconstruir o re-obtener, y reportar la
  divergencia al usuario en la superficie de honestidad existente de la Parte 3
  (PS-9): *tu vista de la geografía de la red discrepa de la de tus pares; los
  juicios de disjunción pueden ser erróneos.* El silencio aquí dejaría correr un
  eclipse-de-geografía sin ser visto.
- **ID-10 (gossip de anomalías). [normativo]** Tres eventos son **anomalías** que
  todo cliente DEBE (MUST) difundir por gossip cuando las detecta, porque son las
  firmas observables de los ataques que esta parte no puede prevenir, solo exponer:
  (a) un `H` que falla la reproducción a partir de su manifiesto (ID-5b); (b) un
  registro que presenta raíces inconsistentes, es decir, equivocación demostrada
  (ID-7a); (c) una divergencia persistente de `H` frente a un quórum corroborado
  (ID-9a). El gossip de anomalías es la señal inmune de la red; un cliente NO DEBE
  (MUST NOT) suprimirlo para parecer sano.

## 9. La costura de fusión con la gobernanza de actualizaciones (OP-8 / ítem 4.1)

Los publicadores de raíces del mapa y los firmantes de las versiones de software
parecen que podrían ser un solo mecanismo. **Posición: mantenlos separados en la
confianza, aunque compartan herramientas.** El razonamiento es que tienen **formas
de confianza opuestas**:

- **ID-11 (la confianza del mapa es reproducción, no firma). [normativo]** El mapa
  se confía porque **se reconstruye a partir de entradas públicas** (ID-5a); su
  corrección **no** descansa en *quién* lo publicó. Un binario de versión, en
  cambio, se confía porque **se reconstruye a partir de código fuente público**
  (compilaciones reproducibles, planificación 4.1/4.2) — también reproducción,
  también no firma. Así que el *ancla de confianza* es la misma —
  **reproducibilidad, nunca identidad del autor** — y el proyecto DEBE (MUST)
  encaminar ambos a través de ella. Pero los **conjuntos de firmantes/anexadores
  DEBEN (MUST) permanecer distintos**: vincular los anexadores del registro del mapa
  a los firmantes de versiones crearía una única lista cuyo compromiso envenena
  *tanto* la inferencia de geografía *como* el software, es decir, exactamente el
  objetivo de coerción concentrada que el ítem 4.1 está construido para evitar. El
  registro del mapa es sin permisos (ID-7); el proceso de versiones puede tener un
  conjunto de firmantes nombrado (seudónimo) que solo *localiza* una compilación que
  no puede falsificar. Fusionarlos cambia la ausencia de permisos del mapa por la
  lista del proceso de versiones — la dirección equivocada.
- **ID-11a (compartir herramientas está bien; compartir autoridad no).** Ambos
  PUEDEN (MAY) reutilizar la misma construcción de registro de transparencia (ID-6)
  y el mismo canal de gossip (GR-6) — compartir *mecanismo* no cuesta nada. Lo que
  NO DEBEN (MUST NOT) compartir es un conjunto de partes cuya firma sea portante para
  ambos, porque ese conjunto sería el interruptor de apagado que I-3 prohíbe, ahora
  capaz de voltear tanto el mapa como el código.

## 10. Lo que esta parte no resuelve (el residual declarado)

Esta parte hace que dos clientes honestos concuerden de forma demostrable o
detecten de forma demostrable que difieren. **No** hace que el mapa sea
*verdadero*. La brecha entre "el mapa en el que concuerda todo cliente honesto" y
"dónde están físicamente los relés" es el residual, y es real:

- **La colocación conjunta tras prefijos disjuntos es indetectable aquí.** Un
  adversario que ejecuta relés en un centro de datos mientras anuncia espacio de
  direcciones que los datos BGP/RIR públicos atribuyen a ASes **diferentes** será
  etiquetado como disjunto por el mapa **correcto**. Ninguna construcción
  reproducible de datos públicos puede ver a través de un anuncio BGP de apariencia
  veraz hasta el rack que hay detrás. Esto se enuncia en el punto honesto más
  profundo de la planificación y se mantiene: **desde la superposición verificas
  consistencia contra un conjunto de datos de confianza acotada, no disjunción
  verdadera.** El trabajo es acotar lo que este adversario gana (ID-8a: el contenido
  sigue con umbral; el ataque es de metadatos/vinculación), no fingir que no existe.
- **BGP es genuinamente ambiguo en algunos puntos.** Los prefijos MOAS (un prefijo
  originado legítimamente por varios ASes), los **ASes hermanos** bajo un operador
  (ASN distintos, una parte controladora — el mapa ve dos ASes donde la realidad-de-
  disjunción es uno), y el **anycast** (un prefijo, muchos sitios físicos) no son
  errores del conjunto de datos; son el territorio. El mapa los maneja de forma
  conservadora (ID-3a, ID-4b: MOAS → conjunto, conflicto de registro → `unknown`), lo
  cual cuesta disponibilidad (más `unknown` ⇒ más repliegue, PS-11) en lugar de
  seguridad. La detección de ASes hermanos está explícitamente **fuera de alcance**
  de una construcción BGP/RIR pura y se deja como un punto ciego declarado: dos ASes
  hermanos se cuentan como disjuntos cuando no lo son.
- **La jurisdicción es gruesa por decisión.** Las etiquetas a nivel de país
  derivadas de los RIR son el umbral de resolución al que se compromete esta parte.
  El razonamiento jurisdiccional más fino (bloques de cooperación legal, la realidad
  de la asistencia legal mutua) deliberadamente **no** se codifica — sería un juicio
  de valor que ninguna construcción reproducible puede hacer sin importar una opinión
  confiable, lo cual ID-1 prohíbe.

El resumen honesto: **la tasa de error del conjunto de datos es un residual
declarado y no nulo, no un defecto a arreglar hasta cero.** Es el precio de rechazar
una autoridad. La respuesta correcta no es ocultarla, sino alimentarla al simulador
y mostrarle al usuario el nivel alcanzado (PS-9, PS-11).

## 11. La tasa de error alimenta al simulador (no se agita a mano)

El residual del §10 no es retórico; es la cantidad exacta que el simulador ya
consume. `poc/network_sim.py` expone **`infer_error`** — la probabilidad de que el
AS inferido por un cliente para un relé sea **erróneo** (la mitad de las veces un AS
erróneo, la mitad de las veces `unknown`), modelando un conjunto de datos que tanto
mapea mal como tiene lagunas (network_sim.py, `Network.random`). El mapa aquí
especificado **es** ese conjunto de datos, y su residual medido **es** esa perilla:

- **ID-12 (el mapa declara una tasa de error medida). [normativo]** Una versión de
  mapa conforme DEBE (MUST) distribuirse con una **estimación de error medida** — su
  tasa de desacuerdo frente a muestras públicas independientes de verdad-de-terreno y
  su fracción de `unknown` — derivada de forma reproducible a partir de datos
  públicos, de modo que el número en sí no tenga autoridad detrás. Ese par medido
  (tasa de mapeo erróneo, tasa de `unknown`) es el valor que un cliente alimenta a la
  maquinaria de confianza de la Parte 3 (planificación 2.2) y el valor que el
  simulador barre como `infer_error`.
- **ID-12a (el caso de error cero es el mejor caso, nunca el esperado).** Según
  PS-11, los números de error cero y vista completa del simulador son el **mejor**
  caso; un cliente conforme DEBE (MUST) presentar el nivel de disjunción alcanzado
  (PS-9) usando el error declarado de su mapa **real**, y la interfaz NO DEBE (MUST
  NOT) citar una cifra de ruptura de contenido como si acotara también la vinculación
  (PS-11) — la asimetría que hace sobrevivible un mal mapa (ID-8a) es la misma
  asimetría que la interfaz no debe reportar erróneamente como seguridad.

## 12. Requisitos introducidos aquí

- **ID-1** — ninguna autoridad del mapa: confía solo en la reproducción y el hashing.
- **ID-2 / ID-2a** — forma del artefacto (prefijo→AS, AS→jurisdicción gruesa),
  direccionado por contenido mediante `H`; búsquedas totales, `unknown` es de primera
  clase.
- **ID-3 / ID-3a** — solo entradas públicas fijadas (BGP de RouteViews + RIPE RIS,
  cinco ficheros de delegación de RIR); resolución de origen multi-ventaja, MOAS
  conservado como un conjunto.
- **ID-4 / ID-4a–d** — determinismo: la época UTC fija la temporización del volcado,
  orden total fijo, desempate especificado, sin entradas flotantes, contenedor
  canónico + un vector de prueba del mapa.
- **ID-5 / ID-5a / ID-5b** — la concordancia es la igualdad de hash; la
  reconstrucción a partir de las entradas es el árbitro libre de autoridad; rechaza
  lo irreproducible.
- **ID-6 / ID-7 / ID-7a–c** — registro de transparencia de Merkle, de solo-anexado y
  sin permisos, de `(epoch, H, manifest-hash)`; equivocación atrapada por raíces
  difundidas + pruebas de consistencia; múltiples registros, ninguno canónico; el
  registro guarda compromisos, no el mapa.
- **ID-8 / ID-8a / ID-8b** — el arranque es TOFU declarado; el daño de un mal primer
  mapa está acotado (el contenido sigue con umbral, es detectable, la reproducción no
  puede falsificarse); detectar, no afirmar que se previene.
- **ID-9 / ID-9a / ID-10** — refresco y gossip de `(epoch, H)` y raíces bajo GR-8;
  divergencia mostrada vía PS-9; gossip de anomalías obligatorio para las tres firmas
  de ataque.
- **ID-11 / ID-11a** — costura de fusión: la misma ancla de confianza
  (reproducibilidad) que la gobernanza de versiones, pero conjuntos de
  firmantes/anexadores **separados**; herramientas compartidas sí, autoridad
  compartida no.
- **ID-12 / ID-12a** — el mapa distribuye una estimación de error medida y
  reproducible que alimenta la perilla `infer_error` del simulador y la confianza de
  la Parte 3; el caso de error cero es el mejor caso, nunca el esperado.

ID-1, ID-5a e ID-8a son los tres portantes: ninguna autoridad, la reproducción es el
árbitro, y un mal mapa no puede bajar el umbral del contenido. Rompe cualquiera de
ellos — encuentra un paso que necesite una parte confiable, un mapa que no pueda
reconstruirse a partir de sus entradas, o una forma en que un mal mapa alcance el
contenido y no meramente la vinculación — y habrás roto esta parte. Esa es la
invitación. El barrido de `infer_error` de `poc/network_sim.py` es el hombre de paja
ejecutable detrás del §11; ataca el modelo, luego este texto.
