# ScrambNet-Spezifikation — Teil 6: Rendezvous und Zustellung
> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../../en/spec/06-rendezvous.md)).

**Status: ENTWURF (DRAFT).** Strohmann-Werte mit `(s)` markiert. Die Abrufmetadaten- und
Ökonomie-Fragen, die dieser Teil öffnet, sind OP-9 und absichtlich ungelöst.

## 1. Geltungsbereich

Wie eine Nachricht jemanden erreicht, der nicht — und nicht sein darf — in irgendjemandes Karte ist.
Empfänger haben keine Netzpositionen; sie haben **Kontaktkarten** und
**Dead-Drops**. Der Absender legt Anteile ab; der Empfänger ruft sie
hinter seinen eigenen Circuits ab. Niemand stellt je *an* eine Person zu.

## 2. Niemand gossippt über Personen

- **RZ-1.** Ein Empfänger DARF NICHT (MUST NOT) über Gossip auffindbar sein. Nur Relais
  veröffentlichen Einträge (Teil 2). Alles, was die Teilnahme einer Person abfragbar macht,
  ist ein Fehler (vgl. L0: es gibt keine Nutzerliste, weil es keinen
  Moment gibt, in dem sich ein Nutzer anmeldet).

## 3. Kontaktkarten

- **RZ-2.** Eine Kontaktkarte ist **je Beziehung**: die Karte, die Korrespondent A
  gegeben wird, MUSS (MUST) mit der Karte, die Korrespondent B gegeben wird, nicht verknüpfbar sein —
  verschiedener Paarschlüssel, verschiedene Postfächer. Die Kompromittierung eines Korrespondenten entblößt
  eine Beziehung, nicht die Welt des Empfängers.
- **RZ-3.** Karteninhalt (kanonisches CBOR, wie Teil 2):

| Schlüssel | Name | Typ | Anmerkungen |
|---|---|---|---|
| 0 | `v` | uint | Formatversion, `1` |
| 1 | `id` | bytes(32) | Ed25519-Identitätsschlüssel des Empfängers |
| 2 | `kpair` | bytes(32) | Paar-Geheimnis; alles darunter leitet sich daraus ab |
| 3 | `drops` | array | `d` eingebettete Relais-Einträge (vollständige Teil-2-Einträge) |
| 4 | `validity` | uint | Unix-Ablauf; SOLLTE (SHOULD) dem Ablauf der eingebetteten Einträge folgen |

  Ableitungen (HKDF-BLAKE2s, Suite 0x01): der SP-7-Tag-Schlüssel für dieses Paar ist
  `K_tag = HKDF(kpair, "tag")`; Postfach-Bezeichner sind
  `box_id(drop, epoch) = PRF(kpair, "box" ‖ drop_index ‖ epoch)`, abgeschnitten auf
  16 Bytes, mit `epoch = floor(unix_time / 86400)` (s). Der Drop-Index MUSS (MUST)
  in die Ableitung eingehen: mit einer einzigen ID je Epoche könnten zwei kolludierende Drops
  die Postfächer des Paares innerhalb dieser Epoche verknüpfen.
- **RZ-4.** Karten reisen Out-of-Band (QR-Code, gedruckte Zeichenkette, ein Freund) oder
  über einen bestehenden ScrambNet-Kanal. Ein Kontakt ist die Untergrenze, wie in GR-10.

## 4. Drops und Ablage

- **RZ-5.** Der Drop-Satz hält `d = n = 4` (s) Relais, vom *Empfänger* gewählt,
  die SOLLTEN (SHOULD) im selben Sinne gegenseitig unabhängig sein, den die Pfadauswahl
  verlangt (OP-1 gilt auch für Drops). Die `n` Anteile einer Nachricht
  MÜSSEN (MUST) an `n` verschiedenen Drops abgelegt werden — SP-7 auf den Speicher ausgedehnt: kein
  einzelner Drop hält je zwei Anteile von irgendetwas.
