# Specifica ScrambNet — Parte 5: Blackout e diversità di collegamento in mesh mista

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([en](../../en/spec/05-blackout-mesh.md)).

**Stato: BOZZA (DRAFT), ed è un rischio di ricerca dichiarato.** Questo è il più
grande design non scritto del progetto, e questa parte restituisce — per quanto la
roadmap lo permetta — un risultato *parziale*: un solido modello di rete mista e
un'idea genuinamente portante (dispersione su gateway indipendenti, come proprietà di
*disponibilità*), avvolti attorno a residui che nomina a piena forza e non pretende di
chiudere. Non impegna **alcuno stack mesh concreto** e non fa **alcuna affermazione di
anonimato per lo strato radio**; è una parte di postura-e-modello, esattamente come lo
è la Parte 4. I valori strawman sono contrassegnati con `(s)`.

Leggi prima il §3 (la valutazione del realismo) — è la spina dorsale, e dice la cosa
molto più grande che questa parte rifiuta di affermare. L'unica affermazione positiva
portante è ristretta: *la dispersione su gateway indipendenti estende I-3 all'uscita
dal vicinato fisico come proprietà di disponibilità, e a nulla nella mesh è consentito
muovere il pavimento del contenuto I-2* (BL-16) — la mesh è tanto indipendente dal
pavimento quanto la Parte 4 tiene il trasporto (CT-16). Questa parte è il piolo L4 a
cui la CT-18a della Parte 4 passa la mano, e resta coerente con quella concessione
(BL-17): quando non c'è alcun vicino, nulla è consegnato.

## 1. Il modello di rete mista e i ruoli

- **BL-1 (la mesh è uno strato, non una modalità). [normativo]** Un nodo conforme DEVE
  (MUST) trattare i collegamenti radio locali e i collegamenti internet come tipi di
  collegamento coesistenti *in ogni momento*, non come una "modalità blackout" in cui
  si entra alla perdita dell'infrastruttura. Perdere l'uplink DEVE (MUST) essere un
  cambiamento di *rotta* (un salto in più verso un gateway), mai un cambiamento di
  protocollo, identità o postura di sicurezza. Un design con una "modalità mesh"
  distinta che l'utente commuta è non conforme a questa inquadratura (OP-6).
- **BL-2 (ruoli, per realtà hardware). [normativo]** Un nodo DEVE (MUST)
  auto-classificarsi, dalla sua effettiva capacità radio, come esattamente uno tra:
  **foglia** (un telefono: concorrenza STA+AP o Wi-Fi Aware, vincolato alla batteria,
  senza root), **dorsale** (un PC/SBC a doppia radio che esegue vero 802.11s,
  store-and-forward continuo), o **gateway** (una dorsale o una foglia che attualmente
  detiene un uplink e lo annuncia). I ruoli sono derivati dalla capacità e variabili
  nel tempo — un gateway che perde il suo uplink diventa dorsale o foglia — mai un
  livello fisso.
