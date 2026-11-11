# Specifica ScrambNet — Parte 9: Requisiti dell'implementazione di riferimento

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([en](../../en/spec/09-reference-implementation.md)).

**Stato: BOZZA (DRAFT).** Questa parte enuncia, come requisiti numerati (`RI-n`),
ciò che un nodo reale DEVE (MUST) fare e che la proof-of-concept omette
deliberatamente — ogni regola legata alla minaccia a cui risponde e, dove si
applica, all'invariante (I-1…I-4) che protegge. Il giocattolo in `poc/` è una
*specifica eseguibile*, non un nodo: lo dice nelle sue prime righe ("NOT PRODUCTION
CODE. No constant-time arithmetic, no networking, no onion layer"). Tutto ciò che
segue è la distanza tra quel giocattolo e qualcosa che si possa puntare contro una
rete ostile. Ogni numero è uno strawman da attaccare per numero di requisito;
l'invito più affilato è nel §1, e il §11 nomina ciò che resta aperto.

## 1. La tensione centrale: un livello minimo teorico-informativo è incondizionato solo quanto il codice che lo calcola

ScrambNet vende un livello minimo di contenuto **incondizionato** (I-2, dimostrato
nella Parte 7): sotto `k` quote, il testo cifrato è *statisticamente indipendente*
dal segreto, contro computazione illimitata e qualunque computer quantistico. Quella
dimostrazione riguarda i **valori** — i byte di quota che un avversario detiene non
portano alcuna informazione sul segreto. Non dice nulla su **come una macchina reale
calcoli quei byte**, ed è lì che il livello minimo può essere perso senza che un
solo teorema sia sbagliato.

Una moltiplicazione in GF(2⁸) tramite lookup in tabella (le tabelle `_EXP`/`_LOG`
della PoC, `poc/dispersal.py`) indicizza la memoria a un indirizzo che **dipende da
un byte di quota segreto**. Su hardware reale, lo stato della cache rende quel tempo
di accesso osservabile a un attaccante co-residente. Il lookup perde perciò,
attraverso un canale laterale di timing, proprio i byte che il livello minimo è
costruito per nascondere. Il livello minimo sarebbe allora *incondizionato in teoria
e recuperabile in pratica*.

Questa è la frase più importante di questa parte, enunciata come principio:

> **Un canale laterale di timing o di divulgazione di memoria che riveli byte di
> quota segreti, coefficienti, o la chiave di contenuto non è una rottura
> "computazionale" che I-2 abbia il permesso di avere. È una rottura di I-2
> stesso.** La Parte 7 concede esattamente un'assunzione computazionale — l'AEAD
> end-to-end *sopra* `k` (SP-1a) — e nient'altro. Un canale laterale che divulga
> byte segreti sotto-`k` non costa all'avversario "lavoro sotto un'assunzione"; gli
> consegna i byte. La dimostrazione di SA-1/SA-2 assume che l'avversario veda
> **solo** i `k−1` valori di quota e i parametri pubblici. Un canale laterale
> aggiunge una vista che la dimostrazione non ha mai concesso, e la dimostrazione
> non la copre.

Due conseguenze, che il resto di questa parte rende normative:

- Il **percorso di calcolo** del livello minimo — ogni operazione GF(2⁸) su dati
  dipendenti dal segreto in split di Shamir, reconstruct, e interpolazione di
  Lagrange — DEVE (MUST) essere a tempo costante (RI-1). Questo non è un
  irrobustimento; è la condizione sotto la quale SA-1/SA-2 descrivono il sistema
  reale, esattamente come lo è SA-3 (casualità dei coefficienti).
- Il **residuo di memoria** del livello minimo — quote, coefficienti, chiavi
  derivate — NON DEVE (MUST NOT) sopravvivere per essere letto da un heap dump, da
  un file di swap, o da un core dump (RI-9). Un livello minimo che è
  teorico-informativo sul filo ma recuperabile da `/proc` non è un livello minimo.

La PoC è onesta sul fatto che fallisce entrambi: è fatta di lookup in tabella in
puro Python senza azzeramento, corretta ma con perdite, e lo dichiara. Questa parte
è l'elenco che un nodo reale deve invece soddisfare. Dove la PoC *già* impone una
regola (rifiuta di disperdere testo in chiaro che non sia passato per l'AEAD —
`send()` esegue seal prima di split), quella è l'asticella, non un vezzo, e RI-6 la
innalza a un DEVE (MUST).

**Ambito.** Questa parte vincola l'*implementazione* di costruzioni fissate altrove;
non introduce alcun nuovo formato sul filo e non cambia alcun byte sul filo (ciò
sarebbe un cambiamento I-1/I-4 e appartiene alle Parti 1–6). NON DEVE (MUST NOT)
essere letta come se rilassasse un qualsiasi requisito che referenzia; dove sembri
farlo, la parte referenziata vince e la contraddizione è un difetto da segnalare.

## 2. Aritmetica di campo a tempo costante (il percorso di calcolo del livello minimo)

- **RI-1 (GF(2⁸) a tempo costante, protegge I-2).** Tutta l'aritmetica GF(2⁸)
  applicata a dati dipendenti dal segreto — `split` di Shamir (valutazione
  polinomiale su coefficienti segreti e il termine noto segreto),
  `reconstruct`/interpolazione di Lagrange (inclusa l'**inversione** di campo
  `gf_inv` nel denominatore della base), e qualunque moltiplicazione il cui operando
  sia un byte di quota, un coefficiente, o un byte segreto ricostruito — DEVE (MUST)
  essere calcolata **senza diramazioni dipendenti dal segreto e senza accesso a
  indirizzi di memoria dipendenti dal segreto**. Concretamente, un'implementazione
  NON DEVE (MUST NOT) indicizzare una tabella (`_EXP`/`_LOG`, una S-box, o qualunque
  array) a un offset derivato da un valore segreto. Tecniche conformi sono una
  moltiplicazione bitsliced o tower-field a tempo costante, una riduzione
  carry-less-multiply (`CLMUL`), o un campo fornito da una libreria che *documenta*
  un comportamento a tempo costante per queste operazioni. Minaccia: un avversario
  co-residente o di remote-timing recupera byte di quota segreti dalla cache o dal
  timing di diramazione — una **rottura diretta di I-2** (vedi §1), non una
  computazionale. Questo si applica simmetricamente a **split e reconstruct**: un
  endpoint che ricostruisce perde il segreto che ha appena recuperato esattamente
  come uno splitter perde quello che sta disperdendo.
- **RI-1a (inversione e divisione non sono esenti).** L'inverso del denominatore di
  Lagrange (`gf_inv` in `poc/dispersal.py`, calcolato lì come `_EXP[255 − _LOG[a]]`)
  opera su un valore derivato dall'insieme di quote segrete e DEVE (MUST) essere a
  tempo costante; un'esponenziazione dipendente dai dati o un inverso tramite lookup
  in tabella è non conforme. Un'implementazione DOVREBBE (SHOULD) preferire
  un'interpolazione priva di inversioni (ad es. raggruppando i denominatori e
  invertendo una sola volta via Fermat `a^{254}` con una catena di addizioni fissa,
  o il trucco di Montgomery) così che non rimanga alcuna divisione dipendente dal
  segreto. I punti di valutazione `x_1…x_n` sono **pubblici** (Parte 7 §2), perciò
  l'aritmetica su *quelli soltanto* non deve essere a tempo costante; nel momento in
  cui un punto pubblico è moltiplicato dentro un segreto, il prodotto è segreto.
