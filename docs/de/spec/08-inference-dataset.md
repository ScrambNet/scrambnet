# ScrambNet-Spezifikation — Teil 8: Der Inferenz-Datensatz
> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../../en/spec/08-inference-dataset.md)).

**Status: ENTWURF (DRAFT), und ein erklärtes Forschungsrisiko.** Dieser Teil
entscheidet, wie ein Client die IP-zu-AS- (und Grob-Jurisdiktions-)Karte erhält,
aus der Teil 3 schlussfolgert (PS-4), unter I-3 — keine Autorität — gegen Relais
und Datensatz-Hosts, die über alles lügen außer dem, was ein Hash oder eine
Signatur bindet. Strohmann-Werte sind mit `(s)` markiert. Die
Disjunktheits-Verifikations-*Verwendung* der Karte ist OP-1; ihre *Verteilung*
ist Roadmap-Punkt 2.3.

Die Hauptentscheidung ist in §1 angegeben und im Rest verteidigt. Lies zuerst §1
und §9 (das Residuum): zusammen sagen sie, was dieser Teil einbringt und was er
einräumt, nicht einbringen zu können.

## 1. Die Entscheidung, in zwei Sätzen

- **Es gibt keine kanonische Karte und keine Karten-Autorität.** Der Datensatz
  ist ein **reproduzierbares, inhaltsadressiertes Artefakt**, das jede Partei
  Byte für Byte aus öffentlichen Eingaben neu baut; zwei Clients stimmen überein,
  nicht weil sie einem Signierer vertrauen, sondern weil sie den **gleichen Hash**
  berechnet haben (ID-1, ID-5). Eine kanonische, von einer festen Menge signierte
  Wurzel wäre eine Verzeichnis-Autorität unter anderem Namen, und I-3 verbietet
  das.
- **Übereinstimmung erfolgt durch Reproduktion; Veröffentlichung durch einen
  anfügbaren (append-only) Transparenz-Log, in den jeder schreiben darf; Vertrauen
  beim ersten Abruf ist TOFU, als solches erklärt.** Der Log *segnet* keine Karte
  — er zeitstempelt und macht Mehrdeutigkeit (Equivocation) erkennbar (ID-6,
  ID-7). Die erste Karte eines frischen Clients ist ein
  Trust-on-First-Use-Moment, den späterer Gossip ihn als schlecht **erkennen**,
  nicht **verhindern** lässt (§7).

Das von der Roadmap gekennzeichnete ehrliche Ergebnis ist also das echte: **TOFU-
Karte + Transparenz-Log + Anomalie-Gossip, keine kanonische Karte.** Alles Weitere
unten ist die Konstruktion, die "reproduziere sie selbst und erkenne jeden, der
log" konkret macht, und §9 ist das Residuum, das keine noch so große Konstruktion
beseitigt.

## 2. Geltungsbereich und die Falle, die dieser Teil vermeidet

Teil 3 (PS-4, PS-5) verlangt von jedem Client, das AS und die Grob-Jurisdiktion
eines Relais *aus seinen `addrs`* zu schlussfolgern, unter Verwendung des
**eigenen** Datensatzes des Clients, niemals der Selbstdeklaration eines Relais
(GR-3). Bei diesem Teil geht es nur darum, **woher dieser Datensatz kommt und wie
zwei Clients wissen, dass sie denselben halten**, ohne eine vertrauenswürdige
Partei irgendwo in der Kette — Bau, Veröffentlichung oder Bootstrap.

Die Falle ist subtil und muss benannt werden: Der einfachste "vertrauenslose"
Entwurf ist ein signierter, kanonischer Schnappschuss, veröffentlicht von einer
kleinen Menge von Betreibern. Das ist genau die Walking-Onions-Autorität, die
sich dieses Projekt für Relais versagt hat (GR-1-Geltungsbereich), nun für
Geografie wieder eingeschmuggelt. Ein Karten-Signierer, der still eine Karte
ausliefern kann, die einen Block von ASes falsch beschriftet, kann die
ko-lokalisierten Relais eines Gegners für jeden Client disjunkt *aussehen*
lassen — eine Eklipse in Geografie-Granularität, die Teil 3 so sicher besiegt
wie ein schlechtes Relais-Verzeichnis es täte. Die Signierer-Menge ist also die
Bedrohung, und der Entwurf darf keine mit dieser Macht haben.

- **ID-1 (keine Karten-Autorität). [normativ]** Kein Schritt des Erhaltens,
  Validierens oder Aktualisierens des Datensatzes MUSS (MUST) darauf vertrauen,
  dass eine bestimmte Partei die Karte erzeugt, signiert oder gesegnet hat;
  gleichbedeutend: Das Erhalten und Validieren der Karte MUSS (MUST) allein mit
  nicht vertrauten Ersätzen möglich sein. Die einzigen vertrauenswürdigen
  Operationen sind: (a) das Neuberechnen eines Hashes und (b) das Neubauen des
  Artefakts aus öffentlichen Eingaben und das Vergleichen. Jedes
  Entwurfselement, das nicht durch einen nicht vertrauten Ersatz ersetzt werden
  kann, der (a) oder (b) ausführt, ist ein Defekt unter I-3 und MUSS (MUST)
  entfernt oder in §9 erklärt werden.

## 3. Was die Karte ist