- **BL-3 (l'opt-in è una precondizione di qualunque collegamento radio). [normativo]**
  Un nodo NON DEVE (MUST NOT) originare, ritrasmettere o fare da gateway ad alcun
  traffico su un collegamento radio locale senza un opt-in preventivo, esplicito e
  informato *specifico alla partecipazione alla mesh* e distinto da qualunque opt-in di
  relay, perché la visibilità della mesh è fisica (BL-18) e porta un'identità a livello
  radio che l'overlay non può ruotare (BL-18a). Il silenzio, o l'ereditare l'opt-in di
  relay, è non conforme.
- **BL-4 (budget onesto di batteria e di archiviazione). [normativo]** Un nodo foglia
  DEVE (MUST) far emergere, prima dell'opt-in, il costo di batteria e di archiviazione
  che effettivamente sosterrà (strawman: una quota di store-and-forward delimitata e
  una schedulazione radio a ciclo di servizio), e NON DEVE (MUST NOT) promettere una
  disponibilità continua di grado-dorsale che non può sostenere a batteria. Il budget
  concreto è aperto in OP-6 e DEVE (MUST) essere dichiarato, non indovinato (BL-20).

## 2. Dispersione su gateway indipendenti, indirizzamento, trasporto e mixing

### 2.1 Dispersione su gateway indipendenti (l'idea portante, come disponibilità)

- **BL-5 (le quote DOVREBBERO uscire attraverso gateway indipendenti). [normativo]**
  Quando le `n` quote (SP-2) di un messaggio attraversano la mesh locale verso un
  uplink, un client conforme DOVREBBE (SHOULD) instradarle così che escano attraverso
  gateway *diversi*, estendendo I-3 (nessun punto singolo) all'uscita dal vicinato
  fisico. Un gateway che porta `k` delle `n` quote è un punto singolo e DEVE (MUST)
  essere evitato dove ≥2 gateway indipendenti-*stimati* (BL-6) sono raggiungibili. In
  un blackout profondo la stima di indipendenza può essere vuota (BL-6); BL-5 allora
  degrada a BL-7 **per default**, non come caso limite. Il beneficio qui affermato è
  **disponibilità**, non non-osservabilità (§3): nessun guasto, blocco o cattura sybil
  di un singolo gateway uccide la consegna — questo è il verdetto CT-15 per i trasporti,
  nello spazio mesh.
- **BL-6 (cosa può significare "indipendente" allo strato radio — enunciato, non
  risolto). [normativo, dichiara-residuo]** Un client conforme NON DEVE (MUST NOT)
  trattare i gateway come indipendenti su *auto-dichiarazione* (GR-3, nello spazio
  radio). "Indipendente" può essere stimato solo da segnali *osservabili e
  non-auto-dichiarati* — AS di uplink distinti *dove una mappa di AS (Parte 8) è
  raggiungibile*, next-hop radio distinti, direzione fisica distinta — ciascuno dei
  quali è debole, falsificabile, o **non disponibile dentro un blackout** (la mappa di
  AS, il segnale più forte, è spesso la prima cosa che se ne va). Il significato onesto
  di "gateway indipendente" è perciò una **stima a fiducia limitata**, non un fatto
  verificato (§4b); un client DEVE (MUST) presentarlo come tale e NON DEVE (MUST NOT)
  affermare un'indipendenza di gateway verificata. Vedi BL-21 — questo è il ricorrente
  problema dell'indipendenza nello spazio radio.
- **BL-7 (troppo pochi — o zero — gateway indipendenti degrada, mai fallisce aperto).
  [normativo]** Dove meno di due gateway indipendenti-stimati sono raggiungibili, un
  client NON DEVE (MUST NOT) spingere silenziosamente `k` quote attraverso uno solo
  come se la dispersione valesse; DEVE (MUST) trattenere le quote per un'uscita
  indipendente successiva (delimitata dal TTL di BL-12), distribuirle nel tempo, o far
  emergere che l'uscita fisica è un punto singolo per questo messaggio (BL-19). Il
  pavimento (I-2) è inalterato in entrambi i casi (BL-16).

### 2.2 Indirizzamento senza raggiungibilità globale

- **BL-8 (i nomi sopravvivono; le rotte globali no). [normativo]** L'`id` Ed25519 del
  relay/destinatario (Parte 2) e il `box_id`/rendezvous della Parte 6 DEVONO (MUST)
  rimanere i nomi stabili dentro un blackout; ciò che si rompe è la *raggiungibilità*
  globale, non la nominazione. Un nodo NON DEVE (MUST NOT) dipendere da un DHT
  raggiungibile o da alcuna rotta globale per la selezione del next-hop sulla mesh.
- **BL-9 (next-hop senza un DHT — il menu e i suoi costi).** In assenza di una rotta
  globale, un next-hop mesh è scelto da un metodo locale a costo delimitato: flooding
  epidemico verso qualunque uplink (economico, senza conoscenza della destinazione,
  alto costo radio); un *gradiente* di raggiungibilità in cui i vicini pubblicizzano la
  raggiungibilità *verso un gateway* — mai verso il destinatario nominato, che sarebbe
  un selettore (I-4/SP-7); o il trasporto fisico (store-and-forward finché un gateway
  non entra a portata). Questa clausola nomina il menu; la scelta è uno strawman
  (BL-20), e ogni opzione DEVE (MUST) preservare SP-7 (nessuna collegabilità
  inter-percorso sui byte) e I-4 (BL-15).
- **BL-10 (la consegna passa ancora attraverso i drop della Parte 6, mai a un
  dispositivo nominato). [normativo]** Il compito della mesh finisce all'*uplink*: una
  volta che le quote raggiungono internet, rientrano nell'overlay e sono consegnate a
  dead-drop dispersi (Parte 6) esattamente come prima. La mesh NON DEVE (MUST NOT)
  tentare di consegnare direttamente a un *dispositivo* destinatario nominato — ciò
  renderebbe la consegna puntata su una persona, violando il contratto della Parte 6
  (RZ-1). Il caso genuinamente-tutto-locale (mittente, drop e destinatario tutti
  in-mesh, senza uplink) è servito dal fatto che il **drop** del destinatario è anch'esso
  raggiungibile via mesh — deposito e polling corrono entrambi sulla mesh *verso un
  drop*, mai verso il dispositivo destinatario — che è l'elemento aperto che la Parte 6
  §9 elenca come "polling sulla mesh durante il blackout (OP-6)". L'instradamento verso
  un dispositivo destinatario nominato resta vietato come selettore.

### 2.3 Store-and-forward e il verdetto di inquadratura

- **BL-11 (la validità Sphinx, non i byte, è il vincolo sul trasporto lungo).
  [normativo, dichiara-residuo]** Il pacchetto Sphinx da 2048 byte (SP-3) è
  autocontenuto nei *byte* ma non nella *validità*: la sua sicurezza per salto si lega
  all'epoca `onion` ≤7 giorni di un relay (CH-5) e alla cache di replay per-epoca (SP-5,
  SP-7b). Un pacchetto trasportato per ore-giorni attraverso collegamenti intermittenti
  PUÒ (MAY) sopravvivere all'epoca che il suo primo salto presumeva, o arrivare dopo che
  lo stato di replay è ruotato o è andato perso tra i riavvii. Un design conforme DEVE
  (MUST) enunciare questo e NON DEVE (MUST NOT) presumere che un pacchetto Sphinx sia
  trasportabile indefinitamente immutato.
