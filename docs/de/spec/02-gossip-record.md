# ScrambNet-Spezifikation — Teil 2: Gossip-Eintrag
> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../../en/spec/02-gossip-record.md)).

**Status: ENTWURF (DRAFT).** Strohmann-Werte mit `(s)` markiert. Die Sybil-/Eclipse-Fragen, auf die sich dieser
Teil stützt, sind OP-2 und absichtlich offen.

## 1. Geltungsbereich

Der Gossip-Eintrag ist der selbstsignierte Deskriptor, durch den ein Relais existiert. Es gibt
kein Verzeichnis, keine Autorität, keine Registrierung (I-3): ein Relais ist die Menge der Einträge,
die es signiert, und die Karte des Netzes ist die überprüfbare Stichprobe, die jeder Client hält.

## 2. Eintragsformat

- **GR-1.** Ein Eintrag ist eine kanonische CBOR-Map (RFC 8949 §4.2.1), höchstens
  `1024` Bytes (s) kodiert. Größere Einträge MÜSSEN (MUST) ungelesen verworfen werden.
- **GR-2.** Felder (Ganzzahl-Schlüssel; unbekannte Schlüssel MÜSSEN (MUST) zur Vorwärts-
  kompatibilität ignoriert werden, sind aber von der Signatur abgedeckt):

| Schlüssel | Name | Typ | Anmerkungen |
|---|---|---|---|
| 0 | `v` | uint | Formatversion, `1` |
| 1 | `id` | bytes(32) | Ed25519-Identitäts-Öffentlichkeitsschlüssel — der Name des Relais |
| 2 | `onion` | bytes(32) | X25519-Schlüssel für Circuit-Handshakes; MUSS ≤ 7 Tage rotieren (s) |
| 3 | `addrs` | array | Endpunkte: Paare `[transport-id uint, blob bytes]` |
| 4 | `bw` | uint | behauptete dauerhafte Bandbreite, kB/s — eine *Behauptung*, siehe GR-7 |
| 5 | `created` | uint | Unix-Zeit, MUSS auf die Stunde abgerundet werden (GR-5) |
| 6 | `expiry` | uint | Unix-Zeit, MUSS ≤ `created` + 7 Tage sein (s) |
| 7 | `sig` | bytes(64) | Ed25519 über die kanonische Kodierung mit abwesendem Schlüssel 7 |

- **GR-3.** Ein Relais DARF NICHT (MUST NOT) geografische oder jurisdiktionelle Behauptungen über
  sich selbst veröffentlichen. Clients schließen AS und Jurisdiktion aus `addrs` mit ihren eigenen Daten
  (OP-1); selbstdeklarierter Standort ist eine Angriffsfläche, keine Information.
- **GR-4.** Signaturgültigkeit, Größenobergrenze, Ablauf und Zeitstempel-Rundung MÜSSEN (MUST) alle
  geprüft werden, bevor ein Eintrag gespeichert oder weitergeleitet wird; Fehlschläge werden
  still verworfen — kein Fehler, der „fehlgeformt" von „abgelaufen" unterscheidet, darf vom
  Absender des Eintrags beobachtbar sein.
- **GR-5.** Die `created`-Rundung existiert, um das Clock-Skew-Fingerprinting von Relais zu stoppen.
  Clients MÜSSEN (MUST) zwei Einträge mit demselben `id` als ein Relais behandeln und
  nur das frischeste `created` behalten.

## 3. Austausch und Abtastung

- **GR-6.** Einträge reisen über etablierte Circuits und über das lokale Mesh
  (Teil 5), huckepack in Chargen fester Größe: eine Gossip-Charge sind `8` Einträge (s),
  auf konstante Größe aufgefüllt, höchstens einmal je Peer je `10` Minuten (s) ausgetauscht.
  Ein Knoten beantwortet eine Stichprobenanfrage mit einer gleichverteilten Stichprobe seiner gespeicherten Einträge;
  er DARF NICHT (MUST NOT) mit einer von der Identität des Anfragers verzerrten Stichprobe antworten (der
  offensichtliche Eclipse-Hebel).
- **GR-7.** `bw` ist eine Behauptung. Clients SOLLTEN (SHOULD) Behauptungen durch randomisiertes Sondieren
  über Circuits verifizieren, die den Sondierer nicht preisgeben, und SOLLTEN (SHOULD) die Pfadauswahl
  nach verifizierter Bandbreite gewichten, nicht nach behaupteter. Der Sondierentwurf ist offen (OP-2).
- **GR-8 (Quellenmischung).** Die gespeicherte Stichprobe eines Clients MUSS (MUST) Einträge aus
  unabhängigen Quellklassen mischen — mindestens: Social-Graph-Brücke (Lox-artig),
  Gossip-Austausch und direktes Sondieren — und DARF NICHT (MUST NOT) zulassen, dass eine einzelne Klasse
  einen konfigurierbaren Anteil (Strohmann 1/2) der Stichprobe übersteigt. Dies ist die
  Eclipse-Verteidigung, bis OP-2 etwas Stärkeres hervorbringt.
