# Gestire un nodo ScrambNet — esposizione e postura di neutralità

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([OPERATORS.md](../en/OPERATORS.md)).

**Gestire un qualsiasi nodo ScrambNet è un atto visibile e deliberato, con un
rischio reale e non nullo.** Questo documento è onesto a riguardo. Ciò che segue
ti dice cosa rivela ciascun ruolo e cosa, in modo dimostrabile, non può rivelare,
così che tu possa decidere. È una dichiarazione tecnica e di postura, **non una
consulenza legale**: questo progetto è pseudonimo e non può conoscere la tua
giurisdizione, il tuo avversario o la tua legge. Quando la posta in gioco lo
giustifica, rivolgiti a un tuo consulente.

Questo è un documento informativo, non una parte normativa della specifica. Si
appoggia alle affermazioni che la specifica già fa — gli invarianti `I-1…I-4`, le
regole dei dead drop (Part 6), i residui della selezione dei percorsi (Part 3), i
residui dell'insieme di dati per l'inferenza (Part 8) — e vi punta anziché
ripeterle. Dove la specifica dichiara apertamente un residuo, questo documento lo
porta apertamente anch'esso; non lo addolcisce.

## Cosa vede ciascun ruolo, e cosa non può vedere

Ogni affermazione ha la stessa forma: **cosa vede il ruolo · cosa, in modo
dimostrabile, non può vedere, e il limite esatto di quell'affermazione · il
residuo onesto.** I ruoli sono quelli che l'architettura definisce («Chi gestisce
cosa»); nulla qui inventa un ruolo che la rete non ha.

### Client puro

Come client sei il ruolo a più bassa esposizione — «quasi invisibile», che cavalca
ponti e trasporti camaleonte — ma **non a esposizione zero**, e questo documento
non farà finta del contrario. La tua **guardia** (il tuo primo salto) vede il tuo
vero indirizzo IP e quando sei attivo (vedi sotto); questa è un'esposizione lato
client, non semplicemente una proprietà della guardia. Anche il recupero ha un
costo permanente e una superficie di metadati: un client interroga i propri drop
secondo un programma fisso obbligatorio (`RZ-9`), ~212 MB/month su quattro drop
prima ancora di inviare qualcosa (`RZ-16b`), e quel programma — non il contenuto —
è osservabile. Sei a bassa esposizione; non sei invisibile.

### Guardia (il primo salto di un client)

Una guardia è l'unico relay che vede il vero indirizzo IP di un client e la
tempistica della sua attività. Se gestisci una guardia, apprendi che un
particolare IP ha parlato ScrambNet con te, e quando. **Non** apprendi dove quel
traffico stesse andando né cosa contenesse: per `I-4` ogni pacchetto che ti
attraversa è rumore a dimensione fissa indistinguibile da byte casuali uniformi, e
tu detieni un solo frammento di un solo messaggio che viaggia su uno di diversi
percorsi.

Il limite esatto di «non puoi ricostruire il messaggio». Il livello minimo del
contenuto (`I-2`) è incondizionato **al di sotto di `k` posizioni catturate**:
detieni meno di `k` frammenti ed essi sono, in senso teorico-informativo, rumore,
senza alcuna via d'uscita computazionale o quantistica. Ma *raggiungere* quel
livello minimo dipende dal fatto che gli `n` percorsi siano genuinamente
**disgiunti**, e la disgiunzione è **inferita, non provata** (`OP-1`; `PS-11`, «la
disgiunzione creduta non è disgiunzione reale»). Una mappa scelta e ostile può
*dirottare* i relay di un avversario in posizione e portare la rottura del
contenuto «dal ~0% al 100% al ~15% di proprietà» (`PS-12`/`ID-8a` — una scoperta
che il progetto porta apertamente dopo che una precedente sopravvalutazione è stata
rotta). Quindi l'affermazione onesta non è «una guardia non può ricostruire», punto
e basta; è «nessuna coalizione ricostruisce **al di sotto di `k` posizioni
catturate**, e se i tuoi percorsi raggiungano davvero quel livello minimo è una
proprietà non verificata che un avversario che dirotta può sconfiggere oltre una
soglia».

