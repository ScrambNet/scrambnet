# Specifica ScrambNet — Parte 1: Share Packet

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([en](../../en/spec/01-share-packet.md)).

**Stato: BOZZA (DRAFT).** Le dimensioni strawman sono contrassegnate con `(s)`. Attaccale per numero di requisito.

## 1. Ambito

Lo share packet è l'unica unità che attraversa l'overlay: porta una quota di
un messaggio attraverso un circuito a cipolla. Tutto in questa parte serve due obiettivi:
il livello minimo incondizionato (I-2) e l'uniformità sul filo (I-4).

## 2. Stratificazione

```
messaggio in chiaro
  └─ AEAD end-to-end (chiave di coppia precondivisa, SP-1a)  [computazionale]
       └─ split di Shamir: n quote, soglia k        [livello minimo incondizionato]
            └─ cifratura a cipolla per quota, circuito proprio, formato Sphinx
                 └─ trasporto camaleonte (Parte 4)
```

- **SP-1.** Il mittente DEVE (MUST) applicare la cifratura end-to-end *prima* della dispersione, e la
  dispersione DEVE (MUST) essere applicata al testo cifrato end-to-end. Con meno di `k`
  quote l'avversario non apprende nulla sul testo cifrato in modo incondizionato
  (Shamir); con `k` o più quote affronta ancora l'AEAD end-to-end. Il
  livello minimo incondizionato e la cintura computazionale si compongono; nessuno dei due sostituisce
  l'altro. La cintura è dimostrata end-to-end in `poc/e2e.py` (cifra → split →
  ricostruisci → decifra, fail-closed in caso di manomissione).
- **SP-1a (stabilimento della chiave di contenuto, e la conseguenza post-quantistica).** La chiave AEAD
  end-to-end DEVE (MUST) essere derivata dal **segreto simmetrico di coppia precondiviso**
  `kpair` trasportato dalla carta di contatto (Parte 6, RZ-2), tramite un KDF separato per
  etichetta: `content_key = HKDF-BLAKE2s(kpair, "e2e-content")`, distinto dalla chiave di tag di
  SP-7 e dalla chiave di box-id derivate dallo stesso `kpair`. NON DEVE (MUST NOT) esserci alcun
  accordo di chiave asimmetrico nel percorso del contenuto. Questa è una scelta deliberata con
  una conseguenza portante: un avversario `≥k` che registra tutto e dispone in futuro di un
  computer quantistico su larga scala non può comunque leggere il contenuto, perché non esiste
  alcuna trascrizione Diffie-Hellman che Shor possa rompere — solo un segreto simmetrico che le
  parti già condividono, e Grover costa all'AEAD al più un dimezzamento della robustezza della
  chiave (quindi è RACCOMANDATO (RECOMMENDED) una chiave derivata ≥256 bit dove il margine conta).
  "Harvest now, decrypt later" (raccogli ora, decifra dopo) è quindi sconfitto a **entrambi** i
  livelli: sotto `k` da Shamir (incondizionatamente), a `k` o oltre da un AEAD simmetrico sotto una
  chiave precondivisa (nessuna assunzione a chiave pubblica da raccogliere). Il costo onesto è il
  **bootstrap**: `kpair` deve prima raggiungere il destinatario su un canale confidenziale
  precedente (lo scambio fuori banda della carta di contatto, Parte 6). Qualsiasi assunzione
  residua a chiave pubblica o PQ-KEM risiede lì, nello scambio della carta — non nel percorso del
  contenuto — e trasportare uno scambio di carta che sia esso stesso post-quantistico è una scelta
  ortogonale e stratificata, non una precondizione per il livello minimo. La suite AEAD è
  ChaCha20-Poly1305 (suite `0x01`); `msg_nonce` (SP-7) è il nonce AEAD, che lega i due livelli e
  rende un nonce riutilizzato doppiamente fatale (collisione di tag SP-7 *e* perdita di
  confidenzialità AEAD — vedi SP-7).
