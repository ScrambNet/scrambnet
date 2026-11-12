# Operar un nodo ScrambNet — la exposición y la postura de neutralidad

> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../en/OPERATORS.md)).

**Operar cualquier nodo ScrambNet es un acto visible y deliberado con un riesgo
real y no nulo.** Este documento es honesto al respecto. Lo que sigue te dice qué
revela cada rol y qué es demostrablemente incapaz de revelar, para que puedas
decidir. Es una declaración técnica y de postura, **no asesoramiento legal**:
este proyecto es seudónimo y no puede conocer tu jurisdicción, tu adversario ni
tu ley. Donde lo que está en juego lo justifique, busca tu propia asesoría.

Este es un informe informativo, no una parte normativa de la especificación. Se
apoya en afirmaciones que la especificación ya hace — los invariantes `I-1…I-4`,
las reglas del dead-drop (Part 6), los residuales de selección de rutas (Part 3),
los residuales del conjunto de datos de inferencia (Part 8) — y los señala en
lugar de reformularlos. Donde la especificación declara un residual abiertamente,
este informe también lo lleva abiertamente; no lo suaviza.

## Qué ve cada rol, y qué no puede ver

Cada afirmación tiene la misma forma: **qué ve el rol · qué es demostrablemente
incapaz de ver, y el límite exacto de esa afirmación · el residual honesto.** Los
roles son los que define la arquitectura («Quién opera qué»); nada de lo que hay
aquí inventa un rol que la red no tenga.

### Cliente puro

Como cliente eres el rol de menor exposición — «casi invisible», cabalgando sobre
puentes y transportes camaleón — pero **no de exposición nula**, y este informe no
pretenderá lo contrario. Tu **guardia** (tu primer salto) ve tu dirección IP real
y cuándo estás activo (ver abajo); esa es una exposición del lado del cliente, no
meramente una propiedad del guardia. La recuperación también tiene un coste
permanente y una superficie de metadatos: un cliente sondea sus drops en un
calendario fijo obligatorio (`RZ-9`), ~212 MB/month a través de cuatro drops antes
de que envíes nada (`RZ-16b`), y ese calendario — no el contenido — es observable.
Eres de baja exposición; no eres invisible.

### Guardia (el primer salto de un cliente)

Un guardia es el único relé que ve la dirección IP real de un cliente y la
temporización de su actividad. Si operas un guardia, aprendes que una IP concreta
te habló en ScrambNet, y cuándo. **No** aprendes adónde iba ese tráfico ni qué
contenía: por `I-4` cada paquete que te cruza es ruido de tamaño fijo
indistinguible de bytes aleatorios uniformes, y sostienes solo una parte de un
mensaje que viaja por una de varias rutas.

El límite exacto de «no puedes reconstruir el mensaje». El suelo de contenido
(`I-2`) es incondicional **por debajo de `k` posiciones capturadas**: sostén menos
de `k` partes y son ruido en sentido de teoría de la información, sin escape
computacional ni cuántico. Pero *alcanzar* ese suelo depende de que las `n` rutas
sean genuinamente **disjuntas**, y la disjunción es **inferida, no demostrada**
(`OP-1`; `PS-11`, «la disjunción creída no es disjunción real»). Un mapa elegido y
hostil puede *dirigir* los relés de un adversario hasta su posición y llevar la
captura de contenido «de ~0% a 100% con ~15% de propiedad» (`PS-12`/`ID-8a` — un
hallazgo que el proyecto lleva abiertamente tras romperse una exageración
anterior). Así que la afirmación honesta no es «un guardia no puede reconstruir»,
sin más; es «ninguna coalición reconstruye **por debajo de `k` posiciones
capturadas**, y que tus rutas alcancen realmente ese suelo es una propiedad no
verificada que un adversario que dirige puede vencer por encima de un umbral».

