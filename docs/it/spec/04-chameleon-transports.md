# Specifica ScrambNet — Parte 4: Trasporti camaleonte

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([en](../../en/spec/04-chameleon-transports.md)).

**Stato: BOZZA (DRAFT), ed è la parte più probabile da marcire.** Questa parte
enuncia un modello di minaccia del trasporto e una valutazione onesta del realismo.
Non impegna alcun meccanismo verso l'esterno e non promette alcuna vittoria nella
corsa agli armamenti della censura. Leggi prima il §1 e la valutazione del realismo
(§8): tra loro due dicono l'unica cosa ristretta che questa parte è disposta ad
affermare, e la cosa molto più grande che rifiuta di affermare. I valori strawman
sono contrassegnati con `(s)`.

Gli strati architetturali L1 (camaleonte) e L3 (trasporti effimeri) vivono qui; il
trasporto è la cosa che porta i byte di una quota oltre un censore. Questa parte è
archiviata sotto OP-7 (raggiungibilità e bootstrap), e dipende da — anziché risolvere
— il problema del bootstrap a contatto-zero (OP-7, GR-10).

## 1. La decisione, in due frasi

- **Questa parte non afferma che ScrambNet vince o sostiene la corsa agli armamenti
  della censura.** Afferma l'opposto sulla propria importanza: il pavimento di
  riservatezza e dispersione (I-2) **non** dipende affatto dallo strato di trasporto.
  Un trasporto compra *raggiungibilità* — la capacità di far arrivare i byte di una
  quota a un relay — e alla raggiungibilità è consentito fallire, giù per la scala di
  degradazione architetturale (L1→L2→L3→L4) e, a un blackout totale senza alcun
  vicino in mesh, fino a zero, **senza che il pavimento del contenuto si muova mai**
  (CT-16).
- **L'affermazione onesta e difendibile è perciò ristretta e non deve essere
  allargata:** *non rendiamo impossibile perdere la corsa del trasporto; rendiamo il
  perderla non catastrofica per la riservatezza.* Un censore può tagliare la
  raggiungibilità fino a zero; un censore ancora non può leggere il contenuto sotto
  `k` quote, perché quella protezione non ha mai cavalcato il trasporto (CT-16, CT-18,
  CT-18a).

Tutto ciò che segue è il modello di minaccia che giustifica questa affermazione
ristretta e la valutazione del realismo (§8) che ne è la spina dorsale — la sezione
più importante della parte, non un'appendice.

## 2. Il modello di minaccia del trasporto (cosa fa davvero il censore del 2026)

- **CT-1 (dichiara a cosa resisti; il silenzio è una concessione). [normativo]** Una
  descrizione di trasporto conforme DEVE (MUST) enunciare quali delle capacità
  avversarie CT-2…CT-7a afferma di resistere e quali concede. Una capacità non
  dichiarata è trattata come concessa (la regola di completezza I-1, per i trasporti)
  — un trasporto che non nomina un attacco non si è difeso da esso.
- **CT-2 (DPI passivo / fingerprinting di protocollo).** Il censore classifica i
  flussi per firme di byte e di struttura senza leggere il contenuto; il compito del
  camaleonte è di non presentare alcuna firma distintiva propria (CT-8).
- **CT-3 (confronto di impronte TLS). [normativo]** Il censore rileva l'impronta del
  ClientHello TLS. La baseline del 2026 è **JA4 / JA4+** (FoxIO), non il ritirato JA3:
  JA4 **ordina** le suite di cifratura e le estensioni prima di hashare e ignora
  GREASE, quindi è robusto rispetto alla *randomizzazione* dell'ordine delle estensioni
  che i browser mainstream ora fanno. Una mimica conforme DEVE (MUST) perciò combaciare
  con l'*insieme* di suite di cifratura, l'*insieme* di estensioni, ALPN,
  supported-versions e il *pattern* GREASE del bersaglio — non meramente il loro
  ordine, che JA4 non distingue più. (Una mimica che randomizza soltanto l'ordine non è
  per ciò nascosta.)
- **CT-4 (ispezione di SNI / ECH).** Il censore legge l'SNI in chiaro per apprendere il
  nome di destinazione. ECH può nasconderlo, ma solo condizionatamente (CT-11).
- **CT-5 (probing attivo / connect-back).** Il censore si connette a un endpoint
  sospetto e controlla se si comporta come ciò che afferma di essere; la sopravvivenza
  richiede CT-10.
- **CT-6 (classificazione statistica passiva della forma del flusso). [normativo,
  dichiara-residuo]** Il censore classifica i flussi per *statistiche*, non per byte:
  timing, volume, direzione, struttura delle raffiche, **ed entropia** — e l'insieme di
  feature è aperto e scelto dall'avversario, inclusi i classificatori appresi (ML). In
  particolare, la **rilevazione di "traffico-completamente-cifrato" ad alta entropia**
  blocca i flussi che appaiono *troppo casuali* senza alcun probe e senza alcun
  combaciare di impronte (osservato sul GFW da fine 2021). Questo ha una conseguenza
  controintuitiva da cui dipende il resto della parte: **la copertura randomizzata o ad
  alta entropia è un segnale *più luminoso*, non più fioco** — la copertura più sicura
  somiglia a un protocollo reale molto comune, mai a rumore. CT-6 non può essere chiusa
  da mimica a livello di byte (CT-8); le sue risposte oneste sono ad altri strati
  (CT-12, CT-15).