- **SP-2.** Parametri di dispersione di default per la messaggistica: `n = 4`, `k = 3` (s).
  I profili di trasferimento di massa POSSONO (MAY) usare l'IDA di Rabin invece di Shamir, e DEVONO (MUST)
  essere etichettati come computazionali nell'interfaccia del client, perché l'IDA non ha un livello minimo
  incondizionato (OP-3).

## 3. Formato sul filo

- **SP-3.** Ogni pacchetto su ogni collegamento DEVE (MUST) essere esattamente `P = 2048` byte (s).
- **SP-4.** Ogni byte del pacchetto DEVE (MUST) essere indistinguibile da uniforme
  casuale per un osservatore privo delle chiavi rilevanti, a ogni salto (proprietà
  Sphinx; I-4). In particolare non c'è alcuna versione, suite, lunghezza,
  contatore di salti o indice di quota in chiaro.

Layout (dimensioni strawman, massimo 3 salti):

| Campo | Dimensione (s) | Visibile a |
|---|---|---|
| `alpha` — elemento di gruppo Sphinx (X25519) | 32 B | tutti (uniforme) |
| `beta` — info di instradamento Sphinx, 3 × 48 B, con padding | 144 B | sbucciato a ogni salto |
| `gamma` — MAC per salto | 16 B | salto corrente |
| `delta` — payload, incapsulato in AEAD per salto | 1856 B | tratta uscita → destinatario |

- **SP-5.** I relay DEVONO (MUST) mantenere una cache di replay dei valori `gamma` visti per epoca
  di chiave e DEVONO (MUST) scartare i replay in silenzio (difesa standard di Sphinx contro il replay).
- **SP-6.** I relay DEVONO (MUST) emettere i pacchetti in batch a dimensione costante con
  jitter definito dall'implementazione in modalità veloce, e DEVONO (MUST) seguire la strategia di mix
  (stop-and-go o Poisson mix, TBD) in modalità paranoica. La scelta della strategia è
  territorio di OP-5 e deliberatamente irrisolta qui.

## 4. Payload della quota (dentro `delta`, fine del circuito)

Decifrato solo dal destinatario:

| Campo | Dimensione (s) | Note |
|---|---|---|
| `tag` | 16 B | tag PRF con chiave del destinatario, vedi SP-7 |
| `index` | 1 B | indice della quota `1..n` |
| `params` | 1 B | `k`, `n` impacchettati (4 bit ciascuno) |
| `share` | 1792 B | byte della quota di Shamir |
| `pad` | resto | casuale |

- **SP-7 (nessuna collegabilità tra percorsi).** Due quote dello stesso messaggio NON DEVONO (MUST NOT)
  portare alcun valore uguale o correlabile osservabile da chiunque tranne il
  destinatario. L'appartenenza all'insieme delle quote è segnalata solo da `tag`:
  `tag = PRF(K_r, msg_nonce ‖ index)` dove `K_r` è una chiave in possesso del destinatario e
  `msg_nonce` è trasportato dentro il livello end-to-end. Un relay d'uscita, o una
  coalizione di uscite, NON DEVE (MUST NOT) poter stabilire se due pacchetti appartengono allo
  stesso messaggio. Questo requisito è portante: senza di esso, la dispersione
  degrada in una comodità di enumerazione per l'avversario.
