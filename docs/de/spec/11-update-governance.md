# ScrambNet-Spezifikation — Teil 11: Update-Governance
> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../../en/spec/11-update-governance.md)).

**Status: ENTWURF (DRAFT).** Dieser Teil entscheidet, wie ein Client dazu kommt,
eine **neuere** ScrambNet-Binärdatei auszuführen, *ohne demjenigen zu vertrauen,
der sie herausgegeben hat*, unter I-3 — keine Autorität — und unter zwei
projekt-eigner-gebundenen Einschränkungen: **keine maßgebliche Signierer-Menge**
und **kein Push jeglicher Art**. Es ist die Übernahme-Schicht, die Teil 10 §10.9
als außerhalb seines eigenen Geltungsbereichs benennt. Teil 10 entscheidet, *ob
diese Binärdatei der Build jenes Quellcodes ist*; dieser Teil entscheidet,
*welchen Build man ausführt und wann*. Strohmann-Werte sind mit `(s)` markiert.

Lies zuerst §1 und §10. Zusammen sagen sie, was dieser Teil einbringt (Reproduktion
und Aktualität, nicht Signatur, als Schiedsrichter der Übernahme) und was er vorweg
einräumt: eine Autorität *und* einen Push zu verweigern erkauft **Patch-Latenz** als
sein zentrales Residuum — ein verwundbarer Client wird vielleicht nie gepatcht, und
im schlimmsten Fall (ein Client, der bereits durch genau den Bug kompromittiert ist,
den ein Patch beheben würde) erfährt er beweisbar vielleicht nicht einmal von dem
Patch (§10.1). Das Projekt akzeptiert diese Kosten bewusst, weil die Alternative —
eine Partei oder ein Kanal, die ein Release allen auf einmal pushen können — genau
der konzentrierte Not-Aus-Schalter (kill switch) ist, den das ganze Projekt zu
verweigern existiert.

Dieser Teil verwendet wieder, statt neu zu erfinden: Teil 10s Frische-Index (RB-8a),
Release-Log (RB-13), Gossip (RB-14), die Zähle-nur-Verifiziertes-Disziplin
(RB-10/RB-10a) und den Zustand des nicht neu bauenden Clients (RB-7b); Teil 8s
erlaubnisfreien Transparenz-Log (ID-6/ID-7), die Verteidigung gegen Equivocation der
per Gossip verbreiteten Wurzel (ID-7a), die Mehrere-Logs-Regel (ID-7b) und das
erklärte TOFU (ID-8); Teil 2s Quellenmischung (GR-8); Teil 3s Ehrlichkeitsfläche
(PS-9). Die Naht mit Teil 10 wird zitiert, nicht neu entschieden (RB-2, Teil 10 §9).

## 1. Die Entscheidung, in zwei Sätzen

- **Es gibt keine Release-Autorität, und es gibt keinen Push.** Ein neueres Release
  ist ein reproduzierbares, inhaltsadressiertes Artefakt, angekündigt durch eine
  erlaubnisfreie Log-Anfügung (UG-2); ein Client *erfährt*, dass es existieren mag,
  nur durch Pullen und Gossippen nach seinem eigenen Zeitplan (UG-3), *entscheidet*,
  es zu übernehmen, durch eine manuelle, lokale, opt-in-Handlung (UG-4), und bindet
  diese Entscheidung an Reproduktion (RB-7) und Aktualität (RB-9a), **niemals** an
  denjenigen, der es angekündigt oder signiert hat (UG-1a, RB-2).
- **Übernahme-Vertrauen fließt durch Reproduktion und Aktualität; Widerruf kann nur
  informieren, niemals erzwingen; und der Preis — ein ungepatchter oder
  kompromittierter Client, der nie übernimmt — ist ein erklärtes Residuum, kein
  gelöstes Problem.** Keine Signatur sperrt die Übernahme (UG-2a); kein Mechanismus
  entfernt eine schlechte Binärdatei von einem laufenden Client (UG-8a); das
  Known-bad-Signal (bekannt-schlecht) ist eine erlaubnisfreie, zwanglose,
  ignorierbare Meldung, niemals eine Autorität (UG-8).

Also das ehrliche Ergebnis: **die Übernahme ist so autoritätsfrei, wie Reproduktion
sie macht, und so verlässlich wie ein Nutzer, der zu handeln wählt und nicht eklipst
ist — nicht mehr.** §10 ist das Residuum, das keine Konstruktion hier beseitigt.

## 2. Ein Release ohne Signierer ankündigen

- **UG-1 (keine Release-Autorität; Übernahme ist eine client-lokale Handlung).
  [normativ]** Kein Schritt des *Erfahrens von*, *Validierens* oder *Übernehmens*
  eines neueren Releases MUSS (MUST) darauf vertrauen, dass eine bestimmte Partei es
  herausgegeben, angekündigt, signiert oder gesegnet hat. Die einzigen
  vertrauenswürdigen Operationen sind die von Teil 10 definierten — `BLAKE2s`
  neuberechnen, neubauen-und-vergleichen (RB-1) — plus das Vergleichen monotoner
  Release-Indizes auf einer Linie (RB-8a, UG-2c). Jedes Element, das nicht durch
  einen nicht vertrauten Ersatz ersetzbar ist, der diese ausführt, ist ein Defekt
  unter I-3 und MUSS (MUST) entfernt oder in §10 erklärt werden (die ID-1-/RB-1-Regel,
  für die Update-Übernahme).
- **UG-1a (Übernahme bindet an Reproduktion, niemals an Veröffentlichung).
  [normativ]** *Welchen* Build man ausführt, wird vom Vertrauens-Anker aus Teil 10
  entschieden — reproduziert er (RB-7), ist er frisch (RB-9a) — und durch nichts
  darüber, *wer* ihn angekündigt hat. Ein Client DARF NICHT (MUST NOT) einen Build
  übernehmen, *weil* er von irgendeiner Partei, einem Schlüssel, einem Kanal oder
  einer Liste angekündigt wurde. Das wiederholt RB-2 (Signaturen lokalisieren,
  autorisieren nie) an der Übernahme-Grenze, an die RB-2 auf diesen Teil verweist.
