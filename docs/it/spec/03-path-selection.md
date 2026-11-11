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

## 6. Cosa questa parte non decide

La distribuzione senza fiducia dell'insieme di dati per la disgiunzione, e la
verifica formale che un insieme scelto sia disgiunto quanto dichiarato (OP-1);
le soglie oneste di dimensione viabile e se `n = 2, k = 2` valga affatto la pena
di essere eseguito (OP-3); l'economia della rotazione delle guardie; la
selezione dei percorsi sulla mesh di blackout, dove AS e giurisdizione non
significano nulla (OP-6). `poc/network_sim.py` è il valore provvisorio
eseguibile dietro questa parte — attacca il suo modello, poi questo testo.