**Il residuo onesto:** tu vedi gli IP dei client. Questa è l'esposizione più netta
di qualunque ruolo di relay, ed è strutturale, non una fuga da correggere. Gli IP
delle persone che usano ScrambNet passano attraverso il tuo nodo e sono visibili a
chiunque possa osservarne le connessioni.

### Relay intermedio

Un relay intermedio non vede nessuna delle due estremità. Per la costruzione Sphinx
e `I-4` non può dire se il suo predecessore sia il client originante o un altro
relay, né se il suo successore sia l'ultimo salto. Non vede alcun IP di client
(quella è la posizione della guardia), nessuna destinazione, nessun contenuto;
detiene un solo frammento cifrato. È il ruolo di relay a minore informazione —
rumore che passa tra due altre macchine. La sua esposizione è quella generale che
ogni ruolo condivide (sotto): gestirlo è un atto visibile, e inoltra traffico che
non puoi ispezionare.

### Drop (storage dead-drop, Part 6)

Un drop conserva i frammenti depositati nelle caselle e li serve quando viene
interrogato. Ciò che conserva è, per `I-2`, illeggibile in senso
teorico-informativo: ciascun frammento conservato è al di sotto di `k` e
indistinguibile da rumore casuale per chiunque — **te incluso, l'operatore** —
senza gli altri frammenti, che si trovano su altri drop che non controlli (`RZ-5`:
nessun singolo drop tiene mai due frammenti di uno stesso messaggio; l'insieme dei
drop è `d = n = 4`, `k = 3`, quindi un drop tiene esattamente un frammento, `< k`).
Non puoi leggere ciò che conservi, non puoi distinguere i contenuti di due caselle,
e non puoi collegare un deposito a un mittente (`RZ-2`/`RZ-10`, `SP-7`). Questa
affermazione è esatta e non è addolcita: un operatore di drop è genuinamente cieco
al contenuto.

**Cieco al contenuto non è la stessa cosa di neutrale nella consegna, e questo è il
residuo onesto.** Un drop vede la **tempistica**: la cadenza pubblica di polling
(`RZ-9`) e i tempi di deposito nelle caselle che detiene, entro un'epoca; un drop
che detiene diverse caselle può correlare i *timestamp* di deposito tra di esse
anche sotto perfetta indipendenza del polling (`RZ-16`/`OP-9`, portato apertamente
nella specifica di rendezvous §9). E un drop *può* negare la **consegna** senza
leggere nulla: lo sfratto con il più vecchio per primo più la finestra di recupero
8-slot significano che un flooder — anche un telefono economico — può seppellire la
posta onesta oltre la finestra in ~17 secondi (`RZ-15`), un residuo di flooding
della consegna che la specifica dichiara non avere ancora una difesa sufficiente
(`OP-9`). Quindi: tu conservi rumore illeggibile, ma osservi *che* quel rumore è
arrivato ed è stato raccolto e quando, e la meccanica dello storage è una
superficie di consegna. Quell'esposizione di tempistica-e-consegna è il residuo
genuino del drop, dichiarato non nascosto.

### Ponte (punto d'ingresso distribuito lungo il grafo sociale)

Un ponte è un punto d'ingresso consegnato di persona in persona dove la rete aperta
è bloccata (livelli di fiducia in stile Lox). Vede informazioni di livello guardia
per i client che lo raggiungono (il loro IP, nulla a valle). La sua esposizione
distintiva è l'**essere individuabile come ponte**: un censore che riesce a
spacciarsi per utente può apprendere l'indirizzo del tuo ponte e bloccarlo o
osservarlo. La distribuzione lungo il grafo sociale limita quanto in fretta e quanto
ampiamente un indirizzo trapela — «un censore può spacciarsi per un utente; non può
spacciarsi per l'amico di tutti» — ma non rende un ponte non individuabile.

**Il residuo onesto:** gestire un ponte significa che un tuo indirizzo, per
progetto, circola tra sconosciuti-di-sconosciuti, alcuni dei quali possono essere
avversari. La resistenza all'enumerazione è una corsa agli armamenti che il modello
di minaccia definisce sostenibile, non vinta.

### Nodo mesh / gateway (strato per il blackout)

