# Specifica ScrambNet — Parte 3: Costruzione dei circuiti e selezione dei percorsi

**Stato: BOZZA (DRAFT), e la parte meno assestata della specifica.** È il muro
portante della sicurezza *operativa* (il contenuto garantito da I-2 regge anche
senza di essa, ma la protezione dalla correlazione e l'intera storia dei
k-percorsi vivono qui). I valori provvisori sono contrassegnati con `(s)`. Il
problema della verifica della disgiunzione è OP-1 ed è apertamente irrisolto;
questa parte enuncia l'obiettivo e un primo meccanismo da attaccare.

## 1. Ambito e perché è difficile

La dispersione (Parte 1) rende il contenuto incondizionatamente sicuro sotto le
`k` quote catturate. Quella garanzia è *operativamente* reale solo se gli `n`
circuiti delle quote sono realmente disgiunti — altrimenti un singolo punto di
osservazione dell'avversario vede `k` quote e il livello minimo garantito,
benché matematicamente intatto, non viene mai raggiunto. Questa parte decide
come un client, che possiede soltanto il proprio campione di gossip verificabile
(Parte 2) e nessuna mappa fidata, selezioni `n` circuiti su cui un avversario
non possa sedersi a basso costo. Tutto ciò che segue deve reggere contro relay
che mentono su tutto tranne ciò che le loro firme vincolano (GR-2).

## 2. Obiettivi di disgiunzione

- **PS-1.** Gli `n` circuiti di un messaggio DEVONO (MUST) essere *disgiunti per
  nodo*: nessun relay compare su due di essi. Questo è il livello minimo, sempre
  imponibile se il campione è abbastanza grande.
- **PS-2.** Il client DOVREBBE (SHOULD) cercare inoltre, in ordine decrescente
  di valore e crescente di difficoltà: **disgiunzione per AS** (nessuna coppia
  di circuiti condivide un sistema autonomo alla guardia o all'uscita), poi
  **disgiunzione per giurisdizione** (nessuna coppia condivide una giurisdizione
  legale). Ogni livello che non riesce a soddisfare DEVE (MUST) essere segnalato
  all'utente, non saltato in silenzio (PS-9).
- **PS-3.** All'interno di un singolo circuito, la guardia, il nodo intermedio e
  l'uscita DEVONO (MUST) essere distinti per nodo, e DOVREBBERO (SHOULD) essere
  distinti per AS. Un circuito la cui guardia e uscita condividono un AS è un
  regalo alla correlazione end-to-end e NON DEVE (MUST NOT) essere usato quando
  esiste una qualsiasi alternativa.

## 3. Inferenza senza autodichiarazione

- **PS-4.** GR-3 vieta ai relay di dichiarare la propria posizione, quindi il
  client inferisce l'AS e la giurisdizione di ogni relay dai suoi `addrs`
  usando il *proprio* insieme di dati (per esempio una mappa IP-verso-AS
  aggiornata periodicamente), mai da ciò che il relay dichiara. La distribuzione
  dell'insieme di dati DEVE (MUST) a sua volta rispettare I-3: nessuna singola
  fonte autoritativa (i progetti candidati sono OP-1).
- **PS-5.** L'inferenza è incerta, e il client DEVE (MUST) trattarla come tale:
  quando l'AS o la giurisdizione di un relay è ignota, essa conta come
  *potenzialmente condivisa* con ogni altra ignota — l'assunzione conservativa,
  mai quella ottimistica.

## 4. Guardie

- **PS-6.** Ogni client mantiene un piccolo insieme di **relay di guardia**
  (valore provvisorio: una guardia primaria per posizione nel circuito, ruotata
  secondo una cadenza di mesi, non di minuti), seguendo il razionale delle
  guardie di Tor: ruotare i punti d'ingresso in fretta moltiplica la probabilità
  di pescarne prima o poi uno ostile. Le guardie DEVONO (MUST) essere scelte
  disgiunte per AS tra loro, così che gli `n` circuiti non convoglino attraverso
  un unico AS all'ingresso.
- **PS-7.** La selezione delle guardie è ponderata sulla banda *verificata*
  (GR-7), mai su quella dichiarata; un relay con una dichiarazione non
  verificabile è trattato come a banda bassa, non alta.

## 5. Reti piccole: degrada, e dillo

- **PS-8.** Quando il campione verificato del client non può fornire `n`
  circuiti disgiunti per AS, esso DEVE (MUST) ripiegare in un ordine fisso —
  disgiunti per AS → disgiunti per nodo → estrazioni indipendenti — e NON DEVE
  (MUST NOT) procedere in silenzio come se la proprietà più forte valesse. I
  parametri POSSONO (MAY) essere ridotti (modalità rete piccola: `n = 2, k = 2`
  con disgiunzione al meglio possibile) quando la dimensione viabile stimata non
  è raggiunta.
- **PS-9.** Il client DEVE (MUST) esporre il livello di disgiunzione
  effettivamente raggiunto per un messaggio, in termini che un non esperto legga
  correttamente: la folla oggi è piccola; ecco cosa stai comprando. Il contenuto
  garantito (I-2) e il livello di correlazione sono enunciati separati e DEVONO
  (MUST) essere mostrati separatamente.
- **PS-10 (stima della dimensione resistente ai sybil).** La stima della
  dimensione viabile DEVE (MUST) contare solo i relay verificati in modo
  indipendente e la diversità di AS osservata, mai il conteggio grezzo dei
  record, così che un avversario non possa gonfiare la rete con sybil per
  ingannare i client e indurli a usare parametri pieni la cui diversità è falsa
  (si lega a OP-2).
- **PS-11 (la disgiunzione creduta non è disgiunzione reale).** La protezione
  che un client costruisce vale solo quanto il suo insieme di dati per
  l'inferenza, e il client DEVE (MUST) trattare il tasso di errore dell'insieme
  di dati come un parametro di sicurezza di prim'ordine, non come un dettaglio
  implementativo. Il simulatore (`poc/network_sim.py`, §1) separa la *verità di
  base* — che l'avversario sfrutta — dalla *convinzione* del client, e fa variare
  il tasso di errore dell'inferenza: al crescere dell'errore, la selezione
  disgiunta per AS diventa in parte illusoria e sia il tasso di rottura del
  contenuto sia la perdita di collegamento crescono in modo monotòno. Due
  conseguenze sono normative: (a) per l'errore di inferenza **casuale** (rumore,
  una mappa semplicemente inaccurata), l'errore erode il **collegamento molto più
  rapidamente del contenuto** — una rottura del contenuto richiede comunque che
  l'avversario sia su `≥ k` circuiti contemporaneamente, quindi il livello minimo
  garantito regge mentre i metadati si degradano per primi; l'interfaccia NON
  DEVE (MUST NOT) presentare un valore basso di rottura del contenuto come se
  limitasse anche il collegamento. Questa asimmetria vale **solo per l'errore
  casuale**; una mappa *scelta in modo avversario* non è rumore (vedi PS-12);
  (b) un **campione di gossip** più sottile
  (PS-10, I-3) costringe al ripiego prima: un client che conosce troppo pochi
  relay non riesce a costruire affatto circuiti disgiunti per AS e precipita a
  `none`, dove il tasso di rottura balza (§2). La stima della dimensione viabile
  (PS-10) DEVE (MUST) quindi tenere conto del campione *raggiungibile*, non
  dell'intera rete. I valori a errore zero e con vista completa sono il caso
  migliore; un client conforme DEVE (MUST) presentare il livello raggiunto (PS-9)
  a partire dalla sua vista reale, rumorosa e parziale.
