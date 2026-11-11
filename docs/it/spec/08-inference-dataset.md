# Specifica ScrambNet — Parte 8: Il dataset di inferenza

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([en](../../en/spec/08-inference-dataset.md)).

**Stato: BOZZA (DRAFT), e un rischio di ricerca dichiarato.** Questa parte decide
come un client ottiene la mappa IP-to-AS (e la giurisdizione a grana grossa) da
cui la Parte 3 inferisce (PS-4), sotto I-3 — nessuna autorità — contro relay e
host del dataset che mentono su tutto tranne ciò che un hash o una firma vincola.
I valori strawman sono contrassegnati con `(s)`. L'*uso* della mappa per la
verifica della disgiunzione è OP-1; la sua *distribuzione* è l'item 2.3 della
roadmap.

La decisione di fondo è enunciata nel §1 e difesa nel resto. Leggi prima il §1 e
il §9 (il residuo): insieme dicono cosa compra questa parte e cosa ammette di non
poter comprare.

## 1. La decisione, in due frasi

- **Non esiste una mappa canonica né un'autorità della mappa.** Il dataset è un
  **artefatto riproducibile e indirizzato per contenuto** che qualunque parte
  ricostruisce byte-per-byte da input pubblici; due client concordano non perché
  si fidano di un firmatario ma perché hanno calcolato lo **stesso hash** (ID-1,
  ID-5). Una radice canonica firmata da un insieme fisso sarebbe un'autorità di
  directory sotto un altro nome, e I-3 lo vieta.
- **L'accordo avviene per riproduzione; la pubblicazione avviene tramite un log
  di trasparenza append-only su cui chiunque può scrivere; la fiducia al primo
  recupero è TOFU, dichiarata come tale.** Il log non *benedice* una mappa — la
  marca temporalmente e rende rilevabile l'equivocazione (ID-6, ID-7). La prima
  mappa di un client nuovo è un momento trust-on-first-use che il gossip
  successivo gli permette di **rilevare** come cattivo, non di **prevenire** (§7).

Quindi l'esito onesto che la roadmap ha segnalato è quello reale: **mappa TOFU +
log di trasparenza + gossip delle anomalie, non una mappa canonica.** Tutto ciò
che segue è la costruzione che rende concreto "riproducila tu stesso, e rileva
chiunque abbia mentito", e il §9 è il residuo che nessuna quantità di costruzione
rimuove.

## 2. Ambito e la trappola che questa parte evita

La Parte 3 (PS-4, PS-5) richiede che ogni client inferisca l'AS e la giurisdizione
a grana grossa di un relay *dai suoi `addrs`*, usando il **proprio** dataset del
client, mai l'autodichiarazione di un relay (GR-3). Questa parte riguarda solo
**da dove proviene quel dataset e come due client sanno di detenere lo stesso**
senza una parte fidata in nessun punto della catena — build, pubblicazione o
bootstrap.

La trappola è sottile e va nominata: il design "senza fiducia" più facile è uno
snapshot canonico firmato, pubblicato da un piccolo insieme di manutentori. Quella
è esattamente l'autorità Walking-Onions che questo progetto si è negato per i
relay (ambito GR-1), ora reintrodotta di nascosto per la geografia. Un firmatario
della mappa che possa silenziosamente distribuire una mappa che etichetti male un
blocco di AS può far *sembrare* disgiunti a ogni client i relay co-locati di un
avversario — un eclipse a granularità geografica che sconfigge la Parte 3 tanto
sicuramente quanto una directory di relay difettosa. Quindi l'insieme di
firmatari è la minaccia, e il design non deve averne uno con quel potere.

- **ID-1 (nessuna autorità della mappa). [normativo]** Nessun passo
  dell'ottenere, validare o aggiornare il dataset DEVE (MUST) richiedere di
  fidarsi che una particolare parte abbia prodotto, firmato o benedetto la mappa;
  equivalentemente, ottenere e validare la mappa DEVE (MUST) essere possibile
  usando solo surrogati non fidati. Le uniche operazioni fidate sono: (a)
  ricalcolare un hash, e (b) ricostruire l'artefatto da input pubblici e
  confrontare. Qualunque elemento di design che non possa essere sostituito da un
  surrogato non fidato che esegue (a) o (b) è un difetto sotto I-3 e DEVE (MUST)
  essere rimosso o dichiarato nel §9.

## 3. Cos'è la mappa

