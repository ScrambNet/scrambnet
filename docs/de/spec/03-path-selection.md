# ScrambNet-Spezifikation — Teil 3: Circuit-Aufbau und Pfadauswahl

**Status: ENTWURF (DRAFT), und der am wenigsten gefestigte Teil der
Spezifikation.** Dies ist die tragende Wand der *operativen* Sicherheit (der
durch I-2 garantierte Inhalt steht auch ohne sie, doch der Schutz vor
Verknüpfung und die ganze Geschichte der k-Pfade wohnen hier). Vorläufige Werte
sind mit `(s)` gekennzeichnet. Das Problem der Disjunktheits-Verifikation ist
OP-1 und offen ungelöst; dieser Teil nennt das Ziel und einen ersten
Mechanismus zum Angreifen.

## 1. Geltungsbereich und warum dies schwer ist

Die Streuung (Teil 1) macht den Inhalt unterhalb von `k` erbeuteten Anteilen
bedingungslos sicher. Diese Garantie ist nur dann *operativ* real, wenn die `n`
Anteil-Circuits wirklich disjunkt sind — sonst sieht ein einziger
Beobachtungspunkt des Gegners `k` Anteile, und die garantierte Untergrenze wird,
mathematisch zwar unversehrt, nie erreicht. Dieser Teil entscheidet, wie ein
Client, der nur seine eigene überprüfbare Gossip-Stichprobe (Teil 2) und keine
vertrauenswürdige Karte besitzt, `n` Circuits auswählt, über die sich ein
Gegner nicht billig setzen kann. Alles hier muss gegen Relais standhalten, die
über alles lügen außer dem, was ihre Signaturen binden (GR-2).

## 2. Disjunktheitsziele

- **PS-1.** Die `n` Circuits einer Nachricht MÜSSEN (MUST) *knotendisjunkt*
  sein: kein Relais erscheint auf zweien von ihnen. Dies ist die Untergrenze,
  stets durchsetzbar, wenn die Stichprobe groß genug ist.
- **PS-2.** Der Client SOLLTE (SHOULD) zusätzlich anstreben, in absteigender
  Reihenfolge des Werts und aufsteigender Reihenfolge der Schwierigkeit:
  **AS-disjunkt** (keine zwei Circuits teilen ein autonomes System am Wächter
  oder am Ausgang), dann **jurisdiktionsdisjunkt** (keine zwei teilen eine
  Rechtsjurisdiktion). Jede Stufe, die er nicht erreichen kann, MUSS (MUST) dem
  Nutzer gemeldet werden, nicht stillschweigend übersprungen (PS-9).
- **PS-3.** Innerhalb eines Circuits MÜSSEN (MUST) Wächter, Mitte und Ausgang
  knotenverschieden sein und SOLLTEN (SHOULD) AS-verschieden sein. Ein Circuit,
  dessen Wächter und Ausgang ein AS teilen, ist ein Geschenk an die
  Ende-zu-Ende-Korrelation und DARF NICHT (MUST NOT) verwendet werden, wenn
  irgendeine Alternative existiert.

## 3. Schlussfolgerung ohne Selbstdeklaration

- **PS-4.** GR-3 verbietet Relais, ihren Standort zu deklarieren, daher
  schließt der Client das AS und die Jurisdiktion jedes Relais aus dessen
  `addrs` mithilfe seines *eigenen* Datensatzes (z. B. einer regelmäßig
  aufgefrischten IP-zu-AS-Karte), niemals aus etwas, das das Relais sagt. Die
  Verteilung des Datensatzes selbst MUSS (MUST) I-3 befolgen: keine einzige
  maßgebliche Quelle (Kandidaten-Entwürfe sind OP-1).
- **PS-5.** Die Schlussfolgerung ist unsicher, und der Client MUSS (MUST) sie so
  behandeln: Ist das AS oder die Jurisdiktion eines Relais unbekannt, zählt es
  als *potenziell geteilt* mit jedem anderen Unbekannten — die konservative
  Annahme, niemals die optimistische.

## 4. Wächter

- **PS-6.** Jeder Client hält eine kleine Menge von **Wächter-Relais**
  (vorläufig: ein primärer Wächter je Circuit-Position, rotiert in einem Takt
  von Monaten, nicht Minuten) und folgt damit Tors Wächter-Begründung: Die
  Eintrittspunkte schnell zu rotieren vervielfacht die Chance, früher oder
  später einen feindlichen zu ziehen. Die Wächter MÜSSEN (MUST) voneinander
  AS-disjunkt gewählt werden, damit die `n` Circuits nicht am Eingang durch ein
  einziges AS geleitet werden.
- **PS-7.** Die Wächter-Auswahl wird nach *verifizierter* Bandbreite (GR-7)
  gewichtet, nie nach behaupteter; ein Relais mit einer nicht verifizierbaren
  Behauptung wird als Relais niedriger Bandbreite behandelt, nicht hoher.

## 5. Kleine Netze: degradieren, und es sagen

- **PS-8.** Wenn die verifizierte Stichprobe des Clients keine `n`
  AS-disjunkten Circuits liefern kann, MUSS (MUST) er in einer festen
  Reihenfolge zurückfallen — AS-disjunkt → knotendisjunkt → unabhängige
  Ziehungen — und DARF NICHT (MUST NOT) stillschweigend so fortfahren, als
  gälte die stärkere Eigenschaft. Die Parameter DÜRFEN (MAY) reduziert werden
  (Kleinnetz-Modus: `n = 2, k = 2` mit bestmöglicher Disjunktheit), wenn die
  geschätzte tragfähige Größe nicht erreicht wird.