- **GR-9.** Neue Identitäten sind qua Entwurf billig (keine Registrierung), also darf nichts in
  diesem Teil Sybil-Resistenz aus den Identitätskosten annehmen. Jeder Mechanismus, der
  Sybil-Resistenz braucht, muss sie aus verifizierten Ressourcen beziehen (Bandbreite,
  langfristige Betriebszeit, vom Client selbst beobachtet) oder aus dem sozialen Graphen — nie
  aus dem Eintrag allein.

## 4. Bootstrap

- **GR-10.** Ein frischer Client MUSS (MUST) von einer einzigen Out-of-Band-Brücken-Zeile
  (einem QR-Code, einer gedruckten Zeichenkette, einer Nachricht von einem Freund) starten können, die
  einen Eintrag plus einen Transport-Hinweis enthält. Null-Kontakt-Bootstrap ist OP-7 und offen.

## 5. Das Bandbreiten-Sondierprotokoll (Abschluss von GR-7)

GR-7 besagt, dass `bw` eine Behauptung ist und durch „randomisiertes Sondieren über
Circuits, die den Sondierer nicht preisgeben" verifiziert werden SOLLTE, und erklärt dann
den Sondierentwurf für offen. Dieser Abschnitt ist dieser Entwurf. Die Sonde beantwortet genau
eine Frage — *welchen Durchsatz kann ich, dieser Client, gerade jetzt durch dieses Relais
schieben, über einen Circuit, der mich nicht benennt?* — und sie beantwortet sie für den
anfragenden Client allein. Es gibt **keine** veröffentlichte, geteilte oder autoritative
Bandbreitenzahl: Tors Bandbreiten-Autoritäten sind genau der zentrale Allokator, den I-3 uns
verwehrt (PS-10, GR-9), also leitet jeder Client seine eigene verifizierte Zahl ab und gewichtet
seine eigene Pfadauswahl (PS-7) danach.

### 5.1 Die Messung, und wovon sie eine reine Funktion ist

- **GR-11 (verifizierte Bandbreite ist eine clientweise Selbstmessung, nie eine veröffentlichte
  Zahl).** `[claim-critical]` Die verifizierte Bandbreite eines Clients für Relais `R`,
  geschrieben `vbw(R)`, MUSS (MUST) als deterministische Funktion von Eingaben berechnet werden, die
  der Client **selbst** beobachtet hat:
  ```
      vbw(R, epoch) = probe(circuits_through_R, bytes_sent, timestamps_seen)
  ```
  und von nichts, das ein Relais, ein Peer oder eine dritte Partei behauptet. `vbw` ist eine lokale
  Variable, kein Netzwerkwert: zwei ehrliche Clients, die dasselbe `R` sondieren, werden
  **unterschiedliche** `vbw(R)` ableiten (ihre Pfade, ihre Überlastung, ihr Moment), und
  das ist korrekt — es gibt kein wahres skalares „Bandbreite von `R`", auf das man sich einigen
  könnte, nur *den Durchsatz, den ein gegebener Client über einen gegebenen Pfad zu einer gegebenen
  Zeit erreicht hat* (GR-18). Ein Client MUSS (MUST) die `bw`-Behauptung eines unsondierten Relais
  als den **Niedrig-Bandbreiten-Standard** (PS-7) behandeln, nie als dessen Zahl; eine Behauptung,
  die der Client nicht selbst gemessen hat, trägt kein Gewicht in der Auswahl.

- **GR-12 (die Sonde ist ein versiegelter Rundlauf über einen Circuit — der Sondierer wird nie
  benannt).** `[claim-critical]` Eine Sonde MUSS (MUST) als gewöhnlicher Circuit-Verkehr getragen werden:
  der Client baut einen Circuit, dessen **gemessenes Relais `R` der mittlere Hop ist**, sendet
  einen begrenzten Zug von Zellen in Share-Paket-Form (Teil 1: feste `P = 2048` Bytes,
  SP-3), adressiert durch `R`, und misst den Rundlauf-Durchsatz des Zuges,
  wie er über denselben Circuit zurückkehrt. `R` sieht eine Zelle von seinem Vorgänger ankommen
  und zu seinem Nachfolger abgehen — genau das, was es bei echtem weitergeleitetem Verkehr sieht — und
  **kann den Client nicht sehen**: der Sondierer sitzt mindestens einen Hop jenseits von `R`s Sicht, wie
  in jedem Sphinx-Circuit (SP-4). Die Sonde DARF NICHT (MUST NOT) irgendeinen Zelltyp, Flag, eine Länge
  oder Kadenz verwenden, die sie von weitergeleitetem Nutzerverkehr unterscheidet (I-4, und GR-13
  unten). Ein Relais, das eine Sonde von einer Nutzlast unterscheiden könnte, könnte die Sonde bestehen
  und die Nutzlast scheitern lassen; also kann ihm per Konstruktion diese Chance nicht gegeben werden.

