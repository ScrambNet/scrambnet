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
| 4 | `validity` | uint | Unix-Ablauf; SOLLTE dem Ablauf der eingebetteten Einträge folgen |

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
  Slot-Ablauf `7` Tage (s), Ältestes-zuerst-Räumung.

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
  das ist der entworfene Rest, begrenzt durch RZ-10 und in OP-9 angegriffen.
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
  begrenzt den Flutungsschaden auf eine Beziehung; die Ablage-Bepreisung (Client-
  Puzzles?) und die Speicherökonomie des Drops sind offen (OP-9).

## 7. Schlüsselableitung und Epochengrenzen

- **RZ-13 (eine KDF-Disziplin).** Jeder Schlüssel und jeder Bezeichner, den ein Paar aus `kpair` ableitet, MUSS (MUST) aus einer einzigen Disziplin stammen: HKDF-BLAKE2s mit einem eindeutigen, zweckbindenden Label. Konkret: der Inhaltsschlüssel ist `HKDF(kpair, "e2e-content")` (SP-1a), der SP-7-Tag-Schlüssel ist `HKDF(kpair, "tag")`, und der Postfach-Bezeichner ist `box_id = HKDF(kpair, "box" ‖ drop_index ‖ epoch)`, abgeschnitten auf `BOX_ID_BYTES`. Kein Wert wird durch rohes keyed-BLAKE2s auf `kpair` oder durch irgendeine zweite Konstruktion abgeleitet — ein früherer Entwurf leitete `box_id` auf diese Weise ab, was diese Anforderung abschafft. Label-Trennung bedeutet, dass die Erfassung oder Schwäche eines abgeleiteten Schlüssels einem Gegner nichts über die Geschwister verrät, und die gesamte Beziehung wird von einer einzigen auditierbaren Ableitung bestimmt (das `SA-4`-Schlüsseltrennungsargument, Teil 7, hängt genau davon ab).
- **RZ-13a (box_id-Breite).** `BOX_ID_BYTES = 16` (128 Bit) (s). Ein Drop sieht nur dieses opake Handle, niemals `kpair`; 128 Bit sind kollisionssicher für die Anzahl der `(pair, drop, epoch)`-Postfächer, die irgendein realistisches Netz hält, und halten die `box_id ‖ slot`-Nutzlast innerhalb eines `delta`.
- **RZ-14 (UTC-Epochengrenzen-Toleranz).** Da `box_id` je UTC-Epoche rotiert (RZ-10), würden ein Absender, der um 23:59 (Epoche `E`) ablegt, und ein Empfänger, der um 00:01 (Epoche `E+1`) pollt, verschiedene Postfächer adressieren, und der Empfänger würde die Post still verpassen. Um dies zu verhindern, MUSS (MUST) ein Empfänger, der innerhalb eines Toleranzfensters einer Epochengrenze pollt, die Postfächer **beider** angrenzenden Epochen pollen: die aktuelle Epoche stets, die vorherige Epoche, wenn innerhalb des Toleranzfensters nach einer Grenze, und die nächste Epoche, wenn innerhalb des Toleranzfensters vor einer. Das Toleranzfenster MUSS (MUST) die ungünstigste Absender-/Empfänger-Taktabweichung plus die Ablage-zu-Poll-Latenz übersteigen (Strohmann `EPOCH_GRACE_SECONDS = 3600` (s)), und `SLOT_TTL_EPOCHS` (RZ-7) MUSS (MUST) ein Postfach mindestens eine Epoche über seine eigene hinaus lesbar halten, damit das zusätzliche Postfach die Post noch hält. Absender legen unter der einzigen `epoch_of(now)` ab; die Toleranz ist eine empfängerseitige Leseregel. Demonstriert in `poc/rendezvous.py` (`epochs_to_poll`, Test `test_deposit_before_boundary_polled_after_boundary`).

## 8. Was dieser Teil nicht entscheidet

Die Minimierung der Abrufmetadaten (schlaueres-als-Polling-Abrufen, PIR-artige
Tricks und ihre echten Kosten), die Löschsemantik, die Ablage-Bepreisung, die Drop-
Anreize (OP-9); die Verifikation der Drop-Satz-Unabhängigkeit (OP-1); das Polling über
das Mesh im Blackout (OP-6). Für jeden existieren nummerierte Issues.
