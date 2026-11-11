# Specifica ScrambNet — Parte 7: L'argomento di sicurezza per I-2

> **Traduzione informativa.** La versione canonica e normativa è quella inglese ([en](../../en/spec/07-security-argument.md)).

**Stato: BOZZA (DRAFT).** Questa parte dimostra, o delimita, l'unica affermazione su cui poggia tutto il resto: il livello minimo incondizionato di contenuto (I-2). È normativa dove enuncia un requisito (`SA-n`) ed espositiva altrove. Se l'argomento qui è sbagliato, il progetto è sbagliato, e il modo più rapido per scoprirlo è attaccare *questo file*.

L'affermazione è deliberatamente stretta. Leggi prima le due frasi del §1; tutto ciò che segue è la loro giustificazione e il loro prezzo.

## 1. Cosa viene dimostrato, in due frasi

- **Livello incondizionato (il livello minimo).** Un avversario che osserva una qualsiasi `k−1` delle `n` quote di un messaggio non apprende **nulla** sul testo cifrato end-to-end — non "nulla di fattibile", ma proprio nulla, contro una computazione illimitata e qualsiasi futuro computer quantistico — perché le `k−1` quote sono *statisticamente indipendenti dal segreto* (Shamir, dimostrato nel §3).
- **Livello computazionale (la cintura).** Un avversario che ottiene `k` o più quote ricostruisce il testo cifrato e poi affronta l'AEAD end-to-end; da lì, la riservatezza del contenuto è esattamente la riservatezza di ChaCha20-Poly1305 sotto una chiave che l'avversario non possiede (SP-1a), il che **è** un'assunzione computazionale.

Questi due livelli sono **disgiunti ed esaustivi**: ogni avversario tiene o `< k` quote (livello 1) o `≥ k` (livello 2), e la garanzia in ciascuno è enunciata senza riferimento all'altro. Il resto di questa parte dimostra rigorosamente il livello 1, enuncia con precisione perché il livello 2 non può essere incondizionato, e inchioda l'unico punto in cui i due livelli potrebbero trafilare l'uno nell'altro (§4: la chiave AEAD deve essere invisibile sotto `k`).

```
  I DUE LIVELLI, PER QUANTE QUOTE TIENE L'AVVERSARIO

   quote tenute:  0 ........... k-1    │  k ........... n
                └──── LIVELLO 1 ────┘ │ └──── LIVELLO 2 ────┘
                                       │
   LIVELLO 1  (sotto k)                │   LIVELLO 2  (k o più)
   ──────────────────                  │   ────────────────────
   le k-1 quote sono                   │   l'avversario ricostruisce C,
   STATISTICAMENTE INDIPENDENTI        │   poi incontra l'AEAD end-to-end
   dal segreto (SA-1, SA-2)            │   sotto la chiave K
          │                            │             │
          ▼                            │             ▼
   non c'è nulla da apprendere,        │   riservatezza = ChaCha20-
   contro computazione ILLIMITATA      │   Poly1305 sotto K che l'avversario
   e qualsiasi computer quantistico    │   non possiede (SP-1a)
          │                            │             │
          ▼                            │             ▼
   INCONDIZIONATO (il livello minimo)  │   COMPUTAZIONALE (la cintura)

   La giuntura (SA-4): K non appare mai in nulla di ciò che vede un
   avversario sotto-k. È questo che impedisce al livello 1 di decadere
   silenziosamente nel livello 2 — il livello minimo nasconde C, e
   l'avversario non guadagna nulla verso K per un futuro C.
```

## 2. Modello e avversario

