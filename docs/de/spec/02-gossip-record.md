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
| 7 | `sig` | bytes(64) | Ed25519 über die Signatureingabe von §2A (GR-24); das Kodierungs- und Verifikationsprofil ist §2A |

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

## 2A. Kanonische Kodierung und das Verifikationsprofil

GR-1 nennt „kanonisches CBOR (RFC 8949 §4.2.1)" und GR-4 verlangt Signatur-
gültigkeit vor dem Speichern oder Weiterleiten, aber §4.2.1 lässt Kodierungs-Entscheidungen
offen, und die Ed25519-Verifikation divergiert bekanntermaßen zwischen Bibliotheken (Chalkias et al.,
*Taming the Many EdDSAs*; die Spaltung ZIP-215 vs. RFC 8032). Für ein I-1-Netz ist
jede dieser Lücken tödlich: zwei Knoten, die über die kanonischen Bytes eines Eintrags uneins sind, oder
darüber, ob eine Signatur gültig ist, verwerfen die gültigen Einträge des jeweils anderen (eine Partition) oder
spalten sich an einem gezielt gebauten Eintrag (eine sicherheitsrelevante Split-View, die die
ID-8/ID-10-Äquivokations- und PS-17-Steering-Bedrohungen speist). Dieser Abschnitt fixiert beides auf das Byte.
Alle von GR-21..GR-28 sind Bestandteile der „Signaturgültigkeit", wie GR-4 den Begriff verwendet,
und MÜSSEN (MUST) durchgesetzt werden, bevor ein Eintrag gespeichert oder weitergeleitet wird, mit GR-4s
stillem uniformem Fehlschlag. Das gesamte Profil wird durch die `records`-Vektoren (GR-30) maschinell
überprüfbar gemacht und in `poc/gossip.py` demonstriert, dessen Ed25519 bitgenau gegen eine
unabhängige Bibliothek gegengeprüft wird.

- **GR-21 (kürzeste Form, definite Länge, nur vier Typen).** Jede Ganzzahl und
  jede Länge in einem Eintrag MUSS (MUST) den kürzesten CBOR-Kopf verwenden (bevorzugte
  Serialisierung, RFC 8949 §4.2.1): ein Dekodierer MUSS (MUST) jeden nicht-kürzesten Kopf zurückweisen
  (z. B. `0x18 0x0a` für `10`). Alle Maps, Arrays und Bytestrings MÜSSEN (MUST) von
  definiter Länge sein; Items unbestimmter Länge MÜSSEN (MUST) zurückgewiesen werden. Die einzigen CBOR-Major-
  Typen, die irgendwo in einem Eintrag erlaubt sind, sind unsigned Integer (major 0), Byte-
  string (major 2), Array (major 4) und Map (major 5) — genau jene, die GR-2 verwendet.
  Negative Ganzzahlen, Textstrings, Floats, Tags, Simple Values (einschließlich
  `false`/`true`/`null`) und jeder andere Major-Typ oder Kopf MÜSSEN (MUST) zurückgewiesen werden.
  Dies macht die Kanonisierung, zusammen mit GR-21a, **total**: jeder Bytestring
  dekodiert entweder zu genau einem Eintrag oder wird zurückgewiesen (I-1).