**El residual honesto:** sí ves IPs de clientes. Esa es la exposición más aguda de
cualquier rol de relé, y es estructural, no una fuga que haya que arreglar. Las IPs
de la gente que usa ScrambNet pasan por tu nodo y son visibles para cualquiera que
pueda observar sus conexiones.

### Relé intermedio

Un relé intermedio no ve ninguno de los dos extremos. Por la construcción Sphinx y
`I-4` no puede saber si su predecesor es el cliente originario u otro relé, ni si
su sucesor es el último salto. No ve ninguna IP de cliente (esa es la posición del
guardia), ningún destino, ningún contenido; sostiene una parte cifrada. Es el rol
de relé de menor información — ruido que pasa entre otras dos máquinas. Su
exposición es la general que comparte cada rol (abajo): operarlo es un acto
visible, y reenvía tráfico que no puedes inspeccionar.

### Drop (almacenamiento dead-drop, Part 6)

Un drop almacena las partes depositadas en buzones y las sirve cuando se le
sondea. Lo que almacena es, por `I-2`, ilegible en sentido de teoría de la
información: cada parte almacenada está por debajo de `k` e indistinguible de ruido
aleatorio para cualquiera — **incluido tú, el operador** — sin las otras partes,
que están en otros drops que no controlas (`RZ-5`: ningún drop sostiene jamás dos
partes de un mismo mensaje; el conjunto de drops es `d = n = 4`, `k = 3`, así que
un drop sostiene exactamente una parte, `< k`). No puedes leer lo que almacenas, no
puedes distinguir el contenido de dos buzones, y no puedes enlazar un depósito con
un remitente (`RZ-2`/`RZ-10`, `SP-7`). Esta afirmación es exacta y no se suaviza:
un operador de drop es genuinamente ciego al contenido.

**Ser ciego al contenido no es lo mismo que ser neutral en la entrega, y este es el
residual honesto.** Un drop ve **temporización**: la cadencia pública de sondeo
(`RZ-9`) y los tiempos de depósito en los buzones que sostiene, dentro de una
época; un drop que sostiene varios buzones puede correlacionar las *marcas de
tiempo* de depósito entre ellos incluso bajo independencia de sondeo perfecta
(`RZ-16`/`OP-9`, llevado abiertamente en la especificación de rendezvous §9). Y un
drop *puede* denegar la **entrega** sin leer nada: el desalojo del más viejo primero
más la ventana de recuperación de 8-slot significan que un inundador — incluso un
teléfono barato — puede enterrar correo honesto más allá de la ventana en ~17
segundos (`RZ-15`), un residual de inundación de entrega que la especificación
declara que aún no tiene defensa suficiente (`OP-9`). Así que: almacenas ruido
ilegible, pero observas *que* ese ruido llegó y fue recogido y cuándo, y las
mecánicas de almacenamiento son una superficie de entrega. Esa exposición de
temporización-y-entrega es el residual genuino del drop, declarado, no oculto.

### Puente (punto de entrada distribuido por el grafo social)

Un puente es un punto de entrada entregado de persona a persona allí donde la red
abierta está bloqueada (niveles de confianza al estilo Lox). Ve información de nivel
guardia para los clientes que lo alcanzan (su IP, nada aguas abajo). Su exposición
distintiva es **ser descubrible como puente**: un censor que logra hacerse pasar por
un usuario puede aprender la dirección de tu puente y bloquearla u observarla. La
distribución por el grafo social limita la rapidez y la amplitud con que se filtra
una dirección — «un censor puede hacerse pasar por un usuario; no puede hacerse
pasar por el amigo de todos» — pero no hace que un puente sea indescubrible.

**El residual honesto:** operar un puente significa que una dirección tuya está, por
diseño, circulando entre desconocidos-de-desconocidos, algunos de los cuales pueden
ser adversarios. La resistencia a la enumeración es una carrera armamentística que
el modelo de amenazas llama sostenible, no ganada.

### Nodo de malla / pasarela (capa de apagón)

