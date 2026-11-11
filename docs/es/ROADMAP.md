# ScrambNet — Hoja de ruta

**Estado: documento vivo.** Este es el plan de trabajo, no una promesa de fechas — un
proyecto de voluntarios seudónimo avanza cuando hay manos libres. Está ordenado por
dependencia y por honestidad: los elementos que podrían demostrar que el proyecto está
*equivocado* van primero, porque si la afirmación portante no se sostiene, nada de lo que viene
después importa. Cada elemento nombra cómo se ve lo «hecho», para que el progreso sea comprobable,
no afirmado.

Se construyó a partir de tres revisiones paralelas — diseño de red, criptografía y
seguridad/operaciones — y los hallazgos más duros se mantienen a la vista en lugar de
suavizarse. Los elementos hacen referencia a las partes de la especificación (`SP-n`, `GR-n`,
`PS-n`, `RZ-n`), los invariantes (`I-1…I-4`) y los problemas abiertos
(`OP-1…OP-9`).

Escala de esfuerzo: **S** ≈ días · **M** ≈ 1–2 semanas · **L** ≈ semanas, riesgo real de
diseño · **XL** ≈ un subproyecto de investigación que puede devolver un resultado parcial o
negativo. Los dos últimos no son fallos que evitar; son la forma honesta de los
problemas no resueltos.

---

## Nivel 0 — Corregir lo que ya sabemos que está mal (ahora)

Estos salieron de las revisiones como defectos concretos o afirmaciones excesivas. Son baratos
y protegen la credibilidad del proyecto, que es su único activo real en esta
etapa.

- **0.1 — Reconciliar las afirmaciones públicas con el alcance probado.** `[crítico-para-la-afirmación]`
  El umbral de contenido es teórico-informativo **solo por debajo de `k` partes**; por encima de
  `k`, el secreto del contenido es computacional (el AEAD). Y «cosecha ahora, descifra
  después» se derrota **solo** para el adversario por-debajo-de-`k` — un adversario `≥k`, que-lo-
  graba-todo, futuro-cuántico aún rompe el contenido *a menos que el acuerdo de claves
  extremo a extremo sea él mismo poscuántico o precompartido*. El README, la COMPARISON
  y el modelo de amenazas deben enunciar el régimen (por-debajo-de-`k` vs por-encima-de-`k`)
  y la suposición (secreto de la clave AEAD) en toda frase sobre el umbral.
  **Hecho:** no queda ninguna «protección de contenido teórico-informativa» sin cualificar en
  ningún documento público. **Esfuerzo S.**

- **0.2 — Especificar y demostrar la capa AEAD extremo a extremo.** `[crítico-para-la-afirmación]`
  SP-1 («cifrar antes de la dispersión») es toda la afirmación de composición, pero la PoC
  divide *texto en claro* — no hay AEAD en ninguna parte, así que la composición se afirma,
  nunca se muestra. Especifica la capa e2e (establecimiento de clave a partir del `kpair` de la
  tarjeta de contacto vs un intercambio efímero — una elección que decide la historia poscuántica),
  y extiende la PoC para que realmente cifre → divida → reconstruya → descifre.
  **Hecho:** la PoC demuestra SP-1 de extremo a extremo; la elección de establecimiento de clave está
  tomada y su consecuencia PQ registrada. **Esfuerzo M.**

- **0.3 — Integridad de las partes bajo un drop malicioso.** `[solidez]`
  La etiqueta SP-7 dice *a qué* mensaje afirma pertenecer un paquete, pero nada
  autentica los bytes de la parte ni el byte `k,n`. Un único drop o salida hostil
  puede voltear bits en una parte; Shamir no puede detectarlo, así que `k` partes corruptas-consistentes
  reconstruyen basura (el AEAD de arriba lo captura — falla cerrado — pero
  esto es una barata *denegación de servicio dirigida* sobre un buzón). Decide: vinculación
  por-parte explícita, o un residuo aceptado-y-documentado de falla-cerrada-con-reintento.
  **Hecho:** un veredicto con la construcción si hace falta, escrito en
  SP-7. **Esfuerzo M.**

