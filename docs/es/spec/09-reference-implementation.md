# Especificación de ScrambNet — Parte 9: Requisitos de la implementación de referencia
> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../../en/spec/09-reference-implementation.md)).

**Estado: BORRADOR (DRAFT).** Esta parte enuncia, como requisitos numerados (`RI-n`), lo que un
nodo real DEBE (MUST) hacer y que la prueba de concepto omite deliberadamente —cada regla ligada
a la amenaza que responde y, donde corresponde, al invariante (I-1…I-4) que
protege. El juguete de `poc/` es una *especificación ejecutable*, no un nodo: lo
dice en sus propias primeras líneas ("NOT PRODUCTION CODE. No constant-time
arithmetic, no networking, no onion layer"). Todo lo que hay aquí es la distancia
entre ese juguete y algo que puedas apuntar a una red hostil. Cada número
es un hombre de paja para ser atacado por número de requisito; la invitación más afilada está en
§1, y §11 nombra lo que sigue abierto.

## 1. La tensión central: un umbral teórico-informativo es solo tan incondicional como el código que lo computa

ScrambNet vende un umbral de contenido **incondicional** (I-2, demostrado en la Parte 7): por debajo de
`k` partes, el texto cifrado es *estadísticamente independiente* del secreto, frente a
computación no acotada y cualquier computador cuántico. Esa prueba es sobre **valores** —
los bytes de parte que un adversario posee no llevan ninguna información sobre el secreto. No dice
nada sobre **cómo una máquina real computa esos bytes**, y ahí es donde el
umbral puede perderse sin que un solo teorema sea erróneo.

Una multiplicación GF(2⁸) por búsqueda en tabla (las tablas `_EXP`/`_LOG` de la PoC,
`poc/dispersal.py`) indexa memoria en una dirección que **depende de un byte de parte
secreto**. En hardware real, el estado de la caché hace que ese acceso sea observable en tiempo para
un atacante corresidente. La búsqueda por tanto filtra, a través de un canal lateral de temporización,
los mismísimos bytes que el umbral está construido para ocultar. El umbral sería entonces *incondicional
en teoría y recuperable en la práctica*.

Esta es la frase más importante de esta parte, enunciada como principio:

> **Un canal lateral de temporización o de revelación de memoria que revele bytes de parte secretos,
> coeficientes o la clave de contenido no es una ruptura "computacional" que a I-2 le
> esté permitido tener. Es una ruptura de I-2 mismo.** La Parte 7 licencia exactamente una
> suposición computacional —el AEAD extremo a extremo *por encima* de `k` (SP-1a)— y
> nada más. Un canal lateral que revela bytes secretos sub-`k` no le cuesta al
> adversario "trabajo bajo una suposición"; le entrega los bytes. La prueba
> de SA-1/SA-2 asume que el adversario ve **solo** los `k−1` valores de parte y
> los parámetros públicos. Un canal lateral añade una vista que la prueba nunca concedió, y
> la prueba no la cubre.

Dos consecuencias, que el resto de esta parte vuelve normativas:

- La **ruta de cómputo** del umbral —toda operación GF(2⁸) sobre datos dependientes del secreto
  en la división de Shamir, la reconstrucción y la interpolación de Lagrange— DEBE (MUST) ser
  de tiempo constante (RI-1). Esto no es endurecimiento; es la condición bajo la cual
  SA-1/SA-2 describen el sistema real, exactamente como SA-3 (aleatoriedad de los coeficientes) lo es.
- El **residuo en memoria** del umbral —partes, coeficientes, claves derivadas— NO DEBE (MUST NOT)
  sobrevivir para ser leído de un volcado de heap, un archivo de swap o un volcado de núcleo (core dump) (RI-9). Un
  umbral que es teórico-informativo en el cable pero recuperable de `/proc` no es
  un umbral.

La PoC es honesta en que falla en ambos: son búsquedas en tabla en Python puro sin
puesta a cero, correctas pero con fugas, y lo dice. Esta parte es la lista que un nodo real
debe satisfacer en su lugar. Donde la PoC *ya* impone una regla (se niega a
dispersar texto en claro que no ha pasado por el AEAD —`send()` sella antes de
dividir), esa es la barra, no un detalle fino, y RI-6 la eleva a un DEBE (MUST).

**Alcance.** Esta parte restringe la *implementación* de construcciones fijadas
en otro lugar; no introduce ningún formato de cable nuevo y no cambia ningún byte en el cable (eso
sería un cambio de I-1/I-4 y pertenece a las Partes 1–6). NO DEBE (MUST NOT) leerse para
relajar ningún requisito que referencia; donde parezca hacerlo, la parte referenciada
gana y la contradicción es un defecto a reportar.

## 2. Aritmética de campo de tiempo constante (la ruta de cómputo del umbral)

- **RI-1 (GF(2⁸) de tiempo constante, protege I-2).** Toda aritmética GF(2⁸) aplicada a
  datos dependientes del secreto —`split` de Shamir (evaluación polinómica sobre coeficientes
  secretos y el término constante secreto), `reconstruct`/interpolación de Lagrange
  (incluida la **inversión** de campo `gf_inv` en el denominador de la
  base), y cualquier multiplicación cuyo operando sea un byte de parte, un coeficiente o
  un byte de secreto reconstruido— DEBE (MUST) computarse **sin ramas
  dependientes del secreto y sin acceso a direcciones de memoria dependiente del secreto**. Concretamente, una
  implementación NO DEBE (MUST NOT) indexar una tabla (`_EXP`/`_LOG`, una S-box o cualquier arreglo)
  en un desplazamiento derivado de un valor secreto. Las técnicas conformes son una
  multiplicación bitsliced o de campo-torre de tiempo constante, una reducción por multiplicación-sin-acarreo
  (`CLMUL`), o un campo provisto por una biblioteca que *documente*
  comportamiento de tiempo constante para estas operaciones. Amenaza: un adversario corresidente o
  de temporización remota recupera bytes de parte secretos de la caché o
  de la temporización de ramas —una **ruptura directa de I-2** (ver §1), no computacional.
  Esto aplica simétricamente a **split y reconstruct**: un extremo que
  reconstruye filtra el secreto que acaba de recuperar exactamente como un divisor filtra el
  que está dispersando.
- **RI-1a (la inversión y la división no están exentas).** El inverso del denominador de Lagrange
  (`gf_inv` en `poc/dispersal.py`, calculado ahí como
  `_EXP[255 − _LOG[a]]`) opera sobre un valor derivado del conjunto de partes secretas
  y DEBE (MUST) ser de tiempo constante; una exponenciación dependiente de datos o un inverso por
  búsqueda en tabla no es conforme. Una implementación DEBERÍA (SHOULD) preferir una
  interpolación libre de inversión (p. ej., agrupando por lotes los denominadores e invirtiendo una
  sola vez vía Fermat `a^{254}` por una cadena de adición fija, o el truco de Montgomery) de modo que no
  quede ninguna división dependiente del secreto. Los puntos de evaluación `x_1…x_n` son **públicos**
  (Parte 7 §2), así que la aritmética sobre *ellos solos* no necesita ser de tiempo constante; en el
  momento en que un punto público se multiplica en un secreto, el producto es secreto.
- **RI-1b (los vectores no certifican la temporización).** Pasar los vectores de prueba de GF de roadmap 3.2
  demuestra que una multiplicación es *correcta*, no que es *de tiempo constante*: las
  tablas con fuga de la PoC pasan esos mismos vectores. Una implementación NO DEBE (MUST NOT) tratar
  la conformidad de vectores como evidencia de cumplimiento de RI-1. El comportamiento de tiempo constante
  DEBERÍA (SHOULD) verificarse con una herramienta de análisis de temporización o estadística (p. ej.,
  pruebas de fuga al estilo dudect) y, donde la plataforma lo permita, deshabilitando transformaciones
  del compilador que reintroduzcan ramas dependientes del secreto (RI-9b).
- **RI-1c (toda la vida del secreto es de tiempo constante, no solo sus operaciones de campo,
  protege I-2).** La disciplina de tiempo constante se define por el **flujo de datos, no por
  nombrar las operaciones de GF**: cualquier valor contaminado por un byte de parte, un coeficiente o
  un byte de secreto reconstruido hereda la obligación de RI-1 hasta que se le pone a cero
  (RI-9), y esa obligación llega *más allá* de la capa de campo. En particular, el
  prefijo de longitud del secreto reconstruido (SP-8) DEBE (MUST) parsearse, y el texto en claro recuperado
  copiarse, segmentarse y validarse, **sin una rama dependiente del secreto y
  sin un acceso a memoria dependiente de la longitud del secreto**; `unpad` NO DEBE (MUST NOT) ramificar sobre
  la longitud decodificada de una manera que un observador pueda cronometrar, y ninguna comparación,
  verificación de límites o movimiento de búfer sobre un secreto puede ser dependiente de datos. Amenaza: el propio
  principio de §1 —"un extremo que reconstruye filtra el secreto que acaba de recuperar
  exactamente como un divisor filtra el que está dispersando"— solo se impone si el
  manejo *completo* del secreto recuperado es de tiempo constante, no meramente su
  aritmética de GF. Un nodo que usa un campo de tiempo constante verificado (RI-1) y un AEAD
  de tiempo constante auditado (RI-8) pero luego ramifica sobre una longitud recuperada satisface
  cada otro DEBE (MUST) mientras filtra la estructura del secreto recuperado por temporización, lo cual
  es una ruptura directa de I-2 por el mismo argumento que RI-1.

## 3. Disciplina del CSPRNG (el umbral es exactamente tan fuerte como su aleatoriedad)

El umbral no es más fuerte que la aleatoriedad de los coeficientes de Shamir: la Parte 7
SA-3 es el "componente de máxima garantía" de toda la especificación, y
`test_properties.test_coefficient_reuse_breaks_the_floor` muestra que la reutilización filtra el
secreto con certeza. La misma disciplina gobierna todo otro secreto que el nodo
extraiga.

- **RI-2 (DRBG criptográfico desde el SO, protege I-2 vía SA-3).** Toda la aleatoriedad
  secreta —coeficientes de Shamir (SA-3), el efímero de circuito por paquete `x`
  de CH-3, `msg_nonce`/contadores de mensaje donde no sean deterministas, la generación de
  `kpair`, y cualquier sal de `box_id`— DEBE (MUST) producirse por un DRBG criptográficamente
  seguro sembrado desde el CSPRNG del sistema operativo (`getrandom`/`getentropy`,
  `/dev/urandom` después de que el pool se inicialice, o una fuente equivalente que bloquee-hasta-
  sembrada). Una implementación NO DEBE (MUST NOT) usar un PRNG no criptográfico
  (un LCG, Mersenne Twister, `rand()`, un hash-de-contador, o un flujo reutilizado como
  "aleatorio") para ningún valor de esta lista.
- **RI-2a (seguridad ante fork y clone —la catástrofe clásica).** Un proceso que hace
  `fork()`, se restaura desde un checkpoint, se migra, o se clona como imagen de VM o
  de contenedor NO DEBE (MUST NOT) reutilizar un estado del DRBG que produjo salida antes de la división. La
  implementación DEBE (MUST) resembrar desde el SO en fork/restauración (p. ej., una disciplina de
  `pthread_atfork`/`MADV_WIPEONFORK`, o una extracción del SO por llamada) de modo que no haya
  dos procesos que emitan jamás el mismo flujo de coeficientes o el mismo efímero `x`.
  Amenaza: dos clones idénticos de VM dividen mensajes *diferentes* bajo los **mismos
  coeficientes**, y por SA-3 el par de conjuntos de partes queda correlacionado con ambos
  secretos —la catástrofe de aleatoriedad de manual, y una ruptura directa de I-2. Esto se
  señala específicamente porque es invisible para cualquier prueba de un solo proceso.
- **RI-2b (verificaciones de salud y arranque).** Antes de emitir el primer valor secreto,
  un nodo DEBE (MUST) confirmar que la fuente de entropía del SO está sembrada (NO DEBE (MUST NOT) recurrir a una
  fuente de baja entropía si el pool no está listo) y DEBERÍA (SHOULD) ejecutar un
  autodiagnóstico de arranque sobre el DRBG. Un nodo DEBERÍA (SHOULD) realizar una
  prueba continua de repetición/salida atascada sobre la entropía cruda donde tenga
  acceso a ella, y DEBE (MUST) fallar cerrado —negarse a dividir o a construir un paquete— en
  lugar de proceder con un generador sospechoso. Un generador que no puede verificarse
  se trata como roto.
- **RI-2c (sin coeficientes inyectables en producción —pero los vectores de conformidad aún
  se ejecutan).** El parámetro `split(..., coeffs=...)` de la PoC existe solo para que los vectores puedan ser
  deterministas y la ruptura por reutilización se demuestre. Un artefacto de producción NO DEBE (MUST NOT)
  exponer ninguna ruta —flag, config, variable de entorno o símbolo— que permita a un llamador suministrar,
  registrar o fijar coeficientes de Shamir o el efímero `x`; tal ruta es un
  foot-gun de SA-3. La conciliación con los vectores de conformidad de roadmap 3.2 (RI-10),
  que requieren coeficientes inyectados deterministas para reproducirse, es una **compuerta de prueba
  en tiempo de compilación**: la ruta de inyección PUEDE (MAY) existir *solo* detrás de una compuerta que esté
  **ausente de cualquier artefacto de producción** e inalcanzable en tiempo de ejecución en producción. Los vectores
  se cotejan contra una compilación de prueba que habilita la compuerta; la compilación de producción DEBE (MUST)
  ser idéntica a ella salvo por la ausencia del código tras la compuerta, y esa equivalencia
  DEBERÍA (SHOULD) ser verificada por la compilación (p. ej., un diff reproducible de las dos). "Compilado
  fuera, no meramente desaconsejado" significa exactamente esto: presente para el binario de prueba,
  físicamente ausente del que se entrega —nunca un conmutador en tiempo de ejecución.

## 4. Estado de nonce y rotación de clave a través de reinicios

Dos secretos diferentes nunca deben reutilizarse a través de un reinicio: el nonce del AEAD/etiqueta
(SP-7b) y la época estática del `onion` del relé (CH-5). Un reinicio es el momento en que un nodo
está más tentado a "empezar de nuevo" y reutilizar un valor que ya usó.

- **RI-3 (la marca de nivel máximo monótona del nonce sobrevive a los reinicios, protege SP-7b y
  SP-1a).** Por `kpair`, el `msg_nonce` del remitente (un contador de mensajes estrictamente
  creciente, SP-7b) DEBE (MUST) persistirse y NO DEBE (MUST NOT) retroceder a través de un reinicio,
  caída o cambio de reloj. La implementación DEBE (MUST) hacer `fsync` (o la barrera durable
  equivalente de la plataforma) de la marca de nivel máximo **a almacenamiento estable antes de que el
  nonce que cubre se use en el cable**, de modo que una caída entre el uso y la persistencia
  solo pueda *saltar* nonces, nunca repetirlos. Un nodo NO DEBE (MUST NOT) reutilizar ni decrementar un
  `msg_nonce` bajo un mismo `kpair`. Amenaza: un `msg_nonce` reutilizado es **doblemente fatal**
  (SP-7b) —colisiona las etiquetas de SP-7 (haciendo un conjunto de partes enlazable a través de drops
  coludidos) **y**, porque `msg_nonce` es el nonce de ChaCha20-Poly1305 (SP-1a),
  destruye la confidencialidad del AEAD como un bloc de un solo uso usado dos veces. Hacer retroceder el
  contador tras un respaldo restaurado es el fallo realista, y es una ruptura de confidencialidad,
  no un glitch.
- **RI-3a (reserva por adelantado para acotar el coste del fsync).** Una implementación PUEDE (MAY) persistir la
  marca de nivel máximo en bloques (reservar `B` nonces con una escritura durable, repartirlos
  desde memoria, persistir de nuevo antes de que el bloque se agote) para evitar un fsync
  por mensaje. Una caída entonces desperdicia a lo sumo la cola no usada de un bloque —aceptable,
  porque el espacio del contador es grande y saltar es seguro mientras repetir es fatal.
  NO DEBE (MUST NOT), bajo ninguna ruta de recuperación de caídas, repartir un nonce en o por debajo de la última
  marca persistida de forma durable.
- **RI-3b (una restauración no es un reinicio —detectar el retroceso o retirar la clave, protege
  SP-7b/SP-1a).** RI-3/RI-3a defienden contra una *caída* (la marca persistida solo avanza
  hacia adelante); **no** defienden contra un snapshot de VM, un snapshot de sistema de
  archivos, o una **restauración** de respaldo que rebobine la propia marca persistida —
  precisamente el "hacer retroceder el contador tras un respaldo restaurado" que RI-3 nombra como
  el fallo realista. Un nodo NO DEBE (MUST NOT) asumir que su almacén de nonce persistido es
  monótono a través de tal restauración. DEBE (MUST) por tanto o bien (a) vincular la
  marca de nivel máximo a una **sal** de nonce por arranque/por restauración (o un contador de
  generación monótono) persistido en la *misma escritura durable* que la reserva, de modo que
  un almacén rebobinado sea detectable, y al detectarlo **retirar el `kpair`** —derivar una
  clave de contenido/etiqueta fresca, tratando una sal reutilizada bajo un contador rebobinado como
  compromiso— o bien (b) negarse a emitir bajo el `kpair` afectado ante cualquier signo de una
  restauración (el reloj del sistema moviéndose hacia atrás, o el contador de generación persistido
  decreciendo) hasta que un `kpair` fresco se negocie fuera de banda (Parte 6). La reserva por adelantado
  (RI-3a) DEBE (MUST) llevar el contador de generación en la escritura durable de la reserva, de modo que una
  restauración no pueda reproducir un bloque reservado entero sin ser detectada. Amenaza: sin esto, una
  restauración de snapshot reemite un bloque entero de valores de `msg_nonce` ya usados —el
  bloc de un solo uso usado dos veces doblemente fatal de RI-3, en una ruta que la guarda solo-ante-caídas de RI-3a no puede ver.
- **RI-4 (estado de la época estática del onion y retirada segura, protege CH-5/CH-6).** Un
  relé DEBE (MUST) persistir en qué época estática del `onion` está (la clave privada activa,
  su `created`/`expiry`, y la ventana de gracia en vuelo) de modo que un reinicio no
  vuelva a publicar silenciosamente una clave expirada, resucite una retirada, o acuñe un segundo
  estático "fresco" dentro de la misma época declarada. En la rotación (≤7 días, CH-5) el
  relé DEBE (MUST), una vez pasada la gracia en vuelo, **poner a cero la mitad privada del
  estático retirado** (RI-9) y NO DEBE (MUST NOT) retenerla; un relé que conserva estáticos viejos
  agranda su propia ventana de exposición de enlazabilidad de CH-6 y no es conforme.
  Los clientes siguen vinculados por GR-4/CH-5 a rechazar cualquier registro cuyo `expiry` exceda
  `created + 7 days` (GR-2 clave 6), de modo que un nodo que olvida su época no puede extender
  la ventana republicando. Amenaza: un reinicio que hace retroceder el estático a una
  ventana que el cliente ya vio, o que falla en destruir un estático retirado,
  reabre exactamente la exposición de enlazabilidad de CH-5a que el techo de rotación existe para acotar.

## 5. Persistencia de la caché de repetición (replay)

ScrambNet rechaza las repeticiones (replays) en dos capas, y ambas tienen estado: la capa de circuito
descarta un `gamma` visto por época de clave (SP-5), y la capa de almacenamiento descarta un redepósito
de un `(box_id, slot)` ya almacenado (SP-7b, RZ-7). Un reinicio que olvida este
estado reabre una ventana de replay.

- **RI-5 (el estado de replay sobrevive a los reinicios, acotado a la época, protege SP-5 /
  SP-7b).** Un relé DEBE (MUST) persistir, o reconstruir de forma segura y completa, su caché de
  replay de Sphinx de valores `gamma` vistos **para la época de clave actual**, y un drop
  DEBE (MUST) persistir su conjunto de depósitos `(box_id, slot)` almacenados, de modo que un reinicio o
  una caída no acepte un paquete o un depósito que ya ha visto dentro de la época
  viva. Amenaza: un relé que reinicia con una caché de replay vacía readmitirá
  cada paquete que un adversario capturó y reinyecta dentro de la época —una ventana de
  replay reabierta, que en la capa de drop también puede multiplicar o desplazar correo honesto
  contra el tope por buzón de RZ-7.
- **RI-5a (la caché está acotada —por dos ventanas de retención *diferentes*, no "la época").** Las
  dos cachés de replay están cada una acotada en memoria, pero por ventanas **distintas** que una
  implementación NO DEBE (MUST NOT) confundir:
    - la caché de `gamma` de Sphinx está acotada por la **época de clave estática del onion** (CH-5,
      ≤7 días) —un `gamma` solo es repetible mientras la clave que lo cifró esté viva;
    - el conjunto de deduplicación de depósitos `(box_id, slot)` está acotado por la **expiración de slot**
      (RZ-7, 7 días), **no** por la rotación de `box_id` de 1 día (RZ-10). El id de box
      rota a diario para el *direccionamiento*, pero un slot depositado se *almacena* hasta por 7
      días (más la gracia de frontera de RZ-14), así que un redepósito es descartable mientras
      el slot con el que colisionaría aún pueda almacenarse —hasta ~7 épocas de box. Dimensionar
      este conjunto a un día lo infradimensiona ~7×.
  Una implementación DEBE (MUST) descartar el estado de cada caché una vez que su propia ventana ha pasado
  (la caché de `gamma` al fin de la época de clave, el conjunto de depósitos a la expiración de slot), lo que
  acota la memoria a aproximadamente el volumen de paquetes de la época de clave y el volumen de depósitos
  de 7 días respectivamente. PUEDE (MAY) acotar la memoria aún más con una estructura de conteo (p. ej., un
  filtro Bloom/cuckoo dimensionado) **solo si** está afinada de modo que los falsos positivos se mantengan
  por debajo de una tasa operativamente despreciable; un falso positivo descarta un paquete honesto
  (una DoS autoinfligida), un falso negativo admite un replay (un fallo de seguridad), así que
  la estructura DEBE (MUST) dimensionarse para hacer lo último imposible dentro de su ventana de retención
  y lo primero raro. Un nodo que no puede persistir una caché DEBE (MUST) fallar cerrado
  para una ventana que no puede cubrir (tratar el lapso olvidado como repetible y, para la
  caché de `gamma`, rotar la época de clave) en lugar de aceptar replays silenciosamente.
- **RI-5b (la reconstrucción debe ser completa, o tratarse como una rotación —y una restauración no
  es una reconstrucción).** Una implementación que reconstruye el estado de replay tras una caída
  (en lugar de persistirlo continuamente) DEBE (MUST) o bien reconstruirlo completamente
  para la ventana viva o tratar el hueco como el comienzo de una nueva época de clave (nuevas claves,
  de modo que los valores `gamma` viejos ya no sean aceptables). Una reconstrucción parcial que deja
  parte de la ventana desprotegida no es conforme. Además, una **restauración** de VM/sistema de
  archivos que rebobina la caché a un estado *anterior, de apariencia completa* no es
  una caída y la verificación de completitud de RI-5b no puede detectarla: un relé restaurado vuelve
  con una caché de *antes* de los paquetes que un adversario capturó, y los readmite. Un
  nodo DEBE (MUST) tratar cualquier signo de una restauración (el mismo retroceso de reloj o
  decremento de contador de generación que RI-3b) como una **rotación de época de clave** obligatoria, de modo
  que los valores `gamma` previos a la restauración ya no sean aceptables independientemente de lo que
  contenga la caché rebobinada.

## 6. API resistente al mal uso (hacer imposible lo inseguro)

I-1 y la disciplina `[soundness]` exigen que la API haga la operación insegura
*irrepresentable*, no meramente documentada como imprudente. El ordenamiento de
SP-1 (cifrar **luego** dividir) y la regla de fallo cerrado de SP-7a son los dos lugares
donde una API más fácilmente se invierte.

- **RI-6 (la API DEBE (MUST) rechazar texto-en-claro-sin-AEAD, protege SP-1/SP-1a).** El
  punto de entrada de dispersión DEBE (MUST) rechazar cualquier entrada que no haya pasado ya por el
  AEAD extremo a extremo (SP-1a): dispersa **solo texto cifrado**, nunca texto en claro.
  NO DEBE (MUST NOT) haber una ruta pública de "divide estos bytes crudos" que eluda el
  ordenamiento cifrar-luego-dividir de SP-1 —es decir, ninguna forma de alcanzar `split()` sin
  el sello del AEAD por delante. La PoC ya cumple esta barra: `send()` llama
  `e2e.seal` antes de `disperse`, y `dispersal.py` está documentado para "never touch
  plaintext." Un nodo real DEBE (MUST) mantener esa puerta cerrada a nivel de tipo, no por
  convención. Amenaza: dividir texto en claro directamente destruye el *cinturón
  computacional* (nivel 2 de la Parte 7) —las partes entonces reconstruyen directamente a texto en claro para
  cualquier adversario `≥k`, sin AEAD detrás de ellas— e invierte la composición sobre la que
  todo el diseño descansa.
- **RI-6a (separar por tipo el texto cifrado del texto en claro).** Una implementación DEBERÍA (SHOULD)
  representar "texto en claro" y "texto cifrado extremo a extremo" como tipos distintos,
  no intercambiables, de modo que el ordenamiento de SP-1 no pueda invertirse pasando el
  búfer equivocado y una llamada de "divide bytes crudos" sea un error en tiempo de compilación en lugar de una
  verificación en tiempo de ejecución. Donde el lenguaje no pueda imponer esto, el nodo DEBE (MUST) interponer una
  guarda en tiempo de ejecución que esté activada por defecto y no pueda deshabilitarse por configuración.
- **RI-6b (los puntos de entrada de campo crudo DEBEN (MUST) ser privados del módulo).** La separación por tipo
  (RI-6a) no basta por sí sola: el `split`/`reconstruct` crudo y cualquier punto de entrada
  de campo directo DEBE (MUST) ser privado del módulo (no exportado), de modo que los *únicos* símbolos de
  dispersión públicos sean el que toma el tipo de texto-cifrado-AEAD (RI-6) y el
  que devuelve un resultado de apertura autenticada (RI-7). Un símbolo público `split(raw_bytes)`
  o `reconstruct(...)` es en sí mismo el defecto, independientemente de lo que un llamador
  le pase —en un lenguaje donde `bytes` es `bytes`, un split-crudo exportado permite a un
  llamador de nivel inferior eludir la compuerta del AEAD mientras pasa el chequeo de tipos limpiamente. La PoC
  expone estos a nivel de módulo *porque es una especificación ejecutable*; un nodo real
  NO DEBE (MUST NOT).
- **RI-7 (la reconstrucción DEBE (MUST) fallar cerrado, en tiempo constante, protege SP-7a).** La
  etiqueta del AEAD es el **único** árbitro de integridad (SP-7a): la reconstrucción de Shamir no tiene
  ninguna propia, así que un byte de parte invertido o un `(k,n)` sobre el que se mintió produce un
  candidato coherente-pero-erróneo que solo el AEAD rechaza. La API de reconstrucción
  DEBE (MUST) devolver un mensaje **solo** después de que el AEAD extremo a extremo verifique, y DEBE (MUST)
  descartar —nunca exponer, registrar ni actuar sobre— cualquier candidato cuya etiqueta falle. NO DEBE
  (MUST NOT) exponer un resultado de "reconstrucción no autenticada" al código de la aplicación. **El
  descarte de fallo cerrado DEBE (MUST) ser también de tiempo constante respecto a *por qué* falló:**
  la ruta reconstruir-luego-abrir DEBE (MUST) tomar un tiempo indistinguible y no emitir ninguna respuesta
  distinguible (CH-9/I-4) tanto si la etiqueta del AEAD verificó, como si el byte `(k,n)`
  fue mentido (RI-7a), o los bytes de parte fueron corrompidos —un adversario que
  puede alimentar candidatos de reconstrucción (el residuo de drop-hostil de SP-7a, o una coalición `≥k`
  reproduciendo conjuntos de partes) NO DEBE (MUST NOT) aprender cuál, por temporización o por respuesta,
  de lo contrario la ruta de rechazo se vuelve un distinguidor al estilo padding-oracle aunque la
  *comparación* de etiqueta (RI-8) sea de tiempo constante. La PoC fija el comportamiento de fallo cerrado
  (`receive()` descarta ante el `ValueError` de `e2e.open_`,
  `test_tampered_share_fails_closed`); un nodo real DEBE (MUST) no añadir una ruta alrededor de él,
  ni una puerta lateral de temporización a través de él. Amenaza: entregar hacia arriba una reconstrucción
  no autenticada convierte el residuo de denegación de servicio aceptado de SP-7a en la
  entrega de basura elegida por el atacante; cronometrar el rechazo lo convierte en un oráculo.
- **RI-7a (parsear el byte `params` defensivamente, no confiar en él).** El byte `(k,n)`
  está controlado por el atacante en una parte hostil (SP-7a) y bloqueado en el orden de nibbles
  por vectores (SP-7a / roadmap 3.2). Una implementación DEBE (MUST) validarlo contra el
  orden bloqueado por vectores y contra `1 ≤ k ≤ n ≤ 15` (como hace `_check_params`) antes del
  uso, y DEBE (MUST) tratar una reconstrucción bajo un `(k,n)` mentido como un
  descarte de fallo cerrado ordinario (RI-7), nunca como una razón para asignar memoria no acotada o indexar
  fuera de límites.

## 7. El AEAD y la comparación de etiqueta (el cinturón también debe ser de tiempo constante)

El cinturón computacional (nivel 2, Parte 7 §5) es solo tan sólido como su implementación.
El AEAD de la PoC es correcto frente a RFC 8439 pero explícitamente **no** es de tiempo constante
("it is correct … but leaks through timing, so a real node MUST use a vetted
constant-time library").

- **RI-8 (AEAD de tiempo constante y comparación de etiqueta, protege SP-1a / SP-7).** Un nodo
  DEBE (MUST) usar una implementación de ChaCha20-Poly1305 cuya ruta de datos y cuya
  **comparación de etiqueta de autenticación** sean de tiempo constante, y DEBE (MUST) comparar la etiqueta de
  parte de SP-7 y la etiqueta del AEAD de SP-7a con una primitiva de igualdad de tiempo constante (sin
  `memcmp` de salida temprana, sin rama dependiente de datos sobre bytes de etiqueta). Amenaza: una
  verificación de etiqueta no de tiempo constante es un oráculo de falsificación clásico —la temporización byte a byte sobre
  la comparación permite a un adversario falsificar una etiqueta válida— lo que ataca el cinturón
  (SP-1a) y la etiqueta de reconocimiento de parte (SP-7) directamente. La aritmética de Poly1305 y X25519
  DEBE (MUST) ser igualmente de tiempo constante (RI-11); una implementación de tiempo variable
  de cualquiera de ellas filtra material de clave por temporización.

## 8. La capa de cebolla (onion) que el juguete omite

La PoC tiene "no onion layer": `dispersal.py` opera solo sobre la parte de la carga útil
`delta`, y la cabecera Sphinx (`alpha`/`beta`/`gamma`) y su criptografía por salto
existen solo como la especificación de la Parte 1 §5. Un nodo real DEBE (MUST) implementar
esa capa, y su criptografía está en alcance aquí porque lleva material secreto
(los secretos de salto y el efímero de cliente) bajo la misma amenaza de canal lateral que el umbral.

- **RI-10 (implementar la derivación por salto de CH-2, protege I-1/I-4).** Un nodo DEBE (MUST)
  implementar el handshake de circuito Sphinx de la Parte 1 §5 exactamente: por salto, derivar el
  secreto compartido `s_i = X25519(alpha_i, onion_i)` a partir del elemento de grupo cegado
  y el estático del relé (CH-2), y derivar la clave de flujo de la información de enrutamiento, la clave
  del MAC `gamma` y la clave del AEAD `delta` a partir de `s_i` por HKDF-BLAKE2s bajo las etiquetas
  fijas `sphinx-rho`, `sphinx-mu`, `sphinx-delta` (CH-2; bytes exactos de etiqueta y
  encadenamiento bloqueados por vectores bajo roadmap 3.2). DEBE (MUST) realizar el cegado de Sphinx
  (re-aleatorizar `alpha` por salto) e imponer la disciplina de replay de SP-5.
  **No** hay **ninguna transcripción de handshake separada** (CH-1); un nodo que emite o
  espera cualquier mensaje Noise/handshake en un circuito no es conforme (CH-1).
  *Señal:* los vectores de prueba entre implementaciones para esta derivación son roadmap
  3.2 y DEBEN (MUST) cotejarse una vez publicados; hasta entonces, dos implementaciones no están
  aún probadas para interoperar en esta capa (I-1), y esto se enuncia abiertamente en lugar de
  asumirse.
- **RI-11 (X25519 de tiempo constante y la disciplina de efímero sin clave, protege
  CH-3/CH-6/I-2).** La multiplicación escalar X25519 en cada salto DEBE (MUST) ser
  de tiempo constante (una implementación de escalera de Montgomery sin rama dependiente del secreto
  ni acceso a memoria); un X25519 de tiempo variable filtra el escalar del salto y por tanto
  el secreto del salto. El escalar efímero de cliente por paquete `x` detrás de `alpha_0`
  (CH-3) DEBE (MUST) extraerse de nuevo del CSPRNG (RI-2) por paquete, NO DEBE (MUST NOT)
  reutilizarse jamás entre paquetes, y DEBE (MUST) ponerse a cero inmediatamente después de que el paquete se
  construya (RI-9) —su destrucción es lo que hace real el forward secrecy con granularidad de época
  de CH-6 (un `x` retenido permite a un decomiso posterior del estático de un relé recomputar el secreto de salto
  que el diseño promete que ha desaparecido). Un relé DEBE (MUST) igualmente mantener su `onion`
  estático bajo el manejo de clave de RI-2 y la rotación/retirada de RI-4, y computar con
  él en tiempo constante.
- **RI-11a (rechazar el secreto compartido degenerado, de la manera correcta para X25519).** X25519
  deliberadamente no expone ninguna prueba barata de on-curve/orden (RFC 7748), así que "validar el
  punto `alpha`" no es la verificación construible; la requerida, construible, es: computar
  `s_i = X25519(alpha_i, onion_i)` y, **en tiempo constante, rechazar si el secreto compartido
  resultante es todo-ceros** (el resultado de orden-bajo / subgrupo-pequeño) *antes* de
  derivar cualquier clave de salto de él. Esto niega a un predecesor malicioso un salto forzado
  de orden pequeño o de clave conocida. Como cada byte en el cable es uniforme
  (SP-4/I-4), la verificación es sobre el *secreto computado*, no una bandera en claro, y un
  relé DEBE (MUST) procesar un `alpha` rechazado en tiempo y bytes **indistinguibles de
  un descarte-de-replay ordinario** (SP-5/CH-9/I-4) —sin respuesta distinguible, sin indicio de
  temporización. La regla completa de validación/codificación de punto está bloqueada por vectores bajo roadmap 3.2,
  pero el rechazo de salida-todo-ceros es normativo *aquí* de modo que el requisito sea
  construible sin esperar a ese archivo (I-1).

## 9. Puesta a cero de memoria, swap y seguridad ante fallos

Un umbral que es incondicional en el cable pero recuperable de un volcado de heap, un archivo de
swap o un volcado de núcleo (core dump) no es un umbral (§1). La revelación de memoria revela los mismísimos bytes
por debajo de `k` que I-2 protege, así que la puesta a cero es un requisito de I-2, no higiene.

- **RI-9 (mantener los secretos en almacenamiento que se pueda poner a cero y borrarlos tras el uso, protege
  I-2).** Las partes de Shamir, los coeficientes polinómicos, el secreto reconstruido, cada
  clave derivada (`content_key`, la clave de `tag` de SP-7, la clave de `box_id`, cada clave de salto Sphinx
  `s_i` y sus derivadas), el `kpair` precompartido, el efímero de cliente `x`
  (RI-11) y el `onion` estático del relé (RI-4) DEBEN (MUST) mantenerse en almacenamiento que el nodo pueda
  sobrescribir en el sitio y DEBEN (MUST) ponerse a cero tan pronto como ya no se necesiten. La
  obligación se enuncia como *elección de almacenamiento primero* porque una mera "puesta a cero" es
  **físicamente imposible** en algunos de los propios lenguajes objetivo de esta especificación: en CPython
  (el lenguaje de la PoC de referencia) un secreto en un objeto `bytes` inmutable puede estar
  internado, copiado por el asignador y liberado sin ninguna sobrescritura alcanzable, y
  un GC copiador/compactador (Go, Java, …) puede reubicar un secreto de modo que ningún borrado único
  alcance cada copia. Por tanto:
    - En un runtime que provee almacenamiento secreto **mutable, en el sitio y determinista**,
      el nodo DEBE (MUST) poner a cero con una primitiva que el compilador no pueda eliminar como una escritura
      muerta (`explicit_bzero`/`memset_s`/`SecureZeroMemory`/una barrera `volatile` o
      el `Zeroize` auditado del lenguaje) —un `memset` corriente sobre un búfer a liberar
      se optimiza y elimina de forma rutinaria.
    - Donde el lenguaje **no puede** garantizar eso (cadenas de bytes inmutables, un
      GC copiador/compactador, semántica de copia-por-valor), el nodo DEBE (MUST) mantener cada secreto
      en memoria **anclada/nativa/fuera-del-heap** que *pueda* poner a cero (la cláusula de memoria nativa de
      RI-9b es entonces un **DEBE (MUST)**, no un DEBERÍA (SHOULD)) y NO DEBE (MUST NOT) mantener el secreto en un
      objeto gestionado por el runtime (un `bytes`/`str`, un arreglo del heap del GC) en absoluto.
  El requisito es por tanto "usar almacenamiento que se pueda poner a cero, luego borrarlo" —satisfacible en
  todo lenguaje— en lugar de "borrar un objeto que el runtime no te dejará alcanzar."
  Amenaza: estos son exactamente los bytes secretos sub-`k` que el umbral oculta; dejarlos
  en heap liberado, un búfer reutilizado, una copia de GC reubicada o una estructura registrada permite
  que una lectura de memoria posterior los reconstruya, lo cual es una ruptura de I-2 por revelación de memoria.
- **RI-9a (mantener los secretos fuera del swap y los volcados de núcleo).** Los búferes secretos DEBERÍAN (SHOULD) estar
  anclados en RAM (`mlock`/`mlockall`/`VirtualLock`) de modo que nunca se paginen a un
  archivo de swap persistente, y el proceso DEBERÍA (SHOULD) deshabilitar los volcados de núcleo
  (`RLIMIT_CORE = 0` o el equivalente de la plataforma) o excluir las páginas secretas de
  ellos. Un nodo que no puede prevenir el intercambio (swapping) de páginas secretas DEBERÍA (SHOULD) usar un
  despliegue de swap cifrado y DEBE (MUST) documentar el residuo. Amenaza: un archivo de swap o
  un volcado de caída es una copia durable, residente en disco, de los bytes sub-`k` —el umbral,
  derramado a almacenamiento donde sobrevive mucho más que el proceso.
- **RI-9b (derrotar los riesgos del optimizador y del lenguaje).** Una implementación DEBE (MUST) asegurar
  que el compilador y el runtime del lenguaje no reintroduzcan las fugas que estas reglas
  prohíben: ninguna rama dependiente del secreto resucitada por la optimización (RI-1), ningún
  secreto copiado-y-olvidado de un contenedor que reasigna, un valor movido, un
  heap recolectado-de-basura o de GC copiador, interning de cadenas, o una excepción/traza de
  pila que capture un búfer secreto. En lenguajes de memoria gestionada donde un búfer
  puede ser copiado por el runtime, un nodo DEBERÍA (SHOULD) mantener los secretos en memoria anclada/nativa
  que pueda poner a cero de forma determinista, y NO DEBE (MUST NOT) confiar en el recolector de basura para
  borrarlos.
- **RI-12 (seguridad ante fallos y excepciones —sin artefacto parcial o enlazable, protege
  I-2/I-4).** Una caída, excepción o cancelación **a mitad de la división (mid-split)** NO DEBE (MUST NOT) emitir un
  conjunto de partes parcial, un subconjunto de partes en el cable, o cualquier artefacto que enlace
  las partes de un mensaje, y NO DEBE (MUST NOT) dejar estado secreto sin poner a cero. Una
  implementación DEBE (MUST) construir las `n` partes y comprometerse a la emisión como un paso de todo-o-
  nada respecto al fallo, poniendo a cero coeficientes y partes en cualquier ruta de error
  antes de desenrollar. Amenaza: un remitente que cae tras emitir algunas pero no
  todas las partes, o que registra una parte intermedia en una traza de pila, entrega a un
  observador un subconjunto correlacionado (socavando la no-enlazabilidad de SP-7 y, si
  revela `≥k` de un mensaje, el umbral) —y un desenrollado sin puesta a cero deja el
  secreto en memoria (RI-9). El manejo de fallos DEBE (MUST) fallar cerrado: ante cualquier error durante
  split, disperse o reconstruct, producir nada y borrar, en lugar de producir
  algo parcial.

## 10. Cómo estos requisitos se mapean a los invariantes y amenazas

| `RI` | Protege | Amenaza que niega (el ataque al nodo real) |
|---|---|---|
| RI-1 / 1a / 1b / 1c | I-2 | recuperación por temporización de caché/rama de bytes sub-`k`, incl. el manejo del secreto recuperado más allá de las operaciones de campo |
| RI-2 / 2a / 2b / 2c | I-2 (SA-3) | RNG débil/forkeado/clonable → coeficientes correlacionados |
| RI-3 / 3a / 3b | SP-7b, SP-1a | retroceso de nonce al reiniciar **o al restaurar snapshot/respaldo** → colisión de etiqueta + bloc de un solo uso usado dos veces |
| RI-4 | CH-5 / CH-6 | retroceso de época estática o estático retirado retenido |
| RI-5 / 5a / 5b | SP-5, SP-7b | estado de replay olvidado (o rebobinado por restauración) reabre la ventana de replay; las dos cachés tienen ventanas de retención diferentes |
| RI-6 / 6a / 6b | SP-1 / SP-1a | dividir-antes-de-cifrar destruye el cinturón computacional; un símbolo público de split-crudo elude la compuerta |
| RI-7 / 7a | SP-7a | reconstrucción no autenticada **o distinguible por temporización** entrega basura / se vuelve un oráculo |
| RI-8 | SP-1a, SP-7 | verificación de etiqueta no de tiempo constante → oráculo de falsificación |
| RI-10 | I-1, I-4 | la capa de cebolla no implementada, construida de forma interoperable |
| RI-11 / 11a | CH-3 / CH-6, I-2 | X25519 de tiempo variable o un efímero reutilizado/retenido |
| RI-9 / 9a / 9b | I-2 | revelación por heap/swap/coredump de los bytes sub-`k` |
| RI-12 | I-2, I-4 | artefacto parcial/enlazable o desenrollado de caída sin puesta a cero |

El hilo conductor: todo lo que toca un valor secreto sub-`k` (parte,
coeficiente, byte reconstruido, clave de contenido, secreto de salto, efímero de cliente) se
mantiene al propio estándar del umbral —computarlo en tiempo constante (RI-1/8/11),
generarlo desde un CSPRNG sólido y seguro ante fork (RI-2), no persistir ningún secreto reutilizable
a través de un reinicio (RI-3/4/5), nunca dejar que la API salte el AEAD (RI-6/7), y borrarlo
antes de que pueda leerse de vuelta (RI-9/12). Un revisor rompe esta parte encontrando una
ruta de nodo real en la que tal valor se computa en tiempo variable, se extrae de un flujo
reutilizado, se repite a través de un reinicio, se expone sin autenticar, o se deja
legible en memoria —y esa ruta es entonces una ruptura de I-2, no una mera brecha de endurecimiento.

## 11. Lo que esta parte **no** decide

- **Red, transporte y modelado de tráfico.** El transporte camaleón (Parte
  4), la estrategia de lote/mezcla y el jitter (SP-6/OP-5), y la temporización de emisión de partes
  (SP-9/OP-4) están fuera de alcance aquí; esta parte restringe la implementación *criptográfica*,
  no el planificador. El residuo de correlación de temporización entre
  partes sigue siendo OP-4, no abordado por ningún RI-n (SA-2 y esta parte son sobre
  valores, no tiempos de emisión).
- **Selección de ruta y disjunción.** Verificar que `n` rutas de parte no comparten
  un AS o una jurisdicción (OP-1, Parte 3) no es una cuestión de implementación-de-una-primitiva
  y no se requiere aquí; RI-7a solo protege contra *confiar* en un
  `(k,n)` mentido, no contra un conjunto de rutas no disjunto.
- **Sybil/eclipse y la capa de gossip.** La criptografía correcta de un nodo conforme no
  resiste por sí sola a un adversario con recursos que compra posición (OP-2, GR-20a); ese
  residuo vive en la Parte 2 y queda intacto por esta parte.
- **El dimensionamiento exacto de la estructura de replay y el mecanismo de detección de fork.** RI-5a
  acota la caché de replay a la época y prohíbe un filtro propenso a falsos negativos,
  pero la estructura de datos concreta, sus parámetros y el medio de persistencia son
  elecciones de implementación a fijar contra los vectores de roadmap 3.2 y el
  volumen de paquetes del despliegue, no fijadas aquí.
- **Vectores de prueba y conformidad.** Los vectores que certifican que dos implementaciones
  interoperan —las tablas de GF como normativas, la derivación por salto de Sphinx, la
  ruta cifrar→dividir→depositar→sondear→reconstruir→descifrar— son **roadmap 3.2** y
  se referencian (RI-1b, RI-7a, RI-10, RI-11a) pero no se reproducen aquí. RI-1b es
  explícito en que esos vectores certifican corrección, nunca temporización; una suite de
  pruebas de canal lateral es una obligación separada, recomendada (RI-1b) que esta parte pide
  pero no especifica.
- **Intercambio de primitiva poscuántica.** La suite `0x02` (un KEM de salto PQ, Parte 1 §5 cierre)
  cambia qué primitiva restringe RI-11, no el requisito de que sea de tiempo
  constante; el umbral de I-2 es PQ-seguro en todo caso (SP-1a), así que nada aquí está
  bloqueado por ello.

## 12. Requisitos introducidos aquí

- **RI-1 / RI-1a / RI-1b / RI-1c** — multiplicación, inverso y división GF(2⁸) de tiempo constante,
  **extendido a toda la vida del secreto recuperado** (el parseo de longitud de SP-8
  y todo el manejo de un byte reconstruido), no solo las operaciones de campo; los vectores
  certifican corrección, no temporización. **[protects I-2]**
- **RI-2 / RI-2a / RI-2b / RI-2c** — disciplina de CSPRNG: DRBG criptográfico desde el
  SO, seguridad ante fork/clone, verificaciones de salud, sin coeficientes inyectables (tras compuerta de prueba, no
  entregados). **[protects I-2 via SA-3]**
- **RI-3 / RI-3a / RI-3b** — marca de nivel máximo de `msg_nonce` persistida y sin retroceso,
  fsync-antes-del-uso, **y una restauración/snapshot se trata como retroceso** (detectar
  o retirar el `kpair`). **[protects SP-7b / SP-1a]**
- **RI-4** — estado de época estática del `onion` persistido y retirada con puesta a cero.
  **[protects CH-5 / CH-6]**
- **RI-5 / RI-5a / RI-5b** — estado de replay persistido para `gamma` (acotado por la época de
  clave) y `(box_id, slot)` (acotado por la **expiración de slot de 7 días**, no por la rotación
  de box de 1 día); una restauración que rebobina una caché es una rotación de época de clave obligatoria.
  **[protects SP-5 / SP-7b]**
- **RI-6 / RI-6a / RI-6b** — la API rechaza texto-en-claro-sin-AEAD; separar por tipo el
  texto cifrado; `split`/`reconstruct` crudo son privados del módulo. **[protects SP-1 /
  SP-1a]**
- **RI-7 / RI-7a** — reconstrucción de fallo cerrado **y rechazo de tiempo constante**;
  parseo defensivo de `(k,n)`. **[protects SP-7a]**
- **RI-8** — AEAD de tiempo constante y comparación de etiqueta de tiempo constante. **[protects
  SP-1a / SP-7]**
- **RI-9 / RI-9a / RI-9b** — almacenamiento que se puede poner a cero primero (anclado/nativo donde el
  runtime prohíbe el borrado en el sitio), luego puesta a cero anti-escritura-muerta; sin swap, sin
  volcados de núcleo; riesgos de optimizador/GC. **[protects I-2]**
- **RI-10** — implementar la derivación por salto Sphinx de CH-2 y la disciplina de replay/cegado;
  los vectores son roadmap 3.2. **[protects I-1 / I-4]**
- **RI-11 / RI-11a** — X25519 de tiempo constante; efímero sin clave, por paquete, puesto a cero;
  rechazar el secreto compartido todo-ceros en tiempo constante. **[protects
  CH-3 / CH-6 / I-2]**
- **RI-12** — seguridad ante fallos/excepciones: sin artefacto parcial o enlazable, poner a cero al
  desenrollar, fallar cerrado. **[protects I-2 / I-4]**

Ninguno de estos es un teorema; cada uno es una condición bajo la cual los teoremas de la Parte 7
y las garantías de las Partes 1–6 describen un **nodo real** en lugar del juguete. El
juguete omite cada uno de ellos a propósito y lo dice. Rompe esta parte nombrando una
ruta de código de nodo real que compute, almacene o revele un secreto sub-`k` de una manera
que ningún RI-n de arriba prohíba —esa ruta es un umbral roto en la práctica, y encontrarlo es
la invitación.
