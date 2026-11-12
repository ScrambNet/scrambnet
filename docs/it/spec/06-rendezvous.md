# Specifica ScrambNet — Parte 6: Rendezvous e consegna

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([en](../../en/spec/06-rendezvous.md)).

**Stato: BOZZA (DRAFT).** Valori strawman contrassegnati con `(s)`. Le questioni di metadati di recupero ed
economia che questa parte apre sono OP-9 e deliberatamente irrisolte.

## 1. Ambito

Come un messaggio raggiunge qualcuno che non è — e non deve essere — nella mappa di nessuno.
I destinatari non hanno posizioni di rete; hanno **carte di contatto** e
**dead drop**. Il mittente deposita le quote; il destinatario le recupera da
dietro i propri circuiti. Nessuno consegna mai *a* una persona.

## 2. Nessuno fa gossip sulle persone

- **RZ-1.** Un destinatario NON DEVE (MUST NOT) essere individuabile tramite gossip. Solo i relay
  pubblicano record (Parte 2). Qualunque cosa renda interrogabile la partecipazione di una persona
  è un difetto (cfr. L0: non c'è un elenco di utenti perché non c'è un momento in cui un utente si
  registra).

## 3. Carte di contatto

- **RZ-2.** Una carta di contatto è **per relazione**: la carta data al
  corrispondente A DEVE (MUST) essere non collegabile alla carta data al corrispondente B —
  chiave di coppia distinta, caselle distinte. La compromissione di un corrispondente espone
  una relazione, non il mondo del destinatario.
- **RZ-3.** Contenuto della carta (CBOR canonico, come la Parte 2):

| Chiave | Nome | Tipo | Note |
|---|---|---|---|
| 0 | `v` | uint | versione del formato, `1` |
| 1 | `id` | bytes(32) | chiave di identità Ed25519 del destinatario |
| 2 | `kpair` | bytes(32) | segreto di coppia; tutto ciò che segue ne deriva |
| 3 | `drops` | array | `d` record di relay incorporati (record completi della Parte 2) |
| 4 | `validity` | uint | scadenza unix; DOVREBBE (SHOULD) seguire la scadenza dei record incorporati |

  Derivazioni (HKDF-BLAKE2s, suite 0x01): la chiave del tag SP-7 per questa coppia è
  `K_tag = HKDF(kpair, "tag")`; gli identificatori delle caselle sono
  `box_id(drop, epoch) = PRF(kpair, "box" ‖ drop_index ‖ epoch)` troncati a
  16 byte, con `epoch = floor(unix_time / 86400)` (s). L'indice del drop DEVE (MUST)
  entrare nella derivazione: con un unico id per epoca, due drop in collusione potrebbero
  collegare le caselle della coppia entro quell'epoca.
- **RZ-4.** Le carte viaggiano fuori banda (codice QR, stringa stampata, un amico) o
  su un canale ScrambNet esistente. Un contatto è il minimo, come in GR-10.

## 4. Drop e deposito

- **RZ-5.** L'insieme dei drop contiene `d = n = 4` (s) relay, scelti dal
  *destinatario*, che DOVREBBERO (SHOULD) essere mutuamente indipendenti nello stesso senso che la selezione
  dei percorsi richiede (OP-1 si applica anche ai drop). Le `n` quote di un messaggio
  DEVONO (MUST) essere depositate presso `n` drop distinti — SP-7 esteso allo storage: nessun
  singolo drop tiene mai due quote di alcunché.
- **RZ-6.** Un deposito è un normale pacchetto della Parte 1 il cui circuito termina al
  drop. Il testo in chiaro dell'ultimo salto di `delta` è `box_id` (16 B) ‖ `slot`
  (1840 B); lo slot è il payload della quota della §4 della Parte 1 con il suo pad finale
  più corto di 16 byte. Il drop archivia lo slot sotto `box_id` alla lettera: non può
  leggere né la semantica del tag né il contenuto della quota (una quota < `k`, e SP-7
  rende le quote mutuamente non collegabili anche tra drop in collusione).
- **RZ-7.** I depositi sono fire-and-forget. Il drop NON DEVE (MUST NOT) emettere alcuna risposta
  che distingua successo, casella sconosciuta o casella piena (uniformità silenziosa, come
  GR-4). Regole di storage: slot fissi di 1840 B, al massimo `64` (s) slot per casella,
  scadenza dello slot `7` giorni (s), sfratto con il più vecchio per primo. Il limite delimita lo
  **storage**, non la **consegna** sotto flooding — vedi RZ-15.

