# Especificación de ScrambNet — Parte 11: Gobernanza de actualizaciones
> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../../en/spec/11-update-governance.md)).

**Estado: BORRADOR (DRAFT).** Esta parte decide cómo un cliente llega a ejecutar un
binario de ScrambNet **más nuevo** *sin confiar en quien lo publicó*, bajo I-3 —ninguna
autoridad— y bajo dos restricciones impuestas por el dueño del proyecto: **ningún conjunto
autoritativo de firmantes** y **ningún push de ningún tipo**. Es la capa de adopción que
la Parte 10 §10.9 nombra como fuera de su propio alcance. La Parte 10 decide *si este
binario es la compilación de ese código fuente*; esta parte decide *qué compilación
ejecutar, y cuándo*. Los valores de hombre de paja se marcan con `(s)`.

Lee primero el §1 y el §10. Entre ambos dicen qué compra esta parte (reproducción y
frescura, no firma, como árbitro de la adopción) y qué concede por delante: rechazar tanto
una autoridad como un push compra **latencia de parcheo** como su residual central —un
cliente vulnerable puede no ser parcheado nunca, y en el peor caso (un cliente ya
comprometido por el mismísimo fallo que un parche corregiría) puede demostrablemente ni
siquiera llegar a enterarse del parche (§10.1). El proyecto acepta ese costo
deliberadamente, porque la alternativa —una parte o un canal que pueda hacer push de una
versión a todo el mundo a la vez— es exactamente el kill switch concentrado que el proyecto
entero existe para negar.

Esta parte reutiliza en lugar de reinventar: el índice de frescura de la Parte 10 (RB-8a),
el registro de versiones (RB-13), el gossip (RB-14), la disciplina de contar-solo-verificadas
(RB-10/RB-10a) y el estado del cliente no reconstructor (RB-7b); el registro de transparencia
sin permisos de la Parte 8 (ID-6/ID-7), la defensa de equivocación de raíz difundida por
gossip (ID-7a), la regla de múltiples registros (ID-7b) y el TOFU declarado (ID-8); la mezcla
de fuentes de la Parte 2 (GR-8); la superficie de honestidad de la Parte 3 (PS-9). La costura
con la Parte 10 se cita, no se vuelve a decidir (RB-2, Parte 10 §9).

## 1. La decisión, en dos frases

- **No hay autoridad de versión, y no hay push.** Una versión más nueva es un artefacto
  reproducible, direccionado por contenido, anunciado por un anexado sin permisos a un
  registro (UG-2); un cliente *se entera* de que puede existir solo tirando (pull) y
  difundiendo por gossip en su propia planificación (UG-3), *decide* adoptarla por un acto
  manual, local y de adhesión voluntaria (opt-in) (UG-4), y vincula esa decisión a la
  reproducción (RB-7) y a la frescura (RB-9a), **nunca** a quién la anunció o firmó (UG-1a,
  RB-2).
- **La confianza de adopción fluye a través de la reproducción y la frescura; la revocación
  solo puede informar, nunca forzar; y el precio —un cliente no parcheado o comprometido que
  nunca adopta— es un residual declarado, no un problema resuelto.** Ninguna firma controla
  la adopción (UG-2a); ningún mecanismo retira un binario malo de un cliente en ejecución
  (UG-8a); la señal de build-mala/known-bad es un informe sin permisos, sin fuerza e
  ignorable, nunca una autoridad (UG-8).

Así que el resultado honesto: **la adopción es tan libre de autoridad como la reproducción
la haga, y tan fiable como un usuario que elige actuar y no está eclipsado —nada más.** El
§10 es el residual que ninguna construcción aquí elimina.

## 2. Anunciar una versión sin un firmante

- **UG-1 (ninguna autoridad de versión; la adopción es un acto local del cliente).
  [normativo]** Ningún paso de *enterarse de*, *validar* o *adoptar* una versión más nueva
  DEBE (MUST) requerir confiar en que una parte concreta la publicó, anunció, firmó o
  bendijo. Las únicas operaciones confiables son las que la Parte 10 define —recomputar
  `BLAKE2s`, reconstruir-y-comparar (RB-1)— más comparar índices de versión monótonos sobre
  una línea (RB-8a, UG-2c). Todo elemento no reemplazable por un sustituto no confiable que
  realice esas operaciones es un defecto bajo I-3 y DEBE (MUST) eliminarse o declararse en el
  §10 (la regla ID-1 / RB-1, para la adopción de actualizaciones).
- **UG-1a (la adopción se vincula a la reproducción, nunca a la publicación). [normativo]**
  *Qué* compilación ejecutar lo decide el ancla de confianza de la Parte 10 —¿se reproduce
  (RB-7)?, ¿está fresca (RB-9a)?— y nada acerca de *quién* la anunció. Un cliente NO DEBE
  (MUST NOT) adoptar una compilación *porque* fue anunciada por una parte, clave, canal o
  lista. Esto reafirma RB-2 (las firmas localizan, nunca autorizan) en la frontera de
  adopción que RB-2 difiere a esta parte.