- **PS-12 (una mappa ostile non deve dirottare la selezione sull'avversario).**
  `[claim-critical]` Una mappa *scelta in modo avversario* non è errore casuale, e
  l'asimmetria di PS-11(a) **non** protegge contro di essa. Una mappa che
  l'avversario controlla ha due leve sulla selezione disgiunta per AS: dare ai
  relay co-locati dell'avversario stesso AS *distinti* falsi (così che non si
  escludano mai a vicenda), e dare ai relay *onesti* AS *collidenti* falsi (così
  che, una volta che il circuito 1 ha scelto un relay onesto, ogni altro relay
  onesto sembri condividere l'AS e venga filtrato via). Il bacino di candidati
  onesti collassa allora dopo la prima estrazione e il client seleziona i circuiti
  2…`n` quasi interamente da relay dell'avversario — portando l'avversario sulla
  guardia **e** sull'uscita di `≥ k` circuiti in modo **deterministico**, una
  rottura di *contenuto*, mentre il client crede ancora di aver raggiunto la
  disgiunzione per AS e non solleva alcun avviso di ripiego. Dimostrato contro
  `poc/network_sim.py`: una mappa di dirottamento porta il tasso di rottura del
  contenuto dal ~0% al **100% al ~15%** di proprietà dell'avversario (contro un
  tasso basso a una sola cifra per una mappa onesta al 35%). Quindi **una mappa
  cattiva PUÒ raggiungere il contenuto, non solo il collegamento** (questo corregge
  una precedente sopravvalutazione; la Parte 8 ID-8a è corretta di conseguenza). Le
  difese che un client conforme DEVE (MUST) applicare:
  1. **Non lasciare che sia la mappa da sola a far collassare il bacino onesto.**
     Un client NON DEVE (MUST NOT) costruire un insieme di circuiti in cui più di
     una frazione limitata dei circuiti dipenda, per la propria disgiunzione
     reciproca dichiarata, da relay che il client non può *indipendentemente*
     corroborare come distinti (mescolamento delle sorgenti GR-8, PS-10 "conta solo
     ciò che è verificato indipendentemente"). Se la selezione creduta-disgiunta
     estraesse i circuiti 2…`n` da un bacino che la mappa ha reso sospettosamente
     piccolo, il client DEVE (MUST) trattarlo come una condizione di
     ripiego/anomalia (PS-8, PS-9), non come un successo.
  2. **Una mappa che implica una struttura di AS implausibile è essa stessa
     un'anomalia.** Una mappa sotto la quale il *campione onesto raggiungibile* del
     client collassa a uno o pochi AS mentre il resto plasmato dall'avversario è
     massimamente diverso è una firma del dirottamento; il client DOVREBBE (SHOULD)
     diffonderla via gossip come anomalia della mappa (Parte 8 ID-10) e ripiegare.
  3. **La ricostruzione è la vera difesa.** Una mappa di dirottamento non è
     riproducibile da input pubblici (Parte 8 ID-5a); un client che ricostruisce, o
     che concorda con un peer onesto che l'ha fatto, la rifiuta. Fino ad allora il
     client DEVE (MUST) trattare le affermazioni di disgiunzione di una mappa non
     verificata come non verificate, non come raggiunte (PS-9).
  Il residuo onesto permane: entro la finestra di eclipse di un client che ha
  accettato una mappa di dirottamento non verificata e non può ancora ricostruire,
  il livello minimo di contenuto può cadere. Questo è delimitato dal margine
  `k`/`n` e dalle difese di cui sopra, non da un'affermazione che non possa
  accadere.

## 6. La procedura di verifica (PS-13…PS-19)

### 6.1 La procedura e il suo certificato

- **PS-13 (la procedura è una funzione pura di tre input dichiarati).**
  `[claim-critical]` La costruzione dei circuiti DEVE (MUST) essere esprimibile come
  una funzione
  deterministica
  ```
      verify(sample, map, corroboration, n, k)  ->  (circuits, certificate)
  ```
  di esattamente tre input lato client, e di nient'altro:
  - **`sample`** — il campione di relay verificato via gossip del client (Parte 2,
    contato sotto PS-10: *solo relay verificati indipendentemente*);
  - **`map`** — la mappa di inferenza della Parte 8, identificata dal suo hash `H` e
    recante il proprio tasso di errore misurato `e` (ID-12);
  - **`corroboration`** — un numero per-relay `c_j ∈ [0,1]` che indica quanto
    indipendentemente l'AS/giurisdizione inferita del relay è corroborata (PS-15).
  L'output è costituito da `n` circuiti **e** un **certificato di disgiunzione**
  (PS-14). Nessun passo può leggere la posizione autodichiarata del relay (GR-3,
  PS-4), una directory fidata (I-3) o la verità di base (non ce n'è da leggere — è
  proprio questo il problema). Un'implementazione conforme che non sa esprimere la
  propria selezione come questa funzione pura non può emettere un certificato
  controllabile ed è non conforme: un implementatore con questa specifica e gli
  stessi tre input DEVE (MUST) poter ricostruire la stessa decisione di
  circuiti-e-certificato (I-1).

- **PS-14 (cosa contiene il certificato — e come è verificabile a macchina).**
  `[claim-critical]` Il certificato è un record in CBOR canonico (codifica della
  Parte 0) che reca **esattamente** i campi di cui una seconda parte ha bisogno per
  **ricalcolarlo e confermarlo**, e nessun campo che chieda di essere creduto:
  1. **`map_hash`** — l'`H` rispetto a cui il certificato è stato calcolato (ID-2).
     Il certificato è privo di senso senza di esso: *"disgiunto per AS"* non è mai
     un'affermazione autonoma, solo *"disgiunto per AS sotto la mappa `H`"*.
  2. **`map_error`** — la coppia `(mismap_rate, unknown_rate)` fornita dalla mappa
     (ID-12), copiata verbatim affinché il verificatore non debba rimisurarla. La
     loro somma è l'errore per-lookup `e` usato più sotto.
  3. **`circuits`** — per ciascuno degli `n` circuiti, gli ID dei relay (impronte di
     chiave GR-2) su guard/middle/exit, e per i **pivot** (guard ed exit — le due
     posizioni che un avversario a livello di AS correla, PS-3) la coppia
     `(AS, giurisdizione)` **creduta** che la mappa ha assegnato, oppure `unknown`.
  4. **`corroboration`** — il `c_j` per-pivot usato (PS-15), affinché il
     verificatore ricalcoli con le stesse riduzioni.
  5. **`class`** — la classe di disgiunzione raggiunta, una tra `as` / `node` /
     `none` (ordine PS-2), cioè la proprietà *più forte* che l'insieme effettivamente
     soddisfa sotto la mappa, non quella richiesta.
  6. **`confidence`** — un numero in `[0,1]` (PS-16), il limite inferiore
     conservativo sulla probabilità che l'affermazione `class` valga, dati i margini
     di errore della mappa e la corroborazione.
  7. **`steering_flag`** — il verdetto del rilevatore PS-12 sul **campione
     raggiungibile completo** del client (PS-17), e il rapporto di sopravvivenza del
     bacino che vi sta dietro.
  Un verificatore **che possiede la stessa mappa `H`** DEVE (MUST) poter: (a)
  rifare il lookup della `(AS, giurisdizione)` di ogni pivot in `H` e confermare
  che corrisponde al campo 3; (b) ricalcolare `class` da quei lookup tramite il test
  di disgiunzione PS-2; (c) ricalcolare `confidence` dai campi 2, 4, 5 e 7 tramite
  la formula PS-16 **così come dichiarata**; e (d) confermare che il record è
  internamente coerente. Se un qualsiasi ricalcolo è in disaccordo, il certificato è
  **invalido** e DEVE (MUST) essere rifiutato (è stato calcolato rispetto a una
  mappa diversa, oppure è falsificato). Il certificato non vincola alcuna firma:
  come la mappa stessa (ID-11), **l'arbitro è la riproduzione, non la firma.**

  **Cosa il verificatore può e non può ri-derivare — detto onestamente (una scoperta
  di una revisione ostile).** Due campi sono *input che il client di origine ha
  misurato*, non quantità che un verificatore remoto può ricalcolare da `H` da solo:
  `steering_flag`/`pool_survival` sono funzioni del **campione di gossip raggiungibile
  completo di quel client** (PS-17), che non è un campo del certificato; e ogni `c_j`
  è la **misura di corroborazione di quel client** (PS-15), anch'essa non
  ri-derivabile da `H`. Quindi il certificato è controllabile **rispetto ai propri
  input dichiarati** — un verificatore conferma che la confidenza segue dai
  `map_error`, `corroboration` e `steering_flag` dichiarati tramite la formula
  PS-16 — ma **non** è una prova incondizionata: un client che **mente** al rialzo
  sul proprio `c_j`, o che omette un flag di dirottamento che il suo campione avrebbe
  sollevato, produce un certificato che si ricalcola *in modo coerente* ed è comunque
  sbagliato. Le difese contro questo non sono nel certificato ma nella rete: un
  client indipendente sulla stessa `H` e con un campione sovrapposto deriva un
  certificato **diverso**, e la divergenza è diffusa via gossip come anomalia (PS-19,
  ID-10) esattamente come lo è una divergenza di mappa. Il certificato rimuove il
  *silenzioso* "disgiunto per AS: sì"; non rende autodimostrante la confidenza di un
  client che mente. Questo è un limite dichiarato (§6.6), non uno nascosto.

### 6.2 Corroborazione: l'input di confidenza per-relay

- **PS-15 (la corroborazione per-relay è accordo indipendente, contato come in
  PS-10).** L'input `c_j` per un relay **non** è un punteggio di fiducia e NON DEVE
  (MUST NOT) provenire dal relay né da una qualsiasi singola parte. È il grado in cui
  l'AS inferita del relay è **corroborata indipendentemente** — la stessa disciplina
  "conta solo ciò che è verificato indipendentemente" che PS-10 applica alle stime di
  dimensione e GR-8 applica al gossip:
  - `c_j = 0` — l'AS del relay proviene dalla mappa `H` **e da nient'altro**; il
    client non ha un secondo punto di osservazione. Questo è il valore predefinito e
    il livello minimo conservativo.
  - `c_j` sale verso `1` man mano che punti di osservazione **indipendenti, con
    sorgenti mescolate** (GR-8) concordano sulla stessa AS inferita per quel relay:
    una seconda mappa costruita in modo riproducibile da un insieme di collector
    disgiunto (ID-3a), un'osservazione fuori banda del prefisso annunciato dal relay,
    un pivot di certificato diffuso via gossip da un peer che corrisponde. Strawman
    (s): `c_j = 1 − 2^(−v)` per `v` punti di osservazione corroboranti indipendenti
    (un punto ⇒ 0.5, due ⇒ 0.75, …), limitato al di sotto di `1` perché nessun numero
    finito di punti di osservazione overlay vede il rack (§6.6).
  Un relay che la mappa etichetta `unknown` ha `c_j = 0` **e** contribuisce con
  un'AS-creduta `unknown` già conservativa (PS-5): collide con tutto, quindi
  raramente sopravvive in una posizione di pivot, e quando lo fa la formula di
  confidenza lo tratta già come pienamente incerto (PS-16). La corroborazione NON
  DEVE (MUST NOT) essere inferita da *quanti* peer riportano un valore prima che sia
  applicato il mescolamento delle sorgenti GR-8/PS-10 — una sybil non può votare
  l'AS di un relay fino a un'alta corroborazione per mera numerosità (si lega a OP-2,
  esattamente come ID-9).

### 6.3 La formula di confidenza

- **PS-16 (la confidenza è un limite inferiore conservativo sulla mislabel
  indipendente).** `[claim-critical]` Siano i **pivot** di un insieme di circuiti i
  relay distinti su guard o exit lungo gli `n` circuiti (al più `2n`, meno dopo la
  deduplicazione). La disgiunzione dichiarata vale **solo se nessun pivot è
  mal-etichettato** in un modo che trasformi una coppia creduta-distinta in una che
  realmente collide. La mappa fornisce l'errore per-lookup
  `e = mismap_rate + unknown_rate` (ID-12); la corroborazione riduce la probabilità
  di mislabel **effettiva** di un pivot a
  ```
      p_j = e · (1 − c_j).
  ```
  Trattando le mislabel per-pivot come **indipendenti**, la `confidence` del
  certificato per `class = as` è il prodotto
  ```
      confidence  =  Π_j ( 1 − e · (1 − c_j) )       over pivots j,
  ```
  azzerata a `0` dal gate di dirottamento PS-17. Per `class = node`, la disgiunzione
  non dipende affatto dalla mappa (l'identità di nodo è vincolata a GR-2, non
  inferita), quindi `confidence = 1 − (gate PS-17)`. Per `class = none`,
  `confidence = 0` per definizione: non si dichiara alcuna disgiunzione, quindi
  nessuna è attestata.

  **L'assunzione di indipendenza, nominata e giustificata come conservativa.** Le
  mislabel reali dei pivot **non** sono indipendenti: un prefisso BGP sbagliato nella
  mappa mal-etichetta in un colpo solo ogni relay sotto di esso (correlazione
  positiva). Assumiamo comunque l'indipendenza, ed è **conservativa nella direzione
  che conta** per un *limite inferiore*: il prodotto `Π(1 − p_j)` sottostima il caso
  *correlato* in cui più pivot condividono una sola causa di mislabel — quando le
  mislabel sono correlate, la probabilità che *almeno un* pivot sia sbagliato è **più
  bassa** di quanto implichi il prodotto indipendente, quindi la vera probabilità
  "tutti i pivot corretti" è **più alta** del nostro limite. Il prodotto è dunque un
  livello minimo sulla confidenza, cioè non sovrastima mai la sicurezza. Dove
  l'indipendenza ci renderebbe *troppo* fiduciosi è una causa *onesta* condivisa (una
  sola AS enorme e corretta), che non minaccia la disgiunzione; la causa condivisa
  avversaria — una sola mappa che fa collassare il bacino — non è gestita affatto da
  questo prodotto ma dal gate PS-17, che azzera la confidenza a 0 indipendentemente
  dal prodotto. Così le due forme di fallimento sono separate nettamente: **errore di
  mappa casuale/correlato → il prodotto (conservativo); struttura di mappa avversaria
  → il gate (livello minimo rigido).**

  Fondamento (non sventolato). Contro `poc/network_sim.py`, senza corroborazione
  (`c_j = 0`, quindi `p_j = e`), `1 − confidence` limita superiormente il tasso di
  collisione per AS reale **osservato** dei pivot a ogni livello di errore — ad es. a
  `e = 0.2`, `1 − confidence ≈ 0.83` contro un fallimento di disgiunzione reale
  osservato di `≈ 0.18`: pessimistico, che è la direzione corretta per un livello
  minimo di sicurezza, mai ottimistico. La corroborazione lo recupera monotonicamente
  (a `e = 0.2`, la confidenza media sale `0.17 → 0.43 → 0.84 → 0.99` man mano che
  `c_j` uniforme va `0 → 0.5 → 0.9 → 1.0`). Un client conforme DOVREBBE (SHOULD)
  presentare questo pessimismo onesto piuttosto che stringere il limite con un modello
  che assume più di quanto giustifichino i tre input dichiarati — un livello minimo
  difendibile batte una falsa precisione (PS-11).

