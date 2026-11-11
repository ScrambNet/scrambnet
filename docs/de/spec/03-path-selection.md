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
  Verknüpfungsleck steigen monoton. Zwei Folgerungen sind normativ: (a) Der
  Fehler untergräbt die **Verknüpfung weit schneller als den Inhalt** — ein
  Inhaltsbruch erfordert weiterhin, dass der Gegner auf `≥ k` Circuits
  gleichzeitig sitzt, sodass die Untergrenze hält, während die Metadaten zuerst
  degradieren; die UI DARF NICHT (MUST NOT) eine niedrige Inhaltsbruchzahl so
  darstellen, als begrenze sie auch die Verknüpfung; (b) eine dünnere
  **Gossip-Stichprobe** (PS-10, I-3) erzwingt das Zurückfallen früher: Ein
  Client, der zu wenige Relais kennt, kann überhaupt keine AS-disjunkten
  Circuits aufbauen und fällt auf `none` zurück, wo die Bruchrate springt (§2).
  Die Schätzung der tragfähigen Größe (PS-10) MUSS (MUST) daher die
  *erreichbare* Stichprobe berücksichtigen, nicht das gesamte Netz. Die Zahlen
  bei null Fehler und voller Sicht sind der beste Fall; ein konformer Client MUSS
  (MUST) die erreichte Stufe (PS-9) aus seiner realen, verrauschten, partiellen
  Sicht darstellen.

## 6. Was dieser Teil nicht entscheidet

Die vertrauenslose Verteilung des Disjunktheits-Datensatzes und die formale
Verifikation, dass eine gewählte Menge so disjunkt ist wie behauptet (OP-1); die
ehrlichen Schwellen der tragfähigen Größe und ob `n = 2, k = 2` überhaupt
auszuführen lohnt (OP-3); die Ökonomie der Wächter-Rotation; die Pfadauswahl
über dem Blackout-Mesh, wo AS und Jurisdiktion nichts bedeuten (OP-6).
`poc/network_sim.py` ist der ausführbare vorläufige Wert hinter diesem Teil —
greife sein Modell an, dann diesen Text.