```
  DIE SONDE ÜBER EINEN CIRCUIT  (R wird gemessen; der Sondierer ist nie in R's Sicht)

   Client (Sondierer)      Wächter G      Relais R  (im Test)           Schwanz T
   ──────────────────      ─────────      ────────────────────         ─────────
        │                    │                  │                          │
        │  baue Circuit  C = [ G , R , T ]  (R ist der MITTLERE Hop)       │
        │───────────────────▶│                  │                          │
        │     Zug von N Zellen fester Größe, ununterscheidbar von          │
        │     echten weitergeleiteten Share-Paketen (SP-3/SP-4, I-4)       │
        │════════════════════╪═════════════════▶│═════════════════════════▶│
        │                    │                  │   T echot den Zug zurück │
        │◀═══════════════════╪══════════════════╪══════════════════════════│
        │   miss: bytes_acked / (t_last − t_first)  = Durchsatz-Stichprobe │
        │          dieser Sonde für R, DIESER Pfad, DIESER Moment          │
        │                    │                  │                          │
      vbw(R) ← robuste Aggregation vieler solcher Stichproben über Zeit (GR-16)

   Was R sieht:  Zellen von G  →  Zellen zu T.   Identisch zum Tragen echten
   Verkehrs.  R sieht NICHT „Client", sieht NICHT „das ist eine Sonde", und
   kann sich nicht nur-wenn-beobachtet gut verhalten, weil es nicht erkennen
   kann, dass es beobachtet wird.  Die Kosten werden vom Sondierer GETRAGEN: er
   sendet N·P Bytes, die er nicht als nützliche Arbeit zurückbekommt (GR-14).
   R kann nicht dazu gebracht werden, ein Opfer zu fluten, denn der Zug kehrt zum
   SONDIERER zurück, nie zu einer vom Angreifer benannten dritten Partei (GR-15).
```

### 5.2 Die fünf Eigenschaften, die die Sonde haben muss

- **GR-13 (Ununterscheidbarkeit — ein Relais kann sich nicht nur verhalten, wenn beobachtet).**
  `[claim-critical]` Die Anti-Gaming-Eigenschaft ist Draht-Uniformität (I-4): **Sonden-
  verkehr MUSS (MUST) Byte für Byte und Timing für Timing ununterscheidbar sein von dem
  echten weitergeleiteten Verkehr, den ein Relais tragen soll**, sodass das Relais seine
  Weiterleitung nicht an „werde ich gerade gemessen?" koppeln kann. Konkret MÜSSEN (MUST) die
  Sonden-Zellen volle Share-Pakete aus Teil 1 sein (`P = 2048` Bytes, SP-3), MÜSSEN (MUST) unter
  derselben Batching-/Jitter-Disziplin emittiert werden, die ein echter Absender verwendet (SP-6, SP-9),
  und DÜRFEN NICHT (MUST NOT) irgendeinen sondenspezifischen Marker tragen. Ein Relais, das echten
  Verkehr unterversorgt und Sonden überversorgt, müsste sie unterscheiden; I-4 verwehrt ihm die
  Information, dies zu tun. Die gemessene `vbw(R)` ist daher eine Untergrenze dessen, was `R` für den
  echten Verkehr dieses Clients weiterleiten *würde*, weil `R` die beiden nicht auseinanderhalten kann —
  was der ganze Sinn ist: *greife dies an, indem du ein Bit findest, auf das das Relais schlüsseln kann.*

- **GR-14 (die Sonde kostet den Sondierer einen begrenzten, vorab bezahlten Betrag).** Eine einzelne
  Sonde von `R` MUSS (MUST) höchstens `B_probe` Bytes senden (Strohmann: `B_probe = 1 MiB`
  verteilt über `≥ τ` Sekunden, `τ = 4 s` (s)) und MUSS (MUST) auf höchstens eine
  im Flug befindliche Sonde pro Zielrelais und höchstens `Q` gleichzeitige Sonden insgesamt pro
  Client rate-begrenzt werden (Strohmann `Q = 8` (s)). Der Sondierer gibt echte Bytes aus, die er nicht
  als nützliche Arbeit zurückgewinnt; das sind die Kosten, die das Sondieren selbstbegrenzend machen. Ein Client DARF
  NICHT (MUST NOT) ein Relais häufiger als einmal je `T_probe` sondieren (Strohmann: Stunden, nicht
  Minuten (s)) — Bandbreite ändert sich langsam relativ dazu, wie schnell eine Messung altert,
  also bringt häufiges Neu-Sondieren wenig und kostet linear (GR-16).

- **GR-15 (die Sonde kann kein DoS-Verstärker werden).** `[claim-critical]` Das
  gemessene Relais MUSS (MUST) Sondenverkehr immer nur **an den Sondierer zurückgeben, über denselben
  Circuit, auf dem er ankam** — nie an irgendeine Adresse, die die Zellen des Sondierers benennen könnten.
  Weil der Schwanz-Hop `T` den Zug entlang `C` zurück zu dem Client echot, der `C` gebaut hat, ist eine Sonde
  eine **geschlossene Schleife**: die Arbeit, die eine Sonde auslöst, ist durch das begrenzt, was der
  Sondierer selbst gesendet hat (Verstärkungsfaktor ≤ 1 per Konstruktion, nicht per Richtlinie), und
  es gibt kein Feld, in das ein Angreifer die Adresse eines Opfers schreiben könnte, um `R`
  es fluten zu lassen. Das ist der strukturelle Unterschied zu jedem „bitte das Relais, einen
  Teststrom an Adresse X zu senden"-Entwurf, der ein Reflektor wäre und **verboten** ist:
  eine Sonde DARF NICHT (MUST NOT) ein Ziel akzeptieren, das sie nicht selbst terminiert. Eine
  Implementierung, die die Sonde eine dritte Partei anvisieren lässt, ist nicht konform.