- **RZ-6.** Eine Ablage ist ein gewöhnliches Teil-1-Paket, dessen Circuit am
  Drop endet. Der Endhop-Klartext von `delta` ist `box_id` (16 B) ‖ `slot`
  (1840 B); der Slot ist die Anteil-Nutzlast aus Teil 1 §4 mit seinem abschließenden Pad
  16 Bytes kürzer. Der Drop speichert den Slot unter `box_id` wörtlich: er kann
  weder die Tag-Semantik noch den Anteil-Inhalt lesen (ein Anteil < `k`, und SP-7
  macht Anteile gegenseitig nicht verknüpfbar, selbst über kolludierende Drops).
- **RZ-7.** Ablagen sind Fire-and-Forget. Der Drop DARF NICHT (MUST NOT) irgendeine Antwort ausgeben,
  die Erfolg, unbekanntes Postfach oder volles Postfach unterscheidet (stille Uniformität, wie
  GR-4). Speicherregeln: feste Slots von 1840 B, höchstens `64` (s) Slots je Postfach,
  Slot-Ablauf `7` Tage (s), Ältestes-zuerst-Räumung. Die Obergrenze begrenzt den **Speicher**,
  nicht die **Zustellung** unter Flooding — siehe RZ-15.

## 5. Abruf

- **RZ-8.** Der Empfänger pollt jeden seiner Drops über seine eigenen Circuits.
  Die Kenntnis von `box_id` autorisiert den Abruf (es ist geheimnisabgeleitet und
  nicht erratbar); Slots werden beim Ablauf gelöscht, nicht beim Abholen (Löschen-beim-
  Abholen-Semantik ist OP-9-Gebiet: ein Gegner, der ein `box_id` stiehlt, darf nicht
  still Post wegessen können).
- **RZ-9 (Polling-Disziplin).** Das Polling MUSS (MUST) einem von der Nutzeraktivität
  unabhängigen Zeitplan folgen: fester Takt mit Jitter (Strohmann: alle `15` Minuten ±
  gleichverteilt `5`), fortgesetzt, wenn der Nutzer untätig ist, mit Köder-Polls zu Köder-
  Postfach-IDs im selben Takt. Eine Abrufantwort ist stets genau `b = 8`
  (s) Slots, aufgefüllt mit Dummy-Slots, die von echten nicht zu unterscheiden sind. Der
  Drop erfährt den Polling-Takt und die Ablagezeiten eines Postfachs innerhalb einer Epoche —
  das ist der entworfene Rest, begrenzt durch RZ-10 und nun in RZ-16 eingepreist: die
  Unabhängigkeit des Zeitplans MUSS (MUST) strikt sein (RZ-16a), und die Köder-/Byte-Kosten sind
  quantifiziert (RZ-16b).
- **RZ-10 (Epochen).** `box_id` rotiert je Epoche. Ein Drop DARF NICHT (MUST NOT) die
  Postfächer desselben Paares über Epochen verknüpfen können; nichts im Abrufprotokoll
  darf einen über Epochen stabilen Wert tragen.

## 6. Erneuerung und Ausfall

- **RZ-11.** Eine Karte wird In-Band erneuert: der Empfänger legt die nächste Karte
  (neues `kpair`, neue Drops) in die bestehenden Postfächer des Paares als gewöhnliche Nachricht ab,
  bevor `validity` abläuft. Wenn jeder Drop eines Paares tot ist oder die
  Karte abgelaufen ist, tauscht das Paar erneut Out-of-Band aus: ein Kontakt ist die
  Untergrenze, wieder.
- **RZ-12.** Jeder, der eine Karte hält, kann ihre Postfächer füllen. Die Postfach-Obergrenze (RZ-7)
  begrenzt den Flooding-Schaden **am Speicher einer Beziehung**, aber nicht die **Zustellung**
  dieser Beziehung — RZ-15 zeigt, dass ein Flooder der Telefon-Klasse den Abruf innerhalb einer
  Poll-Periode verweigert, und dass die Ablage-Bepreisung (Client-Puzzles) die Lücke nicht
  schließen kann; die hinreichende Verteidigung (Ablage-Zulassungskontrolle) ist ein ungelöster
  OP-9-Rest. Die Speicheranreize der Drops bleiben offen (OP-9).

