# Especificación de ScrambNet — Parte 7: El argumento de seguridad para I-2
> **Traducción informativa.** La versión canónica y normativa es la inglesa ([en](../../en/spec/07-security-argument.md)).

**Estado: BORRADOR (DRAFT).** Esta parte demuestra, o acota, la única afirmación sobre la que descansa todo lo demás: el umbral incondicional del contenido (I-2). Es normativa donde enuncia un requisito (`SA-n`) y expositiva en lo demás. Si el argumento de aquí es erróneo, el proyecto es erróneo, y la forma más rápida de descubrirlo es atacar *este fichero*.

La afirmación es deliberadamente estrecha. Lee primero las dos frases del §1; todo lo que sigue es su justificación y su precio.

## 1. Qué se demuestra, en dos frases

- **Nivel incondicional (el umbral).** Un adversario que observa cualesquiera `k−1` de las `n` partes de un mensaje no aprende **nada** sobre el texto cifrado de extremo a extremo — no "nada factible", sino nada en absoluto, frente a cómputo ilimitado y cualquier computadora cuántica futura — porque las `k−1` partes son *estadísticamente independientes del secreto* (Shamir, demostrado en §3).
- **Nivel computacional (el cinturón).** Un adversario que obtiene `k` o más partes reconstruye el texto cifrado y luego se enfrenta al AEAD de extremo a extremo; a partir de ahí, la confidencialidad del contenido es exactamente la confidencialidad de ChaCha20-Poly1305 bajo una clave que el adversario no posee (SP-1a), lo cual **sí es** una hipótesis computacional.

Estos dos niveles son **disjuntos y exhaustivos**: todo adversario posee o bien `< k` partes (nivel 1) o bien `≥ k` (nivel 2), y la garantía de cada uno se enuncia sin referencia al otro. El resto de esta parte demuestra el nivel 1 de forma rigurosa, enuncia con precisión por qué el nivel 2 no puede ser incondicional, y fija el único punto donde los dos niveles podrían filtrarse uno en el otro (§4: la clave AEAD debe ser invisible por debajo de `k`).

```
  LOS DOS NIVELES, SEGÚN CUÁNTAS PARTES POSEE EL ADVERSARIO

   partes poseídas:  0 ............ k-1  │  k ........... n
                     └──── NIVEL 1 ────┘ │ └──── NIVEL 2 ────┘
                                         │
   NIVEL 1  (por debajo de k)            │   NIVEL 2  (k o más)
   ──────────────────────────            │   ──────────────────
   las k-1 partes son                    │   el adversario reconstruye C,
   ESTADÍSTICAMENTE INDEPENDIENTES       │   luego se topa con el AEAD de
   del secreto (SA-1, SA-2)              │   extremo a extremo bajo la clave K
          │                              │          │
          ▼                              │          ▼
   no hay nada ahí que aprender,         │   confidencialidad = ChaCha20-
   frente a cómputo ILIMITADO            │   Poly1305 bajo K que el adversario
   y cualquier computadora cuántica      │   no posee (SP-1a)
          │                              │          │
          ▼                              │          ▼
   INCONDICIONAL (el umbral)             │   COMPUTACIONAL (el cinturón)

   La junta (SA-4): K nunca aparece en nada que vea un adversario por debajo
   de k. Eso es lo que impide que el nivel 1 decaiga silenciosamente en el
   nivel 2 — el umbral oculta C, y el adversario tampoco gana nada hacia K
   para un C futuro.
```

## 2. Modelo y adversario

- Un **mensaje** es una cadena de bytes `M`. El emisor calcula primero el texto cifrado `C = AEAD-Seal(K, N, M)` (SP-1a), donde `K = HKDF(kpair, "e2e-content")` y `N` es el nonce del mensaje. `C` — nunca `M` — es lo que entra en la dispersión.
- La dispersión es Shamir `(n, k)` sobre GF(2⁸), **por byte**: para la posición de byte `j`, el byte secreto `c_j` es el término constante de un polinomio independiente y uniformemente aleatorio de grado `(k−1)`, `f_j`, y la parte `i` en la posición `j` es `f_j(i)` para puntos de evaluación distintos y no nulos `x_1,…,x_n ∈ GF(2⁸)\{0}` (los índices de parte). "Independiente, uniforme" carga el peso y es en sí mismo un requisito (SA-3, más abajo).
- El **adversario por debajo de `k`** ve: cualesquiera `k−1` partes completas (cada posición de byte de esos `k−1` índices), más todo lo público — la especificación, los puntos de evaluación, `n`, `k`, los bytes de cable de otros paquetes. **No** ve `K`, `N`, ni ninguna parte más allá de sus `k−1`. Dispone de cómputo ilimitado.
- Demostramos una propiedad de `C` (el texto cifrado). Lo que el adversario quiere en última instancia es `M`; el §4 muestra que el resultado a nivel de `C` se transfiere a `M` porque `K` no está en la vista del adversario.

