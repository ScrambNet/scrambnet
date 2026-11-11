# Specifica ScrambNet — Parte 0: Convenzioni e struttura

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([en](../../en/spec/00-overview.md)).

**Stato: BOZZA (DRAFT).** Ogni numero in questa specifica è uno strawman da attaccare,
non una decisione. Attaccalo attraverso le issue; cambialo attraverso le PR.

## Come leggere questa specifica

- Le parole chiave **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, **MAY** vanno
  interpretate come descritto in RFC 2119.
- I requisiti sono numerati e stabili: `SP-n` (share packet, Parte 1), `CH-n`
  (handshake di circuito, Parte 1 §5), `GR-n`
  (gossip record, Parte 2), `PS-n` (selezione dei percorsi, Parte 3), `RZ-n`
  (rendezvous, Parte 6), `SA-n` (argomento di sicurezza, Parte 7), `ID-n`
  (dataset di inferenza, Parte 8). Issue e PR
  fanno riferimento ai requisiti per numero.
- I riferimenti `OP-n` puntano all'elenco dei problemi aperti in
  [threat-model.md](../threat-model.md#open-problems).
- Un'implementazione conforme implementa ogni MUST di ogni parte che dichiara.

## Invarianti di progetto

Questi quattro invarianti prevalgono su tutto il resto della specifica. Una proposta che ne viola
uno è respinta a prescindere da ciò che offre.

- **I-1 (Kerckhoffs).** La specifica è completa: un implementatore ostile con
  questo documento e nessun'altra conoscenza DEVE (MUST) poter costruire un nodo interoperabile e
  ugualmente sicuro. Se un dettaglio deve restare segreto perché il sistema funzioni, il
  dettaglio è un difetto.
- **I-2 (Livello minimo incondizionato).** La riservatezza del contenuto del messaggio contro un
  avversario che tiene meno di `k` quote NON DEVE (MUST NOT) dipendere da alcuna assunzione
  computazionale. I livelli sopra la dispersione POSSONO (MAY) essere computazionali; il livello minimo no.
- **I-3 (Nessun punto unico).** Nessun passo del protocollo può richiedere una parte, una chiave o un indirizzo
  che non possa essere sostituito da un surrogato non fidato. Questo include la scoperta, gli
  aggiornamenti e il bootstrap.
- **I-4 (Uniformità).** Tutto ciò che è osservabile sul filo da una parte priva delle
  chiavi rilevanti DEVE (MUST) essere indistinguibile da byte casuali uniformi di lunghezza
  fissa. Nessuna versione, flag o lunghezza in chiaro.

## Suite crittografica

Gli identificatori di suite sono di un byte, negoziati da nessuna parte: la suite è fissa per epoca
di rete e trasportata implicitamente dalla versione del pacchetto (I-4 vieta la negoziazione in
chiaro). Suite `0x01` (strawman):

| Ruolo | Primitiva |
|---|---|
| Handshake di circuito | Pattern Noise `XK`, `Noise_XK_25519_ChaChaPoly_BLAKE2s` |
| Scambio di chiavi | X25519 |
| AEAD | ChaCha20-Poly1305 |
| Hash / KDF / PRF | BLAKE2s / HKDF-BLAKE2s |
| Firme (gossip record) | Ed25519 |
| Formato pacchetto | Parametri Sphinx (Danezis–Goldberg 2009), Parte 1 |
| Dispersione | Schema di Shamir su GF(2^8), per byte |

Motivazione: veloce senza accelerazione hardware (un anonimato che gira solo su un laptop
nuovo non è per chi ne ha più bisogno), niente di esotico, ogni primitiva ha
un decennio di attacchi pubblici alle spalle. Nota post-quantistica: per I-2 il livello minimo di
riservatezza sopravvive già a un avversario quantistico; un handshake PQ (suite `0x02`) è un
aggiornamento pianificato, non un'emergenza.

## Convenzioni di codifica

- Tutti gli interi sono senza segno, in ordine di byte di rete (big-endian).
- Dimensioni fisse ovunque un campo attraversi il filo (I-4). I dati di lunghezza variabile
  esistono solo dentro payload protetti da AEAD, con prefisso di lunghezza di 2 byte.
- I gossip record usano CBOR canonico (RFC 8949 §4.2.1) — Parte 2.

## Parti

1. [Parte 1 — Share packet](01-share-packet.md): l'unità a dimensione fissa che porta
   una quota di un messaggio attraverso un circuito.
2. [Parte 2 — Gossip record](02-gossip-record.md): il descrittore di relay autofirmato
   e le regole per scambiarli e campionarli.
3. [Parte 3 — Costruzione dei circuiti e selezione dei percorsi](03-path-selection.md):
   obiettivi di disgiunzione, inferenza senza autodichiarazione, guardie e il
   fallback per reti piccole (OP-1).
4. [Parte 6 — Rendezvous e consegna](06-rendezvous.md): carte di contatto,
   dead drop dispersi e recupero per polling.
5. [Parte 7 — L'argomento di sicurezza per I-2](07-security-argument.md): la
   dimostrazione che una qualsiasi `k−1` quote sono indipendenti dal segreto, le
   due condizioni su cui poggia (casualità dei coefficienti, separazione delle
   chiavi) e un'affermazione onesta di ciò che non viene dimostrato.
6. [Parte 8 — Il dataset di inferenza](08-inference-dataset.md): come un client
   ottiene la mappa IP-to-AS e giurisdizione a grana grossa da cui la Parte 3
   inferisce, senza autorità — un artefatto riproducibile indirizzato per
   contenuto, un log di trasparenza senza permessi, trust-on-first-use dichiarato,
   e il tasso di errore che la mappa ammette e dà in pasto al simulatore
   (distribuzione OP-1, roadmap 2.3).

Pianificate, non ancora abbozzate: Parte 4 — trasporti camaleonte; Parte 5 — framing per la
modalità blackout.
