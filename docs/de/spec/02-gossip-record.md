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

## 5. Was dieser Teil nicht entscheidet

Sybil-/Eclipse-Resistenz jenseits von GR-8/GR-9 (OP-2), Sondierprotokoll (GR-7),
Null-Kontakt-Bootstrap (OP-7). Für jeden existieren nummerierte Issues.