- **GR-21a (die Gestalt der Schlüssel 0–7 ist fixiert, nicht nur ihr CBOR-Typ).** Ein
  Feld, dessen Wert ein zusammengesetzter Typ ist, ist eine Kanonisierungs-Mehrdeutigkeit, sofern nicht
  seine innere Gestalt fixiert ist: zwei Implementierungen würden sich sonst an einem
  signaturgültigen Eintrag spalten, dessen zusammengesetztes Feld die eine als wohlgeformt liest und die
  andere nicht (Schlüssel 3 `addrs` ist der konkrete Fall — er wird nie krypto-dekodiert, also
  rettet keine spätere Prüfung die Spaltung). Daher MÜSSEN (MUST) die Gestalten der bekannten Schlüssel
  als Zurückweisungsprädikat durchgesetzt werden, nicht als Konvention behandelt: Schlüssel 0 `v` und Schlüssel
  4 `bw`, Schlüssel 5 `created`, Schlüssel 6 `expiry` MÜSSEN (MUST) unsigned Integer sein (GR-21); Schlüssel
  1 `id` und Schlüssel 2 `onion` MÜSSEN (MUST) Bytestrings von genau 32 Bytes sein; Schlüssel 7 `sig`
  MUSS (MUST) ein Bytestring von genau 64 Bytes sein; Schlüssel 3 `addrs` MUSS (MUST) ein Array sein (das
  leer sein DARF (MAY)), von dem jedes Element ein Array von genau zwei Items sein MUSS (MUST), Item
  0 ein unsigned Integer (die Transport-id) und Item 1 ein Bytestring der Länge
  `≤ N_addr = 256` (s) (der Endpunkt-Blob). Jede andere Gestalt eines bekannten Schlüssels MUSS (MUST)
  als Kanonisierungsfehler zurückgewiesen werden (GR-23/GR-29). Unbekannte Schlüssel ≥ 8 sind
  signiert-aber-ignoriert (GR-2) und DÜRFEN (MAY) jeden GR-21-legalen Wert beliebiger Gestalt tragen;
  nur die Schlüssel 0–7 sind gestaltfixiert.
- **GR-22 (aufsteigende Ganzzahl-Schlüsselordnung, für unbekannte Schlüssel voll fixiert).** Map-
  Schlüssel MÜSSEN (MUST) unsigned Integer sein, in kürzester Form kodiert (GR-21), und MÜSSEN (MUST)
  in streng aufsteigender numerischer Ordnung erscheinen. Weil die Schlüssel unsigned Integer in kürzester
  Form sind, **stimmt** die bytelexikografische Ordnung des kodierten Schlüssels aus RFC 8949 §4.2.1
  **für alle Schlüsselwerte genau mit der aufsteigenden numerischen Ordnung überein** (ein
  Ein-Byte-Kopf `0x00`–`0x17` sortiert immer vor jedem Mehr-Byte-Kopf, und innerhalb
  einer festen Breite ist die Big-Endian-Ordnung die numerische Ordnung); die §4.2.1-Feinheit „bytelexikografisch ≠
  numerisch jenseits von 23" existiert nur für nicht-kürzeste Kodierungen, die GR-21
  verbietet. Unbekannte Schlüssel ≥ 8 sind zur Vorwärtskompatibilität erlaubt (GR-2) und
  MÜSSEN (MUST) nach derselben aufsteigend-numerischen Regel sortieren. Schlüssel MÜSSEN (MUST) eindeutig sein; eine Map,
  die denselben Schlüssel zweimal enthält, MUSS (MUST) zurückgewiesen werden (die klassische Signatur-Umgehung,
  bei der zwei Parser uneins sind, welches Duplikat gewinnt). Es gibt somit genau eine
  legale Schlüsselordnung für jede Schlüsselmenge, bekannt oder unbekannt (I-1).