- **0.4 — Publicar la clave PGP del proyecto.** `[opsec, hueco inmediato]`
  SECURITY.md *promete* una clave que no existe. La primera oleada de revisores
  (las listas de correo) no tiene canal confidencial. Genera una clave vinculada a un seudónimo
  para `scrambnet@proton.me`, confirma su huella digital, reemplaza el «tiempo
  razonable» vago por una ventana de divulgación real, y enuncia cómo rota la clave misma
  (incluso la clave de divulgación no debe ser un singleton insustituible, I-3).
  **Hecho:** un informe sensible puede cifrarse hoy a una clave real, publicada.
  **Esfuerzo S.**

*(El fallo del parser en el orden de los nibbles de 0.1 y el hueco de sondeo en la frontera de época UTC
hallado en revisión ya están anotados para los vectores de prueba en 3.2 y el elemento KDF en 2.2.)*

---

## Nivel 1 — Probar o romper la afirmación portante (columna criptográfica)

El diferenciador entero del proyecto es I-2. Estos cuatro elementos, en secuencia,
o lo establecen con rigor o revelan dónde está sobredicho. Nada más
vale la pena construir hasta que esta columna se sostenga.

- **1.1 — Formalizar la composición cifrar-y-luego-Shamir.** `[crítico-para-la-afirmación]`
  Un teorema escrito (o contraejemplo) que enuncie *exactamente* qué es incondicional
  (el texto cifrado está oculto por debajo de `k`, sin hipótesis computacional) y qué
  no lo es (el texto en claro por encima de `k` descansa sobre el AEAD). Confirma que la clave AEAD nunca
  aparece en nada que vea un adversario por-debajo-de-`k`. **Hecho:** una frase precisa
  por cada uno, para el nivel incondicional y el computacional, demostrablemente disjuntos.
  **Esfuerzo M.**

- **1.2 — Probar el umbral sobre todo el secreto, no un byte.** `[crítico-para-la-afirmación]`
  La demo de fuerza bruta de la PoC cubre un *único byte*; las pruebas de propiedad comprueban
  solo una marginal. Prueba la independencia conjunta de cualesquiera `k−1` partes sobre el
  secreto completo (estándar, dados coeficientes uniformes independientes por posición), y añade
  una prueba que fallaría bajo reutilización de coeficientes o un RNG de baja entropía. Documenta
  **«la aleatoriedad de los coeficientes es crítica para el umbral»** como requisito de primera clase.
  **Hecho:** prueba de independencia conjunta citada + una prueba que atrapa el fallo del RNG.
  **Esfuerzo S–M.**

- **1.3 — Etiqueta SP-7: repetición, falsificación, enlazabilidad entre drops.** `[solidez]`
  La propiedad que no debe fallar: dos partes de un mensaje nunca deben llevar un
  valor observable igual a través de drops confabulados. Las partes hacia drops distintos usan
  índices distintos, así que las etiquetas difieren — *prueba* que ningún par `(nonce, índice)` se
  reutiliza nunca entre drops, o arréglalo. Además: reglas de propiedad del nonce (un
  `msg_nonce` reutilizado a la vez colisiona etiquetas y rompe el AEAD de forma catastrófica), y
  defensas de repetición/desalojo en la capa de almacenamiento. **Hecho:** bosquejo de prueba de etiqueta-no-igual,
  disciplina de nonce escrita en SP-7, repetición gestionada en el drop. **Esfuerzo M–L.**