- **GR-16 (eine Sonde misst einen Pfad-Moment; `vbw` ist eine robuste Aggregation vieler).**
  Eine einzelne Sonde ist eine Stichprobe *eines Pfades zu einem Augenblick*, verunreinigt durch die
  eigene Kapazität des Wächters und Schwanzes, durch Querverkehr und durch Überlastung irgendwo auf
  `C`. Ein Client MUSS (MUST) daher (a) `R` durch **mehrere unabhängige Circuits** sondieren
  (verschiedene Wächter und Schwänze, GR-8-quellengemischt wo möglich), (b) `R` den
  **maximalen beobachteten dauerhaften Durchsatz** über diese Circuits in einem Fenster zuordnen
  (das Maximum, weil der Flaschenhals eines einzelnen Circuits eine *Untergrenze* für
  `R` ist — der schnellste Pfad isoliert `R`s eigene Kapazität am besten), und (c) das Ergebnis
  als **Schätzung mit einer Konfidenz, die mit dem Alter verfällt** behandeln (Strohmann:
  Halbwertszeit von einigen Epochen (s)). `vbw(R)` MUSS (MUST) konservativ nach unten begrenzt werden: eine
  unbestätigte einzelne Sonde zählt als niedrig, nicht hoch (PS-7-Disziplin).

- **GR-17 (Sondenergebnisse werden nicht als Bandbreite gegossippt; nur die Disziplin wird
  geteilt).** Ein Client DARF NICHT (MUST NOT) eine skalare „verifizierte Bandbreite von `R`"
  veröffentlichen, gossippen oder von einem Peer akzeptieren — das würde die Bandbreiten-Autorität rekonstruieren, die I-3
  verbietet (eine von einem Peer gemeldete Zahl ist eine Behauptung, nicht besser als `bw` selbst, GR-9). Was
  gegossippt werden DARF (MAY), ist die **Erreichbarkeit/Lebendigkeit** eines Relais als eine Quellklasse unter
  den Klassen von GR-8, und ein Client DARF (MAY) die Zustimmung eines Peers, dass ein Relais *existiert und
  antwortet*, als bestätigenden Aussichtspunkt verwenden (PS-15-Stil), aber die **Durchsatzzahl,
  die jeder Client zur Gewichtung verwendet, MUSS (MUST) seine eigene sein** (GR-11). Sybil-Peers können aufblähen,
  wie *viele* Meldungen sagen „`R` ist schnell", aber nicht aufblähen, was die eigene
  Sonde des Clients gemessen hat — das ist die GR-9/PS-10-Regel „zähle nur verifizierte" angewandt auf
  Bandbreite.

### 5.3 Was eine Sonde dir sagen kann und was nicht (ehrlich degradieren)

- **GR-18 (eine Sonde misst Durchsatz, nicht Ehrlichkeit, nicht Standort, nicht Identität).**
  Eine Sonde beantwortet *„kann dieser Pfad Bytes bewegen?"* und nichts sonst. Sie DARF NICHT (MUST NOT)
  als Beleg dafür gelesen werden, dass:
  - **das Relais ehrlich ist** — ein Relais kann Sondenverkehr perfekt weiterleiten und trotzdem
    echten Verkehr loggen, verzögern oder korrelieren; Durchsatz ist orthogonal zur
    Wächter+Exit-Korrelationsbedrohung (Bedrohungsmodell), die Pfad-*Disjunktheit* (Teil 3)
    adressiert, nicht Bandbreite;
  - **das Relais dort ist, wo die Karte sagt** — eine Sonde misst einen Rundlauf; sie lokalisiert
    `R` nicht in einem AS oder einer Jurisdiktion (das ist Teil 8s Karte, PS-4, mit ihrem eigenen
    deklarierten Fehler), und eine schnelle Sonde sagt nichts über Ko-Lokation (Teil 8 §10);
  - **das Relais eine einzelne eigenständige Partei ist** — ein Sybil-Betreiber mit echter Kapazität
    sondiert *so* schnell wie er ist, weil er die Bandbreite wirklich hat (siehe §6: ein
    ressourcenstarker Angreifer ist kein Sybil, er ist ein teurer echter Angreifer).
  Ein konformer Client MUSS (MUST) verifizierte Bandbreite nur als das präsentieren, was sie ist — eine
  frischeverfallende, pfadverunreinigte Durchsatzschätzung, die der Client selbst gemessen hat
  — und DARF NICHT (MUST NOT) zulassen, dass eine hohe `vbw` Disjunktheit (Teil 3) oder
  Diversität (GR-8) in irgendeiner Auswahlentscheidung ersetzt.