- **PS-9.** Der Client MUSS (MUST) die für eine Nachricht tatsächlich erreichte
  Disjunktheitsstufe offenlegen, in Begriffen, die ein Laie richtig liest: Die
  Menge ist heute klein; das ist es, was du kaufst. Der garantierte Inhalt
  (I-2) und die Verknüpfungsstufe sind getrennte Aussagen und MÜSSEN (MUST)
  getrennt gezeigt werden.
- **PS-10 (sybil-resistente Größenschätzung).** Die Schätzung der tragfähigen
  Größe MUSS (MUST) nur unabhängig verifizierte Relais und beobachtete
  AS-Vielfalt zählen, niemals die rohe Eintragszahl, damit ein Gegner das Netz
  nicht mit Sybils aufblähen kann, um Clients zu vollen Parametern zu verleiten,
  deren Vielfalt falsch ist (bindet an OP-2).
- **PS-11 (vermutete Disjunktheit ist keine echte Disjunktheit).** Der Schutz,
  den ein Client aufbaut, ist nur so gut wie sein Schlussfolgerungs-Datensatz,
  und der Client MUSS (MUST) die Fehlerrate des Datensatzes als
  erstrangigen Sicherheitsparameter behandeln, nicht als Implementierungsdetail.
  Der Simulator (`poc/network_sim.py`, §1) trennt die *Grundwahrheit* — die der
  Gegner ausnutzt — von der *Annahme* des Clients und variiert die
  Schlussfolgerungs-Fehlerrate: Steigt der Fehler, wird die AS-disjunkte Auswahl
  teilweise illusorisch, und sowohl die Inhaltsbruchrate als auch der
  Verknüpfungsleck steigen monoton. Zwei Folgerungen sind normativ: (a) Bei
  **zufälligem** Schlussfolgerungsfehler (Rauschen, eine bloß ungenaue Karte)
  untergräbt der Fehler die **Verknüpfung weit schneller als den Inhalt** — ein
  Inhaltsbruch erfordert weiterhin, dass der Gegner auf `≥ k` Circuits
  gleichzeitig sitzt, sodass die Untergrenze hält, während die Metadaten zuerst
  degradieren; die UI DARF NICHT (MUST NOT) eine niedrige Inhaltsbruchzahl so
  darstellen, als begrenze sie auch die Verknüpfung. Diese Asymmetrie gilt **nur
  für zufälligen Fehler**; eine *adversarisch gewählte* Karte ist kein Rauschen
  (siehe PS-12); (b) eine dünnere
  **Gossip-Stichprobe** (PS-10, I-3) erzwingt das Zurückfallen früher: Ein
  Client, der zu wenige Relais kennt, kann überhaupt keine AS-disjunkten
  Circuits aufbauen und fällt auf `none` zurück, wo die Bruchrate springt (§2).
  Die Schätzung der tragfähigen Größe (PS-10) MUSS (MUST) daher die
  *erreichbare* Stichprobe berücksichtigen, nicht das gesamte Netz. Die Zahlen
  bei null Fehler und voller Sicht sind der beste Fall; ein konformer Client MUSS
  (MUST) die erreichte Stufe (PS-9) aus seiner realen, verrauschten, partiellen
  Sicht darstellen.
- **PS-12 (eine feindliche Karte darf die Auswahl nicht auf den Gegner lenken).**
  `[claim-critical]` Eine *adversarisch gewählte* Karte ist kein zufälliger
  Fehler, und die Asymmetrie aus PS-11(a) schützt **nicht** gegen sie. Eine Karte,
  die der Gegner kontrolliert, hat zwei Hebel über die AS-disjunkte Auswahl: den
  eigenen ko-lokalisierten Relais des Gegners *verschiedene* gefälschte ASes geben
  (damit sie sich nie gegenseitig ausschließen) und *ehrlichen* Relais
  *kollidierende* gefälschte ASes geben (damit, sobald Circuit 1 ein ehrliches
  Relais wählt, jedes andere ehrliche Relais AS-geteilt aussieht und
  herausgefiltert wird). Der ehrliche Kandidaten-Pool kollabiert dann nach der
  ersten Ziehung, und der Client wählt die Circuits 2…`n` fast vollständig aus
  Gegner-Relais — womit der Gegner **deterministisch** auf Wächter **und** Ausgang
  von `≥ k` Circuits landet, ein *Inhalts*-Bruch, während der Client noch glaubt,
  AS-Disjunktheit erreicht zu haben, und keine Rückfall-Warnung erhebt.
  Demonstriert gegen `poc/network_sim.py`: Eine lenkende Karte treibt die
  Inhaltsbruchrate von ~0 % auf **100 % bei ~15 %** Gegner-Besitz (gegenüber einer
  niedrigen einstelligen Rate für eine ehrliche Karte bei 35 %). Also **KANN eine
  schlechte Karte Inhalt erreichen, nicht nur Verknüpfung** (dies korrigiert eine
  frühere Übertreibung; Teil 8 ID-8a ist passend korrigiert). Die Verteidigungen,
  die ein konformer Client anwenden MUSS (MUST):
  1. **Lass die Karte allein nicht den ehrlichen Pool kollabieren.** Ein Client
     DARF NICHT (MUST NOT) eine Circuit-Menge bauen, in der mehr als ein begrenzter
     Anteil der Circuits für ihre behauptete gegenseitige Disjunktheit von Relais
     abhängt, die der Client nicht *unabhängig* als verschieden bestätigen kann
     (GR-8 Quellenmischung, PS-10 "zähle nur unabhängig verifizierte"). Würde die
     als disjunkt geglaubte Auswahl die Circuits 2…`n` aus einem Pool ziehen, den
     die Karte verdächtig klein gemacht hat, MUSS (MUST) der Client dies als
     Rückfall-/Anomalie-Bedingung behandeln (PS-8, PS-9), nicht als Erfolg.
  2. **Eine Karte, die eine unplausible AS-Struktur impliziert, ist selbst eine
     Anomalie.** Eine Karte, unter der die *erreichbare ehrliche Stichprobe* des
     Clients auf ein oder wenige ASes kollabiert, während der gegner-geformte Rest
     maximal vielfältig ist, ist eine Signatur von Lenkung; der Client SOLLTE
     (SHOULD) sie als Karten-Anomalie gossippen (Teil 8 ID-10) und zurückfallen.
  3. **Neubau ist die eigentliche Verteidigung.** Eine lenkende Karte ist nicht aus
     öffentlichen Eingaben reproduzierbar (Teil 8 ID-5a); ein Client, der neu baut
     oder mit einem ehrlichen Peer übereinstimmt, der es tat, lehnt sie ab. Bis
     dahin MUSS (MUST) der Client die Disjunktheits-Behauptungen einer
     unverifizierten Karte als unverifiziert behandeln, nicht als erreicht (PS-9).
  Das ehrliche Residuum bleibt: Innerhalb des Eklipse-Fensters eines Clients, der
  eine unverifizierte lenkende Karte akzeptiert hat und noch nicht neu bauen kann,
  kann die Inhalts-Untergrenze fallen. Dies ist durch die `k`/`n`-Marge und durch
  die obigen Verteidigungen begrenzt, nicht durch eine Behauptung, dass es nicht
  geschehen kann.