- **GR-23 (verifiziere über die empfangenen Bytes; die Draht-Kodierung MUSS (MUST) bereits
  kanonisch sein).** Ein Verifizierer MUSS (MUST) verlangen, dass die empfangenen Eintrags-Bytes die
  kanonische Kodierung sind, die durch GR-21/GR-21a/GR-22 definiert ist, und MUSS (MUST) jeden Eintrag zurückweisen,
  dessen empfangene Bytes nicht kanonisch sind — falsche Schlüsselordnung, nicht-kürzester Kopf,
  unbestimmte Länge, ein unzulässiger Typ, ein Duplikat-Schlüssel, ein fehlgestaltetes bekanntes Feld
  (GR-21a), ein Top-Level-Item, das keine Map (major 5) ist, oder irgendein nachlaufendes Byte
  nach der Top-Level-Map. (Weil jeder Container von definiter Länge ist, GR-21, kann
  der einzige Ort, an dem „nachlaufende Bytes" auftreten können, nach dem Top-Level-Item sein; eine
  Implementierung DARF NICHT (MUST NOT) eine Prüfung auf innere nachlaufende Bytes erfinden, die einen
  kanonischen Eintrag zurückweisen würde.) Der Verifizierer DARF NICHT (MUST NOT) neu kanonisieren und dann über die
  neu kodierten Bytes verifizieren; er verifiziert die Signatur über **genau die empfangenen
  Bytes** (GR-24). Dies ist es, was GR-2s „unbekannte Schlüssel sind von der Signatur abgedeckt, aber
  für die Semantik ignoriert" total macht: die Kanonisierung ist über die **vollständige** Map einschließlich
  der unbekannten Schlüssel definiert, die Ordnung der unbekannten ist fixiert (GR-22),
  und ein Verifizierer muss niemals die Kodierung eines Schlüssels reproduzieren, die ein Signierer für einen von ihm nicht
  verstandenen Schlüssel gewählt hat — er prüft nur, dass die Bytes, die er empfangen hat, selbst kanonisch sind.
  Ein Knoten, der einen nicht-kanonischen Draht-Eintrag toleriert, wo ein anderer Knoten ihn zurückweist,
  ist ein I-1-Defekt.
- **GR-24 (die Signatureingabe ist bytegenau und domänengetrennt).** Die für GR-2 Schlüssel 7
  signierte Nachricht ist

  ```
  "ScrambNet-gossip-v1" ‖ 0x00 ‖ canon( record without key 7 )
  ```

  wobei das Label genau die 19 ASCII-Bytes `ScrambNet-gossip-v1` ist, `0x00` ein
  einzelnes Trenn-Byte ist und `canon(record without key 7)` die
  GR-21/GR-21a/GR-22-kanonische Kodierung der Eintrags-Map mit **vollständig ausgelassenem
  Schlüssel 7** ist — die Map-Header-Zählung spiegelt die verbleibenden Schlüssel wider (z. B. 7, nicht 8),
  und Schlüssel 7 ist abwesend, **nicht** vorhanden-mit-leerem-Wert — einschließlich jedes
  unbekannten Schlüssels ≥ 8 in aufsteigender Ordnung. Label-plus-Trenner ist ein
  Domänentrennungs-Präfix (passend zur Suite-`0x01`-Label-Konvention von
  `"e2e-content"`/`"box"`/`"tag"`), das vorhanden sein MUSS (MUST), sodass eine Eintrags-Signatur
  niemals als Signatur über die Nachricht irgendeines anderen Protokolls oder einer anderen Version
  umgedeutet werden kann. Die Signatur ist reines Ed25519 (RFC 8032, kein Pre-Hash) über diese genauen
  Bytes. Zum Verifizieren rekonstruiert ein Knoten diese Signatureingabe aus dem empfangenen
  kanonischen Eintrag (GR-23) mit entferntem Schlüssel 7 und prüft die Schlüssel-7-Signatur
  dagegen unter dem öffentlichen Schlüssel `A = id` (GR-28). Dies ist die alleinige Definition der
  Signatureingabe; GR-2s Schlüssel-7-Zeile verweist darauf.
- **GR-25 (eine Verifikationsgleichung: RFC 8032 kofaktorlos).** Die Signatur-
  verifikation MUSS (MUST) die kofaktorlose RFC-8032-Gleichung `[S]·B = R + [k]·A` verwenden,
  wobei `k = SHA-512(R ‖ A ‖ M) mod L`, `B` der Ed25519-Basispunkt, `M` die
  GR-24-Signatureingabe ist, und `R`, `A`, `S` aus der Signatur und `id` genommen werden.
  Implementierungen DÜRFEN NICHT (MUST NOT) die kofaktorierte (`[8]`-multiplizierte, ZIP-215-artige)
  Verifikationsgleichung verwenden und DÜRFEN NICHT (MUST NOT) eine Bibliothek verwenden, deren Akzeptanzmenge sich
  von diesem Profil unterscheidet, es sei denn, sie ist so gekapselt, dass sie genau passt. ScrambNet verifiziert
  Einträge einzeln (GR-4), also trifft das Batch-Verifikations-Motiv für eine kofaktorierte
  Gleichung nicht zu; eine einzige fixierte Gleichung ist erforderlich, damit jeder Knoten
  bitgenau über die Gültigkeit übereinstimmt (I-1). Dieses Verbot verbietet nur die `[8]`-
  kofaktorierte *Verifikationsgleichung*; es verbietet **nicht** die Skalar-
  multiplikationen, die GR-28 für die Untergruppen-Zugehörigkeit verwendet.