## 7. Schlüsselableitung und Epochengrenzen

- **RZ-13 (eine KDF-Disziplin).** Jeder Schlüssel und jeder Bezeichner, den ein Paar aus `kpair` ableitet, MUSS (MUST) aus einer einzigen Disziplin stammen: HKDF-BLAKE2s mit einem eindeutigen, zweckbindenden Label. Konkret: der Inhaltsschlüssel ist `HKDF(kpair, "e2e-content")` (SP-1a), der SP-7-Tag-Schlüssel ist `HKDF(kpair, "tag")`, und der Postfach-Bezeichner ist `box_id = HKDF(kpair, "box" ‖ drop_index ‖ epoch)`, abgeschnitten auf `BOX_ID_BYTES`. Kein Wert wird durch rohes keyed-BLAKE2s auf `kpair` oder durch irgendeine zweite Konstruktion abgeleitet — ein früherer Entwurf leitete `box_id` auf diese Weise ab, was diese Anforderung abschafft. Label-Trennung bedeutet, dass die Erfassung oder Schwäche eines abgeleiteten Schlüssels einem Gegner nichts über die Geschwister verrät, und die gesamte Beziehung wird von einer einzigen auditierbaren Ableitung bestimmt (das `SA-4`-Schlüsseltrennungsargument, Teil 7, hängt genau davon ab).
- **RZ-13a (box_id-Breite).** `BOX_ID_BYTES = 16` (128 Bit) (s). Ein Drop sieht nur dieses opake Handle, niemals `kpair`; 128 Bit sind kollisionssicher für die Anzahl der `(pair, drop, epoch)`-Postfächer, die irgendein realistisches Netz hält, und halten die `box_id ‖ slot`-Nutzlast innerhalb eines `delta`.
- **RZ-14 (UTC-Epochengrenzen-Toleranz).** Da `box_id` je UTC-Epoche rotiert (RZ-10), würden ein Absender, der um 23:59 (Epoche `E`) ablegt, und ein Empfänger, der um 00:01 (Epoche `E+1`) pollt, verschiedene Postfächer adressieren, und der Empfänger würde die Post still verpassen. Um dies zu verhindern, MUSS (MUST) ein Empfänger, der innerhalb eines Toleranzfensters einer Epochengrenze pollt, die Postfächer **beider** angrenzenden Epochen pollen: die aktuelle Epoche stets, die vorherige Epoche, wenn innerhalb des Toleranzfensters nach einer Grenze, und die nächste Epoche, wenn innerhalb des Toleranzfensters vor einer. Das Toleranzfenster MUSS (MUST) die ungünstigste Absender-/Empfänger-Taktabweichung plus die Ablage-zu-Poll-Latenz übersteigen (Strohmann `EPOCH_GRACE_SECONDS = 3600` (s)), und `SLOT_TTL_EPOCHS` (RZ-7) MUSS (MUST) ein Postfach mindestens eine Epoche über seine eigene hinaus lesbar halten, damit das zusätzliche Postfach die Post noch hält. Absender legen unter der einzigen `epoch_of(now)` ab; die Toleranz ist eine empfängerseitige Leseregel. Demonstriert in `poc/rendezvous.py` (`epochs_to_poll`, Test `test_deposit_before_boundary_polled_after_boundary`).

## 8. Ökonomie und Abrufmetadaten, eingepreist (OP-9)

Roadmap-Punkt 4.3 hat den beiden OP-9-Fragen, die RZ-7/RZ-9 offen ließen — Flooding und
Polling-Metadaten — Zahlen gegeben, mit dem Simulator `poc/dropecon_sim.py`
(`test_dropecon_sim.py` fixiert die Werte). Das ehrliche Ergebnis ist, dass eine der beiden
Verteidigungen, auf die das Projekt gehofft hatte, **nicht** hält; §9 trägt das als erklärten
Rest, statt es zu verbergen.