- **ID-2 (forma dell'artefatto).** Il dataset è un singolo artefatto compresso,
  la **mappa**, contenente, per lo spazio IPv4 e IPv6:
  - una tabella **prefisso-IP → origin-AS** (lookup per longest-prefix-match), e
  - una tabella **AS → giurisdizione a grana grossa**, dove "giurisdizione" è
    un'etichetta a **livello di paese** derivata dall'allocazione RIR,
    deliberatamente grossolana — una granularità più fine è rumore che questa
    parte non pretenderà di risolvere (§9).
  La mappa porta un'intestazione autodescrittiva: versione del formato `1`,
  l'**epoch** dello snapshot (ID-4), il manifest esatto degli input (ID-3) e la
  versione dello strumento di build. L'artefatto è indirizzato da `H =
  BLAKE2s(artifact)` (l'hash della suite, Parte 0); `H` è l'unico nome della
  mappa. Non esiste una stringa di versione leggibile dall'uomo che possa essere
  fidata al posto di `H`.
- **ID-2a (il lookup è totale).** Ogni lookup DEVE (MUST) restituire o un concreto
  `(AS, jurisdiction)` o il valore esplicito **`unknown`**. `unknown` è una
  risposta di prima classe, non un errore, e la Parte 3 (PS-5) già lo tratta
  conservativamente (`unknown` condivide con tutto). La mappa NON DEVE (MUST NOT)
  tirare a indovinare per evitare un `unknown`; una risposta fabbricata è peggiore
  di una lacuna ammessa, perché sconfigge silenziosamente PS-5.

## 4. Come viene costruita la mappa (riproducibilmente, da input pubblici)

La build è una **funzione pura di input pubblici nominati verso un artefatto
byte-identico**. Il determinismo è tutto il gioco: se due parti oneste possono
divergere, l'uguaglianza degli hash (ID-5) smette di significare "stessa mappa" e
il design collassa nel bisogno di un'autorità che sciolga i pareggi.

```
  INPUT PUBBLICI (pinnati per hash di contenuto nel manifest, ID-3)
  ┌────────────────────────┐   ┌────────────────────────┐
  │ RouteViews + RIPE RIS  │   │ 5 file di delega RIR   │
  │ dump BGP MRT RIB       │   │ (AS → paese)           │
  │ (prefisso → origin-AS) │   │                        │
  └────────────────────────┘   └────────────────────────┘
              │         epoch = ultimo dump ≤ confine 00:00 UTC (ID-4)
              └───────────────┬───────────────┘
                              ▼
            ┌───────────────────────────────────┐
            │ BUILD DETERMINISTICA (fn pura)    │
            │ ordine fisso (ID-4a), tie-        │
            │ breaking fisso (ID-4b), nessun    │
            │ input fluttuante (ID-4c),         │
            │ container canonico (ID-4d)        │
            └───────────────────────────────────┘
                              ▼
                      artefatto mappa
                              │
                              ▼
                   H = BLAKE2s(artifact)   ← l'UNICO nome della mappa (ID-2)

  Alice ─ stessi input ─▶ H_A        Due parti oneste che pinnano gli
  Bob   ─ stessi input ─▶ H_B        stessi input ottengono H_A == H_B.
                                      L'accordo è uguaglianza degli hash
                                      (ID-5), non fiducia in un firmatario.
                                      La riproduzione è l'arbitro.
```

- **ID-3 (input pubblici, pinnati per contenuto). [normativo]** La mappa DEVE
  (MUST) essere costruita solo da input che siano pubblici, riproducibili, ed essi
  stessi pinnati per contenuto nel manifest dell'artefatto tramite i propri hash:
  - **Tabelle di routing BGP** per l'origin-AS: i collector del progetto
    **RouteViews** e i collector **RIPE RIS** (dump MRT `RIB`). Questi sono gli
    archivi BGP pubblici multi-vantaggio standard; usare diversi collector da
    entrambi i progetti è di per sé una misura di diversità (la vista di nessun
    singolo collector è autorevole, ID-3a).
  - **Statistiche di delega RIR** per il mapping AS → paese: i file
    **delegated-extended** pubblicati dai cinque RIR (ARIN, RIPE NCC, APNIC,
    LACNIC, AFRINIC). Questi danno codici paese di allocazione per numeri di AS e
    blocchi di indirizzi senza che nessuno si autodichiari.
  Il manifest DEVE (MUST) elencare ogni file di input per hash di contenuto
  indipendente dall'URL e per il timestamp dichiarato dalla sorgente, così che
  siano gli input — non un server — a definire la build. Una parte ricostruisce
  recuperando gli input con quegli hash da **qualunque** mirror (I-3: la sorgente
  è sostituibile; i byte sono pinnati).
- **ID-3a (risoluzione dell'origine multi-vantaggio).** L'origin AS per un
  prefisso DEVE (MUST) essere risolto attraverso **tutti** i collector del
  manifest tramite una regola fissa (ID-4b), non da un solo collector. Un prefisso
  visto con origini in conflitto tra i punti di vantaggio è risolto
  deterministicamente e, dove il conflitto è reale (MOAS — multiple-origin AS),
  registrato come un **insieme**, che la Parte 3 tratta come "possibilmente uno
  qualunque di questi", cioè condiviso conservativamente (§9). La mappa NON DEVE
  (MUST NOT) sceglierne silenziosamente uno.

### 4.1 Pericoli per il determinismo e come la build li pinna

Ciascun pericolo qui sotto è un punto in cui due builder onesti potrebbero
produrre byte diversi. La procedura di build DEVE (MUST) eliminarne ciascuno; una
build che non lo fa è non conforme perché non può supportare ID-5.

- **ID-4 (epoch dello snapshot — timing del dump). [normativo]** I dati BGP e RIR
  cambiano in continuazione, quindi "il dump corrente" non è una funzione. La
  build DEVE (MUST) pinnare un singolo **confine di epoch**: un istante UTC su una
  cadenza fissa (strawman: lo snapshot delle **00:00 UTC** su una cadenza
  **settimanale (s)** — i commit della Parte 0 già usano UTC), e DEVE (MUST)
  usare, per ogni collector/RIR del manifest, l'**ultimo dump il cui timestamp
  dichiarato dalla sorgente è ≤ il confine di epoch**. Due builder che prendono di
  mira lo stesso epoch selezionano quindi gli stessi file di input a prescindere
  da quando vengono eseguiti. L'epoch è nell'intestazione dell'artefatto (ID-2) e
  nella preimmagine di `H`.
- **ID-4a (ordinamento).** Tutte le tabelle DEVONO (MUST) essere emesse in un
  **ordine totale fisso**: prefissi ordinati per (famiglia di indirizzi, indirizzo
  di rete numerico, lunghezza del prefisso); voci AS per ASN numerico;
  giurisdizioni per la loro stringa fissa di codice paese. Nessun ordine di
  iterazione di mappa, ordine di hash-table o ordine dei file di input può
  raggiungere l'output.
- **ID-4b (il tie-breaking è specificato, non definito dall'implementazione).
  [normativo]** Ogni punto in cui i dati sono ambigui DEVE (MUST) avere una regola
  scritta in questa parte, senza alcun "scegline uno" lasciato all'implementatore:
  - *Origin AS tra i collector:* prendi l'insieme di origini osservato; se è un
    singolo AS, emettilo; se multipli (MOAS), emetti l'insieme completo ordinato
    in modo ascendente. Non collassare mai un MOAS a un solo AS per popolarità —
    quella è una supposizione (§9).
  - *Prefissi sovrapposti:* la semantica di longest-prefix-match è preservata
    memorizzando tutti i prefissi; è il lookup, non la build, a risolvere la
    specificità.
  - *Conflitto AS-paese tra i RIR:* se i file di delega sono in disaccordo sul
    paese di un AS, emetti `unknown` per la giurisdizione di quell'AS. Un
    disaccordo tra registri pubblici è esattamente un caso che la mappa non deve
    risolvere per decreto.
- **ID-4c (input fluttuanti vietati).** La build NON DEVE (MUST NOT) consultare
  alcun input non presente nel manifest — nessun DNS live, nessun WHOIS al tempo
  della build, nessun database di geolocalizzazione sotto una licenza che ne
  vieti la ridistribuzione o che non sia riproducibile, nessun feed commerciale di
  IP-intelligence. Ogni byte di output risale a un input pubblico hashato. (Questo
  esclude i feed comodi-ma-non-verificabili; la loro accuratezza non vale
  l'autorità che reintroducono.)
- **ID-4d (container canonico).** La compressione e il framing dell'artefatto
  DEVONO (MUST) essere deterministici (codec fisso, livello fisso, nessun
  timestamp o nome di file nei metadati del container). La build è specificata in
  modo abbastanza stretto da rendere riproducibile lo stesso strumento di build
  conforme (roadmap 4.2), e DEVE (MUST) esistere un **test vector della mappa**
  cross-implementazione (un manifest di input → l'`H` atteso) così che una seconda
  implementazione possa dimostrare di costruire l'artefatto identico (si collega
  alla roadmap 3.2).

## 5. Come due client concordano di detenere la stessa mappa

- **ID-5 (l'accordo è uguaglianza degli hash, nient'altro). [normativo]** Due
  client detengono la stessa mappa **se e solo se** i loro hash di artefatto `H`
  sono uguali. Il confronto è un controllo di uguaglianza di 32 byte; non ha
  bisogno di firmatario, quorum o autorità. I client fanno gossip di `H` (ID-8);
  un `H` uguale è prova della stessa mappa, un `H` diverso è prova che
  differiscono e DEVE (MUST) essere segnalato all'utente come una **divergenza**
  (ID-9), mai riconciliato silenziosamente verso l'una o l'altra parte.
- **ID-5a (la ricostruzione è l'arbitro).** Quando due client detengono un `H`
  diverso per lo stesso epoch, la disputa è risolvibile da **chiunque**, senza
  appello a un'autorità: ricostruisci dagli input del manifest (ID-3) e vedi quale
  `H` gli input pubblici producono effettivamente. Una mappa il cui `H` non può
  essere riprodotto dal suo manifest dichiarato, per definizione, non è la mappa di
  quegli input, e DEVE (MUST) essere rifiutata (ID-5b). Questa è la proprietà che
  permette al sistema di non avere autorità: *la verità è riproducibilità, non
  firma.*
- **ID-5b (rifiuta ciò che non è riproducibile).** Un client che ha gli input (o
  li recupera) e trova che `H ≠ BLAKE2s(rebuild(manifest))` DEVE (MUST) scartare
  quella mappa e DOVREBBE (SHOULD) fare gossip della discrepanza come anomalia
  (ID-10). Un client senza la banda per ricostruire PUÒ (MAY) accettare una mappa
  secondo i termini TOFU/consenso (§6, §7) ma DEVE (MUST) tracciarla come **non
  verificata** finché esso (o un peer con cui poi concorda) non ricostruisce.

## 6. Il log di trasparenza (e perché non è l'autorità)

L'uguaglianza degli hash dice a due client che *differiscono*; non difende di per
sé contro un avversario che dà a client **diversi** mappe **diverse** mantenendo
ciascun client internamente coerente — un **attacco di split-view (equivocazione)**.
Il log di trasparenza esiste esattamente per quella minaccia e per nient'altro.

```
  L'ATTACCO SPLIT-VIEW, E COME IL GOSSIP LO COGLIE

  Un log ostile prova a mostrare due viste che non si incontrano mai:

     log ──root X (mappa H_good)─▶  Alice   "la mia mappa è corroborata"
         └─root Y (mappa H_bad )─▶  Bob     "la mia mappa è corroborata"

  Ogni client da solo vede una storia coerente. Ma le root sono diffuse
  via gossip sul canale GR-6 (ID-7a), quindi un terzo client Carol le
  sente ENTRAMBE:

        Alice ──root X──┐
                        ├──▶  Carol esige una PROVA DI CONSISTENZA
        Bob   ──root Y──┘     tra X e Y.
                             Se X e Y non sono estensioni di un unico
                             albero append-only, la prova FALLISCE:
                             ✗  prova crittografica che il log ha
                                equivocato
                                → log marcato ostile, diffuso via gossip (ID-10)

  Il log non dice mai quale mappa sia BUONA — lo fa la riproduzione (ID-5a).
  Rende solo rilevabile il mentire a persone diverse allo stesso tempo.
  Chiunque può appendere (ID-7, senza permessi), quindi il log è una
  bacheca, non un'autorità — ed è ciò che lo tiene fuori da I-3.
```

- **ID-6 (cos'è il log).** Il log è un **albero di Merkle append-only** (struttura
  RFC 6962 / Certificate-Transparency: un albero di Merkle su una sequenza di
  foglie, con prove di inclusione e prove di consistenza tra due dimensioni
  dell'albero). Ogni **foglia** è un annuncio di mappa: `(epoch, H, manifest-hash)`.
  Lo stato del log è riassunto dalla sua **signed tree head** — qui, una **root
  hash** a una dimensione dell'albero. Il log dimostra due cose
  crittograficamente: che un dato `H` **è incluso** (prova di inclusione) e che il
  log **è solo cresciuto, non ha mai riscritto la storia** (prova di consistenza).
  Non dimostra nulla sul fatto che `H` sia una mappa *buona* — lo fa la
  riproduzione (ID-5a).
- **ID-7 (chi può appendere — senza permessi, quindi non è un'autorità).
  [normativo]** **Chiunque** PUÒ (MAY) appendere una foglia che annuncia una mappa
  che ha costruito; non c'è alcun appender privilegiato, nessuna allow-list,
  nessun insieme di firmatari la cui firma renda ufficiale una mappa. Il log non è
  quindi la cosa di cui ci si fida — è una **bacheca testimoniata e a prova di
  manomissione**. Il suo unico potere è rendere *rilevabile* l'equivocazione; non
  ha **alcun potere di scegliere la mappa**, ed è questo che lo tiene fuori dal
  divieto di I-3. Un log che limitasse gli append dietro un insieme di firmatari
  SAREBBE l'autorità di directory che I-3 vieta, e un tale design è non conforme
  (ID-1).
- **ID-7a (rilevamento dell'equivocazione tramite root diffuse via gossip).
  [normativo]** La difesa contro una split view **non** è fidarsi dell'operatore
  del log; è **fare gossip delle signed tree head del log sul canale di gossip GR
  esistente** (GR-6) e pretendere **prove di consistenza** tra due qualunque root
  che un client veda. Se un log presenta mai due tree head che non sono estensioni
  consistenti l'una dell'altra — la firma dell'equivocazione — qualunque client
  che osservi entrambe (direttamente o tramite una root diffusa via gossip da un
  peer) ha **prova crittografica** che il log ha mentito, e DEVE (MUST) trattare
  quel log come ostile (ID-10). Poiché le root sono diffuse via gossip su larga
  scala (GR-6 mescola le sorgenti, GR-8), un log non può mostrare al client A la
  root X e al client B la root Y a lungo senza che qualche client detenga entrambe
  e lo colga.
- **ID-7b (log multipli, nessuno canonico). [normativo]** **Non c'è un singolo
  log.** I client DEVONO (MUST) supportare **diversi log indipendenti** e trattare
  una mappa come corroborata-dal-log solo se compare, con root diffuse via gossip
  consistenti, in un quorum configurabile dei log che il client osserva (strawman:
  **≥2 dei log nel suo insieme (s)**). Questo rimuove l'ultimo punto singolo:
  nessun singolo operatore di log è portante, e l'insieme di log di un client —
  come il suo campione di relay — è diverso e sostituibile (razionale GR-8
  applicato ai log). Un log che si spegne viene aggirato, esattamente come un
  relay che si spegne.
- **ID-7c (il log memorizza impegni, non la mappa).** Le foglie portano `(epoch,
  H, manifest-hash)` — decine di byte — mai l'artefatto. La mappa stessa è
  recuperata indirizzata per contenuto tramite `H` da qualunque mirror o peer
  (ID-8); il log attesta solo *quali* valori `H` sono stati annunciati e *quando*,
  così che lo storage del log resti banale e nessun log diventi il collo di
  bottiglia della distribuzione.

## 7. Il paradosso del bootstrap, enunciato onestamente

Un client nuovo non ha alcun campione di relay che possa valutare né alcuna mappa
precedente; deve recuperare la sua **prima** mappa su percorsi la cui disgiunzione
**non può ancora verificare** (quella verifica ha bisogno della mappa stessa che
sta recuperando). Questa è una genuina dipendenza circolare, e questa parte non
pretende di romperla.

```
  LA PRIMA MAPPA È TRUST-ON-FIRST-USE (ID-8) — E IL SUO DANNO È LIMITATO

  client nuovo ─▶ recupera la prima mappa su canali non ancora valutabili
                      │
                      ▼
        ┌───────────────────────────┐  UI: "ti stai fidando della tua
        │ stato: UNVERIFIED-TOFU    │       prima mappa; non ancora
        │ (mostrato all'utente)     │       corroborata"
        └─────────────┬─────────────┘
                      │  nei prossimi epoch, O l'UNO O l'ALTRO:
         ┌────────────┴─────────────┐
         ▼                          ▼
   ricostruisci dagli input    gossip root + H dei peer
   (ID-5a): H combacia?        accordo sopra la soglia?
         │                          │
    sì ──┴── no                sì ──┴── no (continua a divergere)
     ▼       ▼                  ▼       ▼
  VERIFICATO ANOMALIA      VERIFICATO   ANOMALIA diffusa via gossip (ID-10),
             (ID-5b,10)                 utente avvisato (ID-8b)

  Anche una prima mappa PIENAMENTE avversaria è limitata (ID-8a):
    1. il livello minimo I-2 è intatto, MA una mappa di DIROTTAMENTO può
       manovrare l'avversario oltre k (far collassare il bacino onesto,
       PS-12) -> il contenuto PUÒ cadere per una mappa non verificata sopra
       una soglia di proprietà del ~15%. Non solo metadati. Delimitato dal
       margine k/n + difese PS-12, non da un "non può".
    2. temporanea + rilevabile — l'avversario deve eclissare il client
       PER SEMPRE per tenerla nascosta (è OP-2, non una nuova debolezza qui).
    3. non falsificabile — l'avversario non può far ricostruire gli input
       pubblici verso una H cattiva. Una ricostruzione, o un peer onesto
       che l'ha fatta, converge alla verità.
```

- **ID-8 (il bootstrap è trust-on-first-use, dichiarato). [normativo]** La prima
  mappa che un client nuovo ottiene è una decisione **TOFU**. Il client DEVE
  (MUST) ottenerla su quanti più canali **indipendenti** ha (strawman: la linea di
  bridge out-of-band di GR-10, più due o più mirror pubblici raggiunti su reti
  distinte (s)), DEVE (MUST) richiedere lo **stesso `H`** da tutti prima di
  accettarla provvisoriamente, e DEVE (MUST) registrare la mappa come
  **unverified-TOFU** finché non (a) ricostruisce dagli input (ID-5a) o (b)
  accumula root diffuse via gossip consistenti e accordo di `H` tra peer (ID-7a,
  ID-9) sopra una soglia di confidenza. Il client DEVE (MUST) far emergere questo
  stato: *ti stai fidando della tua prima mappa; non è ancora stata corroborata.*
- **ID-8a (limite su ciò che una prima mappa cattiva compra all'avversario).
  [normativo]** Un avversario che controlla l'intero primo recupero di un client
  nuovo può consegnargli una mappa che etichetta male gli AS così che relay
  co-locati sembrino disgiunti. Il limite sul danno è triplice e DEVE (MUST)
  essere preservato dal design:
  1. **Il livello minimo I-2 stesso è intatto; ma una mappa ostile PUÒ
     raggiungere il contenuto tramite dirottamento.** Il livello minimo di Shamir
     sotto `k` è matematico e una mappa cattiva non può abbassarlo. Ciò che una
     mappa cattiva *può* fare — e questo corregge una precedente sopravvalutazione
     — è **manovrare l'avversario oltre `k`**: una mappa che dà ai relay co-locati
     dell'avversario AS falsi distinti e dà ai relay onesti AS falsi collidenti fa
     collassare il bacino di candidati onesti e dirotta la selezione disgiunta per
     AS su `≥ k` circuiti dell'avversario in modo deterministico (la costruzione
     completa e le sue difese sono **PS-12**; dimostrato contro il simulatore,
     ~100% di rottura del contenuto al ~15% di proprietà). Quindi una mappa cattiva
     **non** è un attacco ai soli metadati: per un client che ha accettato una
     mappa non verificata e non può ancora ricostruire, il livello minimo di
     contenuto può cadere. Il limite onesto è perciò condizionale, non assoluto:
     una mappa cattiva raggiunge il contenuto **solo** quando l'avversario possiede
     già abbastanza del campione *raggiungibile* del client da dominare il bacino
     post-collasso (territorio di soglia, PS-12) **e** le difese di PS-12 non sono
     applicate. L'inaccuratezza casuale (rumore) erode comunque il collegamento
     molto più velocemente del contenuto; una mappa *scelta* no. Le affermazioni 2
     e 3 qui sotto sono ciò che mantiene limitato anche questo.
  2. **È temporanea e rilevabile, non permanente.** Nel momento in cui il client
     fa gossip della sua root/`H` (ID-9) o ricostruisce (ID-5a), una mappa che
     nessun peer onesto o input pubblico corrobora salta all'occhio. L'avversario
     deve tenere il client eclissato **per sempre** per mantenere non esposta la
     mappa cattiva — che è il problema di eclipse OP-2, non una nuova debolezza
     che questa parte introduce.
  3. **Non può falsificare la riproduzione.** L'avversario può distribuire un `H`
     cattivo, ma non può far ricostruire gli input pubblici verso quell'`H`
     (ID-5a). Un client che ricostruisce mai, o che incontra mai anche solo un
     peer che l'ha fatto, converge alla mappa reale.
- **ID-8b (rileva, non pretendere di prevenire). [normativo]** Questa parte
  fornisce **rilevamento di un bootstrap cattivo a posteriori**, non la sua
  prevenzione. Un client conforme NON DEVE (MUST NOT) presentare una mappa TOFU
  come verificata, DEVE (MUST) rivalutarla man mano che arriva il gossip e
  (facoltativamente) accumulare ricostruzioni, e DEVE (MUST) avvisare se la
  corroborazione non arriva entro una finestra configurabile (strawman: pochi
  epoch (s)). "Non possiamo prevenire una prima mappa cattiva; rendiamo costoso ed
  eventualmente impossibile tenerla non rilevata" è l'affermazione onesta, ed è
  l'affermazione che l'interfaccia enuncia.

## 8. Conviverci: gestione del refresh e della divergenza

- **ID-9 (freschezza della mappa e gossip).** I client DEVONO (MUST) fare refresh
  verso la mappa dell'epoch corrente (cadenza ID-4) e DEVONO (MUST) fare gossip
  del loro `(epoch, H)` corrente e delle root del log che detengono sui batch
  GR-6, soggetti al mescolamento delle sorgenti GR-8 così che nessuna singola
  classe di peer possa dominare la vista di un client su quale mappa sia corrente
  (la stessa difesa dall'eclipse, riusata). Un client NON DEVE (MUST NOT) pesare
  una mappa in base a quanti peer la riportano *prima* di applicare la regola
  "conta solo le sorgenti verificate indipendentemente" di GR-8/PS-10 — un sybil
  non può votare una mappa cattiva nel consenso per pura numerosità (si collega a
  OP-2).
- **ID-9a (la divergenza è mostrata, non nascosta).** Quando l'`H` di un client
  differisce da un quorum corroborato (ID-7b) per lo stesso epoch, DEVE (MUST)
  trattare la propria mappa come sospetta, tentare la ricostruzione o il
  ri-recupero, e riportare la divergenza all'utente nella superficie di onestà
  esistente della Parte 3 (PS-9): *la tua vista della geografia della rete è in
  disaccordo con quella dei tuoi peer; i giudizi di disgiunzione potrebbero essere
  sbagliati.* Il silenzio qui lascerebbe correre non visto un eclipse geografico.
- **ID-10 (gossip delle anomalie). [normativo]** Tre eventi sono **anomalie** di
  cui ogni client DEVE (MUST) fare gossip quando le rileva, perché sono le firme
  osservabili degli attacchi che questa parte non può prevenire, ma solo far
  emergere: (a) un `H` che fallisce la riproduzione dal suo manifest (ID-5b); (b)
  un log che presenta root inconsistenti, cioè equivocazione dimostrata (ID-7a);
  (c) una divergenza persistente di `H` contro un quorum corroborato (ID-9a). Il
  gossip delle anomalie è il segnale immunitario della rete; un client NON DEVE
  (MUST NOT) sopprimerlo per apparire sano.

## 9. La giunzione con la governance degli aggiornamenti (OP-8 / item 4.1)

I publisher delle root della mappa e i firmatari dei rilasci software sembrano
poter essere un unico meccanismo. **Posizione: tenerli separati nella fiducia,
anche se condividono gli strumenti.** Il ragionamento è che hanno **forme di
fiducia opposte**:

- **ID-11 (la fiducia nella mappa è riproduzione, non firma). [normativo]** La
  mappa è fidata perché **si ricostruisce da input pubblici** (ID-5a); la sua
  correttezza **non** poggia su *chi* l'ha pubblicata. Un binario di rilascio, al
  contrario, è fidato perché **si ricostruisce da sorgente pubblica** (build
  riproducibili, roadmap 4.1/4.2) — anch'essa riproduzione, anch'essa non firma.
  Quindi l'*ancora di fiducia* è la stessa — **riproducibilità, mai identità
  dell'autore** — e il progetto DEVE (MUST) instradare entrambi attraverso di
  essa. Ma gli **insiemi di firmatari/appender DEVONO (MUST) restare distinti**:
  legare gli appender del log della mappa ai firmatari dei rilasci creerebbe un
  unico elenco la cui compromissione avvelena *sia* l'inferenza geografica *sia*
  il software, cioè esattamente il bersaglio di coercizione concentrata che l'item
  4.1 è costruito per evitare. Il log della mappa è senza permessi (ID-7); il
  processo di rilascio può avere un insieme di firmatari nominato (pseudonimo) che
  solo *localizza* una build che non può falsificare. Fonderli baratta la
  permissionlessness della mappa con l'elenco del processo di rilascio — la
  direzione sbagliata.
- **ID-11a (strumenti condivisi va bene; autorità condivisa no).** Entrambi POSSONO
  (MAY) riusare la stessa costruzione di log di trasparenza (ID-6) e lo stesso
  canale di gossip (GR-6) — condividere il *meccanismo* non costa nulla. Ciò che
  NON DEVONO (MUST NOT) condividere è un insieme di parti la cui firma sia portante
  per entrambi, perché quell'insieme sarebbe il kill switch che I-3 vieta, ora in
  grado di ribaltare sia la mappa sia il codice.

## 10. Cosa questa parte non risolve (il residuo dichiarato)

Questa parte fa sì che due client onesti concordino in modo dimostrabile o
rilevino in modo dimostrabile che differiscono. **Non** rende la mappa *vera*. Il
divario tra "la mappa su cui ogni client onesto concorda" e "dove sono fisicamente
i relay" è il residuo, ed è reale:

- **La co-locazione dietro prefissi disgiunti è qui non rilevabile.** Un avversario
  che gestisce relay in un data center annunciando spazio di indirizzamento che i
  dati pubblici BGP/RIR attribuiscono ad AS **diversi** sarà etichettato come
  disgiunto dalla mappa **corretta**. Nessuna build riproducibile di dati pubblici
  può vedere attraverso un annuncio BGP dall'aspetto veritiero fino al rack dietro
  di esso. Questo è enunciato nel punto onesto più profondo della roadmap e
  resiste: **dall'overlay verifichi la consistenza contro un dataset a fiducia
  limitata, non la vera disgiunzione.** Per questo caso *passivo* — una mappa
  corretta che semplicemente capita di etichettare male relay co-locati —
  l'attacco è metadati/collegamento, perché la mappa onesta non fa collassare il
  bacino onesto. (Il caso *attivo*, una mappa scelta per farlo collassare, è
  peggiore e raggiunge il contenuto: PS-12 e il residuo di dirottamento del
  contenuto qui sotto.) Il compito è delimitare ciò che l'avversario guadagna,
  non pretendere di averlo eliminato.
- **Il BGP è genuinamente ambiguo in alcuni punti.** I prefissi MOAS (un prefisso
  legittimamente originato da diversi AS), gli **AS fratelli** sotto un unico
  operatore (ASN distinti, un'unica parte di controllo — la mappa vede due AS dove
  la realtà-di-disgiunzione è uno), e l'**anycast** (un prefisso, molti siti
  fisici) non sono bug del dataset; sono il territorio. La mappa li gestisce
  conservativamente (ID-3a, ID-4b: MOAS → insieme, conflitto di registro →
  `unknown`), il che costa disponibilità (più `unknown` ⇒ più fallback, PS-11)
  piuttosto che sicurezza. Il rilevamento degli AS fratelli è esplicitamente
  **fuori ambito** di una build BGP/RIR pura ed è lasciato come punto cieco
  dichiarato: due AS fratelli sono conteggiati come disgiunti quando non lo sono.
- **La giurisdizione è a grana grossa per decisione.** Le etichette a livello di
  paese derivate dai RIR sono il livello minimo di risoluzione a cui questa parte
  si impegna. Un ragionamento giurisdizionale più fine (blocchi di cooperazione
  legale, realtà dell'assistenza legale reciproca) è deliberatamente **non**
  codificato — sarebbe una valutazione che nessuna build riproducibile può fare
  senza importare un'opinione fidata, cosa che ID-1 vieta.
- **Una mappa avversaria può raggiungere il contenuto, non solo i metadati.** Il
  residuo di co-locazione qui sopra è un errore *passivo* (la mappa corretta
  etichetta male per caso). Una mappa *scelta attivamente* è peggiore: può
  dirottare la selezione disgiunta per AS su `≥ k` circuiti dell'avversario e
  rompere il contenuto, non solo il collegamento (PS-12, che porta le difese).
  Questa parte **non** afferma che una mappa cattiva sia solo sui metadati; quella
  precedente affermazione era sbagliata. Il residuo è delimitato dal margine
  `k`/`n`, dalle difese di collasso del bacino di PS-12 e dalla ricostruzione
  (ID-5a) — non dall'impossibilità.
- **La riproduzione (ID-5a) è l'arbitro solo finché gli input sono recuperabili —
  un limite di liveness.** La ricostruzione risolve una disputa solo se gli input
  pubblici pinnati possono ancora essere recuperati da qualche fonte onesta. I dump
  MRT di RouteViews / RIPE RIS e i file di delega RIR **non** sono archivi
  permanenti con una garanzia di conservazione verso questo progetto; una volta che
  un input pinnato esce da ogni mirror, `rebuild(manifest)` è ineseguibile e una
  disputa su quell'epoch non ha **alcun arbitro** — nel peggiore dei casi proprio
  per le dispute forensi di vecchi epoch che ne hanno bisogno. Un deployment
  conforme DOVREBBE (SHOULD) depositare in escrow i byte degli input pinnati in uno
  store indirizzato per contenuto replicato sullo stesso insieme di mirror senza
  permessi della mappa, così che l'arbitro erediti la disponibilità della mappa
  stessa; in assenza di ciò, ID-5a è dichiarato **limitato dalla liveness**, non
  incondizionato. (Pericoli per il determinismo correlati non ancora pinnati nel
  §4.1: il pruning dipendente dal mirror che rende "ultimo dump ≤ confine"
  dipendente dal mirror; la mutazione di un singolo file-al-giorno RIR contro una
  serie di dump; la divergenza nel *decode dell'input* MRT tra versioni del parser,
  che la canonicalizzazione dell'output di ID-4d non copre.)
- **ID-1 riloca l'autorità su OP-2; non elimina la fiducia.** Nessuna parte
  *firma* la mappa (ID-1 vale alla lettera, e per ogni client che **ricostruisce**
  la sola riproduzione lo sostiene). Ma un client che non ricostruisce (ID-5b lo
  permette) poggia sulla corroborazione del quorum diffuso via gossip (ID-7b,
  ID-9), il cui voto è privo di autorità **solo se** sybil/eclipse possono essere
  resistiti — che è **OP-2, aperto**. Sotto eclipse, il rilevamento
  dell'equivocazione (ID-7a) non può scattare (la vittima non tocca alcuna root
  onesta), un quorum di log dell'avversario può far sembrare corroborata una mappa
  cattiva e — la direzione inversa, sotto-difesa — un avversario può far sembrare
  *non corroborata* una *buona* mappa locale e costringere la vittima ad
  abbandonarla tramite il "tratta la tua mappa come sospetta, ri-recupera" di ID-9a
  (un downgrade attraverso lo stesso macchinario di onestà). Quindi per il client
  che non ricostruisce o è eclissato, "nessuna autorità" significa "fidati del
  quorum", e questo vale solo fin dove vale OP-2. Questa parte **riduce** il
  problema dell'autorità della mappa a OP-2; non lo dissolve.

Il riassunto onesto: **il tasso di errore del dataset è un residuo dichiarato, non
nullo, non un difetto da azzerare** — e, come i tre punti appena aggiunti rendono
esplicito, lo sono anche il tetto di dirottamento del contenuto (PS-12), il limite
di liveness sull'arbitro e la riduzione dell'autorità della mappa a OP-2. Questi
sono il prezzo del rifiutare un'autorità. La risposta corretta non è nasconderli ma
delimitarli, dare in pasto il tasso di errore al simulatore e mostrare all'utente
il livello raggiunto (PS-9, PS-11).

## 11. Il tasso di errore alimenta il simulatore (non ignorato con una scrollata)

Il residuo del §10 non è retorico; è l'esatta quantità che il simulatore già
consuma. `poc/network_sim.py` espone **`infer_error`** — la probabilità che l'AS
inferito da un client per un relay sia **sbagliato** (metà delle volte un AS
sbagliato, metà delle volte `unknown`), modellando un dataset che sia mappa male
sia ha lacune (network_sim.py, `Network.random`). La mappa qui specificata **è**
quel dataset, e il suo residuo misurato **è** quella manopola:

- **ID-12 (la mappa dichiara un tasso di errore misurato). [normativo]** Un
  rilascio di mappa conforme DEVE (MUST) essere distribuito con una **stima
  dell'errore misurata** — il suo tasso di disaccordo contro campioni di ground-
  truth pubblici indipendenti e la sua frazione di `unknown` — derivata
  riproducibilmente da dati pubblici, così che il numero stesso non abbia
  un'autorità dietro di sé. Quella coppia misurata (tasso di mis-map, tasso di
  `unknown`) è il valore che un client dà in pasto al macchinario di confidenza
  della Parte 3 (roadmap 2.2) e il valore che il simulatore scorre come
  `infer_error`.
- **ID-12a (il caso a errore zero è il caso migliore, mai quello atteso).** Per
  PS-11, i numeri a errore zero e vista completa del simulatore sono il caso
  **migliore**; un client conforme DEVE (MUST) presentare il livello di
  disgiunzione raggiunto (PS-9) usando l'errore dichiarato della sua mappa
  **reale**, e l'interfaccia NON DEVE (MUST NOT) citare una cifra di rottura di
  contenuto come se delimitasse anche il collegamento (PS-11) — l'asimmetria che
  rende sopravvivibile una mappa cattiva (ID-8a) è la stessa asimmetria che
  l'interfaccia non deve riportare erroneamente come sicurezza.

## 12. Requisiti introdotti qui

- **ID-1** — nessuna autorità della mappa: fidarsi solo di riproduzione e hashing.
- **ID-2 / ID-2a** — forma dell'artefatto (prefisso→AS, AS→giurisdizione a grana
  grossa), indirizzato per contenuto da `H`; lookup totali, `unknown` di prima
  classe.
- **ID-3 / ID-3a** — solo input pubblici pinnati (BGP RouteViews + RIPE RIS,
  cinque file di delega RIR); risoluzione dell'origine multi-vantaggio, MOAS
  tenuto come insieme.
- **ID-4 / ID-4a–d** — determinismo: l'epoch UTC pinna il timing del dump, ordine
  totale fisso, tie-breaking specificato, nessun input fluttuante, container
  canonico + un test vector della mappa.
- **ID-5 / ID-5a / ID-5b** — l'accordo è uguaglianza degli hash; la ricostruzione
  dagli input è l'arbitro senza autorità; rifiuta ciò che non è riproducibile.
- **ID-6 / ID-7 / ID-7a–c** — log di trasparenza Merkle append-only senza permessi
  di `(epoch, H, manifest-hash)`; equivocazione colta da root diffuse via gossip +
  prove di consistenza; log multipli, nessuno canonico; il log tiene gli impegni,
  non la mappa.
- **ID-8 / ID-8a / ID-8b** — il bootstrap è TOFU dichiarato; il danno di una prima
  mappa cattiva è delimitato ma **non solo sui metadati** — una mappa di
  dirottamento può raggiungere il contenuto (PS-12), quindi il limite è
  condizionale (margine k/n + difese PS-12 + ricostruzione), rilevabile, e la
  riproduzione non può essere falsificata; rileva, non pretendere di prevenire.
- **ID-9 / ID-9a / ID-10** — refresh e gossip di `(epoch, H)` e delle root sotto
  GR-8; divergenza mostrata via PS-9; gossip delle anomalie obbligatorio per le
  tre firme di attacco.
- **ID-11 / ID-11a** — giunzione: stessa ancora di fiducia (riproducibilità) della
  governance dei rilasci, ma insiemi di firmatari/appender **separati**; strumenti
  condivisi sì, autorità condivisa no.
- **ID-12 / ID-12a** — la mappa distribuisce una stima dell'errore misurata e
  riproducibile che alimenta la manopola `infer_error` del simulatore e la
  confidenza della Parte 3; il caso a errore zero è il caso migliore, mai quello
  atteso.

ID-1 e ID-5a sono i due portanti: nessuna autorità, e la riproduzione è l'arbitro.
Entrambi sono delimitati, non assoluti — ID-1 si riduce a OP-2 per un client che
non ricostruisce, e ID-5a è limitato dalla liveness (§10). La terza affermazione
che questa parte faceva originariamente — che una mappa cattiva non possa
raggiungere il contenuto — è stata **rotta** da una revisione ostile: una mappa di
dirottamento manovra l'avversario oltre `k` e rompe il contenuto, non solo il
collegamento. Anziché nasconderlo, questa parte ora lo porta apertamente: la difesa
è PS-12 e il residuo è dichiarato nel §10. Rompi il resto allo stesso modo — trova
un passo che ha bisogno di una parte fidata, una mappa che non possa essere
ricostruita dai suoi input, un vuoto di liveness che ci è sfuggito, o un modo
*nuovo* in cui una mappa cattiva raggiunge il contenuto oltre le difese di PS-12 —
e hai rotto questa parte. Questo è l'invito, ed è già stato accolto una volta. Lo
sweep di `infer_error` di `poc/network_sim.py` (e la costruzione di dirottamento di
PS-12) è lo strawman eseguibile dietro il §11; attacca il modello, poi questo testo.
