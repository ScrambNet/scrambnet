# ScrambNet-Spezifikation — Teil 9: Anforderungen an die Referenzimplementierung
> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../../en/spec/09-reference-implementation.md)).

**Status: ENTWURF (DRAFT).** Dieser Teil legt als nummerierte Anforderungen (`RI-n`)
fest, was ein echter Knoten tun MUSS (MUST), was der Proof-of-Concept bewusst
auslässt — jede Regel an die Bedrohung gebunden, die sie beantwortet, und, wo es
zutrifft, an die Invariante (I-1…I-4), die sie schützt. Das Spielzeug in `poc/` ist
eine *ausführbare Spezifikation*, kein Knoten: es sagt das in seinen eigenen ersten
Zeilen ("NOT PRODUCTION CODE. No constant-time arithmetic, no networking, no onion
layer"). Alles hier ist die Distanz zwischen diesem Spielzeug und etwas, das man auf
ein feindliches Netz richten darf. Jede Zahl ist ein Strohmann, der per
Anforderungsnummer anzugreifen ist; die schärfere Einladung steht in §1, und §11
benennt, was noch offen ist.

## 1. Die zentrale Spannung: eine informationstheoretische Untergrenze ist nur so bedingungslos wie der Code, der sie berechnet

ScrambNet verkauft eine **bedingungslose** Inhalts-Untergrenze (I-2, in Teil 7
bewiesen): unterhalb von `k` Anteilen ist der Chiffretext *statistisch unabhängig*
vom Geheimnis, gegen unbeschränkte Berechnung und jeden Quantencomputer. Dieser
Beweis handelt von **Werten** — die Anteil-Bytes, die ein Gegner hält, tragen keine
Information über das Geheimnis. Er sagt nichts darüber, **wie eine echte Maschine
diese Bytes berechnet**, und genau dort kann die Untergrenze verloren gehen, ohne
dass ein einziges Theorem falsch wäre.

Eine GF(2⁸)-Multiplikation per Tabellenzugriff (die `_EXP`/`_LOG`-Tabellen des PoC,
`poc/dispersal.py`) indexiert den Speicher an einer Adresse, die **von einem
geheimen Anteil-Byte abhängt**. Auf echter Hardware macht der Cache-Zustand diesen
Zugriff für einen co-residenten Angreifer zeitlich beobachtbar. Der Tabellenzugriff
leckt daher über einen Timing-Seitenkanal genau die Bytes, die die Untergrenze
verbergen soll. Die Untergrenze wäre dann *in der Theorie bedingungslos und in der
Praxis wiederherstellbar*.

Dies ist der wichtigste Satz dieses Teils, als Prinzip formuliert:

> **Ein Timing- oder Speicheroffenlegungs-Seitenkanal, der geheime Anteil-Bytes,
> Koeffizienten oder den Inhaltsschlüssel preisgibt, ist kein "rechnerischer" Bruch,
> den I-2 haben darf. Er ist ein Bruch von I-2 selbst.** Teil 7 lizenziert genau
> eine rechnerische Annahme — das Ende-zu-Ende-AEAD *oberhalb* von `k` (SP-1a) — und
> nichts sonst. Ein Seitenkanal, der sub-`k`-Geheimbytes offenlegt, kostet den
> Gegner keine "Arbeit unter einer Annahme"; er händigt die Bytes aus. Der Beweis
> von SA-1/SA-2 setzt voraus, dass der Gegner **nur** die `k−1` Anteil-Werte und die
> öffentlichen Parameter sieht. Ein Seitenkanal fügt eine Sicht hinzu, die der
> Beweis nie gewährt hat, und der Beweis deckt sie nicht ab.

Zwei Konsequenzen, die der Rest dieses Teils normativ macht:

- Der **Rechenpfad** der Untergrenze — jede GF(2⁸)-Operation auf
  geheimnisabhängigen Daten in Shamir-`split`, `reconstruct` und
  Lagrange-Interpolation — MUSS (MUST) in konstanter Zeit erfolgen (RI-1). Das ist
  keine Härtung; es ist die Bedingung, unter der SA-1/SA-2 das reale System
  beschreiben, genau wie SA-3 (Koeffizienten-Zufälligkeit) es ist.
- Der **Speicherrückstand** der Untergrenze — Anteile, Koeffizienten, abgeleitete
  Schlüssel — DARF NICHT (MUST NOT) überleben, um aus einem Heap-Dump, einer
  Swap-Datei oder einem Core-Dump gelesen zu werden (RI-9). Eine Untergrenze, die
  auf dem Draht informationstheoretisch, aber aus `/proc` wiederherstellbar ist, ist
  keine Untergrenze.

Der PoC ist ehrlich darüber, dass er an beidem scheitert: er besteht aus reinen
Python-Tabellenzugriffen ohne Nullsetzen, korrekt, aber leck, und er sagt das. Dieser
Teil ist die Liste, die ein echter Knoten stattdessen erfüllen muss. Wo der PoC eine
Regel *bereits* durchsetzt (er weigert sich, Klartext zu streuen, der nicht durch
das AEAD gelaufen ist — `send()` versiegelt, bevor es teilt), ist das die Messlatte,
keine Nettigkeit, und RI-6 hebt sie auf ein MUSS (MUST).

**Geltungsbereich.** Dieser Teil beschränkt die *Implementierung* von
Konstruktionen, die anderswo festgelegt sind; er führt kein neues Draht-Format ein
und ändert kein Byte auf dem Draht (das wäre eine I-1/I-4-Änderung und gehört in die
Teile 1–6). Er DARF NICHT (MUST NOT) so gelesen werden, dass er irgendeine
Anforderung, die er referenziert, lockert; wo es so scheint, gewinnt der
referenzierte Teil, und der Widerspruch ist ein zu meldender Defekt.

## 2. Feldarithmetik in konstanter Zeit (der Rechenpfad der Untergrenze)

- **RI-1 (GF(2⁸) in konstanter Zeit, schützt I-2).** Alle GF(2⁸)-Arithmetik, die auf
  geheimnisabhängige Daten angewandt wird — Shamir-`split` (Polynomauswertung über
  geheime Koeffizienten und den geheimen konstanten Term), `reconstruct`/Lagrange-
  Interpolation (einschließlich der Feld-**Inversion** `gf_inv` im Basis-Nenner) und
  jede Multiplikation, deren Operand ein Anteil-Byte, ein Koeffizient oder ein
  rekonstruiertes Geheimbyte ist — MUSS (MUST) **ohne geheimnisabhängige
  Verzweigungen und ohne geheimnisabhängigen Speicheradresszugriff** berechnet
  werden. Konkret DARF eine Implementierung NICHT (MUST NOT) eine Tabelle
  (`_EXP`/`_LOG`, eine S-Box oder irgendein Array) an einem aus einem geheimen Wert
  abgeleiteten Offset indexieren. Konforme Techniken sind eine bitsliced oder
  tower-field-Multiplikation in konstanter Zeit, eine
  carry-less-multiply-(`CLMUL`)-Reduktion oder ein Feld, das von einer Bibliothek
  bereitgestellt wird, die *dokumentiert*, dass sie sich für diese Operationen in
  konstanter Zeit verhält. Bedrohung: ein co-residenter oder
  Remote-Timing-Gegner stellt geheime Anteil-Bytes aus Cache- oder Branch-Timing
  wieder her — ein **direkter Bruch von I-2** (siehe §1), kein rechnerischer. Das
  gilt symmetrisch für **split und reconstruct**: ein Endpunkt, der rekonstruiert,
  leckt das Geheimnis, das er gerade wiederhergestellt hat, genauso wie ein Teiler
  das leckt, das er streut.
- **RI-1a (Inversion und Division sind nicht ausgenommen).** Der Lagrange-Nenner-
  Inverse (`gf_inv` in `poc/dispersal.py`, dort berechnet als `_EXP[255 − _LOG[a]]`)
  operiert auf einem aus dem geheimen Anteil-Satz abgeleiteten Wert und MUSS (MUST)
  in konstanter Zeit erfolgen; eine datenabhängige Exponentiation oder ein
  Tabellen-Lookup-Inverse ist nicht konform. Eine Implementierung SOLLTE (SHOULD)
  eine inversionsfreie Interpolation bevorzugen (z. B. die Nenner bündeln und einmal
  via Fermat `a^{254}` durch eine feste Additionskette oder Montgomerys Trick
  invertieren), sodass keine geheimnisabhängige Division verbleibt. Die
  Auswertungspunkte `x_1…x_n` sind **öffentlich** (Teil 7 §2), sodass Arithmetik auf
  *ihnen allein* nicht in konstanter Zeit erfolgen muss; in dem Moment, in dem ein
  öffentlicher Punkt in ein Geheimnis multipliziert wird, ist das Produkt geheim.
- **RI-1b (Vektoren zertifizieren kein Timing).** Das Bestehen der
  roadmap-3.2-GF-Testvektoren beweist, dass eine Multiplikation *korrekt* ist, nicht,
  dass sie *in konstanter Zeit* erfolgt: die lecken Tabellen des PoC bestehen
  dieselben Vektoren. Eine Implementierung DARF NICHT (MUST NOT) Vektorkonformität
  als Beleg für RI-1-Konformität behandeln. Verhalten in konstanter Zeit SOLLTE
  (SHOULD) durch ein Timing-Analyse- oder statistisches Werkzeug geprüft werden (z. B.
  dudect-artige Leckage-Tests) und, wo die Plattform es erlaubt, durch Deaktivieren
  von Compiler-Transformationen, die geheimnisabhängige Verzweigungen
  wiedereinführen (RI-9b).
- **RI-1c (die ganze Lebensdauer des Geheimnisses ist in konstanter Zeit, nicht nur
  seine Feldoperationen, schützt I-2).** Die Disziplin der konstanten Zeit ist durch
  **Datenfluss definiert, nicht durch das Benennen der GF-Operationen**: jeder Wert,
  der von einem Anteil-Byte, einem Koeffizienten oder einem rekonstruierten
  Geheimbyte kontaminiert ist, erbt die RI-1-Verpflichtung, bis er auf null gesetzt
  ist (RI-9), und diese Verpflichtung reicht *über* die Feldschicht hinaus.
  Insbesondere MUSS (MUST) das Längenpräfix des rekonstruierten Geheimnisses (SP-8)
  geparst und der wiederhergestellte Klartext kopiert, geschnitten und validiert
  werden, **ohne eine geheimnisabhängige Verzweigung und ohne einen von der geheimen
  Länge abhängigen Speicherzugriff**; `unpad` DARF NICHT (MUST NOT) auf der
  dekodierten Länge in einer Weise verzweigen, die ein Beobachter messen kann, und
  kein Vergleich, keine Bereichsprüfung und keine Pufferbewegung auf einem Geheimnis
  darf datenabhängig sein. Bedrohung: §1s eigenes Prinzip — "ein Endpunkt, der
  rekonstruiert, leckt das Geheimnis, das er gerade wiederhergestellt hat, genauso
  wie ein Teiler das leckt, das er streut" — wird nur durchgesetzt, wenn die
  *gesamte* Behandlung des wiederhergestellten Geheimnisses in konstanter Zeit
  erfolgt, nicht bloß seine GF-Arithmetik. Ein Knoten, der ein verifiziertes Feld in
  konstanter Zeit (RI-1) und ein geprüftes AEAD in konstanter Zeit (RI-8) nutzt, dann
  aber auf einer wiederhergestellten Länge verzweigt, erfüllt jedes andere MUSS
  (MUST), während er die Struktur des wiederhergestellten Geheimnisses über Timing
  leckt, was nach demselben Argument wie RI-1 ein direkter I-2-Bruch ist.

## 3. CSPRNG-Disziplin (die Untergrenze ist genau so stark wie ihre Zufälligkeit)

Die Untergrenze ist nicht stärker als die Zufälligkeit der Shamir-Koeffizienten:
Teil 7 SA-3 ist die "Komponente mit der höchsten Sicherheitsgewähr" der ganzen
Spezifikation, und `test_properties.test_coefficient_reuse_breaks_the_floor` zeigt,
dass Wiederverwendung das Geheimnis mit Gewissheit leckt. Dieselbe Disziplin
regiert jedes andere Geheimnis, das der Knoten zieht.

- **RI-2 (kryptographischer DRBG vom OS, schützt I-2 via SA-3).** Alle geheime
  Zufälligkeit — Shamir-Koeffizienten (SA-3), der ephemere Circuit-Wert pro Paket
  `x` aus CH-3, `msg_nonce`/Nachrichtenzähler, wo nicht deterministisch,
  `kpair`-Erzeugung und jedes `box_id`-Salt — MUSS (MUST) von einem kryptographisch
  sicheren DRBG erzeugt werden, der vom Betriebssystem-CSPRNG geseedet ist
  (`getrandom`/`getentropy`, `/dev/urandom` nachdem der Pool initialisiert ist, oder
  eine äquivalente bis-zum-Seed-blockierende Quelle). Eine Implementierung DARF NICHT
  (MUST NOT) einen nicht-kryptographischen PRNG (einen LCG, Mersenne Twister,
  `rand()`, einen Hash-eines-Zählers oder einen als "zufällig" wiederverwendeten
  Strom) für irgendeinen Wert in dieser Liste nutzen.
- **RI-2a (Fork- und Clone-Sicherheit — die klassische Katastrophe).** Ein Prozess,
  der `fork()`t, aus einem Checkpoint wiederhergestellt, migriert oder als VM- oder
  Container-Image geklont wird, DARF NICHT (MUST NOT) DRBG-Zustand wiederverwenden,
  der vor der Teilung Ausgabe produziert hat. Die Implementierung MUSS (MUST) bei
  Fork/Wiederherstellung vom OS neu seeden (z. B. eine
  `pthread_atfork`/`MADV_WIPEONFORK`-Disziplin oder ein OS-Zug pro Aufruf), sodass
  niemals zwei Prozesse denselben Koeffizientenstrom oder denselben ephemeren `x`
  ausgeben. Bedrohung: zwei identische VM-Klone teilen *verschiedene* Nachrichten
  unter **denselben Koeffizienten**, und nach SA-3 wird das Paar der Anteil-Sätze
  mit beiden Geheimnissen korreliert — die Lehrbuch-Zufälligkeitskatastrophe und
  ein direkter I-2-Bruch. Dies wird eigens herausgestellt, weil es für jeden
  Einzelprozess-Test unsichtbar ist.
- **RI-2b (Gesundheits- und Startprüfungen).** Bevor er den ersten Geheimwert
  ausgibt, MUSS (MUST) ein Knoten bestätigen, dass die OS-Entropiequelle geseedet ist
  (er DARF NICHT (MUST NOT) auf eine Quelle niedriger Entropie zurückfallen, wenn der
  Pool nicht bereit ist) und SOLLTE (SHOULD) einen Start-Selbsttest am DRBG
  durchführen. Ein Knoten SOLLTE (SHOULD) einen fortlaufenden
  Wiederholungs-/Stuck-Output-Test an der Rohentropie durchführen, wo er Zugriff
  darauf hat, und MUSS (MUST) fail-closed sein — sich weigern, zu teilen oder ein
  Paket zu bauen —, statt mit einem verdächtigen Generator fortzufahren. Ein
  Generator, der nicht verifiziert werden kann, wird als defekt behandelt.
- **RI-2c (keine injizierbaren Koeffizienten in Produktion — aber
  Konformitätsvektoren laufen weiterhin).** Der Parameter `split(..., coeffs=...)` des
  PoC existiert nur, damit Vektoren deterministisch sein und der Wiederverwendungs-
  Bruch vorgeführt werden kann. Ein Produktionsartefakt DARF NICHT (MUST NOT)
  irgendeinen Pfad — Flag, Config, Umgebungsvariable oder Symbol — freilegen, der es
  einem Aufrufer erlaubt, Shamir-Koeffizienten oder den ephemeren `x` zu liefern, zu
  protokollieren oder festzupinnen; ein solcher Pfad ist ein SA-3-Foot-Gun. Die
  Aussöhnung mit den roadmap-3.2-Konformitätsvektoren (RI-10), die deterministisch
  injizierte Koeffizienten zur Reproduktion verlangen, ist ein
  **Build-Zeit-Test-Gate**: der Injektionspfad DARF (MAY) *nur* hinter einem Gate
  existieren, das **in keinem Produktionsartefakt vorhanden** und zur Laufzeit in der
  Produktion unerreichbar ist. Vektoren werden gegen einen Test-Build abgeglichen,
  der das Gate aktiviert; der Produktions-Build MUSS (MUST) mit ihm identisch sein,
  abgesehen von der Abwesenheit des gegateten Codes, und diese Äquivalenz SOLLTE
  (SHOULD) vom Build verifiziert werden (z. B. ein reproduzierbarer Diff der beiden).
  "Einkompiliert heraus, nicht bloß abgeraten" bedeutet genau dies: vorhanden für das
  Test-Binary, physisch abwesend im ausgelieferten — niemals ein Laufzeitschalter.

## 4. Nonce- und Schlüsselrotations-Zustand über Neustarts hinweg

Zwei verschiedene Geheimnisse dürfen über einen Neustart hinweg niemals
wiederverwendet werden: die AEAD/Tag-Nonce (SP-7b) und die statische `onion`-Epoche
des Relais (CH-5). Ein Neustart ist der Moment, in dem ein Knoten am meisten
versucht ist, "frisch anzufangen" und einen bereits verwendeten Wert
wiederzuverwenden.

- **RI-3 (monotone Nonce-High-Water-Mark überlebt Neustarts, schützt SP-7b und
  SP-1a).** Pro `kpair` MUSS (MUST) die `msg_nonce` des Absenders (ein streng
  steigender Nachrichtenzähler, SP-7b) persistiert werden und DARF NICHT (MUST NOT)
  über einen Neustart, Absturz oder Uhrwechsel zurückrollen. Die Implementierung MUSS
  (MUST) die High-Water-Mark `fsync`en (oder die plattformäquivalente dauerhafte
  Barriere) **in stabilen Speicher, bevor die von ihr abgedeckte Nonce auf dem Draht
  verwendet wird**, sodass ein Absturz zwischen Verwendung und Persistierung nur
  Nonces *überspringen*, sie niemals wiederholen kann. Ein Knoten DARF NICHT (MUST
  NOT) eine `msg_nonce` unter einem `kpair` wiederverwenden oder verringern.
  Bedrohung: eine wiederverwendete `msg_nonce` ist **doppelt fatal** (SP-7b) — sie
  kollidiert SP-7-Tags (wodurch ein Anteil-Satz über kolludierende Drops hinweg
  verknüpfbar wird) **und** zerstört, weil `msg_nonce` die
  ChaCha20-Poly1305-Nonce ist (SP-1a), die AEAD-Vertraulichkeit als Two-Time-Pad.
  Den Zähler nach einem wiederhergestellten Backup zurückzurollen ist das
  realistische Versagen, und es ist ein Bruch der Vertraulichkeit, kein Glitch.
- **RI-3a (Vorausreservierung zur Begrenzung der fsync-Kosten).** Eine
  Implementierung DARF (MAY) die High-Water-Mark in Blöcken persistieren (`B` Nonces
  mit einem dauerhaften Schreibvorgang reservieren, sie aus dem Speicher ausgeben,
  erneut persistieren, bevor der Block erschöpft ist), um ein fsync pro Nachricht zu
  vermeiden. Ein Absturz verschwendet dann höchstens das ungenutzte Ende eines
  Blocks — akzeptabel, weil der Zählerraum groß ist und Überspringen sicher ist,
  während Wiederholen fatal ist. Sie DARF NICHT (MUST NOT) unter irgendeinem
  Crash-Recovery-Pfad eine Nonce auf oder unter der zuletzt dauerhaft persistierten
  Marke ausgeben.
- **RI-3b (eine Wiederherstellung ist kein Neustart — Rollback erkennen oder den
  Schlüssel ausmustern, schützt SP-7b/SP-1a).** RI-3/RI-3a verteidigen gegen einen
  *Absturz* (die persistierte Marke bewegt sich nur vorwärts); sie verteidigen
  **nicht** gegen einen VM-Snapshot, Dateisystem-Snapshot oder eine
  Backup-**Wiederherstellung**, die die persistierte Marke selbst zurückspult —
  genau das "Zurückrollen des Zählers nach einem wiederhergestellten Backup", das
  RI-3 als das realistische Versagen benennt. Ein Knoten DARF NICHT (MUST NOT)
  annehmen, dass sein persistierter Nonce-Speicher über eine solche Wiederherstellung
  hinweg monoton ist. Er MUSS (MUST) daher entweder (a) die High-Water-Mark an ein
  pro-Boot/pro-Wiederherstellung gültiges Nonce-**Salt** (oder einen monotonen
  Generationszähler) binden, das im *selben dauerhaften Schreibvorgang* wie die
  Reservierung persistiert wird, sodass ein zurückgespulter Speicher erkennbar ist,
  und bei Erkennung **das `kpair` ausmustern** — einen frischen Inhalts-/Tag-Schlüssel
  ableiten, ein wiederverwendetes Salt unter einem zurückgespulten Zähler als
  Kompromittierung behandeln — oder (b) sich weigern, unter dem betroffenen `kpair`
  auszugeben, bei jedem Anzeichen einer Wiederherstellung (die Systemuhr bewegt sich
  rückwärts oder der persistierte Generationszähler sinkt), bis ein frisches `kpair`
  außerbandig ausgehandelt ist (Teil 6). Die Vorausreservierung (RI-3a) MUSS (MUST)
  den Generationszähler im dauerhaften Schreibvorgang der Reservierung mitführen,
  sodass eine Wiederherstellung nicht einen ganzen reservierten Block unentdeckt
  wiederholen kann. Bedrohung: ohne dies gibt eine Snapshot-Wiederherstellung einen
  ganzen Block bereits verwendeter `msg_nonce`-Werte erneut aus — das doppelt fatale
  Two-Time-Pad aus RI-3, auf einem Pfad, den der nur-Absturz-Schutz von RI-3a nicht
  sehen kann.
- **RI-4 (Zustand der statischen onion-Epoche und sichere Ausmusterung, schützt
  CH-5/CH-6).** Ein Relais MUSS (MUST) persistieren, in welcher statischen
  `onion`-Epoche es sich befindet (der aktive Privatschlüssel, seine
  `created`/`expiry` und das in-Flight-Nachlauffenster), sodass ein Neustart nicht
  still einen abgelaufenen Schlüssel neu veröffentlicht, einen ausgemusterten
  wiederbelebt oder eine zweite "frische" Statik innerhalb derselben deklarierten
  Epoche prägt. Bei Rotation (≤7-day, CH-5) MUSS (MUST) das Relais, sobald die
  in-Flight-Nachlauffrist verstrichen ist, **die private Hälfte der ausgemusterten
  Statik nullen** (RI-9) und DARF sie NICHT (MUST NOT) behalten; ein Relais, das alte
  Statika behält, vergrößert sein eigenes CH-6-Verknüpfungs-Expositionsfenster und
  ist nicht konform. Clients bleiben durch GR-4/CH-5 gebunden, jeden Datensatz
  abzulehnen, dessen `expiry` `created + 7 days` übersteigt (GR-2 Schlüssel 6), sodass
  ein Knoten, der seine Epoche vergisst, das Fenster nicht durch Neuveröffentlichung
  verlängern kann. Bedrohung: ein Neustart, der die Statik in ein Fenster zurückrollt,
  das der Client bereits gesehen hat, oder der eine ausgemusterte Statik nicht
  vernichtet, öffnet erneut genau die CH-5a-Verknüpfungsexposition, die die
  Rotations-Obergrenze zu begrenzen existiert.

## 5. Persistenz des Replay-Caches

ScrambNet weist Replays auf zwei Schichten zurück, und beide sind zustandsbehaftet:
die Circuit-Schicht verwirft ein gesehenes `gamma` pro Schlüsselepoche (SP-5), und
die Speicherschicht verwirft eine erneute Hinterlegung eines bereits gespeicherten
`(box_id, slot)` (SP-7b, RZ-7). Ein Neustart, der diesen Zustand vergisst, öffnet
erneut ein Replay-Fenster.

- **RI-5 (Replay-Zustand überlebt Neustarts, auf die Epoche begrenzt, schützt SP-5 /
  SP-7b).** Ein Relais MUSS (MUST) seinen Sphinx-Replay-Cache gesehener
  `gamma`-Werte **für die aktuelle Schlüsselepoche** persistieren oder sicher und
  vollständig wiederaufbauen, und ein Drop MUSS (MUST) seine Menge gespeicherter
  `(box_id, slot)`-Hinterlegungen persistieren, sodass ein Neustart oder Absturz
  nicht ein Paket oder eine Hinterlegung akzeptiert, die er innerhalb der laufenden
  Epoche bereits gesehen hat. Bedrohung: ein Relais, das mit leerem Replay-Cache
  neustartet, wird jedes Paket, das ein Gegner innerhalb der Epoche aufgezeichnet und
  erneut einschleust, wieder zulassen — ein erneut geöffnetes Replay-Fenster, das
  auf der Drop-Schicht auch ehrliche Post gegen die RZ-7-Je-Box-Obergrenze
  vervielfachen oder verdrängen kann.
- **RI-5a (der Cache ist begrenzt — durch zwei *verschiedene* Aufbewahrungsfenster,
  nicht "die Epoche").** Die beiden Replay-Caches sind jeweils im Speicher begrenzt,
  aber durch **unterschiedliche** Fenster, die eine Implementierung NICHT (MUST NOT)
  vermengen darf:
    - der Sphinx-`gamma`-Cache ist durch die **statische onion-Schlüsselepoche**
      begrenzt (CH-5, ≤7-day) — ein `gamma` ist nur replaybar, solange der Schlüssel,
      der es verschlüsselte, live ist;
    - die `(box_id, slot)`-Deposit-Dedup-Menge ist durch den **Slot-Ablauf** begrenzt
      (RZ-7, 7 days), **nicht** durch die 1-tägige `box_id`-Rotation (RZ-10). Die Box-ID
      rotiert täglich zur *Adressierung*, aber ein hinterlegter Slot wird bis zu 7
      Tage *gespeichert* (plus die RZ-14-Grenz-Nachlauffrist), sodass eine erneute
      Hinterlegung so lange verwerfbar ist, wie der Slot, mit dem sie kollidieren
      würde, noch gespeichert werden kann — bis zu ~7 Box-Epochen. Diese Menge auf
      einen Tag zu dimensionieren, unterdimensioniert sie um ~7×.
  Eine Implementierung MUSS (MUST) den Zustand jedes Caches verwerfen, sobald sein
  eigenes Fenster verstrichen ist (den `gamma`-Cache am Ende der Schlüsselepoche, die
  Deposit-Menge beim Slot-Ablauf), was den Speicher auf grob das Paketvolumen der
  Schlüsselepoche bzw. das 7-Tage-Deposit-Volumen begrenzt. Sie DARF (MAY) den
  Speicher mit einer zählenden Struktur weiter begrenzen (z. B. ein dimensionierter
  Bloom-/Cuckoo-Filter) **nur wenn** sie so abgestimmt ist, dass False Positives
  unter einer betrieblich vernachlässigbaren Rate bleiben; ein False Positive
  verwirft ein ehrliches Paket (ein selbstverschuldeter DoS), ein False Negative
  lässt ein Replay zu (ein Sicherheitsversagen), also MUSS (MUST) die Struktur so
  dimensioniert sein, dass sie Letzteres innerhalb ihres Aufbewahrungsfensters
  unmöglich und Ersteres selten macht. Ein Knoten, der einen Cache nicht
  persistieren kann, MUSS (MUST) fail-closed sein für ein Fenster, das er nicht
  abdecken kann (die vergessene Spanne als replaybar behandeln und, für den
  `gamma`-Cache, die Schlüsselepoche rotieren), statt Replays still zu akzeptieren.
- **RI-5b (Wiederaufbau muss vollständig sein oder als Rotation behandelt werden —
  und eine Wiederherstellung ist kein Wiederaufbau).** Eine Implementierung, die den
  Replay-Zustand nach einem Absturz wiederaufbaut (statt ihn kontinuierlich zu
  persistieren), MUSS (MUST) ihn entweder vollständig für das laufende Fenster
  rekonstruieren oder die Lücke als Beginn einer neuen Schlüsselepoche behandeln
  (neue Schlüssel, sodass alte `gamma`-Werte nicht mehr akzeptabel sind). Ein
  partieller Wiederaufbau, der einen Teil des Fensters ungeschützt lässt, ist nicht
  konform. Ferner ist eine VM-/Dateisystem-**Wiederherstellung**, die den Cache auf
  einen *früheren, vollständig aussehenden* Zustand zurückspult, kein Absturz, und
  die Vollständigkeitsprüfung von RI-5b kann sie nicht erkennen: ein
  wiederhergestelltes Relais kommt mit einem Cache von *vor* den Paketen zurück, die
  ein Gegner aufgezeichnet hat, und lässt sie wieder zu. Ein Knoten MUSS (MUST) jedes
  Anzeichen einer Wiederherstellung (dasselbe Uhr-Zurückspulen oder Sinken des
  Generationszählers wie bei RI-3b) als eine verpflichtende **Schlüsselepochen-Rotation**
  behandeln, sodass die `gamma`-Werte von vor der Wiederherstellung nicht mehr
  akzeptabel sind, unabhängig davon, was der zurückgespulte Cache enthält.

## 6. Missbrauchsresistente API (das Unsichere unmöglich machen)

I-1 und die `[soundness]`-Disziplin verlangen, dass die API die unsichere Operation
*nicht darstellbar* macht, nicht bloß als unklug dokumentiert. Die Reihenfolge von
SP-1 (verschlüsseln **dann** teilen) und die Fail-Closed-Regel von SP-7a sind die
beiden Stellen, an denen eine API am leichtesten invertiert.

- **RI-6 (die API MUSS Klartext-ohne-AEAD verweigern, schützt SP-1/SP-1a).** Der
  Streuungs-Einstiegspunkt MUSS (MUST) jede Eingabe verweigern, die nicht bereits das
  Ende-zu-Ende-AEAD (SP-1a) durchlaufen hat: er streut **nur Chiffretext**, niemals
  Klartext. Es DARF NICHT (MUST NOT) einen öffentlichen "teile diese Rohbytes"-Pfad
  geben, der die encrypt-then-split-Reihenfolge von SP-1 umgeht — d. h. keinen Weg,
  `split()` ohne das AEAD-Siegel davor zu erreichen. Der PoC erfüllt diese Messlatte
  bereits: `send()` ruft `e2e.seal` vor `disperse` auf, und `dispersal.py` ist
  dokumentiert, "never touch plaintext". Ein echter Knoten MUSS (MUST) diese Tür auf
  Typ-Ebene geschlossen halten, nicht per Konvention. Bedrohung: Klartext direkt zu
  teilen zerstört den *rechnerischen Gürtel* (Stufe 2 von Teil 7) — die Anteile
  rekonstruieren dann direkt zu Klartext für jeden `≥k`-Gegner, ohne AEAD dahinter —
  und invertiert die Komposition, auf der der ganze Entwurf ruht.
- **RI-6a (Chiffretext typ-getrennt von Klartext).** Eine Implementierung SOLLTE
  (SHOULD) "Klartext" und "Ende-zu-Ende-Chiffretext" als verschiedene, nicht
  austauschbare Typen darstellen, sodass die SP-1-Reihenfolge nicht durch Übergeben
  des falschen Puffers invertiert werden kann und ein "teile Rohbytes"-Aufruf ein
  Kompilierzeitfehler statt einer Laufzeitprüfung ist. Wo die Sprache dies nicht
  erzwingen kann, MUSS (MUST) der Knoten einen Laufzeit-Schutz dazwischenschalten,
  der standardmäßig an ist und nicht durch Konfiguration deaktiviert werden kann.
- **RI-6b (rohe Feld-Einstiegspunkte MÜSSEN modul-privat sein).** Typtrennung (RI-6a)
  reicht allein nicht aus: das rohe `split`/`reconstruct` und jeder direkte
  Feld-Einstiegspunkt MÜSSEN (MUST) modul-privat sein (nicht exportiert), sodass die
  *einzigen* öffentlichen Streuungs-Symbole dasjenige sind, das den
  AEAD-Chiffretext-Typ nimmt (RI-6), und dasjenige, das ein authentifiziert-geöffnetes
  Ergebnis zurückgibt (RI-7). Ein öffentliches Symbol `split(raw_bytes)` oder
  `reconstruct(...)` ist selbst der Defekt, unabhängig davon, was ein Aufrufer ihm
  übergibt — in einer Sprache, in der `bytes` gleich `bytes` ist, lässt ein
  exportiertes Roh-Split einen tieferliegenden Aufrufer das AEAD-Gate umgehen, während
  die Typprüfung sauber durchläuft. Der PoC legt diese auf Modulebene frei, *weil er
  eine ausführbare Spezifikation ist*; ein echter Knoten DARF dies NICHT (MUST NOT).
- **RI-7 (Rekonstruktion MUSS fail-closed sein, in konstanter Zeit, schützt SP-7a).**
  Das AEAD-Tag ist der **alleinige** Integritätsschiedsrichter (SP-7a): die
  Shamir-Rekonstruktion hat keine eigene, sodass ein gekipptes Anteil-Byte oder ein
  belogenes `(k,n)` einen konsistenten-aber-falschen Kandidaten liefert, den nur das
  AEAD zurückweist. Die Rekonstruktions-API MUSS (MUST) eine Nachricht **nur**
  zurückgeben, nachdem das Ende-zu-Ende-AEAD verifiziert hat, und MUSS (MUST) jeden
  Kandidaten, dessen Tag scheitert, verwerfen — niemals an die Oberfläche bringen,
  protokollieren oder darauf reagieren. Sie DARF NICHT (MUST NOT) ein "unauthentifiziert
  rekonstruiertes" Ergebnis an Anwendungscode freilegen. **Das fail-closed-Verwerfen
  MUSS (MUST) auch in konstanter Zeit bezüglich des *Warum* des Scheiterns erfolgen:**
  der reconstruct-then-open-Pfad MUSS (MUST) ununterscheidbare Zeit brauchen und keine
  unterscheidbare Antwort ausgeben (CH-9/I-4), ob das AEAD-Tag verifiziert hat, ob
  über das `(k,n)`-Byte gelogen wurde (RI-7a) oder ob die Anteil-Bytes beschädigt
  waren — ein Gegner, der Rekonstruktions-Kandidaten einspeisen kann (das
  SP-7a-feindliche-Drop-Restrisiko oder eine `≥k`-Koalition, die Anteil-Sätze
  wiederholt), DARF NICHT (MUST NOT) durch Timing oder durch Antwort erfahren,
  welches, sonst wird der Ablehnungspfad zu einem Padding-Oracle-artigen
  Unterscheider, obwohl der Tag-*Vergleich* (RI-8) in konstanter Zeit erfolgt. Der PoC
  pinnt das fail-closed-Verhalten fest (`receive()` verwirft beim `ValueError` aus
  `e2e.open_`, `test_tampered_share_fails_closed`); ein echter Knoten DARF (MUST NOT)
  keinen Pfad um es herum hinzufügen, noch eine Timing-Seitentür durch es hindurch.
  Bedrohung: eine unauthentifizierte Rekonstruktion hochzureichen verwandelt das
  akzeptierte SP-7a-Dienstverweigerungs-Restrisiko in die Auslieferung von
  angreifergewähltem Müll; die Ablehnung zu messen verwandelt es in ein Orakel.
- **RI-7a (das `params`-Byte defensiv parsen, ihm nicht trauen).** Das `(k,n)`-Byte
  ist auf einem feindlichen Anteil angreiferkontrolliert (SP-7a) und
  nibble-reihenfolge-verriegelt durch Vektoren (SP-7a / roadmap 3.2). Eine
  Implementierung MUSS (MUST) es gegen die vektorverriegelte Reihenfolge und gegen
  `1 ≤ k ≤ n ≤ 15` validieren (wie `_check_params` es tut), bevor sie es nutzt, und
  MUSS (MUST) eine Rekonstruktion unter einem belogenen `(k,n)` als gewöhnlichen
  fail-closed-Drop (RI-7) behandeln, niemals als Grund, unbegrenzt Speicher zu
  allozieren oder außerhalb der Grenzen zu indizieren.

## 7. Das AEAD und der Tag-Vergleich (der Gürtel muss ebenfalls in konstanter Zeit sein)

Der rechnerische Gürtel (Stufe 2, Teil 7 §5) ist nur so solide wie seine
Implementierung. Das AEAD des PoC ist korrekt gegen RFC 8439, aber ausdrücklich
**nicht** in konstanter Zeit ("it is correct … but leaks through timing, so a real
node MUST use a vetted constant-time library").

- **RI-8 (AEAD und Tag-Vergleich in konstanter Zeit, schützt SP-1a / SP-7).** Ein
  Knoten MUSS (MUST) eine ChaCha20-Poly1305-Implementierung nutzen, deren Datenpfad
  und deren **Authentifizierungs-Tag-Vergleich** in konstanter Zeit erfolgen, und
  MUSS (MUST) das SP-7-Anteil-Tag und das SP-7a-AEAD-Tag mit einem
  Gleichheitsprimitiv in konstanter Zeit vergleichen (kein `memcmp` mit frühem
  Ausstieg, keine datenabhängige Verzweigung auf Tag-Bytes). Bedrohung: eine
  Tag-Prüfung, die nicht in konstanter Zeit erfolgt, ist ein klassisches
  Fälschungs-Orakel — byteweises Timing am Vergleich lässt einen Gegner ein gültiges
  Tag fälschen —, das den Gürtel (SP-1a) und das Anteil-Erkennungs-Tag (SP-7) direkt
  angreift. Die Poly1305- und X25519-Arithmetik MUSS (MUST) ebenfalls in konstanter
  Zeit erfolgen (RI-11); eine Implementierung von beidem in variabler Zeit leckt
  Schlüsselmaterial über Timing.

## 8. Die Zwiebel-Schicht, die das Spielzeug auslässt

Der PoC hat "no onion layer": `dispersal.py` operiert nur auf dem Anteil der
`delta`-Nutzlast, und der Sphinx-Header (`alpha`/`beta`/`gamma`) und seine
Kryptographie je Hop existieren nur als die Spezifikation aus Teil 1 §5. Ein echter
Knoten MUSS (MUST) diese Schicht implementieren, und ihre Kryptographie ist hier im
Geltungsbereich, weil sie geheimes Material trägt (die Hop-Geheimnisse und den
Client-Ephemer) unter derselben Seitenkanal-Bedrohung wie die Untergrenze.

- **RI-10 (die CH-2-Ableitung je Hop implementieren, schützt I-1/I-4).** Ein Knoten
  MUSS (MUST) den Sphinx-Circuit-Handshake aus Teil 1 §5 exakt implementieren: je Hop
  das gemeinsame Geheimnis `s_i = X25519(alpha_i, onion_i)` aus dem geblindeten
  Gruppenelement und der Relais-Statik (CH-2) ableiten und den Stromschlüssel der
  Routing-Info, den `gamma`-MAC-Schlüssel und den `delta`-AEAD-Schlüssel aus `s_i`
  per HKDF-BLAKE2s unter den festen Labels `sphinx-rho`, `sphinx-mu`, `sphinx-delta`
  ableiten (CH-2; exakte Label-Bytes und Verkettung vektorverriegelt unter roadmap
  3.2). Er MUSS (MUST) das Sphinx-Blinding durchführen (`alpha` je Hop
  re-randomisieren) und die Replay-Disziplin von SP-5 durchsetzen. Es gibt **kein
  separates Handshake-Transkript** (CH-1); ein Knoten, der irgendeine
  Noise-/Handshake-Nachricht auf einem Circuit aussendet oder erwartet, ist nicht
  konform (CH-1). *Flag:* die implementierungsübergreifenden Testvektoren für diese
  Ableitung sind roadmap 3.2 und MÜSSEN (MUST) abgeglichen werden, sobald
  veröffentlicht; bis dahin ist nicht bewiesen, dass zwei Implementierungen auf
  dieser Schicht interoperieren (I-1), und dies wird offen dargelegt, nicht
  angenommen.
- **RI-11 (X25519 in konstanter Zeit und die schlüssellos-ephemere Disziplin,
  schützt CH-3/CH-6/I-2).** Die X25519-Skalarmultiplikation an jedem Hop MUSS (MUST)
  in konstanter Zeit erfolgen (eine Montgomery-Ladder-Implementierung ohne
  geheimnisabhängige Verzweigung oder Speicherzugriff); ein X25519 in variabler Zeit
  leckt den Hop-Skalar und somit das Hop-Geheimnis. Der ephemere Client-Skalar pro
  Paket `x` hinter `alpha_0` (CH-3) MUSS (MUST) je Paket frisch aus dem CSPRNG
  (RI-2) gezogen werden, DARF niemals (MUST NOT) über Pakete hinweg wiederverwendet
  werden und MUSS (MUST) unmittelbar nach dem Bau des Pakets auf null gesetzt werden
  (RI-9) — seine Vernichtung ist das, was die epochen-granulare Forward Secrecy von
  CH-6 real macht (ein behaltenes `x` lässt eine spätere Ergreifung der Relais-Statik
  das Hop-Geheimnis neu berechnen, das der Entwurf als verschwunden verspricht). Ein
  Relais MUSS (MUST) seine `onion`-Statik ebenfalls unter der Schlüsselbehandlung von
  RI-2 und der Rotation/Ausmusterung von RI-4 halten und in konstanter Zeit mit ihr
  rechnen.
- **RI-11a (das entartete gemeinsame Geheimnis ablehnen, auf die X25519-korrekte
  Weise).** X25519 legt absichtlich keinen billigen On-Curve-/Order-Test offen
  (RFC 7748), sodass "validiere den `alpha`-Punkt" nicht die baubare Prüfung ist; die
  erforderliche, baubare ist: `s_i = X25519(alpha_i, onion_i)` berechnen und, **in
  konstanter Zeit ablehnen, falls das resultierende gemeinsame Geheimnis komplett
  null ist** (das Low-Order-/Small-Subgroup-Ergebnis), *bevor* irgendein Hop-Schlüssel
  daraus abgeleitet wird. Dies verwehrt einem bösartigen Vorgänger einen erzwungenen
  Small-Order- oder Known-Key-Hop. Weil jedes Byte auf dem Draht uniform ist (SP-4/I-4),
  ist die Prüfung auf dem *berechneten Geheimnis*, nicht auf einem Klartext-Flag, und
  ein Relais MUSS (MUST) ein abgelehntes `alpha` in Zeit und Bytes
  **ununterscheidbar von einem gewöhnlichen Replay-Drop** verarbeiten
  (SP-5/CH-9/I-4) — keine unterscheidbare Antwort, kein Timing-Tell. Die vollständige
  Punkt-Validierungs-/Kodierungsregel ist vektorverriegelt unter roadmap 3.2, aber
  die All-Zero-Output-Ablehnung ist *hier* normativ, sodass die Anforderung baubar
  ist, ohne auf diese Datei zu warten (I-1).

## 9. Speicher-Nullsetzen, Swap und Fehlersicherheit

Eine Untergrenze, die auf dem Draht bedingungslos, aber aus einem Heap-Dump, einer
Swap-Datei oder einem Core-Dump wiederherstellbar ist, ist keine Untergrenze (§1).
Speicheroffenlegung enthüllt genau die Bytes unterhalb von `k`, die I-2 schützt,
sodass Nullsetzen eine I-2-Anforderung ist, keine Hygiene.

- **RI-9 (Geheimnisse in nullsetzbarem Speicher halten und nach Gebrauch löschen,
  schützt I-2).** Shamir-Anteile, Polynom-Koeffizienten, das rekonstruierte
  Geheimnis, jeder abgeleitete Schlüssel (`content_key`, der SP-7-`tag`-Schlüssel,
  der `box_id`-Schlüssel, jeder Sphinx-Hop-Schlüssel `s_i` und seine Ableitungen),
  das vorab geteilte `kpair`, der Client-Ephemer `x` (RI-11) und die `onion`-Statik
  des Relais (RI-4) MÜSSEN (MUST) in Speicher gehalten werden, den der Knoten
  an Ort und Stelle überschreiben kann, und MÜSSEN (MUST) auf null gesetzt werden,
  sobald sie nicht mehr gebraucht werden. Die Verpflichtung ist als *Speicherwahl
  zuerst* formuliert, weil ein bloßes "zeroize" in einigen der eigenen Zielsprachen
  dieser Spezifikation **physisch unmöglich** ist: in CPython (der Sprache des
  Referenz-PoC) kann ein Geheimnis in einem unveränderlichen `bytes`-Objekt interniert,
  vom Allokator kopiert und ohne jedes erreichbare Überschreiben freigegeben werden,
  und ein kopierender/kompaktierender GC (Go, Java, …) kann ein Geheimnis verschieben,
  sodass kein einzelnes Löschen jede Kopie erreicht. Daher:
    - In einer Laufzeit, die **deterministischen, an Ort und Stelle veränderlichen**
      Geheimspeicher bietet, MUSS (MUST) der Knoten mit einem Primitiv auf null
      setzen, das der Compiler nicht als Dead Store eliminieren kann
      (`explicit_bzero`/`memset_s`/`SecureZeroMemory`/eine `volatile`-Barriere oder
      das geprüfte `Zeroize` der Sprache) — ein schlichtes `memset` auf einem
      freizugebenden Puffer wird routinemäßig wegoptimiert.
    - Wo die Sprache das **nicht** garantieren kann (unveränderliche Byte-Strings,
      ein kopierender/kompaktierender GC, Wert-Kopier-Semantik), MUSS (MUST) der
      Knoten jedes Geheimnis in **gepinntem/nativem/off-Heap**-Speicher halten, den er
      nullen *kann* (die Native-Memory-Klausel von RI-9b ist dann ein **MUSS (MUST)**,
      kein SOLLTE (SHOULD)), und DARF das Geheimnis NICHT (MUST NOT) überhaupt in
      einem laufzeitverwalteten Objekt (einem `bytes`/`str`, einem GC-Heap-Array)
      halten.
  Die Anforderung ist somit "nutze nullsetzbaren Speicher, dann lösche ihn" — in
  jeder Sprache erfüllbar — statt "lösche ein Objekt, das die Laufzeit dich nicht
  erreichen lässt". Bedrohung: dies sind genau die sub-`k`-Geheimbytes, die die
  Untergrenze verbirgt; sie in freigegebenem Heap, einem wiederverwendeten Puffer,
  einer verschobenen GC-Kopie oder einer protokollierten Struktur zu belassen, lässt
  ein späteres Speicherlesen sie rekonstruieren, was ein I-2-Bruch durch
  Speicheroffenlegung ist.
- **RI-9a (Geheimnisse aus Swap und Core-Dumps heraushalten).** Geheimpuffer SOLLTEN
  (SHOULD) in den RAM gesperrt werden (`mlock`/`mlockall`/`VirtualLock`), sodass sie
  niemals in eine persistente Swap-Datei ausgelagert werden, und der Prozess SOLLTE
  (SHOULD) Core-Dumps deaktivieren (`RLIMIT_CORE = 0` oder das Plattformäquivalent)
  oder Geheimseiten davon ausschließen. Ein Knoten, der das Auslagern von
  Geheimseiten nicht verhindern kann, SOLLTE (SHOULD) ein Deployment mit
  verschlüsseltem Swap nutzen und MUSS (MUST) das Restrisiko dokumentieren.
  Bedrohung: eine Swap-Datei oder ein Crash-Dump ist eine dauerhafte,
  festplatten-residente Kopie der sub-`k`-Bytes — die Untergrenze, verschüttet in
  Speicher, wo sie den Prozess lange überlebt.
- **RI-9b (Optimierer- und Sprachgefahren besiegen).** Eine Implementierung MUSS
  (MUST) sicherstellen, dass Compiler und Sprachlaufzeit die Lecks, die diese Regeln
  verbieten, nicht wiedereinführen: keine durch Optimierung wiederbelebte
  geheimnisabhängige Verzweigung (RI-1), kein kopiert-und-vergessenes Geheimnis aus
  einem reallozierenden Container, einem verschobenen Wert, einem
  garbage-collected-/kopierenden-GC-Heap, String-Interning oder einem
  Exception-/Stack-Trace, der einen Geheimpuffer erfasst. In Sprachen mit verwaltetem
  Speicher, in denen ein Puffer von der Laufzeit kopiert werden kann, SOLLTE (SHOULD)
  ein Knoten Geheimnisse in gepinntem/nativem Speicher halten, den er deterministisch
  nullen kann, und DARF sich NICHT (MUST NOT) darauf verlassen, dass der Garbage
  Collector sie löscht.
- **RI-12 (Fehler- und Exception-Sicherheit — kein partielles oder verknüpfbares
  Artefakt, schützt I-2/I-4).** Ein Absturz, eine Exception oder eine Abbrechung
  **mitten im Teilen** DARF NICHT (MUST NOT) einen partiellen Anteil-Satz, eine
  Teilmenge von Anteilen auf dem Draht oder irgendein Artefakt ausgeben, das die
  Anteile einer Nachricht verknüpft, und DARF NICHT (MUST NOT) geheimen Zustand
  nicht-genullt zurücklassen. Eine Implementierung MUSS (MUST) alle `n` Anteile bauen
  und sich zur Ausgabe als Alles-oder-Nichts-Schritt relativ zum Fehlschlag
  verpflichten, wobei sie Koeffizienten und Anteile auf jedem Fehlerpfad vor dem
  Zurückrollen auf null setzt. Bedrohung: ein Absender, der abstürzt, nachdem er
  einige, aber nicht alle Anteile ausgegeben hat, oder der einen Zwischen-Anteil in
  einem Stack-Trace protokolliert, händigt einem Beobachter eine korrelierte Teilmenge
  aus (die Unverknüpfbarkeit von SP-7 untergrabend und, falls sie `≥k` einer Nachricht
  enthüllt, die Untergrenze) — und ein nicht-genulltes Zurückrollen belässt das
  Geheimnis im Speicher (RI-9). Die Fehlerbehandlung MUSS (MUST) fail-closed sein:
  bei jedem Fehler während split, disperse oder reconstruct nichts produzieren und
  wischen, statt etwas Partielles zu produzieren.

## 10. Wie diese Anforderungen auf die Invarianten und Bedrohungen abbilden

| `RI` | Schützt | Bedrohung, die sie verwehrt (der Echt-Knoten-Angriff) |
|---|---|---|
| RI-1 / 1a / 1b / 1c | I-2 | Cache-/Branch-Timing-Wiederherstellung von sub-`k`-Bytes, inkl. der Behandlung des wiederhergestellten Geheimnisses jenseits der Feldoperationen |
| RI-2 / 2a / 2b / 2c | I-2 (SA-3) | schwacher/geforkter/klonbarer RNG → korrelierte Koeffizienten |
| RI-3 / 3a / 3b | SP-7b, SP-1a | Nonce-Rollback bei Neustart **oder Snapshot-/Backup-Wiederherstellung** → Tag-Kollision + Two-Time-Pad |
| RI-4 | CH-5 / CH-6 | Statik-Epochen-Rollback oder behaltene ausgemusterte Statik |
| RI-5 / 5a / 5b | SP-5, SP-7b | vergessener (oder wiederherstellungs-zurückgespulter) Replay-Zustand öffnet das Replay-Fenster erneut; die beiden Caches haben verschiedene Aufbewahrungsfenster |
| RI-6 / 6a / 6b | SP-1 / SP-1a | teilen-vor-verschlüsseln zerstört den rechnerischen Gürtel; ein öffentliches Roh-Split-Symbol umgeht das Gate |
| RI-7 / 7a | SP-7a | unauthentifizierte **oder timing-unterscheidbare** Rekonstruktion liefert Müll / wird zum Orakel |
| RI-8 | SP-1a, SP-7 | Tag-Prüfung nicht in konstanter Zeit → Fälschungs-Orakel |
| RI-10 | I-1, I-4 | die nicht implementierte Zwiebel-Schicht, interoperabel gebaut |
| RI-11 / 11a | CH-3 / CH-6, I-2 | X25519 in variabler Zeit oder ein wiederverwendeter/behaltener Ephemer |
| RI-9 / 9a / 9b | I-2 | Heap-/Swap-/Coredump-Offenlegung der sub-`k`-Bytes |
| RI-12 | I-2, I-4 | partielles/verknüpfbares Artefakt oder nicht-genulltes Crash-Zurückrollen |

Der rote Faden: alles, was einen sub-`k`-Geheimwert berührt (Anteil, Koeffizient,
rekonstruiertes Byte, Inhaltsschlüssel, Hop-Geheimnis, Client-Ephemer), wird an den
eigenen Standard der Untergrenze gehalten — es in konstanter Zeit berechnen
(RI-1/8/11), es aus einem soliden, fork-sicheren CSPRNG erzeugen (RI-2), kein
wiederverwendbares Geheimnis über einen Neustart hinweg persistieren (RI-3/4/5), die
API niemals das AEAD überspringen lassen (RI-6/7) und es löschen, bevor es
zurückgelesen werden kann (RI-9/12). Ein Überprüfer bricht diesen Teil, indem er
einen Echt-Knoten-Pfad findet, auf dem ein solcher Wert in variabler Zeit berechnet,
aus einem wiederverwendeten Strom gezogen, über einen Neustart hinweg wiederholt,
unauthentifiziert an die Oberfläche gebracht oder im Speicher lesbar belassen wird —
und dieser Pfad ist dann ein I-2-Bruch, keine bloße Härtungslücke.

## 11. Was dieser Teil **nicht** entscheidet

- **Netzwerk, Transport und Traffic-Shaping.** Der Chamäleon-Transport (Teil 4), die
  Batch-/Mix-Strategie und der Jitter (SP-6/OP-5) sowie das Timing der
  Anteil-Ausgabe (SP-9/OP-4) sind hier außerhalb des Geltungsbereichs; dieser Teil
  beschränkt die *kryptographische* Implementierung, nicht den Scheduler. Das
  Timing-Korrelations-Restrisiko zwischen Anteilen bleibt OP-4, von keinem RI-n
  behandelt (SA-2 und dieser Teil handeln von Werten, nicht von Ausgabezeiten).
- **Pfadauswahl und Disjunktheit.** Zu verifizieren, dass `n` Anteil-Pfade kein AS
  oder keine Jurisdiktion teilen (OP-1, Teil 3), ist keine
  Implementierung-eines-Primitivs-Frage und ist hier nicht erforderlich; RI-7a
  schützt nur gegen das *Vertrauen* auf ein belogenes `(k,n)`, nicht gegen einen
  nicht-disjunkten Pfad-Satz.
- **Sybil/Eclipse und die Gossip-Schicht.** Die korrekte Kryptographie eines
  konformen Knotens widersteht nicht von sich aus einem ressourcenstarken Gegner, der
  Position kauft (OP-2, GR-20a); dieses Restrisiko lebt in Teil 2 und wird von diesem
  Teil nicht berührt.
- **Die exakte Dimensionierung der Replay-Struktur und der Fork-Erkennungsmechanismus.**
  RI-5a begrenzt den Replay-Cache auf die Epoche und verbietet einen
  false-negative-anfälligen Filter, aber die konkrete Datenstruktur, ihre Parameter
  und das Persistenzmedium sind Implementierungswahlen, die gegen die
  roadmap-3.2-Vektoren und das Paketvolumen des Deployments festzupinnen sind, nicht
  hier fixiert.
- **Testvektoren und Konformität.** Die Vektoren, die zertifizieren, dass zwei
  Implementierungen interoperieren — die GF-Tabellen als normativ, die
  Sphinx-Ableitung je Hop, der
  encrypt→split→deposit→poll→reconstruct→decrypt-Pfad — sind **roadmap 3.2** und
  werden referenziert (RI-1b, RI-7a, RI-10, RI-11a), aber hier nicht reproduziert.
  RI-1b ist ausdrücklich, dass diese Vektoren Korrektheit zertifizieren, niemals
  Timing; eine Seitenkanal-Testsuite ist eine separate, empfohlene Verpflichtung
  (RI-1b), die dieser Teil verlangt, aber nicht spezifiziert.
- **Post-Quanten-Primitiv-Austausch.** Suite `0x02` (ein PQ-Hop-KEM, Teil 1 §5
  Abschluss) ändert, welches Primitiv RI-11 beschränkt, nicht die Anforderung, dass
  es in konstanter Zeit sein muss; die I-2-Untergrenze ist ungeachtet dessen
  PQ-sicher (SP-1a), sodass hier nichts davon blockiert ist.

## 12. Hier eingeführte Anforderungen

- **RI-1 / RI-1a / RI-1b / RI-1c** — GF(2⁸)-Multiplikation, -Inverse und -Division in
  konstanter Zeit, **erweitert auf die ganze Lebensdauer des wiederhergestellten
  Geheimnisses** (das SP-8-Längen-Parsing und jede Behandlung eines rekonstruierten
  Bytes), nicht nur die Feldoperationen; Vektoren zertifizieren Korrektheit, nicht
  Timing. **[protects I-2]**
- **RI-2 / RI-2a / RI-2b / RI-2c** — CSPRNG-Disziplin: kryptographischer DRBG vom OS,
  Fork-/Clone-Sicherheit, Gesundheitsprüfungen, keine injizierbaren Koeffizienten
  (nur hinter einem Build-Zeit-Test-Gate, nicht ausgeliefert). **[protects I-2 via SA-3]**
- **RI-3 / RI-3a / RI-3b** — persistierte, nicht-zurückrollende
  `msg_nonce`-High-Water-Mark, fsync-vor-Gebrauch, **und eine
  Wiederherstellung/ein Snapshot wird als Rollback behandelt** (das `kpair` erkennen
  oder ausmustern). **[protects SP-7b / SP-1a]**
- **RI-4** — persistierter Zustand der statischen `onion`-Epoche und nullsetzende
  Ausmusterung. **[protects CH-5 / CH-6]**
- **RI-5 / RI-5a / RI-5b** — persistierter Replay-Zustand für `gamma` (durch die
  Schlüsselepoche begrenzt) und `(box_id, slot)` (durch den **7-tägigen Slot-Ablauf**
  begrenzt, nicht die 1-tägige Box-Rotation); eine Wiederherstellung, die einen Cache
  zurückspult, ist eine verpflichtende Schlüsselepochen-Rotation. **[protects SP-5 /
  SP-7b]**
- **RI-6 / RI-6a / RI-6b** — API verweigert Klartext-ohne-AEAD; Chiffretext
  typ-getrennt; rohes `split`/`reconstruct` sind modul-privat. **[protects SP-1 /
  SP-1a]**
- **RI-7 / RI-7a** — fail-closed- **und konstante-Zeit-ablehnende** Rekonstruktion;
  defensives `(k,n)`-Parsing. **[protects SP-7a]**
- **RI-8** — AEAD in konstanter Zeit und Tag-Vergleich in konstanter Zeit.
  **[protects SP-1a / SP-7]**
- **RI-9 / RI-9a / RI-9b** — nullsetzbarer Speicher zuerst (gepinnt/nativ, wo die
  Laufzeit In-Place-Löschen verbietet), dann Anti-Dead-Store-Nullsetzen; kein Swap,
  keine Core-Dumps; Optimierer-/GC-Gefahren. **[protects I-2]**
- **RI-10** — die CH-2-Sphinx-Ableitung je Hop und die Replay-/Blinding-Disziplin
  implementieren; Vektoren sind roadmap 3.2. **[protects I-1 / I-4]**
- **RI-11 / RI-11a** — X25519 in konstanter Zeit; schlüsselloser, pro-Paket,
  genullter Ephemer; das All-Zero-Shared-Secret in konstanter Zeit ablehnen.
  **[protects CH-3 / CH-6 / I-2]**
- **RI-12** — Fehler-/Exception-Sicherheit: kein partielles oder verknüpfbares
  Artefakt, beim Zurückrollen nullen, fail-closed. **[protects I-2 / I-4]**

Keine davon ist ein Theorem; jede ist eine Bedingung, unter der die Theoreme von
Teil 7 und die Garantien der Teile 1–6 einen **echten Knoten** beschreiben statt des
Spielzeugs. Das Spielzeug lässt jede einzelne von ihnen absichtlich aus und sagt das.
Brich diesen Teil, indem du einen Echt-Knoten-Codepfad benennst, der ein
sub-`k`-Geheimnis in einer Weise berechnet, speichert oder offenlegt, die kein RI-n
oben verbietet — dieser Pfad ist eine in der Praxis gebrochene Untergrenze, und ihn
zu finden ist die Einladung.
