# ScrambNet — Modelo de amenazas

> Una red que promete protección total miente, y quien corre riesgos reales
> merece saber exactamente dónde termina el paraguas. Este documento es el contrato.

## Adversarios y resultados

| Adversario | Capacidad | Respuesta de la red | Resultado |
|---|---|---|---|
| Observador local (tu ISP, un Wi-Fi de oficina) | Observar tu tráfico | Ve un flujo TLS corriente hacia una dirección corriente | **Protegido** |
| Censor nacional | Bloquear IPs, cotejar huellas de DPI, enumerar puentes | Transportes camaleón; puentes distribuidos por el grafo social con niveles de confianza al estilo Lox | **Protegido** (una carrera armamentística, pero sostenible) |
| Relé malicioso en una ruta | Observar lo que lo atraviesa | Ve un salto de una parte; los paquetes Sphinx son idénticos en todas partes | **Protegido** |
| Operador de la guardia *y* la salida de un circuito | Correlacionar la temporización entrada/salida | Ese circuito lleva una parte, no el mensaje; las guardias son estables durante meses; el modo paranoico añade retardos de mezcla | **Mitigado** |
| Adversario de `k` rutas (posee guardia+salida en `k` de las `n` rutas de parte a la vez) | Correlación de temporización completa más captura de partes | La selección de rutas impone guardias, AS y jurisdicciones disjuntos, lo que hace de `k` posiciones simultáneas un problema de ocupación | **Mitigado** — este es el riesgo residual de diseño; sube `n`, `k` a tu gusto |
| Adversario global pasivo (ve todo el tráfico en todas partes) | Correlacionar todo | Modo rápido: nada. Modo paranoico: mixnet con retardos y tráfico de cobertura | **Fuera de modelo (modo rápido)** — declarado, como lo declara Tor |

## Qué cambia la dispersión, con precisión

El enrutamiento de cebolla clásico falla *catastróficamente* en una mala tirada: controla la guardia y la
salida del único circuito y obtienes a la vez el enlace (quién habla con quién) **y**, allí donde el
cifrado propio del destino es inexistente o está roto, el contenido. Bajo la dispersión:

- El **contenido** está incondicionalmente protegido por debajo de `k` partes capturadas. No interviene
  ninguna hipótesis computacional. Este umbral no puede erosionarse por el criptoanálisis ni el avance cuántico.
- El **enlace** (metadatos) sobre una única ruta de parte violada sigue siendo una pérdida real: el
  adversario aprende que *algún* flujo corrió entre tú y el recolector de partes de un destino.
  La dispersión estrecha lo que un circuito delata; no lo anula. Las guardias estables, la
  selección de rutas disjunta por AS y la mezcla del modo paranoico son las mitigaciones.

## Suposiciones

1. Las redes subyacentes (ISPs, IXPs, cables, nubes) son hostiles o están comprometidas.
2. El diseño, el código y todos los documentos son plenamente conocidos por todo adversario (Kerckhoffs).
3. Los relés los gestionan desconocidos; una fracción constante es maliciosa y confabula.
4. Los extremos son honestos: un teléfono comprometido pierde antes de que salga el primer paquete.
   La seguridad del dispositivo queda fuera de alcance, dicho sin pretensiones.
5. Los usuarios pueden obtener el cliente. Las compilaciones reproducibles más una especificación pública
   (cualquiera puede reimplementar desde cero) son la respuesta al envenenamiento de binarios y a la desaparición
   de cualquier canal oficial de distribución.

## No-objetivos

- Proteger a un usuario cuyo dispositivo está comprometido.
- Ocultar *que* una región usa herramientas de evasión en conjunto (modo rápido).
- Moderación de contenidos en la capa de red. La red transporta paquetes, no opiniones;
  protege a los disidentes y a sus adversarios con la misma matemática. Una infraestructura
  solo es creíble si no puede tomar partido.

## Problemas abiertos

Marcados para el ataque. Cada problema se discute en **un** solo lugar: una
única [issue](https://github.com/ScrambNet/scrambnet/issues) por problema, con
el texto en inglés y todas las traducciones en el mismo hilo. Lee el problema
aquí en tu idioma; discútelo allí, en la única issue, para que ninguna
discusión se fragmente.

1. **Imposición de la disjunción.** Un primer mecanismo de selección de rutas existe ahora en borrador
   ([spec Parte 3](spec/03-path-selection.md)) con un hombre de paja ejecutable en
   `poc/network_sim.py`; lo que queda abierto es el núcleo duro: ¿cómo *verifica* un cliente
   que las `n` rutas no comparten un AS, una jurisdicción, un centro de datos — usando solo su muestra de
   gossip y un conjunto de datos de inferencia distribuido sin confianza (I-3), contra relés que pueden mentir
   sobre todo salvo sobre sus firmas?
2. **Resistencia a sybil y eclipse** del muestreo de gossip sin un asignador central.
   Walking Onions supone una instantánea firmada por una autoridad; nosotros quitamos la autoridad. ¿Qué
   reemplaza su función anti-sybil — prueba de claves de larga duración? ¿ponderación por grafo social?
   ¿verificación de ancho de banda por sondeo aleatorizado?
3. **Economía de parámetros.** Valores por defecto de `n`, `k` por clase de tráfico; ¿cuándo la IDA de Rabin
   (más barata, computacional) reemplaza a Shamir (incondicional) para datos masivos, y es esa
   rebaja aceptable alguna vez por defecto?
4. **Correlación de temporización de partes.** La no enlazabilidad de contenido entre partes (SP-7) está resuelta e
   implementada en la PoC; la *temporización* no. `n` partes que entran en la red con una separación de
   milisegundos son en sí mismas una huella. Jitter, batching, partes señuelo: ¿cuánto cuesta cada uno
   en latencia, y qué compra de verdad contra un adversario que observe varias salidas?
5. **Economía del tráfico de cobertura** en modo paranoico sobre conexiones móviles con tarifa por volumen.
6. **Direccionamiento en apagón.** Enrutamiento basado en identidad sobre store-and-forward de malla sin un
   DHT alcanzable desde dentro del apagón.
7. **Arranque con cero contactos** para la distribución de puentes por el grafo social.
8. **Gobernanza de actualizaciones.** Publicaciones multifirma a través de jurisdicciones: cuántos firmantes,
   cómo elegidos, cómo reemplazados — sin crear el comité que se convierte en el interruptor de apagado.
9. **Metadatos y economía de los dead-drops.** Un drop ve los tiempos de depósito y la cadencia de sondeo de
   un buzón dentro de una época (spec Parte 6). Distribuciones de sondeo y coste de los señuelos en conexiones
   con tarifa por volumen, semántica de borrado, tarificación de depósitos contra la inundación, incentivos de almacenamiento:
   ¿cuánto cuesta cada defensa, y qué filtra cada una?
