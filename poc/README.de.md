# Dispersionskern — Referenz-PoC

Ausführbarer Begleiter zu [Teil 1 der Spezifikation](../docs/spec/01-share-packet.md).
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

`vectors.json` enthält Vektoren für andere Implementierungen: wer sie
reproduziert, interoperiert auf dieser Schicht.

Was es **nicht** ist: Produktionscode. Keine Constant-Time-Arithmetik, kein
Netzwerk, keine Onion-Schicht, kein Ende-zu-Ende-AEAD (nach SP-1 sieht diese
Schicht nur opaken Chiffretext). Schützt damit nichts.