## 5. Recupero

- **RZ-8.** Il destinatario interroga ciascuno dei propri drop sui propri circuiti.
  La conoscenza di `box_id` autorizza il recupero (è derivata da un segreto e
  non indovinabile); gli slot vengono cancellati alla scadenza, non al prelievo (la semantica di
  cancellazione-al-prelievo è territorio di OP-9: un avversario che ruba un `box_id` non deve
  poter divorare la posta in silenzio).
- **RZ-9 (disciplina di polling).** Il polling DEVE (MUST) seguire un programma indipendente dall'
  attività dell'utente: cadenza fissa con jitter (strawman: ogni `15` minuti ±
  uniforme `5`), proseguendo quando l'utente è inattivo, con polling esca verso id di
  casella esca alla stessa cadenza. Una risposta di recupero è sempre esattamente `b = 8`
  (s) slot, con padding di slot fittizi indistinguibili da quelli reali. Il
  drop apprende la cadenza di polling di una casella e i tempi di deposito entro un'epoca —
  questo è il residuo per progetto, limitato da RZ-10 e ora quantificato in RZ-16:
  l'indipendenza del programma DEVE (MUST) essere stretta (RZ-16a) e il costo in esche/byte è
  quantificato (RZ-16b).
- **RZ-10 (epoche).** `box_id` ruota per epoca. Un drop NON DEVE (MUST NOT) poter
  collegare le caselle della stessa coppia attraverso le epoche; nulla nel protocollo di recupero
  può portare un valore stabile attraverso le epoche.

## 6. Rinnovo e guasto

- **RZ-11.** Una carta è rinnovata in banda: il destinatario deposita la carta successiva
  (nuovo `kpair`, nuovi drop) nelle caselle esistenti della coppia come un normale
  messaggio, prima che `validity` scada. Se ogni drop di una coppia è morto o la
  carta è scaduta, la coppia si riscambia fuori banda: un contatto è il
  minimo, di nuovo.
- **RZ-12.** Chiunque possieda una carta può riempirne le caselle. Il limite per casella (RZ-7)
  delimita il danno da flooding **allo storage di una relazione**, ma non la **consegna** di quella
  relazione — RZ-15 mostra che un flooder di classe telefono nega il recupero entro un periodo di
  polling, e che quel prezzo del deposito (puzzle del client) non può chiudere il divario; la difesa
  sufficiente (ammissione del deposito) è un residuo OP-9 irrisolto. Gli incentivi allo storage del
  drop restano aperti (OP-9).

## 7. Derivazione delle chiavi e confini d'epoca