- **SP-7a (integrità della quota: residuo fail-closed accettato).** Il `tag` dice *a quale*
  messaggio un pacchetto afferma di appartenere; **non** autentica i byte di `share` né il byte
  dei `params` (`k,n`). La ricostruzione di Shamir non ha un'integrità propria, perciò un
  drop ostile, o un'uscita, che inverte dei bit in una quota — o mente su `k,n` — produce un candidato
  in chiaro coerente-ma-sbagliato che Shamir non può rilevare. Questo è **intercettato un livello
  più in alto**: l'AEAD end-to-end (SP-1a) fallisce il suo tag su qualsiasi ricostruzione corrotta
  e il destinatario scarta il messaggio invece di agire su spazzatura (dimostrato in
  `poc/dispersal.py`, test `test_tampered_share_fails_closed`). Il residuo non è quindi **una
  perdita di confidenzialità ma un attacco di negazione del servizio mirato**: un singolo punto di
  osservazione malevolo su uno degli `n` percorsi delle quote può far fallire la ricostruzione di
  un messaggio specifico, al costo di un singolo bit invertito. Il verdetto per questa bozza è
  **accettare e documentare** quel residuo invece di aggiungere un MAC per quota, per due motivi:
  (1) un autenticatore per quota spenderebbe byte di payload e introdurrebbe una seconda chiave da
  gestire senza rimuovere il DoS — una tratta che può corrompere una quota può ugualmente
  *scartarla*, e `n−k` perdite di questo tipo sono già tollerate per progetto; (2) l'AEAD rende già
  sicuro il fallimento (fail-closed), quindi la questione aperta è la disponibilità, non la
  segretezza. Le mitigazioni oneste sono la ridondanza (margine `n−k`), la disgiunzione dei percorsi
  affinché nessun singolo punto di osservazione si trovi su `k` degli `n` percorsi (OP-1), e il
  ritentare su percorsi freschi. Una revisione futura PUÒ (MAY) aggiungere un legame opzionale per
  quota per i profili critici per la disponibilità; qui deliberatamente non è imposto. `k,n` è
  bloccato da vettori (ordine dei nibble, vettori Parte 3 §3.2) affinché un'implementazione non
  possa essere *accidentalmente* in disaccordo, solo una parte malevola può mentire.
- **SP-7b (nessun `tag` uguale tra drop in collusione, e proprietà del nonce).** La proprietà
  che deve valere: nessuna coppia di pacchetti che una coalizione di drop può osservare porta un
  `tag` uguale a meno che il mittente non abbia riusato una coppia `(msg_nonce, index)`.
  *Argomento:* `tag = PRF(K_r, msg_nonce ‖ index)` con `msg_nonce` fisso a 8 byte e `index` fisso a
  1 byte, perciò l'ingresso della PRF è una codifica a larghezza fissa non ambigua di
  `(msg_nonce, index)` — la mappa `(msg_nonce, index) ↦ input` è iniettiva. Una PRF BLAKE2s con
  chiave dà uscite uguali solo su ingressi uguali (salvo una collisione da ~`2^-128`), quindi `tag`
  uguali implicano un `(msg_nonce, index)` uguale. Le `n` quote di un messaggio condividono un solo
  `msg_nonce` ma usano indici *distinti* `1..n`, dunque ingressi distinti, dunque `tag` distinti:
  una coalizione di drop non può distinguere due quote di un messaggio da due pacchetti scorrelati.
  Due messaggi *diversi* producono un `tag` in collisione solo se riusano un `msg_nonce`. Perciò **la
  proprietà del nonce è un DEVE (MUST)**: un mittente NON DEVE (MUST NOT) riusare un `msg_nonce`
  sotto una stessa `kpair`. Il riuso è doppiamente fatale — fa collidere i `tag` di SP-7 (rendendo
  collegabile un insieme di quote) *e*, poiché `msg_nonce` è il nonce dell'AEAD (SP-1a), distrugge la
  confidenzialità di ChaCha20-Poly1305 (un two-time pad, fissato da
  `test_nonce_reuse_is_detectable_catastrophe`). Un contatore di messaggi strettamente crescente per
  `kpair` soddisfa questo requisito; il valore massimo raggiunto (high-water mark) del contatore DEVE
  (MUST) sopravvivere ai riavvii. A livello di memorizzazione, un drop DEVE (MUST) scartare un
  rideposito di un `(box_id, slot)` già memorizzato (replay) e sfratta il più vecchio per primo sotto
  il limite per casella (RZ-7), così un deposito replicato non moltiplica né sposta la posta onesta
  oltre il limite dichiarato.