- **BL-12 (il verdetto: il blackout ha bisogno del proprio involucro di
  store-and-forward). [normativo]** A causa di BL-11, e poiché lo store-and-forward ha
  bisogno di campi per cui il pacchetto fisso da 2048 byte non ha spazio (un
  time-to-live delimitato, frammentazione e riassemblaggio per collegamenti
  intermittenti, segnalazione di custodia per-salto), il verdetto per questa bozza è che
  **il trasporto in blackout ha bisogno della propria inquadratura esterna** — un bundle
  in stile DTN (arte nota: RFC 4838/5050) che *avvolge* il pacchetto Sphinx interno
  immutato, è esso stesso riempito a lunghezza fissa, e i cui metadati sono protetti da
  AEAD, mai in chiaro. Il pacchetto interno è intatto; l'involucro è nuovo e vive solo
  sui collegamenti in blackout. Questo è un verdetto strawman (BL-20), ribaltato solo da
  un argomento che chiude BL-11, che questa bozza non ha.
- **BL-13 (l'involucro non deve diventare un selettore — ed eredita il residuo di
  annidamento di CT-6a). [normativo, dichiara-residuo]** Il TTL, l'indice di frammento e
  i campi di custodia dell'involucro sono esattamente i metadati in chiaro che I-4
  vieta; DEVONO (MUST) vivere dentro una cornice protetta da AEAD, di dimensione fissa e
  dall'aspetto uniforme (disciplina SP-4), e NON DEVONO (MUST NOT) permettere a un
  osservatore radio di collegare due frammenti di un messaggio, o due quote di un
  messaggio, meglio di quanto SP-7 già consenta sull'overlay. **Residuo onesto, ereditato
  dalla Parte 4:** avvolgere un pacchetto interno I-4-uniforme dentro un bundle esterno
  ricrea la **superficie di struttura annidata CT-6a** nello spazio radio — una cornice
  esterna di dimensione fissa la cui dimensione/timing/frammentazione può tradire che
  porta una *seconda* unità fissa, e l'uniformità per-strato **non** rende
  l'annidamento non rilevabile a un osservatore RF. Questo è un residuo dichiarato, non
  chiuso dall'inquadratura. È sopravvivibile solo nel senso in cui lo è tutto qui:
  l'avversario RF del blackout è *locale*, quindi la rilevazione dell'annidamento costa
  *osservabilità-della-partecipazione* — che BL-18 già concede essere perduta — e **non**
  tocca il pavimento del contenuto I-2.

### 2.4 Mixing a livello radio contro il gateway sybil

- **BL-14 (il gateway sybil è un'eclissi fisica; la risposta è parziale). [normativo,
  dichiara-residuo]** Un nodo che annuncia "ho l'uplink" attira il traffico del
  vicinato, e un gateway sybil (o una coalizione) è un'*eclissi fisica* — l'istanza a
  livello radio del residuo di eclissi della Parte 2 (OP-2). La risposta parziale è (i)
  il mixing di sorgente a livello radio (BL-15) così che un gateway non possa
  banalmente attribuire una quota al suo vicino originante *allo strato di cornice*,
  composto con (ii) la dispersione su gateway indipendenti (BL-5) così che nessun
  singolo gateway veda `k`. Una descrizione conforme DEVE (MUST) dichiarare questa
  risposta **parziale**: alza il costo del sybil, non rimuove l'eclissi, e si riduce a
  OP-1/OP-2 ricorrenti allo strato radio (BL-6, BL-21).
