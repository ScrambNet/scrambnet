# ScrambNet — Roadmap

**Stato: documento vivente.** Questo è il piano di lavoro, non una promessa di
date — un progetto di volontari pseudonimi procede quando ci sono mani libere. È
ordinato per dipendenza e per onestà: gli elementi che potrebbero dimostrare il
progetto *sbagliato* vengono per primi, perché se l'affermazione portante non
regge, nulla a valle conta. Ogni elemento dichiara come appare il «fatto», così
che il progresso sia verificabile, non asserito.

È stato costruito a partire da tre revisioni parallele — progetto di rete,
crittografia e sicurezza/operatività — e i risultati più ostici sono tenuti in
piena vista invece di essere smussati. Gli elementi fanno riferimento alle parti
della specifica (`SP-n`, `GR-n`, `PS-n`, `RZ-n`), agli invarianti (`I-1…I-4`) e
ai problemi aperti (`OP-1…OP-9`).

Scala di impegno: **S** ≈ giorni · **M** ≈ 1–2 settimane · **L** ≈ settimane,
rischio di progetto reale · **XL** ≈ un sotto-progetto di ricerca che può
restituire un risultato parziale o negativo. Gli ultimi due non sono fallimenti
da evitare; sono la forma onesta dei problemi irrisolti.

---

## Livello 0 — Correggere ciò che già sappiamo essere sbagliato (ora)

Questi sono emersi dalle revisioni come difetti concreti o affermazioni
eccessive. Sono poco costosi e proteggono la credibilità del progetto, che è il
suo unico vero patrimonio a questo stadio.