- **SP-8.** Un messaggio che non riempie il payload della quota (`1792` byte, meno
  il prefisso di lunghezza di 2 byte) DEVE (MUST) essere riempito con byte casuali prima dello split;
  un messaggio che lo supera è frammentato a un livello superiore a questo
  (il progetto della frammentazione è TBD, interagisce con OP-4). Il prezzo onesto di Shamir: ogni
  quota è lunga quanto il segreto, quindi una dispersione (n, k) trasmette ×`n` il
  volume del testo cifrato (OP-3).
- **SP-9 (timing).** Il mittente NON DEVE (MUST NOT) emettere le `n` quote come una raffica
  simultanea. Le quote DOVREBBERO (SHOULD) essere emesse con ritardo per quota randomizzato; la
  distribuzione e il suo costo in latenza sono OP-4 e irrisolti. I client POSSONO (MAY)
  emettere quote esca (pacchetti con `tag` casuale) a una cadenza configurabile.

## 5. L'handshake di circuito (non esiste — è Sphinx)

La suite un tempo nominava `Noise_XK_25519_ChaChaPoly_BLAKE2s` come "handshake di
circuito" che nulla specificava, un difetto I-1: un implementatore ostile non
poteva costruire un nodo interoperabile, perché non c'era alcuna trascrizione da
costruire. **La soluzione è cancellare la riga.** Sphinx esegue già l'accordo di
chiave per salto di cui un circuito ha bisogno, quindi un handshake Noise separato è
un vestigio — ereditato con ogni probabilità dalla stirpe degli "handshake Noise"
di WireGuard senza accorgersi che Sphinx aveva già fagocitato il compito. Questa
sezione registra tale decisione e specifica, normativamente, l'handshake che
Sphinx *è*, così che I-1 sia soddisfatto per specifica, non da un secondo
protocollo.

**La decisione, in un paragrafo.** `alpha` (SP-3, 32 B, X25519) è un *effimero del
client per-pacchetto*; ogni relay deriva il segreto del salto da `alpha` e dalla sua
chiave statica `onion` (GR-2 chiave 2). Questo è un Diffie-Hellman effimero–statico
per salto, forward-secret *a granularità d'epoca* (CH-6), con relay autenticato
tramite la firma Ed25519 del record di gossip — esattamente ciò di cui un circuito
ha bisogno e tutto ciò di cui ha bisogno. Un secondo handshake `Noise_XK` con stato
rifarebbe lo stesso DH, aggiungerebbe round-trip che una quota dispersa one-shot non
può permettersi, metterebbe un secondo formato sul filo sul collegamento che I-4
dovrebbe poi ripulire, e comprerebbe **una** sola proprietà che Sphinx non ha:
nascondere la chiave statica dell'*iniziatore*. Il client di circuito di ScrambNet
**non ha alcuna chiave statica** (è anonimo per costruzione), quindi quella
proprietà è vacua. `XK` autentica il macchinario per una chiave che non esiste.
Sostituire Sphinx con XK (più round-trip per meno), o usare XK per un canale
laterale (ogni flusso con stato client↔relay — gossip GR-6, probing GR-12/GR-13 — è
deliberatamente tunnellato *attraverso* Sphinx affinché il client resti senza nome,
quindi nessun canale di questo tipo vuole una sessione diretta) falliscono entrambi
all'esame. La specifica è migliore cancellando la riga.