Un nodo mesh inoltra da dispositivo a dispositivo su Wi-Fi Direct / Bluetooth
durante un blackout; un gateway ponta la mesh di nuovo verso internet quando una
rotta esiste. La sua esposizione al contenuto è la stessa di qualunque relay —
frammenti a dimensione fissa che non può leggere (`I-2`/`I-4`). La sua esposizione
distintiva è **fisica e locale**: la sua visibilità è un segnale radio su scala di
quartiere, correlabile a una posizione e potenzialmente a una persona, precisamente
quando e dove un avversario ha spento internet ed è più motivato. È per questo che
l'architettura ne fa sempre un opt-in esplicito. Un **gateway** porta *entrambe* le
esposizioni in una volta: l'esposizione fisica/locale sul lato mesh, **e**
l'ordinaria esposizione da relay sul suo lato internet — il suo IP rivolto a
internet è un nodo ScrambNet osservabile per il suo stesso ISP — pur non essendo mai
un'uscita clear-web (sotto).

**Il residuo onesto:** di tutti i ruoli questo scambia la più forte cecità al
contenuto con il più debole anonimato dell'operatore. I byte sono rumore; il
trasmettitore è in un luogo. Nessun invariante protegge la localizzabilità fisica
di una radio.

### L'uscita clear-web che non esiste

ScrambNet **non ha un ruolo di uscita clear-web**, e questo conta più di tutto per
gli operatori. L'uscita clear-web è il ruolo più esposto in assoluto in Tor: l'IP di
un'uscita Tor compare come sorgente apparente di qualunque cosa i suoi utenti
inviino verso internet aperta, e quell'operatore riceve i reclami per abuso, le
notifiche di rimozione e l'attenzione delle forze dell'ordine per traffico che non
ha scelto né può vedere. ScrambNet non ha un equivalente. Il salto terminale di un
messaggio consegna un frammento in un dead drop (Part 6) — rumore illeggibile in uno
storage interno al progetto — non verso un host terzo arbitrario. **Nessun indirizzo
di nodo ScrambNet compare come origine di traffico attribuibile in arrivo a un
servizio esterno** (il gateway mesh tocca internet, ma porta rumore interno a
ScrambNet verso un relay, non il traffico di un utente verso un host clear-web).
È per questo che l'architettura afferma che l'esposizione di un operatore di
relay/drop è «strutturalmente più bassa di quella di un'uscita Tor» — un confronto
di esposizione **tecnica**, mai un'affermazione sulla tua responsabilità legale.
Detto con precisione: questo rimuove la *specifica* esposizione da nodo d'uscita;
**non** rende alcun ruolo privo di rischio, e non fa di ScrambNet un proxy d'uscita
— strutturalmente non lo è, e quell'assenza è una caratteristica, anche per te.

### Gestire più di un ruolo

La maggior parte delle affermazioni qui sopra descrive un singolo ruolo isolato. Una
stessa macchina comunemente ne gestisce diversi — guardia, relay e drop insieme — e
la co-locazione crea correlazioni che nessuna delle affermazioni su un singolo ruolo
mostra. Un drop che detiene diverse caselle correla la tempistica di deposito tra di
esse (`RZ-16` §9); un relay che è **anche un utente** ed è «acceso esattamente
quando il suo operatore chatta è un attacco a intersezione su sé stesso»
(l'architettura lo nomina direttamente). La disciplina che l'architettura prescrive
è la mitigazione: un programma sempre attivo indipendente dal tuo stesso uso, così
che il tuo tempo di accensione non dica nulla sulla tua attività. Se gestisci più di
un ruolo, la tua esposizione non è il minimo dei ruoli — è la loro combinazione.

## La postura sulla gestione degli abusi

Questa è la parte che un lettore ostile metterà più alla prova, quindi ogni sua
frase è costruita su una vera incapacità, e nessuna di esse introduce una leva.

**(a) L'incapacità, enunciata come proprietà di sicurezza.** ScrambNet non può
leggere, identificare, prendere di mira, né bloccare o dare priorità in modo
selettivo rispetto al contenuto ad alcun messaggio, utente o contenuto. Questa non è
una politica che adottiamo e potremmo invertire; è una proprietà del progetto. Un
drop conserva frammenti che sono illeggibili in senso teorico-informativo al di sotto
di `k` (`I-2`); un relay inoltra rumore a dimensione fissa che non può distinguere da
qualunque altro (`I-4`); non c'è alcun registro di utenti (non c'è registrazione),
nessuna autorità di directory, e nessuna parte privilegiata in alcun punto del
protocollo (`I-3`). Il progetto non ha chiave, né interruttore, né alcuna posizione
nella rete da cui il contenuto *potrebbe* essere ispezionato o filtrato. La stessa
matematica protegge tutti perché non può distinguere nessuno, e quell'indiscriminatezza
è ciò che rende la protezione affidabile: una rete che *potesse* scegliere da che
parte stare è una rete che un avversario potente potrebbe *costringere* a scegliere.
(Una nota onesta di portata: la cecità al contenuto non è neutralità nella consegna —
la meccanica dello storage di un drop è una superficie di consegna, `RZ-15` — quindi
«non può bloccare» qui significa *non può bloccare in modo selettivo rispetto al
contenuto*, che è la proprietà che conta per la neutralità.)