- **1.4 — Unificar la disciplina de derivación de claves del rendezvous.** `[solidez]`
  Hoy `K_tag` proviene de HKDF-BLAKE2s pero `box_id` de BLAKE2s con clave crudo, ambos
  sobre el mismo `kpair` — sin principio. Deriva un PRK maestro de `kpair`, y luego
  subclaves separadas por etiqueta. Especifica la **regla de gracia en la frontera de época UTC** (un
  remitente que deposita a las 23:59 y un destinatario que sondea a las 00:01 no deben perder correo —
  un bug de entrega real). Justifica el ancho de 16 bytes de `box_id`. **Hecho:** una disciplina
  KDF, la regla de gracia de época, vectores regenerados. **Esfuerzo M.**

---

## Nivel 2 — El problema central de la red (OP-1) y su aparato

El umbral solo es *operativamente* real si las `n` rutas son genuinamente disjuntas.
Verificar eso a partir de los propios datos de un cliente — contra relés que mienten sobre
todo salvo sus firmas — es el problema central declarado del proyecto. El
punto honesto más profundo, que los entregables deben enunciar en voz alta: **desde la
superposición no puedes verificar la disjunción *verdadera*, solo la consistencia contra un
conjunto de datos de confianza acotada; un adversario que colocaliza relés mientras anuncia
prefijos disjuntos es probablemente indetectable.** El trabajo es acotar lo que ese
adversario gana, no fingir que no existe.

- **2.1 — Pasada de realismo del simulador.** `[piedra angular]`
  Hoy `network_sim.py` usa etiquetas de AS de *verdad fundamental* — es decir, supone que el
  problema de verificación ya está resuelto. Añade: una **capa de inferencia de AS/jurisdicción
  con error inyectable** (para que «desconocido ⇒ supón compartido» se ejercite),
  **guardias persistentes** a través de un flujo de mensajes (una guardia mala es mala durante meses),
  una **muestra de gossip parcial** por cliente en lugar del pozo con ojo de dios, y un
  **adversario mejorado** (correlación a nivel de AS, el drop contado como un punto de observación de salida,
  confirmación opcional del salto intermedio). **Hecho:** curvas de ruptura y enlace
  en función de la tasa de error de inferencia, mostrando que los números de error-cero de hoy eran
  optimistas. **Esfuerzo L.** Desbloquea casi todo lo de abajo.

- **2.2 — Redactar el procedimiento de verificación de la Parte 3.** `[buque insignia]`
  La expansión que pide la issue OP-1: dada una muestra, un conjunto de datos de inferencia y
  la confianza por relé, produce `n` circuitos **y un certificado comprobable por máquina
  del nivel de disjunción alcanzado, con una confianza** — nunca una
  suposición. Enuncia el límite con honestidad («disjunto bajo el conjunto de datos D con las barras de
  error de D»), y nombra al adversario que juega a la colocalización como un residuo declarado,
  cuantificado por 2.1. **Hecho:** un implementador hostil puede construir el selector a partir
  del texto; cada umbral cita una figura del simulador. **Esfuerzo L.** Depende de
  2.1 y 2.3.

- **2.3 — El conjunto de datos de inferencia IP-a-AS sin confianza.** `[riesgo de investigación]` `I-3`
  Cómo distribuir y autenticar un mapa IP-a-AS (y de jurisdicción gruesa) sin
  una única autoridad: instantáneas reproducibles a partir de datos públicos BGP/RIR, una
  forma de que dos clientes sepan que tienen el *mismo* mapa (direccionamiento por contenido +
  registro de transparencia + raíces difundidas por gossip), y un tratamiento honesto de la paradoja del arranque
  (un cliente nuevo descarga el mapa por rutas que aún no puede evaluar — un
  momento de confianza-en-el-primer-uso). **Costura de fusión:** el conjunto de firmantes del mapa y el
  conjunto de firmantes de la publicación de software (OP-8, elemento 4.1) quizá quieran ser el *mismo*
  mecanismo. **Hecho:** dos clientes honestos tienen demostrablemente el mismo mapa o detectan
  que no; la tasa de error del mapa alimenta la perilla de inferencia de 2.1. **Esfuerzo XL** —
  el resultado honesto puede ser «mapa TOFU + registro de transparencia + gossip de anomalías», no un
  mapa canónico.