```
  THE "HANDSHAKE" IS THE SPHINX HEADER. NOTHING ELSE EXISTS.

  client (nessuna chiave statica)  guard G       middle M          exit X
  ─────────────────────            ───────       ────────          ──────
   per pacchetto: scegli UN effimero x ; alpha_0 = x·B   (B = base X25519)
        │
        │  share packet  [ alpha_0 | beta | gamma | delta ]   (SP-3)
        │────────────────────────▶│
        │     G: s_G = DH(alpha_0, onion_G) ─► chiave hop; sbuccia uno strato beta
        │     G: alpha_1 = blind(alpha_0)   (ri-randomizzazione Sphinx)
        │                          │────────────────▶│
        │                          │  M: s_M = DH(alpha_1, onion_M) ─► chiave hop
        │                          │                  │──────────▶│
        │                          │                  │  X: s_X = DH(alpha_2, onion_X)
        ▼                          ▼                  ▼           ▼
   NESSUN RTT di handshake. NESSUN secondo formato sul filo. NESSUN messaggio Noise.
   Il DH è effimero(client)·statico(relay) a OGNI hop, trasportato interamente in `alpha`.

   Cosa avrebbe aggiunto Noise XK, e perché è cancellato:
      → e ; ← e,ee,s,es ; → s,se   (RTT extra, il relay nomina una sessione, e il
      terzo messaggio porta la statica dell'INIZIATORE che XK esiste per nascondere — che
      il nostro client senza chiavi non ha, quindi non c'è nulla da inviare né ragione di eseguirlo)
```

- **CH-1 (cancellare il vestigio).** La suite `0x01` **non** ha alcun handshake
  Noise; la riga della tabella delle suite nella Parte 0 è rimossa.
  Un'implementazione NON DEVE (MUST NOT) emettere, attendersi o negoziare alcun
  messaggio di handshake Noise su un circuito; un pacchetto che non è uno share
  packet della Parte 1 non fa parte di questo protocollo. *Attaccalo nominando
  un'operazione di circuito che l'header Sphinx non può eseguire — una revisione
  ostile ci ha provato e non ne ha trovata alcuna.*