- **UG-2 (Ankündigung ist eine erlaubnisfreie Log-Anfügung, kein privilegierter
  Anfüger). [normativ]** Ein Release wird angekündigt, indem sein Teil-10-Tupel
  `(triple, H_build, manifest-hash, release-index, committer-date)` (RB-8/RB-8a) an
  die erlaubnisfreien, nur anfügbaren (append-only) Transparenz-Logs von RB-13 / ID-6
  angefügt wird — dieselbe *Konstruktion* wie der Karten-Log, als Werkzeug
  wiederverwendet (RB-2a / ID-11a), niemals als geteilte Autorität. **Jeder DARF (MAY)
  anfügen**; es gibt keine Erlaubnisliste und keine Signierer-Menge, deren Anfügung
  ein Release offiziell macht (ID-7). Ein Log, der Release-Anfügungen hinter eine
  Liste sperrte, wäre die von I-3 verbotene Verzeichnis-Autorität und ist nicht
  konform (ID-7, RB-2a).
- **UG-2a (keine maßgebliche Signatur; Standard ist keine). [normativ]** Ein konformes
  Release trägt **keine maßgebliche Signatur**. Erscheint überhaupt eine pseudonyme
  Signatur, ist sie ein reiner RB-2-Lokalisierer — sie ordnet einen Build einer
  fortdauernden pseudonymen Hand zur Gossip-Bequemlichkeit zu —, und ein Client MUSS
  (MUST) eine signierte und eine unsignierte Ankündigung desselben
  `(triple, H_build, release-index)` so behandeln, dass sie **identisches
  Übernahme-Gewicht** tragen, sobald die Reproduktion sie bestätigt (RB-10). Ein
  Entwurf, in dem die Annahme einer Ankündigung von der Identität eines Signierers
  abhängt, ist nicht konform (RB-1, RB-12).
- **UG-2b (die Release-Linie ist von keiner Partei besessen). [normativ]** Der Index
  von RB-8a ist monoton *innerhalb einer Release-Linie*. Eine Linie MUSS (MUST) so
  definiert sein, dass keine Partei das Recht besitzt, sie zu verlängern; andernfalls
  wird "füge einen höheren Index an" zu einer Autorität, das nächste Release zu
  erklären (die von I-3 verbotene Verzeichnis-Autorität, die eine Versionsnummer
  trägt). UG-2c gibt die Konstruktion.
- **UG-2c (Linien-Identität ist eine reproduktions-verifizierbare Manifest-Kette ab
  einer Genesis). [normativ]** Eine Linie wird durch `line_id = BLAKE2s` ihres
  **Genesis-Manifests** identifiziert (das kanonische Manifest des ersten Releases,
  RB-8a). Ein Release **verlängert** `line_id` genau dann, wenn sein Manifest den
  manifest-hash des vorherigen Releases als explizites Vorgänger-Feld trägt **und**
  sein getaggter Quellcode vorwärts reproduziert (RB-7) aus einer Quellcode-Abstammung,
  deren vorheriger Tag der des Vorgängers ist — sodass "die Linie verlängern" eine
  **erlaubnisfreie, reproduktions-prüfbare Handlung** ist: jeder, der ein
  reproduzierendes Nachfolger-Manifest erzeugen kann, DARF (MAY) einen höheren Index
  anfügen, und kein Repository, kein Committer und kein Schlüssel besitzt die Linie.
  Ein **Fork** ist jedes Manifest, das nicht an `line_id` kettet; er trägt
  notwendigerweise eine andere `line_id` und ist daher **als eigene Linie sichtbar**,
  niemals ein stiller höherer Index, der in die verfolgte eingeschleust wird (die
  ID-2-"der Hash ist der einzige Name"-Regel, für die Release-Abstammung). `line_id`
  ist über ehrliche Releases hinweg stabil (der Genesis-Hash ändert sich nicht) und
  doch von niemandem besessen (die Kette ist öffentlich und reproduktions-geprüft) —
  die zwei Eigenschaften, die UG-2b verlangt.

## 3. Entdeckung ohne einen Push

- **UG-3 (Entdeckung ist nur Pull/Gossip; kein Push-Pfad existiert). [normativ]** Ein
  Client erfährt, dass ein neueres Release existieren *mag*, **nur** durch (a) das
  Pullen des Frische-Index (RB-8a) und der Log-Tupel der Linie (RB-13) nach seinem
  eigenen Zeitplan und (b) das Gossippen von
  `(line_id, triple, H_build, release-index)` über GR-6 unter GR-8-Quellenmischung
  (RB-14). Kein Mechanismus in diesem Teil — und keiner, den eine konforme
  Bereitstellung hinzufügen DARF (MAY) — pusht ein Release, eine Benachrichtigung
  oder eine Aufforderung an einen Client. Der schwächere "Verfügbarkeit-melden"-Pfad
  wird **ausdrücklich nicht übernommen**: Aktualität wird gepullt und gegossippt,
  niemals zugestellt (die bindende Einschränkung des Eigners, normativ angegeben,
  sodass ein Implementierer keinen Push wieder hinzufügen und konform bleiben kann).
- **UG-3a (keine einzelne Quelle sperrt Aktualität). [normativ]** Ein Client DARF
  NICHT (MUST NOT) den höchsten release-index, den er gesehen hat, auf das Wort
  irgendeines einzelnen Peers, Logs oder Spiegels als aktuell behandeln, bevor er
  GR-8 / PS-10 "zähle nur unabhängig verifizierte Quellen" angewandt hat (RB-14,
  ID-9). Seine Sicht darauf, *was aktuell ist*, ist eine quellengemischte Beobachtung
  unter derselben Eklipse-Verteidigung wie seine Karten- und Relais-Stichproben-Sicht.