## 6. Das Verifikationsverfahren (PS-13…PS-19)

### 6.1 Das Verfahren und sein Zertifikat

- **PS-13 (das Verfahren ist eine reine Funktion dreier deklarierter Eingaben).**
  `[claim-critical]` Der Circuit-Aufbau MUSS (MUST) als deterministische Funktion
  ausdrückbar sein
  ```
      verify(sample, map, corroboration, n, k)  ->  (circuits, certificate)
  ```
  von genau drei client-seitigen Eingaben und nichts sonst:
  - **`sample`** — die verifizierte Gossip-Stichprobe von Relais des Clients
    (Teil 2, gezählt unter PS-10: *nur unabhängig verifizierte Relais*);
  - **`map`** — die Schlussfolgerungskarte aus Teil 8, benannt durch ihren Hash
    `H` und ihre eigene gemessene Fehlerrate `e` tragend (ID-12);
  - **`corroboration`** — eine Zahl pro Relais `c_j ∈ [0,1]`, die angibt, wie
    unabhängig das geschlossene AS/die Jurisdiktion des Relais bestätigt ist
    (PS-15).
  Die Ausgabe sind `n` Circuits **und** ein **Disjunktheits-Zertifikat** (PS-14).
  Kein Schritt darf den selbstdeklarierten Standort des Relais (GR-3, PS-4), ein
  vertrauenswürdiges Verzeichnis (I-3) oder die Grundwahrheit lesen (es gibt keine
  zu lesen — das ist das ganze Problem). Eine konforme Implementierung, die ihre
  Auswahl nicht als diese reine Funktion ausdrücken kann, kann kein prüfbares
  Zertifikat ausgeben und ist nicht konform: Ein Implementierer mit dieser
  Spezifikation und denselben drei Eingaben MUSS (MUST) in der Lage sein, dieselbe
  Entscheidung aus Circuits-und-Zertifikat neu aufzubauen (I-1).

