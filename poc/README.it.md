# Cuore di dispersione — PoC di riferimento

Compagno eseguibile delle Parti [1](../docs/spec/01-share-packet.md) e
[6](../docs/spec/06-rendezvous.md) della specifica.
Python 3 puro, solo libreria standard, scritto per essere letto e attaccato:
è una specifica eseguibile, non il futuro nodo.

Che cosa dimostra:

- divisione Shamir (n, k) su GF(2^8), byte per byte, e ricostruzione da
  k quote qualsiasi (SP-1, SP-2);
- il piano incondizionato (I-2), per forza bruta: `floor_demo()` enumera ogni
  polinomio coerente con k−1 quote osservate e trova tutti i 256 byte segreti
  candidati *esattamente ugualmente coerenti* — non si apprende nulla, nemmeno
  con potenza di calcolo illimitata;
- i tag SP-7 a chiave del destinatario (BLAKE2s a chiave) e il riconoscimento
  a finestra di tag che implicano;
- il padding casuale SP-8 e il formato del payload di quota della Parte 1 §4;
- il prezzo onesto: una dispersione (n, k) trasmette ×n il volume del
  ciphertext (issue #4).

Esecuzione:

    python3 dispersal.py        # dimostrazione
    python3 test_dispersal.py   # test, inclusi i vettori di vectors.json
    python3 rendezvous.py       # dimostrazione Parte 6: drop e polling
    python3 test_rendezvous.py  # test Parte 6

`vectors.json` contiene vettori per altre implementazioni: chi li riproduce
interopera a questo livello.

Che cosa **non** è: codice di produzione. Niente aritmetica a tempo costante,
niente rete, niente livello onion, niente AEAD end-to-end (per SP-1 questo
livello vede solo ciphertext opaco). Non usatelo per proteggere alcunché.
