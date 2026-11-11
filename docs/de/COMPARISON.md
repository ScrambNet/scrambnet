# Wie sich ScrambNet einordnet

Eine ehrliche Positionierung gegenüber den Systemen, die ein Gutachter zu Recht zuerst nennt.
Dieses Dokument benennt, was ScrambNet *anders* macht und — wichtiger noch —
was es *schlechter* macht. Ist eine Zelle unten falsch, öffne ein Issue: hier falsch zu liegen
kostet mehr, als irgendwo sonst im Repository falsch zu liegen.

## Der eine echte Unterschied

Jedes eingesetzte Anonymitätssystem schützt den **Inhalt** einer Nachricht mit
einer rechnerischen Annahme: brich die Chiffre (heute oder mit einem künftigen Quanten-
computer) und der Inhalt wird lesbar. ScrambNets Inhaltsboden ist dagegen
**informationstheoretisch**: unterhalb von `k` erbeuteten Anteilen gibt es keinen Geheimtext zu
brechen, denn der Inhalt ist in keinem Satz von `k−1` Anteilen vorhanden — eine Eigenschaft von
Shamirs Secret Sharing, nicht der Stärke irgendeiner Chiffre (Invariante I-2). Das ist
die ganze Wette. Alles andere hier ist zusammengesetzter Stand der Technik.

Dieser Unterschied betrifft **nur den Inhalt**. Bei der **Verknüpfbarkeit** (wer mit wem spricht,
die Metadaten) steht ScrambNet im selben harten Kampf wie alle anderen und gibt dort
im schnellen Modus kein informationstheoretisches Versprechen.

## Nebeneinander

| | **ScrambNet** | **Tor** | **Nym / Loopix** | **Briar** |
|---|---|---|---|---|
| Hauptzweck | Messaging (asynchron, per Dead Drop) | Browsen mit geringer Latenz | Messaging (Mixnet) | Messaging, P2P |
| Inhaltsvertraulichkeit | **Unbedingt unterhalb von `k` Anteilen** | Rechnerisch (TLS + Onion) | Rechnerisch | Rechnerisch |
| Verknüpfbarkeitsabwehr | Verstreute Circuits + Mix (paranoid) | Onion-Circuits | Poisson-Mixnet (stark) | Onion + Kontaktgraph |
| Verzeichnis / Entdeckung | **Keines** — Gossip + überprüfbare Stichprobe | ~9 Directory Authorities | Validatoren / nym-api | Einführung über Kontakte |
| Globaler passiver Gegner | Außerhalb des Modells (schnell) / Mix (paranoid) | Außerhalb des Modells | **Im Modell** (Mixnet) | Teilweise |
| Blackout / offline | Lokales Mesh, Store-and-Forward | Nein | Nein | **Ja** (Bluetooth/Wi-Fi) |
| Anreizschicht | Keine (freiwillig) | Freiwillig | **Token** | Freiwillig |
| Reife | **Pre-Alpha-Spezifikation + PoC** | Produktiv, 20+ Jahre | Produktiv | Produktiv |

## Wo ScrambNet zurückliegt, offen gesagt

- **Reife.** Tor, Nym und Briar sind ausgerollt, auditiert und tragen heute echten
  Verkehr. ScrambNet ist eine Spezifikation und ein Proof of Concept in Python.
  Noch sollte niemand ein echtes Geheimnis hindurchleiten, und das Repository sagt es.
- **Mixnet-Entwurf.** Nym/Loopix haben einen strengen, veröffentlichten Poisson-Mix-Entwurf
  mit einem Modell des globalen passiven Gegners. ScrambNets paranoider Modus ist ein
  Platzhalter (OP-5), bis jemand diese Arbeit auch hier leistet.
- **Verknüpfbarkeits-Metadaten.** Das Abrufmuster per Dead Drop verrät den Polling-Takt
  zu einem Drop innerhalb einer Epoche (OP-9) — ein Preis, den Nyms kontinuierliches Mischen
  gründlicher abträgt.
- **Bandbreite.** Der unbedingte Boden kostet `×n` Bandbreite (×4 im Strawman). Tor
  kostet ×1 für seine schwächere Inhaltsgarantie. Das ist der Preis
  der Wette, kein Fehler, aber ein echter Preis (OP-3).
- **Anreize.** Nym bezahlt Relais; ScrambNet bittet Freiwillige, was das Wachstum
  historisch begrenzt.

## Warum man es trotzdem baut

Weil die Inhaltsgarantie jedes anderen Systems ein Verfallsdatum trägt, das in den
Annahmen von 2003–2017 geschrieben steht, und „jetzt ernten, später entschlüsseln" eine reale
Gegnerstrategie gegen Dissidenten ist, deren Nachrichten über Jahrzehnte unlesbar bleiben
müssen. Ein Inhaltsboden, den kryptoanalytischer oder quantenmechanischer Fortschritt nicht
abtragen kann, ist eine `×n`-Bandbreitenrechnung und die Arbeit am Rest wert. Ist
diese Wette falsch, ist der schnellste Weg, es herauszufinden, sie hier anzugreifen.