- **PS-14 (was das Zertifikat enthält — und wie es maschinell prüfbar ist).**
  `[claim-critical]` Das Zertifikat ist ein kanonischer CBOR-Datensatz
  (Kodierung aus Teil 0), der **genau** die Felder trägt, die eine zweite Partei
  braucht, um es **neu zu berechnen und zu bestätigen**, und kein Feld, das um
  Vertrauen bittet:
  1. **`map_hash`** — der `H`, gegen den das Zertifikat berechnet wurde (ID-2).
     Das Zertifikat ist ohne ihn bedeutungslos: *"AS-disjunkt"* ist niemals eine
     freistehende Behauptung, nur *"AS-disjunkt unter Karte `H`"*.
  2. **`map_error`** — das Paar `(mismap_rate, unknown_rate)`, das die Karte
     auslieferte (ID-12), wortwörtlich kopiert, damit der Prüfer es nicht neu
     messen muss. Ihre Summe ist der Fehler pro Nachschlag `e`, der unten verwendet
     wird.
  3. **`circuits`** — für jeden der `n` Circuits die Relais-IDs (GR-2
     Schlüssel-Fingerabdrücke) an Wächter/Mitte/Ausgang, und für die **Pivots**
     (Wächter und Ausgang — die zwei Positionen, die ein Gegner auf AS-Ebene
     korreliert, PS-3) das **geglaubte** `(AS, jurisdiction)`, das die Karte
     zuwies, oder `unknown`.
  4. **`corroboration`** — das verwendete `c_j` pro Pivot (PS-15), damit der Prüfer
     mit denselben Reduktionen neu rechnet.
  5. **`class`** — die erreichte Disjunktheitsklasse, eine von `as` / `node` /
     `none` (PS-2-Reihenfolge), d.h. die *stärkste* Eigenschaft, die die Menge
     unter der Karte tatsächlich erfüllt, nicht die angeforderte.
  6. **`confidence`** — eine Zahl in `[0,1]` (PS-16), die konservative Untergrenze
     für die Wahrscheinlichkeit, dass die `class`-Behauptung angesichts der
     Fehlerbalken der Karte und der Bestätigung hält.
  7. **`steering_flag`** — das Urteil des PS-12-Detektors über die **volle
     erreichbare Stichprobe** des Clients (PS-17) und das Pool-Überlebensverhältnis
     dahinter.
  Ein Prüfer, der **dieselbe Karte `H` hält**, MUSS (MUST) in der Lage sein:
  (a) das `(AS, jurisdiction)` jedes Pivots in `H` neu nachzuschlagen und zu
  bestätigen, dass es Feld 3 entspricht; (b) `class` aus diesen Nachschlägen durch
  den PS-2-Disjunktheitstest neu zu berechnen; (c) `confidence` aus den Feldern 2,
  4, 5 und 7 durch die PS-16-Formel **wie deklariert** neu zu berechnen; und
  (d) zu bestätigen, dass der Datensatz intern konsistent ist. Widerspricht eine
  Neuberechnung, ist das Zertifikat **ungültig** und MUSS (MUST) abgelehnt werden
  (es wurde gegen eine andere Karte berechnet oder gefälscht). Das Zertifikat
  bindet keine Signatur: Wie die Karte selbst (ID-11) ist **die Reproduktion, nicht
  die Signatur, der Schiedsrichter.**

  **Was der Prüfer neu ableiten kann und was nicht — ehrlich dargelegt (ein
  Befund eines feindlichen Reviews).** Zwei Felder sind *Eingaben, die der
  ausstellende Client gemessen hat*, keine Größen, die ein entfernter Prüfer aus
  `H` allein neu berechnen kann: `steering_flag`/`pool_survival` sind Funktionen
  der **vollen erreichbaren Gossip-Stichprobe jenes Clients** (PS-17), die kein
  Zertifikatsfeld ist; und jedes `c_j` ist die **Bestätigungsmessung jenes
  Clients** (PS-15), die ebenfalls nicht aus `H` neu ableitbar ist. Das Zertifikat
  ist also **relativ zu seinen deklarierten Eingaben** prüfbar — ein Prüfer
  bestätigt, dass die Konfidenz aus dem angegebenen `map_error`, der
  `corroboration` und dem `steering_flag` durch die PS-16-Formel folgt — aber es
  ist **kein** bedingungsloser Beweis: Ein Client, der über sein eigenes `c_j`
  nach oben **lügt** oder ein Steuerungs-Flag auslässt, das seine Stichprobe
  gesetzt hätte, erzeugt ein Zertifikat, das sich *konsistent* neu berechnet und
  dennoch falsch ist. Die Abwehrmaßnahmen dagegen stecken nicht im Zertifikat,
  sondern im Netz: Ein unabhängiger Client über demselben `H` und einer
  überlappenden Stichprobe leitet ein **anderes** Zertifikat ab, und die Divergenz
  wird als Anomalie gegossippt (PS-19, ID-10), genau wie eine Karten-Divergenz. Das
  Zertifikat beseitigt das *stille* "AS-disjunkt: ja"; es macht die Konfidenz eines
  lügenden Clients nicht selbstbeweisend. Dies ist eine deklarierte Grenze (§6.6),
  keine verborgene.

### 6.2 Bestätigung: die Konfidenz-Eingabe pro Relais

- **PS-15 (Bestätigung pro Relais ist unabhängige Übereinstimmung, gezählt wie PS-10).**
  Die Eingabe `c_j` für ein Relais ist **kein** Vertrauenswert und DARF NICHT (MUST
  NOT) vom Relais oder von einer einzelnen Partei bezogen werden. Sie ist das Maß,
  in dem das geschlossene AS des Relais **unabhängig bestätigt** ist — dieselbe
  Disziplin "zähle nur unabhängig verifizierte", die PS-10 auf Größenschätzungen und
  GR-8 auf Gossip anwendet:
  - `c_j = 0` — das AS des Relais stammt aus der Karte `H` **und nichts sonst**; der
    Client hat keinen zweiten Blickwinkel. Dies ist der Standard und die
    konservative Untergrenze.
  - `c_j` steigt gegen `1`, wenn **unabhängige, quellengemischte** Blickwinkel (GR-8)
    über dasselbe geschlossene AS für dieses Relais übereinstimmen: eine zweite
    reproduzierbar gebaute Karte aus einer disjunkten Collector-Menge (ID-3a), eine
    Out-of-Band-Beobachtung des angekündigten Präfixes des Relais, ein gegossippter
    Zertifikats-Pivot eines Peers, der passt. Strohmann (s): `c_j = 1 − 2^(−v)` für
    `v` unabhängige bestätigende Blickwinkel (ein Blickwinkel ⇒ 0,5, zwei ⇒ 0,75,
    …), unter `1` gedeckelt, weil keine endliche Anzahl von Overlay-Blickwinkeln den
    Rack sieht (§6.6).
  Ein Relais, das die Karte als `unknown` kennzeichnet, hat `c_j = 0` **und** trägt
  ein bereits konservatives `unknown` geglaubtes AS bei (PS-5): Es kollidiert mit
  allem, überlebt also selten in eine Pivot-Position, und wenn doch, behandelt die
  Konfidenzformel es bereits als vollständig ungewiss (PS-16). Bestätigung DARF
  NICHT (MUST NOT) daraus geschlossen werden, wie *viele* Peers einen Wert melden,
  bevor die GR-8/PS-10-Quellenmischung angewendet wird — ein Sybil kann das AS eines
  Relais nicht durch schiere Zahl in hohe Bestätigung wählen (bindet an OP-2, genau
  wie ID-9).