- **CT-6a (rilevazione di TLS-in-TLS / cifratura annidata). [normativo,
  dichiara-residuo]** Un trasporto che tunnelizza il traffico di quote di ScrambNet —
  già cifrato e I-4-uniforme — *dentro* un flusso TLS esterno imitato lascia pattern
  caratteristici di dimensione-record e timing — un flusso TLS che sta *portando un
  altro handshake TLS* — che il DPI può segnalare anche quando l'handshake esterno è
  perfetto byte-per-byte (pulito su CT-3/CT-4). Questo è l'attacco di punta
  all'elusione annidata e DEVE (MUST) essere dichiarato: una mimica può essere perfetta
  all'handshake ed essere comunque colta alla struttura del flusso. È un residuo che la
  mimica a livello di byte non può chiudere (appartiene a CT-12); nominarlo è richiesto
  da CT-1.
- **CT-7 (enumerazione di endpoint — bloccare ciò che è noto). [normativo]** Il censore
  scopre e blocca all'ingrosso endpoint/ponti noti. La dispersione (CT-15) e la
  distribuzione di ponti lungo il grafo sociale (architettura L2, Lox) alzano il costo;
  la mimica non affronta affatto l'enumerazione.
- **CT-7a (scoperta di endpoint — la prima linea del bootstrap, dichiarata aperta).**
  Distinta da CT-7: *come un utente censurato ottiene in primo luogo un endpoint non
  bloccato, più velocemente di quanto il censore lo enumeri.* Questo è il problema della
  distribuzione dei ponti (Lox / grafo sociale) e si riduce a **OP-7 (bootstrap a
  contatto-zero), che è aperto.** La Parte 4 non lo risolve; lo richiama in riferimento
  incrociato (GR-10, OP-7), e qualunque affermazione che gli endpoint siano
  affidabilmente scopribili è una promessa non supportata che questa parte rifiuta di
  fare.