- **2.4 — Robustez del descubrimiento: sybil y eclipse (OP-2).**
  Modela la vista muestreada bajo GR-6/GR-8 con fracciones de adversario por clase de fuente,
  rotación, y el tope «ninguna clase > ½»; implementa adversarios de eclipse y sybil;
  comprueba si el «contar solo relés verificados» de PS-10 realmente embota
  la inflación de tamaño por sybil. Luego especifica el protocolo de sondeo de ancho de banda (GR-7) — un
  sondeo que mide un relé sin revelar al sondeador ni convertirse en un amplificador de DoS,
  el reemplazo difícil de la autoridad de ancho de banda de Tor que nos negamos a nosotros
  mismos. **Hecho:** curvas de probabilidad de eclipse e inflación por sybil; una especificación de sondeo
  construible. **Esfuerzo L.**

---

## Nivel 3 — Endurecer las construcciones para una implementación real

- **3.1 — Requisitos criptográficos de la implementación de referencia.** `[solidez]`
  Lo que un nodo real debe hacer y el juguete omite, cada uno atado a una amenaza:
  **GF(2⁸) de tiempo constante** (las búsquedas en tabla de la PoC son un canal de temporización de caché sobre
  los bytes secretos de las partes — una fuga de temporización socavaría el mismísimo umbral que el proyecto
  vende), **disciplina de CSPRNG** (el umbral es exactamente tan fuerte como el RNG de los coeficientes),
  gestión de rotación de nonce/clave a través de reinicios, persistencia de la caché de repetición,
  resistencia al mal uso (la API debe rechazar texto-en-claro-sin-AEAD — cosa que la PoC
  ya hace), y zerorización de memoria. **Hecho:** una lista de verificación atada a amenazas que un
  implementador debe satisfacer. **Esfuerzo L.**

- **3.2 — Vectores de prueba formales y conformidad entre implementaciones.** `I-1`
  Expande `vectors.json` para cubrir toda construcción con clave (PRK de HKDF, ids de buzón
  a través de épocas, la ruta extremo a extremo cifrar→dividir→depositar→sondear→reconstruir→descifrar,
  registros Ed25519 + CBOR canónico, la transcripción del handshake Noise una vez especificado),
  fija las tablas GF como normativas, y **bloquea-con-vector el orden de nibbles de `k,n`**
  (los dos parsers de la PoC discrepaban — ahora arreglado; un vector debe mantenerlos
  honestos). **Hecho:** una segunda implementación en otro lenguaje pasa todos los
  vectores. **Esfuerzo M.** Incremental: añade vectores a medida que cada construcción se asienta.

- **3.3 — Especificar el handshake de circuito (Noise XK) y su secreto hacia adelante.**
  La suite nombra `Noise_XK_25519_ChaChaPoly_BLAKE2s` pero nada lo especifica,
  y Sphinx ya hace acuerdo de claves por salto — así que **¿para qué sirve Noise XK?**
  Resuelve la aparente redundancia (un implementador hostil no puede construir actualmente un
  nodo interoperable, violando I-1), enuncia las propiedades de secreto hacia adelante y
  la ventana de exposición de clave estática de ≤7 días, y decide si el ocultamiento del iniciador
  de XK es siquiera necesario o un patrón más simple basta. **Hecho:** el handshake está
  especificado hasta la completitud de I-1, su relación con Sphinx inequívoca. **Esfuerzo L.**

- **3.4 — Firmas de registro de gossip y CBOR canónico.** `I-1`
  El CBOR canónico es crítico para la firma: dos implementaciones que discrepan en el orden del
  mapa rechazan los registros válidos de la otra. Fija la canonicalización exacta,
  obliga a un perfil estricto de verificación Ed25519, y provee vectores entre implementaciones.
  **Hecho:** canonicalización fijada, vectores existentes. **Esfuerzo S.** Paralelizable.