### 6.3 Die Konfidenzformel

- **PS-16 (Konfidenz ist eine konservative Untergrenze für unabhängige Fehlkennzeichnung).**
  `[claim-critical]` Die **Pivots** einer Circuit-Menge seien die verschiedenen
  Relais an Wächter oder Ausgang über die `n` Circuits (höchstens `2n`, weniger nach
  Deduplizierung). Die behauptete Disjunktheit hält **nur dann, wenn kein Pivot
  fehlgekennzeichnet** ist, und zwar so, dass ein als verschieden geglaubtes Paar in
  ein wahrhaft kollidierendes verwandelt wird. Die Karte liefert den Fehler pro
  Nachschlag `e = mismap_rate + unknown_rate` (ID-12); Bestätigung reduziert die
  **effektive** Fehlkennzeichnungswahrscheinlichkeit eines Pivots auf
  ```
      p_j = e · (1 − c_j).
  ```
  Behandelt man die Fehlkennzeichnungen pro Pivot als **unabhängig**, ist die
  `confidence` des Zertifikats für `class = as` das Produkt
  ```
      confidence  =  Π_j ( 1 − e · (1 − c_j) )       über Pivots j,
  ```
  durch das PS-17-Steuerungsgatter auf `0` gedrückt. Für `class = node` hängt die
  Disjunktheit überhaupt nicht von der Karte ab (Knotenidentität ist GR-2-gebunden,
  nicht geschlossen), also `confidence = 1 − (PS-17-Gatter)`. Für `class = none`
  ist `confidence = 0` per Definition: Es wird keine Disjunktheit behauptet, also
  wird keine attestiert.

  **Die Unabhängigkeitsannahme, benannt und als konservativ begründet.** Reale
  Pivot-Fehlkennzeichnungen sind **nicht** unabhängig: Ein falsches BGP-Präfix in
  der Karte kennzeichnet jedes Relais darunter auf einmal fehl (positive
  Korrelation). Wir nehmen trotzdem Unabhängigkeit an, und das ist **konservativ in
  der Richtung, auf die es ankommt** für eine *Untergrenze*: Das Produkt
  `Π(1 − p_j)` zählt den *korrelierten* Fall zu niedrig, in dem mehrere Pivots eine
  Fehlkennzeichnungsursache teilen — sind Fehlkennzeichnungen korreliert, ist die
  Wahrscheinlichkeit, dass *mindestens ein* Pivot falsch ist, **niedriger**, als das
  unabhängige Produkt impliziert, also ist die wahre Wahrscheinlichkeit "alle Pivots
  korrekt" **höher** als unsere Schranke. Das Produkt ist somit eine Untergrenze für
  die Konfidenz, d.h. es überzeichnet die Sicherheit nie. Wo Unabhängigkeit uns
  *über*zuversichtlich machen würde, ist eine gemeinsame *ehrliche* Ursache (ein
  riesiges korrektes AS), die die Disjunktheit nicht bedroht; die adversarische
  gemeinsame Ursache — eine Karte, die den Pool kollabiert — wird von diesem Produkt
  gar nicht behandelt, sondern vom PS-17-Gatter, das die Konfidenz unabhängig vom
  Produkt auf 0 drückt. So werden die zwei Fehlerformen sauber getrennt:
  **zufälliger/korrelierter Kartenfehler → das Produkt (konservativ);
  adversarische Kartenstruktur → das Gatter (harte Untergrenze).**

  Verankerung (nicht herbeigeredet). Gegen `poc/network_sim.py` begrenzt ohne
  Bestätigung (`c_j = 0`, also `p_j = e`) `1 − confidence` die **beobachtete**
  Real-AS-Kollisionsrate der Pivots auf jeder Fehlerstufe nach oben — z.B. bei
  `e = 0.2` ist `1 − confidence ≈ 0.83` gegenüber einem beobachteten
  Real-Disjunktheits-Versagen von `≈ 0.18`: pessimistisch, was die richtige Richtung
  für eine Sicherheits-Untergrenze ist, niemals optimistisch. Bestätigung stellt sie
  monoton wieder her (bei `e = 0.2` steigt die mittlere Konfidenz
  `0.17 → 0.43 → 0.84 → 0.99`, wenn das gleichmäßige `c_j` `0 → 0.5 → 0.9 → 1.0`
  durchläuft). Ein konformer Client SOLLTE (SHOULD) diesen ehrlichen Pessimismus
  darstellen, statt die Schranke mit einem Modell zu straffen, das mehr annimmt, als
  die drei deklarierten Eingaben rechtfertigen — eine vertretbare Untergrenze
  schlägt falsche Präzision (PS-11).

### 6.4 Robustheit gegen PS-12, durch Konstruktion