Un nodo de malla reenvía dispositivo a dispositivo sobre Wi-Fi Direct / Bluetooth
durante un apagón; una pasarela puentea la malla de vuelta a internet cuando existe
una ruta. Su exposición de contenido es la misma que la de cualquier relé — partes
de tamaño fijo que no puede leer (`I-2`/`I-4`). Su exposición distintiva es **física
y local**: su visibilidad es una señal de radio a escala de barrio, correlacionable
con una ubicación y potencialmente con una persona, precisamente cuándo y dónde un
adversario ha apagado internet y está más motivado. Por eso la arquitectura la hace
siempre una participación explícitamente aceptada. Una **pasarela** carga *ambas*
exposiciones a la vez: la exposición física/local del lado de la malla, **y** la
exposición ordinaria de relé de su lado de internet — su IP de cara a internet es un
nodo ScrambNet observable para su propio ISP — sin ser nunca, aun así, una salida a
la clear-web (abajo).

**El residual honesto:** de todos los roles este es el que cambia la
ceguera-al-contenido más fuerte por el anonimato-del-operador más débil. Los bytes
son ruido; el transmisor está en un lugar. Ningún invariante protege la
localizabilidad física de una radio.

### La salida a la clear-web que no existe

ScrambNet **no tiene rol de salida a la clear-web**, y esto es lo que más importa a
los operadores. La salida a la clear-web es el rol más expuesto de Tor: la IP de una
salida de Tor aparece como la fuente aparente de lo que sea que sus usuarios envían
a la internet abierta, y ese operador recibe las quejas por abuso, los avisos de
retirada y la atención de las fuerzas del orden por tráfico que ni eligió ni puede
ver. ScrambNet no tiene equivalente. El salto terminal de un mensaje entrega una
parte en un dead-drop (Part 6) — ruido ilegible en almacenamiento interno del
proyecto — no hacia afuera a un host de terceros arbitrario. **La dirección de
ningún nodo ScrambNet aparece como el origen de tráfico atribuible que llega a un
servicio externo** (la pasarela de malla toca internet, pero lleva ruido interno de
ScrambNet hacia un relé, no el tráfico de un usuario hacia afuera a un host de la
clear-web). Por eso la arquitectura afirma que la exposición de un operador de
relé/drop es «estructuralmente más baja que la de una salida de Tor» — una
comparación de exposición **técnica**, nunca una afirmación sobre tu responsabilidad
legal. Dicho con precisión: esto elimina la exposición *específica* del nodo de
salida; **no** hace ningún rol libre de riesgo, y no convierte a ScrambNet en un
proxy de salida — estructuralmente no lo es, y esa ausencia es una característica,
también para ti.

### Operar más de un rol

La mayoría de las afirmaciones anteriores describen un solo rol en aislamiento. Una
misma máquina comúnmente opera varios — guardia, relé y drop juntos — y la
co-ubicación crea correlaciones que ninguna de las afirmaciones de rol único
muestra. Un drop que sostiene varios buzones correlaciona la temporización de
depósito entre ellos (`RZ-16` §9); un relé que es **también un usuario** y está «en
línea exactamente cuando su operador chatea es un ataque de intersección contra sí
mismo» (la arquitectura lo nombra directamente). La disciplina que la arquitectura
prescribe es la mitigación: un calendario siempre activo independiente de tu propio
uso, de modo que tu tiempo en línea no diga nada sobre tu actividad. Si operas más
de un rol, tu exposición no es el mínimo de los roles — es su combinación.

## La postura ante el abuso

Esta es la parte que un lector hostil pondrá a prueba con más dureza, así que cada
frase está construida sobre una incapacidad verdadera, y ninguna introduce una
palanca.

