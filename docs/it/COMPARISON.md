# Come si colloca ScrambNet

Un posizionamento onesto rispetto ai sistemi che un revisore nominerebbe giustamente per primi.
Questo documento dichiara ciò che ScrambNet fa *in modo diverso* e — più importante ancora —
ciò che fa *peggio*. Se una cella qui sotto è sbagliata, apri una issue: sbagliare qui
costa più che sbagliare in qualunque altra parte del repository.

## L'unica vera differenza

Ogni sistema di anonimato in uso protegge il **contenuto** dei messaggi con
un'ipotesi computazionale: rompi la cifratura (oggi o con un futuro computer
quantistico) e il contenuto diventa leggibile. Il livello minimo del contenuto di ScrambNet è
**informazionalmente sicuro**: al di sotto di `k` quote catturate non c'è alcun testo cifrato da
rompere, perché il contenuto non è presente in nessun insieme di `k−1` quote — una proprietà del
segreto condiviso di Shamir, non della robustezza di una cifratura (invariante I-2). È
questa l'intera scommessa. Tutto il resto, qui, è arte preesistente, composta.

Questa differenza riguarda **solo il contenuto**. Per la **collegabilità** (chi parla con chi,
i metadati) ScrambNet è nella stessa dura battaglia di tutti gli altri, e non fa
alcuna promessa informazionale lì, in modalità veloce.

## A confronto

| | **ScrambNet** | **Tor** | **Nym / Loopix** | **Briar** |
|---|---|---|---|---|
| Uso principale | Messaggistica (asincrona, a dead-drop) | Navigazione a bassa latenza | Messaggistica (mixnet) | Messaggistica, P2P |
| Riservatezza del contenuto | **Incondizionata sotto `k` quote** | Computazionale (TLS + onion) | Computazionale | Computazionale |
| Difesa dalla collegabilità | Circuiti dispersi + mix (paranoica) | Circuiti onion | Mixnet di Poisson (forte) | Onion + grafo dei contatti |
| Directory / scoperta | **Nessuna** — gossip + campione verificabile | ~9 directory authority | Validatori / nym-api | Introduzione tramite contatti |
| Avversario globale passivo | Fuori modello (veloce) / mix (paranoica) | Fuori modello | **Nel modello** (mixnet) | Parziale |
| Blackout / offline | Mesh locale, store-and-forward | No | No | **Sì** (Bluetooth/Wi-Fi) |
| Strato di incentivi | Nessuno (volontariato) | Volontariato | **Token** | Volontariato |
| Maturità | **Spec pre-alpha + PoC** | Produzione, 20+ anni | Produzione | Produzione |

## Dove ScrambNet è indietro, detto chiaramente

- **Maturità.** Tor, Nym e Briar sono dispiegati, sottoposti ad audit e trasportano traffico
  reale oggi. ScrambNet è una specifica e una proof-of-concept in Python.
  Nessuno dovrebbe ancora instradarci un segreto vero, e il repository lo dichiara.
- **Progetto del mixnet.** Nym/Loopix hanno un progetto di mix di Poisson rigoroso e pubblicato
  con un modello dell'avversario globale passivo. La modalità paranoica di ScrambNet è un
  segnaposto (OP-5) finché qualcuno non svolge quel lavoro anche qui.
- **Metadati di collegabilità.** Lo schema di recupero a dead-drop rivela la cadenza di polling
  verso un drop all'interno di un'epoca (OP-9) — un costo che il mixing continuo di Nym
  ammortizza più a fondo.
- **Banda.** Il livello minimo incondizionato costa `×n` di banda (×4 nello strawman). Tor
  costa ×1 per la sua garanzia di contenuto più debole. Questo è il prezzo
  della scommessa, non un difetto, ma è un prezzo reale (OP-3).
- **Incentivi.** Nym paga i relay; ScrambNet chiede volontari, cosa che storicamente
  limita la crescita.

## Perché costruirla comunque

Perché la garanzia di contenuto di ogni altro sistema ha una data di scadenza scritta nelle
ipotesi del 2003–2017, e «raccogli ora, decifra dopo» è una strategia reale
d'avversario contro dissidenti i cui messaggi devono restare illeggibili per
decenni. Al di sotto di `k` quote il livello minimo del contenuto non può essere eroso affatto dal
progresso crittoanalitico o quantistico — non c'è nulla lì da rompere. A partire dalle `k` quote
la cintura è un normale AEAD, e ScrambNet la alimenta con un segreto *simmetrico* precondiviso,
senza alcun accordo asimmetrico nel percorso del contenuto (spec SP-1a), così che «raccogli ora,
decifra dopo» è sconfitto anche in *quel* regime: non c'è alcuno scambio di chiavi registrato che
un futuro computer quantistico possa rompere, solo un segreto che le parti hanno già condiviso. Il
residuo onesto è lo scambio fuori banda una tantum che consegna quel segreto condiviso. Questo vale
una bolletta di banda `×n` e il lavoro di costruire tutto il resto. Se
quella scommessa è sbagliata, il modo più rapido di scoprirlo è attaccarla qui.