### 6.4 Robustezza a PS-12, per costruzione

- **PS-17 (il gate di dirottamento azzera la confidenza — sul segnale giusto, sul
  campione raggiungibile COMPLETO).** `[claim-critical]` Prima che il prodotto di
  PS-16 sia riportato, la procedura DEVE (MUST) applicare il rilevatore della difesa-2
  di PS-12 (`detect_steering`) all'**intero campione di gossip raggiungibile** del
  client, non ai `2n` pivot scelti — la struttura vive nella *popolazione* ed è sparita
  dai pivot nel momento in cui questi vengono estratti (controllare i soli pivot
  intercetta una mappa di dirottamento solo su ~metà dei messaggi). **Il segnale deve
  essere quello che l'avversario non può evitare.** Una prima versione di questo
  rilevatore si basava su "una sola AS-creduta enorme che tiene il bacino onesto
  collassato, circondata da singleton", e una revisione ostile l'ha **eluso** facendo
  collassare il bacino onesto in *poche* AS false invece di una sola enorme — nessuna
  AS enorme, rilevatore silente, contenuto rotto su ~30% dei messaggi. Il segnale
  corretto e portante è la **frazione anomala di singleton**: per far sembrare i suoi
  relay co-locati disgiunti per AS l'avversario DEVE (MUST) dare a ciascuno una AS
  falsa distinta, cioè renderli singleton, e una rete reale ha pochissime AS
  singleton. Il rilevatore DEVE (MUST) quindi scattare quando i relay singleton
  superano una piccola frazione del campione **e** i relay non-singleton si trovano in
  troppo poche AS affollate per costruire `n` circuiti disgiunti (la seconda clausola
  impedisce al *rumore* di inferenza, che anch'esso produce singleton, di farlo
  scattare). Misurato contro `poc/network_sim.py`
  (`make_steering_map(honest_groups=g)` / il `detect_steering` corretto): questo
  intercetta il regime di dirottamento **effettivo** (`g = 1…5`, una rottura del
  contenuto del 10–100%) al ~100% con **0%** di falsi positivi su mappe oneste anche a
  un errore di inferenza fino a 0.4. Pertanto:
  - Se il rilevatore scatta sul campione raggiungibile, il certificato DEVE (MUST)
    impostare `steering_flag = true`, `class = none` e `confidence = 0`, e il client
    DEVE (MUST) trattare il risultato come la condizione di ripiego/anomalia di PS-12
    (diffonderla via gossip, ID-10; degradare e dirlo, PS-8/PS-9) — NON DEVE (MUST
    NOT) emettere un certificato `as`.
  - **Residuo dichiarato:** una mappa di dirottamento *marginale* che distribuisce il
    bacino onesto su abbastanza AS false (`g ≥ 8`) da costruire circuiti genuinamente
    disgiunti sfugge al rilevatore — ma lì la sua rottura del contenuto è solo del
    ~5%, indistinguibile da una piccola rete legittima, e delimitata dal margine
    `k`/`n` e dalla confidenza PS-16, non da un'affermazione che non possa accadere
    (§6.6).