- **0.1 — Riconciliare le affermazioni pubbliche con l'ambito dimostrato.** `[critico per l'affermazione]`
  Il livello minimo del contenuto è informazionale **solo al di sotto di `k`
  quote**; al di sopra di `k`, la segretezza del contenuto è computazionale
  (l'AEAD). E «raccogli ora, decifra dopo» è sconfitto **solo** per l'avversario
  sotto-`k` — un avversario `≥k`, che registra tutto, con un computer quantistico
  futuro, rompe comunque il contenuto *a meno che l'accordo di chiave end-to-end
  non sia esso stesso post-quantistico o precondiviso*. README, COMPARISON e il
  modello di minaccia devono dichiarare il regime (sotto-`k` vs sopra-`k`) e
  l'ipotesi (segretezza della chiave AEAD) in ogni frase sul livello minimo.
  **Fatto:** nessuna «protezione informazionale del contenuto» non qualificata
  resta in alcun documento pubblico. **Impegno S.**

- **0.2 — Specificare e dimostrare lo strato AEAD end-to-end.** `[critico per l'affermazione]`
  SP-1 («cifra prima della dispersione») è l'intera affermazione di composizione,
  ma la PoC scompone il *testo in chiaro* — non c'è alcun AEAD da nessuna parte,
  quindi la composizione è asserita, mai mostrata. Specifica lo strato e2e
  (stabilimento della chiave dal `kpair` del contact card vs uno scambio
  effimero — una scelta che decide la storia post-quantistica) ed estendi la PoC
  per cifrare → scomporre → ricostruire → decifrare davvero. **Fatto:** la PoC
  dimostra SP-1 da capo a fondo; la scelta sullo stabilimento della chiave è
  fatta e la sua conseguenza PQ è registrata. **Impegno M.**

- **0.3 — Integrità delle quote sotto un drop malevolo.** `[solidità]`
  Il tag SP-7 dice *a quale* messaggio un pacchetto dichiara di appartenere, ma
  nulla autentica i byte della quota o il byte `k,n`. Un singolo drop o un'uscita
  ostile può ribaltare bit in una quota; Shamir non può rilevarlo, quindi `k`
  quote corrotte-consistenti si ricostruiscono in spazzatura (l'AEAD sopra lo
  coglie — fail-closed — ma questo è un *denial of service mirato* a basso costo
  su un box). Decidere: binding esplicito per quota, oppure un residuo
  fail-closed-con-ritentativo accettato e documentato. **Fatto:** un verdetto con
  la costruzione se necessaria, scritto in SP-7. **Impegno M.**

- **0.4 — Pubblicare la chiave PGP del progetto.** `[opsec, lacuna immediata]`
  SECURITY.md *promette* una chiave che non esiste. La prima ondata di revisori
  (le mailing list) non ha alcun canale confidenziale. Genera una chiave vincolata
  allo pseudonimo per `scrambnet@proton.me`, commetti la sua impronta, sostituisci
  il vago «tempo ragionevole» con una finestra di divulgazione reale, e dichiara
  come la chiave stessa ruota (anche la chiave di divulgazione non deve essere un
  singolo esemplare insostituibile, I-3). **Fatto:** una segnalazione sensibile
  può essere cifrata verso una chiave reale e pubblicata oggi. **Impegno S.**

*(Il bug del parser sull'ordine dei nibble di 0.1 e la lacuna di polling al
confine dell'epoca UTC trovati in revisione sono già annotati per i vettori di
test in 3.2 e per l'elemento KDF in 2.2.)*

---

## Livello 1 — Dimostrare o rompere l'affermazione portante (spina dorsale crittografica)

L'intero fattore di differenziazione del progetto è I-2. Questi quattro elementi,
in sequenza, o lo stabiliscono rigorosamente o rivelano dove è sopravvalutato.
Nient'altro vale la pena di essere costruito finché questa spina dorsale non
regge.

- **1.1 — Formalizzare la composizione encrypt-then-Shamir.** `[critico per l'affermazione]`
  Un teorema scritto (o un controesempio) che enuncia *esattamente* cosa è
  incondizionato (il testo cifrato è nascosto al di sotto di `k`, senza alcuna
  ipotesi computazionale) e cosa no (il testo in chiaro al di sopra di `k` poggia
  sull'AEAD). Confermare che la chiave AEAD non compare mai in nulla che un
  avversario sotto-`k` veda. **Fatto:** una frase precisa per ciascun livello,
  l'incondizionato e il computazionale, dimostrabilmente disgiunti. **Impegno M.**

- **1.2 — Dimostrare il livello minimo sull'intero segreto, non su un byte.** `[critico per l'affermazione]`
  La demo a forza bruta della PoC copre un *singolo byte*; i test di proprietà
  controllano solo una marginale. Dimostrare l'indipendenza congiunta di `k−1`
  quote qualsiasi sull'intero segreto (standard, dati coefficienti per posizione
  indipendenti e uniformi), e aggiungere un test che fallirebbe sotto riuso dei
  coefficienti o un RNG a bassa entropia. Documentare **«la casualità dei
  coefficienti è critica per il livello minimo»** come requisito di prima classe.
  **Fatto:** prova di indipendenza congiunta citata + un test che coglie il
  fallimento dell'RNG. **Impegno S–M.**

- **1.3 — Tag SP-7: replay, falsificazione, collegabilità cross-drop.** `[solidità]`
  La proprietà che non deve fallire: due quote di uno stesso messaggio non devono
  mai portare un valore osservabile uguale attraverso drop in collusione. Le quote
  verso drop distinti usano indici distinti, quindi i tag differiscono — *dimostra*
  che nessuna coppia `(nonce, index)` è mai riusata tra i drop, o correggilo. In
  più: regole di proprietà del nonce (un `msg_nonce` riusato sia collide i tag sia
  rompe l'AEAD in modo catastrofico), e difese replay/eviction a livello di
  storage. **Fatto:** schizzo di prova del no-tag-uguale, disciplina del nonce
  scritta in SP-7, replay gestito al drop. **Impegno M–L.**

- **1.4 — Unificare la disciplina di derivazione delle chiavi di rendezvous.** `[solidità]`
  Oggi `K_tag` viene da HKDF-BLAKE2s ma `box_id` da BLAKE2s grezzo con chiave,
  entrambi sullo stesso `kpair` — senza principio. Derivare un unico master PRK
  dal `kpair`, poi sotto-chiavi separate per etichetta. Specificare la **regola di
  grazia al confine dell'epoca UTC** (un mittente che deposita alle 23:59 e un
  destinatario che fa polling alle 00:01 non devono perdere la posta — un vero bug
  di consegna). Giustificare l'ampiezza di 16 byte del `box_id`. **Fatto:** una
  sola disciplina KDF, la regola di grazia dell'epoca, vettori rigenerati.
  **Impegno M.**

---

## Livello 2 — Il problema centrale di rete (OP-1) e il suo apparato

Il livello minimo è reale solo *operativamente* se gli `n` percorsi sono
genuinamente disgiunti. Verificarlo dai dati del client stesso — contro relay che
mentono su tutto tranne che sulle proprie firme — è il problema centrale
dichiarato del progetto. Il punto onesto più profondo, che i deliverable devono
dichiarare ad alta voce: **dall'overlay non puoi verificare la *vera*
disgiunzione, solo la consistenza contro un insieme di dati a fiducia limitata;
un avversario che co-localizza i relay pur annunciando prefissi disgiunti è
probabilmente non rilevabile.** Il compito è limitare ciò che quell'avversario
guadagna, non far finta che non esista.

- **2.1 — Passata di realismo del simulatore.** `[pietra angolare]`
  Oggi `network_sim.py` usa etichette AS di *verità di base* — cioè assume che il
  problema della verifica sia già risolto. Aggiungere: uno **strato di inferenza
  AS/giurisdizione con errore iniettabile** (così che «ignoto ⇒ assumi condiviso»
  venga esercitato), **guardie persistenti** attraverso un flusso di messaggi (una
  guardia cattiva è cattiva per mesi), un **campione di gossip parziale** per
  client invece del pool a occhio divino, e un **avversario potenziato**
  (correlazione a livello AS, il drop contato come punto d'osservazione in uscita,
  conferma opzionale del salto intermedio). **Fatto:** curve di rottura e di
  collegamento in funzione del tasso di errore dell'inferenza, che mostrano come i
  numeri di oggi a errore zero fossero ottimistici. **Impegno L.** Sblocca quasi
  tutto il resto a valle.

- **2.2 — Redigere la procedura di verifica della Parte 3.** `[fiore all'occhiello]`
  L'espansione che la issue OP-1 chiede: dato un campione, un insieme di dati di
  inferenza e una confidenza per relay, produrre `n` circuiti **e un certificato
  verificabile automaticamente del livello di disgiunzione raggiunto, con una
  confidenza** — mai un'assunzione. Dichiarare il limite onestamente («disgiunti
  sotto l'insieme di dati D con le barre d'errore di D»), e nominare l'avversario
  che gioca sulla co-localizzazione come residuo dichiarato, quantificato da 2.1.
  **Fatto:** un implementatore ostile può costruire il selettore dal testo; ogni
  soglia cita una figura del simulatore. **Impegno L.** Dipende da 2.1 e 2.3.

- **2.3 — L'insieme di dati IP-verso-AS senza fiducia.** `[rischio di ricerca]` `I-3`
  Come distribuire e autenticare una mappa IP-verso-AS (e di giurisdizione
  grossolana) senza alcuna autorità singola: snapshot riproducibili da dati
  pubblici BGP/RIR, un modo perché due client capiscano di detenere la *stessa*
  mappa (content-addressing + transparency log + root scambiate via gossip), e un
  trattamento onesto del paradosso del bootstrap (un client nuovo recupera la
  mappa su percorsi che non può ancora valutare — un momento di trust-on-first-use).
  **Giunzione di fusione:** l'insieme dei firmatari della mappa e l'insieme dei
  firmatari del rilascio del software (OP-8, elemento 4.1) potrebbero voler essere
  lo *stesso* meccanismo. **Fatto:** due client onesti detengono dimostrabilmente
  la stessa mappa o rilevano che non è così; il tasso di errore della mappa
  alimenta la manopola dell'inferenza di 2.1. **Impegno XL** — l'esito onesto
  potrebbe essere «mappa TOFU + transparency log + gossip di anomalie», non una
  mappa canonica.

- **2.4 — Robustezza della scoperta: sybil ed eclissi (OP-2).**
  Modellare la vista campionata sotto GR-6/GR-8 con frazioni d'avversario per
  classe di fonte, churn, e il tetto «nessuna classe > ½»; implementare avversari
  di eclissi e sybil; verificare se il «conta solo i relay verificati» di PS-10
  smussi davvero il gonfiaggio della dimensione via sybil. Poi specificare il
  protocollo di sondaggio della banda (GR-7) — una sonda che misura un relay senza
  rivelare il sondatore né diventare un amplificatore di DoS, la difficile
  sostituzione della bandwidth authority di Tor che ci siamo negati. **Fatto:**
  curve di probabilità d'eclissi e di gonfiaggio sybil; una specifica di sonda
  costruibile. **Impegno L.**

---

## Livello 3 — Irrobustire le costruzioni per un'implementazione reale

- **3.1 — Requisiti crittografici dell'implementazione di riferimento.** `[solidità]`
  Ciò che un nodo reale deve fare e che il giocattolo omette, ciascuno legato a
  una minaccia: **GF(2⁸) a tempo costante** (le lookup su tabella della PoC sono un
  canale di cache-timing sui byte segreti delle quote — un leak di temporizzazione
  minerebbe proprio il livello minimo che il progetto vende), **disciplina CSPRNG**
  (il livello minimo è forte esattamente quanto l'RNG dei coefficienti), gestione
  della rotazione di nonce/chiavi attraverso i riavvii, persistenza della
  replay-cache, resistenza all'abuso (l'API deve rifiutare il testo-in-chiaro-
  senza-AEAD — cosa che la PoC stessa fa già), e azzeramento della memoria.
  **Fatto:** una checklist legata alle minacce che un implementatore deve
  soddisfare. **Impegno L.**

- **3.2 — Vettori di test formali e conformità tra implementazioni.** `I-1`
  Espandere `vectors.json` per coprire ogni costruzione con chiave (HKDF PRK, box
  id attraverso le epoche, il percorso end-to-end
  cifra→scomponi→deposita→polla→ricostruisci→decifra, record Ed25519 + CBOR
  canonico, la trascrizione dell'handshake Noise una volta specificata), fissare le
  tabelle GF come normative, e **vincolare a vettore l'ordine dei nibble di `k,n`**
  (i due parser della PoC non concordavano — ora corretto; un vettore deve tenerli
  onesti). **Fatto:** una seconda implementazione in un altro linguaggio supera
  ogni vettore. **Impegno M.** Incrementale: aggiungi vettori man mano che ogni
  costruzione si assesta.

- **3.3 — Specificare l'handshake del circuito (Noise XK) e la sua forward secrecy.**
  La suite nomina `Noise_XK_25519_ChaChaPoly_BLAKE2s` ma nulla la specifica, e
  Sphinx fa già l'accordo di chiave per salto — quindi **a cosa serve Noise XK?**
  Risolvere l'apparente ridondanza (un implementatore ostile non può attualmente
  costruire un nodo interoperabile, violando I-1), dichiarare le proprietà di
  forward secrecy e la finestra di esposizione della chiave statica ≤7 giorni, e
  decidere se l'occultamento dell'iniziatore di XK sia addirittura necessario o se
  basti un pattern più semplice. **Fatto:** l'handshake è specificato alla
  completezza di I-1, la sua relazione con Sphinx è non ambigua. **Impegno L.**

- **3.4 — Firme dei record di gossip e CBOR canonico.** `I-1`
  Il CBOR canonico è critico per la firma: due implementazioni che non concordano
  sull'ordinamento della mappa rifiutano i record validi l'una dell'altra. Fissare
  la canonicalizzazione esatta, imporre un profilo di verifica Ed25519 rigoroso, e
  fornire vettori tra implementazioni. **Fatto:** canonicalizzazione fissata,
  vettori esistenti. **Impegno S.** Parallelizzabile.

---

## Livello 4 — Governance e operatività (protegge il progetto ora e gli utenti dopo)

Le revisioni concordavano su un'inquadratura: il progetto **non ha ancora
utenti**, il che è un dono — lo scheletro di governance e di fiducia nella build
può essere posato con calma *ora*, mentre cambiarlo non rompe nessuno. L'errore
costoso è spedire un nodo di riferimento con una storia di aggiornamento
improvvisata e poi avere bisogno di una migrazione a forma di autorità per
correggerla.

- **4.1 — Governance degli aggiornamenti senza kill switch (OP-8).** `[l'elemento non crittografico più importante]`
  Un record di decisione di progetto che fissa la *forma*: le build riproducibili
  sono l'àncora di fiducia; le firme solo *localizzano* una build; l'adozione
  dell'aggiornamento è locale al client e opt-in, mai una spinta. L'80% difficile è
  umano, non crittografico — *chi* firma, come viene scelto e sostituito in modo
  pseudonimo, e come un quorum eviti di diventare silenziosamente la directory
  authority che I-3 vieta. **La risposta più forte potrebbe essere minimalista:**
  build riproducibili + hash pubblicati in modo incrociato + *nessun*
  auto-aggiornamento e *nessun* insieme di firmatari autoritativo, perché ogni
  insieme di firmatari è un bersaglio di coercizione. **Fatto:** il documento
  sopravvive a una lettura ostile a caccia dell'autorità-backdoor; l'auto-audit
  I-3 nomina il sostituto non fidato per ogni parte. **Impegno L.**

- **4.2 — Pipeline di build riproducibili e catena di fornitura.** `I-1, I-3`
  Progettare (pronto per quando il nodo Rust parte): pinning del toolchain, una
  build ermetica o in stile Nix, un `rebuild-and-compare` che uno sconosciuto possa
  eseguire, attestazioni pubblicate in modo incrociato, un albero delle dipendenze
  minimo e vendorizzato, e la riconciliazione esplicita di «i contributori devono
  essere pseudonimi (nessuna chiave di firma vincolata all'identità)» con «verifica
  l'artefatto» — tutta la fiducia passa per la riproducibilità, nessuna per
  l'identità dell'autore. **Fatto:** due parti su macchine diverse producono
  artefatti identici per hash dalla sorgente taggata, tramite una procedura che non
  nomina alcun singolo esemplare fidato. **Impegno L.**

- **4.3 — Economia dei dead-drop e metadati di recupero (OP-9).**
  Simulare un attacco di flooding con un cartellino del prezzo (puzzle del client
  vs i tetti RZ-7), onesti riguardo alla lacuna per cui un puzzle abbastanza duro
  da scoraggiare una botnet può essere inaccessibile sul telefono economico che il
  progetto dichiara di servire. Simulare la disciplina di polling (RZ-9) contro un
  drop che *profila* un box, e il suo costo sul mobile a consumo. **Fatto:**
  parametri difesi con il residuo dichiarato in numeri. **Impegno M.**

- **4.4 — Esposizione dell'operatore e la postura di neutralità.** `[politicamente spinoso]`
  Un brief onesto (non consulenza legale) su cosa rivela e rischia il far girare
  ciascun ruolo, appoggiato sull'affermazione vera che un drop immagazzina rumore
  illeggibile e un relay inoltra rumore a dimensione fissa senza alcuna uscita sul
  web in chiaro; più una postura scritta di gestione dell'abuso — cosa il progetto
  farà e non farà quando la rete è usata per nuocere, dato che per progetto *non
  può* leggere o prendere di mira il contenuto, e perché quell'incapacità è una
  proprietà di sicurezza, non un'evasione. **Fatto:** ogni ruolo ha una
  dichiarazione di esposizione in linguaggio semplice; la postura è coerente con la
  clausola di neutralità e non introduce alcuna leva di moderazione. **Impegno M.**

---

## Livello 5 — Gli strati ancora da scrivere

- **5.1 — Trasporti camaleonte (Parte 4, OP-7).** `[corsa agli armamenti]`
  Un modello di minaccia del trasporto e una valutazione onesta del realismo:
  deriva dell'impronta uTLS, la realtà del dispiegamento di ECH nel 2026, il
  sondaggio attivo, la correlazione di flusso. L'argomento economico «bloccarmi
  costa più di quanto renda» ha veri controesempi storici — nominali, e porre la
  domanda scomoda se un progetto di volontari pseudonimi abbia la capacità di
  *manutenzione sostenuta* che una corsa agli armamenti esige. Risolvere se la
  dispersione delle quote tra coperture diverse *aiuti* (più tipi di copertura) o
  *danneggi* (più impronte da sbagliare). **Impegno L.**

- **5.2 — Diversità di collegamento blackout / mesh mista (Parte 5, OP-6).** `[rischio di ricerca]`
  Il più grande progetto ancora da scrivere: telefoni come foglie vincolate alla
  batteria, PC/SBC a doppia radio come dorsale 802.11s, e **dispersione tra
  gateway indipendenti** che estende I-3 all'uscita fisica del vicinato. Le parti
  difficili: indirizzamento senza raggiungibilità globale; verificare
  l'indipendenza dei gateway quando la mappa AS è irraggiungibile dentro un
  blackout e la posizione è autodichiarata (OP-1 ricorre nello spazio radio); se il
  pacchetto Sphinx da 2048 byte sopravviva a uno store-and-forward di ore o
  necessiti del proprio framing. E il residuo irriducibile da dichiarare, non
  risolvere: **un nodo mesh in un blackout caldo è un atto fisicamente
  localizzabile** che nessun overlay può nascondere — quindi la partecipazione alla
  mesh è sempre un opt-in esplicito. **Impegno XL.**

---

## Lo stesso problema con tre maschere

Un risultato ricorreva in tutte e tre le revisioni e merita di essere nominato:
l'incapacità di **verificare l'indipendenza di una parte senza autodichiarazione**
compare per i *relay* (disgiunzione dei percorsi OP-1), per i *firmatari dei
rilasci* (diversità giurisdizionale OP-8), e per i *gateway mesh* (indipendenza
fisica OP-6). Una soluzione a uno potrebbe trasferirsi agli altri. È,
plausibilmente, il problema aperto più profondo dell'intero progetto — e la
risposta onesta in ciascun caso potrebbe essere un *residuo limitato e dichiarato*
piuttosto che una verifica. Questo è coerente con la regola che sta sopra tutte le
altre qui: **dichiara dove finisce l'ombrello.**

---

## Percorso critico suggerito

**Ora:** Livello 0 (0.1–0.4) — correggi le affermazioni eccessive note e la
chiave mancante.
**Poi la spina dorsale:** 1.1 → 1.2 → 1.3 → 1.4 (dimostra o rompi I-2), con 0.2
(l'AEAD e2e) incluso dentro poiché sblocca la demo di composizione reale.
**Poi in parallelo:** 2.1 (pietra angolare del simulatore) e 2.3 (l'insieme di
dati XL, iniziato presto) → 2.2 (verifica fiore all'occhiello della Parte 3); 4.1
(governance) e 4.2 (build riproducibili) possono procedere indipendentemente in
qualsiasi momento.
**Chiusura:** 2.4, irrobustimento del Livello 3, economia del Livello 4, poi i
Livelli 5.1 e 5.2 ancora da scrivere.

Due elementi portano una reale possibilità di un risultato *parziale o negativo* —
2.3 (dati BGP riproducibili senza fiducia potrebbero non essere pienamente
raggiungibili) e 5.2 (una mesh che preservi gli invarianti potrebbe essere solo
parzialmente raggiungibile). Questa non è una ragione per rinviarli; è la ragione
per essere onesti su di essi in un documento che non promette atti di fede.