- **ID-2 (Artefakt-Gestalt).** Der Datensatz ist ein einzelnes komprimiertes
  Artefakt, die **Karte**, die für den IPv4- und IPv6-Raum enthält:
  - eine **IP-Präfix → Ursprungs-AS**-Tabelle (Longest-Prefix-Match-Nachschlag)
    und
  - eine **AS → Grob-Jurisdiktion**-Tabelle, wobei "Jurisdiktion" eine Beschriftung
    auf **Länderebene** ist, abgeleitet aus RIR-Zuteilung, bewusst grob — feinere
    Granularität ist Rauschen, das dieser Teil nicht aufzulösen vorgibt (§9).
  Die Karte trägt einen selbstbeschreibenden Header: Format-Version `1`, die
  Schnappschuss-**epoch** (ID-4), das exakte Eingabe-Manifest (ID-3) und die
  Version des Bau-Werkzeugs. Das Artefakt wird durch `H = BLAKE2s(artifact)`
  adressiert (der Suite-Hash, Teil 0); `H` ist der einzige Name der Karte. Es gibt
  keine menschenlesbare Versions-Zeichenkette, der anstelle von `H` vertraut
  werden könnte.
- **ID-2a (Nachschlag ist total).** Jeder Nachschlag MUSS (MUST) entweder ein
  konkretes `(AS, Jurisdiktion)` oder den expliziten Wert **`unknown`**
  zurückgeben. `unknown` ist eine erstklassige Antwort, kein Fehler, und Teil 3
  (PS-5) behandelt es bereits konservativ (`unknown` teilt mit allem). Die Karte
  DARF NICHT (MUST NOT) raten, um ein `unknown` zu vermeiden; eine erfundene
  Antwort ist schlimmer als eine eingeräumte Lücke, denn sie besiegt PS-5
  stillschweigend.

## 4. Wie die Karte gebaut wird (reproduzierbar, aus öffentlichen Eingaben)

Der Bau ist eine **reine Funktion benannter öffentlicher Eingaben auf ein
byte-identisches Artefakt**. Determinismus ist das ganze Spiel: Können zwei
ehrliche Parteien auseinanderdriften, hört Hash-Gleichheit (ID-5) auf, "gleiche
Karte" zu bedeuten, und der Entwurf bricht in das Bedürfnis nach einer Autorität
zusammen, die Gleichstände bricht.

```
  ÖFFENTLICHE EINGABEN (im Manifest per Inhalts-Hash fixiert, ID-3)
  ┌────────────────────────┐   ┌────────────────────────┐
  │ RouteViews + RIPE RIS  │   │ 5 RIR-Delegations-     │
  │ BGP MRT RIB-Dumps      │   │ dateien (AS → Land)    │
  │ (Präfix → Ursprungs-AS)│   │                        │
  └───────────┬────────────┘   └───────────┬────────────┘
              │       epoch = letzter Dump ≤ 00:00 UTC-Grenze (ID-4)
              └───────────────┬───────────────┘
                              ▼
            ┌───────────────────────────────────┐
            │  DETERMINISTISCHER BAU (reine Fn)   │
            │  feste Ordnung (ID-4a), feste       │
            │  Gleichstandsauflösung (ID-4b),     │
            │  keine fließenden Eingaben (ID-4c), │
            │  kanonischer Container (ID-4d)      │
            └─────────────────┬─────────────────┘
                              ▼
                      Karten-Artefakt
                              │
                              ▼
                   H = BLAKE2s(artifact)   ← der EINZIGE Name der Karte (ID-2)

  Alice ─ gleiche Eingaben ─▶ H_A         Zwei ehrliche Parteien, die dieselben
  Bob   ─ gleiche Eingaben ─▶ H_B         Eingaben fixieren, erhalten H_A == H_B.
                                          Übereinstimmung ist Hash-Gleichheit
                                          (ID-5), nicht Vertrauen in einen
                                          Signierer. Reproduktion ist der Richter.
```

- **ID-3 (öffentliche Eingaben, per Inhalt fixiert). [normativ]** Die Karte MUSS
  (MUST) nur aus Eingaben gebaut werden, die öffentlich, reproduzierbar und selbst
  im Manifest des Artefakts durch ihre eigenen Hashes inhaltsfixiert sind:
  - **BGP-Routing-Tabellen** für das Ursprungs-AS: die Kollektoren des
    **RouteViews**-Projekts und die **RIPE RIS**-Kollektoren (MRT-`RIB`-Dumps).
    Das sind die üblichen öffentlichen BGP-Archive mit mehreren Beobachtungspunkten;
    mehrere Kollektoren aus beiden Projekten zu verwenden ist selbst eine
    Diversitäts-Maßnahme (die Sicht keines einzelnen Kollektors ist maßgeblich,
    ID-3a).
  - **RIR-Delegationsstatistiken** für die AS → Land-Zuordnung: die veröffentlichten
    **delegated-extended**-Dateien der fünf RIRs (ARIN, RIPE NCC, APNIC, LACNIC,
    AFRINIC). Diese liefern Zuteilungs-Ländercodes für AS-Nummern und Adressblöcke,
    ohne dass irgendjemand sich selbst deklariert.
  Das Manifest MUSS (MUST) jede Eingabedatei per URL-unabhängigem Inhalts-Hash und
  per quellen-angegebenem Zeitstempel auflisten, sodass die Eingaben — nicht ein
  Server — den Bau definieren. Eine Partei baut neu, indem sie Eingaben mit diesen
  Hashes von **irgendeinem** Spiegel abruft (I-3: die Quelle ist ersetzbar; die
  Bytes sind fixiert).
- **ID-3a (Ursprungsauflösung über mehrere Beobachtungspunkte).** Das
  Ursprungs-AS für ein Präfix MUSS (MUST) über **alle** manifestierten Kollektoren
  nach einer festen Regel aufgelöst werden (ID-4b), nicht aus einem Kollektor. Ein
  Präfix, das über Beobachtungspunkte hinweg mit widersprüchlichen Ursprüngen
  gesehen wird, wird deterministisch aufgelöst und, wo der Widerspruch real ist
  (MOAS — multiple-origin AS), als **Menge** festgehalten, die Teil 3 als
  "möglicherweise jede davon" behandelt, d. h. konservativ geteilt (§9). Die Karte
  DARF NICHT (MUST NOT) stillschweigend eine auswählen.

