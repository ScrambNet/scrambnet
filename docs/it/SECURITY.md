# Politica di sicurezza

ScrambNet è pre-alpha: una specifica e una proof-of-concept, non ancora un sistema con
cui proteggere segreti veri. Il contributo più prezioso che puoi dare è una
falla.

## Che cosa conta come segnalazione

- Un difetto nel **progetto**: un modo per leggere il contenuto sotto `k` quote catturate; un
  modo per collegare le quote di uno stesso messaggio (SP-7); un attacco di eclissi, sybil o
  che sconfigga la disgiunzione contro la scoperta o la selezione dei percorsi; qualunque cosa
  violi un invariante (I-1…I-4).
- Un difetto nel codice della **proof-of-concept** sotto `poc/`. Nota che la PoC
  usa deliberatamente aritmetica non a tempo costante e costruzioni giocattolo; sono
  non-obiettivi documentati, non segnalazioni. Una deviazione dalla specifica, o un
  difetto della specifica che il codice rivela, è una segnalazione.

## Come segnalare

- **Difetti di progetto e problemi della PoC non sensibili:** apri una issue pubblica.
  La discussione aperta è il senso di questo repository.
- **Qualunque cosa ritieni debba essere gestita prima in privato:** scrivi a
  `scrambnet@proton.me`. Cifra le segnalazioni sensibili con la chiave del progetto (vedi
  sotto). Puntiamo a confermare la ricezione **entro 7 giorni**; se a quel punto non hai
  ricevuto risposta, consideralo perso tra le tubature dello pseudonimato e segnalacelo di
  nuovo con un ping su una issue pubblica (senza il dettaglio sensibile) così ce ne accorgiamo.

Per favore non includere la tua identità legale in una segnalazione, a meno che tu non la voglia
pubblica. Le segnalazioni pseudonime sono benvenute e ricevono la stessa considerazione.

## Ambito

In ambito: la specifica in `docs/`, la PoC in `poc/`. Fuori ambito: la
sicurezza del dispositivo o dell'account di chi contribuisce; la piattaforma GitHub in sé; il
denial of service contro questo repository.

## Chiave del progetto

Una chiave PGP per `scrambnet@proton.me` è pubblicata nel repository come
[`scrambnet-pubkey.asc`](../../scrambnet-pubkey.asc). Cifra le segnalazioni sensibili con essa.

```
Fingerprint: E5B5 399D 751F 830D 35CB  5F4A 3087 9F3B F93D 44F7
Algorithm:   Ed25519 (sign) + Cv25519 (encrypt)
Created:     2026-11-11   Expires: 2028-11-10
```

Verifica il fingerprint rispetto a questo file (e, idealmente, rispetto a una seconda copia di
questo documento su un mirror diverso) prima di fidarti della chiave: il senso di pubblicarla
in-band *e* come file versionato è che le due devono coincidere.

Per usarla:

```
gpg --import scrambnet-pubkey.asc
gpg --fingerprint scrambnet@proton.me     # deve corrispondere alla riga qui sopra
gpg --encrypt --armor -r scrambnet@proton.me your-report.txt
```

**Rotazione (perché la chiave scade, invariante I-3).** La chiave scade tra due anni; non è
deliberatamente un singleton immortale. Prima che decada, la chiave successiva sarà pubblicata
qui e **firmata da questa** mentre questa è ancora valida, così il passaggio di consegne è
verificabile anziché un atto di fede. Se questa chiave dovesse mai essere persa o compromessa
prima della scadenza, un certificato di revoca (generato e conservato offline al momento della
creazione) sarà pubblicato qui e inviato a `keys.openpgp.org`, e una nuova chiave annunciata
nello stesso modo. Nessuna singola chiave di divulgazione è un punto di fiducia permanente.

## Divulgazione

Divulgazione coordinata per tutto ciò che potrebbe mettere in pericolo gli utenti di un futuro
dispiegamento; discussione pubblica immediata per tutto ciò che è a questo stadio pre-alpha,
dove non ci sono utenti da mettere in pericolo e l'obiettivo è rompere il progetto prima che
qualcuno ci faccia affidamento.