- **CH-2 (l'handshake di circuito è l'header Sphinx).** L'accordo di chiave per salto
  DEVE (MUST) essere la costruzione Sphinx di SP-3/SP-4: per ogni salto `i`, il relay
  calcola `s_i = X25519(alpha_i, onion_i)` dove `alpha_i` è l'elemento di gruppo
  accecato che riceve e `onion_i` è la sua chiave statica (GR-2 chiave 2). Tutte le
  chiavi di salto (cifrario a flusso delle info di instradamento, il MAC `gamma`,
  l'AEAD `delta`) DEVONO (MUST) essere derivate da `s_i` tramite HKDF-BLAKE2s con
  etichette fisse distinte (`"sphinx-rho"`, `"sphinx-mu"`, `"sphinx-delta"` — byte
  esatti bloccati da vettori sotto roadmap 3.2). Non c'è altro accordo di chiave
  nello strato di circuito.
- **CH-3 (l'iniziatore è senza chiavi, per costruzione).** Un client di circuito
  NON DEVE (MUST NOT) possedere o presentare alcuna chiave statica a lungo termine
  sul percorso del circuito. Il suo unico segreto asimmetrico è lo scalare
  **effimero per-pacchetto** `x` dietro `alpha_0`, che DEVE (MUST) essere campionato
  fresco da un CSPRNG a ogni pacchetto (si applica roadmap 3.1 — la forward secrecy
  qui sotto è robusta esattamente quanto questo RNG) e distrutto dopo che il
  pacchetto è costruito. Senza una chiave statica del client, nessuno schema di
  occultamento dell'iniziatore ha qualcosa da nascondere; `XK`/`IK`/`KK` sono tutti
  inapplicabili al percorso del circuito (CH-7).
- **CH-4 (autenticazione statica del relay, senza una firma di handshake).** Un
  client DEVE (MUST) ottenere la chiave statica `onion` di ciascun relay *solo* da
  un record di gossip la cui firma Ed25519 (GR-2 chiave 7) sulla codifica canonica
  — che copre la chiave 2 — abbia verificato (GR-4). L'autenticazione del relay è
  **offline e trasferibile**: una volta sola, quando il record è validato, non
  interattivamente per ogni circuito. NON DEVE (MUST NOT) esserci una firma del
  relay nel circuito (sarebbe un selettore e un'impronta sul filo, I-4). Il limite
  onesto: un client autentica *la chiave*, non un'*identità al di là di quella
  firma* — il residuo sybil/eclipse risiede nella Parte 2 (OP-2, GR-19a/GR-20a), non
  qui.
- **CH-5 (rotazione della chiave statica — la finestra di esposizione `≤7-day`).**
  Un relay DEVE (MUST) ruotare la propria chiave statica `onion` almeno ogni `7`
  giorni (s), e DEVE (MUST) azzerare la metà privata di una chiave ritirata una
  volta trascorso il periodo di grazia per il traffico in transito; un relay che
  conserva vecchie statiche allarga la propria finestra di esposizione ed è non
  conforme. I client DEVONO (MUST) rifiutare un record la cui `expiry` superi
  `created + 7 days` (GR-2 chiave 6). Il tetto di rotazione è imposto a entrambe le
  estremità ed è il tetto sulla finestra di compromissione della statica (CH-6).
- **CH-5a (il divario `ee`, e la correzione che non è XK).** Una revisione ostile
  ha nominato l'unica proprietà che la cancellazione costa: poiché il DH del salto è
  effimero(client)·**statico**(relay), un avversario che registra il traffico di
  collegamento di un relay e poi ne sequestra la statica `onion` *entro l'epoca
  viva* può ricalcolare i segreti per salto di quell'epoca e recuperare la
  **collegabilità** di un salto per fino a 7 giorni di pacchetti registrati (mai
  contenuto — CH-6). Un `ee` Noise negherebbe anche quello. Questa è una vera
  regressione rispetto a un handshake *pienamente interattivo*, ma **non** è una
  ragione per tenere `XK` (il cui occultamento dell'iniziatore non la chiude) ed è
  chiudibile senza un handshake: un deployment che giudica la finestra troppo ampia
  DEVE (MUST) o (a) **accorciare la rotazione** sotto i 7 giorni (CH-5 è un tetto,
  non un obiettivo), oppure (b) aggiungere una **pre-chiave `ee` opzionale del
  relay** — una pre-chiave effimera a vita breve pubblicata nel record di gossip,
  mescolata nel segreto del salto a **zero** round-trip extra — ruotata e distrutta
  così che un sequestro tardivo della statica non frutti nulla per la sua durata. Il
  campo del record della pre-chiave e la sua rotazione appartengono a GR-2 se un
  deployment la adotta; CH-5a stabilisce solo che il divario è reale, limitato alla
  collegabilità, e chiudibile senza l'handshake cancellato.
- **CH-6 (l'enunciato di forward secrecy, con precisione).** `[claim-critical]` Un
  avversario che compromette la chiave privata `onion` **statica** del relay `R` al
  tempo `T` (e nient'altro — gli effimeri non hanno mai lasciato i client e sono
  stati distrutti, CH-3): (a) **il traffico passato è al sicuro attraverso le
  epoche** — i pacchetti il cui salto presso `R` ha usato una statica precedente,
  ruotata-e-distrutta, non sono decifrabili (la chiave è sparita, CH-5; il logaritmo
  discreto dell'effimero del client è sparito, CH-3); la forward secrecy è a
  granularità d'epoca, essendo la rotazione `≤7-day` quella granularità. (b)
  **Entro l'epoca viva, l'esposizione è la *collegabilità* di un salto, mai il
  contenuto** — per i pacchetti inviati mentre la statica sequestrata era viva,
  l'avversario ricalcola `s_i` per i salti presso `R` e sbuccia lo strato di `R`,
  apprendendo il predecessore/successore di `R`, cioè i metadati che un relay
  malevolo vede già. Non frutta **alcun** contenuto: incondizionatamente sotto `k`
  (I-2, Parte 7), e sopra `k` l'AEAD end-to-end è chiavata da un `kpair` simmetrico
  precondiviso senza alcuna trascrizione DH che la chiave sequestrata possa toccare
  (SP-1a). Una statica sequestrata compra *la collegabilità di un salto sui pacchetti
  di un'epoca* — esattamente la correlazione guard+exit che il progetto di
  dispersione/disgiunzione tratta già come *mitigata, non eliminata*; compromettere
  la statica non porta l'avversario più in là di quanto già faccia *gestire* quel
  relay.
- **CH-7 (l'occultamento dell'iniziatore non serve; il salto ha forma `N`, non `XK`).**
  `[claim-critical]` Il client ha bisogno della proprietà di XK di nascondere la
  statica dell'iniziatore? **No**, in modo dispositivo: il client non ha alcuna
  chiave statica d'iniziatore (CH-3), quindi la proprietà è vacua. Nel vocabolario
  di Noise il salto one-shot è un accordo unidirezionale, a iniziatore effimero e
  responder a statica nota — la forma di Noise `N` (`→ e, es`), non `XK`. Il
  circuito non usa alcun messaggio Noise letterale (CH-2: è Sphinx, che sussume
  questa forma); i due messaggi che XK aggiunge oltre `N` non portano nulla ed
  esistono solo per autenticare una chiave che non abbiamo. L'occultamento
  dell'iniziatore è già fornito in modo più forte da Sphinx (uniformità SP-4; il
  client non è mai un endpoint che un relay possa nominare, GR-12). Abbiamo
  sostituito l'occultamento dell'iniziatore di XK con *"l'iniziatore è anonimo e
  senza chiavi"*, che non ha bisogno di alcuno schema per nascondere ciò che non
  c'è.
- **CH-8 (le sessioni relay↔relay, se mai, sono fuori da questa parte e non sono
  `XK`).** Un futuro canale di controllo o peering che necessiti di una sessione con
  stato, bidirezionale, mutuamente autenticata tra due parti **nominate** (ad es.
  cifratura di collegamento relay-a-relay) è un documento separato e DEVE (MUST)
  comunque soddisfare I-4 (CH-9). Anche lì `XK` è sbagliato: le statiche di entrambi
  i relay sono **pubbliche** nei loro record di gossip, quindi non c'è nulla da
  nascondere e uno schema a statica già nota (`IK`/`KK`) è adatto. Questa sezione non
  specifica alcun canale di questo tipo; preclude solo il re-importare `XK` per
  riflesso.
- **CH-9 (I-4 non avendo alcun secondo formato sul filo).** `[claim-critical]` Lo
  strato di circuito non mette sul filo nulla se non share packet della Parte 1,
  ogni byte uniforme (SP-4). Non c'è **alcun** messaggio di handshake Noise da
  rendere uniforme — l'esito I-4 più pulito, raggiunto *non avendo* un secondo
  protocollo. Una trascrizione Noise XK ha una struttura riconoscibile (schema di
  lunghezza dei messaggi, campi di chiave pubblica `e`/`s`); tenere XK avrebbe
  *aggiunto* un requisito di offuscamento che la cancellazione rimuove. Qualsiasi
  futuro canale di sessione (CH-8) eredita questo obbligo nel proprio documento.

**Cosa non decide la sezione 5.** I parametri Sphinx stessi (gruppo, accecamento,
MAC, etichette HKDF esatte e concatenamento) sono il §3 e i vettori di roadmap 3.2;
CH-2 li referenzia. Post-quantistico: la suite `0x02` può sostituire il DH del salto
X25519 con un KEM PQ — la *forma* di forward secrecy di CH-6 è invariata (effimero +
rotazione statica `≤7-day`), cambia la primitiva, e il livello minimo di contenuto
I-2 è PQ-sicuro in ogni caso (SP-1a). Il canale relay↔relay (CH-8) e il campo
opzionale della pre-chiave `ee` (CH-5a) sono lasciati a parti future. CH-4 autentica
una *chiave che un record ha firmato*, non un'identità al di là di essa: il residuo
gossip/eclipse è della Parte 2 (OP-2).

## 6. Cosa questa parte non decide

La selezione dei percorsi e l'imposizione della disgiunzione (OP-1), i parametri di mix (OP-5),
la frammentazione (SP-8), l'economia delle esche (SP-9) sono aperti di proposito. Ciascuno ha una
issue numerata; discuti lì, con i numeri.
