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
  DEVONO (MUST) essere depositate presso `n` drop distinti — SP-7 esteso all'archiviazione: nessun
  singolo drop tiene mai due quote di alcunché.
- **RZ-6.** Un deposito è un normale pacchetto della Parte 1 il cui circuito termina al
  drop. Il testo in chiaro dell'ultimo salto di `delta` è `box_id` (16 B) ‖ `slot`
  (1840 B); lo slot è il payload della quota della §4 della Parte 1 con il suo pad finale
  più corto di 16 byte. Il drop archivia lo slot sotto `box_id` alla lettera: non può
  leggere né la semantica del tag né il contenuto della quota (una quota < `k`, e SP-7
  rende le quote mutuamente non collegabili anche tra drop in collusione).
- **RZ-7.** I depositi sono fire-and-forget. Il drop NON DEVE (MUST NOT) emettere alcuna risposta
  che distingua successo, casella sconosciuta o casella piena (uniformità silenziosa, come
  GR-4). Regole di archiviazione: slot fissi di 1840 B, al massimo `64` (s) slot per casella,
  scadenza dello slot `7` giorni (s), sfratto con il più vecchio per primo.

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
  questo è il residuo per progetto, limitato da RZ-10 e attaccato in OP-9.
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
  limita il danno da flooding a una relazione; il prezzo del deposito (puzzle del
  client?) e l'economia dell'archiviazione del drop sono aperti (OP-9).

## 7. Derivazione delle chiavi e confini d'epoca

- **RZ-13 (un'unica disciplina di KDF).** Ogni chiave e identificatore che una coppia deriva da `kpair` DEVE (MUST) provenire da un'unica disciplina: HKDF-BLAKE2s con un'etichetta distinta che vincola lo scopo. In concreto: la chiave del contenuto è `HKDF(kpair, "e2e-content")` (SP-1a), la chiave del tag SP-7 è `HKDF(kpair, "tag")` e l'identificatore della casella è `box_id = HKDF(kpair, "box" ‖ drop_index ‖ epoch)` troncato a `BOX_ID_BYTES`. Nessun valore è derivato con BLAKE2s con chiave grezza su `kpair` né da una seconda costruzione — una bozza precedente derivava `box_id` in quel modo, e questo requisito la ritira. La separazione tramite etichette significa che la cattura o la debolezza di una chiave derivata non dice nulla a un avversario sulle sorelle, e l'intera relazione è governata da un'unica derivazione verificabile (l'argomento di separazione delle chiavi `SA-4`, Parte 7, dipende esattamente da questo).
- **RZ-13a (ampiezza di box_id).** `BOX_ID_BYTES = 16` (128 bit) (s). Un drop vede solo questo handle opaco, mai `kpair`; 128 bit sono sicuri rispetto alle collisioni per il numero di caselle `(pair, drop, epoch)` che qualunque rete realistica contiene e mantengono il payload `box_id ‖ slot` entro un unico `delta`.
- **RZ-14 (grazia al confine d'epoca UTC).** Poiché `box_id` ruota per epoca UTC (RZ-10), un mittente che deposita alle 23:59 (epoca `E`) e un destinatario che interroga alle 00:01 (epoca `E+1`) indirizzerebbero caselle diverse e il destinatario mancherebbe silenziosamente la posta. Per evitarlo, un destinatario che interroga entro una finestra di grazia da un confine d'epoca DEVE (MUST) interrogare le caselle di **entrambe** le epoche adiacenti: sempre l'epoca corrente, l'epoca precedente se si è entro la finestra di grazia dopo un confine, e l'epoca successiva se si è entro la finestra di grazia prima di uno. La finestra di grazia DEVE (MUST) superare lo scarto d'orologio mittente/destinatario nel caso peggiore più la latenza deposito-interrogazione (strawman `EPOCH_GRACE_SECONDS = 3600` (s)), e `SLOT_TTL_EPOCHS` (RZ-7) DEVE (MUST) mantenere una casella leggibile almeno un'epoca oltre la propria, così che la casella extra contenga ancora la posta. I mittenti depositano sotto l'unico `epoch_of(now)`; la grazia è una regola di lettura lato destinatario. Dimostrato in `poc/rendezvous.py` (`epochs_to_poll`, test `test_deposit_before_boundary_polled_after_boundary`).

## 8. Cosa questa parte non decide

La minimizzazione dei metadati di recupero (recupero più intelligente del polling, trucchi
in stile PIR e i loro costi reali), la semantica di cancellazione, il prezzo del deposito, gli incentivi del
drop (OP-9); la verifica dell'indipendenza dell'insieme dei drop (OP-1); il polling sulla
mesh durante il blackout (OP-6). Esistono issue numerate per ciascuno.
