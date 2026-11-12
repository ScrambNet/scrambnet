# Specifica ScrambNet — Parte 10: Build riproducibile e supply chain

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([en](../../en/spec/10-reproducible-build.md)).

**Stato: BOZZA (DRAFT).** Questa parte decide come una parte ottiene un **binario**
ScrambNet di cui possa fidarsi *senza fidarsi di chi l'ha costruito*, sotto I-3 —
nessuna autorità — contro un progetto i cui contributori sono **pseudonimi** e
quindi non portano alcuna identità che un utente possa verificare. È l'analogo
software della Parte 8: lì, una *mappa* è fidata perché si ricostruisce da input
pubblici; qui, un *binario* è fidato perché si ricostruisce da sorgente pubblica. I
valori strawman sono contrassegnati con `(s)`.

La Parte 9 dice *cosa deve fare il codice del nodo*; questa parte dice *come quel
codice diventa un binario che puoi verificare di star eseguendo*. Leggi prima il §1
e il §10: insieme dicono cosa compra questa parte (la riproduzione, non la firma,
come arbitro) e cosa ammette di non poter comprare (una backdoor in una sorgente
fedelmente riprodotta; un compilatore che miscompila in modo riproducibile; e, per
l'utente che non può ricostruire, una riduzione a OP-2 — la stessa riduzione su cui
si chiude la Parte 8).

Questa parte decide la riproducibilità come **ancora** di fiducia. **Non** decide
*chi firma un rilascio o come i firmatari vengono scelti e sostituiti* — quello è
l'item 4.1 (OP-8), una parte separata. La giunzione tra loro è il §9, e rispecchia
per citazione gli ID-11/ID-11a della Parte 8.

## 1. La decisione, in due frasi

- **Non esiste un'autorità di rilascio.** Un binario ScrambNet è un **artefatto
  riproducibile e indirizzato per contenuto** che qualunque parte ricostruisce
  byte-per-byte da sorgente pubblica taggata e da input pubblici pinnati; due parti
  concordano che un binario è onesto non perché una parte fidata l'ha firmato ma
  perché hanno calcolato lo **stesso `BLAKE2s`** (RB-1, RB-9). Un binario benedetto
  da un insieme fisso di firmatari sarebbe un'autorità di rilascio sotto un altro
  nome, e I-3 lo vieta.
- **L'accordo avviene per riproduzione; le firme solo *localizzano* una build, non
  l'*autorizzano* mai; la fiducia in una build che l'utente stesso non può
  riprodurre si riduce alla corroborazione-per-conteggio, che è OP-2.** Questa è la
  forma onesta ed è enunciata in testa, non sepolta: per la parte con una macchina
  di build, la riproduzione porta tutta la fiducia; per il telefono che non può
  ricostruire — l'utente modale — la fiducia poggia su un conteggio di riproduttori
  indipendenti, esattamente come il client della Parte 8 che non ricostruisce poggia
  su un quorum diffuso via gossip (RB-7b, §10).

Quindi l'esito onesto è lo stesso che la Parte 8 ha raggiunto per la mappa:
**riproducilo tu stesso e la fiducia è priva di autorità; non puoi riprodurlo, e sei
di nuovo a un quorum di corroborazione soggetto a OP-2.** Tutto ciò che segue rende
concreto "riproducilo tu stesso, e rileva chiunque abbia mentito", e il §10 è il
residuo che nessuna quantità di costruzione rimuove.

## 2. Ambito e la trappola che questa parte evita

Un progetto pseudonimo non può chiedere all'utente di fidarsi dei suoi autori — non
c'è alcun autore di cui fidarsi. Il design "senza fiducia" ingenuo è un binario
firmato dai manutentori del progetto; questo reimporta precisamente l'autorità che
I-3 nega. La trappola: un firmatario che può distribuire di nascosto un binario
malevolo sotto una chiave fidata è il kill switch che l'item 4.1 esiste per evitare.
Quindi la fiducia non deve fluire attraverso *chi ha firmato*; fluisce attraverso
*si ricostruisce?*.