**(b) Cosa il progetto può genuinamente fare.** Ciò che possiamo fare, lo facciamo
allo scoperto: pubblicare il progetto completo così che chiunque possa studiarlo,
attaccarlo o reimplementarlo (`I-1`); ricevere e agire sulle segnalazioni di
**vulnerabilità** secondo la politica di sicurezza (SECURITY.md); correggere difetti;
e continuare a dire chiaramente cosa la rete protegge e cosa non protegge. Questo è
l'intero elenco. Niente di tutto ciò comporta guardare, raggiungere o agire sul
traffico di qualcuno, perché il progetto non ci dà alcun modo di farlo — e il canale
delle vulnerabilità è per i difetti nel progetto e nel codice, mai un canale per
segnalare traffico o utenti, perché non c'è nulla che potremmo fare con una
segnalazione del genere e la sua esistenza non deve far intendere il contrario.

**(c) Cosa il progetto si rifiuta di costruire, e perché.** Non costruiremo una
capacità di moderazione, una backdoor di segnalazione, un filtro di contenuti, una
lista di blocco degli utenti, un rubinetto per l'«accesso legale», né alcun altro
meccanismo che permetta al progetto, a un operatore o a chiunque altro di leggere,
prendere di mira o sopprimere contenuti o utenti. Ci rifiutiamo non per indifferenza
al danno, ma perché un tale meccanismo è autolesionista nei suoi stessi termini.
Qualunque leva possa essere puntata verso contenuti chiamati «abuso» è la stessa
leva, puntata nell'altra direzione, verso contenuti chiamati «dissenso» — è una sola
capacità, e chiunque possa imporne l'uso decide cosa essa prende di mira. Sarebbe
esattamente il singolo punto di controllo che `I-3` proibisce e lo schierarsi da una
parte che il modello di minaccia mette fuori ambito. Nel momento in cui una tale leva
esiste, la promessa della rete è falsa per tutti, incluse le persone che era stata
costruita per proteggere; l'avversario non deve più rompere la matematica, solo
impadronirsi della leva. L'assenza di un meccanismo di moderazione non è una lacuna
che non siamo riusciti a colmare — è una proprietà di sicurezza portante che ci
rifiutiamo di distruggere. (Qualunque controllo di ammissione contro il flooding il
progetto dovesse mai adottare — la questione aperta `OP-9` che `RZ-15` lascia
irrisolta — DEVE (MUST) essere cieco al contenuto e cieco all'identità per
costruzione, e il candidato di punta mette un gate sul possesso di una carta di
contatto per relazione, non sul punto di vista; una regola di ammissione che dovesse
*identificare un mittente* o *ispezionare un deposito* sarebbe una leva ed è
proibita sotto questa stessa postura.)