### 4.1 Determinismus-Gefahren und wie der Bau sie fixiert

Jede Gefahr unten ist eine Stelle, an der zwei ehrliche Bauer verschiedene Bytes
erzeugen könnten. Das Bau-Verfahren MUSS (MUST) jede beseitigen; ein Bau, der das
nicht tut, ist nicht konform, weil er ID-5 nicht stützen kann.

- **ID-4 (Schnappschuss-epoch — Dump-Zeitpunkt). [normativ]** BGP- und RIR-Daten
  ändern sich fortlaufend, daher ist "der aktuelle Dump" keine Funktion. Der Bau
  MUSS (MUST) eine einzige **epoch-Grenze** fixieren: einen UTC-Zeitpunkt in festem
  Takt (Strohmann: der **00:00-UTC**-Schnappschuss in **wöchentlichem (s)** Takt —
  Teil-0-Commits verwenden bereits UTC) und MUSS (MUST) für jeden manifestierten
  Kollektor/jede RIR den **letzten Dump verwenden, dessen quellen-angegebener
  Zeitstempel ≤ der epoch-Grenze ist**. Zwei Bauer, die dieselbe epoch anzielen,
  wählen daher dieselben Eingabedateien aus, unabhängig davon, wann sie laufen. Die
  epoch steht im Artefakt-Header (ID-2) und im Urbild von `H`.
- **ID-4a (Reihenfolge).** Alle Tabellen MÜSSEN (MUST) in einer **festen
  Gesamtordnung** ausgegeben werden: Präfixe sortiert nach (Adressfamilie,
  numerischer Netzadresse, Präfixlänge); AS-Einträge nach numerischer ASN;
  Jurisdiktionen nach ihrer festen Ländercode-Zeichenkette. Keine
  Map-Iterationsreihenfolge, Hash-Tabellen-Reihenfolge oder
  Eingabedatei-Reihenfolge darf in die Ausgabe gelangen.
- **ID-4b (Gleichstandsauflösung ist spezifiziert, nicht
  implementierungsdefiniert). [normativ]** Jede Stelle, an der die Daten
  mehrdeutig sind, MUSS (MUST) eine in diesem Teil geschriebene Regel haben, ohne
  dass ein "nimm eine" dem Implementierer überlassen bleibt:
  - *Ursprungs-AS über Kollektoren:* nimm die beobachtete Ursprungsmenge; ist es
    ein einzelnes AS, gib es aus; sind es mehrere (MOAS), gib die volle Menge
    aufsteigend sortiert aus. Kollabiere nie ein MOAS per Häufigkeit auf ein AS —
    das ist eine Vermutung (§9).
  - *Überlappende Präfixe:* Die Longest-Prefix-Match-Semantik bleibt durch das
    Speichern aller Präfixe erhalten; der Nachschlag, nicht der Bau, löst die
    Spezifität auf.
  - *AS-zu-Land-Widerspruch über RIRs:* Sind sich die Delegationsdateien über das
    Land eines AS uneinig, gib `unknown` für die Jurisdiktion dieses AS aus. Eine
    Uneinigkeit zwischen öffentlichen Registern ist genau ein Fall, den die Karte
    nicht per Dekret auflösen darf.
- **ID-4c (fließende Eingaben verboten).** Der Bau DARF NICHT (MUST NOT) irgendeine
  Eingabe konsultieren, die nicht im Manifest steht — kein Live-DNS, kein WHOIS zur
  Bauzeit, keine Geolokalisierungs-Datenbank unter einer Lizenz, die
  Weiterverbreitung verbietet oder nicht reproduzierbar ist, kein kommerzieller
  IP-Intelligence-Feed. Jedes Ausgabe-Byte lässt sich auf eine gehashte
  öffentliche Eingabe zurückführen. (Das schließt die bequemen-aber-unverifizierbaren
  Feeds aus; ihre Genauigkeit ist die Autorität nicht wert, die sie wieder
  einführen.)
- **ID-4d (kanonischer Container).** Die Komprimierung und Rahmung des Artefakts
  MUSS (MUST) deterministisch sein (fester Codec, feste Stufe, keine Zeitstempel
  oder Dateinamen in den Container-Metadaten). Der Bau ist eng genug spezifiziert,
  dass ein konformes Bau-Werkzeug selbst reproduzierbar ist (Roadmap 4.2), und ein
  implementierungsübergreifender **Karten-Testvektor** (ein Eingabe-Manifest →
  erwartetes `H`) MUSS (MUST) existieren, damit eine zweite Implementierung
  beweisen kann, dass sie das identische Artefakt baut (bindet an Roadmap 3.2).

## 5. Wie zwei Clients übereinkommen, dass sie dieselbe Karte halten

- **ID-5 (Übereinstimmung ist Hash-Gleichheit, nichts weiter). [normativ]** Zwei
  Clients halten dieselbe Karte **genau dann, wenn** ihre Artefakt-Hashes `H`
  gleich sind. Der Vergleich ist eine 32-Byte-Gleichheitsprüfung; er braucht
  keinen Signierer, kein Quorum, keine Autorität. Clients tauschen `H` per Gossip
  aus (ID-8); gleiches `H` ist Beweis derselben Karte, ungleiches `H` ist Beweis,
  dass sie sich unterscheiden, und MUSS (MUST) dem Nutzer als **Divergenz**
  gemeldet werden (ID-9), niemals stillschweigend zu einer der beiden Seiten hin
  abgeglichen.
