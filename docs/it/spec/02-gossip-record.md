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

## 5. Il protocollo di probing della banda (chiusura di GR-7)

GR-7 dice che `bw` è una dichiarazione e DOVREBBE (SHOULD) essere verificata tramite «probing
randomizzato su circuiti che non rivelino chi fa il probing», poi dichiara aperto il progetto del
probing. Questa sezione è quel progetto. Il probe risponde esattamente a una domanda — *quale
throughput posso, io, questo client, spingere attraverso questo relay adesso su un circuito
che non mi nomina?* — e la risponde per il solo client che chiede. Non esiste **alcun** numero di
banda pubblicato, condiviso o autorevole: le bandwidth authority di Tor sono precisamente
l'allocatore centrale che I-3 ci nega (PS-10, GR-9), quindi ogni client ricava la propria cifra
verificata e pondera la propria selezione dei percorsi (PS-7) in base ad essa.

### 5.1 La misurazione, e di cosa è funzione pura

- **GR-11 (la banda verificata è un'auto-misurazione per-client, mai una cifra
  pubblicata).** `[claim-critical]` La banda verificata di un client per il relay `R`,
  scritta `vbw(R)`, DEVE (MUST) essere calcolata come funzione deterministica di input che il
  client ha osservato **da sé**:
  ```
      vbw(R, epoch) = probe(circuits_through_R, bytes_sent, timestamps_seen)
  ```
  e di nulla che un relay, un pari o una terza parte asserisca. `vbw` è una variabile
  locale, non un valore di rete: due client onesti che fanno il probing dello stesso `R`
  ricaveranno `vbw(R)` **diversi** (i loro percorsi, la loro congestione, il loro momento), e
  questo è corretto — non esiste un vero scalare «banda di `R`» su cui concordare, solo
  *il throughput che un dato client ha ottenuto su un dato percorso in un dato momento* (GR-18).
  Un client DEVE (MUST) trattare la dichiarazione `bw` di un relay non ancora sottoposto a probe come
  **default a banda bassa** (PS-7), mai come la sua cifra; una dichiarazione che il client non ha
  misurato da sé porta peso zero nella selezione.

- **GR-12 (il probe è un round-trip sigillato su un circuito — chi fa il probing non è mai
  nominato).** `[claim-critical]` Un probe DEVE (MUST) essere trasportato come traffico ordinario di circuito:
  il client costruisce un circuito il cui **relay misurato `R` è l'hop intermedio**, invia
  un treno limitato di celle a forma di share-packet (Parte 1: `P = 2048` byte fissi,
  SP-3) indirizzate attraverso `R`, e misura il throughput di round-trip del treno
  man mano che ritorna sullo stesso circuito. `R` vede una cella arrivare dal suo predecessore
  e partire verso il suo successore — esattamente ciò che vede per il vero traffico relayato — e
  **non può vedere il client**: chi fa il probing si colloca ad almeno un hop oltre la visuale di `R`, come
  in ogni circuito Sphinx (SP-4). Il probe NON DEVE (MUST NOT) usare alcun tipo di cella, flag, lunghezza
  o cadenza che lo distingua dal traffico utente relayato (I-4, e GR-13
  sotto). Un relay che riuscisse a distinguere un probe da un payload potrebbe superare il probe e
  far fallire il payload; quindi, per costruzione, non gli si può dare l'occasione.

```
  IL PROBE SU UN CIRCUITO  (R è misurato; chi fa il probing non è mai nella visuale di R)

   client (prober)        guard G        relay R  (sotto test)        coda T
   ───────────────        ───────        ──────────────────         ──────
        │                    │                  │                      │
        │  costruisci circuito  C = [ G , R , T ]  (R è l'hop INTERMEDIO)
        │───────────────────▶│                  │                      │
        │     treno di N celle a dimensione fissa, indistinguibili dai  │
        │     veri share packet relayati (SP-3/SP-4, I-4)              │
        │════════════════════╪═════════════════▶│═════════════════════▶│
        │                    │                  │   T rimanda indietro il treno
        │◀═══════════════════╪══════════════════╪══════════════════════│
        │   misura: bytes_acked / (t_last − t_first)  = campione di     │
        │            throughput di questo probe per R, QUESTO percorso, QUESTO momento
        │                    │                  │                      │
      vbw(R) ← aggregato robusto di molti campioni simili nel tempo (GR-16)

   Cosa vede R:  celle da G  →  celle verso T.   Identico al trasporto di vero
   traffico.  R NON vede «client», NON vede «questo è un probe», e
   non può comportarsi bene solo-quando-osservato perché non può sapere di essere osservato.
   Il costo è PAGATO da chi fa il probing: invia N·P byte che non riavrà indietro
   come lavoro utile (GR-14).  R non può essere costretto a inondare una vittima, perché il
   treno ritorna a CHI FA IL PROBING, mai a una terza parte nominata dall'attaccante (GR-15).
```

