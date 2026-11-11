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
  sotto). Puntiamo a confermare la ricezione in tempi ragionevoli; tieni conto di un
  progetto pseudonimo e portato avanti da volontari.

Per favore non includere la tua identità legale in una segnalazione, a meno che tu non la voglia
pubblica. Le segnalazioni pseudonime sono benvenute e ricevono la stessa considerazione.

## Ambito

In ambito: la specifica in `docs/`, la PoC in `poc/`. Fuori ambito: la
sicurezza del dispositivo o dell'account di chi contribuisce; la piattaforma GitHub in sé; il
denial of service contro questo repository.

## Chiave del progetto

Una chiave PGP per `scrambnet@proton.me` per le segnalazioni cifrate sarà pubblicata
qui e nel repository. Finché una chiave firmata non è elencata in questo file, tratta
l'email come confidenziale-ma-non-autenticata e conserva i dettagli più sensibili
per un canale che puoi verificare.

## Divulgazione

Divulgazione coordinata per tutto ciò che potrebbe mettere in pericolo gli utenti di un futuro
dispiegamento; discussione pubblica immediata per tutto ciò che è a questo stadio pre-alpha,
dove non ci sono utenti da mettere in pericolo e l'obiettivo è rompere il progetto prima che
qualcuno ci faccia affidamento.
