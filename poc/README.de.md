# Dispersionskern — Referenz-PoC

Ausführbarer Begleiter zu den Teilen [1](../docs/de/spec/01-share-packet.md) und
[6](../docs/de/spec/06-rendezvous.md) der Spezifikation.
Reines Python 3, nur Standardbibliothek, geschrieben, um gelesen und
angegriffen zu werden: eine ausführbare Spezifikation, nicht der künftige
Knoten.

Was es zeigt:

- (n, k)-Shamir-Teilung über GF(2^8), byteweise, und Rekonstruktion aus
  beliebigen k Anteilen (SP-1, SP-2);
- die bedingungslose Untergrenze (I-2), per Brute Force: `floor_demo()`
  enumeriert jedes mit k−1 beobachteten Anteilen konsistente Polynom und
  findet alle 256 Kandidaten-Geheimbytes *exakt gleich konsistent* — nichts
  wird gelernt, auch mit unbegrenzter Rechenleistung;
- die SP-7-Tags mit Empfängerschlüssel (BLAKE2s mit Schlüssel) und die
  Tag-Fenster-Erkennung, die sie implizieren;
- das zufällige SP-8-Padding und das Anteils-Payload-Format aus Teil 1 §4;
- den ehrlichen Preis: eine (n, k)-Dispersion überträgt das ×n-fache des
  Chiffretextvolumens (Issue #4).

Ausführen:

    python3 dispersal.py        # Demo
    python3 test_dispersal.py   # Tests, einschließlich vectors.json
    python3 rendezvous.py       # Demo Teil 6: Drops und Polling
    python3 test_rendezvous.py  # Tests Teil 6
    python3 network_sim.py      # Experiment: k-Pfad-Gegner vs Netzgröße
    python3 test_properties.py  # statistische Eigenschaftstests (Uniformität, SP-7)
    python3 run_all.py          # jede Demo + jeder Test, ein Urteil

## Das Experiment: was der Gegner bekommt, in Zahlen

`network_sim.py` macht aus den offenen Fragen der Issues #2/#4/#10 eine
Tabelle. Es modelliert eine Nachricht als n=4 Anteile über 4 disjunkte
Schaltkreise zu 4 Drops; ein k-Pfad-Gegner besitzt einen Anteil der Relays und
"sieht" einen Schaltkreis, wenn er dessen Guard und Exit zugleich hält:

    Sender                                         Drops (je ein Anteil)
      |  Anteil 1 --[guard]--[mid]--[exit]-->  box 1  \
      |  Anteil 2 --[guard]--[mid]--[exit]-->  box 2   |  Empfänger holt,
      |  Anteil 3 --[guard]--[mid]--[exit]-->  box 3   |  nimmt 3 beliebige,
      |  Anteil 4 --[guard]--[mid]--[exit]-->  box 4  /   rekonstruiert

- **gesehen >= k** -> Inhaltsbruch (und nur dann; unter k hält die I-2-
  Untergrenze bedingungslos, bei jeder Netzgröße);
- **gesehen < k** -> Inhalt sicher, aber jeder gesehene Schaltkreis verrät
  dennoch, dass *irgendein* Fluss lief — der Metadatenverlust, den das
  Bedrohungsmodell einräumt: Dispersion verengt ihn, hebt ihn nicht auf.

Das gedruckte Ergebnis: Inhaltsbrüche sind selten und verschwinden, sobald das
Netz groß genug für AS-disjunkte Schaltkreise ist; der Verknüpfungs-Leak ist
klein, aber ungleich null und am schlimmsten in einem winzigen Netz, das sie
*nicht* bauen kann — genau darum muss ein junges Netz einen degradierten
„Kleinnetz-Modus" fahren und ihn ansagen (Issue #4). Vorläufige Zahlen:
reproduziere sie, brich das Modell, diskutiere in den Issues.

`vectors.json` enthält Vektoren für andere Implementierungen: wer sie
reproduziert, interoperiert auf dieser Schicht.

Was es **nicht** ist: Produktionscode. Keine Constant-Time-Arithmetik, kein
Netzwerk, keine Onion-Schicht, kein Ende-zu-Ende-AEAD (nach SP-1 sieht diese
Schicht nur opaken Chiffretext). Schützt damit nichts.