---

## Nivel 4 — Gobernanza y operaciones (protege el proyecto ahora y a los usuarios después)

Las revisiones coincidieron en un encuadre: el proyecto **aún no tiene usuarios**, lo cual es un
regalo — el esqueleto de gobernanza y confianza de compilación puede asentarse con calma *ahora*,
mientras que cambiarlo no rompe a nadie. El error caro es desplegar un nodo de referencia
con una historia de actualización improvisada y luego necesitar una migración con forma de autoridad para
arreglarlo.

- **4.1 — Gobernanza de actualizaciones sin interruptor de apagado (OP-8).** `[el elemento no-cripto más importante]`
  Un registro de decisión de diseño que fija la *forma*: las compilaciones reproducibles son el ancla
  de confianza; las firmas solo *localizan* una compilación; la adopción de la actualización es local al cliente
  y opcional, nunca un empuje. El 80% difícil es humano, no criptográfico — *quién* firma,
  cómo se eligen y se reemplazan de forma seudónima, y cómo un quórum evita convertirse calladamente
  en la autoridad de directorio que I-3 prohíbe. **La respuesta más fuerte puede ser
  minimalista:** compilaciones reproducibles + hashes publicados de forma cruzada + *sin* autoactualización
  y *sin* conjunto de firmantes autoritativo, porque todo conjunto de firmantes es un objetivo de coacción.
  **Hecho:** el documento sobrevive a una lectura hostil que caza la autoridad de puerta trasera;
  la autoauditoría de I-3 nombra el sustituto no confiable para cada parte. **Esfuerzo L.**

- **4.2 — Tubería de compilación reproducible y cadena de suministro.** `I-1, I-3`
  Diseño (listo para cuando arranque el nodo en Rust): fijado de la cadena de herramientas, una compilación
  hermética o al estilo Nix, un `rebuild-and-compare` que un desconocido pueda ejecutar, atestaciones
  publicadas de forma cruzada, un árbol de dependencias mínimo y vendorizado, y la reconciliación explícita de
  «los colaboradores deben ser seudónimos (sin claves de firma vinculadas a identidad)» con «verifica el
  artefacto» — toda la confianza fluye por la reproducibilidad, ninguna por la identidad del autor.
  **Hecho:** dos partes en máquinas distintas producen artefactos de hash idéntico a partir del
  código etiquetado, mediante un procedimiento que no nombra ningún singleton confiable. **Esfuerzo L.**

- **4.3 — Economía de los dead-drops y metadatos de recuperación (OP-9).**
  Simula un ataque de inundación con un precio (puzzles de cliente vs los topes RZ-7),
  honesto sobre el hueco de que un puzzle lo bastante duro para disuadir a una botnet puede ser
  inasequible en el teléfono barato al que el proyecto dice servir. Simula la
  disciplina de sondeo (RZ-9) contra un drop que *perfila* un buzón, y su coste en
  móvil con tarifa por volumen. **Hecho:** parámetros defendidos con el residuo enunciado en
  números. **Esfuerzo M.**

- **4.4 — Exposición del operador y la postura de neutralidad.** `[políticamente delicado]`
  Un informe honesto (no asesoría legal) sobre lo que revela y arriesga ejecutar cada rol,
  apoyándose en la afirmación verdadera de que un drop almacena ruido ilegible y un relé
  reenvía ruido de tamaño fijo sin salida a la web abierta; más una postura escrita de manejo de abusos —
  qué hará y qué no hará el proyecto cuando la red se use para
  dañar, dado que *no puede* leer ni apuntar al contenido por diseño, y por qué esa
  incapacidad es una propiedad de seguridad, no una evasión. **Hecho:** cada rol tiene una
  declaración de exposición en lenguaje llano; la postura es consistente con la cláusula de
  neutralidad y no introduce palanca de moderación alguna. **Esfuerzo M.**