- **ID-5a (Neubau ist der Schiedsrichter).** Halten zwei Clients verschiedene `H`
  für dieselbe epoch, ist der Streit von **jedem** auflösbar, ohne Berufung auf
  eine Autorität: aus den manifestierten Eingaben neu bauen (ID-3) und sehen,
  welches `H` die öffentlichen Eingaben tatsächlich erzeugen. Eine Karte, deren
  `H` aus ihrem angegebenen Manifest nicht reproduziert werden kann, ist per
  Definition nicht die Karte dieser Eingaben und MUSS (MUST) abgelehnt werden
  (ID-5b). Das ist die Eigenschaft, die es dem System erlaubt, keine Autorität zu
  haben: *Wahrheit ist Reproduzierbarkeit, nicht Signatur.*
- **ID-5b (das Unreproduzierbare ablehnen).** Ein Client, der die Eingaben hat
  (oder sie abruft) und feststellt, dass `H ≠ BLAKE2s(rebuild(manifest))`, MUSS
  (MUST) diese Karte verwerfen und SOLLTE (SHOULD) die Diskrepanz als Anomalie per
  Gossip verbreiten (ID-10). Ein Client ohne die Bandbreite zum Neubauen DARF (MAY)
  eine Karte zu TOFU-/Konsens-Bedingungen akzeptieren (§6, §7), MUSS (MUST) sie
  aber als **unverifiziert** führen, bis er (oder ein Peer, mit dem er dann
  übereinstimmt) neu baut.

## 6. Der Transparenz-Log (und warum er nicht die Autorität ist)

Hash-Gleichheit sagt zwei Clients, dass sie sich *unterscheiden*; sie verteidigt
für sich allein nicht gegen einen Gegner, der **verschiedenen** Clients
**verschiedene** Karten zuführt und jeden Client intern konsistent hält — einen
**Split-View-Angriff (Equivocation)**. Der Transparenz-Log existiert für genau
diese Bedrohung und für nichts weiter.

```
  DER SPLIT-VIEW-ANGRIFF, UND WIE GOSSIP IHN FÄNGT

  Ein feindlicher Log versucht, zwei Sichten zu zeigen, die sich nie treffen:

     Log ──Wurzel X (Karte H_good)──▶  Alice   "meine Karte ist bestätigt"
         └─Wurzel Y (Karte H_bad )──▶  Bob     "meine Karte ist bestätigt"

  Jeder Client allein sieht eine konsistente Geschichte. Aber Wurzeln werden
  über den GR-6-Kanal (ID-7a) per Gossip verbreitet, sodass ein dritter Client
  Carol BEIDE hört:

        Alice ──Wurzel X──┐
                          ├──▶  Carol verlangt einen KONSISTENZBEWEIS
        Bob   ──Wurzel Y──┘     zwischen X und Y.
                               Sind X und Y nicht Erweiterungen eines
                               anfügbaren Baums, SCHEITERT der Beweis:
                               ✗  kryptografischer Beweis, dass der Log
                                  Equivocation beging → Log als feindlich
                                  markiert, per Gossip verbreitet (ID-10)

  Der Log sagt nie, welche Karte GUT ist — das tut die Reproduktion (ID-5a).
  Er macht nur das Lügen gegenüber verschiedenen Leuten zugleich erkennbar.
  Jeder darf anfügen (ID-7, erlaubnisfrei), also ist der Log ein schwarzes
  Brett, keine Autorität — was ihn vom I-3-Verbot freihält.
```

- **ID-6 (was der Log ist).** Der Log ist ein **anfügbarer (append-only)
  Merkle-Baum** (RFC 6962 / Certificate-Transparency-Struktur: ein Merkle-Baum
  über eine Folge von Blättern, mit Inklusionsbeweisen und Konsistenzbeweisen
  zwischen zwei Baumgrößen). Jedes **Blatt** ist eine Karten-Ankündigung: `(epoch,
  H, input-manifest-hash)`. Der Zustand des Logs wird durch seinen **signierten
  Baumkopf (signed tree head)** zusammengefasst — hier ein **Wurzel-Hash** bei
  einer Baumgröße. Der Log beweist zwei Dinge kryptografisch: dass ein gegebenes
  `H` **enthalten ist** (Inklusionsbeweis) und dass der Log **nur je gewachsen,
  nie die Historie umgeschrieben hat** (Konsistenzbeweis). Er beweist nichts
  darüber, ob `H` eine *gute* Karte ist — das tut die Reproduktion (ID-5a).
- **ID-7 (wer anfügen darf — erlaubnisfrei, daher keine Autorität). [normativ]**
  **Jeder** DARF (MAY) ein Blatt anfügen, das eine von ihm gebaute Karte
  ankündigt; es gibt keinen privilegierten Anfüger, keine Erlaubnisliste, keine
  Signierer-Menge, deren Signatur eine Karte offiziell macht. Der Log ist daher
  **nicht** das, dem vertraut wird — er ist ein **bezeugtes,
  manipulations-evidentes schwarzes Brett**. Seine einzige Macht ist, Equivocation
  *erkennbar* zu machen; er hat **keine Macht, die Karte zu wählen**, was ihn vom
  I-3-Verbot freihält. Ein Log, der Anfügungen hinter eine Signierer-Menge
  sperrte, WÄRE die von I-3 verbotene Verzeichnis-Autorität, und ein solcher
  Entwurf ist nicht konform (ID-1).
- **ID-7a (Equivocation-Erkennung über per Gossip verbreitete Wurzeln).
  [normativ]** Die Verteidigung gegen eine Split-View ist **nicht** das Vertrauen
  in den Log-Betreiber; sie ist das **Verbreiten der signierten Baumköpfe des Logs
  per Gossip über den bestehenden GR-Gossip-Kanal** (GR-6) und das Verlangen von
  **Konsistenzbeweisen** zwischen je zwei Wurzeln, die ein Client sieht. Legt ein
  Log je zwei Baumköpfe vor, die keine konsistenten Erweiterungen voneinander sind
  — die Signatur der Equivocation —, hat jeder Client, der beide beobachtet
  (direkt oder über eine von einem Peer per Gossip verbreitete Wurzel),
  **kryptografischen Beweis**, dass der Log log, und MUSS (MUST) diesen Log als
  feindlich behandeln (ID-10). Weil Wurzeln weit per Gossip verbreitet werden (GR-6
  mischt Quellen, GR-8), kann ein Log Client A nicht lange Wurzel X und Client B
  Wurzel Y zeigen, ohne dass irgendein Client beide hält und ihn ertappt.