- **PS-17 (das Steuerungsgatter drückt die Konfidenz auf die Untergrenze — auf dem
  richtigen Signal, über die VOLLE erreichbare Stichprobe).** `[claim-critical]`
  Bevor das Produkt aus PS-16 gemeldet wird, MUSS (MUST) das Verfahren den
  PS-12-Verteidigung-2-Detektor (`detect_steering`) auf die **gesamte erreichbare
  Gossip-Stichprobe** des Clients anwenden, nicht auf die `2n` gewählten Pivots —
  die Struktur lebt in der *Population* und ist aus den Pivots verschwunden, bis sie
  gezogen werden (eine Prüfung allein der Pivots erfasst eine lenkende Karte bei nur
  ~der Hälfte der Nachrichten). **Das Signal muss jenes sein, dem der Gegner nicht
  ausweichen kann.** Eine erste Version dieses Detektors knüpfte an "ein riesiges
  geglaubtes AS, das den kollabierten ehrlichen Pool hält, umgeben von
  Einzelgängern" an, und ein feindliches Review **umging sie**, indem es den
  ehrlichen Pool stattdessen in *einige wenige* gefälschte ASes kollabierte — kein
  riesiges AS, Detektor stumm, Inhalt bei ~30 % der Nachrichten gebrochen. Das
  korrekte, tragende Signal ist der **anomale Einzelgänger-Anteil**: Um seine
  ko-lokalisierten Relais AS-disjunkt aussehen zu lassen, MUSS (MUST) der Gegner
  jedem ein eigenes gefälschtes AS geben, d.h. sie zu Einzelgängern machen, und ein
  reales Netz hat sehr wenige Einzelgänger-ASes. Der Detektor MUSS (MUST) daher
  feuern, wenn Einzelgänger-Relais einen kleinen Anteil der Stichprobe überschreiten
  **und** die Nicht-Einzelgänger-Relais in zu wenigen vollen ASes sitzen, um `n`
  disjunkte Circuits zu bauen (die zweite Klausel hält Schlussfolgerungs-*Rauschen*,
  das ebenfalls Einzelgänger erzeugt, davon ab, ihn auszulösen). Gemessen gegen
  `poc/network_sim.py` (`make_steering_map(honest_groups=g)` / der korrigierte
  `detect_steering`): Dies fängt das **effektive** Lenkungsregime (`g = 1…5`, ein
  10–100 % Inhaltsbruch) zu ~100 % mit **0 %** Falsch-Positiven auf ehrlichen Karten
  selbst bei Schlussfolgerungsfehler bis 0,4. Daher:
  - Feuert der Detektor auf der erreichbaren Stichprobe, MUSS (MUST) das Zertifikat
    `steering_flag = true`, `class = none` und `confidence = 0` setzen, und der
    Client MUSS (MUST) das Ergebnis als PS-12-Rückfall-/Anomalie-Bedingung behandeln
    (gossippe es, ID-10; degradiere und sage es, PS-8/PS-9) — er DARF NICHT (MUST
    NOT) ein `as`-Zertifikat ausgeben.
  - **Deklariertes Residuum:** Eine *marginale* lenkende Karte, die den ehrlichen
    Pool über genug gefälschte ASes (`g ≥ 8`) verteilt, um wahrhaft disjunkte
    Circuits zu bauen, entkommt dem Detektor — aber dort beträgt ihr Inhaltsbruch nur
    ~5 %, nicht unterscheidbar von einem kleinen legitimen Netz, und begrenzt durch
    die `k`/`n`-Marge und die PS-16-Konfidenz, nicht durch eine Behauptung, dass es
    nicht geschehen kann (§6.6).

- **PS-18 (Pool-Kollaps-Vorbedingung — PS-12-Verteidigung 1, als Konfidenz-Eingabe
  eingefaltet).** `[claim-critical]` Unabhängig vom strukturellen Detektor MUSS
  (MUST) das Verfahren das **Überlebensverhältnis des ehrlichen Pools** berechnen:
  den Anteil der erreichbaren, unabhängig bestätigten Stichprobe (PS-10, PS-15 mit
  `c_j > 0`), der **nach** dem Ziehen des ersten Circuits ein
  *als-verschieden-geglaubtes-AS*-Kandidat bleibt. Ein Zertifikat DARF NICHT (MUST
  NOT) `class = as` behaupten, wenn die Circuits `2…n` aus einem Pool gezogen wurden,
  den die Karte unter einen begrenzten Anteil kollabierte (Strohmann (s): Überleben
  `< 1/n` der bestätigten ehrlichen Stichprobe), denn dann beruht die behauptete
  gegenseitige Disjunktheit der Menge auf Relais, die der Client nicht *unabhängig*
  als verschieden bestätigen kann — genau PS-12-Verteidigung 1. In diesem Fall MUSS
  (MUST) das Verfahren entweder `class` auf `node` senken (die kartenabhängige
  Behauptung ganz fallen lassen) oder die Anomalie-Bedingung wie in PS-17 setzen.
  **Die Konfidenz ist genau dann NIEDRIG, wenn PS-12 sagt, dass der Client gelenkt
  wird:** Das Gatter nullt sie auf der strukturellen Signatur, und die
  Überlebens-Vorbedingung streift die `as`-Behauptung ab, wenn der Pool verdächtig
  dünn ist — eine lenkende Karte kann sich also kein `as`-Zertifikat mit hoher
  Konfidenz über einen der beiden Hebel verdienen (gegnerische ASes als verschiedene
  Fälschungen oder ehrliche ASes als kollidierende Fälschungen). Dies ist die nicht
  verhandelbare Eigenschaft, und sie wird verifiziert, nicht behauptet: Dasselbe
  Gatter, das die PS-12-Tests aus einem 100 % Inhaltsbruch einen 100 % Rückfall
  machen lassen, treibt die Zertifikatskonfidenz bei 100 % der lenkenden Karten
  auf 0.

