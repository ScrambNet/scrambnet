# Núcleo de dispersión — PoC de referencia

Compañero ejecutable de las Partes [1](../docs/es/spec/01-share-packet.md) y
[6](../docs/es/spec/06-rendezvous.md) de la especificación.
Python 3 puro, solo biblioteca estándar, escrito para ser leído y atacado:
es una especificación ejecutable, no el futuro nodo.

Qué demuestra:

- la **composición SP-1 completa**, ejecutada, no afirmada: `e2e.py` cifra el
  mensaje bajo una clave de par precompartida (ChaCha20-Poly1305, verificada
  contra los vectores de prueba RFC 8439), luego `dispersal.send()` divide el
  *texto cifrado* y `receive()` reconstruye y descifra — encrypt → split →
  reconstruct → decrypt, con un fragmento invertido que falla en cerrado en el
  AEAD, nunca reconstruido en basura (SP-1, SP-1a);
- división Shamir (n, k) sobre GF(2^8), byte a byte, y reconstrucción desde
  k fragmentos cualesquiera (SP-1, SP-2);
- el suelo incondicional (I-2), por fuerza bruta: `floor_demo()` enumera cada
  polinomio coherente con k−1 fragmentos observados y encuentra los 256 bytes
  secretos candidatos *exactamente igual de coherentes* — no se aprende nada,
  ni con cómputo ilimitado;
- las etiquetas SP-7 con clave del destinatario (BLAKE2s con clave) y el
  reconocimiento por ventana de etiquetas que implican;
- el relleno aleatorio SP-8 y el formato de carga útil de la Parte 1 §4;
- el precio honesto: una dispersión (n, k) transmite ×n el volumen del
  texto cifrado (issue #4).

Ejecución:

    python3 e2e.py              # cinturón SP-1: KAT AEAD + ida y vuelta seal/open
    python3 test_e2e.py         # suite de pruebas AEAD (vectores RFC 8439)
    python3 dispersal.py        # demo: SP-1 completo encrypt->split->...->decrypt
    python3 test_dispersal.py   # pruebas, incluye vectors.json
    python3 rendezvous.py       # demostración Parte 6: drops y sondeo
    python3 test_rendezvous.py  # pruebas Parte 6
    python3 network_sim.py      # experimento: adversario k-path vs tamaño red
    python3 test_properties.py  # pruebas estadísticas de propiedades (uniformidad, SP-7)
    python3 run_all.py          # cada demo + cada prueba, un veredicto

## El experimento: qué compra el adversario, en números

`network_sim.py` convierte las preguntas abiertas de las issues #2/#4/#10 en
una tabla. Modela un mensaje como n=4 fragmentos sobre 4 circuitos disjuntos
hacia 4 drops; un adversario k-path posee una fracción de los relays y "ve" un
circuito cuando controla a la vez su guard y su exit:

    emisor                                         drops (un fragmento c/u)
      |  frag 1 --[guard]--[mid]--[exit]-->  box 1  \
      |  frag 2 --[guard]--[mid]--[exit]-->  box 2   |  el destinatario
      |  frag 3 --[guard]--[mid]--[exit]-->  box 3   |  recoge, toma 3
      |  frag 4 --[guard]--[mid]--[exit]-->  box 4  /   cualesquiera, recon.

- **vistos >= k** -> rotura del contenido (y solo entonces; por debajo de k el
  suelo I-2 se mantiene incondicionalmente, a cualquier tamaño);
- **vistos < k** -> contenido a salvo, pero cada circuito visto revela aun así
  que *algún* flujo circuló — la pérdida de metadatos que el modelo de amenazas
  admite: la dispersión la estrecha, no la anula.

El resultado impreso: las roturas de contenido son raras y desaparecen cuando
la red crece lo bastante para construir circuitos AS-disjuntos; la fuga de
vínculo es pequeña pero no nula y peor en una red minúscula que *no* puede
construirlos — por eso una red joven debe usar, y declarar, un "modo red
pequeña" degradado (issue #4). Números provisionales: reprodúcelos, rompe el
modelo, discute en las issues.

`vectors.json` contiene vectores para otras implementaciones: quien los
reproduce interopera en esta capa.

Lo que **no** es: código de producción. El AEAD en `e2e.py` es Python puro y
**no es de tiempo constante** — es correcto (reproduce los vectores RFC 8439)
pero filtra por temporización, así que un nodo real DEBE usar una biblioteca de
tiempo constante verificada. Sin aritmética de tiempo constante en ninguna
parte, sin red, sin capa onion. No lo uséis para proteger nada.