- **GR-26 (kanonischer Skalar S).** Ein Eintrag MUSS (MUST) zurückgewiesen werden, es sei denn
  `0 ≤ S < L`, wobei `L = 2^252 + 27742317777372353535851937790883648493` die
  Ed25519-Gruppenordnung ist. Eine Signatur mit `S ≥ L` (ein nicht-reduzierter Skalar) ist die
  klassische Ed25519-Malleabilität und MUSS (MUST) zurückgewiesen werden, selbst wenn die Arithmetik sonst
  aufgehen würde, sodass keine zweite Kodierung derselben Signatur von einer
  Bibliothek akzeptiert und von einer anderen zurückgewiesen wird (I-1).
- **GR-27 (kanonische Punkt-Kodierungen für R und A).** Die 32-Byte-Kodierungen von `R`
  (aus der Signatur) und `A` (die `id`) MÜSSEN (MUST) kanonisch sein: die kodierte
  y-Koordinate MUSS (MUST) `y < p` erfüllen (`p = 2^255 − 19`), und eine Kodierung mit
  `y ≥ p`, oder mit gesetztem Vorzeichen-Bit bei der nicht-kanonischen Kodierung von `x = 0`, MUSS (MUST)
  zurückgewiesen werden. Eine nicht-kanonische Punkt-Kodierung ist ein zweiter Name für einen Punkt und ist
  genau eine Eingabe, bei der Bibliotheken divergieren; sie zurückzuweisen hält die Akzeptanz-
  menge total (I-1).
- **GR-28 (`id` ist der öffentliche Schlüssel; A und R MÜSSEN (MUST) von Primordnung sein — getestet durch
  `[L]·P`, nicht durch eine Blacklist).** GR-2 Schlüssel 1 `id` **ist** der öffentliche Ed25519-Schlüssel `A`
  und der Name des Relais: die Verifikation verwendet ihn direkt, ohne Verzeichnis- oder Schlüssel-
  Lookup (I-3, keine Autorität). Ein Eintrag MUSS (MUST) zurückgewiesen werden, es sei denn, sowohl `A` als auch `R`
  dekodieren (GR-27) zu Punkten der **großen Untergruppe von Primordnung** — gleichbedeutend,
  keiner von beiden darf ein Punkt kleiner Ordnung oder gemischter Ordnung sein. Diese Zugehörigkeit MUSS (MUST) als
  `[L]·P = 𝒪` (die Identität) **und** `P ≠ 𝒪` getestet werden, berechnet durch Skalar-
  multiplikation mit der Gruppenordnung `L`: die erste Bedingung lässt nur die
  Identität und die Punkte der Ordnung `L` zu (da `L` prim ist, teilt sie keine Ordnung in {2,4,8}),
  und die Bedingung `P ≠ 𝒪` weist dann die Identität selbst zurück. Eine
  **Blacklist von Kodierungen kleiner Ordnung DARF NICHT (MUST NOT)** als Test verwendet werden: sie lässt
  Punkte gemischter Ordnung zu (Ordnung `2L`/`4L`/`8L`, die nicht unter den acht
  Kodierungen kleiner Ordnung sind), und ein `A` oder `R` gemischter Ordnung ist genau eine Eingabe,
  bei der die kofaktorierten und kofaktorlosen Gleichungen divergieren — sodass eine
  Nur-Blacklist-Implementierung eine Signatur akzeptieren würde, die ein konformer Knoten zurückweist (I-1). Nach
  GR-26/GR-27/GR-28 ist die Akzeptanzmenge die eine strikte Menge, die jeder konforme
  Knoten identisch berechnet. Ein Eintrag, dessen `id` kein gültiger kanonischer
  Punkt von Primordnung ist, hat keinen verifizierbaren Signierer und MUSS (MUST) still verworfen werden (GR-4).