---

## 6. Sybil und Eclipse, begrenzt (Verschärfung von GR-8/GR-9)

Identitäten sind kostenlos (GR-9), also bläht ein Angreifer die **rohe** Eintragszahl nach
Belieben auf. Die Verteidigungen unten stoppen das nicht; sie begrenzen, was die Aufblähung
*kauft*, und die Grenze ist die Kurve, die der Simulator misst (§7.1).

### 6.1 Die Eclipse-Grenze aus der Quellenmischung

- **GR-19 (die GR-8-Obergrenze liefert eine angegebene Eclipse-Grenze; die Annahme ist Klassen-
  unabhängigkeit).** `[claim-critical]` Der Client mische seine Stichprobe über `m`
  unabhängige Quellklassen (GR-8: mindestens Social-Graph-Brücke, Gossip-
  Austausch, direktes Sondieren — also `m ≥ 3`), mit der klassenweisen Obergrenze, dass **keine einzelne
  Klasse mehr als den Anteil `f`** der gespeicherten Stichprobe beiträgt (Strohmann
  `f = 1/2` (s)). Ein Angreifer kontrolliere `a` dieser `m` Klassen vollständig (jeder
  durch eine kontrollierte Klasse gelieferte Eintrag ist feindlich) und nichts in
  den anderen. Dann ist der Anteil des Angreifers an der Stichprobe des Clients begrenzt durch
  ```
        A(a, f)  ≤  min( 1 ,  a · f ).
  ```
  Ein **vollständiger Eclipse** — der Angreifer liefert die gesamte Sicht des Clients, sodass
  jedes ehrliche Relais unsichtbar ist und die Pfadauswahl nur Angreifer-Circuits zieht
  — erfordert `A = 1`, somit
  ```
        a  ≥  ⌈ 1 / f ⌉       Klassen unter vollständiger Angreiferkontrolle.
  ```
  Mit dem Strohmann `f = 1/2` **erfordert ein vollständiger Eclipse, dass der Angreifer mindestens
  2 der ≥3 Klassen besitzt**; der Besitz einer **beliebigen einzelnen** Klasse deckelt den Angreifer bei `f = 1/2` der
  Stichprobe, und ein vollständiger Eclipse ist **strukturell unmöglich** (die ehrlichen Klassen
  liefern immer noch ≥ `1 − f` der Sicht). Das ist genau die Größe, die GR-8 behauptete
  ohne sie anzugeben: die Obergrenze verwandelt „Eclipse" von „besitze genug Relais" in „besitze
  genug *unabhängige Klassen*", was ein strikt schwierigeres und anders
  ressourciertes Problem ist.

- **GR-19a (benenne die Annahme, und wo sie scheitert).** Die Grenze in GR-19 gilt
  **nur wenn die Klassen wirklich unabhängig sind** — wenn die Kompromittierung der
  Social-Graph-Brücken-Verteilung dem Angreifer nichts über die Gossip-Peers oder die Sondenziele
  verrät und ihm keine Kontrolle darüber gibt. Sie **scheitert** genau
  dann, wenn eine Partei mehr als eine Klasse auf einmal kontrolliert:
  - ein Angreifer, der **sowohl** die Social-Graph-Brücke **als auch** die Gossip-Peers besitzt,
    kontrolliert `a = 2` Klassen und erreicht bei `f = 1/2` `A = 1` — einen vollständigen Eclipse, den die
    Obergrenze nicht verhindert, weil die Obergrenze *pro Klasse* begrenzt, und zwei Klassen, die
    heimlich eine Partei sind, keine zwei Klassen sind;
  - korreliertes Versagen (ein Hosting-Anbieter, eine Jurisdiktion, eine Software-
    Monokultur hinter zwei nominellen Klassen) lässt `m` still gegen 1 kollabieren.
  Daher ist der Schutz der Obergrenze **genau so stark wie die Unabhängigkeit der
  Klassen**, und ein konformer Client MUSS (MUST) (a) seine Klassen aus
  nachweislich verschiedenen Vertrauensursprüngen beziehen (eine von einem Freund eingeführte Brücke ist nicht
  unabhängig von Gossip, wenn der Freund der Gossip-Peer ist), und (b) eine Stichprobe,
  in der die Klassen *zu perfekt* über eine ungewöhnliche Sicht *übereinstimmen*, als dasselbe Anomalie-
  Signal behandeln, das Teil 8 für Kartendivergenz (ID-10) und Teil 3 für Steering
  (PS-17) verwendet — gossippe sie, vertraue ihr nicht. Unabhängigkeit ist eine **Annahme, die der Client
  aktiv aufrechterhalten muss**, keine Eigenschaft, die er kostenlos vom Zählen der Klassen erhält.

### 6.2 Die Sybil-Grenze