**(d) Il costo onesto.** Questo non è gratuito, e non faremo finta del contrario. Una
rete che non può scegliere da che parte stare non può nemmeno scegliere *contro* il
danno. ScrambNet può essere usato per cose che i suoi autori trovano ripugnanti, e il
progetto non può impedirlo per progetto. Le analogie consuete — il sistema postale
non può leggere ogni lettera, una rete telefonica non può restare in ascolto di
chiamate «cattive», TLS non può rifiutarsi di cifrare la connessione di un criminale —
portano la forma del punto ma lo **sottovalutano**, e la differenza è l'intera
affermazione: gli endpoint postali, telefonici e TLS *possono* essere costretti da un
mandato a intercettare un bersaglio specifico, perché un punto di osservazione e una
chiave esistono. Il «non può» di ScrambNet è **più forte** — non c'è posizione da cui
un operatore costretto *potrebbe* consegnare contenuto al di sotto di `k` (`I-2`), e
nessuna singola parte che *potrebbe* ricevere l'ordine di pubblicare una vista
avvelenata della rete (`I-3`; la specifica nomina direttamente la realtà del
«costretto, intimato con mandato o sequestrato»). Le protezioni sono indiscriminate
perché la protezione selettiva non è protezione — è un elenco di chi è autorizzato a
essere al sicuro, tenuto da chiunque abbia in mano la penna. Accettiamo il costo a
occhi aperti: uno strumento abbastanza potente da proteggere gli indifesi dai
potenti non può venire con un interruttore che i potenti possano azionare. Il riassunto
onesto non è «ScrambNet previene gli abusi». È: **ScrambNet protegge la
comunicazione, e quella protezione non viene con un interruttore di spegnimento —
per nessuno, contro nessuno, noi inclusi.**

## Dove sei esposto comunque

Enunciato chiaramente e lasciato in piedi — nessun «ma non preoccuparti», nessuna
sicurezza sottintesa.

- **Gestire un qualsiasi nodo è un atto visibile.** Un relay pubblica un indirizzo;
  un ponte ne fa circolare uno; un nodo mesh emette un segnale radio. La matematica
  protegge il *contenuto e la collegabilità del traffico*, non il *fatto che la tua
  macchina sia sulla rete*. Se l'essere visto gestire infrastruttura di anonimato è
  esso stesso il tuo rischio, nessun invariante lo rimuove.
- **Una guardia vede gli IP dei client.** Strutturale, non un bug. Gli IP degli
  utenti ScrambNet passano attraverso la tua guardia e sono visibili a chiunque
  possa osservarne le connessioni.
- **Un drop vede la tempistica e plasma la consegna.** Contenuto illeggibile, sì —
  ma i tempi di deposito e di polling entro un'epoca, la correlazione dei tempi di
  deposito tra caselle, e la superficie di consegna sfratto/flooding sono residui
  reali, dichiarati (`RZ-15`/`RZ-16`/`OP-9`).
- **Un ponte è individuabile.** Per progetto è consegnato a sconosciuti; alcuni
  possono essere avversari. La resistenza all'enumerazione è una corsa agli
  armamenti, non una garanzia.
- **Un nodo mesh è fisicamente localizzabile.** I byte sono rumore; il trasmettitore
  è in un luogo, precisamente quando un avversario ha spento internet.
- **Raggiungere il livello minimo del contenuto dipende da una disgiunzione che non
  puoi verificare.** Il livello minimo `I-2` al di sotto di `k` è incondizionato; che
  i tuoi percorsi o i tuoi drop siano davvero indipendenti è inferito, non provato
  (`OP-1`/`PS-11`), e una mappa di dirottamento può sconfiggerlo oltre una soglia
  (`PS-12`). Gestisci sapendo questo.
- **La tua legge locale può costringerti indipendentemente da cosa siano i byte.**
  Questo progetto non può dirti cosa una qualsiasi autorità possa esigere da te, e non
  farà finta che la cecità al contenuto della rete sia uno scudo legale — è un fatto
  tecnico sui byte, non una conclusione legale specifica di una giurisdizione. Che un
  drop *non possa* leggere ciò che conserva è vero e può contare, oppure no, a seconda
  di una legge che questo progetto pseudonimo non può conoscere. **È qui che ti serve
  un tuo consulente, non il nostro.** Noi enunciamo ciò che è tecnicamente rivelato;
  cosa significhi per te, legalmente, sta a te scoprirlo.