## 3. El umbral: cualesquiera `k−1` partes son independientes del secreto (nivel 1)

**SA-1 (secreto perfecto por byte).** Fijemos una posición de byte `j`. Sea el byte secreto `s = c_j` y el polinomio `f_j(x) = s + a_1 x + … + a_{k−1} x^{k−1}` con `a_1,…,a_{k−1}` independientes y uniformes sobre GF(2⁸). Para cualquier conjunto de `k−1` puntos distintos y no nulos `x_{i_1},…,x_{i_{k−1}}` y cualesquiera valores objetivo `y_1,…,y_{k−1}`:

> el número de tuplas de coeficientes `(a_1,…,a_{k−1})` consistentes con `f_j(x_{i_t}) = y_t` para todo `t` es **exactamente uno, para cada candidato `s`**.

*Demostración.* Fijemos `s`. Las `k−1` ecuaciones `f_j(x_{i_t}) = y_t` son lineales en las `k−1` incógnitas `a_1,…,a_{k−1}`; su matriz de coeficientes es la matriz de Vandermonde sobre los puntos distintos y no nulos `x_{i_t}` (columnas `x, x², …, x^{k−1}`), que es invertible sobre el cuerpo. Así que para cada `s` hay exactamente una solución. Por tanto `Pr[partes = (y_1,…,y_{k−1}) | secreto = s]` es la misma (`= 1 / 256^{k−1}`) para cada `s`: las partes son **independientes de `s`**. ∎

Esta es la enumeración que la PoC ejecuta por fuerza bruta para `k = 3` (`poc/dispersal.py`, `floor_demo()` — los 256 bytes candidatos resultan igualmente consistentes, de exactamente una forma cada uno). SA-1 es el enunciado general de lo que esa demostración comprueba para un caso.

**SA-2 (el secreto entero, no un byte — independencia conjunta).** Sea el texto cifrado `C = c_1 c_2 … c_L` (los `L` bytes). El emisor extrae las tuplas de coeficientes para las `L` posiciones **de forma independiente** (SA-3). Entonces la vista completa de `k−1` partes — las cadenas de bytes de longitud `L` mantenidas en `k−1` índices — es *conjuntamente* independiente de `C`:

> `Pr[vista = v | C = c]` es idéntica para cada `c ∈ (GF(2⁸))^L`.

*Demostración.* La vista factoriza sobre las posiciones: los bytes que el adversario ve en la posición `j` dependen solo de `(c_j, a^{(j)}_1,…,a^{(j)}_{k−1})`, y entre posiciones las extracciones de coeficientes son independientes (SA-3). Así que `Pr[vista = v | C = c] = ∏_{j=1}^{L} Pr[vista_j = v_j | c_j]`, y por SA-1 cada factor es igual a `1/256^{k−1}` con independencia de `c_j`. El producto es por tanto `1/256^{(k−1)L}` para **cada** `c`. La independencia de `C` se sigue. ∎

SA-2 es el paso que las pruebas antiguas de la PoC **no** cubrían: `floor_demo()` es un byte y las pruebas estadísticas comprobaban solo una marginal (la distribución de una posición). El argumento del producto sobre las posiciones es lo que convierte el umbral en una afirmación sobre el *mensaje*, y se sostiene **solo porque** los coeficientes por posición son independientes — que es exactamente el modo de fallo que SA-3 vigila.

**SA-3 (la aleatoriedad de los coeficientes es crítica para el umbral). [normativo]** Los coeficientes del polinomio `a^{(j)}_t` DEBEN (MUST) extraerse de un RNG criptográficamente seguro, de forma independiente tanto en el índice de coeficiente `t` como en la posición de byte `j`. El umbral es exactamente tan fuerte como esta aleatoriedad y no más:

- **La reutilización entre posiciones** (p. ej. una tupla de coeficientes reutilizada para cada byte, o un flujo de claves corto y repetido de coeficientes) rompe la independencia de SA-2: la factorización falla, las `k−1` partes se vuelven *correlacionadas* con `C`, y un adversario puede obtener información sobre `C` correlacionando posiciones entre sí. Un umbral construido sobre coeficientes reutilizados no es un umbral.
- **Un RNG de baja entropía** (un generador débil o predecible) colapsa la extracción uniforme de SA-1: si el adversario puede predecir o enumerar la distribución de coeficientes, el recuento de "exactamente una tupla consistente por `s`" deja de ser uniforme sobre `s`, y las partes filtran.

Este es el requisito de implementación más importante de toda la especificación. Es barato de satisfacer y catastrófico de errar, y a diferencia de una debilidad del AEAD no puede arreglarse rotando una clave más tarde — un mensaje dividido bajo coeficientes malos queda comprometido para siempre. Una implementación conforme DEBE (MUST) tratar el RNG de los coeficientes como su componente de mayor garantía (véanse también los requisitos de criptografía de referencia, roadmap 3.1).