- **GR-20 (Sybils blähen die rohe Zahl auf, nie verifizierte Ressourcen oder echte Kanten).**
  `[claim-critical]` Weil Identitäten kostenlos sind (GR-9), setzt ein Sybil-Angreifer die
  **rohe Eintragszahl** auf jeden beliebigen Wert. Zwei clientseitige Größen, die er
  **nicht** aufblähen kann, begrenzen den Schaden:
  1. **Verifizierte Bandbreite, die er nicht hat.** `vbw` (GR-11) ist die eigene
     Messung des Clients; ein Sybil aus 10 000 Null-Bandbreiten-Identitäten misst als 10 000
     Relais mit ~0 verifizierter Bandbreite und trägt ~0 Auswahlgewicht (PS-7). Um *Gewicht*
     zu gewinnen, muss der Angreifer die Bytes tatsächlich bewegen — siehe GR-20a.
  2. **Echte Social-Graph-Kanten.** Eine Lox-artige Brückenklasse (GR-8) reicht Vertrauen
     entlang *menschlicher* Kanten; ein Sybil kann Identitäten prägen, aber nicht die Kanten, die
     sie einführen, also lässt die Social-Graph-Klasse Sybils nur in dem Maße zu, in dem echte
     Menschen für sie bürgen (was der ganze Grund ist, warum diese Klasse existiert).
  Die operative Konsequenz ist **PS-10, nun quantifiziert**: die Schätzung der tauglichen Größe
  MUSS (MUST) **nur unabhängig verifizierte Relais und beobachtete AS-
  Diversität** zählen, sodass das Aufblähen der rohen Zahl von `N` auf `10N` Sybils die
  verifizierte Größenschätzung um **0** bewegt (keiner der Sybils besteht die Verifikation), und ein
  Client kann nicht in volle `n, k`-Parameter getäuscht werden, deren Diversität falsch ist. Was
  „zähle nur verifizierte" kauft, in einer Zeile: **die Größe, die die Parameterwahl treibt,
  ist invariant unter Sybil-Aufblähung** — der Angreifer kann das Netz beliebig groß *aussehen*
  lassen und nichts ändern, worauf ein Client reagiert.