- **UG-3b (Entdeckungs-Kadenz ist client-lokal und datenschutz-begrenzt). [normativ]**
  Die Pull-Kadenz ist eine client-lokale Richtlinie (Strohmann: opportunistisch, in
  bestehende GR-6-Gossip-Stapel eingefaltet, niemals ein unterscheidbares Beacon (s)).
  Frische-Pull-Verkehr DARF NICHT (MUST NOT) zu einem Fingerabdruck werden; er reitet
  auf dem Gossip-Kanal, den der Client ohnehin nutzt (die GR-8-/Teil-6-Metadaten-
  Disziplin, auf die Update-Entdeckung angewandt).
- **UG-3c (ein Client pullt nach seiner eigenen Uhr, niemals als Reaktion auf ein
  Peer-Signal). [normativ]** Ein Client DARF (MAY) einen Abruf **nur** nach seiner
  eigenen datenschutz-begrenzten Kadenz (UG-3b) oder auf eine explizite Nutzerhandlung
  hin einleiten. Er DARF NICHT (MUST NOT) einen Abruf *als Reaktion auf* ein von einem
  Peer gemeldetes Divergenz-, Known-bad- oder Equivocation-Signal einleiten: Dieser
  reaktive Auslöser ist das ID-9a-Re-Fetch-Downgrade (Teil 8 §10 markiert "behandle
  deine Karte als verdächtig, hole neu" als eine unterverteidigte Richtung, die ein
  Gegner treibt), und für Updates ist er **Push in Verkleidung** (UG-5a). Anomalien
  werden sichtbar gemacht und gegossippt (UG-7), niemals durch Abrufen behandelt. Das
  ist die Grenze zwischen "mein geplanter Pull bemerkte einen höheren Index" (erlaubt)
  und "ein Peer brachte mich dazu, nachzuschauen" (verboten).

## 4. Die Entscheidung zur Übernahme (manuelles Opt-in, keine Signatur-Sperre)