- **RZ-15 (Flooding: weder die Obergrenze noch ein Puzzle verteidigt die *Zustellung*; es ist ein
  erklärter Rest). [normativ]** Die RZ-7-Postfach-Obergrenze begrenzt den **Speicher** auf
  `BOX_CAP × SLOT_BYTES = 115 KiB` je `(pair, drop, epoch)`-Postfach, eine von Angreifer-Budget
  unabhängige Decke. Sie begrenzt die **Zustellung** **nicht**. Weil ein Poll nur die
  `B_SLOTS = 8` ältesten überlebenden Slots zurückgibt (RZ-8) und Ablagen das Älteste zuerst
  räumen (RZ-7), verweigert ein Angreifer, der einen frischen ehrlichen Slot hinter `≥ 8`
  neueren Müll-Slots vergräbt, dessen Abruf **ohne überhaupt die Obergrenze zu erreichen** —
  und der Simulator zeigt, dass ein Flooder der **Telefon-Klasse** (`2 × 10⁶ H/s`) dies in
  `~17 s` tut, weit innerhalb eines `POLL_PERIOD = 900 s`-Polls, bei jeder nutzbaren Puzzle-
  Härte. Ein ablageseitiges proof-of-work-Puzzle rettet das nicht: keine Härte `z` ist
  zugleich botnetz-abschreckend und telefon-bezahlbar — der ARM-gegen-GPU-Abstand beträgt
  `~25 000×`, sodass bei `z = 20` (dem letzten telefon-bezahlbaren Punkt, `0.52 s/deposit`)
  eine einzige GPU ein Postfach immer noch `~1.7 × 10⁸`-mal/Stunde nachfüllt, während das Zwingen
  einer GPU auf `1 s/deposit` das Telefon `~9.5 Stunden/deposit` kostet. Ein Puzzle DARF (MAY) bei
  niedriger Härte (`z ≤ 20` (s)) als triviale Nachfüll-Bremsschwelle verlangt werden, wird aber
  **nicht** als Verlass genommen. Die `n = 4, k = 3`-Dispersion hebt die Hürde nur darauf, dass
  `≥ n − k + 1 = 2` der Drops eines Paares gleichzeitig geflutet werden müssen.
  **Zustellungs-Flooding hat daher in diesem Teil keine hinreichende Verteidigung:** es braucht
  eine Ablage-**Zulassungskontrolle**, die das Projekt noch nicht entworfen hat (eine
  Kandidaten-Richtung, keine Entscheidung: ein je-Beziehung aus der Karte abgeleitetes
  Zulassungs-Token, sodass nur ein Kartenhalter ablegt und nur mit begrenzter Rate). Bis das
  existiert, ist Zustellungs-Flooding ein erklärter OP-9-Rest, quantifiziert in §9.