### 5.2 Le cinque proprietà che il probe deve avere

- **GR-13 (indistinguibilità — un relay non può comportarsi bene solo quando è osservato).**
  `[claim-critical]` La proprietà anti-gaming è l'uniformità sul filo (I-4): **il traffico di
  probe DEVE (MUST) essere byte-per-byte e timing-per-timing indistinguibile dal
  vero traffico relayato che a un relay è chiesto di trasportare**, così che il relay non possa
  condizionare il proprio inoltro su «sono sotto misurazione?». Concretamente le celle di probe
  DEVONO (MUST) essere share packet completi della Parte 1 (`P = 2048` byte, SP-3), DEVONO (MUST) essere emesse sotto
  la stessa disciplina di batching/jitter usata da un vero mittente (SP-6, SP-9), e NON DEVONO (MUST NOT)
  portare alcun marcatore specifico del probe. Un relay che sotto-serve il vero traffico e
  sovra-serve i probe dovrebbe distinguerli; I-4 gli nega l'informazione
  per farlo. La `vbw(R)` misurata è quindi un limite inferiore di ciò che `R` *inoltrerebbe*
  per il vero traffico di questo client, perché `R` non può distinguere i due —
  che è tutto il punto: *attacca questo trovando un bit su cui il relay possa basarsi.*

- **GR-14 (il probe costa a chi fa il probing una quantità limitata e pre-pagata).** Un singolo
  probe di `R` DEVE (MUST) inviare al massimo `B_probe` byte (strawman: `B_probe = 1 MiB`
  distribuito su `≥ τ` secondi, `τ = 4 s` (s)) e DEVE (MUST) essere limitato in frequenza al massimo a un
  probe in volo per relay target e al massimo a `Q` probe concorrenti totali per
  client (strawman `Q = 8` (s)). Chi fa il probing spende byte reali che non recupera
  come lavoro utile; questo è il costo che rende il probing auto-limitante. Un client NON DEVE (MUST
  NOT) fare il probing di un relay più spesso di una volta per `T_probe` (strawman: ore, non
  minuti (s)) — la banda cambia lentamente rispetto a quanto in fretta una misurazione invecchia,
  quindi ripetere spesso il probe rende poco e costa linearmente (GR-16).

- **GR-15 (il probe non può diventare un amplificatore di DoS).** `[claim-critical]` Il
  relay misurato DEVE (MUST) sempre restituire il traffico di probe **solo a chi fa il probing, sullo stesso
  circuito su cui è arrivato** — mai a un indirizzo che le celle di chi fa il probing potrebbero nominare.
  Poiché l'hop di coda `T` rimanda indietro il treno lungo `C` al client che ha costruito
  `C`, un probe è un **anello chiuso**: il lavoro che un probe induce è limitato da ciò che
  chi fa il probing ha inviato (fattore di amplificazione ≤ 1 per costruzione, non per policy), e
  non esiste campo in cui un attaccante possa scrivere l'indirizzo di una vittima per far sì che `R`
  la inondi. Questa è la differenza strutturale rispetto a qualunque progetto «chiedi al relay di inviare un
  flusso di test all'indirizzo X», che sarebbe un riflettore ed è **proibito**:
  un probe NON DEVE (MUST NOT) accettare una destinazione che non termina esso stesso. Un'implementazione
  che permette al probe di prendere di mira una terza parte è non conforme.