- **PS-18 (precondizione di collasso del bacino — difesa 1 di PS-12, ripiegata come
  input di confidenza).** `[claim-critical]` Indipendentemente dal rilevatore
  strutturale, la procedura DEVE (MUST) calcolare il **rapporto di sopravvivenza del
  bacino onesto**: la frazione del campione raggiungibile e corroborato
  indipendentemente (PS-10, PS-15 con `c_j > 0`) che rimane candidata a un'
  *AS-creduta-distinta* **dopo** che il primo circuito è stato estratto. Un
  certificato NON DEVE (MUST NOT) dichiarare `class = as` quando i circuiti `2…n`
  sono stati estratti da un bacino che la mappa ha fatto collassare al di sotto di una
  frazione limitata (strawman (s): sopravvivenza `< 1/n` del campione onesto
  corroborato), perché allora la dichiarata disgiunzione reciproca dell'insieme
  poggia su relay che il client non può corroborare *indipendentemente* come
  distinti — esattamente la difesa 1 di PS-12. In tal caso la procedura DEVE (MUST)
  o abbassare `class` a `node` (abbandonando del tutto l'affermazione dipendente
  dalla mappa) oppure impostare la condizione di anomalia come in PS-17. **La
  confidenza è BASSA esattamente quando PS-12 dice che il client sta venendo
  dirottato:** il gate la azzera sulla firma strutturale, e la precondizione di
  sopravvivenza spoglia l'affermazione `as` quando il bacino è sospettosamente
  sottile — così una mappa di dirottamento non può guadagnare un certificato `as` ad
  alta confidenza tramite nessuna delle due leve (AS avversarie false distinte o AS
  oneste false che collidono). Questa è la proprietà non negoziabile, ed è
  verificata, non asserita: lo stesso gate che i test di PS-12 mostrano trasformare
  una rottura del contenuto del 100% in un ripiego del 100% porta a 0 la confidenza
  del certificato sul 100% delle mappe di dirottamento.