- **RZ-16 (Polling-Metadaten: zwei Lecks, zwei Stellschrauben). [normativ]** Die
  Innerhalb-einer-Epoche-Beobachtung eines profilierenden Drops (über Epochen durch RZ-10
  begrenzt) zerfällt in zwei Lecks mit zwei unabhängigen Verteidigungen, und der Simulator
  preist beide.
  - **RZ-16a (Online-Muster-Leck — frei verteidigt durch strikte Unabhängigkeit).
    [normativ]** Ob der Empfänger auf eine Ablage *reagierte*, ist das einzige
    nutzer-identifizierende Leck, und es wird dadurch verteidigt, dass der Poll-Zeitplan
    **strikt unabhängig** von Ablagen und Nutzeraktivität gemacht wird (RZ-9): der Zeitplan
    DARF NICHT (MUST NOT) durch eine Ablage oder ein App-Ereignis vorgezogen, ausgelöst oder
    umgeformt werden, sodass die `deposit → next-poll`-Latenz beim Inspektionsparadoxon-Mittel
    des Zeitplans selbst bleibt (`≈ 467 s` für `POLL_PERIOD = 900, POLL_JITTER = 300`) und mit
    der Ablagezeit unkorreliert ist. Ein Drop erkennt eine Verletzung nicht am Mittel (zu stumpf
    — ein halb-reaktiver Zeitplan liest am Mittel immer noch nahezu unabhängig), sondern am
    **Tail** `P[latency < 60 s]`, der laut Simulator von Rauschen bei Unabhängigkeit zu einem
    klaren Signal bei einem `5 %`-reaktiven Anteil ansteigt. Diese Verteidigung ist
    **verpflichtend und in Bytes frei**.
  - **RZ-16b (Welche-Box-Leck — verteidigt durch Köder zu einem echten Byte-Preis). [normativ]**
    Welches von mehreren gehaltenen Postfächern das echte des Empfängers ist, wird durch Köder-
    Polls mit einem Multiplikator `r` (s: `r = 1`) verteidigt, eine Frage, die die RZ-2/RZ-10-
    Nichtverknüpfbarkeit bereits weitgehend beantwortet, sodass die marginale Privatheit je Byte
    gering ist. Jeder Poll reitet auf Sphinx — `B_SLOTS + 1 = 9` Pakete von `2048 B` über den
    gemessenen Eingangs-Hop, `~18.4 KiB`, nicht die rohen Slot-Bytes —, sodass über `d = 4` Drops
    im RZ-9-Takt die stehenden Kosten `~212 MB/Monat` bei `r = 0` betragen (vor der Ablage-/
    Sendeseite) und `~425 MB/Monat` bei der `r = 1`-Vorgabe. `r = 0` ist ein expliziter
    Niedrigdaten-Modus. Demonstriert in `poc/dropecon_sim.py` (Szenario B).

## 9. Was dieser Teil nicht entscheidet (der erklärte OP-9-Rest)

Die Minimierung der Abrufmetadaten (schlaueres-als-Polling-Abrufen, PIR-artige Tricks und ihre
echten Kosten), die Löschsemantik und die Drop-Anreize (warum ein Relais das Rauschen eines
Fremden speichert) bleiben echt offen (OP-9); die Verifikation der Drop-Satz-Unabhängigkeit
(OP-1); das Polling über das Mesh im Blackout (OP-6). Für jeden existieren nummerierte Issues.
Drei Ergebnisse aus §8 werden offen als erklärte Reste getragen, mit den Zahlen, die sie
beweisen:

- **Zustellungs-Flooding hat hier keine hinreichende Verteidigung.** Weder die RZ-7-Obergrenze
  (nur Speicher) noch ein proof-of-work-Puzzle (keine telefon-bezahlbare, botnetz-abschreckende
  Härte existiert — der `~25 000×`-ARM-gegen-GPU-Abstand) hält einen Angreifer davon ab, ehrliche
  Post in `~17 s` hinter das 8-Slot-Abruffenster zu vergraben, weit innerhalb eines 900 s-Polls,
  mit Hardware der Telefon-Klasse (RZ-15). Es braucht eine Zulassungskontrolle, die das Projekt
  noch nicht gebaut hat; bis dahin ist es ein erklärter Rest.
- **Der Innerhalb-einer-Epoche-Profiling-Boden ist real.** Strikte Unabhängigkeit (RZ-16a)
  entfernt das einzige nutzer-identifizierende Leck, aber ein Drop erfährt immer noch den
  öffentlichen RZ-9-Takt und die Ablagezeiten in die Postfächer, die er hält; Köder reichen nur
  an die Welche-Box-Frage (RZ-16b). Ein kolludierender Mehr-Box-Drop kann auch *Ablage*-
  Zeitstempel über seine Postfächer hinweg korrelieren, selbst unter perfekter Poll-
  Unabhängigkeit — die RZ-2/RZ-10-Nichtverknüpfbarkeit deckt Bezeichner ab, nicht das Ablage-
  *Timing*.
- **Die RZ-9-Polling-Baseline ist schwer für das mobile Ziel.** Selbst mit ausgeschalteten
  Ködern (`r = 0`) kostet das verpflichtende Polling mit festem Takt über `d = 4` Drops
  `~212 MB/Monat` (RZ-16b) — der Preis der Online-Muster-Verteidigung, in Bytes bezahlt, bevor
  irgendeine Nachricht gesendet wird.