- **UG-4 (Übernahme ist eine manuelle, lokale, opt-in-Handlung). [normativ]** Die
  laufende Binärdatei durch eine entdeckte neuere zu ersetzen, ist eine Entscheidung,
  die der **Nutzer** lokal trifft; kein konformer Client übernimmt ein Release
  automatisch, per Timer oder beim Erreichen irgendeiner Bestätigungs-Schwelle. Die
  Schwelle regelt, *was der Client anbieten oder sichtbar machen darf*, niemals, *was
  er installiert*. "Bestätigt" ist eine Vorbedingung, die der Client prüft;
  "übernehmen" ist eine Handlung, die der Nutzer vornimmt (die ID-8b-"erkennen, nicht
  zu verhindern behaupten"-Haltung, von der Erkennung zur Übernahme verschoben).
- **UG-4a (die Übernahme-Checkliste — keine Signatur-Sperre). [normativ]** Bevor ein
  Client ein entdecktes Release als *übernehmbar* sichtbar macht, MUSS (MUST) er für
  sein eigenes Ziel-triple und seine verfolgte `line_id` haben:
  1. **Reproduktions-Bestätigung** — `H_build` stimmt mit dem Manifest überein, durch
     den eigenen Neubau des Clients (RB-7) **oder**, für den nicht neu bauenden
     modalen Client (RB-7b), eine Zählung **unabhängig verifizierter** Reproduzierer
     unter RB-10 (niemals eine rohe Attestierungs-Summe);
  2. **Aktualität** — ein release-index ≥ dem höchsten, den der Client auf jener Linie
     bezeugt hat, geordnet im Log (RB-9a, RB-8a, UG-2c);
  3. **Log-Bestätigung** — Erscheinen mit konsistenten per Gossip verbreiteten Wurzeln
     in einem konfigurierten Quorum der Logs, die er überwacht (ID-7b, Strohmann ≥2
     (s));
  4. **keine Equivocation** — keine ausstehende UG-6-Split-View-Anomalie gegen jene
     Linie.

  Es gibt **keinen Signatur-Sperr-Schritt**, durch Konstruktion (UG-2a). Ein Client
  DARF NICHT (MUST NOT) irgendeines davon als "verifiziert" darstellen, wenn er nur
  Bestätigung-durch-Zählung hat; er trägt den Teil-10-Zustand
  `reproduced-by-others-unverified` bis in die UI durch (RB-7b).
- **UG-4b (Übernahme-Richtlinie ist erklärt, client-lokal, standardmäßig konservativ).
  [normativ]** Die Richtlinie, die die UG-4a-Prüfungen in ein *Angebot* verwandelt,
  ist client-lokal und MUSS (MUST) dem Nutzer erklärt werden (Strohmann-Standard:
  biete nur ein per Index frischeres Release an, reproduktions-bestätigt über der
  Schwelle des Clients, log-bestätigt im Quorum und frei von Equivocation; biete
  niemals über einen `line_id`-Wechsel hinweg (UG-2c) ohne einen expliziten
  Nutzerschritt an (s)). Ein Client DARF (MAY) eine striktere Richtlinie offenlegen
  (z. B. "biete nur an, was ich selbst neu gebaut habe"); er DARF NICHT (MUST NOT)
  eine offenlegen, die schwächer ist als "frischerer Index + im Quorum bestätigt +
  keine Equivocation", weil schwächer sich darauf reduziert, auf das Wort einer
  einzelnen Quelle hin zu übernehmen (UG-3a). **Eine unwiderlegte
  Known-bad-Meldung der Schwachstellen-Klasse (UG-8) DARF NICHT (MUST NOT) von sich
  aus ein Release unter diese Angebots-Schwelle senken** (UG-8, Verteidigung gegen
  H-Verleumdung).
- **UG-4c (Anbieten und Installieren sind mechanisch getrennt). [normativ]**
  **ANBIETEN** ist das Sichtbarmachen eines Verfügbarkeits-und-Bestätigungs-Zustands
  gegenüber dem Nutzer; es DARF NICHT (MUST NOT) den Artefakt-Körper als Reaktion auf
  einen Divergenz- oder Known-bad-Auslöser abrufen (UG-3c), und jedes Vorabholen MUSS
  (MUST) auf der UG-3b-Kadenz reiten, sodass es kein unterscheidbares Beacon
  hinzufügt. **INSTALLIEREN** ist eine vom Nutzer eingeleitete Handlung, die die
  laufende Binärdatei ersetzt. Kein automatischer Übergang von ANBIETEN zu
  INSTALLIEREN darf existieren (UG-10). Eine Implementierung, die eine Binärdatei einen
  Fingertipp vom Laufen entfernt vorab-staged oder auf ein Peer-Signal hin abruft, hat
  einen Push gebaut und ist nicht konform, selbst wenn sie den Schritt "anbieten"
  nennt.

## 5. Die Verteidigung gegen reproduzierbaren Downgrade, client-seitig

- **UG-5 (akzeptiere niemals still einen niedrigeren Index; mache ihn sichtbar).
  [normativ]** Ein Client DARF NICHT (MUST NOT) ein Release, dessen Index **niedriger**
  ist als der höchste, den er für jene `line_id` bezeugt hat, übernehmen noch still
  als aktuell behandeln (RB-9a). Ein vorgelegter niedrigerer Index ist die
  Einzel-Sichtpunkt-Signatur eines **reproduzierbaren Downgrade-Angriffs** — ein
  alter, perfekt reproduzierender, bekannt verwundbarer Tag, dem Client zugeführt
  (RB-9a) — und MUSS (MUST) dem Nutzer sichtbar gemacht und als Downgrade-Anomalie
  gegossippt werden (UG-7d), niemals als ein gewöhnliches "neuestes" verzehrt. Weil
  der Index an das abgeleitete Committer-Datum und die Manifest-Kette gebunden ist
  (RB-8a, UG-2c) und im Log geordnet wird (RB-13), ist "niedrigerer Index" eine
  prüfbare Eigenschaft, kein Urteil.
- **UG-5a (Veraltung wird sichtbar gemacht, nicht behandelt). [normativ]** Wenn der
  eigene laufende Index eines Clients unter den aktuellen Index eines bestätigten
  Quorums für seine Linie fällt, MUSS (MUST) er die Veraltung dem Nutzer sichtbar
  machen (PS-9s Ehrlichkeitsfläche, wiederverwendet) — *du führst ein älteres Release
  aus als deine bestätigten Peers; ein neueres existiert.* Er DARF NICHT (MUST NOT)
  auf dieses Sichtbarmachen durch Pullen, Auffordern-als-Push oder Übernehmen hin
  handeln (UG-3c); er informiert, und der Nutzer entscheidet (UG-4). Die ehrliche
  Asymmetrie mit ID-9a ist bewusst: Die Maschinerie der Karte *holt neu* bei
  Divergenz; die Update-Übernahme darf das **nicht**, weil ein erzwungenes Neuholen
  ein Push in Verkleidung wäre. Veraltung endet an der Ehrlichkeitsfläche.

## 6. Split-View und Equivocation bei Releases

- **UG-6 (zwei verschiedene "neueste" an zwei Clients wird durch per Gossip
  verbreitete Wurzeln gefangen). [normativ]** Ein Gegner, der Release X an Alice und
  Release Y an Bob ausliefert — gleiches triple, gleiche `line_id` —, ist ein
  Split-View-Angriff auf *Aktualität*, der ID-7a-Angriff, der eine Update-Maske trägt.
  Die Verteidigung ist **nicht** das Vertrauen in den Log-Betreiber; sie ist das
  Gossippen der signierten Baumwurzeln der Logs über GR-6 (GR-8-quellengemischt) und
  das Verlangen von **Konsistenzbeweisen** zwischen je zwei Wurzeln, die ein Client
  sieht (ID-7a, RB-14). Ein Client, der beide Wurzeln hält, hat kryptografischen Beweis,
  dass der Log equivoziert hat, und MUSS (MUST) ihn als feindlich behandeln (ID-10,
  UG-7b).
- **UG-6a (Index-Equivocation ist die quer-sichtpunktliche Signatur; von Downgrade
  unterschieden). [normativ]** **Downgrade** (UG-5 / UG-7d) ist die
  *Einzel-Sichtpunkt*-Signatur: *mein eigenes* bezeugtes Maximum auf einer Linie ist
  zurückgegangen. **Index-Equivocation** (UG-7b) ist die *quer-sichtpunktliche*
  Signatur: dieselbe `line_id` mit einem anderen höchsten Index an verschiedene
  quellengemischte Sichtpunkte vorgelegt **und** die Wurzeln der Logs scheitern an
  einem Konsistenzbeweis — zwei verschiedene Indizes allein sind keine Equivocation
  (ein Sichtpunkt mag einfach hinterher sein); das **Scheitern des Konsistenzbeweises**
  ist, was sie beweist. Ein einziges zugrundeliegendes Ereignis mag beide Signaturen
  auslösen (das an einem veralteten Index fixierte Opfer sieht ein Downgrade, wenn es
  später vom höheren hört; eine Partei, die beide Wurzeln hält, sieht Equivocation);
  es MUSS (MUST) per `(line_id, widersprüchliche Wurzeln)` dedupliziert werden (die
  RB-10a-Dedup-Disziplin, wiederverwendet), sodass es einmal gezählt wird.
  Index-Equivocation wird gegossippt, sodass ein teilweise eklipster Client sie bei
  nicht eklipsten Peers fängt.

## 7. Release-Anomalien werden gegossippt, nicht unterdrückt

- **UG-7 (verpflichtender Anomalie-Gossip). [normativ]** Fünf Ereignisse sind
  Release-Anomalien, die jeder Client bei Erkennung gossippen MUSS (MUST), unter
  Vergleich nur von Daten gleichen triples und gleicher `line_id` und dedupliziert
  gemäß RB-10a: (a) ein `H_build`, das die Reproduktion aus seinem Manifest scheitern
  lässt (RB-7a / RB-15a); (b) ein Log, der über Release-Ankündigungen inkonsistente
  Wurzeln vorlegt — bewiesene Equivocation (RB-15b, UG-6/UG-6a); (c) eine persistente
  `H_build`-Divergenz gleichen triples gegen unabhängige Reproduzierer (RB-15c); (d)
  eine **Release-Index-Regression** auf einer Linie — die Downgrade-Signatur (UG-5 /
  RB-15d); (e) eine **Known-bad-Meldung** (UG-8). Ein Client DARF NICHT (MUST NOT)
  eine Anomalie unterdrücken, um ein Release gesund aussehen zu lassen (ID-10, für
  Releases).

## 8. Das Widerrufs-Problem (das schwere)

- **UG-8 (Known-bad ist eine erlaubnisfreie, bestätigte, zwanglose MELDUNG — niemals
  ein maßgeblicher Widerruf). [normativ]** "Release X ist Known-bad" kann keine
  maßgebliche Aussage sein: *jede* Partei, der vertraut wird, ein Release für schlecht
  zu erklären, ist ein Not-Aus-Schalter (sie kann ein ehrliches Release **zensieren**,
  indem sie es für schlecht erklärt — die I-3-Autorität invertiert), also existiert
  keine solche Partei. Stattdessen liefert dieser Teil eine **Known-bad-Meldung**:
  eine Behauptung `(line_id, triple, H_build, reason-class, evidence-locator)`, die
  **jeder veröffentlichen DARF (MAY) und jeder ignorieren DARF (MAY)**. Meldungen
  überqueren den Draht und speisen eine Zählung, also MÜSSEN (MUST) sie **RB-10a
  wortwörtlich wiederverwenden**: kanonisches CBOR, Dedup per
  `(Reproduktions-Identität des Melders, line_id, triple, H_build, reason-class)` und
  Gewicht **pro unabhängigem Reproduzierer, niemals pro Meldungs-Bytes** — ohne das
  ist der Kanal ein Format-Stuffing-/Verleumdungs-Hebel (H-Verleumdung). Evidenz
  teilt sich in zwei Arten:
  - **reproduzierbare Evidenz (die Meldung verifiziert sich selbst; kein Vertrauen
    nötig)** — *Nicht-Reproduktion* (aus dem Manifest neu bauen und RB-7a scheitern
    sehen), *Index-Regression / Downgrade* (die Log-Ordnung zeigt es, UG-5),
    *Log-Equivocation* (der Konsistenzbeweis scheitert, UG-6). Für einen Client, der
    **neu bauen / einen ehrlichen Reproduzierer erreichen kann**, reduziert sich
    "Known-bad" hier auf eine Teil-10-Prüfung, die er selbst ausführt; die Meldung
    *lokalisiert* den Defekt lediglich, sie *autorisiert* das Urteil nicht.
  - **nicht reproduzierbare Evidenz (reduziert sich auf sozialen Konsens)** — *"dieser
    reproduzierende Build enthält eine Schwachstelle / Hintertür."* Keine
    kryptografische Prüfung entscheidet das — es ist das Teil-10-§10.1-/OP-10-Residuum
    der Quellcode-Ehrlichkeit. Hier ist "Known-bad" eine Behauptung, gewichtet durch
    öffentliche Überprüfung (I-1), Bestätigungs-Zählung und
    Reproduzierbarkeit-der-Evidenz-wo-sie-existiert (ein PoC, der neu baut), und sie
    reduziert sich auf **OP-2 und die soziale Schicht des Projekts**. Eine
    **unwiderlegte Meldung der Schwachstellen-Klasse DARF NICHT (MUST NOT) von sich
    aus ein Angebot sperren** (UG-4b): sie DARF (MAY) das Angebot nur *annotieren* ("N
    unabhängig verifizierte Parteien behaupten eine Schwachstelle; Evidenz unter …"),
    niemals das Release unter die UG-4a-Schwelle senken — gerade weil diese Klasse
    sybil-wählbar ist (GR-19a) und das Sperren daran einen Gegner einen ehrlichen
    Sicherheitspatch in Veraltung zensieren ließe.

  **Das modale Telefon (RB-7b) genießt die reproduzierbaren Klassen nicht.** Ein
  Client, der nicht neu bauen kann, kann eine Nicht-Reproduktions-Meldung nicht
  selbst-verifizieren, und ein eklipster Client kann die zwei Wurzeln nicht halten,
  die ein Log-Equivocation-Beweis braucht (ID-7a §10). Für den nicht neu bauenden oder
  eklipsten Client reduzieren sich **alle außer der arithmetischen
  Index-Regressions-Prüfung auf RB-10-Bestätigung, d. h. OP-2** (die Teil-10-§10.5-
  Reduktion, geerbt — siehe §10.2). Ein konformer Client DARF NICHT (MUST NOT)
  automatisch auf eine Known-bad-Meldung hin handeln (das würde den Push und die
  Autorität auf einmal wieder erschaffen); er macht die Meldung mit ihrer
  Bestätigungs-Ebene und Evidenz-Klasse sichtbar, und der Nutzer entscheidet, ob er
  anhält oder wechselt.
- **UG-8a (Widerruf kann nur informieren; er kann nicht pushen, also kann er nicht
  zwangs-patchen). [normativ]** Weil kein Push existiert (UG-3) und keine Autorität
  existiert (UG-1), erreicht eine Known-bad-Meldung einen Client nur, wenn dieser
  Client pullt/gossippt, und ändert nichts, bis der Nutzer handelt. Es gibt **keinen
  Mechanismus, eine Known-bad-Binärdatei von einem laufenden Client zu entfernen**,
  und dieser Teil gibt nicht vor, einen zu haben. Das Known-bad-Signal macht ein
  schlechtes Release *für einen aufmerksamen, nicht eklipsten Nutzer erkennbar und
  vermeidbar*; es kann es nicht per Dekret *unausführbar* machen. Das ist das
  Widerrufs-Residuum (§10.2), angegeben, nicht geglättet.
- **UG-8b (selbst-verifizierende Ausführungsverweigerung (refuse-to-run) —
  autoritätsfrei, opt-in, nur Selbstbeweis). [normativ]** Ein Client, der **selbst**
  beweist (RB-7, keine externe Partei), dass seine **eigene laufende Binärdatei** die
  Reproduktion gegen ihr ausgeliefertes Manifest scheitern lässt — oder dass sein
  eigener eingebetteter Index eine Regression ist, die er arithmetisch gegen eine
  nicht eklipste Untergrenze prüfen kann —, DARF (MAY), **als client-lokales Opt-in,
  nicht als Standard**, sich weigern, jene Binärdatei weiter auszuführen, und auf
  Neu-Bootstrap zurückfallen (ID-8). Das ist **autoritätsfrei** (der Beweis ist der
  eigene Neubau des Clients, und ein falscher Nicht-Reproduktions-Beweis ist
  *unmöglich* — der Gegner kann ehrlichen öffentlichen Quellcode nicht zu einem
  schlechten `H` reproduzieren lassen, ID-8a.3) und es ist **kein Push** (nichts wird
  installiert; der Client weigert sich, Code auszuführen, von dem er bewies, dass er
  nicht die Reproduktion seines eigenen angegebenen Quellcodes ist — das
  Laufzeit-Analogon zu RB-7a, das ein nicht reproduzierendes Release bereits bei der
  Übernahme *ablehnt*). Ausführungsverweigerung MUSS (MUST) für jede Evidenz, die der
  Client nicht selbst-verifizieren kann, **verboten** bleiben — die Schwachstellen-
  Klasse und alles, was auf einer Bestätigungs-Zählung oder einer Quorum-Untergrenze
  ruht (beide OP-2 / eklipse-fälschbar) —, weil dort eine *falsche* Untergrenze oder
  Meldung ein Denial of Service gegen einen ehrlichen Client wäre. Das schützt nur den
  **neu bauenden** Client; das nicht neu bauende modale Telefon (RB-7b) reduziert sich
  weiterhin auf OP-2 (§10.2), sodass UG-8b die Flotten-Sicherheits-Lücke (§10.1)
  verengt, ohne sie zu schließen.

## 9. Bootstrap: das erste Update ist TOFU

- **UG-9 (das erste Update erbt Teil 10s First-Binary-TOFU und kann sich nicht selbst
  verifizieren). [normativ]** Die Sicht eines Clients darauf, *welches Release aktuell
  ist*, wird durch die Binärdatei vermittelt, die er bereits ausführt; eine
  kompromittierte erste Binärdatei (Teil 10 §10.8) besitzt den gesamten Entdeckungs-,
  Frische- und Gossip-Apparat des Clients und kann daher **über Aktualität lügen** —
  den Nutzer an einem veralteten, verwundbaren Index fixieren, eine Known-bad-Meldung
  über sich selbst verbergen oder eine Equivocation unterdrücken, an der sie beteiligt
  ist. Ein Client kann seine *eigene* Aktualität ebenso wenig ehrlich verifizieren wie
  seine *eigene* Reproduktion (Teil 10 §10.8). Das Vertrauen in das erste Update ruht
  auf derselben **außerbandigen unabhängigen Bestätigung** wie die erste Binärdatei:
  eine Sicht auf release-index und Known-bad, erreicht von einer Maschine oder einem
  Kanal, dem der Nutzer mehr vertraut als der zu testenden Binärdatei. Das ist
  erklärtes TOFU (ID-8), nicht gelöst.
- **UG-9a (die erste Release-Wahl eines frischen Clients ist TOFU über unabhängige
  Kanäle). [normativ]** Bei der ersten Installation MUSS (MUST) ein Client sein
  anfängliches `(line_id, index, H_build)` über so viele **unabhängige** Kanäle
  beziehen, wie er hat (Teil 10 §10.8 / ID-8: die außerbandige Bridge-Linie GR-10 plus
  ≥2 Spiegel über verschiedene Netze (s)), **dasselbe** `(line_id, index, H_build)`
  von allen verlangen, bevor er es vorläufig annimmt, und es als **unverified-TOFU**
  aufzeichnen, bis er neu baut (RB-7) oder konsistente per Gossip verbreitete
  Bestätigung ansammelt. Er MUSS (MUST) diesen Zustand sichtbar machen: *du vertraust
  deinem ersten Client und deiner ersten Vorstellung von "neuestem"; keines ist bisher
  bestätigt.*

## 10. Was dieser Teil nicht löst (das erklärte Residuum)

Dieser Teil verschiebt das Update-Übernahme-Vertrauen von *wer es ausgeliefert hat*
auf *reproduziert es und ist es frisch*, und verweigert sowohl eine Autorität als
auch einen Push — die richtige Wahl für ein Projekt, dessen jede Liste ein
Zwangs-Ziel ist. Er liefert **nicht** eine gepatchte, sichere Flotte. Die Lücken sind
real und werden erklärt, nicht geglättet:

- **§10.1 — Das Ungepatchte-Flotte-Residuum und sein schlimmster Fall: kein Push
  bedeutet keinen erzwungenen Patch, und der kompromittierte Client erfährt beweisbar
  vielleicht nie von der Behebung. [primäres Residuum]** Ein Client, dessen Nutzer nie
  manuell übernimmt — offline, unaufmerksam oder verlassen —, führt sein aktuelles
  Release, Schwachstellen und alles, **unbegrenzt** aus (UG-4). Kein Override
  existiert, weil ein Override ein Push ist. Schlimmer, die Klauseln setzen sich gegen
  die Flotte zusammen: im einen Szenario, das am meisten zählt — ein Client, der eine
  **aktiv ausgenutzte RCE** ausführt —, ist die laufende Binärdatei **bereits
  angreifer-kontrolliert**, und das ist genau die Binärdatei, von der UG-9 sagt, dass
  sie über Aktualität lügen und das Known-bad über sich selbst unterdrücken kann. Also
  läuft der Mechanismus, der den Patch leiten würde (Gossip + Veraltungs-Fläche,
  UG-3/UG-5a), **innerhalb des kompromittierten Prozesses** und kann stummgeschaltet
  werden. Die ehrliche Schlussfolgerung: für den kompromittierten-RCE-Fall bieten die
  Ehrlichkeitsfläche und der Gossip-Pfad **keine** Garantie der Zustellung; das
  Residuum ist nicht "langsameres Patchen", sondern **"die kompromittierte Teilmenge
  übernimmt vielleicht nie"**, ein terminaler Zustand bis zum außerbandigen
  Neu-Bootstrap (ID-8), nur dadurch begrenzt, dass der Nutzer es über einen Kanal
  außerhalb des kompromittierten Clients bemerkt. UG-8b verengt das für den *neu
  bauenden* Opt-in-Client (er kann sich weigern, eine selbst-bewiesen-schlechte
  Binärdatei auszuführen), nicht für das modale Telefon. Das ist der bewusste Preis
  dafür, einen Push und eine Autorität zu verweigern, und er wird zuerst und in voller
  Stärke benannt.
- **§10.2 — Widerruf-ohne-Autorität ist für die Schwachstellen-Klasse
  unerreichbar und reduziert sich für den modalen Client über mehr als eine Klasse
  auf OP-2.** Nicht-Reproduktion, Downgrade und Equivocation sind autoritätsfrei
  widerrufbar *nur für einen Client, der neu bauen oder einen ehrlichen Reproduzierer
  erreichen kann* (UG-8). "Dieser reproduzierende Build ist hintertürig" ist niemals
  autoritätsfrei — keine Prüfung entscheidet Quellcode-Ehrlichkeit (OP-10 / Teil 10
  §10.1) —, also ruht der Widerruf eines überprüften-aber-bösartigen Releases auf
  öffentlicher Überprüfung (I-1), auf Bestätigung, deren Unabhängigkeit nicht
  verifizierbar ist (RB-10 / GR-19a), und darauf, dass der Nutzer zu handeln wählt:
  OP-2 plus die soziale Schicht. Für den **nicht neu bauenden oder eklipsten modalen
  Client** reduzieren sich die Nicht-Reproduktions- und Log-Equivocation-Klassen
  **ebenfalls** auf OP-2 (nur die arithmetische Index-Regressions-Prüfung überlebt die
  Selbst-Verifikation) — die Teil-10-§10.5-Reduktion, geerbt. Der Beitrag des Entwurfs
  ist, die Known-bad-*Behauptung* erlaubnisfrei, bestätigt, dedup-diszipliniert
  (RB-10a) und **zwanglos** zu machen, sodass sie nie eine Autorität ist; er trägt
  **keinen** Mechanismus bei, der ein schlechtes-aber-reproduzierendes Release von
  einer laufenden Flotte entfernt.
- **§10.3 — Der eklipste Client erfährt nie vom Update, und seine Frische-Maschinerie
  ist manipulierbar.** Ein eklipster Client (OP-2) berührt keine ehrliche Wurzel,
  sodass die Equivocation-Erkennung von UG-6 **nicht feuern kann** — das Opfer hält nie zwei
  widersprüchliche Wurzeln. Unter Eklipse kann ein Gegner das Opfer an einem
  **veralteten, bekannt verwundbaren Index** fixieren (ein stilles Downgrade, das
  UG-5 nicht fangen kann, weil das Opfer nie den höheren Index bezeugt), jede
  Known-bad-Meldung über den laufenden Build **unterdrücken** und eine
  **sybil-bestätigte** eingefrorene Vergangenheit zeigen. Aktualität ist eine
  *relative* Garantie — frischer als das, was du bezeugt hast —, und ein eklipster
  Client hat nur bezeugt, was der Gegner zuließ. Für den nicht neu bauenden eklipsten
  Client bedeutet "keine Autorität, nur Pull" "vertraue dem quellengemischten Quorum",
  und das hält **nur so weit wie OP-2** — die Reduktion, mit der die Teile 8 und 10
  enden.
- **§10.4 — Der nie übernehmende Nutzer steckt durch Entwurf fest.** Das manuelle Opt-in von UG-4
  bedeutet, dass ein Nutzer, der jedes Angebot abweist, auf einem alten Build
  bleibt; es gibt keinen Override, weil ein Override ein Push ist. Der Entwurf
  akzeptiert einen **von null verschiedenen Dauerzustands-Bruchteil der Flotte auf
  veralteten Releases** als die erklärten Kosten dafür, einen Push zu verweigern, und
  macht Veraltung sichtbar (UG-5a), statt auf sie hin zu handeln.
- **§10.5 — First-Update-TOFU erbt Teil 10 §10.8 und ist für Aktualität strikt
  schlechter.** Eine kompromittierte erste Binärdatei kann über Aktualität ebenso
  leicht lügen wie über Reproduktion — den Nutzer für immer an einem veralteten Index
  einfrieren, von innen unerkennbar (UG-9). Die Erste-Vorstellung-von-neuestem ist
  TOFU, nur außerbandig bestätigt.
- **§10.6 — Geteilte Werkzeuge, nicht geteilte Autorität, müssen für den Update-Log
  neu auditiert werden.** Die Wiederverwendung der Log-Konstruktion und des
  Gossip-Kanals der Karte / von Teil 10 (RB-2a, ID-11a) ist *nur* frei, solange keine
  Partei eine Rolle hat, die sowohl für die Karte/den Code als auch für die
  Update-Linie tragend ist. Eine konforme Bereitstellung MUSS (MUST) die Anfüger des
  Release-Linien-Logs als Nicht-Liste halten (UG-2) und SOLLTE (SHOULD) eine
  Log-Menge nutzen, die von der der Karte unabhängig ist (ID-7b), sodass "Bequemlichkeit:
  dieselben Betreiber wiederverwenden" nicht still den quer-schneidenden Not-Aus-
  Schalter wieder erschafft, den ID-11 verbietet. Der Fork-vs-Flucht-Fall ist ein
  weiteres Residuum: ein ehrlicher Hard-Fork (legitime Divergenz) und ein Gegner, der
  eine parallele Linie eröffnet, um einem Downgrade/Known-bad auf der verfolgten Linie
  zu entkommen, sind **auf Protokoll-Ebene ununterscheidbar** — beide sind eine neue
  `line_id` (UG-2c). UG-2c macht die *Existenz* einer zweiten Linie sichtbar; es
  entscheidet nicht die *Absicht*, die ein soziales / OP-2-Urteil ist, kein
  kryptografisches.

Die ehrliche Zusammenfassung: Dieser Teil verweigert sowohl eine Autorität als auch
einen Push, und im Austausch ist er **stumm** dazu, einen Patch zu erzwingen (§10.1),
**kann ein überprüftes-aber-bösartiges Release nicht kryptografisch widerrufen**
(§10.2), **reduziert sich unter Eklipse auf OP-2** (§10.3), **lässt den nie
übernehmenden Nutzer durch Entwurf feststecken** (§10.4) und ist **TOFU auf der
ersten Vorstellung von "neuestem"** (§10.5). Die richtige Antwort ist, sie zu
begrenzen — lauter, erlaubnisfreier, dedup-disziplinierter Known-bad-Gossip
(UG-7/UG-8), eine sichtbare Veraltungs-Fläche (UG-5a), außerbandige
First-Update-Bestätigung (UG-9a), selbst-verifizierende Opt-in-Ausführungsverweigerung
für den Neubauer (UG-8b), aggressive Quellenmischung (UG-3a) — und den Patch-Latenz-
Handel in der UI und der Spezifikation **anzugeben**, nicht hinter "kein Auto-Update
ist sicherer" zu verbergen.

## 11. Hier eingeführte Anforderungen

- **UG-1 / UG-1a** — keine Release-Autorität; Übernahme bindet an Reproduktion und
  Aktualität, niemals an Veröffentlichung (wiederholt RB-2 an der Übernahme-Grenze).
- **UG-2 / UG-2a / UG-2b / UG-2c** — erlaubnisfreie Log-Anfügungs-Ankündigung, kein
  Signierer; signiert und unsigniert tragen identisches Übernahme-Gewicht; die
  Release-Linie ist von keiner Partei besessen — `line_id` ist eine
  reproduktions-verifizierbare Manifest-Kette ab einer Genesis, ein Fork ist eine
  sichtbar eigene Linie.
- **UG-3 / UG-3a / UG-3b / UG-3c** — Entdeckung ist nur Pull/Gossip, kein Push;
  quellengemischt, datenschutz-begrenzt, client-getaktet; niemals ein Abruf reaktiv
  auf ein Peer-Signal (das ist das ID-9a-Re-Fetch-Downgrade).
- **UG-4 / UG-4a / UG-4b / UG-4c** — Übernahme ist manuelles Opt-in; eine
  Vier-Tore-Checkliste ohne Signatur-Sperre; eine erklärte konservative Richtlinie;
  Anbieten und Installieren sind mechanisch getrennt ohne automatischen Übergang.
- **UG-5 / UG-5a** — akzeptiere niemals still einen niedrigeren Index
  (reproduzierbarer Downgrade); Veraltung wird auf PS-9 sichtbar gemacht, nicht auf
  sie hin gehandelt (die bewusste Asymmetrie mit ID-9a).
- **UG-6 / UG-6a** — Split-View auf Aktualität gefangen durch per Gossip verbreitete
  Wurzeln + Konsistenzbeweise; Index-Equivocation ist die quer-sichtpunktliche
  Signatur, von Einzel-Sichtpunkt-Downgrade unterschieden und dedupliziert.
- **UG-7** — fünf verpflichtende Release-Anomalien, gegossippt, dedupliziert gemäß
  RB-10a.
- **UG-8 / UG-8a / UG-8b** — Known-bad ist eine erlaubnisfreie, RB-10a-disziplinierte,
  zwanglose Meldung, niemals eine Autorität; eine Meldung der Schwachstellen-Klasse
  annotiert, sperrt aber nie ein Angebot; Widerruf kann nur informieren;
  selbst-verifizierende Opt-in-Ausführungsverweigerung ist autoritätsfrei und erlaubt,
  Ausführungsverweigerung auf externer Evidenz ist verboten.
- **UG-9 / UG-9a** — das erste Update ist erklärtes TOFU über unabhängige Kanäle; eine
  kompromittierte erste Binärdatei kann über Aktualität lügen, nur außerbandig
  bestätigt.

UG-1 und UG-4 sind die tragenden zwei: keine Autorität, und Übernahme ist eine
manuelle Handlung, gebunden an Reproduktion. Beide sind begrenzt, nicht absolut —
UG-1 reduziert sich für den nicht neu bauenden oder eklipsten Client auf OP-2 (§10.2,
§10.3), und das Kein-Push von UG-4 erkauft das Ungepatchte-Flotte-Residuum (§10.1), dessen
schlimmster Fall — ein kompromittierter Client, der beweisbar vielleicht nie vom
Patch erfährt — in voller Stärke benannt statt abgemildert wird. Brich diesen Teil,
indem du einen Push-Pfad benennst, den ein konformer Client hinzufügen DARF (MAY),
einen Signierer, der die Übernahme sperrt, einen Weg, auf dem eine Known-bad-Meldung
eine Handlung erzwingt oder ein ehrliches Release über UG-4b hinaus zensiert, einen
Weg, eine Release-Linie ohne Reproduktion zu verlängern (ein Eigner der Linie), oder
einen Weg, auf dem der nicht neu bauende Client einer Mehrheit vertrauend
zurückgelassen wird, die nicht OP-2 ist. Das ist die Einladung, in der Stimme von
Teil 8.