- **CT-7b (whitelisting di protocollo — il caso limite).** Il censore permette soltanto
  una allow-list di protocolli/destinazioni e scarta il resto (osservato: la whitelist
  di rete nazionale dell'Iran, 2025–2026). Contro questo, la mimica di una destinazione
  *consentita* è la sola mossa, e persino essa fallisce quando il censore accetta il
  costo collaterale (§8, CT-14) — fino a un blackout totale, dove nessun trasporto
  raggiunge nulla (CT-18a).

## 3. Disciplina della mimica (il tapis roulant, reso normativo)

- **CT-8 (nessuna firma statica di progetto; imita come-dispiegato). [normativo]** Un
  trasporto camaleonte NON DEVE (MUST NOT) presentare una firma sul filo statica e
  specifica del progetto, e DEVE (MUST) imitare un protocollo bersaglio *come
  effettivamente dispiegato*, non uno idealizzato. Uno stack fatto a mano o congelato è
  esso stesso un'impronta ed è non conforme.
- **CT-9 (la clausola di deriva di uTLS). [normativo]** Una mimica in stile uTLS DEVE
  (MUST) seguire il ClientHello *attualmente dispiegato* del bersaglio e DEVE (MUST)
  dichiarare la versione del bersaglio che imita (CT-20). Contro JA4 (CT-3) il
  distinguitore è la divergenza negli *insiemi* di cifratura ed estensioni, in ALPN,
  supported-versions e nel pattern GREASE — questi derivano a ogni rilascio del browser,
  quindi una mimica congelata alla versione N diventa un distinguitore una volta che la
  popolazione reale passa a N+1. Questo è un **tapis roulant di manutenzione senza stato
  terminale**: non c'è alcuna versione alla quale il lavoro sia finito (§8). Il pavimento
  NON DEVE (MUST NOT) dipendere dal tenerne il passo (CT-16).
- **CT-9a (preferisci un bersaglio ad alta popolazione — per ragioni di insieme di
  anonimato, non economiche). [normativo]** Un deployment conforme DOVREBBE (SHOULD)
  imitare un bersaglio ad alta popolazione e in rapido movimento (il TLS di un browser
  mainstream) anziché uno di nicchia, per due ragioni *meccaniche*: il grande gregge è
  un migliore insieme di anonimato (più flussi reali tra cui nascondersi), e un bersaglio
  che si rattoppa in fretta accorcia la finestra di stantezza di CT-9. Questa clausola
  **non** fa alcuna affermazione economica che il gregge sia "troppo costoso da
  bloccare" — quella scommessa è CT-13, dichiarata confutabile, e il registro del 2026
  (un censore nazionale ha bloccato il più grande gregge ECH, §8) mostra che può essere
  persa.

## 4. Sopravvivenza al probe attivo

- **CT-10 (sopravvivi a un probe connect-back; il silenzio è esso stesso un'impronta).
  [normativo]** Un endpoint camaleonte DEVE (MUST) sopravvivere a un probe attivo: DEVE
  (MUST) completare un handshake *reale* e valido del protocollo che imita e servire un
  comportamento di copertura plausibile a un sondatore non autenticato (ad es.,
  terminazione TLS reale che fa da proxy verso contenuto dall'aspetto reale), rivelando
  il servizio nascosto solo a un client che dimostra un segreto pre-condiviso. Il
  modello moderno è termina-il-TLS-reale-e-fai-da-proxy-verso-un-sito-reale, **non** il
  più vecchio modello resta-in-silenzio: *restare in silenzio a un sondatore non
  autenticato è esso stesso un comportamento rilevabile* (timeout caratteristici, soglie
  di accettazione dei byte, gestione del replay) ed è non conforme.
- **CT-10a (il segreto pre-condiviso è una linea di ponte — la sua distribuzione è
  aperta). [normativo]** Il segreto che distingue un client reale da un sondatore in
  CT-10 è una **linea di ponte**, e **la sua distribuzione è OP-7 / GR-10, dichiarata
  aperta.** CT-10 presuppone un segreto già consegnato; **non** risolve la consegna. La
  resistenza al probe e il bootstrap sono problemi separati, e confonderli (presumere
  che il segreto sia in qualche modo già ovunque) è l'errore che CT-7a vieta.
- **CT-10b (il costo assottiglia il pool di operatori).** Contenuto di copertura reale,
  certificati reali e terminazione reale sono un onere operativo permanente per
  endpoint. Alzare quell'asticella è esattamente ciò che rimpicciolisce il pool di
  operatori volontari — che è il problema della manutenzione sostenuta (§8) con indosso
  un cappello operativo.

## 5. Postura ECH (nessun eccesso di rivendicazione)

- **CT-11 (ECH è opportunistico e delimitato dalla disponibilità, mai un pavimento).
  [normativo]** Una descrizione conforme NON DEVE (MUST NOT) presentare ECH (Encrypted
  Client Hello) come una difesa dell'SNI risolta. Enuncia: (a) ECH nasconde l'SNI solo
  dove il provider di fronting lo dispiega, il client lo supporta, **e la lookup DNS
  cifrata che porta la config ECH riesce** — blocca o declassa quel DNS ed ECH
  silenziosamente non entra in azione, che è l'effettiva modalità di guasto del 2026;
  (b) il dispiegamento lato server del 2026 è una fetta *minoritaria-ma-in-crescita*,
  concentrata presso pochi grandi provider di fronting, non la coda lunga, quindi "l'SNI
  è nascosto" è falso per la maggior parte delle destinazioni la maggior parte del tempo;
  (c) **"bloccare ECH del tutto" è una risposta del censore osservata** (un censore
  nazionale che blocca le connessioni ECH verso un provider importante da fine 2024),
  che ECH per costruzione non può contrastare. ECH è un miglioramento opportunistico,
  non una garanzia. *(La specifica ECH è il lavoro ESNI/ECH del working group TLS
  dell'IETF; questa parte non fissa un numero di RFC pubblicato, che non era ancora
  confermato alla stesura — cita il documento corrente, non un numero che potrebbe essere
  sbagliato.)*
- **CT-11a (degrada, non far trapelare). [normativo]** Dove ECH è non disponibile o
  bloccato, un trasporto conforme DEVE (MUST) degradare al prossimo piolo della scala
  (ponti effimeri L2) anziché ripiegare su un flusso con SNI in chiaro distinguibile. Il
  percorso di degradazione, non ECH, è la garanzia.

## 6. Il residuo di correlazione di flusso

- **CT-12 (la mimica non può sconfiggere la forma del flusso; dillo). [normativo,
  dichiara-residuo]** La mimica a livello di byte NON DEVE (MUST NOT) essere affermata
  sconfiggere la correlazione della forma del flusso (CT-6), la rilevazione di TLS
  annidato (CT-6a), o un osservatore passivo globale che correla ingresso e uscita.
  Timing, volume, direzione, struttura delle raffiche e annidamento trapelano attraverso
  una mimica perfetta. Questi sono residui che la mimica *non può* chiudere e DEVONO
  (MUST) essere dichiarati, non nascosti. Le sole risposte oneste sono ad altri strati —
  la dispersione distribuisce la forma di un messaggio tra le coperture (CT-15, una
  proprietà di *disponibilità*, non di occultamento-della-forma) e il mixing in
  modalità-paranoica (architettura L2) baratta latenza per resistenza alla forma — mai
  la mimica stessa. Gli attacchi website-oracle e di conferma lato-ingresso si riducono a
  questo stesso residuo di correlazione e alla riga dell'avversario-passivo-globale che
  il modello di minaccia già dichiara fuori dall'ambito della modalità veloce.

## 7. Dispersione delle quote attraverso coperture diverse (il verdetto normativo)

- **CT-15 (il verdetto: la diversità aiuta la disponibilità, danneggia la
  non-osservabilità; compra la prima, paga e dichiara la seconda). [normativo]**
  Portare le `n` quote di un messaggio su *tipi di copertura diversi* (una in TLS, una in
  WebRTC, una su mesh) è una decisione a due facce, risolta come segue:
  (a) NON DEVE (MUST NOT) essere presunto migliorare la **non-osservabilità** — `n`
  coperture sono `n` impronte da azzeccare (CT-3), `n` tapis roulant (CT-9), e un danno
  genuinamente nuovo: una **superficie di correlazione inter-copertura**. Un avversario
  che vede un flusso TLS, un flusso WebRTC e una raffica su mesh che sono correlati per
  timing/volume (CT-6) può collegarli come le quote di un unico messaggio *senza rompere
  alcuna singola mimica* — la diversità non attenua quel segnale, può renderlo più
  luminoso;
  (b) è consentito e valorizzato **strettamente come misura di disponibilità**: nessun
  singolo blocco di copertura uccide la consegna (`k < n` compra già questo), e
  l'enumerazione di endpoint (CT-7) deve ora riuscire contro le coperture
  *individualmente* — ciò che alza il costo del censore contro un censore che blocca le
  coperture *una alla volta*, e non fornisce **alcun** beneficio contro una whitelist di
  protocollo (CT-7b) o un blackout totale (CT-18a), che bloccano tutte le coperture in un
  unico atto.
- **CT-15a (vendila come raggiungibilità, mai come camuffamento). [normativo]** Un client
  conforme NON DEVE (MUST NOT) presentare la dispersione multi-copertura all'utente come
  *camuffamento più forte*; PUÒ (MAY) presentarla come *raggiungibilità più forte*.
  Confondere le due è lo stesso errore di categoria collegamento-contro-contenuto che
  ID-12a vieta per la mappa, riformulato per i trasporti: la multi-copertura migliora una
  proprietà di disponibilità e non migliora una proprietà di mimica.
- **CT-15b (insieme minimo di coperture lasciato aperto; affermazioni delimitate da ciò
  che è effettivamente eseguito). [normativo]** La Parte 4 **non** impone un insieme
  minimo di coperture — imporre `n` coperture impone `n` tapis roulant di manutenzione
  che il progetto potrebbe non essere in grado di presidiare (§8). Un client con un
  insieme di coperture aperto/non specificato NON DEVE (MUST NOT) affermare alcuna
  proprietà di disponibilità *quantitativa* (nessun "resiste all'enumerazione attraverso
  N coperture" senza un N enunciato ed effettivamente-eseguito); PUÒ (MAY) affermare solo
  il *qualitativo* "nessun singolo blocco di copertura uccide la consegna," e solo quando
  esegue effettivamente ≥2 coperture indipendenti con `k < n`. Se richiedere ≥2 coperture
  per il default di consegna-dispersa è una decisione del titolare (§8).

## 8. La valutazione onesta del realismo (la spina dorsale)

*(Questa sezione è la parte, non un'appendice. È scritta nella voce del §residuo delle
Parti 8 e 11.)*

**Questa parte non impegna alcun meccanismo verso l'esterno e non deve fingere di
farlo.** È un verdetto su dove il progetto è fragile, enunciato a piena forza: **lo
strato di trasporto è lo strato più debole e più probabile da marcire del progetto, e
la postura onesta è dirlo e progettare così che il pavimento non dipenda mai da esso.**

**Il tapis roulant di deriva di uTLS (CT-9).** Una mimica congelata a una versione di
browser diventa un distinguitore nel momento in cui la popolazione reale va avanti — un
gregge più piccolo e più stantio è un segnale *più luminoso*, non più fioco. Non c'è
alcuna versione alla quale il lavoro sia finito. Contro JA4 l'ordine non conta più, ma
gli *insiemi* di cifratura/estensioni derivano ancora a ogni rilascio, quindi il tapis
roulant è più lento di quanto fosse contro JA3 ma non si ferma. Il progetto non ha
modo di vincere questo; ha modo di correrci sopra o di scenderne, e CT-16 è la decisione
di rendere lo scendere sopravvivibile.

**La realtà del 2026 di ECH (CT-11).** ECH nasconde l'SNI solo dove provider, client *e
la lookup DNS cifrata* riescono tutti, e nel 2026 quella è una minoranza di
destinazioni. "Bloccare ECH del tutto" è già stato usato da un censore nazionale contro
il più grande provider di fronting, cosa che ECH non può contrastare. ECH è un
miglioramento opportunistico delimitato dal dispiegamento; il pavimento è il percorso di
degradazione, mai ECH.

**L'argomento economico e i suoi controesempi (CT-13/CT-14).** "Bloccarmi costa più di
quanto rende" è un deterrente reale e una falsa garanzia. Il registro del 2026 ha
controesempi ripetuti di censori che pagano grandi costi collaterali piuttosto che
permettere l'elusione: un regolatore nazionale che blocca ECH verso un provider
importante (da fine 2024); una **whitelist di protocollo** di rete nazionale che permette
solo una breve allow-list (Iran, 2025–2026); e **blackout totali di internet** durante
disordini (Iran, metà 2025 e di nuovo inizio 2026). Ciascuno è un censore che sceglie il
controllo rispetto al commercio. La scommessa economica è probabilistica: funziona
contro un censore che tiene al collaterale e fallisce contro uno che ha mostrato che non
lo farà. Enunciamo questo anziché agitare la mano sull'economia come se fosse risolta.
*(Questi sono citati come categorie di comportamento osservato; una stesura conforme
dovrebbe allegare date e giurisdizioni e DEVE (MUST) lasciar cadere qualunque
controesempio dietro cui non possa stare — un controesempio sbagliato è peggio di
nessuno, CT-14.)*

**La domanda scomoda, con risposta (il residuo centrale dichiarato).** *Un progetto di
volontari pseudonimi ha la capacità di manutenzione sostenuta che una corsa agli
armamenti del trasporto richiede?* Tor ha personale retribuito, un ecosistema di
pluggable-transport finanziato e anni di memoria istituzionale, e *comunque* perde round
contro censori determinati. Un progetto pseudonimo, senza elenco — uno che per design
(I-3, e la governance delle Parti 10/11) rifiuta il coordinamento centrale che
permetterebbe di fare push di un aggiornamento del trasporto a tutti in una volta — ha
**meno** di quella capacità, non di più. La risposta onesta è perciò **no, non
affidabilmente.** La corsa agli armamenti del trasporto premia esattamente la
manutenzione finanziata, coordinata e legata all'identità a cui il progetto ha rinunciato
per ragioni di principio. Dovremmo aspettarci che lo strato di mimica resti indietro.

**Ed è per questo che nulla di portante poggia su di esso.** La capacità di manutenzione
per vincere una corsa agli armamenti del trasporto è esattamente ciò che non abbiamo ed
esattamente ciò che il pavimento non richiede. Ci aspettiamo che lo strato di mimica
resti indietro; l'architettura è una scommessa che possa farlo — la stessa scommessa che
l'architettura fa già per la cintura onion ("se tutto questo strato computazionale un
giorno cade, la rete non diventa leggibile — diventa meno comoda") e che le Parti 10/11
fanno per gli aggiornamenti (rifiuta il push, paga la latenza, enuncialo). Questo è
pessimismo onesto su una capacità che ci manca, convertito nella motivazione di design
che rende lo scarto non catastrofico — non disfattismo.

**Il fondo della scala, concesso (CT-18a).** La scala di degradazione L1→L2→L3→L4 ha un
fondo, e il fondo ha un fondo. A un **blackout totale senza alcun vicino in mesh fisico a
portata**, nessun trasporto raggiunge nulla e **nessun messaggio è consegnato — punto e
basta.** Non rendiamo *quello* sopravvivibile. Il pavimento del contenuto I-2 ancora
regge (nulla è *rivelato*; ciò che non può essere inviato non può essere letto), ma la
raggiungibilità è zero, e il pavimento a quel punto è *intatto e inutile*: riservatezza
perfetta di un messaggio che non può lasciare il dispositivo. L'affermazione onesta non è
"la comunicazione arriva sempre a destinazione" — è "la riservatezza non dipende mai dal
trasporto, e quando il trasporto muore il segreto muore con esso non consegnato, non
esposto." Un nodo mesh in un blackout caldo è esso stesso un atto fisicamente
localizzabile (Parte 5, OP-6), quindi persino l'ultimo piolo è un opt-in esplicito e
pericoloso, non una garanzia.

## 9. La guardia dell'invariante

- **CT-16 (il pavimento non dipende dal vincere la corsa; riservatezza ≠ disponibilità).
  [normativo]** Nessuna garanzia di riservatezza o dispersione (I-2) DEVE (MUST)
  dipendere dal successo di alcun trasporto camaleonte, dal fatto che una mimica resti
  corrente (CT-9), dalla disponibilità di ECH (CT-11), o dalla tenuta dell'argomento
  economico (CT-14). I trasporti comprano **solo raggiungibilità**. I-2 garantisce
  **riservatezza** (il contenuto sotto `k` è illeggibile), una proprietà
  *consegnato-contro-non-consegnato* che è silente sul fatto che qualcosa sia consegnato
  — **non** una garanzia leggibile-contro-illeggibile della consegna. Il guasto del
  trasporto DEVE (MUST) degradare giù per la scala (L1→L2→L3→L4), e al fondo a
  raggiungibilità zero (CT-18a), **mai** compromettendo il contenuto sotto `k`. Un design
  in cui perdere la corsa del trasporto perde il pavimento è non conforme.
- **CT-17 (minimizza la dipendenza; non promettere di vincere). [normativo]** Una postura
  conforme DEVE (MUST) minimizzare la dipendenza del pavimento dalla mimica anziché
  promettere di sostenerla. Dove sia la mimica sia la degradazione rispondono a una
  minaccia, la parte DEVE (MUST) preferire il percorso di degradazione come la garanzia e
  trattare la mimica come la comodità (la massima stessa dell'architettura: tutto ciò che
  può scadere è una comodità).
- **CT-18 (il soffitto dichiarato: nessuna affermazione di vittoria nella corsa agli
  armamenti). [normativo]** La Parte 4 NON DEVE (MUST NOT) affermare che ScrambNet vince
  o sostiene la corsa agli armamenti della censura. L'unica affermazione che fa è quella
  di CT-16: allo strato di trasporto è *consentito perdere* senza che il pavimento perda.
  Qualunque testo, UI o README che asserisca invincibilità a livello di trasporto, una
  vittoria "sostenibile" nella corsa agli armamenti, o ECH-come-risolto è non conforme e
  DEVE (MUST) essere corretto — inclusa la riga del censore-nazionale del modello di
  minaccia, che questa parte revisiona per scindere la *raggiungibilità* (contesa, può
  arrivare a zero) dal *contenuto* (protetto incondizionatamente, indipendente dal
  trasporto).
- **CT-18a (il caso terminale è enunciato, non nascosto). [normativo]** Una stesura
  conforme DEVE (MUST) enunciare il caso terminale di CT-18 esplicitamente: a un blackout
  totale senza portata in mesh, la raggiungibilità è zero e nessun messaggio è consegnato;
  il pavimento del contenuto regge ma è inutile per quel messaggio non consegnato.
  "Rendiamo il perdere la corsa del trasporto sopravvivibile *per la riservatezza*, non
  per la consegna" è l'affermazione esatta, e nulla può essere formulato per implicare che
  la consegna sia garantita.

## 10. Superficie di onestà operativa

- **CT-19 (fai emergere la postura del trasporto onestamente). [normativo]** Un client
  conforme DEVE (MUST) far emergere la sua postura corrente del trasporto sulla superficie
  di onestà esistente (PS-9): quale copertura sta usando, se ECH è *effettivamente* in
  vigore (non meramente tentato), e che la raggiungibilità del trasporto — a differenza
  del pavimento I-2 — non porta **alcuna** garanzia e può fallire fino a zero. Il
  messaggio che la UI enuncia: *il tuo pavimento del contenuto regge; la tua capacità di
  raggiungere la rete no.*
- **CT-20 (dichiara la stantezza della mimica). [normativo]** Un deployment conforme
  DOVREBBE (SHOULD) dichiarare quanto è corrente il suo bersaglio di mimica (CT-9),
  l'analogo per il trasporto del tasso di errore misurato della mappa (ID-12), così che
  l'utente e il simulatore possano trattare una mimica obsoleta come l'impronta che è
  anziché fidarsene silenziosamente.

## 11. Un design esplorato e rifiutato: il trasporto polimorfico QUIC

Questa sezione registra un design di trasporto concreto che è stato architettato,
sottoposto a red-team e **rifiutato prima che alcun meccanismo fosse impegnato**. È
conservato, non cancellato, per la stessa ragione per cui il dataset di inferenza
conserva PS-11/PS-12 e ID-8a: un design attaccato e lasciato cadere è un risultato, e
registrare *perché* ha fallito impedisce al progetto — e al prossimo lettore — di
riproporlo. Nessuno dei `CT-n` qui sotto è normativo; il design non viene dispiegato.
I tre fallimenti sono stati verificati contro fonti primarie, non asseriti.

**Il design.** Un trasporto *polimorfico* il cui polimorfismo è una **selezione su un
piccolo insieme di template di protocollo comune reali, come effettivamente
dispiegati** (mai randomizzazione byte-per-byte — CT-6 rende già la casualità un
segnale più luminoso), con la classe di bersaglio di mimica scelta come **QUIC /
HTTP-3**: un protocollo a datagrammi ad alta popolazione, sulla premessa che
nascondersi nel gregge di QUIC eluda l'euristica dell'entropia e che una selezione di
template per-connessione derivata da un segreto di ponte pre-condiviso resista al
template-pinning. L'endpoint sarebbe un'**origin H3 reale** gestita dall'operatore,
così che un probe attivo (CT-5) incontri un sito web reale e non apprenda nulla di
nascosto (modello CT-10).

**Perché è stato rifiutato — tre fallimenti, ciascuno verificato:**

- **La motivazione dell'elusione-dell'entropia è un errore di categoria su una premessa
  falsa.** Il rilevatore di "traffico-completamente-cifrato" che affermava di eludere
  (USENIX Security 2023, Wu et al.) opera sul **primo pacchetto TCP** (un test di
  popcount bit-per-byte e regole di prefisso ASCII-stampabile); non è un rilevatore di
  QUIC, quindi un trasporto QUIC né lo elude né ha bisogno di eluderlo. E la
  sotto-premessa — "il QUIC reale è già ad alta entropia, quindi ci confondiamo" — è
  falsa per la parte che un classificatore a buon mercato legge per prima: la protezione
  dell'header di QUIC v1 maschera solo i bit bassi del primo byte e il numero di
  pacchetto (RFC 9001 §5.4), mentre la **versione** dell'header lungo (il fisso
  `0x00000001` nel 2026), i byte di lunghezza del connection-ID e la lunghezza del token
  sono **in chiaro**, e il payload del pacchetto Initial è sigillato AEAD sotto una
  chiave derivata da un salt **pubblico** e dal connection ID di destinazione in chiaro
  (RFC 9001 §5.2) — quindi qualunque osservatore può decifrare il ClientHello. Un
  Initial di QUIC è una **ricca superficie di impronta**, non un muro di byte casuali.
  La minaccia reale di QUIC è il fingerprinting dell'Initial / ClientHello (la famiglia
  JA4, inclusa la sua variante QUIC, più i parametri di trasporto), che CT-3 già
  nomina — non l'entropia.

- **Il selettore nascosto sopravvive a un pacchetto.** Derivare il template dal
  Destination Connection ID di QUIC che il client sceglie era impraticabile: RFC 9000
  §7.2 richiede che quel primo DCID del client sia **"un valore che non può essere
  predetto"** (l'opposto di una derivazione-di-chiave deterministica), lungo almeno 8
  byte, e il client lo usa **solo finché il server non risponde** — dopo il primo
  Initial del server (e immediatamente su un Retry, prima ancora che l'handshake sia
  completato), il connection ID è scelto dal server. Un selettore per-connessione che
  vive in un campo che il protocollo sovrascrive entro un round trip non è un selettore.
  (Un segreto pre-condiviso dà già a entrambe le parti l'indice del template;
  instradarlo attraverso un campo osservabile non comprava nulla e rischiava una
  divergenza dal QUIC come-effettivamente-dispiegato, che è essa stessa un'impronta
  sotto CT-8.)

- **QUIC / UDP è la *prima* cosa che un censore nazionale blocca, e a buon mercato.**
  Questo è quello decisivo, perché riguarda l'utente esatto per cui questa rete esiste.
  La Russia, il 2022-03-04, ha scartato **tutto** il QUIC internazionale con un filtro
  UDP/443 (primo pacchetto ≥ 1001 byte che porta l'header di versione di QUIC v1 → la
  4-tupla scartata per 420 s), restringendo poi a un filtraggio di QUIC-SNI, ancora
  attivo nel 2026; l'Iran, in una scansione pre-shutdown del 2025, è passato da un
  dominio QUIC bloccato a circa novemila (≈ 100 %) tramite scarti completi dell'Initial
  UDP. Poiché i browser ripiegano automaticamente su TCP, bloccare UDP/443 porta quasi
  nessun collaterale — quindi lo si fa **presto**. Scegliere QUIC baratta perciò una
  vittoria inesistente contro l'euristica dell'entropia per una perdita reale *più
  rapida* contro il blocco di UDP e il whitelisting di protocollo (CT-7b). QUIC non è
  inutilizzabile — QUIC v2 elude il filtro-solo-versione-1 della Russia, e il gregge H3
  è reale — ma è nel migliore dei casi **un template dichiarato-confutabile per ragioni
  di dimensione-del-gregge di CT-9a, dove UDP non è già scartato**, mai l'ancora. Una
  mimica TCP/HTTP-2 di una destinazione consentita sopravvive a strettamente più dei
  regimi per cui questa parte è scritta.

**Tre residui che sono sopravvissuti al design QUIC e vincolano qualunque futuro
trasporto polimorfico, QUIC o no:**

- **L'appartenenza al gregge è una proprietà dell'handshake, mai una proprietà del
  flusso — e non deve mai essere venduta come camuffamento.** "Sta' nel gregge" nasconde
  i byte dell'handshake; **non** nasconde la forma del flusso (sequenza di
  dimensioni-di-pacchetto, timing, struttura delle raffiche, volume per-messaggio di
  `n` quote), che resta ScrambNet-sagomato ed è esattamente ciò su cui CT-6 / CT-12
  classificano. Qualunque affermazione che l'appartenenza al gregge renda un flusso
  non-osservabile è l'eccesso di rivendicazione del camuffamento che CT-15a vieta, in un
  nuovo costume.

- **La risposta del probe con sito-web-reale non è solo un costo di assottigliamento del
  pool (CT-10b); è una nuova superficie di deanonimizzazione e una nuova superficie
  legale.** Il sito pubblico di un operatore e il suo canale nascosto condividono un
  indirizzo, un certificato, un endpoint, quindi la congestione da carico-nascosto
  trasforma il sito pubblico in un oracolo di timing sull'operatore (il problema
  dell'identità-non-ruotabile di BL-18a, ricorrente allo strato di trasporto), e gestire
  contenuto reale ospitato porta un'esposizione ad abuso/rimozione che la postura
  "trasporta pacchetti, non opinioni" del modello di minaccia e di OPERATORS.md non
  copre. Entrambe devono essere dichiarate da qualunque design che risponda a un probe
  con un servizio reale.

- **La selezione per-connessione su un piccolo insieme di template è essa stessa
  un'impronta a livello di popolazione.** Una scelta uniforme `1/T` su `T` template non
  combacia con la distribuzione sbilanciata per quota-di-mercato, variabile
  geograficamente e temporalmente, degli stack client reali, quindi la *distribuzione di
  selezione* — apprendibile aggregando molte connessioni — diventa la firma ScrambNet
  che il polimorfismo doveva rimuovere. Un design futuro DEVE (MUST) pesare la mescolanza
  verso la popolazione reale e comunque dichiarare il residuo che la mescolanza pesata è
  una costante globale attraverso i client, che la mimica non può chiudere.

Il risultato negativo utile è lo stesso che il modello di minaccia porta già: il vincolo
portante sulla raggiungibilità di questa rete non è il camuffamento dell'handshake ma
**la scoperta e l'enumerazione di endpoint (CT-7 / CT-7a → OP-7)**, che nessuna mimica
di trasporto affronta. Un camaleonte perfetto arriva comunque a un indirizzo che un
censore può apprendere e bloccare all'ingrosso. Quella è la prima linea del bootstrap,
dichiarata aperta.

## 12. Requisiti introdotti qui

- **CT-1 / CT-2 / CT-3 / CT-4 / CT-5** — dichiara-a-cosa-resisti; DPI passivo;
  fingerprinting TLS JA4 (insiemi + GREASE, non ordine); ispezione SNI/ECH; probing
  attivo.
- **CT-6 / CT-6a** — classificazione statistica/entropia/ML passiva del flusso (la
  casualità è un segnale più luminoso); rilevazione TLS-in-TLS annidata — entrambi residui
  che la mimica non può chiudere.
- **CT-7 / CT-7a / CT-7b** — enumerazione di endpoint contro *scoperta* di endpoint (la
  prima linea del bootstrap OP-7, dichiarata aperta); whitelisting di protocollo.
- **CT-8 / CT-9 / CT-9a** — nessuna firma statica; il tapis roulant di deriva di uTLS;
  preferisci un bersaglio ad alta popolazione per ragioni di insieme di anonimato, non una
  promessa economica.
- **CT-10 / CT-10a / CT-10b** — sopravvivi a un probe con copertura reale (il silenzio è
  un'impronta); il segreto pre-condiviso è una linea di ponte la cui distribuzione è OP-7;
  il costo assottiglia il pool di operatori.
- **CT-11 / CT-11a** — ECH è opportunistico, dipendente dal DNS, con blocco-ECH-osservato,
  non un pavimento; degrada anziché far trapelare SNI in chiaro.
- **CT-12** — la mimica non può sconfiggere la forma-del-flusso/annidamento/correlazione;
  le risposte sono ad altri strati, mai la mimica.
- **CT-15 / CT-15a / CT-15b** — la dispersione multi-copertura aiuta la disponibilità,
  danneggia la non-osservabilità, aggiunge una superficie di correlazione inter-copertura;
  vendila come raggiungibilità non camuffamento; affermazioni delimitate dalle coperture
  effettivamente eseguite.
- **CT-16 / CT-17 / CT-18 / CT-18a** — il pavimento non dipende mai dal trasporto;
  riservatezza ≠ disponibilità; nessuna affermazione di vittoria nella corsa agli
  armamenti; il caso terminale di raggiungibilità-zero enunciato, non nascosto.
- **CT-19 / CT-20** — postura del trasporto onesta su PS-9; stantezza della mimica
  dichiarata.

CT-16 e CT-18 sono i due portanti: il pavimento non dipende dal vincere la corsa del
trasporto, e la parte non fa alcuna affermazione che la corsa sia vinta. Lo strato di
trasporto è quello su cui il progetto si aspetta di perdere round, ed è architettato così
che il perderli costi *raggiungibilità*, mai *riservatezza* — giù fino al caso terminale
dove la raggiungibilità è zero e il segreto non consegnato è ancora un segreto (CT-18a).
Rompi questa parte nominando una capacità del censore che CT-2…CT-7b manca, una clausola
che promette di vincere o sostenere la corsa agli armamenti oltre CT-18, un punto in cui
il pavimento I-2 è fatto dipendere dal successo di un trasporto, o un modo in cui la
dispersione multi-copertura è venduta come camuffamento oltre CT-15a. Questo è l'invito,
nella voce della casa.