### 6.5 Ein durchgerechnetes Zertifikat

Eingaben: `n = 4`, `k = 3`; eine gesunde Stichprobe; Karte `H = 0x9f2c…a17b`, die
`map_error = (0.04, 0.03)` ausliefert, also `e = 0.07`; die 8 Pivots (4 Wächter +
4 Ausgänge) — 6 bestätigt durch einen zusätzlichen unabhängigen Blickwinkel
(`c_j = 0.5`), 2 allein auf der Karte ruhend (`c_j = 0.0`); der Steuerungs-Detektor
feuert auf der erreichbaren Stichprobe **nicht**. Dann ist `p_j = 0.035` für die
sechs und `0.07` für die zwei, und
`confidence = (1−0.035)^6 · (1−0.07)^2 = 0.698`.

```
disjointness-certificate (canonical CBOR; shown as a record):
  map_hash      : 0x9f2c3e...a17b
  map_error     : { mismap: 0.04, unknown: 0.03 }         # e = 0.07 (ID-12)
  class         : "as"                                     # stärkste erfüllt, PS-2
  confidence    : 0.698                                    # PS-16-Produkt, Gatter=1
  steering_flag : false                                    # PS-17, Vollsicht-Prüfung
  pool_survival : 0.61                                     # PS-18, > 1/n = 0.25 OK
  circuits:
    - { guard: 4a1f.., mid: 7c02.., exit: e9d3..,
        pivots:[{as:3356, jur:"US", c:0.5},{as:1299, jur:"SE", c:0.5}] }
    - { guard: b17c.., mid: 02aa.., exit: 55f1..,
        pivots:[{as:3320, jur:"DE", c:0.5},{as:9002, jur:"GB", c:0.0}] }
    - { guard: cc90.., mid: 1d44.., exit: a7e8..,
        pivots:[{as:6830, jur:"NL", c:0.5},{as:2914, jur:"JP", c:0.5}] }
    - { guard: 3e5b.., mid: f108.., exit: 9b22..,
        pivots:[{as:174,  jur:"US", c:0.0},{as:8075, jur:"IE", c:0.5}] }
```
Richtig gelesen (PS-9): *"Diese 4 Circuits sind AS-disjunkt **unter Karte `H`**, die
eine 7 % Fehlerrate zulässt; angesichts dessen, wie unabhängig das AS jedes Relais
bestätigt ist, besteht mindestens eine **70 % Chance**, dass die AS-Disjunktheit
real ist und kein Artefakt einer Fehlkennzeichnung. Es ist keine Garantie, und es
sagt nichts über ein Rechenzentrum, das die Karte nicht sehen kann (§6.6)."* Hätte
der Steuerungs-Detektor gefeuert, würde jede Zahl oben durch
`class: none, confidence: 0, steering_flag: true` und eine Rückfall-Warnung ersetzt
— es gibt kein Zertifikat mit hoher Konfidenz für einen gelenkten Client.

```
  DER CIRCUITS-UND-ZERTIFIKAT-ERZEUGUNGSFLUSS

   sample (PS-10)      map H + e (ID-12)      corroboration c_j (PS-15)
        │                   │                        │
        └─────────┬─────────┴───────────┬────────────┘
                  ▼                      ▼
        ┌────────────────────┐   ┌─────────────────────────────┐
        │ detect_steering    │   │ als-AS-disjunkt auswählen   │
        │ auf VOLLER Probe   │   │ (PS-2-Ordnung: as→node→none)│
        │ (PS-17, Verteid. 2)│   │ + Pool-Überleben (PS-18,    │
        └─────────┬──────────┘   │     Verteidigung 1)         │
                  │              └──────────────┬──────────────┘
         feuert?  │                             │ n Circuits + Pivots
         ┌────────┴────────┐                    ▼
       ja                nein      ┌────────────────────────────┐
         │                 └──────▶│ confidence = Π(1−e(1−c_j)) │ PS-16
         ▼                         │ class = stärkste erfüllt   │
  class=none, conf=0               └──────────────┬─────────────┘
  steering_flag=true                              ▼
  → Rückfall + Gossip        ┌─────────────────────────────────────┐
    (PS-8/9, ID-10)          │ ZERTIFIKAT {map_hash, map_error,    │
                             │ circuits, corroboration, class,     │
                             │ confidence, steering_flag}          │
                             └──────────────┬──────────────────────┘
                                            ▼
                     ein Prüfer mit DEMSELBEN H berechnet neu und bestätigt
                     (Reproduktion ist der Schiedsrichter — keine Signatur, ID-11)
```

- **PS-19 (das Zertifikat ist für den Nutzer und den Peer, beide).** Die
  `confidence` und `class` MÜSSEN (MUST) die PS-9-Ehrlichkeitsoberfläche treiben,
  die der Nutzer liest (*die Menge ist heute so disjunkt, mit so viel Gewissheit*),
  und das Zertifikat MUSS (MUST) gossippbar sein, damit ein Peer, der dasselbe `H`
  hält, es neu ableiten kann (PS-14) und damit eine Divergenz — zwei Clients,
  dasselbe `H` und dieselbe Stichprobe, ein anderes Zertifikat — erfasst und als
  Anomalie gegossippt wird (ID-10), dasselbe Immunsignal, das Teil 8 für
  Karten-Divergenz verwendet. Die UI DARF NICHT (MUST NOT) `confidence` so zitieren,
  als begrenze sie Verknüpfung: Sie begrenzt die **Inhalts**-Disjunktheits-Behauptung;
  Metadaten degradieren schneller (PS-11(a)), und eine hohe Konfidenz in
  `class = as` bedeutet nicht wenig Verknüpfungsleck.

