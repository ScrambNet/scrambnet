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
  └─ AEAD end-to-end (chiavi del destinatario)      [computazionale]
       └─ split di Shamir: n quote, soglia k        [livello minimo incondizionato]
            └─ cifratura a cipolla per quota, circuito proprio, formato Sphinx
                 └─ trasporto camaleonte (Parte 4)
```

- **SP-1.** Il mittente DEVE (MUST) applicare la cifratura end-to-end *prima* della dispersione, e la
  dispersione DEVE (MUST) essere applicata al testo cifrato end-to-end. Con meno di `k`
  quote l'avversario non apprende nulla sul testo cifrato in modo incondizionato
  (Shamir); con `k` o più quote affronta ancora l'AEAD end-to-end. Il
  livello minimo incondizionato e la cintura computazionale si compongono; nessuno dei due sostituisce
  l'altro.
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