- **BL-15 (il mixing di sorgente a livello radio è una misura di
  disponibilità/anti-eclissi, non di occultamento-dell'origine). [normativo]** Il
  traffico su un collegamento radio locale DEVE (MUST) soddisfare I-4 verso un
  osservatore radio sui byte (cornici uniformi di dimensione fissa, BL-13) e DOVREBBE
  (SHOULD) applicare il mixing di sorgente così che il mittente immediato a livello di
  cornice di una quota non sia, per la cornice, marcato come il suo originatore.
  Questa **non** è la difesa di campionamento-della-directory GR-8 (GR-8 mescola il
  *campione memorizzato* di un client attraverso classi di sorgente contro l'eclissi
  della mappa — un meccanismo diverso contro un avversario diverso) e NON DEVE (MUST
  NOT) prenderne in prestito il nome o le sue assicurazioni. E NON DEVE (MUST NOT)
  essere presentato come occultamento dell'originatore *fisico*: un avversario locale
  con radiogoniometria conosce l'emettitore fisico di una trasmissione a prescindere dal
  contenuto della cornice (BL-18), quindi il mixing di sorgente radio compra *costo
  anti-eclissi contro un gateway sybil*, mai anonimato dell'origine — la stessa
  disciplina collegamento-contro-disponibilità che CT-15a impone per i trasporti.

## 3. La valutazione onesta del realismo (la spina dorsale)

*(Scritta nella voce del §residuo delle Parti 4, 8 e 11. Questa è la parte, non
un'appendice.)*

**Cosa è genuinamente progettabile, e reale.** Tre cose. Primo, il *modello di rete
mista* (BL-1): trattare radio e internet come tipi di collegamento coesistenti così che
perdere un uplink sia un salto in più, non un mondo diverso, è pulito, costruibile e
sostenuto da arte nota (Briar, Reticulum, Yggdrasil/cjdns, Freifunk ne dimostrano
pezzi). Secondo — l'idea che fa guadagnare al paradigma il suo mantenimento — la
*dispersione su gateway indipendenti* (BL-5): la classica debolezza fatale di ogni mesh
a gateway è che il gateway vede tutto, e ScrambNet le risponde con il meccanismo che
definisce l'intera rete, spargendo le `n` quote attraverso i gateway così che
nessuna singola uscita fisica veda `k`. Terzo, la *guardia dell'invariante* (BL-16):
tenere il pavimento I-2 del tutto indipendente dal fatto che la mesh si formi non è
meramente progettabile, è forzato, ed è la stessa disciplina che la Parte 4 applica ai
trasporti. Queste tre sono solide.

**Ma la buona idea è un'idea di *disponibilità*, e deve essere venduta come nulla di
più.** La dispersione su gateway indipendenti fa poco per il *chi* o il *dove* nel
modello di minaccia del blackout-caldo, perché due residui e una fuga di identità la
minano come meccanismo di anonimato: non puoi verificare l'indipendenza del gateway in
un blackout (BL-6), l'emettitore è fisicamente localizzabile (BL-18), e lo strato radio
porta un'identità che l'overlay non può ruotare (BL-18a). Ciò che la dispersione *fa*
consegnare, e consegna genuinamente, è disponibilità: nessun guasto, blocco o cattura
sybil di un singolo gateway uccide la consegna, e questo vale anche quando ogni
proprietà di anonimato è crollata. Questo è esattamente il verdetto CT-15 per i
trasporti multi-copertura — disponibilità sì, camuffamento no — e la parte lo fissa lì
(BL-16). Venduta come anonimato sarebbe un eccesso di rivendicazione; venduta come
disponibilità è una proprietà reale e non vacua.

**Cosa è solo parziale.** Il problema del gateway-sybil / eclissi-fisica (BL-14). Il
mixing di sorgente a livello radio più la dispersione su gateway indipendenti alza il
costo di un'eclissi sybil; non la rimuove. Una coalizione di gateway che controlla `k`
delle uscite raggiungibili in una piccola mesh di vicinato mette in eclissi un mittente
esattamente come una coalizione di relay fa sull'overlay — OP-1 e OP-2 ricorrenti nello
spazio radio, non una nuova difesa. "Parziale" è la parola corretta.

**Cosa non è risolto — dichiarato a piena forza, tre residui.**

*Primo, la verifica dell'indipendenza del gateway (BL-6, BL-21).* Non puoi verificare da
alcunché che un gateway auto-dichiari che due gateway siano indipendenti, e dentro un
blackout è peggio che sull'overlay: la mappa di AS (Parte 8) che permetterebbe a un
client di *inferire* l'indipendenza da dati non-auto-dichiarati è essa stessa spesso
irraggiungibile — l'unico strumento andato proprio quando serve, così che la stima può
essere quasi-vuota in un blackout profondo (BL-5 degrada a BL-7 per default). Questo non
è un orfano della Parte 5: il modello di minaccia lo nomina come una faccia del problema
ricorrente più profondo del progetto — verificare l'indipendenza di una parte senza
fidarsi della sua auto-dichiarazione — condiviso con i relay (OP-1), i firmatari di
rilascio (OP-8) e gli autori di dipendenze (OP-2/RB). La risposta onesta è la stessa che
lì: un *residuo delimitato e dichiarato* che alimenta una *stima* di fiducia con un
errore allegato (in stile ID-12), non un controllo crittografico. La Parte 5 non ha il
privilegio di essere dove questo è finalmente risolto.

*Secondo, e irriducibilmente, la localizzabilità fisica (BL-18).* Un nodo mesh in un
blackout caldo è un trasmettitore radio in un luogo fisico, e **nessun overlay nasconde
un emettitore radio da un avversario con un radiogoniometro.** Questo è
categoricamente più duro di qualunque altra cosa nella specifica, perché ogni altra
minaccia in ScrambNet è un avversario *remoto* che ragiona sui byte, e questo è un
avversario *locale* con un'antenna — presente proprio perché ha imposto il blackout.
L'intero edificio crittografico opera su *ciò che i byte rivelano*; la localizzabilità
non riguarda affatto i byte, è il fatto elettromagnetico della trasmissione. La parte non
deve promettere che la mesh preservi l'anonimato, e non lo fa.

*Terzo — la fuga che l'overlay lavora più duramente per prevenire e che la radio disfa
(BL-18a).* La localizzabilità è *dove sei*; l'identità è *chi sei*, e lo strato radio
fa trapelare entrambe. Una radio Wi-Fi/802.11s emette identificatori persistenti di
livello-2 che l'overlay ScrambNet non tocca mai — un indirizzo MAC (e il peering 802.11s
può richiederne uno stabile), ID di servizio e di dispositivo Wi-Fi Direct/Aware,
impronte di probe-request, e, contro un avversario capace, un *RF fingerprint hardware*
(imperfezioni dell'oscillatore) che sopravvive interamente alla randomizzazione del MAC.
Così l'intera storia dell'overlay — `id` rotante, `box_id` per-epoca, carte
per-relazione (RZ-2), non-collegabilità delle quote SP-7 — siede *sopra* uno
pseudonimo di livello-2 che un sniffer locale legge direttamente, e la rotazione
dell'overlay non può ruotarlo. E la *topologia* stessa della mesh è una mappa RF
osservabile: chi ritrasmette a chi è visibile nell'etere anche sotto cornici uniformi.
Questo è l'unico residuo che la prima bozza di questa parte ometteva; è nominato qui a
piena forza perché è probabilmente peggiore della localizzabilità — non sei soltanto
individuabile mentre trasmetti, porti uno pseudonimo radio stabile ogni volta che ti
unisci.

**La mesh può preservare gli invarianti che eredita? Parzialmente, ed ecco il registro
onesto.** **I-2 (pavimento del contenuto):** preservato pulitamente — il pavimento non
ha mai cavalcato la mesh più di quanto cavalcasse il trasporto (BL-16); questa è
l'affermazione più forte e più vera che la parte fa. **I-4 (uniformità sul filo) e SP-7
(non-collegabilità delle quote):** preservati **solo allo strato di byte** — una
cornice uniforme è comunque un'emissione rilevabile (BL-18), e due quote di un
messaggio emesse dallo *stesso dispositivo fisico nella stessa finestra* sono correlate
da radiogoniometria e timing (la radio ricollega ciò che l'overlay scollega); la parte
NON DEVE (MUST NOT) affermare che la non-collegabilità sui byte ereditata sopravviva
fino allo strato RF. **I-3 (nessun punto singolo):** *esteso*, come proprietà di
disponibilità a massimo sforzo, attraverso la dispersione su gateway indipendenti (BL-5)
— ma solo nella misura in cui la stima di BL-6 è affidabile, che è il residuo non
risolto. Quindi: I-2 preservato, I-4/SP-7 preservati-solo-sui-byte, I-3
esteso-ma-stimato. Questo è il registro, ed è anti-trionfale di proposito.

**Coerenza con CT-18a.** La Parte 4 concedeva che a uno spegnimento totale senza alcun
vicino in mesh, la consegna è zero e il pavimento è intatto-e-inutile. La Parte 5 è il
piolo *sotto* quella concessione — cosa fai *quando c'è* un vicino — e non la ritratta.
Estende la raggiungibilità uno strato più in basso; non rende la consegna garantita
(BL-17). L'affermazione onesta non è "la comunicazione arriva sempre a destinazione
sulla mesh" — è: *quando esistono un vicino in mesh e un gateway, un messaggio può
attraversare la città alla velocità di un autobus; quando nessuno esiste, il segreto
resta a casa, non consegnato e non esposto; e in entrambi i casi, trasmettere sulla mesh
è un atto fisicamente localizzabile e radio-identificabile che l'overlay non può
nascondere.*

Questo è un elemento XL / a rischio-di-ricerca, e restituisce, per quanto la roadmap lo
permetta, un risultato *parziale*: un solido modello di rete mista e una genuina idea di
disponibilità, attorno a residui (indipendenza del gateway, localizzabilità fisica,
identità radio) nominati a piena forza e non pretesi chiusi.

## 4. I due verdetti ragionati

**(a) Il pacchetto Sphinx da 2048 byte sopravvive allo store-and-forward lungo ore, o il
blackout ha bisogno della propria inquadratura? → Ha bisogno della propria inquadratura
(BL-11, BL-12).** Il pacchetto va bene nei *byte* ma fallisce nella *validità e nella
funzione* su tre conteggi indipendenti: (1) la sua sicurezza per salto si lega a
un'epoca `onion` ≤7 giorni (CH-5), che un trasporto lungo giorni può sopravvivere,
arrivando a una chiave ruotata e azzerata; (2) SP-5/SP-7b richiedono stato di replay
per-epoca che sopravviva ai riavvii, e i nodi radio intermittenti perdono alimentazione
e cache proprio attraverso l'orizzonte lungo ore; (3) il layout fisso da 2048 byte
(SP-3) non ha alcun campo di riserva per il TTL, la frammentazione e la segnalazione di
custodia di cui i collegamenti intermittenti hanno bisogno, e non può crescerne uno in
chiaro (I-4). La risoluzione pulita è un bundle esterno in stile DTN che avvolge il
pacchetto interno immutato (BL-12/BL-13), con il residuo di annidamento CT-6a
dichiarato. Questo è un verdetto strawman, ribaltato solo chiudendo BL-11.

**(b) L'indipendenza del gateway può essere verificata allo strato radio? → No; è un
residuo dichiarato che alimenta una stima a fiducia limitata (BL-6, BL-21).**
"Indipendente" dovrebbe essere stabilito senza fidarsi di ciò che il gateway dice (GR-3,
nello spazio radio), e ogni segnale disponibile è debole o andato: AS di uplink distinti
hanno bisogno della mappa della Parte 8, *irraggiungibile dentro il medesimo blackout
dove l'indipendenza conta di più*; la direzione fisica distinta è falsificabile e
grossolana; il next-hop radio distinto prova la topologia, non l'indipendenza
dell'uscita. Non c'è alcun controllo crittografico che due gateway abbiano uplink
indipendenti — lo stesso muro che OP-1 colpisce per la disgiunzione dei relay e OP-8 per
la giurisdizione dei firmatari. Quindi l'architettura onesta è identica a quella della
mappa di AS (ID-12): non affermare la verifica, produci una stima a fiducia limitata da
osservabili non-auto-dichiarati (che può essere quasi-vuota in un blackout profondo),
allega l'incertezza, falla emergere (BL-19), e lascia che la dispersione (BL-5) e la
distribuzione nel tempo (BL-7) delimitino — non rimuovano — il danno quando la stima è
sbagliata.

## 5. Le guardie dell'invariante e dell'onestà

- **BL-16 (il pavimento è indipendente dal successo della mesh — l'analogo di CT-16).
  [normativo]** Nessuna garanzia di riservatezza o dispersione (I-2) DEVE (MUST)
  dipendere dalla formazione della mesh, dal fatto che un gateway sia raggiungibile, dal
  fatto che i gateway siano genuinamente indipendenti (BL-6), o dal fatto che l'involucro
  di blackout sia consegnato. La mesh compra **solo raggiungibilità** — la stessa parola
  che la Parte 4 usa per i trasporti. Un design in cui perdere la mesh perde il pavimento
  è non conforme.
- **BL-17 (coerenza con CT-18a: il fondo è ancora un fondo, tre stati). [normativo]** La
  Parte 5 estende la raggiungibilità un piolo sotto CT-18a e NON DEVE (MUST NOT) essere
  formulata per contraddirla. I tre stati, tutti espliciti: (1) **nessun vicino a
  portata** → CT-18a, consegna zero, pavimento intatto-e-inutile; (2) **vicino(i) a
  portata ma nessun gateway raggiungibile da nessuna parte nella mesh** → *anche*
  consegna zero, raggiunta via mesh anziché direttamente — lo store-and-forward PUÒ (MAY)
  trattenere le quote contro un gateway *futuro* entro il TTL di BL-12, ma questo NON
  DEVE (MUST NOT) essere presentato come consegna; (3) **≥1 gateway raggiungibile** →
  dispersione BL-5/BL-7 o degrada. Lo stato (2) collassa allo stesso esito dello (1);
  solo il percorso differisce. La Parte 5 rende la consegna *possibile* uno strato più in
  basso, mai *probabile* e mai *garantita*.
- **BL-18 (residuo di localizzabilità fisica — enunciato a piena forza, mai risolto).
  [normativo, dichiara-residuo]** Un nodo mesh che trasmette in un blackout caldo è un
  **atto fisicamente localizzabile**: un emettitore radio in un luogo, esattamente nel
  momento in cui l'avversario locale che ha imposto il blackout è più aggressivo e più
  disposto a usare la radiogoniometria e tattiche in stile IMSI-catcher. **Nessun
  overlay, mixing, dispersione o inquadratura in questa specifica nasconde questo, e
  questa parte NON DEVE (MUST NOT) affermare o implicare che lo faccia.** È la ragione
  per cui la partecipazione alla mesh DEVE (MUST) essere un opt-in esplicito, informato e
  per-contesto (BL-3), e la ragione per cui l'affermazione onesta di questa parte è
  ristretta (§3).
- **BL-18a (residuo di identità a livello radio — dichiarato, non risolto). [normativo,
  dichiara-residuo]** La partecipazione alla mesh espone identificatori persistenti di
  livello-2 che l'overlay non può ruotare: un indirizzo MAC (il peering 802.11s può
  richiederne uno stabile), ID di dispositivo e di servizio Wi-Fi Direct/Aware, impronte
  di probe-request e — contro un avversario capace — un *RF fingerprint hardware* che
  sopravvive alla randomizzazione del MAC. Ciascuno è uno pseudonimo stabile per il
  *dispositivo*, indipendente da ogni rotazione dell'overlay (`id`, `box_id`, carte RZ-2,
  SP-7). La randomizzazione del MAC aiuta contro la prima classe e nulla contro l'RF
  fingerprinting. La *topologia* della mesh è parimenti una mappa RF osservabile — chi
  ritrasmette a chi è visibile nell'etere anche sotto cornici uniformi. La parte NON DEVE
  (MUST NOT) implicare che la non-collegabilità dell'overlay si estenda all'emettitore
  radio. Questa è la seconda faccia, accanto all'indipendenza del gateway (BL-21), del
  ricorrente problema di identità/indipendenza nello spazio radio, dichiarato e non
  chiuso.
- **BL-19 (fai emergere la postura della mesh onestamente — l'analogo di CT-19).
  [normativo]** Un client conforme DEVE (MUST) far emergere, sulla superficie di onestà
  esistente (PS-9/CT-19): che un collegamento radio è in uso; che questo collegamento è
  *fisicamente localizzabile* (BL-18) **e radio-identificabile** (BL-18a); se la sua
  uscita di gateway è singola o plurale-e-indipendente-*stimata* (BL-6/BL-7); e che la
  raggiungibilità della mesh — a differenza del pavimento I-2 — non porta **alcuna**
  garanzia e può essere zero. Il messaggio che la UI enuncia: *il tuo pavimento del
  contenuto regge; sulla mesh puoi essere localizzato e il tuo dispositivo riconosciuto
  nell'etere dove sei fermo.*
- **BL-20 (stack concreto lasciato aperto; affermazioni delimitate da ciò che è
  eseguito). [normativo]** La Parte 5 **non** impone uno stack radio specifico, un metodo
  di instradamento (BL-9), un dimensionamento di TTL/frammento (BL-12) o un budget di
  batteria (BL-4); questi sono strawman e decisioni del titolare. Un client con uno stack
  mesh non specificato NON DEVE (MUST NOT) affermare alcuna proprietà *quantitativa* di
  disponibilità della mesh; PUÒ (MAY) affermare solo il *qualitativo* "un nodo che perde
  l'uplink può fare un salto in più verso un gateway vicino, e le quote DOVREBBERO
  (SHOULD) uscire attraverso gateway indipendenti-stimati", e solo dove esegue
  effettivamente ≥2 gateway indipendenti-stimati con `k < n`.
- **BL-21 (il problema ricorrente dell'indipendenza è dichiarato, non chiuso). [normativo,
  dichiara-residuo]** Verificare l'indipendenza del gateway senza una mappa raggiungibile
  e con la posizione auto-dichiarata (BL-6) è lo **stesso problema che appare per i relay
  (OP-1), i firmatari di rilascio (OP-8) e gli autori di dipendenze (OP-2/RB)** —
  verificare l'indipendenza di una parte senza fidarsi della sua auto-dichiarazione — ora
  che indossa la sua maschera a livello radio dentro un blackout, dove la mappa di AS
  (Parte 8) è essa stessa irraggiungibile. La Parte 5 **non** lo risolve; lo riduce a quel
  residuo ricorrente dichiarato e alimenta una stima a fiducia limitata, esattamente come
  la mappa ne alimenta una con un tasso di errore dichiarato (ID-12).

## 6. Requisiti introdotti qui

- **BL-1 / BL-2 / BL-3 / BL-4** — la mesh è uno strato non una modalità; ruoli derivati
  dalla capacità e variabili nel tempo; opt-in esplicito per-contesto prima di qualunque
  collegamento radio; un budget onesto di batteria/archiviazione.
- **BL-5 / BL-6 / BL-7** — dispersione su gateway indipendenti come disponibilità;
  "indipendente" è una stima a fiducia limitata, mai auto-dichiarata e quasi-vuota in un
  blackout profondo; troppo-pochi/zero gateway degradano, mai falliscono aperto.
- **BL-8 / BL-9 / BL-10** — i nomi sopravvivono, le rotte no; next-hop senza un DHT e i
  suoi costi; la consegna passa ancora attraverso i drop della Parte 6, mai a un
  dispositivo nominato, e il caso tutto-locale è servito da un drop raggiungibile via mesh.
- **BL-11 / BL-12 / BL-13** — la validità Sphinx (non i byte) delimita il trasporto lungo;
  il blackout ha bisogno del proprio involucro in stile DTN; l'involucro non deve essere un
  selettore ed eredita il residuo di annidamento di CT-6a.
- **BL-14 / BL-15** — il gateway sybil è un'eclissi fisica, risposta solo parzialmente; il
  mixing di sorgente radio è una misura di disponibilità/anti-eclissi, **non** GR-8 e
  **non** occultamento-dell'origine.
- **BL-16 / BL-17** — il pavimento è indipendente dalla mesh; coerenza con CT-18a, i tre
  stati di consegna, il fondo è ancora un fondo.
- **BL-18 / BL-18a / BL-19** — localizzabilità fisica e identità radio, entrambe
  dichiarate a piena forza e mai risolte; postura onesta della mesh su PS-9.
- **BL-20 / BL-21** — stack concreto lasciato aperto; il problema ricorrente
  dell'indipendenza dichiarato, non chiuso.

BL-16 e BL-18/BL-18a sono i tre portanti: il pavimento non dipende dalla mesh, e la mesh
non può nascondere che stai trasmettendo o che il tuo dispositivo è riconoscibile
nell'etere. L'affermazione onesta è ristretta e a forma di disponibilità: *la mesh
estende la raggiungibilità un piolo sotto uno spegnimento e tiene il pavimento del
contenuto che eredita, ma non nasconde l'emettitore, il dispositivo o la topologia, e non
garantisce la consegna.* Rompi questa parte nominando un anonimato a livello mesh che le
clausole promettono oltre BL-18/BL-18a, un punto in cui il pavimento I-2 è fatto dipendere
dal successo della mesh oltre BL-16, un modo in cui BL-17 è letta come promozione di
"possibile" a "probabile", o una fuga a livello radio che BL-18/BL-18a mancano. Questo è
l'invito, nella voce della casa — e su questa parte in particolare, la risposta onesta a
"risolve il blackout?" è "in parte, ed ecco esattamente dove non lo fa".