- **RI-1b (i vettori non certificano il timing).** Superare i vettori di test GF
  della roadmap 3.2 dimostra che una moltiplicazione è *corretta*, non che è *a
  tempo costante*: le tabelle con perdite della PoC superano quegli stessi vettori.
  Un'implementazione NON DEVE (MUST NOT) trattare la conformità ai vettori come prova
  di conformità a RI-1. Il comportamento a tempo costante DOVREBBE (SHOULD) essere
  verificato con uno strumento di analisi del timing o statistico (ad es. test di
  leakage in stile dudect) e, dove la piattaforma lo consente, disabilitando le
  trasformazioni del compilatore che reintroducono diramazioni dipendenti dal
  segreto (RI-9b).
- **RI-1c (l'intera vita del segreto è a tempo costante, non solo le sue operazioni
  di campo, protegge I-2).** La disciplina a tempo costante è definita dal **flusso
  dei dati, non dal nominare le operazioni GF**: qualunque valore contaminato da un
  byte di quota, un coefficiente, o un byte segreto ricostruito eredita l'obbligo di
  RI-1 finché non è azzerato (RI-9), e tale obbligo si estende *oltre* lo strato di
  campo. In particolare, il prefisso di lunghezza del segreto ricostruito (SP-8)
  DEVE (MUST) essere analizzato, e il testo in chiaro recuperato copiato, affettato,
  e validato, **senza una diramazione dipendente dal segreto e senza un accesso a
  memoria dipendente dalla lunghezza segreta**; `unpad` NON DEVE (MUST NOT) diramare
  sulla lunghezza decodificata in un modo che un osservatore possa misurare nel
  tempo, e nessun confronto, controllo di limiti, o spostamento di buffer su un
  segreto può essere dipendente dai dati. Minaccia: il principio stesso del §1 — "un
  endpoint che ricostruisce perde il segreto che ha appena recuperato esattamente
  come uno splitter perde quello che sta disperdendo" — è imposto solo se *l'intera*
  gestione del segreto recuperato è a tempo costante, non soltanto la sua aritmetica
  GF. Un nodo che usa un campo a tempo costante verificato (RI-1) e un AEAD a tempo
  costante vagliato (RI-8) ma poi dirama su una lunghezza recuperata soddisfa ogni
  altro DEVE (MUST) mentre perde la struttura del segreto recuperato attraverso il
  timing, che è una rottura diretta di I-2 per lo stesso argomento di RI-1.

## 3. Disciplina del CSPRNG (il livello minimo è robusto esattamente quanto la sua casualità)

Il livello minimo non è più robusto della casualità dei coefficienti di Shamir: SA-3
della Parte 7 è il "componente di massima assicurazione" dell'intera specifica, e
`test_properties.test_coefficient_reuse_breaks_the_floor` mostra che il riuso perde
il segreto con certezza. La stessa disciplina governa ogni altro segreto che il nodo
estrae.

- **RI-2 (DRBG crittografico dal sistema operativo, protegge I-2 tramite SA-3).**
  Tutta la casualità segreta — coefficienti di Shamir (SA-3), l'effimero di circuito
  per-pacchetto `x` di CH-3, `msg_nonce`/contatori di messaggio dove non
  deterministici, generazione di `kpair`, e qualunque salt di `box_id` — DEVE (MUST)
  essere prodotta da un DRBG crittograficamente sicuro inizializzato con seed dal
  CSPRNG del sistema operativo (`getrandom`/`getentropy`, `/dev/urandom` dopo che il
  pool è inizializzato, o una sorgente equivalente che blocca finché non è
  inizializzata con seed). Un'implementazione NON DEVE (MUST NOT) usare un PRNG non
  crittografico (un LCG, Mersenne Twister, `rand()`, un hash-di-contatore, o uno
  stream riusato come "casuale") per alcun valore di questo elenco.
- **RI-2a (sicurezza su fork e clone — la catastrofe classica).** Un processo che
  esegue `fork()`, viene ripristinato da un checkpoint, viene migrato, o viene
  clonato come immagine di VM o container NON DEVE (MUST NOT) riusare uno stato DRBG
  che ha prodotto output prima della scissione. L'implementazione DEVE (MUST)
  reinizializzare con seed dal sistema operativo su fork/ripristino (ad es. una
  disciplina `pthread_atfork`/`MADV_WIPEONFORK`, o un prelievo dall'OS a ogni
  chiamata) così che nessuna coppia di processi emetta mai lo stesso stream di
  coefficienti o lo stesso effimero `x`. Minaccia: due cloni VM identici eseguono lo
  split di messaggi *diversi* sotto gli **stessi coefficienti**, e per SA-3 la coppia
  di insiemi di quote diventa correlata con entrambi i segreti — la catastrofe di
  casualità da manuale, e una rottura diretta di I-2. È evidenziata specificamente
  perché è invisibile a qualunque test a singolo processo.
- **RI-2b (controlli di salute e di avvio).** Prima di emettere il primo valore
  segreto, un nodo DEVE (MUST) confermare che la sorgente di entropia dell'OS sia
  inizializzata con seed (NON DEVE (MUST NOT) ripiegare su una sorgente a bassa
  entropia se il pool non è pronto) e DOVREBBE (SHOULD) eseguire un self-test di
  avvio sul DRBG. Un nodo DOVREBBE (SHOULD) eseguire un test continuo di
  ripetizione/output bloccato sull'entropia grezza dove vi ha accesso, e DEVE (MUST)
  fallire in modo sicuro (fail closed) — rifiutare di eseguire split o di costruire
  un pacchetto — invece di procedere con un generatore sospetto. Un generatore che
  non può essere verificato è trattato come rotto.