- Un **messaggio** è una stringa di byte `M`. Il mittente calcola prima il testo cifrato `C = AEAD-Seal(K, N, M)` (SP-1a), dove `K = HKDF(kpair, "e2e-content")` e `N` è il nonce del messaggio. È `C` — mai `M` — a entrare nella dispersione.
- La dispersione è Shamir `(n, k)` su GF(2⁸), **per byte**: per la posizione di byte `j`, il byte segreto `c_j` è il termine costante di un polinomio `f_j` di grado `(k−1)` indipendente e uniformemente casuale, e la quota `i` alla posizione `j` è `f_j(i)` per punti di valutazione distinti e non nulli `x_1,…,x_n ∈ GF(2⁸)\{0}` (gli indici delle quote). "Indipendente, uniforme" è portante ed è esso stesso un requisito (SA-3, più sotto).
- L'**avversario sotto-`k`** vede: una qualsiasi `k−1` quote complete (ogni posizione di byte di quegli `k−1` indici), più tutto ciò che è pubblico — la specifica, i punti di valutazione, `n`, `k`, i byte sul filo degli altri pacchetti. **Non** vede `K`, `N`, né alcuna quota oltre le sue `k−1`. Dispone di computazione illimitata.
- Dimostriamo una proprietà di `C` (il testo cifrato). Ciò che l'avversario vuole in ultima analisi è `M`; il §4 mostra che il risultato a livello di `C` si trasferisce a `M` perché `K` non è nella vista dell'avversario.

## 3. Il livello minimo: una qualsiasi `k−1` quote sono indipendenti dal segreto (livello 1)

**SA-1 (segretezza perfetta per byte).** Fissa una posizione di byte `j`. Sia il byte segreto `s = c_j` e il polinomio `f_j(x) = s + a_1 x + … + a_{k−1} x^{k−1}` con `a_1,…,a_{k−1}` indipendenti e uniformi su GF(2⁸). Per qualsiasi insieme di `k−1` punti distinti e non nulli `x_{i_1},…,x_{i_{k−1}}` e qualsiasi valore bersaglio `y_1,…,y_{k−1}`:

> il numero di tuple di coefficienti `(a_1,…,a_{k−1})` coerenti con `f_j(x_{i_t}) = y_t` per ogni `t` è **esattamente uno, per ogni candidato `s`**.

*Dimostrazione.* Fissa `s`. Le `k−1` equazioni `f_j(x_{i_t}) = y_t` sono lineari nelle `k−1` incognite `a_1,…,a_{k−1}`; la loro matrice dei coefficienti è la matrice di Vandermonde sui punti distinti e non nulli `x_{i_t}` (colonne `x, x², …, x^{k−1}`), che è invertibile sul campo. Quindi per ogni `s` c'è esattamente una soluzione. Perciò `Pr[shares = (y_1,…,y_{k−1}) | secret = s]` è la stessa (`= 1 / 256^{k−1}`) per ogni `s`: le quote sono **indipendenti da `s`**. ∎

Questa è l'enumerazione che il PoC esegue per forza bruta per `k = 3` (`poc/dispersal.py`, `floor_demo()` — tutti i 256 byte candidati risultano ugualmente coerenti, in esattamente un modo ciascuno). SA-1 è l'enunciato generale di ciò che quella demo verifica per un caso.