- **GR-20a (ein ressourcenstarker Angreifer ist kein Sybil — er ist ein echter, teurer,
  akzeptierter Angreifer).** `[claim-critical]` Die Kehrseite von GR-20 wird ehrlich
  angegeben: ein Angreifer, der die Bandbreite, die soziale Verbürgung
  und die AS-/Jurisdiktions-Diversität **tatsächlich hat**, wird durch keine Sybil-Verteidigung besiegt,
  weil er **kein** Sybil ist — er ist ein echter `k`-Pfad-Angreifer, der für seine
  Positionen bezahlt hat. Das ist das vorgesehene Restrisiko, das das Bedrohungsmodell bereits
  akzeptiert (die `k`-Pfad-Zeile: „erhöhe `n`, `k` nach Geschmack"), keine Lücke in diesem Teil.
  Die Sybil-Verteidigungen erhöhen die Kosten des Angreifers von *kostenlos* (Identitäten prägen) auf
  *echte Ressourcen proportional zum gesuchten Einfluss*; sie machen Einfluss nicht und können ihn nicht
  unkäuflich machen. Ein Client DARF NICHT (MUST NOT) „sybil-resistent" als „ein Angreifer
  mit echten Ressourcen kann keine Position gewinnen" präsentieren — das erste ist wahr, das zweite ist falsch
  und ist eine andere, benannte, akzeptierte Bedrohung.

---

## 7. Was dies nicht löst (OP-2 bleibt offen)

**OP-2 wird hier nicht gelöst, und keine Anforderung oben behauptet, dass es so ist.** Ein zentraler
Allokator — Tors Bandbreiten-Autorität, Walking Onions' signierter Snapshot — *würde*
sowohl Sybil als auch Eclipse per Dekret lösen: er würde eine vertrauenswürdige Sicht veröffentlichen, und
Sybils könnten nicht in sie injizieren noch könnte ein Angreifer einem Opfer eine private
Sicht davon zuführen. I-3 verbietet diesen Allokator, weil die Partei, die die eine
vertrauenswürdige Sicht veröffentlichen kann, auch die Partei ist, die genötigt, vorgeladen oder beschlagnahmt werden kann, um
eine *vergiftete* zu veröffentlichen, und ein Discovery-Mechanismus mit diesem einzelnen Punkt ist der
Notausschalter, den das ganze Projekt ablehnt. Nachdem wir ihn abgelehnt haben, bleibt uns eine
**Grenze, keine Heilung**:

- **Es gibt keinen rein-Overlay-Mechanismus, der die Gossip-Abtastung vollständig
  sybil-/eclipse-sicher macht.** Jede Verteidigung oben ist eine *clientseitige Ressourcen-Verifikations-
  oder Quellenmischungs-Disziplin*, und jede hat eine deklarierte Naht:
  - die Eclipse-Grenze (GR-19) gilt nur unter Klassenunabhängigkeit und **kollabiert,
    wenn eine Partei ≥ `⌈1/f⌉` Klassen besitzt** (GR-19a) — ein Angreifer, reich genug, um
    der Freund zu sein, der dir die Brücke reicht, **und** die Peers, mit denen du gossippst,
    verfinstert dich, und das Overlay kann „zwei Klassen" nicht von „eine Partei, die
    zwei Hüte trägt" unterscheiden;
  - die Sybil-Grenze (GR-20) stoppt *kostenlose* Aufblähung, aber nicht *bezahlte* Position
    (GR-20a) — Verifikation erhöht die Kosten, sie deckelt sie nicht;
  - die Bandbreiten-Sonde (§6) misst Durchsatz, nicht Ehrlichkeit oder Standort (GR-18) —
    ein Relais kann jede Sonde meistern und trotzdem das des Angreifers sein, und ein schneller Sybil mit
    echter Kapazität ist ein echter Angreifer (GR-20a). Eine Sonde schließt GR-7s *Entwurfs*-
    Frage; sie schließt nicht OP-2.
- **Bootstrap unter Eclipse ist das harte Residuum.** Ein Client, der von seinem ersten
  Kontakt an verfinstert ist (GR-10), sieht nur Angreiferklassen, misst nur Angreiferrelais als
  „schnell" und hört nur Angreiferzustimmung — jeder Bestätigungsmechanismus in
  diesem Teil braucht *einen ehrlichen Aussichtspunkt*, um zu funktionieren, und ein Angreifer, der
  die gesamte Welt des Clients ab dem ersten Paket liefert, verwehrt ihm diesen Aussichtspunkt. Das ist
  dieselbe Form wie Teil 8s TOFU-Bootstrap (ID-8): die Verteidigungen **erkennen** eine schlechte
  Sicht, sobald eine ehrliche Quelle erreicht ist, und machen es teuer, einen Client *für immer*
  verfinstert zu halten — sie **verhindern** nicht den anfänglichen Eclipse. „Erkenne und
  mache permanenten Eclipse teuer", nicht „verhindere Eclipse", ist die ehrliche Behauptung, und sie
  ist die Behauptung, die die UI angibt.

**Was der Entwurf präzise tut, ist den Angriff entlang dreier Achsen zu begrenzen:**
Ressourcen-Verifikation (GR-11/GR-20: kostenlose Sybils kaufen nichts), Quellenmischung
(GR-19: Eclipse braucht ≥ `⌈1/f⌉` unabhängige Klassen, nicht nur viele Relais) und der
soziale Graph (GR-20: Kanten können nicht geprägt werden). Das Residuum, das nach allen
drei bleibt, ist: **ein Angreifer mit echten Ressourcen, echter sozialer Verbürgung über mehrere
wirklich-unabhängig-aussehende Klassen und der Fähigkeit, die gesamte erste Sicht eines frischen Clients
zu liefern, kann Einfluss sybil-aufblähen, für den er bezahlt hat, und einen Client verfinstern, den er
umgibt — und das Overlay kann, von innen, nicht beweisen, dass es umgeben wird.**
Dieses Residuum ist OP-2, und es ist offen.

### 7.1 Die Grenzen sind die Kurven des Simulators

Diese Anforderungen sind falsifizierbar, nicht rhetorisch: ein Sybil-/Eclipse-Modell wird
von `poc/sybil_sim.py` neben dem bestehenden `infer_error`-Durchlauf von `network_sim.py` gemessen (der
Simulator modelliert bereits eine partielle clientweise `gossip_sample` — genau die Sicht, die ein
Eclipse-Angreifer formt — und trennt bereits die Grundwahrheit vom Glauben des Clients). Die
Grenzen des Entwurfs sind die Kurven, die er messen MUSS (MUST):

- **die Eclipse-Kurve:** Angreifer-Stichprobenanteil `A` vs. Anzahl kontrollierter
  Klassen `a`, die `min(1, a·f)` von GR-19 verfolgen MUSS (MUST) und die Knickstelle bei
  `a = ⌈1/f⌉` (vollständiger Eclipse) zeigen MUSS (MUST) — und zeigen MUSS (MUST), dass bei `a = 1` die ehrliche Sicht nie
  unter `1 − f` fällt;
- **die Sybil-Aufblähungs-Kurve:** verifizierte Größenschätzung (PS-10) vs. rohe Sybil-Zahl,
  die **flach** sein MUSS (MUST) — die GR-20-Behauptung, dass das Aufblähen der rohen Zahl die
  verifizierte Schätzung um null bewegt, ist genau diese Flachheit, und eine nicht-flache Kurve falsifiziert
  GR-20;
- **die Churn-Interaktion:** Eclipse-Wahrscheinlichkeit vs. Stichproben-Churn-Rate, denn ein
  Client, der schneller neu abtastet, trifft einen ehrlichen Aussichtspunkt früher (die „erkenne, mache
  permanenten Eclipse teuer"-Behauptung ist eine Rate, und der Simulator muss eine Zahl darauf setzen).

Wenn der Simulator zeigt, dass die Eclipse-Kurve `min(1, a·f)` schlägt, oder die
Sybil-Aufblähungs-Kurve ansteigt, ist die Grenze falsch und diese Erweiterung ist kaputt —
greife das Modell an, dann diesen Text. Das Einzige, was nicht zu einer Kurve gemacht werden kann, ist der
Erst-Kontakt-Eclipse eines Clients ganz ohne ehrlichen Aussichtspunkt: der hat keine
overlay-interne Messung, weil das Opfer per Definition nicht außerhalb
der Welt des Angreifers sehen kann. Es ist das OP-2-Residuum, deklariert, und es ist, warum dieser Teil
*begrenzen* sagt, nicht *lösen*.

---

## Hier eingeführte Anforderungen

- **GR-11** — verifizierte Bandbreite ist eine clientweise Selbstmessung (`vbw`), nie eine
  veröffentlichte oder geteilte Zahl; unsondierte Behauptungen zählen als niedrig.
- **GR-12** — die Sonde ist ein versiegelter Rundlauf mit dem gemessenen Relais als
  mittlerem Hop; der Sondierer ist nie in der Sicht des Relais.
- **GR-13** — Ununterscheidbarkeit: Sondenverkehr MUSS (MUST) byte- und timing-identisch
  zu echtem weitergeleitetem Verkehr sein (I-4), sodass ein Relais nicht Sonden bedienen und Nutzlasten aushungern kann.
- **GR-14** — eine Sonde kostet den Sondierer ein begrenztes, vorab bezahltes Byte-Budget, rate-begrenzt
  pro Ziel und im Aggregat.
- **GR-15** — die Sonde ist eine geschlossene Schleife (kehrt nur zum Sondierer zurück); sie kann kein
  Drittparteien-Ziel benennen, also kann sie nicht zu einem DoS-Reflektor verstärken.
- **GR-16** — `vbw` ist eine robuste Aggregation über mehrere unabhängige Circuits, die den
  maximalen dauerhaften Durchsatz nimmt, mit altersverfallender Konfidenz und einer konservativen Untergrenze.
- **GR-17** — Durchsatzzahlen werden nie als Bandbreite gegossippt; nur Lebendigkeit/
  Erreichbarkeit ist eine teilbare Quellklasse — jeder Client gewichtet nach seiner eigenen Messung.
- **GR-18** — ehrliche Degradation: eine Sonde misst Durchsatz, nicht Ehrlichkeit, nicht
  Standort, nicht eigenständige Identität.
- **GR-19** — die GR-8-Obergrenze liefert die Eclipse-Grenze `A ≤ min(1, a·f)`; vollständiger Eclipse
  braucht `a ≥ ⌈1/f⌉` kontrollierte Klassen (≥2 bei `f = 1/2`).
- **GR-19a** — die Grenze nimmt Klassenunabhängigkeit an und scheitert, wenn eine Partei
  ≥ `⌈1/f⌉` Klassen besitzt; Unabhängigkeit wird aufrechterhalten, nicht kostenlos erlangt.
- **GR-20** — Sybils blähen die rohe Eintragszahl auf, aber nie verifizierte Bandbreite oder echte
  soziale Kanten; die verifizierte Größenschätzung (PS-10) ist invariant unter Sybil-Aufblähung.
- **GR-20a** — ein ressourcenstarker Angreifer ist kein Sybil, sondern ein echter, teurer, akzeptierter
  `k`-Pfad-Angreifer; Verifikation erhöht die Kosten, sie macht Position nicht unkäuflich.

GR-11 und GR-19 sind die beiden tragenden: jeder Client misst seine eigene Bandbreite
(keine Autorität), und die Quellenmischungs-Obergrenze verwandelt Eclipse von „besitze genug Relais"
in „besitze genug unabhängige Klassen". Beide sind **begrenzt, nicht absolut** — GR-11s
Sonde kann Ehrlichkeit oder Standort nicht lesen (GR-18), und GR-19 kollabiert, wenn die Klassen
heimlich eine Partei sind (GR-19a). OP-2 ist nicht gelöst: es gibt keinen rein-Overlay-
Mechanismus, der die Gossip-Abtastung vollständig sybil-/eclipse-sicher macht, und ein Client,
der von seinem ersten Kontakt an verfinstert ist, hat keinen ehrlichen Aussichtspunkt, um es zu erkennen. Der Entwurf
begrenzt den Angriff aus Ressourcen-Verifikation, Quellenmischung und dem sozialen Graphen;
er eliminiert ihn nicht. Das ist das ehrliche Residuum, und die Kurven des Simulators
sind, wo es an seinen eigenen Zahlen gemessen wird. Brich es auf dieselbe Weise, wie der Rest der Spezifikation
gebrochen wird: finde ein Sondenbit, auf das ein Relais schlüsseln kann (um GR-13 zu besiegen), einen Weg, wie die Sonde
ein Opfer benennt (um GR-15 zu besiegen), einen Sybil, der die verifizierte Größenschätzung bewegt
(um GR-20 zu besiegen), oder einen Eclipse, der `min(1, a·f)` unter wirklich
unabhängigen Klassen schlägt (um GR-19 zu besiegen) — und du hast diese Erweiterung gebrochen.


## 8. Was dieser Teil nicht entscheidet

Sybil-/Eclipse-Resistenz jenseits von GR-8/GR-9 (OP-2), Sondierprotokoll (GR-7),
Null-Kontakt-Bootstrap (OP-7). Für jeden existieren nummerierte Issues.