- **GR-16 (un probe misura un momento-percorso; `vbw` è un aggregato robusto di molti).**
  Un singolo probe è un campione di *un percorso in un istante*, contaminato dalla capacità propria del
  guard e della coda, dal traffico incrociato e dalla congestione in un punto qualunque di
  `C`. Un client DEVE (MUST) quindi (a) fare il probing di `R` attraverso **vari circuiti indipendenti**
  (guard e code distinti, source-mixed per GR-8 ove possibile), (b) attribuire a
  `R` il **massimo throughput sostenuto osservato** tra quei circuiti su una
  finestra (il massimo, perché il collo di bottiglia di un singolo circuito è un limite *inferiore* di
  `R` — il percorso più veloce isola meglio la capacità propria di `R`), e (c) trattare il
  risultato come una **stima con una confidenza che decade con l'età** (strawman:
  emivita di poche epoch (s)). `vbw(R)` DEVE (MUST) avere un livello minimo conservativo: un
  singolo probe non corroborato conta come basso, non alto (disciplina PS-7).

- **GR-17 (i risultati del probe non sono diffusi via gossip come banda; solo la disciplina è
  condivisa).** Un client NON DEVE (MUST NOT) pubblicare, diffondere via gossip o accettare da un pari uno scalare
  «banda verificata di `R`» — ciò ricostruirebbe la bandwidth authority che I-3
  proibisce (una cifra riportata da un pari è una dichiarazione non migliore di `bw` stessa, GR-9). Ciò che
  PUÒ (MAY) essere diffuso via gossip è la **raggiungibilità/liveness** di un relay come una classe di fonte tra
  le classi di GR-8, e un client PUÒ (MAY) usare l'accordo di un pari sul fatto che un relay *esista e
  risponda* come punto di osservazione corroborante (stile PS-15), ma il **numero di throughput
  che ciascun client usa per la ponderazione DEVE (MUST) essere il proprio** (GR-11). I pari sybil possono gonfiare
  *quanti* report dicono «`R` è veloce», ma non possono gonfiare ciò che il probe
  proprio del client ha misurato — questa è la regola GR-9/PS-10 «conta solo il verificato» applicata alla
  banda.

### 5.3 Cosa un probe può e non può dirti (degradare onestamente)

- **GR-18 (un probe misura il throughput, non l'onestà, non la posizione, non l'identità).**
  Un probe risponde a *«questo percorso può muovere byte?»* e a nient'altro. NON DEVE (MUST NOT) essere
  letto come prova che:
  - **il relay sia onesto** — un relay può inoltrare perfettamente il traffico di probe e comunque
    loggare, ritardare o correlare il vero traffico; il throughput è ortogonale alla
    minaccia di correlazione guard+exit (modello di minaccia), che la *disgiunzione* dei percorsi (Parte 3)
    affronta, non la banda;
  - **il relay sia dove la mappa dice** — un probe cronometra un round trip; non
    localizza `R` in un AS o giurisdizione (quello è la mappa della Parte 8, PS-4, con il suo proprio
    errore dichiarato), e un probe veloce non dice nulla sulla co-locazione (Parte 8 §10);
  - **il relay sia una singola parte distinta** — un operatore sybil con capacità reale fa il
    probing *tanto* velocemente quanto è, perché ha davvero la banda (vedi §6: un
    avversario dotato di risorse non è un sybil, è un costoso avversario reale).
  Un client conforme DEVE (MUST) presentare la banda verificata solo come ciò che è — una
  stima di throughput che decade con la freschezza, contaminata dal percorso, che il client ha misurato
  da sé — e NON DEVE (MUST NOT) lasciare che una `vbw` alta sostituisca la disgiunzione (Parte 3) o
  la diversità (GR-8) in alcuna decisione di selezione.

---

## 6. Sybil ed eclipse, limitati (stringendo GR-8/GR-9)

Le identità sono gratuite (GR-9), quindi un avversario gonfia a piacere il conteggio **grezzo** dei
record. Le difese sottostanti non lo impediscono; limitano ciò che il gonfiaggio *compra*,
e il limite è la curva che il simulatore misura (§7.1).