- **GR-29 (dies sind GR-4-Prüfungen; der Fehlschlag ist still und uniform).** GR-21 bis
  GR-28 sind Bestandteile der „Signaturgültigkeit", wie GR-4 den Begriff verwendet. Ein Knoten
  MUSS (MUST) sie durchführen, bevor ein Eintrag gespeichert oder weitergeleitet wird, und MUSS (MUST) einen scheiternden
  Eintrag still verwerfen, ohne beobachtbare Unterscheidung — durch Fehler, Antwort oder Timing —
  zwischen einem Kanonisierungsfehler, einem fehlgestalteten Feld, einer ungültigen Signatur,
  einem schlechten Punkt, einer Verletzung der Größenobergrenze (GR-1), Ablauf oder einem Zeitstempel-Rundungs-
  fehler (GR-4/GR-5). Das uniforme stille Verwerfen ist die I-4-artige Eigenschaft, die GR-4 bereits
  verlangt; die Konstant-Arbeit-Disziplin, die es gegenüber einem Timing-Beobachter aufrechterhält, ist ein
  MUSS (MUST), durchgesetzt wie Teil 9 RI-1b es verlangt (ein Verwerfen, dessen Arbeit seinen Grund
  verrät, ist nicht konform), kein bloßer Best-Effort.
- **GR-29a (Prüfreihenfolge: ein Eintrag beweist sich selbst, bevor er den Zustand beeinflussen kann).**
  Die Prüfungen MÜSSEN (MUST) in dieser Reihenfolge angewandt werden: (1) die GR-1-Größenobergrenze (ein Eintrag größer
  als die Obergrenze wird ungelesen verworfen); (2) kanonische Kodierung und Feld-Gestalt
  (GR-21/GR-21a/GR-22/GR-23) und Signaturgültigkeit (GR-24..GR-28); (3) erst dann
  darf der Eintrag an der GR-5-Deduplizierung und Frische teilnehmen. Ein Eintrag, der (1)
  oder (2) nicht besteht, DARF NICHT (MUST NOT) irgendeinen gespeicherten Eintrag verdrängen, ersetzen oder sonstwie beeinflussen.
  Ohne diese Reihenfolge kann ein Relais, das vor dem Verifizieren dedupliziert, dazu gebracht werden, einen
  ehrlichen, signierten Eintrag zugunsten eines gefälschten mit einem höheren `created` zu verwerfen
  (der dann die Verifikation nicht besteht und verworfen wird, nachdem er bereits den guten
  Eintrag verdrängt hat) — eine Dienstverweigerung, zu der GR-5 sonst einlüde.
- **GR-30 (Konformität ist durch die records-Vektoren definiert).** Eine konforme
  Implementierung MUSS (MUST) die kanonische Kodierung und die Signatureingabe jedes
  positiven Eintrags-Vektors (Roadmap 3.2, `vectors.json`-Abschnitt `records`)
  bytegenau reproduzieren, MUSS (MUST) jeden positiven Vektor verifizieren und MUSS (MUST) jeden negativen
  Vektor **für die spezifische GR-Klausel, die der Vektor benennt**, zurückweisen. Einen Eintrag zu akzeptieren, den ein
  Vektor als „reject" markiert, einen positiven Vektor zurückzuweisen oder einen negativen
  Vektor aus dem falschen Grund zurückzuweisen, ist Nichtkonformität: es ist genau die Divergenz
  (ein Eintrag, den ein Knoten akzeptiert und ein anderer zurückweist, oder umgekehrt), die dieser Abschnitt
  zu verhindern existiert (I-1). Vektorkonformität bescheinigt Übereinstimmung über das
  Akzeptier-/Zurückweis-Prädikat; sie bescheinigt kein Timing (GR-29, vgl. RI-1b).

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