- **ID-7b (mehrere Logs, kein kanonischer). [normativ]** Es gibt **keinen
  einzelnen Log.** Clients MÜSSEN (MUST) **mehrere unabhängige Logs** unterstützen
  und eine Karte nur dann als log-bestätigt behandeln, wenn sie, mit konsistenten
  per Gossip verbreiteten Wurzeln, in einem konfigurierbaren Quorum der Logs
  auftaucht, die der Client beobachtet (Strohmann: **≥2 der Logs in seiner Menge
  (s)**). Das beseitigt den letzten einzelnen Punkt: Kein einzelner Log-Betreiber
  ist tragend, und die Log-Menge eines Clients — wie seine Relais-Stichprobe — ist
  vielfältig und ersetzbar (GR-8-Begründung auf Logs angewandt). Ein Log, der
  dunkel wird, wird umgangen, genau wie ein Relais, das dunkel wird.
- **ID-7c (der Log speichert Zusagen, nicht die Karte).** Blätter tragen `(epoch,
  H, manifest-hash)` — Dutzende Bytes — niemals das Artefakt. Die Karte selbst wird
  inhaltsadressiert per `H` von irgendeinem Spiegel oder Peer abgerufen (ID-8); der
  Log bezeugt nur, *welche* `H`-Werte angekündigt wurden und *wann*, sodass die
  Log-Speicherung trivial bleibt und kein Log zum Verteilungs-Flaschenhals wird.

## 7. Das Bootstrap-Paradox, ehrlich angegeben

Ein frischer Client hat keine Relais-Stichprobe, die er bewerten kann, und keine
vorherige Karte; er muss seine **erste** Karte über Pfade abrufen, deren
Disjunktheit er **noch nicht verifizieren kann** (diese Verifikation braucht genau
die Karte, die er abruft). Das ist eine echte zirkuläre Abhängigkeit, und dieser
Teil gibt nicht vor, sie zu brechen.

```
  DIE ERSTE KARTE IST TRUST-ON-FIRST-USE (ID-8) — IHR SCHADEN IST BEGRENZT

  frischer Client ──▶ erste Karte über Kanäle holen, die er noch nicht bewerten kann
                      │
                      ▼
        ┌───────────────────────────┐
        │  Zustand: UNVERIFIED-TOFU  │  UI: "du vertraust deiner ersten
        │  (dem Nutzer gezeigt)      │       Karte; noch nicht bestätigt"
        └─────────────┬─────────────┘
                      │  über die nächsten epochs, ENTWEDER:
         ┌────────────┴─────────────┐
         ▼                          ▼
   aus Eingaben neu bauen     Wurzeln gossippen + Peer-H
   (ID-5a): H passt?          über Schwelle einig?
         │                          │
    ja ──┴── nein              ja ──┴── nein (driftet weiter)
     ▼       ▼                  ▼        ▼
  VERIFIZ.  ANOMALIE         VERIFIZ.   ANOMALIE gegossippt (ID-10),
            (ID-5b,10)                 Nutzer gewarnt (ID-8b)

  Selbst eine VÖLLIG feindliche erste Karte ist begrenzt (ID-8a):
    1. die I-2-Untergrenze bleibt unberührt, ABER eine *lenkende* Karte kann den
       Gegner über k hinaus manövrieren (den ehrlichen Pool kollabieren, PS-12) ->
       Inhalt KANN für eine unverifizierte Karte oberhalb einer ~15%-Besitz-
       Schwelle fallen. Nicht nur Metadaten. Begrenzt durch die k/n-Marge + PS-12-
       Verteidigungen, nicht durch "geht nicht".
    2. vorübergehend + erkennbar — der Gegner muss den Client FÜR IMMER
       verfinstern (eclipsen), um sie verborgen zu halten (das ist OP-2, keine
       neue Schwäche hier).
    3. unfälschbar — der Gegner kann die öffentlichen Eingaben nicht dazu bringen,
       auf ein schlechtes H neu zu bauen. Ein Neubau, oder ein ehrlicher Peer, der
       es tat, konvergiert zur Wahrheit.
```

- **ID-8 (Bootstrap ist Trust-on-First-Use, erklärt). [normativ]** Die erste
  Karte, die ein frischer Client erhält, ist eine **TOFU**-Entscheidung. Der Client
  MUSS (MUST) sie über so viele **unabhängige** Kanäle erhalten, wie er hat
  (Strohmann: die Out-of-Band-Bridge-Linie von GR-10 plus zwei oder mehr
  öffentliche Spiegel, über verschiedene Netze erreicht (s)), MUSS (MUST) von allen
  das **gleiche `H`** verlangen, bevor er provisorisch akzeptiert, und MUSS (MUST)
  die Karte als **unverified-TOFU** festhalten, bis er entweder (a) aus Eingaben
  neu baut (ID-5a) oder (b) konsistente per Gossip verbreitete Wurzeln und
  Peer-`H`-Übereinstimmung über einer Konfidenzschwelle ansammelt (ID-7a, ID-9).
  Der Client MUSS (MUST) diesen Zustand sichtbar machen: *Du vertraust deiner
  ersten Karte; sie wurde noch nicht bestätigt.*