### 6.5 Un certificato svolto

Input: `n = 4`, `k = 3`; un campione sano; mappa `H = 0x9f2c…a17b` che fornisce
`map_error = (0.04, 0.03)` quindi `e = 0.07`; gli 8 pivot (4 guard + 4 exit) — 6
corroborati da un ulteriore punto di osservazione indipendente (`c_j = 0.5`), 2
poggianti sulla mappa da sola (`c_j = 0.0`); il rilevatore di dirottamento **non**
scatta sul campione raggiungibile. Allora `p_j = 0.035` per i sei e `0.07` per i
due, e `confidence = (1−0.035)^6 · (1−0.07)^2 = 0.698`.

```
disjointness-certificate (canonical CBOR; shown as a record):
  map_hash      : 0x9f2c3e...a17b
  map_error     : { mismap: 0.04, unknown: 0.03 }         # e = 0.07 (ID-12)
  class         : "as"                                     # più forte raggiunta, PS-2
  confidence    : 0.698                                    # prodotto PS-16, gate=1
  steering_flag : false                                    # PS-17, verifica vista completa
  pool_survival : 0.61                                     # PS-18, > 1/n = 0.25 OK
  circuits:
    - { guard: 4a1f.., mid: 7c02.., exit: e9d3..,
        pivots:[{as:3356, jur:"US", c:0.5},{as:1299, jur:"SE", c:0.5}] }
    - { guard: b17c.., mid: 02aa.., exit: 55f1..,
        pivots:[{as:3320, jur:"DE", c:0.5},{as:9002, jur:"GB", c:0.0}] }
    - { guard: cc90.., mid: 1d44.., exit: a7e8..,
        pivots:[{as:6830, jur:"NL", c:0.5},{as:2914, jur:"JP", c:0.5}] }
    - { guard: 3e5b.., mid: f108.., exit: 9b22..,
        pivots:[{as:174,  jur:"US", c:0.0},{as:8075, jur:"IE", c:0.5}] }
```
Letto correttamente (PS-9): *"Questi 4 circuiti sono disgiunti per AS **sotto la
mappa `H`**, che ammette un tasso di errore del 7%; dato quanto indipendentemente è
corroborata l'AS di ciascun relay, c'è almeno una **probabilità del 70%** che la
disgiunzione per AS sia reale e non un artefatto di una mislabel. Non è una garanzia,
e non dice nulla su un data center che la mappa non può vedere (§6.6)."* Se il
rilevatore di dirottamento fosse scattato, ogni numero qui sopra sarebbe sostituito
da `class: none, confidence: 0, steering_flag: true` e un avviso di ripiego — non
c'è alcun certificato ad alta confidenza per un client dirottato.

