# Contribuire a ScrambNet

Il progetto è alla fase di pre-specifica. I contributi più preziosi in questo momento,
in ordine:

1. **Attacca il modello di minaccia.** Apri una issue contro qualsiasi affermazione in
   [docs/threat-model.md](threat-model.md), specialmente l'elenco dei problemi aperti.
2. **Proponi testo di specifica.** PR contro `docs/` — in stile RFC, un meccanismo per PR.
3. **Traduci.** I README esistono in sei lingue; `docs/` è finora solo in inglese.
   Traduzioni e correzioni da parte di madrelingua sono contributi di prima classe.
4. **Segnala lavori precedenti.** Se qualcosa qui reinventa la ruota, nomina la ruota. La
   filosofia di progetto è comporre lavoro pubblicato e attaccato, mai inventare dove basta
   una citazione.

## Come lavoriamo

- Un argomento per issue. I dibattiti di progettazione vivono nelle issue, le decisioni
  vengono registrate in `docs/`.
- L'inglese è la lingua canonica di `docs/`; se modifichi un README in una lingua,
  o aggiorni gli altri oppure dichiari nella PR che ora sono obsoleti.
- Niente codice finché il modello di minaccia e la specifica di protocollo non si assestano.
  Quando il codice partirà: un unico client di riferimento piccolo, noioso e mobile-first.

## Politica di pseudonimia

I nomi reali non sono richiesti e non lo saranno mai. I contributi pseudonimi e anonimi
sono di prima classe. Non c'è alcun CLA; contribuendo rilasci il tuo contributo alla
documentazione sotto [CC0 1.0](../../LICENSE).

Se il tuo modello di minaccia lo richiede, proteggiti:

- Usa l'indirizzo noreply della tua forge nei commit:
  `git config user.email "USERNAME@users.noreply.github.com"`
- Committa in UTC così il tuo fuso orario non trapela:
  `git config alias.ci '!TZ=UTC git commit'`
- Non firmare i commit con una chiave legata alla tua identità legale; se firmi, usa una
  chiave creata solo per questo pseudonimo.
- Non riutilizzare soprannomi usati altrove, e ricorda che lo stile della prosa è
  un'impronta digitale.

## Neutralità

Questa rete trasporta pacchetti, non opinioni. Protegge i dissidenti e i loro avversari
con la stessa matematica; gli avversari politici non sono nemici. Le proposte che
porterebbero la rete a favorire o sfavorire particolari punti di vista, origini o
destinazioni saranno respinte a prescindere dal punto di vista — quella neutralità è
l'argomento di sicurezza del progetto tanto quanto la sua etica.