**(a) La incapacidad, enunciada como una propiedad de seguridad.** ScrambNet es
incapaz de leer, identificar, apuntar a, o bloquear o priorizar de forma selectiva
por contenido cualquier mensaje, usuario o contenido. Esto no es una política que
adoptemos y pudiéramos revertir; es una propiedad del diseño. Un drop almacena
partes que son ilegibles en sentido de teoría de la información por debajo de `k`
(`I-2`); un relé reenvía ruido de tamaño fijo que no puede distinguir de ningún otro
(`I-4`); no hay registro de usuarios (no hay alta), ni autoridad de directorio, ni
parte privilegiada en ningún punto del protocolo (`I-3`). El proyecto no tiene
clave, ni interruptor, ni posición en la red desde la cual el contenido *pudiera*
inspeccionarse o filtrarse. La misma matemática protege a todos porque es incapaz de
distinguir a nadie, y esa indiscriminación es lo que hace fiable la protección: una
red que *pudiera* elegir bando es una red que un adversario poderoso podría *hacer*
elegir bando. (Una nota honesta de alcance: la ceguera al contenido no es
neutralidad en la entrega — las mecánicas de almacenamiento de un drop son una
superficie de entrega, `RZ-15` — así que «no puede bloquear» aquí significa *no
puede bloquear de forma selectiva por contenido*, que es la propiedad que importa
para la neutralidad.)

**(b) Lo que el proyecto genuinamente sí puede hacer.** Lo que podemos hacer, lo
hacemos en abierto: publicar el diseño completo para que cualquiera pueda
estudiarlo, atacarlo o reimplementarlo (`I-1`); recibir y actuar sobre reportes de
**vulnerabilidad** bajo la política de seguridad (SECURITY.md); corregir defectos; y
seguir diciendo con claridad qué protege la red y qué no protege. Esa es la lista
entera. Nada de ello implica mirar, buscar o actuar sobre el tráfico de nadie,
porque el diseño no nos da forma de hacerlo — y el canal de vulnerabilidad es para
defectos en el diseño y el código, nunca un canal para reportar tráfico o usuarios,
porque no hay nada que pudiéramos hacer con tal reporte y su existencia no debe dar
a entender lo contrario.

**(c) Lo que el proyecto se niega a construir, y por qué.** No construiremos una
capacidad de moderación, una puerta trasera de reportes, un filtro de contenido, una
lista de bloqueo de usuarios, un acceso «legal» pinchable, ni ningún otro mecanismo
que permita al proyecto, a un operador, o a cualquier otro leer, apuntar a o suprimir
contenido o usuarios. Nos negamos no por indiferencia al daño sino porque tal
mecanismo es contraproducente en sus propios términos. Cualquier palanca que pueda
apuntarse a contenido llamado «abuso» es la misma palanca, apuntada al revés,
dirigida a contenido llamado «disidencia» — es una sola capacidad, y quien pueda
obligar a su uso decide a qué apunta. Sería precisamente el único punto de control
que `I-3` prohíbe y la elección de bando que el modelo de amenazas deja fuera de
alcance. En el momento en que tal palanca existe, la promesa de la red es falsa para
todos, incluidas las personas para quienes se construyó; el adversario ya no tiene
que romper la matemática, solo apoderarse de la palanca. La ausencia de un mecanismo
de moderación no es un hueco que no logramos llenar — es una propiedad de seguridad
portante que nos negamos a destruir. (Cualquier control de admisión frente a la
inundación que el proyecto llegue a adoptar — la cuestión abierta `OP-9` que `RZ-15`
deja sin resolver — DEBE ser ciego al contenido y ciego a la identidad por
construcción, y el candidato principal filtra por posesión de una tarjeta de
contacto por relación, no por punto de vista; una regla de admisión que tuviera que
*identificar a un remitente* o *inspeccionar un depósito* sería una palanca y está
prohibida bajo esta misma postura.)