- **UG-2 (el anuncio es un anexado sin permisos a un registro, sin anexador privilegiado).
  [normativo]** Una versión se anuncia anexando su tupla de la Parte 10
  `(triple, H_build, manifest-hash, release-index, committer-date)` (RB-8/RB-8a) a los
  registros de transparencia sin permisos y de solo-anexado de RB-13 / ID-6 —la misma
  *construcción* que el registro del mapa, reutilizada como herramienta (RB-2a / ID-11a),
  nunca como autoridad compartida. **Cualquiera PUEDE (MAY) anexar**; no hay lista de
  permitidos ni conjunto de firmantes cuyo anexado haga oficial una versión (ID-7). Un
  registro que controlara los anexados de versión tras una lista sería la autoridad de
  directorio que I-3 prohíbe y es no conforme (ID-7, RB-2a).
- **UG-2a (ninguna firma autoritativa; por defecto no hay ninguna). [normativo]** Una versión
  conforme no porta **ninguna firma autoritativa**. Si aparece una firma seudónima en
  absoluto, es un puro localizador RB-2 —atribuye una compilación a una mano seudónima
  continua para conveniencia del gossip— y un cliente DEBE (MUST) tratar un anuncio firmado y
  uno sin firmar de la misma `(triple, H_build, release-index)` como portadores de **idéntico
  peso de adopción** una vez que la reproducción los corrobora (RB-10). Un diseño en el que la
  aceptación de un anuncio depende de la identidad de un firmante es no conforme (RB-1,
  RB-12).
- **UG-2b (la línea de versión no es propiedad de ninguna parte). [normativo]** El índice de
  RB-8a es monótono *dentro de una línea de versión*. Una línea DEBE (MUST) definirse de modo
  que ninguna parte posea el derecho a extenderla; de lo contrario "anexar un índice más alto"
  se convierte en una autoridad para declarar la siguiente versión (la autoridad de directorio
  que I-3 prohíbe, llevando un número de versión). UG-2c da la construcción.