## 4. La junta: la clave AEAD debe ser invisible por debajo de `k` (sin filtración entre niveles)

SA-2 demuestra que las `k−1` partes son independientes del **texto cifrado `C`**. El adversario quiere el **texto en claro `M`**. El puente es que `M = AEAD-Open(K,N,C)` y el adversario por debajo de `k` no posee `K`. Esto solo es cierto si `K` nunca aparece en nada que ese adversario vea — lo cual es un requisito, no una coincidencia:

**SA-4 (separación de claves a través del umbral). [normativo]** Ningún valor derivable por un adversario por debajo de `k` puede revelar `K = HKDF(kpair, "e2e-content")` ni `kpair`. En particular:

- `K` NO DEBE (MUST NOT) colocarse en ninguna parte, etiqueta o campo de paquete. (En este diseño no lo está: `K` se usa solo en los extremos, para sellar y abrir `C`; las partes llevan bytes de `C`, y la etiqueta SP-7 se deriva de una clave *separada por etiqueta* `HKDF(kpair, "tag")`, no de `K` — véanse §5 y SP-7a.)
- Por tanto, la vista de un adversario por debajo de `k` es independiente de `C` (SA-2) **y** no lleva información sobre `K`. No puede ni leer `C` (no hay nada ahí) ni obtener `K` para atacar un `C` futuro. Los dos niveles no se filtran uno en el otro.

Si se violara SA-4 — si cualquier valor observable por debajo de `k` fuera una función de `K` — el umbral seguiría ocultando *este* `C`, pero el adversario podría cosechar `K` y leerlo en cuanto obtuviera más tarde `k` partes, o leer *otros* mensajes bajo la misma `K`. SA-4 es lo que impide que el nivel incondicional se vuelva silenciosamente computacional.

## 5. Por qué el nivel 2 es computacional, dicho con honestidad

Con `k` o más partes el adversario reconstruye `C` exactamente (interpolación de Lagrange — esta es la ruta *prevista*, es como el destinatario lee el correo). A partir de `C`, la confidencialidad de `M` es precisamente la confidencialidad de ChaCha20-Poly1305 bajo `K`. Eso es una hipótesis computacional: en principio puede romperse por criptoanálisis del cifrador. **No** la rompe una computadora cuántica futura vía Shor, porque `K` proviene de un secreto *simétrico* precompartido sin transcripción Diffie-Hellman que invertir (SP-1a); Grover cuesta como mucho una reducción a la mitad de la longitud efectiva de la clave, de ahí la recomendación de ≥256 bits. Así que el enunciado honesto del nivel 2 es: *tan fuerte como un AEAD simétrico bajo una clave que el adversario no tiene, y no más* — una garantía computacional real, convencional y consciente de lo cuántico, no una incondicional. El proyecto nunca afirma lo contrario, y todo documento público enuncia ahora el régimen (roadmap 0.1).

## 6. Qué **no** demuestra esta parte

- **Enlazabilidad / metadatos.** I-2 trata del contenido, no de quién habla con quién. Nada de aquí oculta que *algún* flujo ocurrió sobre una ruta de partes capturada; ese es el residual admitido del modelo de amenazas, estrechado por la dispersión, no anulado.
- **Disponibilidad.** Una parte hostil en una ruta de partes puede corromper o descartar una parte; el AEAD falla cerrado (SP-7a), así que esto es denegación de servicio, no divulgación. SA-1…SA-4 no dicen nada sobre que el mensaje *llegue*, solo sobre lo que un adversario por debajo de `k` *aprende* si no llega.
- **Correlación temporal entre partes (SP-9 / OP-4).** SA-2 trata de los *valores* de las partes, no de sus instantes de emisión. `n` partes entrando en la red en cuestión de milisegundos son una huella aunque sus bytes sean independientes de `C`. Eso es un problema abierto, no algo que esta demostración aborde.
- **El propio AEAD.** El nivel 2 hereda lo que sea cierto de ChaCha20-Poly1305. Si ese cifrador cae, el nivel 2 cae; el umbral (nivel 1) no.

## 7. Requisitos introducidos aquí

- **SA-1** — secreto perfecto por byte de cualesquiera `k−1` partes (demostrado).
- **SA-2** — independencia conjunta sobre el secreto entero (demostrado, dado SA-3).
- **SA-3** — *la aleatoriedad de los coeficientes es crítica para el umbral*: CSPRNG, independiente por posición y por coeficiente. **[normativo, máxima garantía]**
- **SA-4** — separación de claves a través del umbral: ningún valor observable por debajo de `k` revela `K` ni `kpair`. **[normativo]**

SA-1 y SA-2 son teoremas; SA-3 y SA-4 son las dos condiciones bajo las cuales los teoremas describen el sistema real. Rompe cualquiera de los cuatro — encuentra una vista que la demostración pasó por alto, una correlación que SA-3 deja pasar, un campo que lleve `K` — y habrás roto I-2. Esa es la invitación.
