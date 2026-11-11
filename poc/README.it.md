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
    python3 network_sim.py      # esperimento: avversario k-path vs taglia rete

## L'esperimento: cosa compra l'avversario, in numeri

`network_sim.py` trasforma le domande aperte delle issue #2/#4/#10 in una
tabella. Modella un messaggio come n=4 quote su 4 circuiti disgiunti verso 4
drop; un avversario k-path possiede una frazione dei relay e "vede" un circuito
quando ne controlla sia il guard sia l'exit:

    mittente                                       drop (una quota ciascuno)
      |  quota 1 --[guard]--[mid]--[exit]-->  box 1  \
      |  quota 2 --[guard]--[mid]--[exit]-->  box 2   |  il destinatario
      |  quota 3 --[guard]--[mid]--[exit]-->  box 3   |  ritira, ne prende
      |  quota 4 --[guard]--[mid]--[exit]-->  box 4  /   3 qualsiasi, ricostr.

- **visti >= k** -> rottura del contenuto (e solo allora; sotto k il piano I-2
  regge incondizionatamente, a qualunque taglia di rete);
- **visti < k** -> contenuto salvo, ma ogni circuito visto rivela comunque che
  *un* flusso è passato — la perdita di metadati che il threat model ammette:
  la dispersione la restringe, non la annulla.

Il risultato stampato: le rotture di contenuto sono rare e spariscono quando la
rete cresce abbastanza da costruire circuiti AS-disgiunti; la perdita di
linkage è piccola ma nonzero e peggiore su una rete minuscola che *non* riesce
a costruirli — ecco perché una rete giovane deve usare, e dichiarare, una
"modalità rete piccola" degradata (issue #4). Numeri provvisori: riproducili,
rompi il modello, discuti sulle issue.

`vectors.json` contiene vettori per altre implementazioni: chi li riproduce
interopera a questo livello.

Che cosa **non** è: codice di produzione. Niente aritmetica a tempo costante,
niente rete, niente livello onion, niente AEAD end-to-end (per SP-1 questo
livello vede solo ciphertext opaco). Non usatelo per proteggere alcunché.
