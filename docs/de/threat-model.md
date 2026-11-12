# ScrambNet — Bedrohungsmodell

> Ein Netz, das totalen Schutz verspricht, lügt, und die Menschen, die echte Risiken tragen,
> verdienen zu wissen, wo genau der Schirm endet. Dieses Dokument ist der Vertrag.

## Gegner und Ergebnisse

| Gegner | Fähigkeit | Antwort des Netzes | Ergebnis |
|---|---|---|---|
| Lokaler Beobachter (dein ISP, ein Büro-WLAN) | Deinen Verkehr beobachten | Sieht einen gewöhnlichen TLS-Fluss zu einer gewöhnlichen Adresse | **Geschützt** |
| Nationaler Zensor | IPs blockieren, DPI-Fingerabdrücke abgleichen, Brücken aufzählen | Chamäleon-Transporte (Teil 4); Brücken über den sozialen Graphen mit Lox-artigen Vertrauensstufen verteilt | **Erreichbarkeit: umkämpft, kann auf null fallen** — ein Wettrüsten, dessen Sieg wir nicht versprechen; es degradiert L1→L4 und kann bei einer vollständigen Abschaltung ganz ausfallen (Teil 4 CT-18a). **Inhalt unterhalb von `k`: bedingungslos geschützt (I-2), unabhängig vom Transport.** |
| Bösartiges Relais auf einem Pfad | Beobachten, was es durchquert | Sieht einen Hop eines Anteils; Sphinx-Pakete sind überall identisch | **Geschützt** |
| Betreiber von Wächter *und* Ausgang eines Circuits | Eingang/Ausgang-Timing korrelieren | Dieser Circuit trägt einen Anteil, nicht die Nachricht; Wächter sind monatelang stabil; der paranoide Modus fügt Mix-Verzögerungen hinzu | **Gemindert** |
| `k`-Pfad-Gegner (hält Wächter+Ausgang auf `k` der `n` Anteil-Pfade gleichzeitig) | Vollständige Timing-Korrelation plus Anteil-Erfassung | Die Pfadauswahl erzwingt disjunkte Wächter, ASe, Jurisdiktionen, was gleichzeitige `k` Positionen zu einem Besetzungsproblem macht | **Gemindert** — dies ist das entworfene Restrisiko; erhöhe `n`, `k` nach Geschmack |
| Globaler passiver Gegner (sieht allen Verkehr überall) | Alles korrelieren | Schneller Modus: nichts. Paranoider Modus: Mixnet mit Verzögerungen und Decktraffic | **Außerhalb des Modells (schneller Modus)** — offengelegt, wie Tor es offenlegt |

## Was die Streuung genau ändert

Klassisches Onion-Routing versagt *katastrophal* bei einem schlechten Zug: Kontrolliere Wächter und
Ausgang des einzigen Circuits, und du erhältst sowohl die Verknüpfung (wer mit wem spricht) **als auch**,
wo die eigene Verschlüsselung des Ziels fehlt oder gebrochen ist, den Inhalt. Unter Streuung:

- **Inhalt** ist unterhalb von `k` erbeuteten Anteilen bedingungslos geschützt. Keine rechnerische
  Annahme ist beteiligt. Diese Untergrenze kann durch Kryptoanalyse oder Quantenfortschritt nicht erodiert werden.
  Bei oder oberhalb von `k` Anteilen setzt der Gegner den Geheimtext wieder zusammen und trifft auf das
  Ende-zu-Ende-AEAD — ein rechnerischer Gürtel, geschlüsselt aus einem vorab geteilten symmetrischen Geheimnis,
  sodass selbst diese Stufe einem künftigen Quantengegner nach dem Muster „harvest now, decrypt later"
  standhält (Spec SP-1a). Die Behauptung ist die Beständigkeit der Untergrenze, nicht die Unzerbrechlichkeit
  des Gürtels.
- **Verknüpfung** (Metadaten) auf einem einzelnen verletzten Anteil-Pfad ist immer noch ein echter Verlust: Der
  Gegner erfährt, dass *irgendein* Fluss zwischen dir und dem Anteil-Sammler eines Ziels lief.
  Die Streuung verengt, was ein Circuit verrät; sie hebt es nicht auf. Stabile Wächter,
  AS-disjunkte Pfadauswahl und das Mixen im paranoiden Modus sind die Minderungen.

## Annahmen