- **RZ-13 (un'unica disciplina di KDF).** Ogni chiave e identificatore che una coppia deriva da `kpair` DEVE (MUST) provenire da un'unica disciplina: HKDF-BLAKE2s con un'etichetta distinta che vincola lo scopo. In concreto: la chiave del contenuto è `HKDF(kpair, "e2e-content")` (SP-1a), la chiave del tag SP-7 è `HKDF(kpair, "tag")` e l'identificatore della casella è `box_id = HKDF(kpair, "box" ‖ drop_index ‖ epoch)` troncato a `BOX_ID_BYTES`. Nessun valore è derivato con BLAKE2s con chiave grezza su `kpair` né da una seconda costruzione — una bozza precedente derivava `box_id` in quel modo, e questo requisito la ritira. La separazione tramite etichette significa che la cattura o la debolezza di una chiave derivata non dice nulla a un avversario sulle sorelle, e l'intera relazione è governata da un'unica derivazione verificabile (l'argomento di separazione delle chiavi `SA-4`, Parte 7, dipende esattamente da questo).
- **RZ-13a (ampiezza di box_id).** `BOX_ID_BYTES = 16` (128 bit) (s). Un drop vede solo questo handle opaco, mai `kpair`; 128 bit sono sicuri rispetto alle collisioni per il numero di caselle `(pair, drop, epoch)` che qualunque rete realistica contiene e mantengono il payload `box_id ‖ slot` entro un unico `delta`.
- **RZ-14 (grazia al confine d'epoca UTC).** Poiché `box_id` ruota per epoca UTC (RZ-10), un mittente che deposita alle 23:59 (epoca `E`) e un destinatario che interroga alle 00:01 (epoca `E+1`) indirizzerebbero caselle diverse e il destinatario mancherebbe silenziosamente la posta. Per evitarlo, un destinatario che interroga entro una finestra di grazia da un confine d'epoca DEVE (MUST) interrogare le caselle di **entrambe** le epoche adiacenti: sempre l'epoca corrente, l'epoca precedente se si è entro la finestra di grazia dopo un confine, e l'epoca successiva se si è entro la finestra di grazia prima di uno. La finestra di grazia DEVE (MUST) superare lo scarto d'orologio mittente/destinatario nel caso peggiore più la latenza deposito-interrogazione (strawman `EPOCH_GRACE_SECONDS = 3600` (s)), e `SLOT_TTL_EPOCHS` (RZ-7) DEVE (MUST) mantenere una casella leggibile almeno un'epoca oltre la propria, così che la casella extra contenga ancora la posta. I mittenti depositano sotto l'unico `epoch_of(now)`; la grazia è una regola di lettura lato destinatario. Dimostrato in `poc/rendezvous.py` (`epochs_to_poll`, test `test_deposit_before_boundary_polled_after_boundary`).

## 8. Economia e metadati di recupero, con un prezzo (OP-9)

L'item 4.3 della roadmap ha messo numeri alle due questioni OP-9 che RZ-7/RZ-9 avevano lasciato
aperte — il flooding e i metadati di polling — con il simulatore `poc/dropecon_sim.py`
(`test_dropecon_sim.py` fissa le cifre). Il risultato onesto è che una delle due difese che il
progetto sperava **non** regge; il §9 la porta come residuo dichiarato anziché nasconderla.

- **RZ-15 (flooding: né il limite né un puzzle difendono la *consegna*; è un
  residuo dichiarato). [normativo]** Il limite per casella di RZ-7 delimita lo **storage** a
  `BOX_CAP × SLOT_BYTES = 115 KiB` per casella `(pair, drop, epoch)`, un tetto
  indipendente dal budget dell'attaccante. **Non** delimita la **consegna**. Poiché un
  polling restituisce solo gli `B_SLOTS = 8` slot sopravvissuti più vecchi (RZ-8) e i depositi
  sfrattano il più vecchio per primo (RZ-7), un attaccante che seppellisce uno slot onesto fresco dietro
  `≥ 8` slot spazzatura più recenti ne nega il recupero **senza nemmeno raggiungere il limite** —
  e il simulatore mostra che un flooder di **classe telefono** (`2 × 10⁶ H/s`) fa questo in
  `~17 s`, ben dentro un singolo polling `POLL_PERIOD = 900 s`, a ogni durezza di puzzle
  utilizzabile. Un puzzle proof-of-work lato deposito non salva la situazione: nessuna durezza
  `z` è al tempo stesso deterrente per le botnet e sostenibile dal telefono — il divario ARM-vs-GPU è
  `~25 000×`, quindi a `z = 20` (l'ultimo punto sostenibile dal telefono, `0.52 s/deposito`)
  una singola GPU riempie comunque di nuovo una casella `~1.7 × 10⁸` volte/ora, mentre forzare una GPU
  a `1 s/deposito` costa al telefono `~9.5 ore/deposito`. Un puzzle PUÒ (MAY) essere richiesto
  a bassa durezza (`z ≤ 20` (s)) come banale rallentatore del riempimento, ma **non** vi si
  fa affidamento. La dispersione `n = 4, k = 3` alza l'asticella solo al flooding
  `≥ n − k + 1 = 2` dei drop di una coppia in una volta. **Il flooding della consegna quindi non ha
  alcuna difesa sufficiente in questa parte:** serve un controllo di **ammissione** del deposito
  che il progetto non ha ancora progettato (una direzione candidata, non una decisione: un
  token di ammissione per-relazione derivato dalla carta, così che solo un detentore della carta
  depositi e solo a un tasso limitato). Finché ciò non esiste, il flooding della consegna è un
  residuo OP-9 dichiarato, quantificato nel §9.

- **RZ-16 (metadati di polling: due leak, due manopole). [normativo]** L'osservazione
  entro un'epoca di un drop profilatore (limitata attraverso le epoche da RZ-10) si scompone
  in due leak con due difese indipendenti, e il simulatore mette un prezzo a entrambe.
  - **RZ-16a (leak del pattern di attività — difeso gratis dall'indipendenza stretta).
    [normativo]** Se il destinatario *ha reagito* a un deposito è l'unico leak
    che identifica l'utente, ed è difeso rendendo il programma di polling
    **strettamente indipendente** dai depositi e dall'attività dell'utente (RZ-9): il programma
    NON DEVE (MUST NOT) essere anticipato, innescato o rimodellato da un deposito o da un evento dell'app, così
    che la latenza `deposito → polling-successivo` resti alla media da paradosso dell'ispezione propria
    del programma (`≈ 467 s` per `POLL_PERIOD = 900, POLL_JITTER = 300`)
    e sia non correlata con il tempo di deposito. Un drop rileva una violazione non per la
    media (troppo grossolana — un programma semi-reattivo risulta comunque quasi indipendente sulla
    media) ma per la **coda** `P[latency < 60 s]`, che il simulatore mostra
    salire dal rumore all'indipendenza fino a un segnale chiaro per una frazione reattiva del `5 %`.
    Questa difesa è **obbligatoria e gratuita in byte**.
  - **RZ-16b (leak su quale casella — difeso da esche a un reale costo in byte). [normativo]**
    Quale delle diverse caselle detenute sia quella reale del destinatario è difeso da polling
    esca a un moltiplicatore `r` (s: `r = 1`), una domanda a cui l'incollegabilità di RZ-2/RZ-10
    già risponde in larga parte, quindi la privacy marginale per byte è bassa. Ogni polling
    viaggia su Sphinx — `B_SLOTS + 1 = 9` pacchetti di `2048 B` sul salto d'ingresso contabilizzato,
    `~18.4 KiB`, non i byte grezzi dello slot — quindi attraverso `d = 4` drop alla
    cadenza di RZ-9 il costo fisso è `~212 MB/mese` a `r = 0` (prima del
    lato deposito/invio) e `~425 MB/mese` al default `r = 1`. `r = 0` è una
    modalità a basso consumo di dati esplicita. Dimostrato in `poc/dropecon_sim.py` (Scenario B).

## 9. Cosa questa parte non decide (il residuo OP-9 dichiarato)

La minimizzazione dei metadati di recupero (recupero più intelligente del polling, trucchi
in stile PIR e i loro costi reali), la semantica di cancellazione e gli incentivi del drop (perché
un relay archivia il rumore di uno sconosciuto) restano genuinamente aperti (OP-9); la verifica
dell'indipendenza dell'insieme dei drop (OP-1); il polling sulla mesh durante il blackout (OP-6).
Esistono issue numerate per ciascuno. Tre risultati del §8 sono portati apertamente come
residui dichiarati, con i numeri che li provano:

- **Il flooding della consegna non ha alcuna difesa sufficiente qui.** Né il limite di RZ-7
  (solo-storage) né un puzzle proof-of-work (non esiste durezza sostenibile dal telefono e
  deterrente per le botnet — il divario ARM-vs-GPU di `~25 000×`) ferma un attaccante che
  seppellisce la posta onesta oltre la finestra di recupero a 8 slot in `~17 s`, ben
  dentro un polling da 900 s, con hardware di classe telefono (RZ-15). Serve un controllo di
  ammissione che il progetto non ha ancora costruito; fino ad allora è un residuo dichiarato.
- **Il piano di profilazione entro un'epoca è reale.** L'indipendenza stretta (RZ-16a)
  rimuove l'unico leak che identifica l'utente, ma un drop apprende comunque la cadenza pubblica
  di RZ-9 e i tempi di deposito nelle caselle che detiene; le esche raggiungono solo la
  domanda su quale casella (RZ-16b). Un drop multi-casella in collusione può anche correlare i
  timestamp di *deposito* attraverso le sue caselle anche sotto perfetta indipendenza del polling —
  l'incollegabilità di RZ-2/RZ-10 copre gli identificatori, non il *timing* di deposito.
- **La baseline di polling di RZ-9 è pesante per il target mobile.** Anche con le esche
  disattivate (`r = 0`), il polling obbligatorio a cadenza fissa attraverso `d = 4` drop costa
  `~212 MB/mese` (RZ-16b) — il prezzo della difesa dal pattern di attività, pagato in
  byte, prima che sia inviato alcun messaggio.