- **ID-8a (Schranke dafür, was dem Gegner eine schlechte erste Karte einbringt).
  [normativ]** Ein Gegner, der den gesamten ersten Abruf eines frischen Clients
  kontrolliert, kann ihm eine Karte geben, die ASes so falsch beschriftet, dass
  ko-lokalisierte Relais disjunkt aussehen. Die Schranke für den Schaden ist
  dreifach und MUSS (MUST) vom Entwurf gewahrt bleiben:
  1. **Der Inhalt bleibt auf der Untergrenze.** Selbst eine völlig feindliche Karte
     kann die I-2-Inhalts-Untergrenze nicht senken: Sie kann den Client nur die
     *Disjunktheit falsch beurteilen* lassen, was (gemäß PS-11 und dem Simulator,
     §10) **Verknüpfbarkeit weit schneller als Inhalt** erodiert — ein Inhaltsbruch
     braucht immer noch den Gegner auf ≥`k` Circuits zugleich. Eine schlechte Karte
     ist ein Metadaten-Angriff, kein Inhalts-Angriff. Diese Asymmetrie ist der
     einzige wichtigste Grund, warum das Bootstrap-Paradox überlebbar ist.
  2. **Sie ist vorübergehend und erkennbar, nicht dauerhaft.** In dem Moment, in dem
     der Client seine Wurzel/sein `H` per Gossip verbreitet (ID-9) oder neu baut
     (ID-5a), sticht eine Karte hervor, die kein ehrlicher Peer und keine
     öffentliche Eingabe bestätigt. Der Gegner muss den Client **für immer**
     verfinstern (eclipsen), um die schlechte Karte unentdeckt zu halten — was das
     OP-2-Eklipse-Problem ist, keine neue Schwäche, die dieser Teil einführt.
  3. **Sie kann Reproduktion nicht fälschen.** Der Gegner kann ein schlechtes `H`
     ausliefern, aber er kann die öffentlichen Eingaben nicht dazu bringen, auf
     dieses `H` neu zu bauen (ID-5a). Ein Client, der je neu baut oder je einen
     Peer trifft, der es tat, konvergiert zur echten Karte.
- **ID-8b (erkennen, nicht zu verhindern beanspruchen). [normativ]** Dieser Teil
  liefert **Erkennung eines schlechten Bootstraps im Nachhinein**, nicht dessen
  Verhinderung. Ein konformer Client DARF NICHT (MUST NOT) eine TOFU-Karte als
  verifiziert darstellen, MUSS (MUST) sie als Gossip neu bewerten und (optional)
  Neubau-Ansammlung betreiben und MUSS (MUST) warnen, wenn Bestätigung nicht
  innerhalb eines konfigurierbaren Fensters eintrifft (Strohmann: einige epochs
  (s)). "Wir können eine schlechte erste Karte nicht verhindern; wir machen es
  teuer und schließlich unmöglich, sie unentdeckt zu behalten" ist die ehrliche
  Behauptung, und es ist die Behauptung, die die UI angibt.

## 8. Damit leben: Auffrischung und Divergenz-Behandlung

- **ID-9 (Karten-Frische und Gossip).** Clients MÜSSEN (MUST) zur Karte der
  aktuellen epoch hin auffrischen (ID-4-Takt) und MÜSSEN (MUST) ihr aktuelles
  `(epoch, H)` und die Log-Wurzeln, die sie halten, über GR-6-Stapel per Gossip
  verbreiten, unterworfen der GR-8-Quellenmischung, sodass keine einzelne
  Peer-Klasse die Sicht eines Clients darauf dominieren kann, welche Karte aktuell
  ist (dieselbe Eklipse-Verteidigung, wiederverwendet). Ein Client DARF NICHT (MUST
  NOT) eine Karte danach gewichten, wie viele Peers sie melden, *bevor* er die
  Regel "zähle nur unabhängig verifizierte Quellen" von GR-8/PS-10 anwendet — ein
  Sybil kann eine schlechte Karte nicht per schierer Zahl in den Konsens wählen
  (bindet an OP-2).
- **ID-9a (Divergenz wird gezeigt, nicht verborgen).** Wenn das `H` eines Clients
  für dieselbe epoch von einem bestätigten Quorum (ID-7b) abweicht, MUSS (MUST) er
  seine eigene Karte als verdächtig behandeln, Neubau oder erneuten Abruf
  versuchen und die Divergenz dem Nutzer in der bestehenden Ehrlichkeits-Fläche von
  Teil 3 melden (PS-9): *Deine Sicht auf die Geografie des Netzes widerspricht der
  deiner Peers; Disjunktheits-Urteile können falsch sein.* Schweigen hier ließe
  eine Geografie-Eklipse ungesehen laufen.
- **ID-10 (Anomalie-Gossip). [normativ]** Drei Ereignisse sind **Anomalien**, die
  jeder Client per Gossip verbreiten MUSS (MUST), wenn er sie erkennt, weil sie die
  beobachtbaren Signaturen der Angriffe sind, die dieser Teil nicht verhindern,
  sondern nur sichtbar machen kann: (a) ein `H`, das die Reproduktion aus seinem
  Manifest scheitern lässt (ID-5b); (b) ein Log, der inkonsistente Wurzeln vorlegt,
  d. h. bewiesene Equivocation (ID-7a); (c) eine persistente `H`-Divergenz gegen
  ein bestätigtes Quorum (ID-9a). Anomalie-Gossip ist das Immunsignal des Netzes;
  ein Client DARF NICHT (MUST NOT) es unterdrücken, um gesund zu erscheinen.

## 9. Die Verschmelzungsnaht mit der Update-Governance (OP-8 / Punkt 4.1)

Die Wurzel-Veröffentlicher der Karte und die Software-Release-Signierer sehen
aus, als könnten sie ein Mechanismus sein. **Position: sie im Vertrauen getrennt
halten, auch wenn sie Werkzeuge teilen.** Die Begründung ist, dass sie
**entgegengesetzte Vertrauens-Gestalten** haben:

