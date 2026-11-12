# Specifica ScrambNet — Parte 11: Governance degli aggiornamenti

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([en](../../en/spec/11-update-governance.md)).

**Stato: BOZZA (DRAFT).** Questa parte decide come un client arriva a eseguire un
binario ScrambNet **più recente** *senza fidarsi di chi l'ha rilasciato*, sotto I-3 —
nessuna autorità — e sotto due vincoli legati al titolare del progetto: **nessun
insieme di firmatari autorevole**, e **nessun push di alcun tipo**. È lo strato di
adozione che la Parte 10 §10.9 nomina come fuori dal proprio ambito. La Parte 10
decide *se questo binario è la build di quella sorgente*; questa parte decide *quale
build eseguire, e quando*. I valori strawman sono contrassegnati con `(s)`.

Leggi prima il §1 e il §10. Insieme dicono cosa compra questa parte (la riproduzione
e la freschezza, non la firma, come arbitro dell'adozione) e cosa concede in testa:
rifiutare sia un'autorità sia un push compra la **latenza di patch** come suo residuo
centrale — un client vulnerabile potrebbe non essere mai rattoppato, e nel caso
peggiore (un client già compromesso dal preciso bug che una patch correggerebbe) può
dimostrabilmente non sentire nemmeno mai parlare della patch (§10.1). Il progetto
accetta deliberatamente quel costo, perché l'alternativa — una parte o un canale che
può fare push di un rilascio a tutti in una volta — è esattamente il kill switch
concentrato che l'intero progetto esiste per negare.

Questa parte riusa anziché reinventare: l'indice di freschezza della Parte 10
(RB-8a), il log di rilascio (RB-13), il gossip (RB-14), la disciplina conta-solo-le-
verificate (RB-10/RB-10a) e lo stato del client-che-non-ricostruisce (RB-7b); il log
di trasparenza senza permessi della Parte 8 (ID-6/ID-7), la difesa dall'equivocazione
della root diffusa via gossip (ID-7a), la regola dei log multipli (ID-7b), e il TOFU
dichiarato (ID-8); il mescolamento delle sorgenti della Parte 2 (GR-8); la superficie
di onestà della Parte 3 (PS-9). La giunzione con la Parte 10 è citata, non
ri-decisa (RB-2, Parte 10 §9).

## 1. La decisione, in due frasi

- **Non esiste un'autorità di rilascio, e non esiste alcun push.** Un rilascio più
  recente è un artefatto riproducibile e indirizzato per contenuto annunciato da un
  append a un log senza permessi (UG-2); un client *apprende* che può esistere solo
  facendo pull e gossip sul proprio calendario (UG-3), *decide* di adottarlo con un
  atto manuale, locale, opt-in (UG-4), e lega quella decisione alla riproduzione
  (RB-7) e alla freschezza (RB-9a), **mai** a chi l'ha annunciato o firmato (UG-1a,
  RB-2).
- **La fiducia nell'adozione fluisce attraverso la riproduzione e la freschezza; la
  revoca può solo informare, mai forzare; e il prezzo — un client non rattoppato o
  compromesso che non adotta mai — è un residuo dichiarato, non un problema risolto.**
  Nessuna firma vincola l'adozione (UG-2a); nessun meccanismo rimuove un binario
  cattivo da un client in esecuzione (UG-8a); il segnale known-bad è un report senza
  permessi, senza forza, ignorabile, mai un'autorità (UG-8).

Quindi l'esito onesto: **l'adozione è priva di autorità tanto quanto la riproduzione
la rende tale, e affidabile tanto quanto un utente che sceglie di agire e non è
eclissato — niente di più.** Il §10 è il residuo che nessuna costruzione qui rimuove.

## 2. Annunciare un rilascio senza un firmatario