### 6.1 Il limite di eclipse dal mixing delle fonti

- **GR-19 (il cap di GR-8 dà un limite di eclipse dichiarato; l'assunzione è l'indipendenza
  delle classi).** `[claim-critical]` Supponiamo che il client mescoli il proprio campione tra `m`
  classi di fonti indipendenti (GR-8: come minimo ponte lungo il grafo sociale, scambio di
  gossip, probing diretto — quindi `m ≥ 3`), con il cap per-classe che **nessuna singola
  classe contribuisce con più della frazione `f`** del campione archiviato (strawman
  `f = 1/2` (s)). Supponiamo che un avversario controlli pienamente `a` di quelle `m` classi (ogni
  record consegnato attraverso una classe controllata è avversariale) e nulla nelle
  altre. Allora la quota del campione del client appartenente all'avversario è limitata da
  ```
        A(a, f)  ≤  min( 1 ,  a · f ).
  ```
  Un **eclipse completo** — l'avversario che fornisce l'intera visuale del client, così che
  ogni relay onesto sia invisibile e la selezione dei percorsi attinga solo a circuiti avversariali
  — richiede `A = 1`, quindi
  ```
        a  ≥  ⌈ 1 / f ⌉       classi sotto pieno controllo avversariale.
  ```
  Con lo strawman `f = 1/2`, **l'eclipse completo richiede che l'avversario possieda almeno
  2 delle ≥3 classi**; possederne una **qualsiasi** limita l'avversario a `f = 1/2` del
  campione e un eclipse completo è **strutturalmente impossibile** (le classi oneste
  consegnano ancora ≥ `1 − f` della visuale). Questa è la quantità esatta che GR-8 asseriva
  senza enunciarla: il cap converte «eclipse» da «possedere abbastanza relay» in «possedere
  abbastanza *classi indipendenti*», che è un problema strettamente più difficile, e con risorse
  diverse.

