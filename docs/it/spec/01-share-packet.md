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

## 5. Cosa questa parte non decide

La selezione dei percorsi e l'imposizione della disgiunzione (OP-1), i parametri di mix (OP-5),
la frammentazione (SP-8), l'economia delle esche (SP-9) sono aperti di proposito. Ciascuno ha una
issue numerata; discuti lì, con i numeri.