```
  IL FLUSSO PRODUCI-CIRCUITI-E-CERTIFICATO

   sample (PS-10)      map H + e (ID-12)      corroboration c_j (PS-15)
        │                   │                        │
        └─────────┬─────────┴───────────┬────────────┘
                  ▼                      ▼
        ┌───────────────────┐   ┌─────────────────────────────┐
        │ detect_steering    │   │ selez. disgiunta per AS-cred│
        │ campione COMPLETO  │   │ (ordine PS-2: as→node→none) │
        │ (PS-17, difesa 2)  │   │  + sopravv. bacino (PS-18,  │
        └─────────┬─────────┘   │     difesa 1)               │
                  │             └──────────────┬──────────────┘
          scatta? │                            │ n circuiti + pivot
         ┌────────┴────────┐                   ▼
       sì                no        ┌────────────────────────────┐
         │                 └──────▶ │ confidence = Π(1−e(1−c_j))  │ PS-16
         ▼                         │ class = più forte raggiunta │
  class=none, conf=0               └──────────────┬─────────────┘
  steering_flag=true                              ▼
  → ripiego + gossip         ┌─────────────────────────────────────┐
    (PS-8/9, ID-10)          │ CERTIFICATO {map_hash, map_error,    │
                             │  circuits, corroboration, class,     │
                             │  confidence, steering_flag}          │
                             └──────────────┬──────────────────────┘
                                            ▼
                     un verificatore con la STESSA H ricalcola e conferma
                     (l'arbitro è la riproduzione — nessuna firma, ID-11)
```