- **RI-2c (nessun coefficiente iniettabile in produzione — ma i vettori di
  conformità girano ancora).** Il parametro `split(..., coeffs=...)` della PoC esiste
  solo perché i vettori possano essere deterministici e la rottura da riuso
  dimostrata. Un artefatto di produzione NON DEVE (MUST NOT) esporre alcun percorso —
  flag, config, variabile d'ambiente, o simbolo — che permetta a un chiamante di
  fornire, loggare, o fissare i coefficienti di Shamir o l'effimero `x`; un tale
  percorso è un foot-gun di SA-3. La riconciliazione con i vettori di conformità
  della roadmap 3.2 (RI-10), che richiedono coefficienti iniettati deterministici per
  riprodurre, è un **cancello di test a build-time**: il percorso di iniezione PUÒ
  (MAY) esistere *solo* dietro un cancello che sia **assente da qualunque artefatto
  di produzione** e irraggiungibile a runtime in produzione. I vettori sono
  confrontati con una build di test che abilita il cancello; la build di produzione
  DEVE (MUST) essere identica ad essa salvo l'assenza del codice dietro il cancello,
  e tale equivalenza DOVREBBE (SHOULD) essere verificata dalla build (ad es. un diff
  riproducibile delle due). "Compilato via, non meramente scoraggiato" significa
  esattamente questo: presente per il binario di test, fisicamente assente da quello
  spedito — mai un interruttore a runtime.

## 4. Stato del nonce e della rotazione di chiave attraverso i riavvii

Due segreti diversi non devono mai essere riusati attraverso un riavvio: il nonce
AEAD/tag (SP-7b) e l'epoca statica `onion` del relay (CH-5). Un riavvio è il momento
in cui un nodo è più tentato di "ripartire da capo" e riusare un valore che ha già
usato.

- **RI-3 (il massimo raggiunto monotono del nonce (high-water mark) sopravvive ai
  riavvii, protegge SP-7b e SP-1a).** Per `kpair`, il `msg_nonce` del mittente (un
  contatore di messaggi strettamente crescente, SP-7b) DEVE (MUST) essere persistito
  e NON DEVE (MUST NOT) retrocedere attraverso un riavvio, crash, o cambio di
  orologio. L'implementazione DEVE (MUST) eseguire `fsync` (o la barriera durevole
  equivalente della piattaforma) del massimo raggiunto **su memoria stabile prima
  che il nonce che esso copre sia usato sul filo**, così che un crash tra l'uso e la
  persistenza possa solo *saltare* dei nonce, mai ripeterli. Un nodo NON DEVE (MUST
  NOT) riusare o diminuire un `msg_nonce` sotto una stessa `kpair`. Minaccia: un
  `msg_nonce` riusato è **doppiamente fatale** (SP-7b) — fa collidere i tag SP-7
  (rendendo un insieme di quote collegabile attraverso drop in collusione) **e**,
  poiché `msg_nonce` è il nonce di ChaCha20-Poly1305 (SP-1a), distrugge la
  confidenzialità dell'AEAD come un two-time pad. Retrocedere il contatore dopo un
  backup ripristinato è il fallimento realistico, ed è una rottura di confidenzialità,
  non un intoppo.
- **RI-3a (riservare in anticipo per limitare il costo di fsync).** Un'implementazione
  PUÒ (MAY) persistere il massimo raggiunto a blocchi (riservare `B` nonce con una
  scrittura durevole, distribuirli dalla memoria, persistere di nuovo prima che il
  blocco sia esaurito) per evitare un fsync per messaggio. Un crash spreca allora al
  più la coda inutilizzata di un blocco — accettabile, perché lo spazio del contatore
  è ampio e saltare è sicuro mentre ripetere è fatale. NON DEVE (MUST NOT), sotto
  alcun percorso di recupero da crash, distribuire un nonce pari o inferiore
  all'ultimo massimo persistito durevolmente.