- **ID-11 (Karten-Vertrauen ist Reproduktion, nicht Signatur). [normativ]** Der
  Karte wird vertraut, weil sie **aus öffentlichen Eingaben neu baut** (ID-5a);
  ihre Korrektheit ruht **nicht** darauf, *wer* sie veröffentlicht hat. Einer
  Release-Binärdatei wird dagegen vertraut, weil sie **aus öffentlichem Quellcode
  neu baut** (reproduzierbare Builds, Roadmap 4.1/4.2) — ebenfalls Reproduktion,
  ebenfalls nicht Signatur. Der *Vertrauens-Anker* ist also derselbe —
  **Reproduzierbarkeit, niemals Autoren-Identität** —, und das Projekt MUSS (MUST)
  beide über ihn leiten. Aber die **Signierer-/Anfüger-Mengen MÜSSEN (MUST)
  verschieden bleiben**: Die Anfüger des Karten-Logs an die Release-Signierer zu
  binden, erschüfe eine einzige Liste, deren Kompromittierung *sowohl* die
  Geografie-Inferenz *als auch* die Software vergiftet, d. h. genau das
  konzentrierte Zwangsziel, das Punkt 4.1 zu vermeiden gebaut ist. Der Karten-Log
  ist erlaubnisfrei (ID-7); der Release-Prozess darf eine benannte (pseudonyme)
  Signierer-Menge haben, die einen Build nur *lokalisiert*, den sie nicht fälschen
  kann. Sie zu verschmelzen, tauscht die Erlaubnisfreiheit der Karte gegen die
  Liste des Release-Prozesses — die falsche Richtung.
- **ID-11a (geteilte Werkzeuge sind in Ordnung; geteilte Autorität nicht).** Beide
  DÜRFEN (MAY) dieselbe Transparenz-Log-Konstruktion (ID-6) und denselben
  Gossip-Kanal (GR-6) wiederverwenden — das Teilen von *Mechanismus* kostet nichts.
  Was sie NICHT (MUST NOT) teilen dürfen, ist eine Menge von Parteien, deren
  Signatur für beide tragend ist, denn diese Menge wäre der von I-3 verbotene
  Not-Aus-Schalter, nun fähig, sowohl die Karte als auch den Code umzulegen.

## 10. Was dieser Teil nicht löst (das erklärte Residuum)

Dieser Teil lässt zwei ehrliche Clients beweisbar übereinstimmen oder beweisbar
erkennen, dass sie sich unterscheiden. Er macht die Karte **nicht** *wahr*. Die
Lücke zwischen "der Karte, auf die sich jeder ehrliche Client einigt" und "wo die
Relais physisch sind" ist das Residuum, und es ist real:

- **Ko-Lokation hinter disjunkten Präfixen ist hier nicht erkennbar.** Ein Gegner,
  der Relais in einem Rechenzentrum betreibt, während er Adressraum ankündigt, den
  die öffentlichen BGP-/RIR-Daten **verschiedenen** ASes zuschreiben, wird von der
  **korrekten** Karte als disjunkt beschriftet. Kein reproduzierbarer Bau
  öffentlicher Daten kann durch eine wahrheitsgemäß aussehende BGP-Ankündigung
  hindurch auf das Rack dahinter sehen. Das steht im tiefsten ehrlichen Punkt der
  Roadmap, und es hält: **Vom Overlay aus verifizierst du Konsistenz gegen einen
  Datensatz mit beschränktem Vertrauen, nicht wahre Disjunktheit.** Die Aufgabe ist,
  zu begrenzen, was dieser Gegner gewinnt (ID-8a: der Inhalt bleibt auf der
  Untergrenze; der Angriff ist Metadaten/Verknüpfbarkeit), nicht, ihn
  wegzureden.
- **BGP ist stellenweise echt mehrdeutig.** MOAS-Präfixe (ein Präfix, legitim von
  mehreren ASes originiert), **Geschwister-ASes (sibling ASes)** unter einem
  Betreiber (verschiedene ASNs, eine kontrollierende Partei — die Karte sieht zwei
  ASes, wo die Disjunktheits-Realität eines ist) und **anycast** (ein Präfix, viele
  physische Standorte) sind keine Datensatz-Fehler; sie sind das Terrain. Die Karte
  behandelt sie konservativ (ID-3a, ID-4b: MOAS → Menge, Register-Widerspruch →
  `unknown`), was Verfügbarkeit kostet (mehr `unknown` ⇒ mehr Rückfall, PS-11) statt
  Sicherheit. Die Geschwister-AS-Erkennung ist ausdrücklich **außerhalb des
  Geltungsbereichs** eines reinen BGP-/RIR-Baus und bleibt als erklärter toter
  Winkel: Zwei Geschwister-ASes werden als disjunkt gezählt, wenn sie es nicht
  sind.
- **Jurisdiktion ist per Entscheidung grob.** Aus RIR abgeleitete Beschriftungen
  auf Länderebene sind die Auflösungs-Untergrenze, auf die sich dieser Teil
  festlegt. Feinere jurisdiktionelle Schlussfolgerung (rechtliche
  Kooperationsblöcke, Realität der Rechtshilfe) ist bewusst **nicht** kodiert — sie
  wäre ein Ermessensurteil, das kein reproduzierbarer Bau treffen kann, ohne eine
  vertrauenswürdige Meinung zu importieren, was ID-1 verbietet.

Die ehrliche Zusammenfassung: **Die Fehlerrate des Datensatzes ist ein erklärtes,
von null verschiedenes Residuum, kein auf null zu behebender Defekt.** Sie ist der
Preis dafür, eine Autorität zu verweigern. Die richtige Antwort ist nicht, sie zu
verbergen, sondern sie dem Simulator zuzuführen und dem Nutzer das erreichte
Niveau zu zeigen (PS-9, PS-11).