- **UG-1 (nessuna autorità di rilascio; l'adozione è un atto locale-al-client).
  [normativo]** Nessun passo dell'*apprendere di*, *validare*, o *adottare* un
  rilascio più recente DEVE (MUST) richiedere di fidarsi che una particolare parte
  l'abbia rilasciato, annunciato, firmato, o benedetto. Le uniche operazioni fidate
  sono quelle che la Parte 10 definisce — ricalcolare `BLAKE2s`, ricostruisci-e-
  confronta (RB-1) — più il confronto degli indici di rilascio monotoni su una linea
  (RB-8a, UG-2c). Qualunque elemento non sostituibile da un surrogato non fidato che
  esegue quelle operazioni è un difetto sotto I-3 e DEVE (MUST) essere rimosso o
  dichiarato nel §10 (la regola ID-1 / RB-1, per l'adozione degli aggiornamenti).
- **UG-1a (l'adozione si lega alla riproduzione, mai alla pubblicazione).
  [normativo]** *Quale* build eseguire è deciso dall'ancora di fiducia della Parte 10
  — si riproduce (RB-7), è fresca (RB-9a) — e da nient'altro su *chi* l'ha annunciata.
  Un client NON DEVE (MUST NOT) adottare una build *perché* è stata annunciata da una
  qualunque parte, chiave, canale, o elenco. Questo riafferma RB-2 (le firme
  localizzano, mai autorizzano) al confine di adozione che RB-2 rimanda a questa parte.
- **UG-2 (l'annuncio è un append a un log senza permessi, nessun appender
  privilegiato). [normativo]** Un rilascio è annunciato appendendo la sua tupla della
  Parte 10 `(triple, H_build, manifest-hash, release-index, committer-date)`
  (RB-8/RB-8a) ai log di trasparenza append-only senza permessi di RB-13 / ID-6 — la
  stessa *costruzione* del log della mappa, riusata come strumentazione (RB-2a /
  ID-11a), mai come autorità condivisa. **Chiunque PUÒ (MAY) appendere**; non c'è
  alcuna allow-list e nessun insieme di firmatari il cui append renda un rilascio
  ufficiale (ID-7). Un log che vincolasse gli append di rilascio dietro un elenco
  sarebbe l'autorità di directory che I-3 vieta ed è non conforme (ID-7, RB-2a).
- **UG-2a (nessuna firma autorevole; il default è nessuna). [normativo]** Un rilascio
  conforme non porta **alcuna firma autorevole**. Se una firma pseudonima compare del
  tutto, è un puro localizzatore RB-2 — attribuisce una build a una mano pseudonima
  continuativa per comodità di gossip — e un client DEVE (MUST) trattare un annuncio
  firmato e uno non firmato dello stesso `(triple, H_build, release-index)` come
  portatori di **peso di adozione identico** una volta che la riproduzione li
  corrobora (RB-10). Un design in cui l'accettazione di un annuncio dipende
  dall'identità di un firmatario è non conforme (RB-1, RB-12).
- **UG-2b (la linea di release non è di proprietà di alcuna parte). [normativo]**
  L'indice di RB-8a è monotono *all'interno di una linea di release*. Una linea DEVE
  (MUST) essere definita così che nessuna parte possieda il diritto di estenderla;
  altrimenti "appendi un indice più alto" diventa un'autorità per dichiarare il
  prossimo rilascio (l'autorità di directory che I-3 vieta, con indosso un numero di
  versione). UG-2c fornisce la costruzione.
- **UG-2c (l'identità della linea è una catena di manifest verificabile per
  riproduzione a partire da un genesis). [normativo]** Una linea è identificata da
  `line_id = BLAKE2s` del suo **manifest genesis** (il manifest canonico del primo
  rilascio, RB-8a). Un rilascio **estende** `line_id` se e solo se il suo manifest
  porta il manifest-hash del rilascio precedente come un campo predecessore esplicito
  **e** la sua sorgente taggata si riproduce in avanti (RB-7) da una discendenza di
  sorgente il cui tag precedente è quello del predecessore — così "estendere la linea"
  è un **atto senza permessi, controllabile per riproduzione**: chiunque possa produrre
  un manifest successore che si riproduce può appendere un indice più alto, e nessun
  repository, committer, o chiave possiede la linea. Un **fork** è qualunque manifest
  che non si concatena a `line_id`; porta necessariamente un `line_id` diverso ed è
  quindi **visibile come una linea distinta**, mai un indice più alto silenzioso
  iniettato in quella tracciata (la regola ID-2 "l'hash è l'unico nome", per la
  discendenza dei rilasci). `line_id` è stabile attraverso i rilasci onesti (l'hash
  genesis non cambia) eppure non è di proprietà di nessuno (la catena è pubblica e
  controllata per riproduzione) — le due proprietà che UG-2b richiede.

## 3. Scoperta senza un push

- **UG-3 (la scoperta è solo pull/gossip; nessun percorso di push esiste).
  [normativo]** Un client apprende che un rilascio più recente *può* esistere **solo**
  (a) facendo pull dell'indice di freschezza (RB-8a) e delle tuple di log della linea
  (RB-13) sul proprio calendario, e (b) facendo gossip di
  `(line_id, triple, H_build, release-index)` su GR-6 sotto il mescolamento delle
  sorgenti GR-8 (RB-14). Nessun meccanismo in questa parte — e nessuno che un
  deployment conforme PUÒ (MAY) aggiungere — fa push di un rilascio, una notifica, o
  un prompt a un client. Il percorso più debole di "notifica-di-disponibilità" è
  **esplicitamente non adottato**: la freschezza è ottenuta per pull e gossip, mai
  recapitata (il vincolo stringente del titolare, enunciato normativamente così che un
  implementatore non possa ri-aggiungere un push e restare conforme).
- **UG-3a (nessuna singola sorgente vincola la freschezza). [normativo]** Un client
  NON DEVE (MUST NOT) trattare il più alto release-index che ha visto come corrente
  sulla parola di un qualunque singolo peer, log, o mirror prima di applicare GR-8 /
  PS-10 "conta solo le sorgenti verificate indipendentemente" (RB-14, ID-9). La sua
  visione di *cosa sia corrente* è un'osservazione con mescolamento delle sorgenti
  sotto la stessa difesa dall'eclissi delle sue viste della mappa e del campione di
  relay.
- **UG-3b (la cadenza di scoperta è locale-al-client e delimitata dalla privacy).
  [normativo]** La cadenza di pull è una politica locale-al-client (strawman:
  opportunistica, incorporata nei batch di gossip GR-6 esistenti, mai un beacon
  distinguibile (s)). Il traffico di pull-di-freschezza NON DEVE (MUST NOT) diventare
  un'impronta digitale; cavalca il canale di gossip che il client usa già (la
  disciplina dei metadati GR-8 / Parte 6, applicata alla scoperta degli aggiornamenti).
- **UG-3c (un client fa pull sul proprio orologio, mai in reazione a un segnale di un
  peer). [normativo]** Un client PUÒ (MAY) avviare un fetch **solo** sulla propria
  cadenza delimitata dalla privacy (UG-3b) o su un'azione esplicita dell'utente. NON
  DEVE (MUST NOT) avviare un fetch *in risposta a* un segnale di divergenza, known-bad,
  o equivocazione riportato da un peer: quel trigger reattivo è il downgrade di
  re-fetch ID-9a (la Parte 8 §10 segnala "tratta la tua mappa come sospetta,
  ri-recupera" come una direzione sotto-difesa che un avversario pilota), e per gli
  aggiornamenti è un **push travestito** (UG-5a). Le anomalie sono fatte emergere e
  diffuse via gossip (UG-7), mai agite tramite fetch. Questo è il confine tra "il mio
  pull programmato ha notato un indice più alto" (consentito) e "un peer mi ha fatto
  andare a guardare" (vietato).

## 4. Decidere di adottare (opt-in manuale, nessun gate di firma)

- **UG-4 (l'adozione è un atto manuale, locale, opt-in). [normativo]** Sostituire il
  binario in esecuzione con uno più recente scoperto è una decisione che l'**utente**
  prende localmente; nessun client conforme adotta un rilascio automaticamente, su un
  timer, o al raggiungimento di una qualunque soglia di corroborazione. La soglia
  governa *cosa il client può offrire o far emergere*, mai *cosa installa*.
  "Corroborato" è una precondizione che il client controlla; "adottare" è un atto che
  l'utente compie (la postura ID-8b "rileva, non pretendere di prevenire", spostata
  dalla rilevazione all'adozione).
- **UG-4a (la checklist di adozione — nessun gate di firma). [normativo]** Prima di
  far emergere un rilascio scoperto come *adottabile*, un client DEVE (MUST) avere, per
  la propria target triple e `line_id` tracciato:
  1. **corroborazione di riproduzione** — `H_build` combacia con il manifest, tramite
     la ricostruzione propria del client (RB-7) **oppure**, per il client modale che
     non ricostruisce (RB-7b), un conteggio di riproduttori **verificati
     indipendentemente** sotto RB-10 (mai un conteggio grezzo di attestazioni);
  2. **freschezza** — un release-index ≥ al più alto che il client abbia testimoniato
     su quella linea, ordinato nel log (RB-9a, RB-8a, UG-2c);
  3. **corroborazione di log** — comparsa con root diffuse via gossip consistenti in
     un quorum configurato dei log che osserva (ID-7b, strawman ≥2 (s));
  4. **nessuna equivocazione** — nessuna anomalia di split-view UG-6 in sospeso contro
     quella linea.

  Non c'è alcun **passo di gate-di-firma**, per costruzione (UG-2a). Un client NON
  DEVE (MUST NOT) presentare alcuna di queste come "verificata" quando ha solo
  corroborazione-per-conteggio; porta lo stato `reproduced-by-others-unverified` della
  Parte 10 fino alla UI (RB-7b).
- **UG-4b (la politica di adozione è dichiarata, locale-al-client, conservativa per
  default). [normativo]** La politica che trasforma i controlli UG-4a in un'*offerta*
  è locale-al-client e DEVE (MUST) essere dichiarata all'utente (default strawman:
  offri solo un rilascio più fresco per indice, corroborato per riproduzione sopra la
  soglia del client, corroborato per log in quorum, e privo di equivocazione; non
  offrire mai attraverso un cambio di `line_id` (UG-2c) senza un passo esplicito
  dell'utente (s)). Un client PUÒ (MAY) esporre una politica più stringente (ad es.
  "offri solo ciò che ho ricostruito io stesso"); NON DEVE (MUST NOT) esporne una più
  debole di "indice più fresco + corroborato in quorum + nessuna equivocazione",
  perché più debole si riduce ad adottare sulla parola di una singola sorgente (UG-3a).
  **Un report known-bad di classe-vulnerabilità non confutato (UG-8) NON DEVE (MUST
  NOT) da solo abbassare un rilascio sotto questa soglia di offerta** (UG-8, difesa
  dalla diffamazione H).
- **UG-4c (offerta e installazione sono meccanicamente distinte). [normativo]**
  L'**OFFERTA** è il far emergere all'utente uno stato di disponibilità-e-
  corroborazione; NON DEVE (MUST NOT) recuperare il corpo dell'artefatto in risposta a
  un trigger di divergenza o known-bad (UG-3c), e qualunque pre-fetch DEVE (MUST)
  cavalcare la cadenza UG-3b così da non aggiungere alcun beacon distinguibile.
  L'**INSTALLAZIONE** è un atto avviato dall'utente che sostituisce il binario in
  esecuzione. Nessuna transizione automatica da OFFERTA a INSTALLAZIONE può esistere
  (UG-10). Un'implementazione che pre-posiziona un binario a un tap dall'esecuzione, o
  recupera su un segnale di un peer, ha costruito un push ed è non conforme anche se
  chiama il passo "offerta".

## 5. La difesa dal downgrade riproducibile, lato client

- **UG-5 (non accettare mai silenziosamente un indice inferiore; fallo emergere).
  [normativo]** Un client NON DEVE (MUST NOT) adottare, né trattare silenziosamente
  come corrente, alcun rilascio il cui indice sia **inferiore** al più alto che abbia
  testimoniato per quel `line_id` (RB-9a). Un indice presentato-inferiore è la firma a
  singola prospettiva di un **attacco di downgrade riproducibile** — un vecchio tag,
  perfettamente riproducibile, con vulnerabilità nota, alimentato al client (RB-9a) —
  e DEVE (MUST) essere fatto emergere all'utente e diffuso via gossip come anomalia di
  downgrade (UG-7d), mai consumato come un ordinario "ultimo". Poiché l'indice è legato
  alla data di commit derivata e alla catena di manifest (RB-8a, UG-2c) e ordinato nel
  log (RB-13), "indice inferiore" è una proprietà controllabile, non un giudizio.
- **UG-5a (la stantezza è fatta emergere, non agita). [normativo]** Quando l'indice in
  esecuzione proprio di un client scende sotto l'indice corrente di un quorum
  corroborato per la sua linea, DEVE (MUST) far emergere la stantezza all'utente (la
  superficie di onestà di PS-9, riusata) — *stai eseguendo un rilascio più vecchio dei
  tuoi peer corroborati; ne esiste uno più recente.* NON DEVE (MUST NOT) agire su quel
  far-emergere facendo pull, prompting-come-push, o adottando (UG-3c); informa, e
  l'utente decide (UG-4). L'asimmetria onesta con ID-9a è deliberata: il macchinario
  della mappa *ri-recupera* alla divergenza; l'adozione degli aggiornamenti **non**
  deve, perché un ri-recupero forzato sarebbe un push travestito. La stantezza si
  ferma alla superficie di onestà.

## 6. Split-view ed equivocazione sui rilasci

- **UG-6 (due "ultimi" diversi a due client sono colti dalle root diffuse via gossip).
  [normativo]** Un avversario che serve il rilascio X ad Alice e il rilascio Y a Bob —
  stessa triple, stesso `line_id` — è un attacco di split-view sulla *freschezza*,
  l'attacco ID-7a con indosso una maschera di aggiornamento. La difesa **non** è
  fidarsi dell'operatore del log; è fare gossip delle tree head firmate dei log su GR-6
  (con mescolamento delle sorgenti GR-8) e pretendere **prove di consistenza** tra due
  qualunque root che un client veda (ID-7a, RB-14). Un client che detiene entrambe le
  root ha prova crittografica che il log ha equivocato e DEVE (MUST) trattarlo come
  ostile (ID-10, UG-7b).
- **UG-6a (l'equivocazione-di-indice è la firma cross-prospettiva; disambiguata dal
  downgrade). [normativo]** Il **downgrade** (UG-5 / UG-7d) è la firma a *singola
  prospettiva*: il *mio stesso* massimo testimoniato su una linea è regredito.
  L'**equivocazione-di-indice** (UG-7b) è la firma *cross-prospettiva*: lo stesso
  `line_id` presentato con un indice più alto diverso a prospettive diverse con
  mescolamento delle sorgenti **e** le root dei log falliscono una prova di consistenza
  — due indici diversi da soli non sono equivocazione (una prospettiva può
  semplicemente essere indietro); il **fallimento della prova di consistenza** è ciò
  che lo dimostra. Un singolo evento sottostante può sollevare entrambe le firme (la
  vittima pinnata a un indice stantio vede un downgrade quando sente in seguito quello
  più alto; una parte che detiene entrambe le root vede equivocazione); DEVE (MUST)
  essere deduplicato per `(line_id, root in conflitto)` (la disciplina di dedup RB-10a,
  riusata) così che sia contato una volta. L'equivocazione-di-indice è diffusa via
  gossip così che un client parzialmente eclissato la colga da peer non eclissati.

## 7. Le anomalie di rilascio sono diffuse via gossip, non soppresse

- **UG-7 (gossip di anomalie obbligatorio). [normativo]** Cinque eventi sono anomalie
  di rilascio di cui ogni client DEVE (MUST) fare gossip al rilevamento, confrontando
  solo dati di stessa triple, stesso `line_id`, e deduplicati per RB-10a: (a) un
  `H_build` che fallisce la riproduzione dal suo manifest (RB-7a / RB-15a); (b) un log
  che presenta root inconsistenti sugli annunci di rilascio — equivocazione dimostrata
  (RB-15b, UG-6/UG-6a); (c) una divergenza persistente di `H_build` di stessa triple
  contro riproduttori indipendenti (RB-15c); (d) una **regressione del release-index**
  su una linea — la firma del downgrade (UG-5 / RB-15d); (e) un **report known-bad**
  (UG-8). Un client NON DEVE (MUST NOT) sopprimere un'anomalia per far sembrare sano un
  rilascio (ID-10, per i rilasci).

## 8. Il problema della revoca (quello difficile)

- **UG-8 (known-bad è un REPORT senza permessi, corroborato, senza forza — mai una
  revoca autorevole). [normativo]** "Il rilascio X è known-bad" non può essere
  un'affermazione autorevole: *qualunque* parte fidata di pronunciare cattivo un
  rilascio è un kill switch (può **censurare** un rilascio onesto dichiarandolo cattivo
  — l'autorità I-3 ribaltata), quindi nessuna tale parte esiste. Invece questa parte
  fornisce un **report known-bad** (segnalazione di build-cattiva): una rivendicazione
  `(line_id, triple, H_build, reason-class, evidence-locator)` che **chiunque PUÒ (MAY)
  pubblicare e chiunque PUÒ (MAY) ignorare**. I report attraversano il filo e
  alimentano un conteggio, quindi DEVONO (MUST) riusare **RB-10a alla lettera**: CBOR
  canonico, dedup per `(identità di riproduzione del segnalatore, line_id, triple,
  H_build, reason-class)`, e peso **per-riproduttore-indipendente, mai
  per-byte-di-report** — senza cui il canale è una leva di format-stuffing /
  diffamazione (diffamazione H). L'evidenza si divide in due tipi:
  - **evidenza riproducibile (il report si auto-verifica; nessuna fiducia necessaria)**
    — *non-riproduzione* (ricostruisci dal manifest e vedi RB-7a fallire),
    *regressione-di-indice / downgrade* (l'ordine del log lo mostra, UG-5),
    *equivocazione di log* (la prova di consistenza fallisce, UG-6). Per un client che
    **può ricostruire / raggiungere un riproduttore onesto**, "known-bad" qui si riduce
    a un controllo della Parte 10 che esegue esso stesso; il report semplicemente
    *localizza* il difetto, non *autorizza* il verdetto.
  - **evidenza non riproducibile (si riduce al consenso sociale)** — *"questa build che
    si riproduce contiene una vulnerabilità / backdoor."* Nessun controllo
    crittografico decide questo — è il residuo di onestà-della-sorgente della Parte 10
    §10.1 / OP-10. Qui "known-bad" è una rivendicazione pesata per la revisione pubblica
    (I-1), il conteggio di corroborazione, e la riproducibilità-dell'evidenza-dove-
    esiste (una PoC che si ricostruisce), e si riduce a **OP-2 e allo strato sociale
    del progetto**. Un **report di classe-vulnerabilità non confutato NON DEVE (MUST
    NOT) da solo vincolare un'offerta** (UG-4b): PUÒ (MAY) solo *annotare* l'offerta
    ("N parti verificate indipendentemente asseriscono una vulnerabilità; evidenza
    a …"), mai abbassare il rilascio sotto la soglia UG-4a — precisamente perché questa
    classe è votabile-da-sybil (GR-19a) e vincolare su di essa lascerebbe un avversario
    censurare un'onesta patch di sicurezza nella stantezza.

  **Il telefono modale (RB-7b) non gode delle classi riproducibili.** Un client che
  non può ricostruire non può auto-verificare un report di non-riproduzione, e un
  client eclissato non può detenere le due root di cui una prova di equivocazione di
  log ha bisogno (ID-7a §10). Per il client che non ricostruisce o è eclissato, **tutto
  tranne il controllo aritmetico di regressione-di-indice si riduce a corroborazione
  RB-10, cioè OP-2** (la riduzione della Parte 10 §10.5, ereditata — vedi §10.2). Un
  client conforme NON DEVE (MUST NOT) auto-agire su un report known-bad (ciò
  ricreerebbe il push e l'autorità in una volta); fa emergere il report con il suo
  livello di corroborazione e la sua classe di evidenza, e l'utente decide se fermarsi
  o spostarsi.
- **UG-8a (la revoca può solo informare; non può fare push, quindi non può
  forzare-la-patch). [normativo]** Poiché nessun push esiste (UG-3) e nessuna autorità
  esiste (UG-1), un report known-bad raggiunge un client solo quando quel client fa
  pull/gossip, e non cambia nulla finché l'utente non agisce. Non c'è **alcun
  meccanismo per rimuovere un binario known-bad da un client in esecuzione**, e questa
  parte non finge di averne uno. Il segnale known-bad rende un rilascio cattivo
  *rilevabile ed evitabile da un utente attento e non eclissato*; non può renderlo
  *ineseguibile* per decreto. Questo è il residuo della revoca (§10.2), enunciato, non
  lisciato.
- **UG-8b (rifiuto di esecuzione auto-verificante — refuse-to-run, privo di autorità,
  opt-in, solo auto-prova). [normativo]** Un client che **esso stesso** dimostra (RB-7,
  nessuna parte esterna) che il **proprio binario in esecuzione** fallisce la
  riproduzione contro il manifest che spedisce — o che il proprio indice incorporato è
  una regressione che può controllare aritmeticamente contro un piancito non eclissato
  — PUÒ (MAY), **come opt-in locale-al-client, non un default**, rifiutare di
  continuare a eseguire quel binario e ripiegare su un re-bootstrap (ID-8). Questo è
  **privo di autorità** (la prova è la ricostruzione propria del client, e una falsa
  prova di non-riproduzione è *impossibile* — l'avversario non può far sì che una
  sorgente pubblica onesta si riproduca a un `H` cattivo, ID-8a.3) ed **non è un push**
  (nulla è installato; il client rifiuta di eseguire codice che ha dimostrato non
  essere la riproduzione della propria sorgente dichiarata — l'analogo a runtime di
  RB-7a, che già *rifiuta* un rilascio che non si riproduce all'adozione). Il rifiuto
  di esecuzione DEVE (MUST) restare **vietato** per qualunque evidenza che il client
  non possa auto-verificare — la classe-vulnerabilità e qualunque cosa poggi su un
  conteggio di corroborazione o su un piancito di quorum (entrambi OP-2 /
  falsificabili-per-eclissi) — perché lì un *falso* piancito o report sarebbe un
  denial of service contro un client onesto. Questo protegge solo il client **che
  ricostruisce**; il telefono modale che non ricostruisce (RB-7b) si riduce ancora a
  OP-2 (§10.2), così che UG-8b restringe il divario di sicurezza della flotta (§10.1)
  senza chiuderlo.

## 9. Bootstrap: il primo aggiornamento è TOFU

- **UG-9 (il primo aggiornamento eredita il TOFU del primo-binario della Parte 10 e
  non può verificare sé stesso). [normativo]** La visione di un client su *quale
  rilascio sia corrente* è mediata dal binario che sta già eseguendo; un primo binario
  compromesso (Parte 10 §10.8) possiede l'intero apparato di scoperta, freschezza, e
  gossip del client e può quindi **mentire sulla freschezza** — pinnare l'utente a un
  indice stantio e vulnerabile, nascondere un report known-bad su sé stesso, o
  sopprimere un'equivocazione di cui è parte. Un client non può verificare onestamente
  la *propria* recenza più di quanto possa la *propria* riproduzione (Parte 10 §10.8).
  La fiducia nel primo-aggiornamento poggia sulla stessa **corroborazione indipendente
  out-of-band** del primo binario: una visione di release-index e known-bad raggiunta
  da una macchina o un canale di cui l'utente si fida più del binario sotto test.
  Questo è TOFU dichiarato (ID-8), non risolto.
- **UG-9a (la prima scelta di rilascio di un client nuovo è TOFU su canali
  indipendenti). [normativo]** Alla prima installazione un client DEVE (MUST) ottenere
  il suo `(line_id, index, H_build)` iniziale su quanti più **canali indipendenti** ha
  (Parte 10 §10.8 / ID-8: la linea di ponte out-of-band GR-10 più ≥2 mirror su reti
  distinte (s)), richiedere lo **stesso** `(line_id, index, H_build)` da tutti prima di
  accettarlo provvisoriamente, e registrarlo come **unverified-TOFU** finché non
  ricostruisce (RB-7) o accumula corroborazione consistente diffusa via gossip. DEVE
  (MUST) far emergere questo stato: *ti stai fidando del tuo primo client e della tua
  prima nozione di "ultimo"; nessuno dei due è ancora corroborato.*

## 10. Cosa questa parte non risolve (il residuo dichiarato)

Questa parte sposta la fiducia nell'adozione degli aggiornamenti da *chi l'ha
spedito* a *si riproduce ed è fresco*, e rifiuta sia un'autorità sia un push — la
scelta giusta per un progetto ogni cui elenco è un bersaglio di coercizione. **Non**
consegna una flotta rattoppata e sicura. I divari sono reali e dichiarati, non
lisciati via:

- **§10.1 — Il residuo della flotta-non-rattoppata, e il suo caso peggiore: nessun
  push significa nessuna patch forzata, e il client compromesso potrebbe
  dimostrabilmente non sentire mai parlare della correzione. [residuo primario]** Un
  client il cui utente non adotta mai manualmente — offline, disattento, o abbandonato
  — esegue il suo rilascio corrente, vulnerabilità e tutto, **indefinitamente** (UG-4).
  Nessun override esiste, perché un override è un push. Peggio, le clausole si
  compongono contro la flotta: nell'unico scenario che conta di più — un client che
  esegue un **RCE attivamente sfruttato** — il binario in esecuzione è **già controllato
  dall'attaccante**, e quello è esattamente il binario che UG-9 dice può mentire sulla
  freschezza e sopprimere il known-bad su sé stesso. Così il meccanismo che instraderebbe
  la patch (gossip + superficie di stantezza, UG-3/UG-5a) gira **dentro il processo
  compromesso** e può essere messo a tacere. La conclusione onesta: per il caso
  RCE-compromesso la superficie di onestà e il percorso di gossip forniscono **nessuna**
  garanzia di consegna; il residuo non è "patching più lento" ma **"il sottoinsieme
  compromesso potrebbe non adottare mai"**, uno stato terminale fino a un re-bootstrap
  out-of-band (ID-8), delimitato solo dall'utente che si accorge tramite qualche canale
  fuori dal client compromesso. UG-8b restringe questo per il client opt-in *che
  ricostruisce* (può rifiutare di eseguire un binario auto-dimostrato-cattivo), non per
  il telefono modale. Questo è il prezzo deliberato del rifiutare un push e un'autorità,
  ed è nominato per primo e a piena forza.
- **§10.2 — La revoca-senza-autorità è irraggiungibile per la classe-vulnerabilità, e
  si riduce a OP-2 per il client modale su più di una classe.** Non-riproduzione,
  downgrade, ed equivocazione sono revocabili senza autorità *solo per un client che
  può ricostruire o raggiungere un riproduttore onesto* (UG-8). "Questa build che si
  riproduce ha una backdoor" non è mai priva di autorità — nessun controllo decide
  l'onestà-della-sorgente (OP-10 / Parte 10 §10.1) — così che la revoca di un rilascio
  revisionato-ma-malevolo poggia sulla revisione pubblica (I-1), su una corroborazione
  la cui indipendenza è non verificabile (RB-10 / GR-19a), e sull'utente che sceglie di
  agire: OP-2 più lo strato sociale. Per il **client modale che non ricostruisce o è
  eclissato**, le classi di non-riproduzione ed equivocazione-di-log **anch'esse** si
  riducono a OP-2 (solo il controllo aritmetico di regressione-di-indice sopravvive
  all'auto-verifica) — la riduzione della Parte 10 §10.5, ereditata. Il contributo del
  design è di rendere la *rivendicazione* known-bad senza permessi, corroborata,
  disciplinata-per-dedup (RB-10a) e **senza forza** così che non sia mai un'autorità;
  non contribuisce **alcun** meccanismo che rimuova un rilascio cattivo-ma-riproducibile
  da una flotta in esecuzione.
- **§10.3 — Il client eclissato non sente mai l'aggiornamento, e il suo macchinario di
  freschezza è manipolabile.** Un client eclissato (OP-2) non tocca alcuna root
  onesta, quindi la rilevazione di equivocazione di UG-6 **non può scattare** — la
  vittima non detiene mai due root in conflitto. Sotto eclissi un avversario può pinnare
  la vittima a un **indice stantio, con vulnerabilità nota** (un downgrade silenzioso
  che UG-5 non può cogliere, perché la vittima non testimonia mai l'indice più alto),
  **sopprimere** ogni report known-bad sulla build in esecuzione, e mostrare un passato
  congelato **corroborato-da-sybil**. La freschezza è una garanzia *relativa* — più
  fresca di ciò che hai testimoniato — e un client eclissato ha testimoniato solo ciò
  che l'avversario ha permesso. Per il client eclissato che non ricostruisce, "nessuna
  autorità, solo-pull" significa "fidati del quorum con mescolamento delle sorgenti", e
  questo regge **solo fin dove regge OP-2** — la riduzione su cui le Parti 8 e 10 si
  chiudono.
- **§10.4 — L'utente che non adotta mai è bloccato per design.** L'opt-in manuale di
  UG-4 significa che un utente che respinge ogni offerta resta su una vecchia build;
  non c'è override, perché un override è un push. Il design accetta una **frazione
  stazionaria non nulla della flotta su rilasci stantii** come costo dichiarato del
  rifiutare un push, e fa emergere la stantezza (UG-5a) anziché agire su di essa.
- **§10.5 — Il TOFU del primo-aggiornamento eredita la Parte 10 §10.8 ed è
  strettamente peggiore per la freschezza.** Un primo binario compromesso può mentire
  sulla recenza con la stessa facilità con cui mente sulla riproduzione — congelando
  l'utente a un indice stantio per sempre, non rilevabilmente dall'interno (UG-9). La
  prima-nozione-di-ultimo è TOFU, corroborata solo out-of-band.
- **§10.6 — Strumenti condivisi, non autorità condivisa, devono essere ri-auditati per
  il log degli aggiornamenti.** Riusare la costruzione del log della mappa / della
  Parte 10 e il canale di gossip (RB-2a, ID-11a) è gratuito *solo* finché il ruolo di
  nessuna parte è portante sia per la mappa/codice sia per la linea di aggiornamento.
  Un deployment conforme DEVE (MUST) tenere gli appender del log della linea-di-release
  un non-elenco (UG-2) e DOVREBBE (SHOULD) usare un insieme di log indipendente da
  quello della mappa (ID-7b), così che "comodità: riusa gli stessi operatori" non
  ricrei silenziosamente il kill switch trasversale che ID-11 vieta. Il caso
  fork-contro-fuga è un ulteriore residuo: un fork rigido onesto (divergenza legittima)
  e un avversario che apre una linea parallela per sfuggire a un downgrade/known-bad
  sulla linea tracciata sono **indistinguibili a livello di protocollo** — entrambi
  sono un nuovo `line_id` (UG-2c). UG-2c rende visibile l'*esistenza* di una seconda
  linea; non decide l'*intento*, che è un giudizio sociale / OP-2, non uno
  crittografico.

Il riassunto onesto: questa parte rifiuta sia un'autorità sia un push, e in cambio è
**silenziosa** sul forzare una patch (§10.1), **non può revocare crittograficamente un
rilascio revisionato-ma-malevolo** (§10.2), **si riduce a OP-2 sotto eclissi** (§10.3),
**lascia l'utente che non adotta mai bloccato per design** (§10.4), ed è **TOFU sulla
prima nozione di "ultimo"** (§10.5). La risposta corretta è delimitarli — gossip
known-bad rumoroso, senza permessi, disciplinato-per-dedup (UG-7/UG-8), una superficie
di stantezza visibile (UG-5a), corroborazione out-of-band del primo-aggiornamento
(UG-9a), rifiuto di esecuzione opt-in auto-verificante per chi ricostruisce (UG-8b),
mescolamento aggressivo delle sorgenti (UG-3a) — e **enunciare** il compromesso di
latenza-di-patch nella UI e nella spec, non nasconderlo dietro "nessun auto-update è
più sicuro".

## 11. Requisiti introdotti qui

- **UG-1 / UG-1a** — nessuna autorità di rilascio; l'adozione si lega alla riproduzione
  e alla freschezza, mai alla pubblicazione (riafferma RB-2 al confine di adozione).
- **UG-2 / UG-2a / UG-2b / UG-2c** — annuncio per append a un log senza permessi,
  nessun firmatario; firmato e non firmato portano peso di adozione identico; la linea
  di release non è di proprietà di alcuna parte — `line_id` è una catena di manifest
  verificabile per riproduzione da un genesis, un fork è una linea visibilmente
  distinta.
- **UG-3 / UG-3a / UG-3b / UG-3c** — la scoperta è solo pull/gossip, nessun push; con
  mescolamento delle sorgenti, delimitata dalla privacy, scandita dall'orologio del
  client; mai un fetch reattivo a un segnale di un peer (quello è il downgrade di
  re-fetch ID-9a).
- **UG-4 / UG-4a / UG-4b / UG-4c** — l'adozione è opt-in manuale; una checklist a
  quattro gate senza gate di firma; una politica conservativa dichiarata; offerta e
  installazione sono meccanicamente distinte senza transizione automatica.
- **UG-5 / UG-5a** — non accettare mai silenziosamente un indice inferiore
  (downgrade riproducibile); la stantezza è fatta emergere su PS-9, non agita
  (l'asimmetria deliberata con ID-9a).
- **UG-6 / UG-6a** — split-view sulla freschezza colto dalle root diffuse via gossip +
  prove di consistenza; l'equivocazione-di-indice è la firma cross-prospettiva,
  disambiguata dal downgrade a singola prospettiva e deduplicata.
- **UG-7** — cinque anomalie di rilascio obbligatorie, diffuse via gossip, deduplicate
  per RB-10a.
- **UG-8 / UG-8a / UG-8b** — known-bad è un report senza permessi, disciplinato-per-
  RB-10a, senza forza, mai un'autorità; un report di classe-vulnerabilità annota ma
  non vincola mai un'offerta; la revoca può solo informare; il rifiuto di esecuzione
  opt-in auto-verificante è privo di autorità e permesso, il rifiuto di esecuzione su
  evidenza-esterna è vietato.
- **UG-9 / UG-9a** — il primo aggiornamento è TOFU dichiarato su canali indipendenti;
  un primo binario compromesso può mentire sulla freschezza, corroborato solo
  out-of-band.

UG-1 e UG-4 sono i due portanti: nessuna autorità, e l'adozione è un atto manuale
legato alla riproduzione. Entrambi sono delimitati, non assoluti — UG-1 si riduce a
OP-2 per il client che non ricostruisce o è eclissato (§10.2, §10.3), e il no-push di
UG-4 compra il residuo della flotta-non-rattoppata (§10.1), il cui caso peggiore — un
client compromesso che potrebbe dimostrabilmente non sentire mai la patch — è nominato
a piena forza anziché ammorbidito. Rompi questa parte nominando un percorso di push che
un client conforme PUÒ (MAY) aggiungere, un firmatario che vincola l'adozione, un modo
in cui un report known-bad forza un'azione o censura un rilascio onesto oltre UG-4b, un
modo per estendere una linea di release senza riproduzione (un proprietario della
linea), o un modo in cui il client che non ricostruisce resta a fidarsi di una
maggioranza che non è OP-2. Questo è l'invito, nella voce della Parte 8.