- **RI-3b (un ripristino non è un riavvio — rilevare il rollback o ritirare la
  chiave, protegge SP-7b/SP-1a).** RI-3/RI-3a difendono da un *crash* (il massimo
  persistito si muove solo in avanti); **non** difendono da uno snapshot di VM, uno
  snapshot di filesystem, o un **ripristino** da backup che riavvolga il massimo
  persistito stesso — precisamente il "retrocedere il contatore dopo un backup
  ripristinato" che RI-3 nomina come il fallimento realistico. Un nodo NON DEVE (MUST
  NOT) assumere che il suo archivio di nonce persistito sia monotono attraverso un
  tale ripristino. DEVE (MUST) perciò o (a) legare il massimo raggiunto a un
  nonce-**salt** per-boot/per-ripristino (o un contatore di generazione monotono)
  persistito nella *stessa scrittura durevole* della riservazione, così che un
  archivio riavvolto sia rilevabile, e al rilevamento **ritirare la `kpair`** —
  derivare una chiave di contenuto/tag fresca, trattando un salt riusato sotto un
  contatore riavvolto come compromissione — oppure (b) rifiutare di emettere sotto la
  `kpair` interessata a qualunque segno di ripristino (l'orologio di sistema che va
  all'indietro, o il contatore di generazione persistito che diminuisce) finché una
  `kpair` fresca non sia negoziata fuori banda (Parte 6). Riservare in anticipo
  (RI-3a) DEVE (MUST) portare il contatore di generazione nella scrittura durevole
  della riservazione, così che un ripristino non possa rigiocare un intero blocco
  riservato senza essere rilevato. Minaccia: senza questo, un ripristino da snapshot
  riemette un intero blocco di valori `msg_nonce` già usati — il two-time pad
  doppiamente fatale di RI-3, su un percorso che la guardia solo-crash di RI-3a non
  può vedere.
- **RI-4 (stato dell'epoca statica `onion` e ritiro sicuro, protegge CH-5/CH-6).** Un
  relay DEVE (MUST) persistere in quale epoca statica `onion` si trova (la chiave
  privata attiva, i suoi `created`/`expiry`, e la finestra di grazia per il traffico
  in transito) così che un riavvio non ripubblichi in silenzio una chiave scaduta,
  non resusciti una ritirata, né conii una seconda statica "fresca" dentro la stessa
  epoca dichiarata. Alla rotazione (≤7-day, CH-5) il relay DEVE (MUST), una volta
  trascorsa la grazia per il traffico in transito, **azzerare la metà privata della
  statica ritirata** (RI-9) e NON DEVE (MUST NOT) conservarla; un relay che tiene
  vecchie statiche ingrandisce la propria finestra di esposizione alla collegabilità
  di CH-6 ed è non conforme. I client restano vincolati da GR-4/CH-5 a rifiutare
  qualunque record la cui `expiry` superi `created + 7 days` (GR-2 chiave 6), così che
  un nodo che dimentica la propria epoca non possa estendere la finestra
  ripubblicando. Minaccia: un riavvio che riporta la statica dentro una finestra che
  il client ha già visto, o che non distrugge una statica ritirata, riapre
  esattamente l'esposizione alla collegabilità di CH-5a che il tetto di rotazione
  esiste per limitare.

## 5. Persistenza della cache di replay

ScrambNet rifiuta i replay a due strati, ed entrambi sono con stato: lo strato di
circuito scarta un `gamma` visto per epoca di chiave (SP-5), e lo strato di
memorizzazione scarta un rideposito di un `(box_id, slot)` già memorizzato (SP-7b,
RZ-7). Un riavvio che dimentica questo stato riapre una finestra di replay.

- **RI-5 (lo stato di replay sopravvive ai riavvii, limitato all'epoca, protegge
  SP-5 / SP-7b).** Un relay DEVE (MUST) persistere, o ricostruire in modo sicuro e
  completo, la propria cache di replay Sphinx dei valori `gamma` visti **per l'epoca
  di chiave corrente**, e un drop DEVE (MUST) persistere il proprio insieme di
  depositi `(box_id, slot)` memorizzati, così che un riavvio o crash non accetti un
  pacchetto o un deposito che ha già visto all'interno dell'epoca viva. Minaccia: un
  relay che si riavvia con una cache di replay vuota riammetterà ogni pacchetto che
  un avversario ha catturato e reinietta dentro l'epoca — una finestra di replay
  riaperta, che allo strato di drop può anche moltiplicare o spostare posta onesta
  contro il limite per-casella di RZ-7.
- **RI-5a (la cache è limitata — da due finestre di ritenzione *diverse*, non "dall'
  epoca").** Le due cache di replay sono ciascuna limitata in memoria, ma da finestre
  **distinte** che un'implementazione NON DEVE (MUST NOT) confondere:
    - la cache dei `gamma` di Sphinx è limitata dall'**epoca di chiave statica onion**
      (CH-5, ≤7-day) — un `gamma` è replicabile solo finché la chiave che lo ha
      chiavato è viva;
    - l'insieme di deduplicazione dei depositi `(box_id, slot)` è limitato dalla
      **scadenza dello slot** (RZ-7, 7 days), **non** dalla rotazione giornaliera del
      `box_id` (RZ-10). Il box id ruota quotidianamente per l'*indirizzamento*, ma uno
      slot depositato è *memorizzato* per fino a 7 giorni (più la grazia di confine di
      RZ-14), così che un rideposito è scartabile per tutto il tempo in cui lo slot
      con cui collidere può ancora essere memorizzato — fino a ~7 epoche di box.
      Dimensionare questo insieme a un giorno lo sottodimensiona di ~7×.
  Un'implementazione DEVE (MUST) scartare lo stato di ciascuna cache una volta
  trascorsa la sua propria finestra (la cache dei `gamma` alla fine dell'epoca di
  chiave, l'insieme di depositi alla scadenza dello slot), il che limita la memoria a
  grosso modo il volume di pacchetti dell'epoca di chiave e il volume di depositi di 7
  giorni rispettivamente. PUÒ (MAY) limitare ulteriormente la memoria con una
  struttura di conteggio (ad es. un filtro di Bloom/cuckoo dimensionato) **solo se**
  è tarata così che i falsi positivi restino sotto un tasso operativamente
  trascurabile; un falso positivo scarta un pacchetto onesto (un DoS autoinflitto),
  un falso negativo ammette un replay (un fallimento di sicurezza), così che la
  struttura DEVE (MUST) essere dimensionata per rendere il secondo impossibile entro
  la sua finestra di ritenzione e il primo raro. Un nodo che non può persistere una
  cache DEVE (MUST) fallire in modo sicuro (fail closed) per una finestra che non può
  coprire (trattare l'intervallo dimenticato come replicabile e, per la cache dei
  `gamma`, ruotare l'epoca di chiave) invece di accettare replay in silenzio.
- **RI-5b (la ricostruzione deve essere completa, o trattata come una rotazione — e
  un ripristino non è una ricostruzione).** Un'implementazione che ricostruisce lo
  stato di replay dopo un crash (invece di persisterlo in continuo) DEVE (MUST) o
  ricostruirlo completamente per la finestra viva o trattare il divario come l'inizio
  di una nuova epoca di chiave (nuove chiavi, così che i vecchi valori `gamma` non
  siano più accettabili). Una ricostruzione parziale che lascia parte della finestra
  non protetta è non conforme. Inoltre, un **ripristino** di VM/filesystem che
  riavvolge la cache a uno stato *anteriore, dall'aspetto completo* non è un crash e
  il controllo di completezza di RI-5b non può rilevarlo: un relay ripristinato torna
  con una cache di *prima* dei pacchetti che un avversario ha catturato, e li
  riammette. Un nodo DEVE (MUST) trattare qualunque segno di un ripristino (lo stesso
  riavvolgimento di orologio o diminuzione del contatore di generazione di RI-3b)
  come una **rotazione di epoca di chiave** obbligatoria, così che i valori `gamma`
  precedenti al ripristino non siano più accettabili indipendentemente da ciò che la
  cache riavvolta contiene.

## 6. API resistente all'uso improprio (rendere impossibile la cosa insicura)

I-1 e la disciplina `[soundness]` esigono che l'API renda l'operazione insicura
*irrappresentabile*, non meramente documentata come sconsigliata. L'ordinamento di
SP-1 (cifra **poi** split) e la regola fail-closed di SP-7a sono i due punti in cui
un'API più facilmente si inverte.

- **RI-6 (l'API DEVE rifiutare il testo in chiaro senza AEAD, protegge
  SP-1/SP-1a).** Il punto di ingresso della dispersione DEVE (MUST) rifiutare
  qualunque input che non sia già passato per l'AEAD end-to-end (SP-1a): disperde
  **solo testo cifrato**, mai testo in chiaro. NON DEVE (MUST NOT) esistere un
  percorso pubblico "fai lo split di questi byte grezzi" che bypassi l'ordinamento
  cifra-poi-split di SP-1 — cioè nessun modo per raggiungere `split()` senza il seal
  AEAD davanti ad esso. La PoC soddisfa già questa asticella: `send()` chiama
  `e2e.seal` prima di `disperse`, e `dispersal.py` è documentato per "non toccare mai
  il testo in chiaro." Un nodo reale DEVE (MUST) tenere quella porta chiusa a livello
  di tipo, non per convenzione. Minaccia: eseguire lo split di testo in chiaro
  direttamente distrugge la *cintura computazionale* (tier 2 della Parte 7) — le
  quote ricostruiscono allora direttamente al testo in chiaro per qualunque
  avversario `≥k`, senza alcun AEAD dietro di esse — e inverte la composizione su cui
  poggia l'intero progetto.
- **RI-6a (separare per tipo il testo cifrato dal testo in chiaro).** Un'
  implementazione DOVREBBE (SHOULD) rappresentare "testo in chiaro" e "testo cifrato
  end-to-end" come tipi distinti, non intercambiabili, così che l'ordinamento di SP-1
  non possa essere invertito passando il buffer sbagliato e una chiamata "fai lo
  split di byte grezzi" sia un errore a compile-time piuttosto che un controllo a
  runtime. Dove il linguaggio non può imporlo, il nodo DEVE (MUST) interporre una
  guardia a runtime che sia attiva di default e non possa essere disabilitata da
  configurazione.
- **RI-6b (i punti di ingresso di campo grezzi DEVONO essere privati del modulo).**
  La separazione per tipo (RI-6a) non basta da sola: i `split`/`reconstruct` grezzi e
  qualunque punto di ingresso di campo diretto DEVONO (MUST) essere privati del
  modulo (non esportati), così che gli *unici* simboli pubblici di dispersione siano
  quello che prende il tipo testo-cifrato-AEAD (RI-6) e quello che restituisce un
  risultato di apertura autenticata (RI-7). Un simbolo pubblico `split(raw_bytes)` o
  `reconstruct(...)` è di per sé il difetto, indipendentemente da ciò che un
  chiamante gli passa — in un linguaggio dove `bytes` è `bytes`, uno split grezzo
  esportato lascia che un chiamante di livello inferiore bypassi il cancello AEAD pur
  passando il controllo di tipo in modo pulito. La PoC li espone a livello di modulo
  *perché è una specifica eseguibile*; un nodo reale NON DEVE (MUST NOT).
- **RI-7 (la ricostruzione DEVE fallire in modo sicuro (fail closed), a tempo
  costante, protegge SP-7a).** Il tag AEAD è l'**unico** arbitro di integrità
  (SP-7a): la ricostruzione di Shamir non ne ha uno proprio, così che un byte di
  quota invertito o un `(k,n)` mentito produce un candidato coerente-ma-sbagliato che
  solo l'AEAD rifiuta. L'API di ricostruzione DEVE (MUST) restituire un messaggio
  **solo** dopo che l'AEAD end-to-end ha verificato, e DEVE (MUST) scartare — mai
  esporre, loggare, o agire su — qualunque candidato il cui tag fallisca. NON DEVE
  (MUST NOT) esporre un risultato di "ricostruzione non autenticata" al codice
  applicativo. **Lo scarto fail-closed DEVE (MUST) essere anche a tempo costante
  rispetto al *perché* ha fallito:** il percorso ricostruisci-poi-apri DEVE (MUST)
  impiegare un tempo indistinguibile ed emettere nessuna risposta distinguibile
  (CH-9/I-4) sia che il tag AEAD abbia verificato, sia che il byte `(k,n)` sia stato
  mentito (RI-7a), sia che i byte di quota siano stati corrotti — un avversario che
  può alimentare candidati di ricostruzione (il residuo del drop ostile di SP-7a, o
  una coalizione `≥k` che rigioca insiemi di quote) NON DEVE (MUST NOT) apprendere
  quale, per timing o per risposta, altrimenti il percorso di rifiuto diventa un
  distinguitore in stile padding-oracle anche se il *confronto* del tag (RI-8) è a
  tempo costante. La PoC fissa il comportamento fail-closed (`receive()` scarta sul
  `ValueError` da `e2e.open_`, `test_tampered_share_fails_closed`); un nodo reale NON
  DEVE (MUST) aggiungere un percorso che lo aggiri, né una porta laterale di timing
  che lo attraversi. Minaccia: consegnare in alto una ricostruzione non autenticata
  trasforma il residuo di negazione del servizio accettato di SP-7a nella consegna di
  spazzatura scelta dall'attaccante; misurare nel tempo il rifiuto lo trasforma in un
  oracolo.
- **RI-7a (analizzare il byte `params` in modo difensivo, non fidarsi di esso).** Il
  byte `(k,n)` è controllato dall'attaccante su una quota ostile (SP-7a) e bloccato
  nell'ordine dei nibble dai vettori (SP-7a / roadmap 3.2). Un'implementazione DEVE
  (MUST) validarlo rispetto all'ordine bloccato dai vettori e rispetto a
  `1 ≤ k ≤ n ≤ 15` (come fa `_check_params`) prima dell'uso, e DEVE (MUST) trattare
  una ricostruzione sotto un `(k,n)` mentito come un ordinario scarto fail-closed
  (RI-7), mai come una ragione per allocare memoria illimitata o indicizzare fuori dai
  limiti.

## 7. L'AEAD e il confronto del tag (anche la cintura deve essere a tempo costante)

La cintura computazionale (tier 2, Parte 7 §5) è solida solo quanto la sua
implementazione. L'AEAD della PoC è corretto rispetto a RFC 8439 ma esplicitamente
**non** è a tempo costante ("è corretto … ma perde attraverso il timing, perciò un
nodo reale DEVE (MUST) usare una libreria a tempo costante vagliata").

- **RI-8 (AEAD e confronto del tag a tempo costante, protegge SP-1a / SP-7).** Un
  nodo DEVE (MUST) usare un'implementazione di ChaCha20-Poly1305 il cui percorso dei
  dati e il cui **confronto del tag di autenticazione** siano a tempo costante, e
  DEVE (MUST) confrontare il tag di quota SP-7 e il tag AEAD SP-7a con una primitiva
  di uguaglianza a tempo costante (nessun `memcmp` con uscita anticipata, nessuna
  diramazione dipendente dai dati sui byte del tag). Minaccia: un controllo del tag
  non a tempo costante è un classico oracolo di contraffazione — il timing
  byte-per-byte sul confronto lascia che un avversario contraffaccia un tag valido —
  che attacca la cintura (SP-1a) e il tag di riconoscimento di quota (SP-7)
  direttamente. L'aritmetica di Poly1305 e X25519 DEVE (MUST) essere parimenti a
  tempo costante (RI-11); un'implementazione a tempo variabile di una delle due
  perde materiale di chiave attraverso il timing.

## 8. Lo strato a cipolla che il giocattolo omette

La PoC ha "no onion layer": `dispersal.py` opera solo sulla quota del payload
`delta`, e l'header Sphinx (`alpha`/`beta`/`gamma`) e la sua crittografia per salto
esistono solo come la specifica della Parte 1 §5. Un nodo reale DEVE (MUST)
implementare quello strato, e la sua crittografia è nell'ambito qui perché porta
materiale segreto (i segreti di salto e l'effimero del client) sotto la stessa
minaccia di canale laterale del livello minimo.

- **RI-10 (implementare la derivazione per salto di CH-2, protegge I-1/I-4).** Un
  nodo DEVE (MUST) implementare l'handshake di circuito Sphinx della Parte 1 §5
  esattamente: per salto, derivare il segreto condiviso
  `s_i = X25519(alpha_i, onion_i)` dall'elemento di gruppo accecato e dalla statica
  del relay (CH-2), e derivare la chiave del cifrario a flusso delle info di
  instradamento, la chiave del MAC `gamma`, e la chiave AEAD `delta` da `s_i` tramite
  HKDF-BLAKE2s sotto le etichette fisse `sphinx-rho`, `sphinx-mu`, `sphinx-delta`
  (CH-2; byte esatti delle etichette e concatenamento bloccati da vettori sotto
  roadmap 3.2). DEVE (MUST) eseguire l'accecamento Sphinx (ri-randomizzare `alpha`
  per salto) e imporre la disciplina di replay di SP-5. Non c'è **alcuna trascrizione
  di handshake separata** (CH-1); un nodo che emette o si attende un qualsiasi
  messaggio Noise/handshake su un circuito è non conforme (CH-1). *Flag:* i vettori di
  test cross-implementazione per questa derivazione sono roadmap 3.2 e DEVONO (MUST)
  essere soddisfatti una volta pubblicati; fino ad allora, due implementazioni non
  sono ancora dimostrate interoperabili a questo strato (I-1), e ciò è dichiarato
  apertamente invece di essere assunto.
- **RI-11 (X25519 a tempo costante e la disciplina dell'effimero senza chiavi,
  protegge CH-3/CH-6/I-2).** La moltiplicazione scalare X25519 su ogni salto DEVE
  (MUST) essere a tempo costante (un'implementazione a scala di Montgomery senza
  alcuna diramazione o accesso a memoria dipendente dal segreto); un X25519 a tempo
  variabile perde lo scalare di salto e quindi il segreto di salto. Lo scalare
  effimero del client per-pacchetto `x` dietro `alpha_0` (CH-3) DEVE (MUST) essere
  estratto fresco dal CSPRNG (RI-2) per pacchetto, NON DEVE (MUST NOT) mai essere
  riusato tra pacchetti, e DEVE (MUST) essere azzerato immediatamente dopo che il
  pacchetto è costruito (RI-9) — la sua distruzione è ciò che rende reale la forward
  secrecy a granularità d'epoca di CH-6 (un `x` conservato lascia che un successivo
  sequestro della statica del relay ricalcoli il segreto di salto che il progetto
  promette sparito). Un relay DEVE (MUST) parimenti tenere la propria statica `onion`
  sotto la gestione di chiavi di RI-2 e la rotazione/ritiro di RI-4, e calcolare con
  essa a tempo costante.
- **RI-11a (rifiutare il segreto condiviso degenere, nel modo corretto per X25519).**
  X25519 deliberatamente non espone alcun test economico on-curve/order (RFC 7748),
  perciò "validare il punto `alpha`" non è il controllo costruibile; quello
  richiesto e costruibile è: calcolare `s_i = X25519(alpha_i, onion_i)` e, **a tempo
  costante, rifiutare se il segreto condiviso risultante è tutto a zero** (l'esito
  low-order / small-subgroup) *prima* di derivare qualsiasi chiave di salto da esso.
  Questo nega a un predecessore malevolo un salto a ordine piccolo forzato o a chiave
  nota. Poiché ogni byte sul filo è uniforme (SP-4/I-4), il controllo è sul *segreto
  calcolato*, non su un flag in chiaro, e un relay DEVE (MUST) processare un `alpha`
  rifiutato in tempo e byte **indistinguibili da un ordinario scarto per replay**
  (SP-5/CH-9/I-4) — nessuna risposta distinguibile, nessuna spia di timing. La regola
  completa di validazione/codifica del punto è bloccata da vettori sotto roadmap 3.2,
  ma il rifiuto dell'output tutto-a-zero è normativo *qui* così che il requisito sia
  costruibile senza attendere quel file (I-1).

## 9. Azzeramento della memoria, swap, e sicurezza in caso di guasto

Un livello minimo che è incondizionato sul filo ma recuperabile da un heap dump, un
file di swap, o un core dump non è un livello minimo (§1). La divulgazione di memoria
rivela proprio i byte sotto `k` che I-2 protegge, perciò l'azzeramento è un requisito
I-2, non igiene.

- **RI-9 (tenere i segreti in memoria azzerabile e cancellarli dopo l'uso, protegge
  I-2).** Le quote di Shamir, i coefficienti polinomiali, il segreto ricostruito,
  ogni chiave derivata (`content_key`, la chiave del `tag` SP-7, la chiave del
  `box_id`, ogni chiave di salto Sphinx `s_i` e le sue derivate), la `kpair`
  precondivisa, l'effimero del client `x` (RI-11), e la statica `onion` del relay
  (RI-4) DEVONO (MUST) essere tenuti in memoria che il nodo possa sovrascrivere in
  loco e DEVONO (MUST) essere azzerati non appena non sono più necessari. L'obbligo è
  enunciato come *scelta della memoria prima* perché un nudo "azzera" è
  **fisicamente impossibile** in alcuni dei linguaggi target di questa specifica: in
  CPython (il linguaggio della PoC di riferimento) un segreto in un oggetto `bytes`
  immutabile può essere internato, copiato dall'allocatore, e liberato senza alcuna
  sovrascrittura raggiungibile, e un GC copiante/compattante (Go, Java, …) può
  rilocare un segreto così che nessuna singola cancellazione raggiunga ogni copia.
  Perciò:
    - In un runtime che fornisce memoria segreta **mutabile in loco e
      deterministica**, il nodo DEVE (MUST) azzerare con una primitiva che il
      compilatore non possa elidere come dead store
      (`explicit_bzero`/`memset_s`/`SecureZeroMemory`/una barriera `volatile` o il
      `Zeroize` auditato del linguaggio) — un semplice `memset` su un buffer da
      liberare è di routine ottimizzato via.
    - Dove il linguaggio **non può** garantirlo (stringhe di byte immutabili, un GC
      copiante/compattante, semantica di copia-valore), il nodo DEVE (MUST) tenere
      ogni segreto in memoria **pinned/native/off-heap** che *possa* azzerare (la
      clausola della memoria nativa di RI-9b è allora un **DEVE (MUST)**, non un
      DOVREBBE (SHOULD)) e NON DEVE (MUST NOT) tenere affatto il segreto in un oggetto
      gestito dal runtime (un `bytes`/`str`, un array su heap GC).
  Il requisito è dunque "usa memoria azzerabile, poi cancellala" — soddisfabile in
  ogni linguaggio — invece di "cancella un oggetto che il runtime non ti lascerà
  raggiungere." Minaccia: questi sono esattamente i byte segreti sotto-`k` che il
  livello minimo nasconde; lasciarli in heap liberato, un buffer riusato, una copia
  GC rilocata, o una struttura loggata lascia che una successiva lettura di memoria li
  ricostruisca, il che è una rottura di I-2 per divulgazione di memoria.
- **RI-9a (tenere i segreti fuori da swap e core dump).** I buffer segreti DOVREBBERO
  (SHOULD) essere bloccati in RAM (`mlock`/`mlockall`/`VirtualLock`) così che non
  siano mai paginati su un file di swap persistente, e il processo DOVREBBE (SHOULD)
  disabilitare i core dump (`RLIMIT_CORE = 0` o l'equivalente di piattaforma) o
  escludere le pagine segrete da essi. Un nodo che non può prevenire lo swapping delle
  pagine segrete DOVREBBE (SHOULD) usare un deployment a swap cifrato e DEVE (MUST)
  documentare il residuo. Minaccia: un file di swap o un crash dump è una copia
  durevole, residente su disco, dei byte sotto-`k` — il livello minimo, versato su
  memoria dove sopravvive al processo assai a lungo.
- **RI-9b (sconfiggere i pericoli dell'ottimizzatore e del linguaggio).** Un'
  implementazione DEVE (MUST) assicurare che il compilatore e il runtime del
  linguaggio non reintroducano le perdite che queste regole vietano: nessuna
  diramazione dipendente dal segreto resuscitata dall'ottimizzazione (RI-1), nessun
  segreto copiato-e-dimenticato da un contenitore che si rialloca, un valore spostato,
  un heap con garbage collection o GC copiante, l'internamento di stringhe, o una
  traccia di eccezione/stack che cattura un buffer segreto. Nei linguaggi a memoria
  gestita dove un buffer può essere copiato dal runtime, un nodo DOVREBBE (SHOULD)
  tenere i segreti in memoria pinned/native che possa azzerare deterministicamente, e
  NON DEVE (MUST NOT) affidarsi al garbage collector per cancellarli.
- **RI-12 (sicurezza in caso di guasto ed eccezione — nessun artefatto parziale o
  collegabile, protegge I-2/I-4).** Un crash, un'eccezione, o una cancellazione
  **a metà split** NON DEVE (MUST NOT) emettere un insieme di quote parziale, un
  sottoinsieme di quote sul filo, o un qualsiasi artefatto che colleghi le quote di un
  messaggio, e NON DEVE (MUST NOT) lasciare stato segreto non azzerato. Un'
  implementazione DEVE (MUST) costruire tutte le `n` quote e impegnarsi all'emissione
  come un passo tutto-o-niente rispetto al fallimento, azzerando coefficienti e quote
  su qualunque percorso di errore prima di risalire. Minaccia: un mittente che va in
  crash dopo aver emesso alcune ma non tutte le quote, o che logga una quota
  intermedia in una traccia di stack, consegna a un osservatore un sottoinsieme
  correlato (minando la non collegabilità di SP-7 e, se rivela `≥k` di un messaggio,
  il livello minimo) — e una risalita non azzerata lascia il segreto in memoria
  (RI-9). La gestione dei guasti DEVE (MUST) fallire in modo sicuro (fail closed): su
  qualunque errore durante split, disperse, o reconstruct, produrre nulla e ripulire,
  invece di produrre qualcosa di parziale.

## 10. Come questi requisiti si mappano sugli invarianti e sulle minacce

| `RI` | Protegge | Minaccia che nega (l'attacco al nodo reale) |
|---|---|---|
| RI-1 / 1a / 1b / 1c | I-2 | recupero per cache-/branch-timing dei byte sotto-`k`, inclusa la gestione del segreto recuperato oltre le operazioni di campo |
| RI-2 / 2a / 2b / 2c | I-2 (SA-3) | RNG debole/forkato/clonabile → coefficienti correlati |
| RI-3 / 3a / 3b | SP-7b, SP-1a | rollback del nonce al riavvio **o ripristino da snapshot/backup** → collisione di tag + two-time pad |
| RI-4 | CH-5 / CH-6 | rollback dell'epoca statica o statica ritirata conservata |
| RI-5 / 5a / 5b | SP-5, SP-7b | stato di replay dimenticato (o riavvolto da ripristino) riapre la finestra di replay; le due cache hanno finestre di ritenzione diverse |
| RI-6 / 6a / 6b | SP-1 / SP-1a | split-prima-di-cifrare distrugge la cintura computazionale; un simbolo pubblico di split grezzo bypassa il cancello |
| RI-7 / 7a | SP-7a | ricostruzione non autenticata **o distinguibile per timing** consegna spazzatura / diventa un oracolo |
| RI-8 | SP-1a, SP-7 | controllo del tag non a tempo costante → oracolo di contraffazione |
| RI-10 | I-1, I-4 | lo strato a cipolla non implementato, costruito in modo interoperabile |
| RI-11 / 11a | CH-3 / CH-6, I-2 | X25519 a tempo variabile o un effimero riusato/conservato |
| RI-9 / 9a / 9b | I-2 | divulgazione heap/swap/coredump dei byte sotto-`k` |
| RI-12 | I-2, I-4 | artefatto parziale/collegabile o risalita da crash non azzerata |

Il filo conduttore: tutto ciò che tocca un valore segreto sotto-`k` (quota,
coefficiente, byte ricostruito, chiave di contenuto, segreto di salto, effimero del
client) è tenuto allo standard proprio del livello minimo — calcolarlo a tempo
costante (RI-1/8/11), generarlo da un CSPRNG solido e sicuro su fork (RI-2),
persistere nessun segreto riusabile attraverso un riavvio (RI-3/4/5), mai lasciare
che l'API salti l'AEAD (RI-6/7), e cancellarlo prima che possa essere riletto
(RI-9/12). Un revisore rompe questa parte trovando un percorso di nodo reale su cui
un tale valore è calcolato a tempo variabile, estratto da uno stream riusato,
ripetuto attraverso un riavvio, esposto non autenticato, o lasciato leggibile in
memoria — e quel percorso è allora una rottura di I-2, non un mero divario di
irrobustimento.

## 11. Cosa questa parte **non** decide

- **Rete, trasporto, e traffic shaping.** Il trasporto camaleonte (Parte 4), la
  strategia di batch/mix e il jitter (SP-6/OP-5), e il timing di emissione delle
  quote (SP-9/OP-4) sono fuori dall'ambito qui; questa parte vincola
  l'implementazione *crittografica*, non lo scheduler. Il residuo di
  correlazione-di-timing tra le quote resta OP-4, non affrontato da alcun RI-n (SA-2 e
  questa parte riguardano i valori, non i tempi di emissione).
- **Selezione dei percorsi e disgiunzione.** Verificare che gli `n` percorsi delle
  quote non condividano un AS o una giurisdizione (OP-1, Parte 3) non è una questione
  di implementazione-di-una-primitiva e non è richiesto qui; RI-7a guarda solo dal
  *fidarsi* di un `(k,n)` mentito, non da un insieme di percorsi non disgiunto.
- **Sybil/eclipse e lo strato di gossip.** La crittografia corretta di un nodo
  conforme non resiste da sola a un avversario dotato di risorse che compra posizione
  (OP-2, GR-20a); quel residuo risiede nella Parte 2 ed è intoccato da questa parte.
- **Il dimensionamento esatto della struttura di replay e il meccanismo di
  rilevamento del fork.** RI-5a limita la cache di replay all'epoca e vieta un filtro
  incline ai falsi negativi, ma la struttura dati concreta, i suoi parametri, e il
  mezzo di persistenza sono scelte di implementazione da fissare contro i vettori
  della roadmap 3.2 e il volume di pacchetti del deployment, non fissate qui.
- **Vettori di test e conformità.** I vettori che certificano che due implementazioni
  interoperano — le tabelle GF come normative, la derivazione Sphinx per salto, il
  percorso cifra→split→deposita→interroga→ricostruisci→decifra — sono **roadmap 3.2**
  e sono referenziati (RI-1b, RI-7a, RI-10, RI-11a) ma non riprodotti qui. RI-1b è
  esplicito sul fatto che quei vettori certificano la correttezza, mai il timing; una
  suite di test sui canali laterali è un obbligo separato, raccomandato (RI-1b) che
  questa parte chiede ma non specifica.
- **Sostituzione della primitiva post-quantistica.** La suite `0x02` (un KEM di salto
  PQ, Parte 1 §5 in chiusura) cambia quale primitiva RI-11 vincola, non il requisito
  che sia a tempo costante; il livello minimo I-2 è PQ-sicuro comunque (SP-1a), perciò
  nulla qui è bloccato su di esso.

## 12. Requisiti introdotti qui

- **RI-1 / RI-1a / RI-1b / RI-1c** — moltiplicazione, inverso, e divisione GF(2⁸) a
  tempo costante, **estesi all'intera vita del segreto recuperato** (l'analisi della
  lunghezza SP-8 e tutta la gestione di un byte ricostruito), non solo le operazioni
  di campo; i vettori certificano la correttezza, non il timing. **[protects I-2]**
- **RI-2 / RI-2a / RI-2b / RI-2c** — disciplina del CSPRNG: DRBG crittografico
  dall'OS, sicurezza su fork/clone, controlli di salute, nessun coefficiente
  iniettabile (dietro cancello di test, non spedito). **[protects I-2 via SA-3]**
- **RI-3 / RI-3a / RI-3b** — massimo raggiunto (high-water mark) di `msg_nonce`
  persistito e senza rollback, fsync-prima-dell'uso, **e un ripristino/snapshot è
  trattato come rollback** (rileva o ritira la `kpair`). **[protects SP-7b / SP-1a]**
- **RI-4** — stato dell'epoca statica `onion` persistito e ritiro con azzeramento.
  **[protects CH-5 / CH-6]**
- **RI-5 / RI-5a / RI-5b** — stato di replay persistito per `gamma` (limitato
  dall'epoca di chiave) e `(box_id, slot)` (limitato dalla **scadenza dello slot di 7
  giorni**, non dalla rotazione giornaliera del box); un ripristino che riavvolge una
  cache è una rotazione di epoca di chiave obbligatoria. **[protects SP-5 / SP-7b]**
- **RI-6 / RI-6a / RI-6b** — l'API rifiuta il testo in chiaro senza AEAD;
  separazione per tipo del testo cifrato; `split`/`reconstruct` grezzi sono privati
  del modulo. **[protects SP-1 / SP-1a]**
- **RI-7 / RI-7a** — ricostruzione fail-closed **e a rifiuto a tempo costante**;
  analisi difensiva di `(k,n)`. **[protects SP-7a]**
- **RI-8** — AEAD a tempo costante e confronto del tag a tempo costante. **[protects
  SP-1a / SP-7]**
- **RI-9 / RI-9a / RI-9b** — memoria azzerabile prima (pinned/native dove il runtime
  vieta la cancellazione in loco), poi azzeramento anti-dead-store; niente swap,
  niente core dump; pericoli dell'ottimizzatore/GC. **[protects I-2]**
- **RI-10** — implementare la derivazione Sphinx per salto di CH-2 e la disciplina di
  replay/accecamento; i vettori sono roadmap 3.2. **[protects I-1 / I-4]**
- **RI-11 / RI-11a** — X25519 a tempo costante; effimero senza chiavi, per-pacchetto,
  azzerato; rifiutare il segreto condiviso tutto-a-zero a tempo costante. **[protects
  CH-3 / CH-6 / I-2]**
- **RI-12** — sicurezza in caso di guasto/eccezione: nessun artefatto parziale o
  collegabile, azzeramento alla risalita, fail closed. **[protects I-2 / I-4]**

Nessuno di questi è un teorema; ciascuno è una condizione sotto la quale i teoremi
della Parte 7 e le garanzie delle Parti 1–6 descrivono un **nodo reale** piuttosto
che il giocattolo. Il giocattolo li omette tutti di proposito e lo dichiara. Rompi
questa parte nominando un percorso di codice di nodo reale che calcola, memorizza, o
divulga un segreto sotto-`k` in un modo che nessun RI-n qui sopra vieta — quel
percorso è un livello minimo rotto in pratica, e trovarlo è l'invito.