- **RB-1 (nessuna autorità di rilascio; la riproduzione è l'arbitro). [normativo]**
  Nessun passo dell'ottenere o validare una build DEVE (MUST) richiedere di fidarsi
  che una particolare parte l'abbia compilata, firmata o benedetta. Le uniche
  operazioni fidate sono (a) ricalcolare `BLAKE2s`, e (b) ricostruire l'artefatto da
  sorgente taggata e input pinnati e confrontare. Qualunque elemento di design che
  non possa essere sostituito da un surrogato non fidato che esegue (a) o (b) è un
  difetto sotto I-3 e DEVE (MUST) essere rimosso o dichiarato nel §10. (L'operazione
  (b), ricostruisci-e-confronta, è fidata **modulo** il residuo della toolchain:
  eseguire la build esegue il compilatore pinnato, che RB-3b dichiara un residuo di
  "trusting-trust" — la ricostruzione riduce la fiducia al compilatore, non la
  elimina. RB-1 è l'affermazione delle due operazioni, letta con quel riferimento
  incrociato, non senza di esso.)
- **RB-2 (la riproducibilità autorizza; le firme solo localizzano). [normativo]**
  Questa parte non decide nulla su *chi firma un rilascio o come i firmatari vengono
  scelti e sostituiti* — quello è l'item 4.1. Una firma su una build, se ne esiste
  una, DEVE (MUST) essere trattata come un **localizzatore** ("una build con questo
  `H_build` è stata annunciata qui, allora, da questa mano pseudonima"), mai come
  un'**autorizzazione** ("questa è la build da eseguire"). Un client conforme NON
  DEVE (MUST NOT) adottare una build *perché* è stata firmata; *quale* build
  adottare è di competenza dell'item 4.1 ed è locale-al-client e opt-in. Legare
  l'onestà di una build a un insieme di firmatari reimporta l'autorità che I-3 vieta
  (la regola ID-11a, per il software).
- **RB-2a (strumenti condivisi, non autorità condivisa).** Questa parte PUÒ (MAY)
  riusare la costruzione del log di trasparenza della Parte 8 (ID-6) e il canale di
  gossip GR-6 per pubblicare e fare gossip degli hash delle build (RB-14) —
  condividere il *meccanismo* non costa nulla (ID-11a). NON DEVE (MUST NOT)
  condividere con la mappa un insieme di parti — **elenco di firmatari o di appender
  del log** — il cui ruolo sia portante sia per la mappa sia per il codice, perché
  quell'insieme sarebbe il kill switch che I-3 vieta, ora in grado di ribaltare sia
  l'inferenza geografica sia il software. Il log condiviso non introduce alcuna
  autorità **perché** entrambe le parti instradano la fiducia attraverso la
  riproduzione, non il log, e il log resta senza permessi (ID-7).

## 3. La toolchain, pinnata per contenuto

- **RB-3 (la toolchain è pinnata per contenuto, non per nome di canale).
  [normativo]** La build DEVE (MUST) pinnare una toolchain *esatta* — uno specifico
  rilascio stable (strawman: `rust 1.xx.y` in `rust-toolchain.toml` con
  `channel = "1.xx.y"`, mai `stable`/`latest`/`beta`/`nightly`) — **e** pinnare gli
  artefatti binari di quella toolchain per `BLAKE2s` nel manifest della build
  (RB-8). "La toolchain" è un insieme di byte hashati, non un nome che un mirror
  possa risolvere diversamente. Un ricostruttore recupera la toolchain da **qualunque**
  mirror e verifica gli hash (I-3: il distributore è sostituibile; i byte sono
  pinnati — il pattern ID-3 applicato al compilatore).
- **RB-3a (pinna l'intera superficie di compilazione).** Il pin DEVE (MUST) coprire
  ogni strumento il cui output raggiunge l'artefatto: `rustc`, `cargo`, le librerie
  precompilate `std`/`core` effettivamente linkate, il linker (strawman: un `lld`/`mold`
  pinnato (s), non l'`ld` ambientale dell'host), la libc/sysroot, e qualunque
  strumento che un `build.rs` invoca. Uno strumento lasciato all'host è un input non
  pinnato e un pericolo per il determinismo (RB-6, RB-18).
- **RB-3b (il compilatore è un binario recuperato — "trusting-trust" è un residuo
  dichiarato). [normativo]** Il `rustc` pinnato è un *binario recuperato*, non
  qualcosa che questa pipeline costruisce da sorgente. Fidarsi di esso è un **residuo
  dichiarato** (§10, "trusting-trust"): RB-3 pinna *quali* byte di compilatore usano
  tutti, così che tutti i ricostruttori condividano lo *stesso* residuo e qualunque
  *sostituzione* sia rilevabile per divergenza; **non** rende il compilatore onesto.
  Pinnare dimostra la **provenienza**, non l'**onestà** (vedi RB-18). Un percorso di
  bootstrap-da-sorgente o di diverse-double-compilation, se mai adottato, è nominato
  come lavoro futuro, non richiesto qui.

## 4. La build ermetica

La build è una **funzione pura dal manifest a un artefatto byte-identico**. Il
determinismo è tutto il gioco: se due builder onesti possono divergere, l'uguaglianza
degli hash (RB-9) smette di significare "stesso binario" e i builder onesti vengono
segnalati come un attacco (RB-7, RB-15) — la lezione della Parte 8 (preambolo
ID-4), disimparata qui sarebbe fatale.

```
  LA BUILD È UNA FUNZIONE PURA DEL MANIFEST (RB-8)

  ┌──────────────────────── manifest (RB-8) ────────────────────────┐
  │  commit/tag di sorgente · hash della toolchain (RB-3) · hash di  │
  │  contenuto di ogni dipendenza (RB-5) · ambiente fisso (RB-4b) ·  │
  │  target triple · SOURCE_DATE_EPOCH (derivato, RB-4b) · H_build   │
  │  atteso                                                          │
  └────────────────────────────┬────────────────────────────────────┘
                               ▼
            ┌─────────────────────────────────────────┐
            │  BUILD ERMETICA (fn pura, RB-4)         │
            │  nessuna rete (RB-4a), nessuno stato    │
            │  host ambientale, env fisso (RB-4b), il │
            │  nondeterminismo eliminato secondo      │
            │  l'insieme di pericoli pinnato          │
            │  (RB-6, versionato per toolchain)       │
            └───────────────────┬─────────────────────┘
                               ▼
                   artefatto (per UN target triple)
                               │
                               ▼
              H_build = BLAKE2s(artefatto)   ← l'UNICO nome della build (RB-6a)
                                              definito per (sorgente, manifest,
                                              target triple) — RB-6b

  Alice ─ stesso manifest, stessa triple ─▶ H_A   Due builder onesti concordano
  Bob   ─ stesso manifest, stessa triple ─▶ H_B   per H_build uguale. La riprodu-
                                                   zione è l'arbitro (RB-7), non
                                                   un firmatario.
```

- **RB-4 (build ermetica, offline, priva di ambiente). [normativo]** La build DEVE
  (MUST) essere eseguita con **nessun accesso di rete** e **nessuno stato host
  ambientale**: nessuna lettura di `$HOME`, variabili d'ambiente dell'host (oltre
  una allow-list esplicita, RB-4b), l'orologio di sistema per alcun valore
  incorporato, nomi di utente/gruppo, hostname, conteggio di CPU dove inciderebbe
  sull'output, o qualunque percorso fuori dalla sandbox. Substrati conformi: una
  derivazione pura stile Nix/`crane`, **oppure** una sandbox container/`bwrap` con il
  namespace di rete rimosso e un ambiente minimo fisso. Questa parte specifica le
  **proprietà** e non impone alcun substrato (I-1: un implementatore ostile
  costruisce un builder conforme dalle proprietà); Nix e un container in sandbox sono
  nominati come i due substrati conformi di riferimento. Una parte che adotta un
  substrato DEVE (MUST) pinnare anche *esso* (una toolchain Nix è essa stessa un pin
  RB-3).
- **RB-4a (nessun recupero di rete al tempo della build, mai). [normativo]** La build
  NON DEVE (MUST NOT) recuperare alcunché — nessun accesso al registry, nessuna
  risoluzione di dipendenze git, nessun download da `build.rs`, nessun pull della
  toolchain. Ogni recupero avviene *prima* del passo ermetico, pinnato per hash, ed è
  passato attraverso il manifest. Una build che *può* raggiungere la rete è non
  conforme anche se capita di non usarla, perché il suo determinismo dipende allora
  da un server (il divieto di input fluttuanti ID-4c, per il software).
- **RB-4b (ambiente fisso, dichiarato, derivato). [normativo]** L'ambiente di build
  DEVE (MUST) essere fissato nel, e solo nel, manifest: locale `C`/`C.UTF-8`,
  `TZ=UTC`, umask, l'allow-list di env, e `SOURCE_DATE_EPOCH`. `SOURCE_DATE_EPOCH`
  DEVE (MUST) essere **derivato deterministicamente dal commit taggato** (la data di
  commit del tag pinnato), così che sia una funzione di un input pinnato, non
  un'asserzione del manifest fluttuante che un builder possa impostare a piacere. Una
  data di commit falsificata non è una vittoria silenziosa: cambia `H_build` ed è
  quindi colta per divergenza (RB-7), esattamente come qualunque altro cambiamento
  di input.

## 5. L'albero delle dipendenze

- **RB-5 (albero delle dipendenze minimale, auditato, vendorizzato, pinnato per
  contenuto). [normativo]** Le dipendenze DEVONO (MUST) essere (a) *minimizzate* —
  ciascuna giustificata contro il non averla, perché ogni crate è un autore non
  fidato nella catena di fiducia (RB-16, OP-10); (b) *vendorizzate* — la sorgente
  esatta di ogni dipendenza transitiva pinnata negli input della build, non risolta
  live (RB-4a); e (c) *pinnate per contenuto* — `Cargo.lock` committato, **e** ogni
  crate inoltre pinnato per `BLAKE2s` della sua sorgente nel manifest (RB-8), non
  affidato al solo checksum del registry. Un registry che può cambiare i byte sotto
  un nome è un'autorità; l'hash di contenuto lo rimuove e rende il registry una CDN
  sostituibile.
- **RB-5a (il lockfile è necessario, non sufficiente).** `Cargo.lock` pinna le
  versioni e i checksum del registry; non rende di per sé la *build* riproducibile
  (l'unificazione delle feature, `cfg`, le differenze di host mordono ancora — RB-6)
  né rimuove la fiducia nel registry. Il pin-per-contenuto di RB-5 e l'ermeticità di
  RB-4 chiudono quel divario. Una build che pinna solo il lockfile è non conforme.
- **RB-5b (gli script di build e i proc-macro sono calcolo fidato, non dati inerti).
  [normativo]** Gli script `build.rs` e le macro procedurali eseguono codice
  arbitrario *al tempo della build*; DEVONO (MUST) essere eseguiti dentro la sandbox
  RB-4 sotto le stesse regole no-rete/no-ambiente, e sono nell'ambito dell'audit
  RB-16 esattamente come il codice a runtime. Un proc-macro che legge l'orologio o la
  rete è un pericolo per il determinismo e una superficie di supply chain in uno.

## 6. I pericoli per il determinismo e come la build li pinna

Ciascun pericolo qui sotto è un punto in cui due builder onesti potrebbero produrre
byte diversi. La build DEVE (MUST) eliminare ciascuno; una build che non lo fa è non
conforme perché non può supportare RB-9, e la sua divergenza è mal interpretata da
RB-7 come un attacco.

- **RB-6 (l'insieme di pericoli è normativo, versionato per toolchain). [normativo]**
  La build DEVE (MUST) eliminare ogni pericolo nell'**insieme di pericoli pinnato**
  per la versione di toolchain in uso. Questo insieme è normativo-rispetto-a-una-
  toolchain-pinnata, non per sempre (residuo §10.7: il determinismo è un bersaglio
  mobile contro il turnover delle toolchain), e il manifest DEVE (MUST) referenziare
  la versione dell'insieme di pericoli contro cui è stato costruito. L'insieme, come
  minimo, DEVE (MUST) pinnare:
  - **timestamp** — `SOURCE_DATE_EPOCH` dal commit taggato (RB-4b); nessun mtime in
    alcun archivio emesso;
  - **percorsi di build** — `--remap-path-prefix` verso una radice `/build` fissa,
    così che nessun percorso assoluto, `$HOME`, o nome utente sia incorporato nelle
    debug info o nelle stringhe di panic;
  - **parallelismo e ordinamento** — l'ordine delle codegen-unit, l'ordine di link,
    l'ordine della symbol-table, l'ordine dei membri dell'archivio, e qualunque
    ordine di iterazione di hash-map che raggiunga l'output DEVONO (MUST) essere resi
    deterministici (fissi o ordinati);
  - **derivazione di `-C metadata` / `-C extra-filename`** — derivata
    deterministicamente da input pinnati, mai da un valore che vari con l'host;
  - **locale/codifica** — `LC_ALL=C`;
  - **debug-info e simboli** — deterministici, o rimossi (strip); se tenuti,
    deterministici;
  - **layout e seed randomizzati** — `-Z randomize-layout` disattivato; qualunque
    codegen con seed di RNG pinnato;
  - **il framing di archivio/pacchetto** — un codec fisso a un livello fisso, senza
    nomi di file, timestamp, o uid/gid nei metadati del container (la regola di
    container-canonico ID-4d, per il packaging software).

  L'analogo del pericolo di decode non pinnato della Parte 8 (nota §10 di ID-4d) si
  applica qui ed è nominato, non nascosto: **la codegen dipendente dalla versione di
  LLVM e l'unificazione di `cfg`/feature dipendente dall'host** (ammessa in RB-5a)
  sono riproducibili solo *rispetto alla toolchain pinnata e alla risoluzione delle
  feature pinnata*; ogni avanzamento di toolchain è un nuovo obbligo di audit del
  determinismo (§10.7), non un pasto gratis.
- **RB-6a (l'artefatto è indirizzato per contenuto; `H_build` è il suo unico nome).
  [normativo]** L'artefatto di rilascio è indirizzato da `H_build = BLAKE2s(artefatto)`
  (l'hash della suite, Parte 0). `H_build` è l'unico nome autorevole della build; una
  stringa di versione leggibile dall'uomo (`v1.2.3`) è un'etichetta di comodo e NON
  DEVE (MUST NOT) essere fidata al posto di `H_build` (la regola ID-2 "l'hash è
  l'unico nome"). La freschezza — *quale* versione un client dovrebbe eseguire — è una
  proprietà separata, portata da RB-8a, non dalla stringa di versione.
- **RB-6b (`H_build` è per-target; l'accordo è definito all'interno di una triple).
  [normativo]** Un rilascio si riproduce in byte *diversi* per target
  (`aarch64-linux-android`, `x86_64-unknown-linux-gnu`, `armv7-…`, …) dalla *stessa*
  sorgente, così che `H_build` è una funzione di **(sorgente taggata, manifest,
  target triple)**. Il manifest DEVE (MUST) pinnare il target triple; l'accordo
  (RB-9) è definito **solo all'interno di una triple fissa**; e RB-7/RB-15 DEVONO
  (MUST) confrontare solo `H_build` di triple uguali. Un client che confronta il
  proprio hash di triple con un hash pubblicato di una triple diversa NON DEVE (MUST
  NOT) sollevare un'anomalia di divergenza-di-build — quello è un errore di
  categoria, non un attacco. La parte pinna anche esattamente quali byte `H_build`
  copre per ogni artefatto spedito (il binario del nodo, e separatamente qualunque
  installer o libreria), così che due ricostruttori hashino lo stesso oggetto.

## 7. Come due parti concordano di detenere lo stesso binario

- **RB-7 (la procedura di ricostruisci-e-confronta di uno sconosciuto). [normativo]**
  La procedura che una parte con *nessuna relazione con alcun contributore* esegue
  per ottenere un artefatto bit-identico e verificarlo:
  1. recupera la sorgente taggata e il manifest (RB-8) da **qualunque** mirror;
  2. verifica ogni input contro il suo `BLAKE2s` di manifest (RB-3, RB-5);
  3. esegui la build ermetica (RB-4) per il target triple (RB-6b);
  4. calcola `H_build`;
  5. confronta per uguaglianza di `BLAKE2s` con l'hash pubblicato (RB-14) e con
     l'hash di stessa triple di qualunque peer.

  Un `H_build` uguale è prova dello stesso binario; uno diverso è prova che
  differiscono e DEVE (MUST) essere fatto emergere come una **divergenza di build**
  (RB-15), mai riconciliato silenziosamente. La disputa è risolvibile da chiunque
  senza appello a un'autorità: ricostruisci e vedi cosa produce la sorgente pubblica
  (l'arbitro ID-5a, per il software). Questo è il criterio di "fatto" dell'item 4.2:
  due parti su macchine diverse producono artefatti hash-identici dalla sorgente
  taggata tramite una procedura che non nomina alcun singoletto fidato.
- **RB-7a (un rilascio che non si riproduce è rifiutato, non rattoppato).
  [normativo]** Un artefatto rilasciato il cui `H_build` non può essere riprodotto
  dal suo manifest dichiarato è, per definizione, non la build di quella sorgente: un
  verificatore conforme che *può* ricostruire DEVE (MUST) rifiutarlo e DOVREBBE
  (SHOULD) fare gossip della discrepanza come anomalia di build (RB-15). "Si
  costruisce sulla macchina del manutentore ma da nessun'altra parte" è un
  fallimento di riproducibilità — un difetto — non uno stato accettabile (la regola
  ID-5b, per il software).
- **RB-7b (il client che non può ricostruire — l'utente modale). [normativo]** Quasi
  ogni utente reale esegue il client su un telefono senza toolchain, senza disco, e
  senza banda per compilare l'albero delle dipendenze; *non può* eseguire
  l'operazione (b) di RB-1. Un tale client DEVE (MUST) tracciare ogni binario che
  esegue come **`reproduced-by-others-unverified`** finché esso (o un peer il cui
  `H_build` poi corrisponde) non ricostruisce, DEVE (MUST) trattare la corroborazione
  come un conteggio di riproduttori **verificati indipendentemente** sotto la regola
  RB-10 (mai un conteggio grezzo di attestazioni), e la parte enuncia chiaramente:
  **per il client che non ricostruisce, la fiducia-nella-build non fluisce dalla
  riproduzione — si riduce alla corroborazione-per-conteggio, che è OP-2**,
  esattamente come la fiducia-nella-mappa della Parte 8 si riduce a OP-2 per il
  client della mappa che non ricostruisce (§10, ID-5b/§10). Il client DEVE (MUST)
  far emergere questo stato; NON DEVE (MUST NOT) presentare un binario non
  ricostruito come se l'utente l'avesse verificato.

## 8. Il manifest, l'accordo, e la freschezza

- **RB-8 (il manifest è la ricetta di riproduzione). [normativo]** Ogni rilascio
  DEVE (MUST) spedire un **manifest**: il commit/tag di sorgente, gli hash della
  toolchain pinnata (RB-3), l'hash di contenuto di ogni dipendenza (RB-5),
  l'ambiente fisso (RB-4b), il target triple (RB-6b), `SOURCE_DATE_EPOCH` (derivato,
  RB-4b), la versione dell'insieme di pericoli (RB-6), e l'`H_build` atteso. Il
  manifest — non un server, non una persona — definisce la build (il manifest ID-3,
  per il software).
- **RB-8a (il manifest è canonico e indirizzato per contenuto; la freschezza è un
  campo controllabile). [normativo]** Il manifest DEVE (MUST) avere una
  **serializzazione canonica** (riusa il profilo canonical-CBOR della Parte 2,
  GR-21..GR-30) ed è esso stesso indirizzato per contenuto da
  `manifest-hash = BLAKE2s(manifest canonico)`; altrimenti due parti oneste
  producono manifest-hash diversi per la stessa ricetta e la corroborazione del log
  (RB-14) si spacca su una differenza di formattazione — la lezione GR-21
  disimparata. Il manifest DEVE (MUST) portare un **indice di rilascio monotono**
  legato insieme alla data di commit derivata, e la foglia del log di trasparenza
  (RB-13) DEVE (MUST) preservare quell'ordinamento, così che la *recenza* sia una
  proprietà controllabile dell'artefatto. Questo chiude il divario di giunzione con
  4.1 che 4.1 non può chiudere più tardi (lo schema del manifest è un artefatto 4.2):
  vedi RB-9a.
- **RB-9 (l'accordo è uguaglianza degli hash, nient'altro). [normativo]** Due parti
  detengono lo stesso binario **se e solo se** i loro `H_build` di stessa triple sono
  uguali (RB-6b). Il confronto è un controllo di 32 byte; non ha bisogno di
  firmatario, quorum, o autorità (la regola ID-5, per il software).
- **RB-9a (la riproducibilità dimostra binario-combacia-con-sorgente, non
  sorgente-è-corrente — il residuo di freschezza). [normativo]** `H_build` autentica
  *che i byte combaciano con la sorgente*; non dice nulla su *quale sorgente sia
  quella da eseguire*. Un **attacco di downgrade riproducibile** — alimentare a un
  client un vecchio tag con una vulnerabilità nota, che si riproduce perfettamente e
  supera ogni controllo RB qui sopra — è sconfitto **solo** da una regola di
  freschezza. Questa parte fornisce l'input controllabile per quella regola (l'indice
  di rilascio monotono + la data derivata di RB-8a, ordinati nel log, RB-13); la
  *politica di adozione* che lo usa (rifiuta un indice inferiore a uno già visto;
  avvisa sulla stantezza) è l'item 4.1 ed è locale-al-client. Il residuo: la
  riproducibilità da sola non sconfigge il downgrade; il campo di manifest che questa
  parte impone è ciò che rende *possibile* sconfiggerlo per 4.1 (l'epoch ID-4, per i
  rilasci).

## 9. La giunzione di merge con la governance degli aggiornamenti (OP-8 / item 4.1)

I firmatari dei rilasci e i publisher delle root della mappa sembrano un unico
meccanismo. **Posizione, che rispecchia il §9 della Parte 8: tenerli separati nella
fiducia, anche se condividono gli strumenti.**

- **RB-10 (un'attestazione è una rivendicazione di riproduzione, pesata per
  ri-riproduzione indipendente, non per chi l'ha emessa). [normativo]** Un'**attestazione**
  di build è un'affermazione *"ho ricostruito il manifest M per la triple T e ho
  ottenuto `H_build`"* — un **rapporto di riproduzione**, non un'autorizzazione. Il
  suo peso viene dall'essere **controllabile indipendentemente** (chiunque riesegue
  RB-7 e la conferma o la confuta), non dall'identità dell'attestante:
  un'attestazione firmata con pseudonimo e una non firmata portano lo **stesso** peso
  una volta che una terza parte ha riprodotto la rivendicazione; la firma solo
  *localizza* la rivendicazione (RB-2). La corroborazione DEVE (MUST) seguire
  esattamente la disciplina della Parte 2: **conta solo le riproduzioni verificate
  indipendentemente, mai un conteggio grezzo di attestazioni** (la regola GR-20 /
  PS-10 "conta solo le verificate, mai le grezze"). E la parte concede ciò che
  GR-19a già dimostra: **l'indipendenza dei riproduttori non è verificabile dalle
  sole attestazioni** — non puoi distinguere 10 000 riproduttori da una sola parte
  che indossa 10 000 maschere — così che un conteggio di riproduttori è un segnale
  *debole* che si riduce a OP-2, e il segnale *forte* è la ricostruzione propria del
  client (RB-7). Un design in cui l'accettazione di un'attestazione dipende
  dall'identità dell'attestante, o in cui un conteggio grezzo di attestazioni non
  verificate corrobora una build, è non conforme (RB-1, ed è l'autorità di
  maggioranza votabile-da-sybil che RB-10 esiste per vietare).
- **RB-10a (formato di attestazione canonico, dedup per riproduttore). [normativo]**
  Le attestazioni attraversano il filo (RB-14) e alimentano un conteggio (RB-10),
  quindi DEVONO (MUST) avere una codifica canonica (riusa il CBOR canonico,
  GR-21..GR-30) o due attestanti onesti producono byte non corrispondenti e il
  conteggio si rompe. Le attestazioni DEVONO (MUST) essere deduplicate per
  `(identità di riproduzione, M, triple, H_build)`, e il peso è
  **per-riproduttore-indipendente, mai per-stringa-di-byte-di-attestazione**, così
  che un avversario non possa gonfiare la corroborazione coniando varianti
  byte-distinte di un'unica rivendicazione (format-stuffing).
- **RB-11 (la toolchain deve costruire in modo deterministicamente usabile; esiste un
  test vector cross-host). [normativo]** Poiché la toolchain pinnata può essa stessa
  incorporare nondeterminismo (codegen parallela, `OUT_DIR`, host triple nei
  metadati), la parte DEVE (MUST) pinnare i flag e le modalità che le fanno produrre
  output identico attraverso gli host (RB-6), e DEVE (MUST) esistere un **test vector
  di build cross-host** (manifest → `H_build` atteso per una triple fissa) così che
  una seconda macchina dimostri di riprodurre l'artefatto identico (la regola di
  test-vector della mappa ID-4d; si lega all'harness di conformità della roadmap
  3.2). Questo è l'analogo RB di RI-1b della Parte 9: *un test funzionale superato
  dimostra che il binario gira, non che è bit-identico* — la riproducibilità è
  controllata per ricostruisci-e-confronta, mai assunta da "ha compilato".
- **RB-12 (i contributori sono pseudonimi; la fiducia fluisce solo attraverso la
  riproducibilità). [normativo]** ScrambNet **non ha chiavi di firma legate
  all'identità** e nessuna identità d'autore fidata. La fiducia in un binario DEVE
  (MUST) derivare **interamente** da (a) la sorgente che è pubblica e revisionabile
  (I-1) e (b) il binario che si riproduce da quella sorgente (RB-7) — **mai** da *chi*
  l'ha scritto, committato, taggato, o firmato. Un passo che richiede un'identità
  fidata di autore, manutentore, o firmatario per accettare una build è non conforme
  sia sotto RB-1 sia sotto la regola di pseudonimità del progetto. Questa è la
  risoluzione della tensione centrale di questa parte: *l'autore è non fidato per
  costruzione; il binario è fidato per riproduzione.*
- **RB-12a (a cosa servono le chiavi di pseudonimo — e la precondizione su cui
  poggiano).** Una chiave di contributore, se usata affatto, autentica la *continuità
  di uno pseudonimo* e *localizza* il lavoro (questo commit, questa attestazione,
  vengono dalla stessa mano pseudonima) — un comodo per il gossip e per il ruolo di
  localizzatore di 4.1 (RB-2), mai una radice di fiducia-nella-build. Perdere,
  ruotare, o sostituire una tale chiave NON DEVE (MUST NOT) invalidare alcun binario
  che si riproduce ancora. Un detentore di una chiave compromessa non può distribuire
  un binario malevolo-ma-riproducibile che **sopravviva a un revisore onesto più un
  riproduttore onesto** — ma quella protezione è *la loro esistenza*, non la chiave:
  in assenza di un revisore onesto della sorgente (I-1) e di un riproduttore onesto
  che il client possa raggiungere (RB-7/RB-10), la chiave compromessa *può*
  distribuire un binario malevolo a un client che né revisiona né ricostruisce
  (RB-7b). Quindi la protezione si riduce a I-1 (revisione) e OP-2 (raggiungibilità
  di un riproduttore onesto); non è una proprietà incondizionata della chiave.
  (Questo enuncia la precondizione esplicitamente, così che l'affermazione non sia
  circolare.)
- **RB-12b (la riproducibilità dimostra binario-combacia-con-sorgente, non dice nulla
  sull'onestà della sorgente).** Riproducibilità e revisione sono **assi ortogonali**.
  La riproducibilità dimostra che il binario combacia con la sorgente; non dice nulla
  sul fatto che la sorgente sia onesta. La pseudonimità (RB-12) rimuove "un autore
  fidato ha garantito per la sorgente", così che l'onestà-della-sorgente poggia sulla
  **revisione pubblica (I-1)** e nient'altro. La parte enuncia questo chiaramente
  così che nessun lettore scambi "riproducibile" per "sicuro" o "revisionato": una
  build fedelmente riprodotta di una sorgente con backdoor è una fedele riproduzione
  di una backdoor (§10, OP-10).
- **RB-13 (hash e manifest sono pubblicati su un log senza permessi, ordinati per
  indice di rilascio).** Le tuple di rilascio
  `(triple, H_build, manifest-hash, release-index, committer-date)` DOVREBBERO
  (SHOULD) essere annunciate agli stessi log di trasparenza append-only senza
  permessi usati per le mappe (ID-6/ID-7), preservando l'ordinamento RB-8a, così che
  gli annunci di build siano marcati temporalmente e con equivocazione rilevabile
  **senza alcun appender privilegiato** (ID-7). Il log non *benedice* una build — lo
  fa la riproduzione (RB-7) — rende rilevabile "binario diverso mostrato a persone
  diverse" e dà alla freschezza (RB-9a) un ordine testimoniato. Per RB-2a la
  *costruzione* del log è condivisa con la mappa; le *istanze/insiemi* DOVREBBERO
  (SHOULD) restare indipendenti (ID-7b "log multipli, nessuno canonico") così che i
  due domini di disponibilità non collassino in un unico operatore portante.
- **RB-14 (fai gossip della tupla di build; rileva lo split-view). [normativo]** I
  client e i ricostruttori DOVREBBERO (SHOULD) fare gossip di
  `(triple, H_build, manifest-hash, release-index)` su GR-6 sotto il mescolamento
  delle sorgenti GR-8, e pretendere prove di consistenza del log di trasparenza, così
  che un avversario che serve il binario X ad Alice e il binario Y a Bob (stessa
  triple, indice uguale o in conflitto) sia colto da qualunque parte che detenga
  entrambi (la difesa dall'equivocazione ID-7a, per le build). Un log che vincoli gli
  append di build dietro un insieme di firmatari è non conforme (RB-2a/ID-7).
- **RB-15 (le anomalie di build sono diffuse via gossip, non soppresse). [normativo]**
  Quattro eventi sono anomalie di build di cui ogni verificatore DEVE (MUST) fare
  gossip al rilevamento, confrontando solo hash di stessa triple (RB-6b): (a) un
  `H_build` che fallisce la riproduzione dal suo manifest (RB-7a); (b) un log di
  trasparenza che presenta root inconsistenti sugli annunci di build (equivocazione
  dimostrata); (c) una divergenza persistente di `H_build` di stessa triple contro
  riproduttori indipendenti; (d) una **regressione dell'indice di rilascio** — un tag
  presentato con un indice inferiore a uno già testimoniato per quella linea di
  rilascio (la firma del downgrade, RB-9a). Un verificatore NON DEVE (MUST NOT)
  sopprimere un'anomalia per far sembrare sano un rilascio (la regola del segnale
  immunitario ID-10, per le build).

## 10. Cosa questa parte non risolve (il residuo dichiarato)

Questa parte fa sì che due parti che *entrambe ricostruiscono* concordino in modo
dimostrabile o rilevino in modo dimostrabile che differiscono, e sposta la fiducia da
*chi l'ha costruito* a *si ricostruisce?* — una riduzione reale e grande, quella
giusta per un progetto pseudonimo. **Non** rende il binario *sicuro*. I divari sono
reali e sono dichiarati, non lisciati via:

- **§10.1 — Una backdoor in una dipendenza pinnata è riprodotta fedelmente, non
  colta.** Se un crate vendorizzato contiene codice ostile, ogni ricostruttore
  ottiene il binario malevolo identico e RB-7 *conferma* la corrispondenza — la
  riproduzione funziona esattamente come progettata ed è cieca alla malizia. Il
  binario riflette onestamente una sorgente che è onestamente con backdoor. Le uniche
  difese sono **la revisione pubblica (I-1), l'audit (RB-16), e la minimizzazione
  della superficie di dipendenze (RB-5/RB-17)** — processi umani che *delimitano* la
  superficie, nessuno un controllo crittografico privo di autorità. **Questo è il
  residuo primario, non ha alcun surrogato non fidato, ed è il problema ricorrente
  del progetto che indossa una quarta maschera — OP-10.** La proposta di valore è
  onesta proprio qui: la riproducibilità **non** difende dall'attacco reale più
  probabile, e non è mai stata pensata per farlo — ma cambia *che tipo* di attacco è
  richiesto. Senza di essa, un attaccante avvelena **un binario per un target**, in
  modo invisibile e non attribuibile. Con essa, un binario malevolo deve risalire a
  **sorgente pubblica** che **tutti possono revisionare** e che **si riproduce
  identica per tutti** — forzando l'attacco da "avvelena il binario" (invisibile,
  per-target) a "avvelena la sorgente pubblica o una dipendenza pubblica"
  (revisionabile, universale, massimamente esposto all'unico revisore onesto). Quella
  trasformazione è il valore della parte; cogliere la sorgente avvelenata è OP-10 e
  I-1, non la riproducibilità.
- **§10.2 — Una toolchain compromessa che miscompila in modo riproducibile.** Un
  `rustc`/LLVM con backdoor può inserire comportamento assente dalla sorgente, in
  modo deterministico, così che ogni ricostruttore riproduce il binario cattivo
  identico e l'uguaglianza di `H_build` regge. Il pinning (RB-3) fa condividere a
  tutti un solo compilatore e rende *sostituirlo* rilevabile; non rende onesto il
  compilatore pinnato. **Nessun surrogato non fidato** a meno di un
  bootstrap-da-sorgente o di una diverse-double-compilation, che questa parte nomina
  come lavoro futuro (RB-3b), non un requisito corrente.
- **§10.3 — "Trusting-trust" (Thompson).** Il caso generale del §10.2: un
  compilatore che inserisce una backdoor *e* propaga la backdoor nei compilatori che
  costruisce. Pinnare i byte del compilatore non rompe il ciclo; garantisce che tutti
  siano dentro lo *stesso* ciclo. Dichiarato, non risolto. (È per questo che RB-18
  dice "ogni byte di output risale a un input *pinnato*" — provenienza — e
  esplicitamente **non** "a un input *onesto*": un compilatore hashato, pinnato, con
  backdoor soddisfa la tracciabilità ed è comunque malevolo.)
- **§10.4 — Riproducibile ≠ sicuro; riproducibile ≠ revisionato.** Una build
  perfettamente riproducibile di una sorgente dall'aspetto-onesto-ma-sottilmente-
  sbagliata è perfettamente riproducibile. La pseudonimità (RB-12) significa che
  nessun autore fidato garantisce per la sorgente, così che l'onestà-della-sorgente
  poggia interamente sulla revisione pubblica (I-1); riproducibilità e revisione sono
  ortogonali (RB-12b).
- **§10.5 — La corroborazione-per-conteggio si riduce a OP-2; il client che non
  ricostruisce è l'utente modale.** "N ricostruttori indipendenti hanno ottenuto
  `H_build`" è solido solo quanto l'*indipendenza* degli N (RB-10, GR-19a). Una sola
  ri-riproduzione onesta confuta una falsa rivendicazione con certezza (più forte del
  caso della mappa, poiché la sorgente è deterministica), ma un client che **non può
  ricostruire** (RB-7b — il telefono, cioè quasi ogni utente) si appoggia al
  conteggio delle attestazioni, che è un quorum votabile-da-sybil: un avversario conia
  attestazioni pseudonime per un `H_build` cattivo, e un client **eclissato** vede
  solo attestazioni dell'avversario e non incontra mai un riproduttore onesto. Quindi
  per il client che non ricostruisce o è eclissato, "nessuna autorità" significa
  "fidati del quorum di riproduttori verificati", e questo vale solo fin dove vale
  **OP-2**. Questa parte **riduce** l'autorità della build a OP-2 per chi non
  ricostruisce; non la dissolve — la riduzione identica su cui si chiude la Parte 8
  (ID-1 → OP-2).
- **§10.6 — L'arbitro è limitato dalla liveness; l'escrow deve essere replicato o è un
  singoletto.** Ricostruisci-e-confronta è l'arbitro privo di autorità **solo finché
  gli input pinnati sono ancora recuperabili**. I binari della toolchain e l'intero
  albero dei crate sono grandi e deperibili: un **crate yankato** o un **rilascio di
  toolchain de-pubblicato** rende `rebuild(manifest)` ineseguibile, e allora l'unica
  operazione fidata è sparita — nel peggiore dei casi proprio per le dispute forensi
  ("la v1.2 aveva una backdoor?") che ne hanno più bisogno. Un deployment conforme
  DOVREBBE (SHOULD) depositare in escrow i byte degli input pinnati in uno store
  indirizzato per contenuto **replicato sullo stesso insieme di mirror senza permessi**
  delle build; un escrow a singola replica è indirizzato per contenuto (così che non
  possa *mentire*) ma è un **singoletto di liveness** (può *svanire*), e I-3 copre la
  liveness. In assenza di replica, RB-7 è dichiarato **limitato dalla liveness**, non
  incondizionato (il residuo di liveness ID-5a, per le build).
- **§10.7 — Il determinismo è un bersaglio mobile contro il turnover delle
  toolchain.** Nuove versioni di `rustc`/LLVM introducono nuove sorgenti di
  nondeterminismo (nuovi passi paralleli, nuovi metadati, nuovo comportamento di
  `cfg`). L'insieme di pericoli di RB-6 è **corrente**, non chiuso; una toolchain
  pinnata è riproducibile *come pinnata*, ma ogni avanzamento di toolchain è un nuovo
  obbligo di audit del determinismo, e il manifest registra contro quale versione
  dell'insieme di pericoli è stato costruito (RB-6, RB-8). "Riproducibile una volta"
  non significa "riproducibile per sempre".
- **§10.8 — TOFU della prima build: un primo binario malevolo mente sul riprodurre sé
  stesso.** Il *primo* binario client di un utente nuovo non può essere riprodotto
  prima di essere usato per il bootstrap (ti serve un client funzionante per
  recuperare la sorgente, la toolchain, e raggiungere i log e i peer). Il primo
  binario è adottato per trust-on-first-use esattamente come lo è la prima mappa della
  Parte 8 (ID-8) — e peggio: un primo binario compromesso possiede d'allora in poi
  l'intero apparato di riproduzione e gossip dell'utente, così che può **mentire
  sulla propria riproduzione** ("ho ricostruito me stesso; `H_build` combacia"). Un
  client quindi non può verificare onestamente *la propria* riproduzione; la fiducia
  nel primo binario poggia su un **riproduttore indipendente out-of-band** — una
  macchina/toolchain diversa di cui l'utente si fida più del binario sotto test.
  Questo è il confine di "trusting-trust" / host-compromesso (§10.9); è un residuo
  dichiarato, enunciato qui anziché inghiottito silenziosamente da "fuori ambito".
- **§10.9 — Cosa questa parte non tenta nemmeno.** La compromissione a runtime della
  macchina dell'utente; una *build malevola di sorgente onesta fatta dall'utente
  stesso* su un host compromesso (la riproduzione conferma la corrispondenza; l'host
  possiede comunque il processo); e tutto ciò che sta sopra il confine dell'artefatto
  — l'installazione, e l'*adozione* degli aggiornamenti (quale build eseguire e
  quando), che è l'item 4.1. La parte riguarda solo l'artefatto bit-identico; nomina
  queste come fuori ambito, non come risolte.

Il riassunto onesto: le build riproducibili spostano la fiducia da *chi l'ha
costruito* a *si ricostruisce?* — reale e grande. Ma sono **silenziose** sul fatto
che la sorgente sia onesta (§10.1, §10.4), **cieche** a una backdoor riproducibile di
compilatore/dipendenza (§10.1, §10.2, §10.3), **limitate dalla liveness** come
arbitro (§10.6), **ridotte a OP-2** per il client che non ricostruisce o è eclissato
(§10.5) — l'utente modale (RB-7b) — e **TOFU** sul primo binario (§10.8). Questi sono
il prezzo del rifiutare un'autorità di rilascio. La risposta corretta è delimitarle —
minimizzare e auditare la base di calcolo fidata, replicare l'escrow, incoraggiare le
ricostruzioni indipendenti, portare l'indice di freschezza — e enunciarle, non
nasconderle.

## 11. Igiene della supply chain che delimita il residuo

- **RB-16 (l'audit delle dipendenze e della toolchain è obbligatorio e nell'ambito).**
  Poiché la riproduzione non può vedere una backdoor che ogni ricostruttore riproduce
  fedelmente (§10.1), la parte DEVE (MUST) richiedere una traccia di audit committata
  e revisionabile per l'insieme di dipendenze e per la toolchain (record stile
  `cargo-vet`/`cargo-audit`, pinnati per contenuto), trattata come **evidenza di
  revisione (I-1), non come autorità**. L'audit riduce la superficie d'attacco del
  §10.1; non la rimuove, e la parte lo dice.
- **RB-17 (minimizza la base di calcolo fidata).** La parte DOVREBBE (SHOULD)
  richiedere di ridurre attivamente ciò che deve essere fidato-e-auditato: meno
  dipendenze (RB-5), meno `build.rs`/proc-macro (RB-5b), una superficie di toolchain
  più piccola (RB-3a), `#![forbid(unsafe_code)]` dove fattibile — perché ogni elemento
  della base di calcolo fidata è un residuo del §10.1 che l'audit deve coprire e che
  la riproduzione non può. Nota onesta: "minimale" non è "piccolo" — un nodo reale
  async + crypto (un runtime async, uno stack Sphinx/X25519, CBOR, …) trascina
  *centinaia* di crate transitivi, molti con script di build, così che il residuo di
  backdoor-nelle-dipendenze del §10.1 non è un caso limite ma la superficie d'attacco
  **attesa**. Quella è l'inquadratura onesta di OP-10.
- **RB-18 (l'intera catena è pinnata o non è pinnata — e pinnato significa
  provenienza, non onestà). [normativo]** Un singolo input non pinnato ovunque — un
  componente di toolchain non hashato, una dipendenza fluttuante, un `build.rs` che
  legge l'host, un'immagine base di container recuperata per tag — annulla la
  rivendicazione di riproducibilità per l'intero artefatto, perché quell'unico input
  reintroduce un server o un host come parte fidata (RB-1). Il manifest DEVE (MUST)
  essere **completo**: se un byte di output non può essere tracciato a un input
  *pinnato*, la build è non conforme (la regola ID-4c, per il software). **Questa è
  un'affermazione di determinismo/provenienza, non un'affermazione di fiducia:** un
  input pinnato può essere malevolo (§10.1, §10.2, §10.3); il pinning rende la malizia
  identica per tutti e rende rilevabile qualunque *divergenza da un input onesto* —
  **non** rende onesto l'input. "Pinnato" non significa mai "sicuro".

## 12. Requisiti introdotti qui

- **RB-1 / RB-2 / RB-2a** — nessuna autorità di rilascio, la riproduzione è l'arbitro;
  le firme solo localizzano, mai autorizzano; strumenti condivisi con la mappa, mai
  autorità condivisa.
- **RB-3 / RB-3a / RB-3b** — toolchain pinnata per contenuto su tutta la superficie di
  compilazione; il compilatore pinnato è un residuo di "trusting-trust" dichiarato
  (provenienza, non onestà).
- **RB-4 / RB-4a / RB-4b** — build ermetica, offline, priva di ambiente; nessun
  recupero al tempo della build; un ambiente fisso con `SOURCE_DATE_EPOCH`
  **derivato** dal commit taggato.
- **RB-5 / RB-5a / RB-5b** — albero delle dipendenze minimale, vendorizzato, pinnato
  per contenuto; lockfile necessario-non-sufficiente; script di build e proc-macro
  sono calcolo fidato in sandbox.
- **RB-6 / RB-6a / RB-6b** — insieme di pericoli di nondeterminismo normativo,
  versionato per toolchain; `H_build` è l'unico nome; `H_build` è per-(sorgente,
  manifest, target triple) e l'accordo è all'interno di una triple.
- **RB-7 / RB-7a / RB-7b** — il ricostruisci-e-confronta dello sconosciuto; rifiuta
  ciò che non è riproducibile; l'utente modale che non ricostruisce traccia
  `reproduced-by-others-unverified` e si riduce a OP-2.
- **RB-8 / RB-8a / RB-9 / RB-9a** — il manifest è la ricetta, canonico e indirizzato
  per contenuto, che porta un indice di rilascio monotono; l'accordo è uguaglianza di
  hash di stessa triple; il residuo di freschezza (downgrade riproducibile) con il
  campo di manifest che 4.1 richiede.
- **RB-10 / RB-10a** — un'attestazione è una rivendicazione di riproduzione pesata per
  ri-riproduzione indipendente (conta solo le verificate, mai le grezze;
  l'indipendenza è OP-2); formato canonico, dedup per riproduttore.
- **RB-11 / RB-12 / RB-12a / RB-12b** — test vector di build cross-host; la fiducia
  fluisce solo attraverso la riproducibilità; le chiavi di pseudonimo localizzano, mai
  radicano la fiducia (con la precondizione resa esplicita, non circolare);
  riproducibilità ⊥ revisione.
- **RB-13 / RB-14 / RB-15** — log senza permessi di tuple di build ordinate per indice
  di rilascio; gossip + rilevamento di split-view; quattro anomalie obbligatorie
  inclusa la firma del downgrade.
- **RB-16 / RB-17 / RB-18** — audit obbligatorio come evidenza di revisione;
  minimizza la TCB (che è ancora grande); l'intera catena pinnata, dove pinnato è
  provenienza, non onestà.

RB-1 e RB-7 sono i due portanti: nessuna autorità, e la riproduzione è l'arbitro.
Entrambi sono delimitati, non assoluti — RB-1 si riduce a OP-2 per il client che non
ricostruisce (§10.5, l'utente modale), e RB-7 è limitato dalla liveness (§10.6). Il
residuo più affilato, enunciato e non nascosto, è il §10.1: **la riproducibilità non
coglie una dipendenza con backdoor, che è l'attacco reale più probabile — forza
l'attacco dentro sorgente pubblica, revisionabile, universale, che è il punto, e
coglierla lì è OP-10, non questa parte.** Rompi questa parte nominando un passo di
build che ha bisogno di una parte fidata, un artefatto rilasciato che non può essere
ricostruito dal suo manifest, un pericolo per il determinismo che RB-6 manca, un modo
in cui una firma contrabbanda di nuovo l'autorizzazione oltre RB-2, o un modo in cui
il client che non ricostruisce resta a fidarsi di una maggioranza che non è OP-2.
Questo è l'invito, nella voce della Parte 8.