1. Die zugrunde liegenden Netze (ISPs, IXPs, Kabel, Clouds) sind feindlich oder kompromittiert.
2. Der Entwurf, der Code und alle Dokumente sind jedem Gegner vollständig bekannt (Kerckhoffs).
3. Relais werden von Fremden betrieben; ein konstanter Anteil ist bösartig und kolludiert.
4. Die Endpunkte sind ehrlich: Ein kompromittiertes Telefon verliert, bevor das erste Paket losgeht.
   Gerätesicherheit liegt außerhalb des Rahmens, ohne Vortäuschung gesagt.
5. Nutzer können den Client beschaffen. Reproduzierbare Builds plus eine öffentliche Spezifikation
   (jeder kann von Grund auf neu implementieren) sind die Antwort auf Binärvergiftung und auf das Verschwinden
   jedes offiziellen Vertriebskanals.

## Nicht-Ziele

- Einen Nutzer zu schützen, dessen Gerät kompromittiert ist.
- Zu verbergen, *dass* eine Region in der Masse Umgehungswerkzeuge nutzt (schneller Modus).
- Inhaltsmoderation auf der Netzschicht. Das Netz trägt Pakete, keine Meinungen;
  es schützt Dissidenten und ihre Gegner mit derselben Mathematik. Eine Infrastruktur
  ist nur glaubwürdig, wenn sie keine Seite wählen kann.

<a id="open-problems"></a>
## Offene Probleme

Zum Angriff markiert. Jedes Problem wird an **einem** Ort diskutiert: einem
einzigen [Issue](https://github.com/ScrambNet/scrambnet/issues) pro Problem, mit
dem englischen Text und allen Übersetzungen im selben Thread. Lies das Problem
hier in deiner Sprache; diskutiere es dort, im einen Issue, damit keine
Diskussion zersplittert.

1. **Durchsetzung der Disjunktheit.** Ein erster Pfadauswahl-Mechanismus liegt nun im Entwurf vor
   ([Spec Teil 3](spec/03-path-selection.md)) mit einem ausführbaren Strohmann in
   `poc/network_sim.py`; offen bleibt der harte Kern: Wie *verifiziert* ein Client,
   dass die `n` Pfade kein AS, keine Jurisdiktion, kein Rechenzentrum teilen — nur mit seiner Gossip-
   Stichprobe und einem vertrauenslos verteilten Inferenz-Datensatz (I-3), gegen Relais, die über
   alles lügen können außer ihren Signaturen?
2. **Sybil- und Eclipse-Resistenz** der Gossip-Stichprobe ohne zentralen Zuteiler.
   Walking Onions nimmt einen von einer Autorität signierten Schnappschuss an; wir haben die Autorität entfernt. Was
   ersetzt ihre Anti-Sybil-Funktion — Nachweis langlebiger Schlüssel? Gewichtung über den sozialen Graphen?
   Bandbreitenverifikation durch randomisiertes Sondieren?
3. **Parameter-Ökonomie.** Standardwerte für `n`, `k` je Verkehrsklasse; wann ersetzt Rabins IDA
   (billiger, rechnerisch) Shamir (bedingungslos) für Massendaten, und ist diese
   Herabstufung je standardmäßig akzeptabel?
4. **Anteil-Timing-Korrelation.** Die Inhalts-Nichtverknüpfbarkeit zwischen Anteilen (SP-7) ist geklärt und
   im PoC implementiert; das *Timing* nicht. `n` Anteile, die innerhalb von
   Millisekunden ins Netz eintreten, sind selbst ein Fingerabdruck. Jitter, Batching, Köder-Anteile: Was kostet jedes
   an Latenz, und was bringt es tatsächlich gegen einen Gegner, der mehrere Ausgänge beobachtet?
5. **Decktraffic-Ökonomie** im paranoiden Modus auf volumenbasierten Mobilverbindungen.
6. **Blackout-Adressierung.** Identitätsbasiertes Routing über Mesh-Store-and-Forward ohne eine
   aus dem Blackout erreichbare DHT.
7. **Bootstrap mit null Kontakten** für die Brücken-Verteilung über den sozialen Graphen.
8. **Update-Governance.** Multi-Signatur-Releases über Jurisdiktionen hinweg: wie viele Unterzeichner,
   wie gewählt, wie ersetzt — ohne das Komitee zu schaffen, das zum Kill-Switch wird.
9. **Dead-Drop-Metadaten und -Ökonomie.** Ein Drop sieht Ablagezeiten und Polling-Takt für
   ein Postfach innerhalb einer Epoche (Spec Teil 6). Polling-Verteilungen und Köderkosten auf volumenbasierten
   Verbindungen, Löschsemantik, Ablage-Bepreisung gegen Flutung, Speicheranreize:
   Was kostet jede Verteidigung, und was leckt jede?