- **PS-19 (il certificato è per l'utente e per il peer, entrambi).** La `confidence`
  e la `class` DEVONO (MUST) guidare la superficie di onestà PS-9 che l'utente legge
  (*la folla è disgiunta così tanto oggi, con questa certezza*), e il certificato DEVE
  (MUST) essere diffondibile via gossip affinché un peer che possiede la stessa `H`
  possa ri-derivarlo (PS-14) e affinché una divergenza — due client, stessa `H` e
  campione, certificato diverso — sia intercettata e diffusa via gossip come anomalia
  (ID-10), lo stesso segnale immunitario che la Parte 8 usa per la divergenza di
  mappa. L'interfaccia utente NON DEVE (MUST NOT) citare `confidence` come se
  delimitasse il collegamento: delimita l'affermazione di disgiunzione del
  **contenuto**; i metadati degradano più in fretta (PS-11(a)), e un'alta confidenza
  in `class = as` non significa un basso trafilamento di collegamento.

### 6.6 Cosa questo non risolve

Il certificato attesta **coerenza rispetto a un insieme di dati a fiducia limitata,
non vera disgiunzione** (Parte 8 §10), e l'onestà di tutta questa procedura sta nel
dirlo su ogni record. Un avversario che co-loca i relay in un solo rack mentre
annuncia spazio di indirizzamento che i dati pubblici BGP/RIR attribuiscono
**veritieramente** ad AS diverse è etichettato disgiunto dalla mappa **corretta** —
quindi i lookup corrispondono a `H`, il rilevatore di dirottamento non scatta (la
struttura non è una firma di dirottamento, è la genuina tabella di instradamento
pubblica), il bacino non collassa, e i pivot sono ben corroborati **perché ogni punto
di osservazione onesto concorda con la mappa**. La procedura emette quindi un
**certificato `as` ad alta confidenza che è nondimeno sbagliato**: `confidence`
misura la probabilità che l'insieme sia disgiunto *sotto la mappa*, e qui la mappa è
giusta e l'overlay comunque non può vedere il rack. Questo è il residuo di
co-locazione della Parte 8 §10, ed è l'unica limitazione che il certificato **non**
può rimuovere — nessuna quantità di corroborazione la chiude, perché la corroborazione
conferma solo l'accordo *con i dati pubblici*, e i dati pubblici stessi sono ciò che
l'avversario ha soddisfatto. La sua entità è esattamente il divario del simulatore tra
AS creduta e reale a `infer_error = 0`: il certificato legge 1.0, la realtà può ancora
collidere, e solo alzare il margine `k`/`n` — non un qualsiasi campo del certificato —
delimita la perdita. Il dono del certificato è che non **nasconde** mai questo: dichiara
i propri margini di errore, si azzera sotto dirottamento (PS-17/18), ed è controllabile
da chiunque possieda la mappa (PS-14). Trasforma "disgiunto per AS: sì" — una menzogna
— in "disgiunto per AS sotto la mappa `H` con errore `e`, confidenza `c`" — un'
affermazione vera il cui unico punto cieco rimanente è nominato qui e non nascosto da
nessuna parte.

Tre ulteriori limiti che una revisione ostile ha fatto emergere, dichiarati qui
anziché mascherati:

- **Il dirottamento marginale sfugge al rilevatore.** Una mappa di dirottamento che
  distribuisce il bacino onesto su abbastanza AS false (`g ≥ 8`) costruisce circuiti
  genuinamente disgiunti e quindi non fa scattare il rilevatore di frazione di
  singleton (PS-17) — ma la sua rottura del contenuto è allora solo del ~5%, il
  livello di una piccola rete legittima, delimitata dal margine `k`/`n` e dalla
  confidenza PS-16. Il rilevatore intercetta il regime di dirottamento *effettivo*
  (rottura del 10–100%), non ogni mappa.
- **La confidenza di un client che mente non è autodimostrante.** `confidence` è onesta
  solo quanto lo sono i `c_j` e lo `steering_flag` che il client di origine ha misurato
  e messo nel certificato; un client che sovrastima la propria corroborazione, o che
  omette un flag, emette un certificato che si ricalcola in modo coerente ed è comunque
  sbagliato (PS-14). La presa è sociale, non aritmetica: un client indipendente sulla
  stessa `H` deriva un certificato diverso, e la divergenza è diffusa via gossip come
  anomalia (PS-19). Il certificato rimuove la menzogna *silenziosa*, non una
  *rilevabile*.
- **Il prodotto di confidenza delimita le collisioni tra coppie di pivot, non ogni
  collisione.** PS-16 misura la probabilità che una *coppia* di pivot creduta-disgiunta
  stia realmente collidendo. Una mislabel che fa collidere un pivot con un hop *middle*,
  o che confonde la giurisdizione con l'AS, è fuori dal prodotto e deve essere
  intercettata dal test di disgiunzione PS-2 sull'intero circuito, non letta dal numero
  di confidenza.

## 7. Cosa questa parte non decide

La distribuzione senza fiducia dell'insieme di dati per la disgiunzione, e la
verifica formale che un insieme scelto sia disgiunto quanto dichiarato (OP-1);
le soglie oneste di dimensione viabile e se `n = 2, k = 2` valga affatto la pena
di essere eseguito (OP-3); l'economia della rotazione delle guardie; la
selezione dei percorsi sulla mesh di blackout, dove AS e giurisdizione non
significano nulla (OP-6). `poc/network_sim.py` è il valore provvisorio
eseguibile dietro questa parte — attacca il suo modello, poi questo testo.