### 6.6 Was dies nicht löst

Das Zertifikat attestiert **Konsistenz gegen einen Datensatz mit begrenztem
Vertrauen, nicht echte Disjunktheit** (Teil 8 §10), und die Ehrlichkeit dieses
ganzen Verfahrens besteht darin, dies auf jedem Datensatz zu sagen. Ein Gegner, der
Relais in einem Rack ko-lokalisiert, während er Adressraum ankündigt, den die
öffentlichen BGP/RIR-Daten **wahrheitsgemäß** verschiedenen ASes zuschreiben, wird
von der **korrekten** Karte als disjunkt gekennzeichnet — also stimmen die
Nachschläge mit `H` überein, der Steuerungs-Detektor feuert nicht (die Struktur ist
keine Lenkungssignatur, sie ist die echte öffentliche Routing-Tabelle), der Pool
kollabiert nicht, und die Pivots sind gut bestätigt, **weil jeder ehrliche
Blickwinkel mit der Karte übereinstimmt**. Das Verfahren stellt daher ein
**`as`-Zertifikat mit hoher Konfidenz aus, das dennoch falsch ist**: `confidence`
misst die Chance, dass die Menge *unter der Karte* disjunkt ist, und hier ist die
Karte richtig und das Overlay kann den Rack trotzdem nicht sehen. Dies ist das
Ko-Lokationsresiduum aus Teil 8 §10, und es ist die eine Beschränkung, die das
Zertifikat **nicht** beseitigen kann — keine Menge an Bestätigung schließt sie,
weil Bestätigung nur die Übereinstimmung *mit öffentlichen Daten* bestätigt, und die
öffentlichen Daten selbst sind das, was der Gegner erfüllt hat. Ihr Ausmaß ist genau
die Lücke des Simulators zwischen geglaubtem und wahrem AS bei `infer_error = 0`:
Das Zertifikat liest 1.0, die Realität kann trotzdem kollidieren, und nur das
Anheben der `k`/`n`-Marge — kein Zertifikatsfeld — begrenzt den Verlust. Die Gabe
des Zertifikats ist, dass es dies nie **verbirgt**: Es gibt seine eigenen
Fehlerbalken an, drückt sich unter Lenkung auf null (PS-17/18) und ist für jeden mit
der Karte prüfbar (PS-14). Es verwandelt "AS-disjunkt: ja" — eine Lüge — in
"AS-disjunkt unter Karte `H` mit Fehler `e`, Konfidenz `c`" — eine wahre Aussage,
deren einziger verbleibender blinder Fleck hier benannt und nirgends verborgen wird.

Drei weitere Grenzen, die ein feindliches Review zutage förderte, hier deklariert
statt übertüncht:

- **Marginale Lenkung entkommt dem Detektor.** Eine lenkende Karte, die den ehrlichen
  Pool über genug gefälschte ASes (`g ≥ 8`) verteilt, baut wahrhaft disjunkte
  Circuits und löst daher den Einzelgänger-Anteil-Detektor (PS-17) nicht aus — aber
  ihr Inhaltsbruch beträgt dann nur ~5 %, die Stufe eines kleinen legitimen Netzes,
  begrenzt durch die `k`/`n`-Marge und die PS-16-Konfidenz. Der Detektor fängt das
  *effektive* Lenkungsregime (10–100 % Bruch), nicht jede Karte.
- **Die Konfidenz eines lügenden Clients ist nicht selbstbeweisend.** `confidence`
  ist nur so ehrlich wie das `c_j` und das `steering_flag`, die der ausstellende
  Client gemessen und ins Zertifikat gesetzt hat; ein Client, der seine eigene
  Bestätigung übertreibt oder ein Flag auslässt, gibt ein Zertifikat aus, das sich
  konsistent neu berechnet und dennoch falsch ist (PS-14). Der Haken ist sozial,
  nicht arithmetisch: Ein unabhängiger Client über demselben `H` leitet ein anderes
  Zertifikat ab, und die Divergenz wird als Anomalie gegossippt (PS-19). Das
  Zertifikat beseitigt die *stille* Lüge, nicht eine *erkennbare*.
- **Das Konfidenzprodukt begrenzt Pivot-Paar-Kollisionen, nicht jede Kollision.**
  PS-16 misst die Chance, dass ein als disjunkt geglaubtes Pivot-*Paar* wahrhaft
  kollidiert. Eine Fehlkennzeichnung, die einen Pivot mit einem *Mittel*-Hop
  kollidiert oder Jurisdiktion mit AS verwechselt, liegt außerhalb des Produkts und
  muss vom PS-2-Disjunktheitstest auf dem vollen Circuit gefangen werden, nicht aus
  der Konfidenzzahl abgelesen.


## 7. Was dieser Teil nicht entscheidet

Die vertrauenslose Verteilung des Disjunktheits-Datensatzes und die formale
Verifikation, dass eine gewählte Menge so disjunkt ist wie behauptet (OP-1); die
ehrlichen Schwellen der tragfähigen Größe und ob `n = 2, k = 2` überhaupt
auszuführen lohnt (OP-3); die Ökonomie der Wächter-Rotation; die Pfadauswahl
über dem Blackout-Mesh, wo AS und Jurisdiktion nichts bedeuten (OP-6).
`poc/network_sim.py` ist der ausführbare vorläufige Wert hinter diesem Teil —
greife sein Modell an, dann diesen Text.