---

## Nivel 5 — Las capas aún sin escribir

- **5.1 — Transportes camaleón (Parte 4, OP-7).** `[carrera armamentística]`
  Un modelo de amenazas del transporte y una evaluación honesta de realismo: deriva de la huella uTLS,
  la realidad de despliegue de ECH en 2026, el sondeo activo, la correlación de flujo. El
  argumento económico de «bloquearme cuesta más de lo que rinde» tiene contraejemplos históricos
  reales — nómbralos, y haz la pregunta incómoda de si un proyecto de voluntarios
  seudónimo tiene la capacidad de *mantenimiento sostenido* que una carrera armamentística
  exige. Resuelve si la dispersión de partes a través de coberturas diversas *ayuda* (más tipos de
  cobertura) o *perjudica* (más huellas que equivocar). **Esfuerzo L.**

- **5.2 — Diversidad de enlaces en apagón / malla mixta (Parte 5, OP-6).** `[riesgo de investigación]`
  El mayor diseño sin escribir: teléfonos como hojas atadas a batería,
  PCs/SBCs de doble radio como columna 802.11s, y **dispersión a través de pasarelas independientes**
  que extiende I-3 a la salida del vecindario físico. Las partes difíciles: direccionamiento
  sin alcanzabilidad global; verificar la independencia de las pasarelas cuando el mapa de AS es
  inalcanzable dentro de un apagón y la ubicación es autodeclarada (OP-1 reaparece en
  el espacio radio); si el paquete Sphinx de 2048 bytes sobrevive a horas de
  store-and-forward o necesita su propio encuadre. Y el residuo irreducible que
  enunciar, no resolver: **un nodo de malla en un apagón candente es un acto físicamente localizable**
  que ninguna superposición puede ocultar — así que la participación en la malla es siempre una participación
  explícitamente aceptada. **Esfuerzo XL.**

---

## El mismo problema con tres máscaras

Un hallazgo reapareció en las tres revisiones y merece ser nombrado: la
incapacidad de **verificar la independencia de una parte sin autodeclaración** aparece
para los *relés* (OP-1 disjunción de rutas), para los *firmantes de publicación* (OP-8 diversidad
jurisdiccional) y para las *pasarelas de malla* (OP-6 independencia física). Una solución a
uno puede transferirse a los otros. Es, podría decirse, el problema abierto más profundo de
todo el proyecto — y la respuesta honesta en cada caso puede ser un *residuo acotado y declarado*
en lugar de una verificación. Eso es consistente con la regla por encima de
todas las demás aquí: **enuncia dónde termina el paraguas.**

---

## Camino crítico sugerido

**Ahora:** Nivel 0 (0.1–0.4) — corrige las afirmaciones excesivas conocidas y la clave que falta.
**Luego la columna:** 1.1 → 1.2 → 1.3 → 1.4 (probar o romper I-2), con 0.2 (el
AEAD e2e) plegado dentro, ya que desbloquea la demo de composición real.
**Luego en paralelo:** 2.1 (piedra angular del simulador) y 2.3 (el conjunto de datos XL, empezado
pronto) → 2.2 (verificación buque insignia de la Parte 3); 4.1 (gobernanza) y 4.2
(compilaciones reproducibles) pueden avanzar de forma independiente en cualquier momento.
**Cierre:** 2.4, endurecimiento del Nivel 3, economía del Nivel 4, y luego los Niveles no escritos
5.1 y 5.2.

Dos elementos cargan una posibilidad real de un resultado *parcial o negativo* — 2.3 (los datos BGP
reproducibles sin confianza quizá no sean plenamente alcanzables) y 5.2 (una malla que preserve los
invariantes quizá solo sea parcialmente alcanzable). Eso no es razón para aplazarlos; es la
razón para ser honestos sobre ellos en un documento que no promete actos de fe.
