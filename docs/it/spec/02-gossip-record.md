# Specifica ScrambNet — Parte 2: Gossip Record

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([en](../../en/spec/02-gossip-record.md)).

**Stato: BOZZA (DRAFT).** Valori strawman contrassegnati con `(s)`. Le questioni di sybil/eclipse su cui questa
parte si appoggia sono OP-2 e deliberatamente aperte.

## 1. Ambito

Il gossip record è il descrittore autofirmato tramite cui un relay esiste. Non c'è
directory, autorità, registrazione (I-3): un relay è l'insieme dei record
che firma, e la mappa della rete è qualunque campione verificabile ciascun client possiede.

## 2. Formato del record

- **GR-1.** Un record è una mappa CBOR canonica (RFC 8949 §4.2.1), al massimo
  `1024` byte (s) codificati. I record più grandi DEVONO (MUST) essere scartati senza leggerli.
- **GR-2.** Campi (chiavi intere; le chiavi sconosciute DEVONO (MUST) essere ignorate per la compatibilità
  in avanti, ma sono coperte dalla firma):

| Chiave | Nome | Tipo | Note |
|---|---|---|---|
| 0 | `v` | uint | versione del formato, `1` |
| 1 | `id` | bytes(32) | chiave pubblica di identità Ed25519 — il nome del relay |
| 2 | `onion` | bytes(32) | chiave X25519 per gli handshake di circuito; DEVE (MUST) ruotare ≤ 7 giorni (s) |
| 3 | `addrs` | array | endpoint: coppie `[transport-id uint, blob bytes]` |
| 4 | `bw` | uint | banda sostenuta dichiarata, kB/s — una *dichiarazione*, vedi GR-7 |
| 5 | `created` | uint | tempo unix, DEVE (MUST) essere arrotondato per difetto all'ora (GR-5) |
| 6 | `expiry` | uint | tempo unix, DEVE (MUST) essere ≤ `created` + 7 giorni (s) |
| 7 | `sig` | bytes(64) | Ed25519 sulla codifica canonica con la chiave 7 assente |

- **GR-3.** Un relay NON DEVE (MUST NOT) pubblicare dichiarazioni geografiche o giurisdizionali su
  sé stesso. I client inferiscono l'AS e la giurisdizione dagli `addrs` con i propri dati
  (OP-1); la posizione autodichiarata è una superficie d'attacco, non informazione.
- **GR-4.** Validità della firma, limite di dimensione, scadenza e arrotondamento del timestamp DEVONO (MUST)
  essere tutti verificati prima che un record sia archiviato o inoltrato; i fallimenti sono scartati
  in silenzio — nessun errore che distingua «malformato» da «scaduto» può essere
  osservabile dal mittente del record.
- **GR-5.** L'arrotondamento di `created` esiste per impedire il fingerprinting dei relay tramite
  deriva dell'orologio. I client DEVONO (MUST) trattare due record con lo stesso `id` come un unico relay e
  conservare solo il `created` più fresco.

## 3. Scambio e campionamento

- **GR-6.** I record viaggiano su circuiti stabiliti e sulla mesh locale
  (Parte 5), appoggiati a batch a dimensione fissa: un batch di gossip è `8` record (s)
  con padding a dimensione costante, scambiato al massimo una volta per pari ogni `10` minuti (s).
  Un nodo risponde a una richiesta di campione con un campione uniforme dei propri record archiviati;
  NON DEVE (MUST NOT) rispondere con un campione distorto dall'identità del richiedente (l'ovvia
  leva di eclipse).
- **GR-7.** `bw` è una dichiarazione. I client DOVREBBERO (SHOULD) verificare le dichiarazioni con probing
  randomizzato su circuiti che non rivelino chi fa il probing, e DOVREBBERO (SHOULD) ponderare la selezione dei
  percorsi sulla banda verificata, non dichiarata. Il progetto del probing è aperto (OP-2).
- **GR-8 (mixing delle fonti).** Il campione archiviato di un client DEVE (MUST) mescolare record da
  classi di fonti indipendenti — come minimo: ponte lungo il grafo sociale (stile Lox),
  scambio di gossip e probing diretto — e NON DEVE (MUST NOT) permettere ad alcuna singola classe di
  superare una frazione configurabile (strawman 1/2) del campione. Questa è la
  difesa da eclipse finché OP-2 non produce qualcosa di più forte.
- **GR-9.** Le nuove identità sono economiche per progetto (nessuna registrazione), quindi nulla in
  questa parte può assumere resistenza ai sybil dal costo dell'identità. Qualunque meccanismo che
  necessiti di resistenza ai sybil deve ottenerla da risorse verificate (banda,
  uptime a lungo termine osservato dal client stesso) o dal grafo sociale — mai
  dal record da solo.

## 4. Bootstrap

- **GR-10.** Un client appena nato DEVE (MUST) poter partire da una singola riga di ponte
  fuori banda (un codice QR, una stringa stampata, un messaggio da un amico) contenente
  un record più un suggerimento di trasporto. Il bootstrap senza contatti è OP-7 ed è aperto.

## 5. Cosa questa parte non decide

La resistenza a sybil/eclipse oltre GR-8/GR-9 (OP-2), il protocollo di probing (GR-7),
il bootstrap senza contatti (OP-7). Esistono issue numerate per ciascuno.
