# ScrambNet — Modello di minaccia

> Una rete che promette protezione totale sta mentendo, e chi corre rischi reali
> merita di sapere esattamente dove finisce l'ombrello. Questo documento è il contratto.

## Avversari ed esiti

| Avversario | Capacità | Risposta della rete | Esito |
|---|---|---|---|
| Osservatore locale (il tuo ISP, il Wi-Fi dell'ufficio) | Osservare il tuo traffico | Vede un normale flusso TLS verso un normale indirizzo | **Protetto** |
| Censore nazionale | Bloccare IP, confrontare impronte DPI, enumerare i ponti | Trasporti camaleonte; ponti distribuiti lungo il grafo sociale con livelli di fiducia in stile Lox | **Protetto** (una corsa agli armamenti, ma sostenibile) |
| Relay malevolo su un percorso | Osservare ciò che lo attraversa | Vede un salto di una quota; i pacchetti Sphinx sono identici ovunque | **Protetto** |
| Operatore di guardia *e* uscita di un circuito | Correlare i tempi di entrata/uscita | Quel circuito porta una quota, non il messaggio; le guardie sono stabili per mesi; la modalità paranoica aggiunge ritardi di mixing | **Mitigato** |
| Avversario a `k`-percorsi (tiene guardia+uscita su `k` degli `n` percorsi di quota simultaneamente) | Correlazione temporale completa più cattura delle quote | La selezione dei percorsi impone guardie, AS e giurisdizioni disgiunti, rendendo le `k` posizioni simultanee un problema di occupazione | **Mitigato** — questo è il rischio residuo per progetto; alza `n`, `k` a piacere |
| Avversario passivo globale (vede tutto il traffico ovunque) | Correlare ogni cosa | Modalità veloce: niente. Modalità paranoica: mixnet con ritardi e traffico di copertura | **Fuori modello (modalità veloce)** — dichiarato, come lo dichiara Tor |

## Cosa cambia la dispersione, con precisione

L'instradamento a cipolla classico fallisce in modo *catastrofico* su una singola estrazione sfortunata:
controlla guardia e uscita del singolo circuito e ottieni sia il collegamento (chi parla con chi) **sia**,
dove la cifratura propria della destinazione è assente o compromessa, il contenuto. Con la dispersione:

- Il **contenuto** è protetto incondizionatamente sotto le `k` quote catturate. Nessuna assunzione
  computazionale è in gioco. Questo livello minimo non può essere eroso da crittoanalisi o progresso quantistico.
- Il **collegamento** (metadati) su un singolo percorso di quota violato è comunque una perdita reale: l'
  avversario apprende che *un qualche* flusso è passato tra te e il raccoglitore di quote di una destinazione.
  La dispersione restringe ciò che un circuito tradisce; non lo annulla. Guardie stabili,
  selezione dei percorsi disgiunta per AS e mixing in modalità paranoica sono le mitigazioni.

## Assunzioni

1. Le reti sottostanti (ISP, IXP, cavi, cloud) sono ostili o compromesse.
2. Il progetto, il codice e tutti i documenti sono pienamente noti a ogni avversario (Kerckhoffs).
3. I relay sono gestiti da estranei; una frazione costante è malevola e in collusione.
4. Gli endpoint sono onesti: un telefono compromesso perde prima che il primo pacchetto parta.
   La sicurezza del dispositivo è fuori ambito, affermato senza pretese.
5. Gli utenti possono procurarsi il client. Build riproducibili più una specifica pubblica (chiunque può
   reimplementare da zero) sono la risposta all'avvelenamento dei binari e alla scomparsa
   di qualsiasi canale di distribuzione ufficiale.

## Non obiettivi

- Proteggere un utente il cui dispositivo è compromesso.
- Nascondere *che* una regione usa strumenti di aggiramento, nell'aggregato (modalità veloce).
- Moderazione dei contenuti a livello di rete. La rete trasporta pacchetti, non opinioni;
  protegge i dissidenti e i loro avversari con la stessa matematica. Un'infrastruttura
  è credibile solo se non può scegliere da che parte stare.

<a id="open-problems"></a>
## Problemi aperti

Segnati per l'attacco. Ogni problema si discute in **un** solo posto: una
singola [issue](https://github.com/ScrambNet/scrambnet/issues) per problema, con
il testo inglese e tutte le traduzioni nello stesso thread. Leggi il problema
qui nella tua lingua; discutilo lì, nell'unica issue, così nessuna discussione
si frammenta.

1. **Imposizione della disgiunzione.** Un primo meccanismo di selezione dei percorsi ora esiste in bozza
   ([spec Parte 3](spec/03-path-selection.md)) con uno strawman eseguibile in
   `poc/network_sim.py`; ciò che resta aperto è il nucleo duro: come fa un client a *verificare*
   che `n` percorsi non condividano un AS, una giurisdizione, un data center — usando solo il proprio campione
   di gossip e un insieme di dati di inferenza distribuito senza fiducia (I-3), contro relay che possono mentire
   su tutto tranne le loro firme?
2. **Resistenza a sybil ed eclipse** del campionamento gossip senza un allocatore centrale.
   Walking Onions assume un'istantanea firmata da un'autorità; noi abbiamo rimosso l'autorità. Cosa
   ne sostituisce la funzione anti-sybil — prova di chiavi a lungo termine? ponderazione sul grafo sociale?
   verifica della banda tramite probing randomizzato?
3. **Economia dei parametri.** Default per `n`, `k` per classe di traffico; quando l'IDA di Rabin
   (più economico, computazionale) sostituisce Shamir (incondizionato) per i dati di massa, e questo
   declassamento è mai accettabile per default?
4. **Correlazione temporale tra quote.** La non collegabilità del contenuto tra quote (SP-7) è risolta e
   implementata nel PoC; il *timing* no. `n` quote che entrano nella rete nel giro di
   millisecondi sono esse stesse un'impronta. Jitter, batching, quote esca: quanto costa ciascuna
   in latenza, e cosa compra davvero contro un avversario che osserva diverse uscite?
5. **Economia del traffico di copertura** in modalità paranoica su connessioni mobili a consumo.
6. **Indirizzamento in blackout.** Instradamento basato sull'identità su store-and-forward in mesh senza una
   DHT raggiungibile dall'interno del blackout.
7. **Bootstrap senza contatti** per la distribuzione dei ponti lungo il grafo sociale.
8. **Governance degli aggiornamenti.** Rilasci a firma multipla attraverso le giurisdizioni: quanti firmatari,
   come scelti, come sostituiti — senza creare il comitato che diventa il kill switch.
9. **Metadati ed economia dei dead drop.** Un drop vede i tempi di deposito e la cadenza di polling per
   una casella entro un'epoca (spec Parte 6). Distribuzioni di polling e costo delle esche su connessioni a
   consumo, semantica di cancellazione, prezzo del deposito contro il flooding, incentivi di archiviazione:
   quanto costa ciascuna difesa, e cosa fa trapelare ciascuna?