**(d) El coste honesto.** Esto no es gratis, y no pretenderemos lo contrario. Una red
que no puede elegir bando tampoco puede elegir *contra* el daño. ScrambNet puede
usarse para cosas que sus autores encuentran repugnantes, y el proyecto es incapaz de
impedirlo por diseño. Las analogías habituales — el sistema postal no puede leer cada
carta, una red telefónica no puede escuchar en busca de llamadas «malas», TLS no puede
negarse a cifrar la conexión de un criminal — llevan la forma del argumento pero lo
**subestiman**, y la diferencia es la afirmación entera: los extremos del correo, el
teléfono y TLS *pueden* ser obligados por orden judicial a interceptar un objetivo
concreto, porque existen un punto de observación y una clave. El «no puede» de
ScrambNet es **más fuerte** — no hay posición desde la cual un operador coaccionado
*pudiera* entregar contenido por debajo de `k` (`I-2`), ni parte única a la que
*pudiera* ordenarse publicar una vista envenenada de la red (`I-3`; la especificación
nombra directamente la realidad «coaccionado, requerido judicialmente o incautado»).
Las protecciones son indiscriminadas porque la protección selectiva no es protección
— es una lista de quién tiene permiso de estar a salvo, en manos de quien sostiene la
pluma. Aceptamos el coste con los ojos abiertos: una herramienta lo bastante potente
para proteger a los que no tienen poder de los que sí lo tienen no puede venir con un
interruptor que los poderosos puedan accionar. El resumen honesto no es «ScrambNet
previene el abuso». Es: **ScrambNet protege la comunicación, y esa protección no viene
con un kill switch — para nadie, contra nadie, incluidos nosotros.**

## Dónde estás expuesto de todos modos

Dicho con claridad y dejado en pie — ningún «pero no te preocupes», ninguna seguridad
implícita.

- **Operar cualquier nodo es un acto visible.** Un relé publica una dirección; un
  puente hace circular una; un nodo de malla emite una señal de radio. La matemática
  protege el *contenido y el enlace del tráfico*, no el *hecho de que tu máquina está
  en la red*. Si ser visto operando infraestructura de anonimato es en sí mismo tu
  riesgo, ningún invariante lo elimina.
- **Un guardia ve IPs de clientes.** Estructural, no un error. Las IPs de usuarios de
  ScrambNet pasan por tu guardia y son visibles para cualquiera que pueda observar sus
  conexiones.
- **Un drop ve temporización y modela la entrega.** Contenido ilegible, sí — pero los
  tiempos de depósito y sondeo dentro de una época, la correlación de temporización de
  depósito entre buzones, y la superficie de entrega de desalojo/inundación son
  residuales reales, declarados (`RZ-15`/`RZ-16`/`OP-9`).
- **Un puente es descubrible.** Por diseño se entrega a desconocidos; algunos pueden ser
  adversarios. La resistencia a la enumeración es una carrera armamentística, no una
  garantía.
- **Un nodo de malla es físicamente localizable.** Los bytes son ruido; el transmisor
  está en un lugar, precisamente cuando un adversario ha apagado internet.
- **Alcanzar el suelo de contenido depende de una disjunción que no puedes verificar.** El
  suelo `I-2` por debajo de `k` es incondicional; que tus rutas o drops sean
  verdaderamente independientes es inferido, no demostrado (`OP-1`/`PS-11`), y un mapa
  que dirige puede vencerlo por encima de un umbral (`PS-12`). Opera sabiéndolo.
- **Tu ley local puede obligarte al margen de qué sean los bytes.** Este proyecto es
  incapaz de decirte qué puede exigirte una autoridad, y no pretenderá que la ceguera al
  contenido de la red sea un escudo legal — es un hecho técnico sobre los bytes, no una
  conclusión legal específica de una jurisdicción. Que un drop *no pueda* leer lo que
  almacena es cierto y puede importar, o puede que no, según una ley que este proyecto
  seudónimo no puede conocer. **Aquí es donde necesitas tu propia asesoría, no la
  nuestra.** Enunciamos qué se revela técnicamente; lo que significa para ti, legalmente,
  te toca a ti averiguarlo.