## 11. Die Fehlerrate speist den Simulator (nicht weggewedelt)

Das Residuum von §10 ist nicht rhetorisch; es ist die exakte Größe, die der
Simulator bereits verbraucht. `poc/network_sim.py` legt **`infer_error`** offen —
die Wahrscheinlichkeit, dass das von einem Client geschlussfolgerte AS für ein
Relais **falsch** ist (halb der Zeit ein falsches AS, halb der Zeit `unknown`), was
einen Datensatz modelliert, der sowohl falsch kartiert als auch Lücken hat
(network_sim.py, `Network.random`). Die hier spezifizierte Karte **ist** dieser
Datensatz, und ihr gemessenes Residuum **ist** dieser Stellknopf:

- **ID-12 (die Karte deklariert eine gemessene Fehlerrate). [normativ]** Ein
  konformes Karten-Release MUSS (MUST) mit einer **gemessenen Fehlerschätzung**
  ausgeliefert werden — seiner Uneinigkeitsrate gegen unabhängige öffentliche
  Ground-Truth-Stichproben und seinem `unknown`-Anteil —, reproduzierbar aus
  öffentlichen Daten abgeleitet, sodass die Zahl selbst keine Autorität hinter sich
  hat. Dieses gemessene Paar (Fehlkartierungsrate, `unknown`-Rate) ist der Wert,
  den ein Client der Konfidenz-Maschinerie von Teil 3 zuführt (Roadmap 2.2), und
  der Wert, den der Simulator als `infer_error` durchfährt.
- **ID-12a (der Null-Fehler-Fall ist der beste Fall, nie der erwartete).** Gemäß
  PS-11 sind die Null-Fehler-, Vollsicht-Zahlen des Simulators der **beste** Fall;
  ein konformer Client MUSS (MUST) das erreichte Disjunktheits-Niveau (PS-9) unter
  Verwendung des deklarierten Fehlers seiner **echten** Karte darstellen, und die
  UI DARF NICHT (MUST NOT) eine Inhaltsbruch-Zahl zitieren, als begrenzte sie auch
  die Verknüpfbarkeit (PS-11) — die Asymmetrie, die eine schlechte Karte überlebbar
  macht (ID-8a), ist dieselbe Asymmetrie, die die UI nicht als Sicherheit
  falsch melden darf.

## 12. Hier eingeführte Anforderungen

- **ID-1** — keine Karten-Autorität: vertraue nur der Reproduktion und dem
  Hashing.
- **ID-2 / ID-2a** — Artefakt-Gestalt (Präfix→AS, AS→Grob-Jurisdiktion),
  inhaltsadressiert durch `H`; Nachschläge total, `unknown` ist erstklassig.
- **ID-3 / ID-3a** — nur öffentliche fixierte Eingaben (RouteViews + RIPE RIS BGP,
  fünf RIR-Delegationsdateien); Ursprungsauflösung über mehrere
  Beobachtungspunkte, MOAS als Menge gehalten.
- **ID-4 / ID-4a–d** — Determinismus: UTC-epoch fixiert den Dump-Zeitpunkt, feste
  Gesamtordnung, spezifizierte Gleichstandsauflösung, keine fließenden Eingaben,
  kanonischer Container + ein Karten-Testvektor.
- **ID-5 / ID-5a / ID-5b** — Übereinstimmung ist Hash-Gleichheit; Neubau aus
  Eingaben ist der autoritätsfreie Schiedsrichter; lehne das Unreproduzierbare ab.
- **ID-6 / ID-7 / ID-7a–c** — erlaubnisfreier, anfügbarer Merkle-Transparenz-Log
  von `(epoch, H, manifest-hash)`; Equivocation gefangen durch per Gossip
  verbreitete Wurzeln + Konsistenzbeweise; mehrere Logs, kein kanonischer; der Log
  hält Zusagen, nicht die Karte.
- **ID-8 / ID-8a / ID-8b** — Bootstrap ist erklärtes TOFU; der Schaden einer
  schlechten ersten Karte ist begrenzt (der Inhalt bleibt auf der Untergrenze, sie
  ist erkennbar, Reproduktion kann nicht gefälscht werden); erkennen, nicht zu
  verhindern beanspruchen.
- **ID-9 / ID-9a / ID-10** — Auffrischung und Gossip von `(epoch, H)` und Wurzeln
  unter GR-8; Divergenz gezeigt über PS-9; obligatorischer Anomalie-Gossip für die
  drei Angriffs-Signaturen.
- **ID-11 / ID-11a** — Verschmelzungsnaht: derselbe Vertrauens-Anker
  (Reproduzierbarkeit) wie die Release-Governance, aber **getrennte**
  Signierer-/Anfüger-Mengen; geteilte Werkzeuge ja, geteilte Autorität nein.
- **ID-12 / ID-12a** — die Karte liefert eine gemessene, reproduzierbare
  Fehlerschätzung aus, die den `infer_error`-Stellknopf des Simulators und die
  Konfidenz von Teil 3 speist; der Null-Fehler-Fall ist der beste Fall, nie der
  erwartete.

ID-1, ID-5a und ID-8a sind die tragenden drei: keine Autorität, Reproduktion ist
der Schiedsrichter, und eine schlechte Karte kann die Inhalts-Untergrenze nicht
senken. Brich eine von ihnen — finde einen Schritt, der eine vertrauenswürdige
Partei braucht, eine Karte, die aus ihren Eingaben nicht neu gebaut werden kann,
oder einen Weg, auf dem eine schlechte Karte Inhalt und nicht bloß
Verknüpfbarkeit erreicht — und du hast diesen Teil gebrochen. Das ist die
Einladung. Der `infer_error`-Durchlauf von `poc/network_sim.py` ist der
ausführbare Strohmann hinter §11; greif das Modell an, dann diesen Text.