**SA-2 (l'intero segreto, non un byte — indipendenza congiunta).** Sia il testo cifrato `C = c_1 c_2 … c_L` (tutti gli `L` byte). Il mittente estrae le tuple di coefficienti per le `L` posizioni **in modo indipendente** (SA-3). Allora l'intera vista delle `k−1` quote — le stringhe di byte di lunghezza `L` tenute a `k−1` indici — è *congiuntamente* indipendente da `C`:

> `Pr[view = v | C = c]` è identica per ogni `c ∈ (GF(2⁸))^L`.

*Dimostrazione.* La vista si fattorizza sulle posizioni: i byte che l'avversario vede alla posizione `j` dipendono solo da `(c_j, a^{(j)}_1,…,a^{(j)}_{k−1})`, e tra le posizioni le estrazioni dei coefficienti sono indipendenti (SA-3). Quindi `Pr[view = v | C = c] = ∏_{j=1}^{L} Pr[view_j = v_j | c_j]`, e per SA-1 ogni fattore è uguale a `1/256^{k−1}` indipendentemente da `c_j`. Il prodotto è perciò `1/256^{(k−1)L}` per **ogni** `c`. L'indipendenza da `C` ne segue. ∎

SA-2 è il passo che i vecchi test del PoC **non** coprivano: `floor_demo()` è un byte e i test statistici verificavano solo una marginale (la distribuzione di una posizione). L'argomento del prodotto-sulle-posizioni è ciò che rende il livello minimo un'affermazione sul *messaggio*, e vale **solo perché** i coefficienti per posizione sono indipendenti — che è esattamente la modalità di guasto da cui SA-3 protegge.

**SA-3 (la casualità dei coefficienti è critica per il livello minimo). [normativo]** I coefficienti del polinomio `a^{(j)}_t` DEVONO (MUST) essere estratti da un RNG crittograficamente sicuro, in modo indipendente sia rispetto all'indice di coefficiente `t` sia rispetto alla posizione di byte `j`. Il livello minimo è robusto esattamente quanto questa casualità e non di più:

- **Il riutilizzo tra posizioni** (ad es. una sola tupla di coefficienti riutilizzata per ogni byte, o un breve key-stream ripetuto di coefficienti) rompe l'indipendenza di SA-2: la fattorizzazione fallisce, le `k−1` quote diventano *correlate* con `C`, e un avversario può ottenere informazioni su `C` correlando incrociatamente le posizioni. Un livello minimo costruito su coefficienti riutilizzati non è un livello minimo.
- **Un RNG a bassa entropia** (un generatore debole o prevedibile) fa collassare l'estrazione uniforme di SA-1: se l'avversario può prevedere o enumerare la distribuzione dei coefficienti, il conteggio "esattamente una tupla coerente per `s`" non è più uniforme su `s`, e le quote trafilano.

Questo è il singolo requisito implementativo più importante dell'intera specifica. È economico da soddisfare e catastrofico da sbagliare, e a differenza di una debolezza dell'AEAD non può essere corretto ruotando una chiave in seguito — un messaggio suddiviso sotto coefficienti cattivi è compromesso per sempre. Un'implementazione conforme DEVE (MUST) trattare l'RNG dei coefficienti come il suo componente di massima affidabilità (vedi anche i requisiti di crittografia di riferimento, roadmap 3.1).

## 4. La giuntura: la chiave AEAD deve essere invisibile sotto `k` (nessuna perdita tra i livelli)

SA-2 dimostra che le `k−1` quote sono indipendenti dal **testo cifrato `C`**. L'avversario vuole il **testo in chiaro `M`**. Il ponte è che `M = AEAD-Open(K,N,C)` e l'avversario sotto-`k` non possiede `K`. Questo è vero solo se `K` non compare mai in nulla di ciò che quell'avversario vede — il che è un requisito, non una coincidenza:

**SA-4 (separazione delle chiavi attraverso il livello minimo). [normativo]** Nessun valore derivabile da un avversario sotto-`k` può rivelare `K = HKDF(kpair, "e2e-content")` o `kpair`. In particolare:

- `K` NON DEVE (MUST NOT) essere collocata in alcuna quota, tag o campo di pacchetto. (In questo progetto non lo è: `K` è usata solo agli estremi, per sigillare e aprire `C`; le quote portano byte di `C`, e il tag SP-7 è derivato da una chiave *separata per etichetta* `HKDF(kpair, "tag")`, non da `K` — vedi §5 e SP-7a.)
- Perciò la vista di un avversario sotto-`k` è indipendente da `C` (SA-2) **e** non porta alcuna informazione su `K`. Non può né leggere `C` (lì non c'è nulla) né ottenere `K` per attaccare un futuro `C`. I due livelli non trafilano l'uno nell'altro.

Se SA-4 fosse violato — se un qualsiasi valore osservabile sotto-`k` fosse una funzione di `K` — il livello minimo nasconderebbe comunque *questo* `C`, ma l'avversario potrebbe raccogliere `K` e leggerlo nel momento in cui in seguito ottiene `k` quote, oppure leggere *altri* messaggi sotto la stessa `K`. SA-4 è ciò che impedisce al livello incondizionato di diventare silenziosamente computazionale.

## 5. Perché il livello 2 è computazionale, detto onestamente

Con `k` o più quote l'avversario ricostruisce `C` esattamente (interpolazione di Lagrange — questo è il percorso *previsto*, è il modo in cui il destinatario legge la posta). Da `C`, la riservatezza di `M` è precisamente la riservatezza di ChaCha20-Poly1305 sotto `K`. Questa è un'assunzione computazionale: può in linea di principio essere rotta dalla crittanalisi del cifrario. **Non** è rotta da un futuro computer quantistico tramite Shor, perché `K` proviene da un segreto *simmetrico* precondiviso senza alcuna trascrizione Diffie-Hellman da invertire (SP-1a); Grover costa al più un dimezzamento della lunghezza effettiva della chiave, da cui la raccomandazione di ≥256 bit. Quindi l'enunciato onesto del livello 2 è: *robusto quanto un AEAD simmetrico sotto una chiave che l'avversario non ha, e non di più* — una garanzia computazionale reale, convenzionale e consapevole del quantistico, non una incondizionata. Il progetto non afferma mai il contrario, e ogni documento pubblico ora enuncia il regime (roadmap 0.1).

## 6. Cosa questa parte **non** dimostra

- **Collegabilità / metadati.** I-2 riguarda il contenuto, non chi parla con chi. Nulla qui nasconde che *un qualche* flusso sia avvenuto su un percorso di quote catturato; quello è il residuo ammesso dal modello di minaccia, ristretto dalla dispersione, non annullato.
- **Disponibilità.** Una parte ostile su un percorso di quote può corrompere o scartare una quota; l'AEAD fallisce in modo chiuso (fail-closed) (SP-7a), quindi questo è un diniego di servizio, non una divulgazione. SA-1…SA-4 non dicono nulla sull'*arrivo* del messaggio, solo su ciò che un avversario sotto-`k` *apprende* se non arriva.
- **Correlazione temporale tra le quote (SP-9 / OP-4).** SA-2 riguarda i *valori* delle quote, non i loro tempi di emissione. `n` quote che entrano nella rete nel giro di millisecondi sono un'impronta digitale anche se i loro byte sono indipendenti da `C`. Questo è un problema aperto, non qualcosa che questa dimostrazione affronti.
- **L'AEAD stesso.** Il livello 2 eredita qualunque cosa sia vera di ChaCha20-Poly1305. Se quel cifrario cade, il livello 2 cade; il livello minimo (livello 1) no.

## 7. Requisiti introdotti qui

- **SA-1** — segretezza perfetta per byte di una qualsiasi `k−1` quote (dimostrata).
- **SA-2** — indipendenza congiunta sull'intero segreto (dimostrata, dato SA-3).
- **SA-3** — *la casualità dei coefficienti è critica per il livello minimo*: CSPRNG, indipendente per posizione e per coefficiente. **[normativo, massima affidabilità]**
- **SA-4** — separazione delle chiavi attraverso il livello minimo: nessun valore osservabile sotto-`k` rivela `K` o `kpair`. **[normativo]**

SA-1 e SA-2 sono teoremi; SA-3 e SA-4 sono le due condizioni sotto cui i teoremi descrivono il sistema reale. Rompi uno qualunque dei quattro — trova una vista che la dimostrazione ha mancato, una correlazione che SA-3 lascia passare, un campo che porta `K` — e avrai rotto I-2. Questo è l'invito.