- **GR-19a (nomina l'assunzione, e dove fallisce).** Il limite in GR-19 vale
  **solo se le classi sono genuinamente indipendenti** — se compromettere la
  distribuzione dei ponti lungo il grafo sociale non dice all'avversario nulla su, e non gli dà
  alcun controllo su, i pari di gossip o i target di probe. **Fallisce** precisamente
  quando una parte controlla più di una classe alla volta:
  - un avversario che possiede **sia** il ponte lungo il grafo sociale **sia** i pari di gossip
    controlla `a = 2` classi e, a `f = 1/2`, raggiunge `A = 1` — un eclipse completo che il
    cap non previene, perché il cap limita *per classe*, e due classi che
    sono segretamente una sola parte non sono due classi;
  - un fallimento correlato (un unico hosting provider, un'unica giurisdizione, un'unica monocultura
    software dietro due classi nominali) collassa `m` verso 1 silenziosamente.
  Pertanto la protezione del cap è **esattamente forte quanto l'indipendenza delle
  classi**, e un client conforme DEVE (MUST) (a) ricavare le proprie classi da
  origini di fiducia dimostrabilmente diverse (un ponte introdotto da un amico non è
  indipendente dal gossip se l'amico è il pari di gossip), e (b) trattare un campione
  in cui le classi *concordano troppo perfettamente* su una visuale inusuale come lo stesso segnale di anomalia
  che la Parte 8 usa per la divergenza della mappa (ID-10) e la Parte 3 usa per lo steering
  (PS-17) — diffondilo via gossip, non fidartene. L'indipendenza è un'**assunzione che il client
  deve mantenere attivamente**, non una proprietà che ottiene gratis dal contare le classi.

### 6.2 Il limite dei sybil

- **GR-20 (i sybil gonfiano il conteggio grezzo, mai le risorse verificate o gli edge reali).**
  `[claim-critical]` Poiché le identità sono gratuite (GR-9), un avversario sybil imposta il
  **conteggio grezzo dei record** a qualunque valore desideri. Due quantità lato client che
  **non** può gonfiare limitano il danno:
  1. **Banda verificata che non ha.** `vbw` (GR-11) è la misurazione propria del
     client; un sybil di 10 000 identità a banda zero misura come 10 000
     relay di banda verificata ~0 e porta peso di selezione ~0 (PS-7). Per guadagnare
     *peso* l'avversario deve davvero muovere i byte — vedi GR-20a.
  2. **Edge genuini del grafo sociale.** Una classe di ponte stile Lox (GR-8) consegna fiducia
     lungo edge *umani*; un sybil può coniare identità ma non gli edge che
     le introducono, quindi la classe del grafo sociale ammette i sybil solo al ritmo con cui persone
     reali li raccomandano (che è l'intera ragione per cui quella classe esiste).
  La conseguenza operativa è **PS-10, ora quantificato**: la stima della dimensione utilizzabile
  DEVE (MUST) contare **solo i relay verificati indipendentemente e la diversità di AS
  osservata**, così che gonfiare il conteggio grezzo da `N` a `10N` sybil muove la
  stima della dimensione verificata di **0** (nessuno dei sybil supera la verifica), e un
  client non può essere ingannato ad adottare parametri `n, k` completi la cui diversità è falsa. Ciò che
  «conta solo il verificato» compra, in una riga: **la dimensione che guida la scelta dei parametri
  è invariante rispetto al gonfiaggio sybil** — l'avversario può far *sembrare* la rete
  arbitrariamente grande e non cambiare nulla su cui un client agisca.

- **GR-20a (un avversario dotato di risorse non è un sybil — è un avversario reale, costoso,
  accettato).** `[claim-critical]` Il rovescio di GR-20 è enunciato
  onestamente: un avversario che **ha davvero** la banda, la raccomandazione sociale,
  e la diversità di AS/giurisdizione **non** è sconfitto da alcuna difesa dai sybil,
  perché **non è un sybil** — è un genuino avversario a `k`-percorsi che ha pagato per
  le sue posizioni. Questo è il rischio residuo per progetto che il modello di minaccia già
  accetta (la riga `k`-percorsi: «alza `n`, `k` a piacere»), non una lacuna in questa parte.
  Le difese dai sybil alzano il costo dell'avversario da *gratuito* (coniare identità) a
  *risorse reali proporzionali all'influenza cercata*; non rendono e non possono rendere
  l'influenza non acquistabile. Un client NON DEVE (MUST NOT) presentare «resistente ai sybil» come «un avversario
  con risorse reali non può guadagnare posizione» — la prima è vera, la seconda è falsa
  ed è una minaccia diversa, nominata, accettata.

---

## 7. Cosa questo non risolve (OP-2 resta aperto)

**OP-2 non è risolto qui, e nessun requisito sopra pretende che lo sia.** Un allocatore
centrale — la bandwidth authority di Tor, lo snapshot firmato di Walking Onions — *risolverebbe*
sia sybil sia eclipse per decreto: pubblicherebbe una visuale fidata, e i
sybil non potrebbero iniettarvisi né un avversario potrebbe dare a una vittima una visuale privata
di essa. I-3 proibisce quell'allocatore, perché la parte che può pubblicare la visuale fidata
è anche la parte che può essere coercita, citata in giudizio o sequestrata per
pubblicarne una *avvelenata*, e un meccanismo di discovery con quel singolo punto è il
kill switch che l'intero progetto rifiuta. Avendolo rifiutato, ci resta un
**limite, non una cura**:

- **Non esiste alcun meccanismo solo-overlay che renda il campionamento di gossip pienamente
  a prova di sybil/eclipse.** Ogni difesa sopra è una *disciplina lato client di verifica delle
  risorse o di mixing delle fonti*, e ciascuna ha una cucitura dichiarata:
  - il limite di eclipse (GR-19) vale solo sotto l'indipendenza delle classi, e **collassa
    quando una parte possiede ≥ `⌈1/f⌉` classi** (GR-19a) — un avversario abbastanza ricco da
    essere l'amico che ti consegna il ponte **e** i pari con cui fai gossip
    ti mette in eclipse, e l'overlay non sa distinguere «due classi» da «una parte che indossa
    due cappelli»;
  - il limite dei sybil (GR-20) ferma il gonfiaggio *gratuito* ma non la posizione *pagata*
    (GR-20a) — la verifica alza il costo, non lo limita;
  - il probe di banda (§6) misura il throughput, non l'onestà o la posizione (GR-18) —
    un relay può superare ogni probe ed essere comunque dell'avversario, e un sybil veloce con
    capacità reale è un avversario reale (GR-20a). Un probe chiude la domanda di *progetto* di GR-7;
    non chiude OP-2.
- **Il bootstrap sotto eclipse è il residuo difficile.** Un client messo in eclipse dal suo primo
  contatto (GR-10) vede solo classi avversariali, misura solo relay avversariali come
  «veloci» e sente solo l'accordo dell'avversario — ogni meccanismo di corroborazione in
  questa parte ha bisogno di *un punto di osservazione onesto* per funzionare, e un avversario che fornisce
  l'intero mondo del client dal primo pacchetto gli nega quel punto di osservazione. Questa è
  la stessa forma del bootstrap TOFU della Parte 8 (ID-8): le difese **rilevano** una visuale
  cattiva una volta raggiunta una fonte onesta e rendono mantenere un client in eclipse
  *per sempre* costoso — non **prevengono** l'eclipse iniziale. «Rilevare e
  rendere costoso l'eclipse permanente», non «prevenire l'eclipse», è l'affermazione onesta, ed è
  l'affermazione che la UI enuncia.

**Ciò che il progetto fa, precisamente, è limitare l'attacco lungo tre assi:**
verifica delle risorse (GR-11/GR-20: i sybil gratuiti non comprano nulla), mixing delle fonti
(GR-19: l'eclipse ha bisogno di ≥ `⌈1/f⌉` classi indipendenti, non solo di molti relay), e il
grafo sociale (GR-20: gli edge non possono essere coniati). Il residuo che rimane dopo tutti e
tre è: **un avversario con risorse reali, raccomandazione sociale reale attraverso molteplici
classi che sembrano genuinamente indipendenti, e la capacità di fornire l'intera prima visuale di un
client appena nato può gonfiare via sybil l'influenza che ha pagato e mettere in eclipse un client che
circonda — e l'overlay non può, da dentro, provare di essere circondato.**
Quel residuo è OP-2, ed è aperto.

### 7.1 I limiti sono le curve del simulatore

Questi requisiti sono falsificabili, non retorici: un modello di sybil/eclipse è
misurato da `poc/sybil_sim.py` insieme allo sweep `infer_error` esistente di `network_sim.py` (il
simulatore già modella un `gossip_sample` parziale per-client — la visuale esatta che un
avversario di eclipse modella — e già separa la ground truth dalla convinzione del
client). I limiti del progetto sono le curve che DEVE (MUST) misurare:

- **la curva di eclipse:** frazione del campione dell'avversario `A` contro numero di classi
  controllate `a`, che DEVE (MUST) seguire `min(1, a·f)` di GR-19 e DEVE (MUST) mostrare il ginocchio a
  `a = ⌈1/f⌉` (eclipse completo) — e DEVE (MUST) mostrare che a `a = 1` la visuale onesta non
  scende mai sotto `1 − f`;
- **la curva di gonfiaggio sybil:** stima della dimensione verificata (PS-10) contro conteggio grezzo dei sybil,
  che DEVE (MUST) essere **piatta** — l'affermazione di GR-20 che gonfiare il conteggio grezzo muove la
  stima verificata di zero è esattamente questa piattezza, e una curva non piatta falsifica
  GR-20;
- **l'interazione del churn:** probabilità di eclipse contro tasso di churn del campione, poiché un
  client che ricampiona più in fretta incontra un punto di osservazione onesto prima (l'affermazione «rileva, rendi
  costoso l'eclipse permanente» è un tasso, e il simulatore deve metterci sopra un numero).

Se il simulatore mostra la curva di eclipse che batte `min(1, a·f)`, o la
curva di gonfiaggio sybil che sale, il limite è sbagliato e questa estensione è rotta —
attacca il modello, poi questo testo. L'unica cosa che non può essere resa una curva è l'
eclipse al primo contatto di un client senza alcun punto di osservazione onesto: quello non ha
misurazione interna all'overlay, perché la vittima, per definizione, non può vedere fuori dal
mondo dell'avversario. È il residuo di OP-2, dichiarato, ed è perché questa parte
dice *limita*, non *risolve*.

---

## Requisiti introdotti qui

- **GR-11** — la banda verificata è un'auto-misurazione per-client (`vbw`), mai una
  cifra pubblicata o condivisa; le dichiarazioni non sottoposte a probe contano come basse.
- **GR-12** — il probe è un round-trip sigillato con il relay misurato come
  hop intermedio; chi fa il probing non è mai nella visuale del relay.
- **GR-13** — indistinguibilità: il traffico di probe DEVE (MUST) essere identico in byte e timing
  al vero traffico relayato (I-4), così che un relay non possa servire i probe e affamare i payload.
- **GR-14** — un probe costa a chi fa il probing un budget di byte limitato e pre-pagato, limitato in frequenza
  per target e in aggregato.
- **GR-15** — il probe è un anello chiuso (ritorna solo a chi fa il probing); non può nominare alcuna
  destinazione di terze parti, quindi non può amplificarsi in un riflettore di DoS.
- **GR-16** — `vbw` è un aggregato robusto su vari circuiti indipendenti, prendendo
  il massimo throughput sostenuto, con confidenza che decade con l'età e un livello minimo conservativo.
- **GR-17** — i numeri di throughput non sono mai diffusi via gossip come banda; solo la liveness/
  raggiungibilità è una classe di fonte condivisibile — ciascun client pondera in base alla propria misurazione.
- **GR-18** — degradazione onesta: un probe misura il throughput, non l'onestà, non la
  posizione, non l'identità distinta.
- **GR-19** — il cap di GR-8 produce il limite di eclipse `A ≤ min(1, a·f)`; l'eclipse completo
  ha bisogno di `a ≥ ⌈1/f⌉` classi controllate (≥2 a `f = 1/2`).
- **GR-19a** — il limite assume l'indipendenza delle classi e fallisce quando una parte possiede
  ≥ `⌈1/f⌉` classi; l'indipendenza è mantenuta, non gratuita.
- **GR-20** — i sybil gonfiano il conteggio grezzo dei record ma mai la banda verificata o gli edge sociali
  reali; la stima della dimensione verificata (PS-10) è invariante rispetto al gonfiaggio sybil.
- **GR-20a** — un avversario dotato di risorse non è un sybil ma un avversario reale, costoso, accettato
  a `k`-percorsi; la verifica alza il costo, non rende la posizione non acquistabile.

GR-11 e GR-19 sono i due portanti: ciascun client misura la propria banda
(nessuna autorità), e il cap di mixing delle fonti converte l'eclipse da «possedere abbastanza relay»
in «possedere abbastanza classi indipendenti». Entrambi sono **limitati, non assoluti** — il
probe di GR-11 non può leggere l'onestà o la posizione (GR-18), e GR-19 collassa quando le classi
sono segretamente una sola parte (GR-19a). OP-2 non è risolto: non esiste alcun meccanismo
solo-overlay che renda il campionamento di gossip pienamente a prova di sybil/eclipse, e un client
messo in eclipse dal suo primo contatto non ha alcun punto di osservazione onesto per rilevarlo. Il progetto
limita l'attacco da verifica delle risorse, mixing delle fonti e grafo sociale;
non lo elimina. Questo è il residuo onesto, e le curve del simulatore
sono dove è tenuto ai suoi stessi numeri. Rompilo nello stesso modo in cui il resto della spec
è rotto: trova un bit di probe su cui un relay possa basarsi (sconfiggendo GR-13), un modo in cui il probe
nomina una vittima (sconfiggendo GR-15), un sybil che muove la stima della dimensione verificata
(sconfiggendo GR-20), o un eclipse che batte `min(1, a·f)` sotto classi genuinamente
indipendenti (sconfiggendo GR-19) — e hai rotto questa estensione.


## 8. Cosa questa parte non decide

La resistenza a sybil/eclipse oltre GR-8/GR-9 (OP-2), il protocollo di probing (GR-7),
il bootstrap senza contatti (OP-7). Esistono issue numerate per ciascuno.