- **UG-2c (la identidad de línea es una cadena de manifiestos verificable por reproducción
  desde un génesis). [normativo]** Una línea se identifica por `line_id = BLAKE2s` de su
  **manifiesto génesis** (el manifiesto canónico de la primera versión, RB-8a). Una versión
  **extiende** `line_id` si y solo si su manifiesto porta el manifest-hash de la versión
  previa como un campo predecesor explícito **y** su código fuente etiquetado se reproduce
  hacia adelante (RB-7) desde un linaje de código fuente cuya etiqueta previa es la del
  predecesor —así que "extender la línea" es un **acto sin permisos, verificable por
  reproducción**: cualquiera que pueda producir un manifiesto sucesor que reproduzca puede
  anexar un índice más alto, y ningún repositorio, committer o clave posee la línea. Una
  **bifurcación (fork)** es cualquier manifiesto que no encadena con `line_id`; porta
  necesariamente un `line_id` diferente y por tanto es **visible como una línea distinta**,
  nunca un índice más alto silenciosamente inyectado en la que se rastrea (la regla ID-2 "el
  hash es el único nombre", para el linaje de versión). `line_id` es estable a través de
  versiones honestas (el hash del génesis no cambia) y sin embargo no es propiedad de nadie
  (la cadena es pública y verificada por reproducción) —las dos propiedades que UG-2b exige.

## 3. Descubrimiento sin un push

- **UG-3 (el descubrimiento es solo pull/gossip; no existe ruta de push). [normativo]** Un
  cliente se entera de que una versión más nueva *puede* existir **solo** (a) tirando (pull)
  del índice de frescura (RB-8a) y de las tuplas de registro de la línea (RB-13) en su propia
  planificación, y (b) difundiendo por gossip `(line_id, triple, H_build, release-index)` por
  GR-6 bajo la mezcla de fuentes de GR-8 (RB-14). Ningún mecanismo de esta parte —y ninguno
  que un despliegue conforme PUEDA (MAY) añadir— hace push de una versión, una notificación o
  un aviso a un cliente. La ruta más débil de "notificar-disponibilidad" **no se adopta
  explícitamente**: la frescura se tira (pull) y se difunde por gossip, nunca se entrega (la
  restricción vinculante del dueño, enunciada normativamente para que un implementador no
  pueda re-añadir un push y seguir siendo conforme).
- **UG-3a (ninguna fuente única controla la frescura). [normativo]** Un cliente NO DEBE (MUST
  NOT) tratar el release-index más alto que ha visto como actual bajo la palabra de un solo
  par, registro o espejo antes de aplicar la regla GR-8 / PS-10 "cuenta solo las fuentes
  verificadas independientemente" (RB-14, ID-9). Su visión de *qué es actual* es una
  observación con mezcla de fuentes bajo la misma defensa de eclipse que sus vistas del mapa y
  de muestra de relés.
- **UG-3b (la cadencia de descubrimiento es local al cliente y acotada por privacidad).
  [normativo]** La cadencia de pull es una política local al cliente (hombre de paja:
  oportunista, plegada en los lotes de gossip GR-6 existentes, nunca un faro distintivo (s)).
  El tráfico de pull de frescura NO DEBE (MUST NOT) convertirse en una huella; va montado en
  el canal de gossip que el cliente ya usa (la disciplina de metadatos GR-8 / Parte 6,
  aplicada al descubrimiento de actualizaciones).
- **UG-3c (un cliente tira (pull) según su propio reloj, nunca en reacción a una señal de un
  par). [normativo]** Un cliente PUEDE (MAY) iniciar una obtención **solo** en su propia
  cadencia acotada por privacidad (UG-3b) o en una acción explícita del usuario. NO DEBE (MUST
  NOT) iniciar una obtención *en respuesta a* una señal de divergencia, build-mala/known-bad o
  equivocación reportada por un par: ese disparador reactivo es la degradación de re-obtención
  ID-9a (la Parte 8 §10 marca "trata tu mapa como sospechoso, vuelve a obtener" como una
  dirección poco defendida que un adversario impulsa), y para actualizaciones es
  **push-disfrazado** (UG-5a). Las anomalías se exponen y se difunden por gossip (UG-7), nunca
  se actúan sobre ellas obteniendo. Esta es la frontera entre "mi pull programado notó un
  índice más alto" (permitido) y "un par me hizo ir a mirar" (prohibido).

## 4. Decidir adoptar (opt-in manual, sin puerta de firma)

- **UG-4 (la adopción es un acto manual, local y de adhesión voluntaria (opt-in)).
  [normativo]** Reemplazar el binario en ejecución por uno más nuevo descubierto es una
  decisión que el **usuario** toma localmente; ningún cliente conforme adopta una versión
  automáticamente, por temporizador, ni al alcanzar cualquier umbral de corroboración. El
  umbral gobierna *qué puede ofrecer o exponer el cliente*, nunca *qué instala*.
  "Corroborada" es una precondición que el cliente verifica; "adoptar" es un acto que el
  usuario realiza (la postura ID-8b "detectar, no pretender prevenir", trasladada de la
  detección a la adopción).
- **UG-4a (la lista de verificación de adopción —sin puerta de firma). [normativo]** Antes de
  exponer una versión descubierta como *adoptable*, un cliente DEBE (MUST) tener, para su
  propio triple de destino y `line_id` rastreado:
  1. **corroboración de reproducción** — `H_build` coincide con el manifiesto, por la propia
     reconstrucción del cliente (RB-7) **o**, para el cliente modal no reconstructor (RB-7b),
     una cuenta de reproductores **verificados independientemente** bajo RB-10 (nunca un
     conteo crudo de atestaciones);
  2. **frescura** — un release-index ≥ el más alto que el cliente ha atestiguado en esa línea,
     ordenado en el registro (RB-9a, RB-8a, UG-2c);
  3. **corroboración de registro** — aparición con raíces difundidas por gossip consistentes
     en un quórum configurado de los registros que vigila (ID-7b, hombre de paja ≥2 (s));
  4. **sin equivocación** — ninguna anomalía de vista partida UG-6 pendiente contra esa línea.

  **No hay paso de puerta de firma**, por construcción (UG-2a). Un cliente NO DEBE (MUST NOT)
  presentar ninguna de estas como "verificada" cuando solo tiene corroboración-por-cuenta;
  arrastra el estado `reproducido-por-otros-no-verificado` de la Parte 10 hasta la interfaz
  (RB-7b).
- **UG-4b (la política de adopción es declarada, local al cliente, conservadora por defecto).
  [normativo]** La política que convierte las verificaciones UG-4a en un *ofrecimiento* es
  local al cliente y DEBE (MUST) declararse al usuario (hombre de paja por defecto: ofrecer
  solo una versión más fresca por índice, corroborada por reproducción por encima del umbral
  del cliente, corroborada por registro en quórum, y libre de equivocación; nunca ofrecer a
  través de un cambio de `line_id` (UG-2c) sin un paso explícito del usuario (s)). Un cliente
  PUEDE (MAY) exponer una política más estricta (p. ej. "ofrecer solo lo que yo mismo
  reconstruí"); NO DEBE (MUST NOT) exponer una más débil que "índice más fresco + corroborado
  en quórum + sin equivocación", porque más débil se reduce a adoptar bajo la palabra de una
  sola fuente (UG-3a). **Un informe de build-mala/known-bad de clase vulnerabilidad no
  refutado (UG-8) NO DEBE (MUST NOT) por sí mismo rebajar una versión por debajo de este
  umbral de ofrecimiento** (UG-8, defensa de H-difamación).
- **UG-4c (ofrecer e instalar son mecánicamente distintos). [normativo]** **OFRECER** es la
  exposición al usuario de un estado de disponibilidad-y-corroboración; NO DEBE (MUST NOT)
  obtener el cuerpo del artefacto en respuesta a un disparador de divergencia o de
  build-mala/known-bad (UG-3c), y toda pre-obtención DEBE (MUST) ir montada en la cadencia
  UG-3b de modo que no añada ningún faro distintivo. **INSTALAR** es un acto iniciado por el
  usuario que reemplaza el binario en ejecución. No puede existir ninguna transición
  automática de OFRECER a INSTALAR (UG-10). Una implementación que pre-prepara un binario a un
  toque de ejecutarse, u obtiene ante una señal de un par, ha construido un push y es no
  conforme aunque llame al paso "ofrecer".

## 5. La defensa de downgrade reproducible, del lado del cliente

- **UG-5 (nunca aceptar silenciosamente un índice menor; exponerlo). [normativo]** Un cliente
  NO DEBE (MUST NOT) adoptar, ni tratar silenciosamente como actual, cualquier versión cuyo
  índice sea **menor** que el más alto que ha atestiguado para ese `line_id` (RB-9a). Un
  índice presentado-como-menor es la firma, desde un único punto de vista, de un **ataque de
  downgrade reproducible** —una etiqueta antigua, que reproduce perfectamente y con
  vulnerabilidad conocida, alimentada al cliente (RB-9a)— y DEBE (MUST) exponerse al usuario y
  difundirse por gossip como una anomalía de downgrade (UG-7d), nunca consumirse como un
  "último" ordinario. Porque el índice está vinculado a la fecha de committer derivada y a la
  cadena de manifiestos (RB-8a, UG-2c) y ordenado en el registro (RB-13), "índice menor" es
  una propiedad verificable, no un juicio.
- **UG-5a (la obsolescencia se expone, no se actúa sobre ella). [normativo]** Cuando el propio
  índice en ejecución de un cliente cae por debajo del índice actual de un quórum corroborado
  para su línea, DEBE (MUST) exponer la obsolescencia al usuario (la superficie de honestidad
  de PS-9, reutilizada) —*estás ejecutando una versión más antigua que tus pares corroborados;
  existe una más nueva.* NO DEBE (MUST NOT) actuar sobre esa exposición tirando (pull),
  avisando-como-push, ni adoptando (UG-3c); informa, y el usuario decide (UG-4). La asimetría
  honesta con ID-9a es deliberada: la maquinaria del mapa *vuelve a obtener* ante la
  divergencia; la adopción de actualizaciones **no** debe hacerlo, porque una re-obtención
  forzada sería un push disfrazado. La obsolescencia se detiene en la superficie de
  honestidad.

## 6. Vista partida y equivocación sobre versiones

- **UG-6 (dos "últimos" diferentes a dos clientes se atrapan por raíces difundidas por
  gossip). [normativo]** Un adversario que sirve la versión X a Alice y la versión Y a Bob
  —mismo triple, mismo `line_id`— es un ataque de vista partida sobre la *frescura*, el ataque
  ID-7a llevando una máscara de actualización. La defensa **no** es confiar en el operador del
  registro; es difundir por gossip las cabezas de árbol firmadas de los registros por GR-6
  (con mezcla de fuentes GR-8) y exigir **pruebas de consistencia** entre cualesquiera dos
  raíces que un cliente vea (ID-7a, RB-14). Un cliente que tiene ambas raíces tiene prueba
  criptográfica de que el registro equivocó y DEBE (MUST) tratarlo como hostil (ID-10, UG-7b).
- **UG-6a (la equivocación-de-índice es la firma de punto-de-vista-cruzado; desambiguada del
  downgrade). [normativo]** El **downgrade** (UG-5 / UG-7d) es la firma de *un único punto de
  vista*: *mi propio* máximo atestiguado en una línea retrocedió. La
  **equivocación-de-índice** (UG-7b) es la firma de *punto-de-vista-cruzado*: el mismo
  `line_id` presentado con un índice más alto diferente a distintos puntos de vista con mezcla
  de fuentes **y** las raíces de los registros fallan una prueba de consistencia —dos índices
  diferentes por sí solos no son equivocación (un punto de vista puede simplemente ir
  retrasado); el **fallo de prueba de consistencia** es lo que la demuestra. Un único evento
  subyacente puede levantar ambas firmas (la víctima fijada a un índice obsoleto ve un
  downgrade cuando luego oye el más alto; una parte que tiene ambas raíces ve equivocación);
  DEBE (MUST) deduplicarse por `(line_id, raíces conflictivas)` (la disciplina de dedup
  RB-10a, reutilizada) de modo que se cuente una sola vez. La equivocación-de-índice se
  difunde por gossip de modo que un cliente parcialmente eclipsado la atrape a través de pares
  no eclipsados.

## 7. Las anomalías de versión se difunden por gossip, no se suprimen

- **UG-7 (gossip de anomalías obligatorio). [normativo]** Cinco eventos son anomalías de
  versión que todo cliente DEBE (MUST) difundir por gossip al detectarlas, comparando solo
  datos de triple-igual y `line_id`-igual, y deduplicadas según RB-10a: (a) un `H_build` que
  falla la reproducción a partir de su manifiesto (RB-7a / RB-15a); (b) un registro que
  presenta raíces inconsistentes sobre los anuncios de versión —equivocación demostrada
  (RB-15b, UG-6/UG-6a); (c) una divergencia persistente de `H_build` de triple-igual frente a
  reproductores independientes (RB-15c); (d) una **regresión de release-index** sobre una
  línea —la firma del downgrade (UG-5 / RB-15d); (e) un **informe de build-mala/known-bad**
  (UG-8). Un cliente NO DEBE (MUST NOT) suprimir una anomalía para hacer que una versión
  parezca sana (ID-10, para versiones).

## 8. El problema de la revocación (el difícil)

- **UG-8 (build-mala/known-bad es un INFORME sin permisos, corroborado y sin fuerza —nunca una
  revocación autoritativa). [normativo]** "La versión X es build-mala/known-bad" no puede ser
  una afirmación autoritativa: *cualquier* parte en la que se confíe para pronunciar que una
  versión es mala es un kill switch (puede **censurar** una versión honesta declarándola mala
  —la autoridad I-3 invertida), así que ninguna tal parte existe. En su lugar esta parte provee
  un **informe de build-mala/known-bad**: una afirmación
  `(line_id, triple, H_build, reason-class, evidence-locator)` que **cualquiera PUEDE (MAY)
  publicar y cualquiera PUEDE (MAY) ignorar**. Los informes cruzan el cable y alimentan un
  conteo, así que DEBEN (MUST) reutilizar **RB-10a al pie de la letra**: CBOR canónico, dedup
  por `(identidad de reproducción del reportante, line_id, triple, H_build, reason-class)`, y
  peso **por-reproductor-independiente, nunca por-cadena-de-bytes-de-informe** —sin lo cual el
  canal es una palanca de relleno-de-formato / difamación (H-difamación). La evidencia se
  divide en dos tipos:
  - **evidencia reproducible (el informe se autoverifica; no se necesita confianza)** —
    *no-reproducción* (reconstruir a partir del manifiesto y ver fallar RB-7a),
    *regresión-de-índice / downgrade* (el orden del registro lo muestra, UG-5), *equivocación
    de registro* (la prueba de consistencia falla, UG-6). Para un cliente que **puede
    reconstruir / alcanzar un reproductor honesto**, "build-mala/known-bad" aquí se reduce a
    una verificación de la Parte 10 que él mismo ejecuta; el informe meramente *localiza* el
    defecto, no *autoriza* el veredicto.
  - **evidencia no reproducible (se reduce a consenso social)** — *"esta compilación que
    reproduce contiene una vulnerabilidad / puerta trasera."* Ninguna verificación
    criptográfica decide esto —es el residual de honestidad-del-fuente de la Parte 10 §10.1 /
    OP-10. Aquí "build-mala/known-bad" es una afirmación ponderada por revisión pública (I-1),
    cuenta de corroboración, y reproducibilidad-de-la-evidencia-donde-exista (una PoC que
    reconstruye), y se reduce a **OP-2 y la capa social del proyecto**. Un **informe de clase
    vulnerabilidad no refutado NO DEBE (MUST NOT) por sí mismo controlar un ofrecimiento**
    (UG-4b): PUEDE (MAY) solo *anotar* el ofrecimiento ("N partes verificadas
    independientemente alegan una vulnerabilidad; evidencia en …"), nunca rebajar la versión
    por debajo del umbral UG-4a —precisamente porque esta clase es votable por sybil (GR-19a) y
    controlar sobre ella dejaría a un adversario censurar un parche de seguridad honesto hacia
    la obsolescencia.

  **El teléfono modal (RB-7b) no disfruta de las clases reproducibles.** Un cliente que no
  puede reconstruir no puede autoverificar un informe de no-reproducción, y un cliente
  eclipsado no puede tener las dos raíces que una prueba de equivocación de registro necesita
  (ID-7a §10). Para el cliente no reconstructor o eclipsado, **todo salvo la verificación
  aritmética de regresión-de-índice se reduce a corroboración RB-10, es decir, OP-2** (la
  reducción de la Parte 10 §10.5, heredada —véase §10.2). Un cliente conforme NO DEBE (MUST
  NOT) auto-actuar sobre un informe de build-mala/known-bad (eso recrearía el push y la
  autoridad a la vez); expone el informe con su nivel de corroboración y clase de evidencia, y
  el usuario decide si detenerse o moverse.
- **UG-8a (la revocación solo puede informar; no puede hacer push, así que no puede
  forzar-parche). [normativo]** Porque no existe push (UG-3) y no existe autoridad (UG-1), un
  informe de build-mala/known-bad llega a un cliente solo cuando ese cliente tira (pull) /
  difunde por gossip, y no cambia nada hasta que el usuario actúa. **No hay mecanismo para
  retirar un binario build-mala/known-bad de un cliente en ejecución**, y esta parte no finge
  tenerlo. La señal de build-mala/known-bad hace una versión mala *detectable y evitable por un
  usuario atento y no eclipsado*; no puede hacerla *inejecutable* por decreto. Este es el
  residual de revocación (§10.2), enunciado, no suavizado.
- **UG-8b (negarse-a-ejecutar autoverificado —libre de autoridad, opt-in, solo autoprueba).
  [normativo]** Un cliente que **él mismo** demuestra (RB-7, sin parte externa) que su **propio
  binario en ejecución** falla la reproducción contra su manifiesto enviado —o que su propio
  índice embebido es una regresión que puede verificar aritméticamente contra un piso no
  eclipsado— PUEDE (MAY), **como un opt-in local al cliente, no un valor por defecto**,
  negarse a seguir ejecutando ese binario y recurrir al re-arranque (ID-8). Esto es **libre de
  autoridad** (la prueba es la propia reconstrucción del cliente, y una prueba de
  no-reproducción falsa es *imposible* —el adversario no puede hacer que código fuente público
  honesto reproduzca a un `H` malo, ID-8a.3) y **no es un push** (nada se instala; el cliente
  declina ejecutar código que demostró que no es la reproducción de su propio código fuente
  declarado —el análogo en tiempo de ejecución de RB-7a, que ya *rechaza* una versión que no
  reproduce en la adopción). Negarse-a-ejecutar DEBE (MUST) permanecer **prohibido** para
  cualquier evidencia que el cliente no pueda autoverificar —la clase vulnerabilidad y
  cualquier cosa que descanse en una cuenta de corroboración o un piso de quórum (ambos OP-2 /
  falsificables por eclipse)— porque allí un piso o informe *falso* sería una denegación de
  servicio contra un cliente honesto. Esto protege solo al cliente **reconstructor**; el
  teléfono modal no reconstructor (RB-7b) aún se reduce a OP-2 (§10.2), así que UG-8b estrecha
  la brecha de seguridad-de-flota (§10.1) sin cerrarla.

## 9. Arranque: la primera actualización es TOFU

- **UG-9 (la primera actualización hereda el TOFU del primer-binario de la Parte 10 y no puede
  verificarse a sí misma). [normativo]** La visión de un cliente de *qué versión es actual*
  está mediada por el binario que ya está ejecutando; un primer binario comprometido (Parte 10
  §10.8) posee todo el aparato de descubrimiento, frescura y gossip del cliente y por tanto
  puede **mentir sobre la frescura** —fijar al usuario a un índice obsoleto y vulnerable,
  ocultar un informe de build-mala/known-bad sobre sí mismo, o suprimir una equivocación de la
  que es parte. Un cliente no puede verificar honestamente su *propia* actualidad más de lo que
  puede verificar su *propia* reproducción (Parte 10 §10.8). La confianza en la primera
  actualización descansa en la misma **corroboración independiente fuera de banda** que el
  primer binario: una vista de release-index y de build-mala/known-bad alcanzada desde una
  máquina o canal en el que el usuario confía más que en el binario bajo prueba. Esto es TOFU
  declarado (ID-8), no resuelto.
- **UG-9a (la primera elección de versión de un cliente recién llegado es TOFU sobre canales
  independientes). [normativo]** En la primera instalación un cliente DEBE (MUST) obtener su
  `(line_id, index, H_build)` inicial sobre tantos canales **independientes** como tenga (Parte
  10 §10.8 / ID-8: la línea puente fuera de banda GR-10 más ≥2 espejos sobre redes distintas
  (s)), exigir el **mismo** `(line_id, index, H_build)` de todos antes de aceptar
  provisionalmente, y registrarlo como **TOFU-no-verificado** hasta que reconstruya (RB-7) o
  acumule corroboración consistente difundida por gossip. DEBE (MUST) exponer este estado:
  *estás confiando en tu primer cliente y en tu primera noción de "último"; ninguno está aún
  corroborado.*

## 10. Lo que esta parte no resuelve (el residual declarado)

Esta parte mueve la confianza de adopción de actualizaciones de *quién lo envió* a *¿se
reproduce y está fresco?*, y rechaza tanto una autoridad como un push —la elección correcta
para un proyecto cuya cada lista es un objetivo de coerción. **No** entrega una flota
parcheada y segura. Las brechas son reales y declaradas, no suavizadas:

- **§10.1 — El residual de flota-no-parcheada, y su peor caso: sin push no hay parche forzado,
  y el cliente comprometido demostrablemente puede no enterarse nunca de la corrección.
  [residual primario]** Un cliente cuyo usuario nunca adopta manualmente —offline, desatento o
  abandonado— ejecuta su versión actual, con vulnerabilidades y todo, **indefinidamente**
  (UG-4). No existe anulación, porque una anulación es un push. Peor aún, las cláusulas se
  componen contra la flota: en el único escenario que más importa —un cliente ejecutando un
  **RCE activamente explotado**— el binario en ejecución está **ya controlado por el atacante**,
  y ese es exactamente el binario que UG-9 dice que puede mentir sobre la frescura y suprimir
  la build-mala/known-bad sobre sí mismo. Así que el mecanismo que encaminaría el parche
  (gossip + superficie de obsolescencia, UG-3/UG-5a) corre **dentro del proceso comprometido**
  y puede ser silenciado. La conclusión honesta: para el caso de RCE-comprometido la superficie
  de honestidad y la ruta de gossip no dan **ninguna** garantía de entrega; el residual no es
  "parcheo más lento" sino **"el subconjunto comprometido puede no adoptar nunca,"** un estado
  terminal hasta el re-arranque fuera de banda (ID-8), acotado solo por que el usuario lo note
  por algún canal fuera del cliente comprometido. UG-8b estrecha esto para el cliente opt-in
  *reconstructor* (puede negarse a ejecutar un binario autoprobado como malo), no para el
  teléfono modal. Este es el precio deliberado de rechazar un push y una autoridad, y se nombra
  primero y a plena fuerza.
- **§10.2 — La revocación-sin-autoridad es inalcanzable para la clase vulnerabilidad, y se
  reduce a OP-2 para el cliente modal a través de más de una clase.** La no-reproducción, el
  downgrade y la equivocación son revocables de forma libre de autoridad *solo para un cliente
  que puede reconstruir o alcanzar un reproductor honesto* (UG-8). "Esta compilación que
  reproduce tiene una puerta trasera" nunca es libre de autoridad —ninguna verificación decide
  la honestidad-del-fuente (OP-10 / Parte 10 §10.1)— así que la revocación de una versión
  revisada-pero-maliciosa descansa en la revisión pública (I-1), en la corroboración cuya
  independencia es inverificable (RB-10 / GR-19a), y en que el usuario elija actuar: OP-2 más
  la capa social. Para el **cliente modal no reconstructor o eclipsado**, las clases de
  no-reproducción y equivocación de registro **también** se reducen a OP-2 (solo la
  verificación aritmética de regresión-de-índice sobrevive a la autoverificación) —la reducción
  de la Parte 10 §10.5, heredada. La contribución del diseño es hacer la *afirmación* de
  build-mala/known-bad sin permisos, corroborada, con disciplina de dedup (RB-10a) y **sin
  fuerza** de modo que nunca sea una autoridad; **no** contribuye ningún mecanismo que retire
  una versión mala-pero-que-reproduce de una flota en ejecución.
- **§10.3 — El cliente eclipsado nunca oye la actualización, y su maquinaria de frescura es
  manipulable.** Un cliente eclipsado (OP-2) no toca ninguna raíz honesta, así que la detección
  de equivocación de UG-6 **no puede dispararse** —la víctima nunca tiene dos raíces
  conflictivas. Bajo eclipse un adversario puede fijar a la víctima a un **índice obsoleto y con
  vulnerabilidad conocida** (un downgrade silencioso que UG-5 no puede atrapar, porque la
  víctima nunca atestigua el índice más alto), **suprimir** cada informe de build-mala/known-bad
  sobre la compilación en ejecución, y mostrar un pasado congelado **corroborado por sybil**. La
  frescura es una garantía *relativa* —más fresca que lo que has atestiguado— y un cliente
  eclipsado solo ha atestiguado lo que el adversario permitió. Para el cliente eclipsado no
  reconstructor, "ninguna autoridad, solo-pull" significa "confía en el quórum con mezcla de
  fuentes", y eso se sostiene **solo hasta donde lo hace OP-2** —la reducción con la que las
  Partes 8 y 10 terminan.
- **§10.4 — El usuario que nunca adopta está atascado por diseño.** El opt-in manual de UG-4
  significa que un usuario que descarta cada ofrecimiento se queda en una compilación antigua;
  no hay anulación, porque una anulación es un push. El diseño acepta una **fracción no nula en
  estado estacionario de la flota sobre versiones obsoletas** como el costo declarado de
  rechazar un push, y expone la obsolescencia (UG-5a) en lugar de actuar sobre ella.
- **§10.5 — El TOFU de la primera actualización hereda la Parte 10 §10.8 y es estrictamente peor
  para la frescura.** Un primer binario comprometido puede mentir sobre la actualidad tan
  fácilmente como sobre la reproducción —congelando al usuario a un índice obsoleto para siempre,
  indetectablemente desde dentro (UG-9). La primera-noción-de-último es TOFU, corroborada solo
  fuera de banda.
- **§10.6 — Herramientas compartidas, no autoridad compartida, deben re-auditarse para el
  registro de actualizaciones.** Reutilizar la construcción de registro y el canal de gossip del
  mapa / de la Parte 10 (RB-2a, ID-11a) es gratis *solo* mientras ningún rol de una parte sea
  portante tanto para el mapa/código como para la línea de actualizaciones. Un despliegue
  conforme DEBE (MUST) mantener los anexadores del registro de línea de versión como una
  no-lista (UG-2) y DEBERÍA (SHOULD) usar un conjunto de registros independiente del del mapa
  (ID-7b), de modo que "conveniencia: reutiliza los mismos operadores" no recree silenciosamente
  el kill switch transversal que ID-11 prohíbe. El caso fork-vs-escape es un residual adicional:
  una bifurcación dura honesta (divergencia legítima) y un adversario abriendo una línea paralela
  para escapar de un downgrade/build-mala/known-bad sobre la línea rastreada son
  **indistinguibles a nivel de protocolo** —ambos son un nuevo `line_id` (UG-2c). UG-2c hace
  visible la *existencia* de una segunda línea; no decide la *intención*, que es un juicio
  social / OP-2, no uno criptográfico.

El resumen honesto: esta parte rechaza tanto una autoridad como un push, y a cambio es
**silenciosa** sobre forzar un parche (§10.1), **no puede revocar criptográficamente una versión
revisada-pero-maliciosa** (§10.2), **se reduce a OP-2 bajo eclipse** (§10.3), **deja al usuario
que nunca adopta atascado por diseño** (§10.4), y es **TOFU en la primera noción de "último"**
(§10.5). La respuesta correcta es acotarlos —gossip de build-mala/known-bad ruidoso, sin permisos
y con disciplina de dedup (UG-7/UG-8), una superficie de obsolescencia visible (UG-5a),
corroboración fuera de banda de la primera actualización (UG-9a), negarse-a-ejecutar opt-in
autoverificado para el reconstructor (UG-8b), mezcla de fuentes agresiva (UG-3a)— y **enunciar**
el intercambio de latencia-de-parcheo en la interfaz y en la especificación, no esconderlo tras
"ninguna autoactualización es más segura".

## 11. Requisitos introducidos aquí

- **UG-1 / UG-1a** — ninguna autoridad de versión; la adopción se vincula a la reproducción y la
  frescura, nunca a la publicación (reafirma RB-2 en la frontera de adopción).
- **UG-2 / UG-2a / UG-2b / UG-2c** — anuncio por anexado a un registro sin permisos, sin firmante;
  firmado y sin firmar portan idéntico peso de adopción; la línea de versión no es propiedad de
  ninguna parte —`line_id` es una cadena de manifiestos verificable por reproducción desde un
  génesis, una bifurcación es una línea visiblemente distinta.
- **UG-3 / UG-3a / UG-3b / UG-3c** — el descubrimiento es solo pull/gossip, sin push; con mezcla de
  fuentes, acotado por privacidad, según el reloj del cliente; nunca una obtención reactiva a una
  señal de un par (esa es la degradación de re-obtención ID-9a).
- **UG-4 / UG-4a / UG-4b / UG-4c** — la adopción es opt-in manual; una lista de verificación de
  cuatro puertas sin puerta de firma; una política conservadora declarada; ofrecer e instalar son
  mecánicamente distintos sin transición automática.
- **UG-5 / UG-5a** — nunca aceptar silenciosamente un índice menor (downgrade reproducible); la
  obsolescencia se expone en PS-9, no se actúa sobre ella (la asimetría deliberada con ID-9a).
- **UG-6 / UG-6a** — la vista partida sobre la frescura se atrapa por raíces difundidas por gossip +
  pruebas de consistencia; la equivocación-de-índice es la firma de punto-de-vista-cruzado,
  desambiguada del downgrade de punto-de-vista-único y deduplicada.
- **UG-7** — cinco anomalías de versión obligatorias, difundidas por gossip, deduplicadas según
  RB-10a.
- **UG-8 / UG-8a / UG-8b** — build-mala/known-bad es un informe sin permisos, con disciplina RB-10a
  y sin fuerza, nunca una autoridad; un informe de clase vulnerabilidad anota pero nunca controla un
  ofrecimiento; la revocación solo puede informar; negarse-a-ejecutar autoverificado opt-in es libre
  de autoridad y permitido, negarse-a-ejecutar por evidencia-externa está prohibido.
- **UG-9 / UG-9a** — la primera actualización se declara TOFU sobre canales independientes; un primer
  binario comprometido puede mentir sobre la frescura, corroborada solo fuera de banda.

UG-1 y UG-4 son las dos portantes: ninguna autoridad, y la adopción es un acto manual vinculado a la
reproducción. Ambas están acotadas, no son absolutas —UG-1 se reduce a OP-2 para el cliente no
reconstructor o eclipsado (§10.2, §10.3), y el no-push de UG-4 compra el residual de
flota-no-parcheada (§10.1), cuyo peor caso —un cliente comprometido que demostrablemente puede no
oír nunca el parche— se nombra a plena fuerza en lugar de suavizarse. Rompe esta parte nombrando una
ruta de push que un cliente conforme PUEDA (MAY) añadir, un firmante que controle la adopción, una
forma en que un informe de build-mala/known-bad fuerce una acción o censure una versión honesta más
allá de UG-4b, una forma de extender una línea de versión sin reproducción (un dueño de la línea), o
una forma en que el cliente no reconstructor quede confiando en una mayoría que no es OP-2. Esa es la
invitación, en la voz de la Parte 8.
