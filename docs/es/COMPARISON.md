# Cómo se sitúa ScrambNet

Un posicionamiento honesto frente a los sistemas que un revisor nombrará con razón primero.
Este documento declara lo que ScrambNet hace *de forma distinta* y — más importante aún —
lo que hace *peor*. Si una celda de abajo está mal, abre una issue: equivocarse aquí
cuesta más que equivocarse en cualquier otra parte del repositorio.

## La única diferencia real

Todo sistema de anonimato desplegado protege el **contenido** de los mensajes con
una hipótesis computacional: rompe el cifrado (hoy o con un futuro ordenador
cuántico) y el contenido queda legible. El umbral de contenido de ScrambNet es
**informacionalmente seguro**: por debajo de `k` partes capturadas no hay texto cifrado que
romper, porque el contenido no está presente en ningún conjunto de `k−1` partes — una propiedad del
secreto compartido de Shamir, no de la fortaleza de ningún cifrado (invariante I-2). Esa es
toda la apuesta. Todo lo demás, aquí, es arte previo, compuesto.

Esta diferencia es **solo sobre el contenido**. Para la **vinculabilidad** (quién habla con quién,
los metadatos) ScrambNet está en la misma dura pelea que todos los demás, y no hace
ninguna promesa informacional ahí, en modo rápido.

## Lado a lado

| | **ScrambNet** | **Tor** | **Nym / Loopix** | **Briar** |
|---|---|---|---|---|
| Uso principal | Mensajería (asíncrona, por dead-drop) | Navegación de baja latencia | Mensajería (mixnet) | Mensajería, P2P |
| Confidencialidad del contenido | **Incondicional por debajo de `k` partes** | Computacional (TLS + onion) | Computacional | Computacional |
| Defensa de la vinculabilidad | Circuitos dispersos + mix (paranoica) | Circuitos onion | Mixnet de Poisson (fuerte) | Onion + grafo de contactos |
| Directorio / descubrimiento | **Ninguno** — gossip + muestra verificable | ~9 autoridades de directorio | Validadores / nym-api | Introducción por contactos |
| Adversario global pasivo | Fuera de modelo (rápido) / mix (paranoica) | Fuera de modelo | **En el modelo** (mixnet) | Parcial |
| Apagón / sin conexión | Malla local, store-and-forward | No | No | **Sí** (Bluetooth/Wi-Fi) |
| Capa de incentivos | Ninguna (voluntariado) | Voluntariado | **Token** | Voluntariado |
| Madurez | **Spec pre-alpha + PoC** | Producción, más de 20 años | Producción | Producción |

## En qué va ScrambNet por detrás, dicho con claridad

- **Madurez.** Tor, Nym y Briar están desplegados, auditados y transportan tráfico
  real hoy. ScrambNet es una especificación y una prueba de concepto en Python.
  Nadie debería enrutar todavía un secreto real por ella, y el repositorio lo dice.
- **Diseño del mixnet.** Nym/Loopix tienen un diseño de mix de Poisson riguroso y publicado
  con un modelo de adversario global pasivo. El modo paranoico de ScrambNet es un
  marcador de posición (OP-5) hasta que alguien haga también aquí ese trabajo.
- **Metadatos de vinculabilidad.** El patrón de recuperación por dead-drop filtra la cadencia
  de sondeo hacia un drop dentro de una época (OP-9) — un coste que el mezclado continuo de
  Nym amortiza más a fondo.
- **Ancho de banda.** El umbral incondicional cuesta `×n` de ancho de banda (×4 en el
  strawman). Tor cuesta ×1 por su garantía de contenido más débil. Este es el precio
  de la apuesta, no un fallo, pero es un precio real (OP-3).
- **Incentivos.** Nym paga a los relés; ScrambNet pide voluntarios, lo que históricamente
  limita el crecimiento.

## Por qué construirla de todos modos

Porque la garantía de contenido de todos los demás sistemas tiene fecha de caducidad escrita en
las hipótesis de 2003–2017, y «recolecta ahora, descifra después» es una estrategia real
de adversario contra disidentes cuyos mensajes deben seguir siendo ilegibles durante
décadas. Por debajo de `k` partes, el umbral de contenido no puede ser erosionado en absoluto por el
progreso criptoanalítico o cuántico — no hay nada ahí que romper. En `k` partes o por encima, el
cinturón es un AEAD convencional, y ScrambNet lo alimenta desde un secreto *simétrico* precompartido
sin acuerdo asimétrico en la ruta del contenido (spec SP-1a), de modo que «recolecta ahora, descifra
después» queda derrotado también en *ese* régimen: no hay intercambio de claves registrado que un futuro
ordenador cuántico pueda romper, solo un secreto que las partes ya compartían. El residuo honesto es el
intercambio único, fuera de banda, que entrega ese secreto compartido. Esto vale una factura de ancho de
banda `×n` y el trabajo de construir el resto. Si
esa apuesta está equivocada, la forma más rápida de descubrirlo es atacarla aquí.
