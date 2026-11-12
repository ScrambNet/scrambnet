# ScrambNet-Spezifikation — Teil 4: Chamäleon-Transporte
> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../../en/spec/04-chameleon-transports.md)).

**Status: ENTWURF (DRAFT), und der Teil, der am ehesten verrottet.** Dieser Teil
gibt ein Transport-Bedrohungsmodell und eine ehrliche Realismus-Einschätzung an. Er
verpflichtet sich auf keinen nach außen gerichteten Mechanismus und verspricht keinen
Sieg im Zensur-Wettrüsten. Lies zuerst §1 und die Realismus-Einschätzung (§8):
zwischen beiden sagen sie das eine enge Ding, das dieser Teil zu behaupten bereit ist,
und das viel größere, das er verweigert. Strohmann-Werte sind mit `(s)` markiert.

Die Architektur-Schichten L1 (Chamäleon) und L3 (ephemere Transporte) leben hier; der
Transport ist das Ding, das die Bytes eines Anteils an einem Zensor vorbeiträgt.
Dieser Teil ist unter OP-7 (Erreichbarkeit und Bootstrap) abgelegt, und er hängt vom
Zero-Contact-Bootstrap-Problem ab (OP-7, GR-10), statt es zu lösen.

## 1. Die Entscheidung, in zwei Sätzen

- **Dieser Teil behauptet nicht, dass ScrambNet das Zensur-Wettrüsten gewinnt oder
  durchhält.** Er behauptet das Gegenteil über seine eigene Wichtigkeit: Die
  Vertraulichkeits- und Dispersions-Untergrenze (I-2) hängt **überhaupt nicht** von der
  Transportschicht ab. Ein Transport erkauft *Erreichbarkeit* — die Fähigkeit, die
  Bytes eines Anteils zu einem Relais zu bringen —, und Erreichbarkeit darf scheitern,
  die Architektur-Degradations-Leiter hinab (L1→L2→L3→L4) und, bei einer vollständigen
  Abschaltung ohne Mesh-Nachbarn, ganz bis auf null, **ohne dass sich die
  Inhalts-Untergrenze je bewegt** (CT-16).
- **Die ehrliche, verteidigbare Behauptung ist daher eng und darf nicht verbreitert
  werden:** *Wir machen es nicht unmöglich, das Transport-Rennen zu verlieren; wir
  machen es nicht-katastrophal für die Vertraulichkeit, es zu verlieren.* Ein Zensor
  kann die Erreichbarkeit auf null kappen; ein Zensor kann dennoch keinen Inhalt
  unterhalb von `k` Anteilen lesen, weil dieser Schutz nie auf dem Transport ritt
  (CT-16, CT-18, CT-18a).

Alles Folgende ist das Bedrohungsmodell, das diese enge Behauptung rechtfertigt, und
die Realismus-Einschätzung (§8), die ihr Rückgrat ist — der wichtigste Abschnitt des
Teils, kein Anhang.

## 2. Das Transport-Bedrohungsmodell (was der Zensor von 2026 tatsächlich tut)

- **CT-1 (erkläre, was du widerstehst; Schweigen ist ein Zugeständnis). [normativ]**
  Eine konforme Transport-Beschreibung MUSS (MUST) angeben, welche der
  CT-2…CT-7a-Gegner-Fähigkeiten sie zu widerstehen beansprucht und welche sie
  einräumt. Eine nicht deklarierte Fähigkeit wird als eingeräumt behandelt (die
  I-1-Vollständigkeitsregel, für Transporte) — ein Transport, der einen Angriff nicht
  benennt, hat nicht gegen ihn verteidigt.
- **CT-2 (passives DPI / Protokoll-Fingerabdruck).** Der Zensor klassifiziert Flüsse
  nach Byte- und Struktursignaturen, ohne Inhalt zu lesen; die Aufgabe des Chamäleons
  ist es, keine eigene unterscheidende Signatur zu präsentieren (CT-8).
- **CT-3 (TLS-Fingerabdruck-Abgleich). [normativ]** Der Zensor erstellt einen
  Fingerabdruck des TLS-ClientHello. Die Basislinie von 2026 ist **JA4 / JA4+**
  (FoxIO), nicht das ausgemusterte JA3: JA4 **sortiert** Cipher-Suites und Erweiterungen
  vor dem Hashen und ignoriert GREASE, sodass es robust gegen die
  Erweiterungs-Reihenfolge-*Randomisierung* ist, die Mainstream-Browser jetzt vornehmen.
  Eine konforme Nachahmung MUSS (MUST) daher die Cipher-Suite-*Menge*,
  Erweiterungs-*Menge*, ALPN, supported-versions und das GREASE-*Muster* des Ziels
  treffen — nicht bloß ihre Reihenfolge, die JA4 nicht mehr unterscheidet. (Eine
  Nachahmung, die nur die Reihenfolge randomisiert, ist dadurch nicht verborgen.)
- **CT-4 (SNI- / ECH-Inspektion).** Der Zensor liest den Klartext-SNI, um den
  Zielnamen zu erfahren. ECH kann ihn verbergen, aber nur bedingt (CT-11).
- **CT-5 (aktives Sondieren / Connect-back).** Der Zensor verbindet sich mit einem
  verdächtigten Endpunkt und prüft, ob er sich so verhält wie das, was er zu sein
  behauptet; das Überleben erfordert CT-10.
- **CT-6 (passive statistische Klassifikation der Flussform). [normativ,
  Residuum-erklärend]** Der Zensor klassifiziert Flüsse nach *Statistik*, nicht nach
  Bytes: Timing, Volumen, Richtung, Burst-Struktur **und Entropie** — und die
  Merkmalsmenge ist offen und gegner-gewählt, einschließlich gelernter
  (ML-)Klassifikatoren. Insbesondere blockiert **Erkennung von
  "vollständig-verschlüsseltem-Verkehr" hoher Entropie** Flüsse, die *zu zufällig*
  aussehen, ohne Sonde und ohne Fingerabdruck-Treffer (beobachtet an der GFW seit Ende
  2021). Das hat eine kontraintuitive Konsequenz, von der der Rest des Teils abhängt:
  **randomisierte oder hochentropische Tarnung ist ein *helleres* Signal, kein
  dunkleres** — die sicherste Tarnung ähnelt einem sehr verbreiteten echten Protokoll,
  niemals Rauschen. CT-6 kann nicht durch Byte-Level-Nachahmung geschlossen werden
  (CT-8); seine ehrlichen Antworten liegen auf anderen Schichten (CT-12, CT-15).
- **CT-6a (TLS-in-TLS- / verschachtelte-Verschlüsselung-Erkennung). [normativ,
  Residuum-erklärend]** Ein Transport, der ScrambNets eigenen bereits verschlüsselten,
  I-4-uniformen Anteils-Verkehr *innerhalb* eines nachgeahmten äußeren TLS-Flusses
  tunnelt, hinterlässt charakteristische Record-Größen- und Timing-Muster — ein
  TLS-Fluss, der *einen anderen TLS-Handshake trägt* —, die DPI markieren kann, selbst
  wenn der äußere Handshake byte-perfekt ist (CT-3/CT-4 sauber). Das ist der
  Vorzeige-Angriff auf verschachtelte Umgehung und MUSS (MUST) deklariert werden: Eine
  Nachahmung kann beim Handshake perfekt sein und dennoch an der Flussstruktur gefangen
  werden. Es ist ein Residuum, das Byte-Nachahmung nicht schließen kann (es gehört zu
  CT-12); es zu benennen ist von CT-1 verlangt.
- **CT-7 (Endpunkt-Aufzählung — blockieren, was bekannt ist). [normativ]** Der Zensor
  entdeckt und blockiert bekannte Endpunkte/Brücken en gros. Dispersion (CT-15) und
  Brücken-Verteilung über den sozialen Graphen (Architektur L2, Lox) erhöhen die
  Kosten; Nachahmung adressiert die Aufzählung überhaupt nicht.
- **CT-7a (Endpunkt-Entdeckung — die Bootstrap-Frontlinie, als offen deklariert).**
  Verschieden von CT-7: *wie ein zensierter Nutzer überhaupt einen unblockierten
  Endpunkt erlangt, schneller als der Zensor ihn aufzählt.* Das ist das
  Brücken-Verteilungs-Problem (Lox / sozialer Graph) und es reduziert sich auf **OP-7
  (Zero-Contact-Bootstrap), das offen ist.** Teil 4 löst es nicht; er verweist darauf
  (GR-10, OP-7), und jede Behauptung, dass Endpunkte verlässlich entdeckbar seien, ist
  ein ungedecktes Versprechen, das dieser Teil zu machen verweigert.
- **CT-7b (Protokoll-Whitelisting — der Grenzfall).** Der Zensor erlaubt nur eine
  Allow-Liste von Protokollen/Zielen und verwirft den Rest (beobachtet: Irans
  National-Netzwerk-Whitelist, 2025–2026). Dagegen ist die Nachahmung eines *erlaubten*
  Ziels der einzige Zug, und selbst er scheitert, wenn der Zensor die Kollateralkosten
  akzeptiert (§8, CT-14) — bis hin zu einer vollständigen Abschaltung, bei der kein
  Transport irgendetwas erreicht (CT-18a).

## 3. Nachahmungs-Disziplin (die Tretmühle, normativ gemacht)

- **CT-8 (keine statische Projekt-Signatur; imitiere wie-bereitgestellt). [normativ]**
  Ein Chamäleon-Transport DARF NICHT (MUST NOT) eine statische, projektspezifische
  Draht-Signatur präsentieren, und MUSS (MUST) ein Zielprotokoll *so, wie es
  tatsächlich bereitgestellt ist*, imitieren, nicht ein idealisiertes. Ein
  handgestrickter oder eingefrorener Stack ist selbst ein Fingerabdruck und ist nicht
  konform.
- **CT-9 (die uTLS-Drift-Klausel). [normativ]** Eine Nachahmung im uTLS-Stil MUSS
  (MUST) dem *aktuell bereitgestellten* ClientHello des Ziels folgen und MUSS (MUST)
  die Zielversion angeben, die sie nachahmt (CT-20). Gegen JA4 (CT-3) ist der
  Unterscheider die Divergenz in den Cipher- und Erweiterungs-*Mengen*, ALPN,
  supported-versions und dem GREASE-Muster — diese driften mit jedem Browser-Release,
  sodass eine bei Version N eingefrorene Nachahmung zu einem Unterscheider wird, sobald
  die reale Population zu N+1 wechselt. Das ist eine **Wartungs-Tretmühle ohne
  Endzustand**: Es gibt keine Version, bei der die Arbeit getan ist (§8). Die
  Untergrenze DARF NICHT (MUST NOT) davon abhängen, mit ihr Schritt zu halten (CT-16).
- **CT-9a (bevorzuge ein populationsstarkes Ziel — aus Gründen der Anonymitätsmenge,
  nicht aus ökonomischen). [normativ]** Eine konforme Bereitstellung SOLLTE (SHOULD)
  ein populationsstarkes, schnell-bewegliches Ziel (das TLS eines Mainstream-Browsers)
  statt eines Nischen-Ziels nachahmen, aus zwei *mechanischen* Gründen: Die große Herde
  ist eine bessere Anonymitätsmenge (mehr echte Flüsse, unter denen man sich versteckt),
  und ein schnell-patchendes Ziel verkürzt das CT-9-Veraltungs-Fenster. Diese Klausel
  macht **keine** ökonomische Behauptung, dass die Herde "zu teuer zu blockieren" sei —
  diese Wette ist CT-13, als widerlegbar deklariert, und der Rekord von 2026 (ein
  nationaler Zensor blockierte die größte ECH-Herde, §8) zeigt, dass sie verloren
  werden kann.

## 4. Überleben aktiver Sonden

- **CT-10 (überlebe eine Connect-back-Sonde; Schweigen ist selbst ein Fingerabdruck).
  [normativ]** Ein Chamäleon-Endpunkt MUSS (MUST) eine aktive Sonde überleben: Er MUSS
  (MUST) einen *echten*, gültigen Handshake des Protokolls, das er imitiert,
  vollständig ausführen und einem nicht authentifizierten Sondierer plausibles
  Tarn-Verhalten servieren (z. B. echte TLS-Terminierung, die zu echt-aussehendem
  Inhalt proxyt), und den verdeckten Dienst nur einem Client offenbaren, der ein
  vorab geteiltes Geheimnis nachweist. Das moderne Modell ist
  echtes-TLS-terminieren-und-zu-einer-echten-Seite-proxyen, **nicht** das ältere
  Schweige-Modell: *einem nicht authentifizierten Sondierer gegenüber zu schweigen ist
  selbst ein erkennbares Verhalten* (charakteristische Timeouts,
  Byte-Akzeptanz-Schwellen, Replay-Behandlung) und ist nicht konform.
- **CT-10a (das vorab geteilte Geheimnis ist eine Brücken-Linie — seine Verteilung ist
  offen). [normativ]** Das Geheimnis, das in CT-10 einen echten Client von einem
  Sondierer unterscheidet, ist eine **Brücken-Linie**, und **seine Verteilung ist OP-7
  / GR-10, als offen deklariert.** CT-10 setzt ein bereits ausgeliefertes Geheimnis
  voraus; es löst die Auslieferung **nicht**. Sonden-Widerstand und Bootstrap sind
  getrennte Probleme, und sie zu vermengen (anzunehmen, das Geheimnis sei irgendwie
  bereits überall) ist der Fehler, den CT-7a verbietet.
- **CT-10b (die Kosten dünnen den Betreiber-Pool aus).** Echter Tarn-Inhalt, echte
  Zertifikate und echte Terminierung sind eine stehende operative Last pro Endpunkt.
  Diese Hürde anzuheben ist genau das, was den Freiwilligen-Betreiber-Pool schrumpfen
  lässt — was das Dauer-Wartungs-Problem (§8) mit operativem Hut ist.

## 5. ECH-Haltung (keine Überbehauptung)

- **CT-11 (ECH ist opportunistisch und verfügbarkeits-begrenzt, niemals eine
  Untergrenze). [normativ]** Eine konforme Beschreibung DARF NICHT (MUST NOT) ECH
  (Encrypted Client Hello) als gelöste SNI-Verteidigung präsentieren. Sie gibt an: (a)
  ECH verbirgt den SNI nur dort, wo der Fronting-Provider es bereitstellt, der Client
  es unterstützt **und die verschlüsselte DNS-Abfrage, die die ECH-Konfiguration
  trägt, gelingt** — blockiere oder degradiere dieses DNS und ECH greift stillschweigend
  nicht, was der tatsächliche Fehlermodus von 2026 ist; (b) die serverseitige
  Bereitstellung von 2026 ist ein *Minderheits-aber-wachsender* Anteil, konzentriert
  bei wenigen großen Fronting-Providern, nicht im Long Tail, sodass "der SNI ist
  verborgen" für die meisten Ziele die meiste Zeit falsch ist; (c) **"ECH vollständig
  blockieren" ist eine beobachtete Zensor-Reaktion** (ein nationaler Zensor blockierte
  ab Ende 2024 ECH-Verbindungen zu einem großen Provider), der ECH konstruktionsbedingt
  nichts entgegensetzen kann. ECH ist eine opportunistische Verbesserung, keine
  Garantie. *(Die ECH-Spezifikation ist die ESNI/ECH-Arbeit der IETF-TLS-Arbeitsgruppe;
  dieser Teil fixiert keine veröffentlichte RFC-Nummer, die bei der Entwurfserstellung
  noch nicht bestätigt war — zitiere das aktuelle Dokument, nicht eine Nummer, die
  falsch sein könnte.)*
- **CT-11a (degradiere, lecke nicht). [normativ]** Wo ECH nicht verfügbar oder
  blockiert ist, MUSS (MUST) ein konformer Transport zur nächsten Sprosse der Leiter
  (L2 ephemere Brücken) degradieren, statt auf einen unterscheidbaren
  Klartext-SNI-Fluss zurückzufallen. Der Degradations-Pfad, nicht ECH, ist die
  Garantie.

## 6. Das Fluss-Korrelations-Residuum

- **CT-12 (Nachahmung kann die Flussform nicht besiegen; sag es). [normativ,
  Residuum-erklärend]** Von Byte-Level-Nachahmung DARF NICHT (MUST NOT) behauptet
  werden, dass sie Flussform-Korrelation (CT-6), verschachtelte-TLS-Erkennung (CT-6a)
  oder einen globalen passiven Beobachter, der Eintritt und Austritt korreliert,
  besiegt. Timing, Volumen, Richtung, Burst-Struktur und Verschachtelung lecken durch
  eine perfekte Nachahmung. Das sind Residuen, die Nachahmung *nicht* schließen kann,
  und sie MÜSSEN (MUST) deklariert, nicht verborgen werden. Die einzigen ehrlichen
  Antworten liegen auf anderen Schichten — Dispersion verteilt die Form einer Nachricht
  über Cover (CT-15, eine *Verfügbarkeits*-Eigenschaft, keine formverbergende) und das
  Mixing im Paranoia-Modus (Architektur L2) tauscht Latenz gegen Form-Widerstand —
  niemals die Nachahmung selbst. Website-Orakel- und eintrittsseitige
  Bestätigungs-Angriffe reduzieren sich auf dasselbe Korrelations-Residuum und die
  Zeile des globalen passiven Gegners, die das Bedrohungsmodell bereits als außerhalb
  des Fast-Mode-Geltungsbereichs deklariert.

## 7. Anteils-Dispersion über diverse Cover (das normative Urteil)

- **CT-15 (das Urteil: Diversität hilft der Verfügbarkeit, schadet der
  Unbeobachtbarkeit; kaufe das Erste, bezahle und deklariere das Zweite). [normativ]**
  Die `n` Anteile einer Nachricht über *verschiedene Cover-Typen* zu tragen (einen in
  TLS, einen in WebRTC, einen im Mesh) ist eine zweiseitige Entscheidung, wie folgt
  aufgelöst:
  (a) Es DARF NICHT (MUST NOT) angenommen werden, dass sie die **Unbeobachtbarkeit**
  verbessert — `n` Cover sind `n` Fingerabdrücke, die man richtig treffen muss (CT-3),
  `n` Tretmühlen (CT-9), und ein wahrhaft neuer Schaden: eine
  **Cover-übergreifende Korrelationsfläche**. Ein Gegner, der einen TLS-Fluss, einen
  WebRTC-Fluss und einen Mesh-Burst sieht, die timing-/volumen-korreliert sind (CT-6),
  kann sie als die Anteile einer Nachricht verknüpfen, *ohne irgendeine einzelne
  Nachahmung zu brechen* — Diversität dimmt dieses Signal nicht, sie kann es
  aufhellen;
  (b) Sie ist erlaubt und wird geschätzt **strikt als eine Verfügbarkeits-Maßnahme**:
  Keine einzelne Cover-Blockade tötet die Zustellung (`k < n` erkauft dies bereits),
  und die Endpunkt-Aufzählung (CT-7) muss nun gegen Cover *einzeln* gelingen — was die
  Kosten des Zensors gegen einen Zensor erhöht, der Cover *eins nach dem anderen*
  blockiert, und **keinen** Nutzen gegen eine Protokoll-Whitelist (CT-7b) oder eine
  vollständige Abschaltung (CT-18a) bietet, die alle Cover in einem einzigen Akt
  blockieren.
- **CT-15a (verkaufe es als Erreichbarkeit, niemals als Tarnung). [normativ]** Ein
  konformer Client DARF NICHT (MUST NOT) dem Nutzer die Multi-Cover-Dispersion als
  *stärkere Tarnung* präsentieren; er DARF (MAY) sie als *stärkere Erreichbarkeit*
  präsentieren. Die beiden zu vermengen ist derselbe
  Verknüpfung-gegen-Inhalt-Kategorienfehler, den ID-12a für die Karte verbietet, für
  Transporte wiederholt: Multi-Cover verbessert eine Verfügbarkeits-Eigenschaft und
  verbessert keine Nachahmungs-Eigenschaft.
- **CT-15b (minimale Cover-Menge offen gelassen; Behauptungen durch das Tatsächlich-
  Betriebene begrenzt). [normativ]** Teil 4 schreibt **keine** minimale Cover-Menge vor
  — `n` Cover vorzuschreiben schreibt `n` Wartungs-Tretmühlen vor, die das Projekt
  vielleicht nicht besetzen kann (§8). Ein Client mit einer offenen/nicht spezifizierten
  Cover-Menge DARF NICHT (MUST NOT) irgendeine *quantitative*
  Verfügbarkeits-Eigenschaft behaupten (kein "widersteht der Aufzählung über N Cover"
  ohne ein angegebenes, tatsächlich betriebenes N); er DARF (MAY) nur das *qualitative*
  "keine einzelne Cover-Blockade tötet die Zustellung" behaupten, und nur, wenn er
  tatsächlich ≥2 unabhängige Cover mit `k < n` betreibt. Ob ≥2 Cover für den
  Standard der dispergierten Zustellung zu verlangen sind, ist eine Eigner-Entscheidung
  (§8).

## 8. Die ehrliche Realismus-Einschätzung (das Rückgrat)

*(Dieser Abschnitt ist der Teil, kein Anhang. Er ist in der §Residuum-Stimme der
Teile 8 und 11 geschrieben.)*

**Dieser Teil verpflichtet sich auf keinen nach außen gerichteten Mechanismus und
darf nicht so tun.** Er ist ein Urteil darüber, wo das Projekt fragil ist, in voller
Stärke angegeben: **Die Transportschicht ist die schwächste und am-ehesten-verrottende
Schicht des Projekts, und die ehrliche Haltung ist, es zu sagen und so zu entwerfen,
dass die Untergrenze nie von ihr abhängt.**

**Die uTLS-Drift-Tretmühle (CT-9).** Eine bei einer Browser-Version eingefrorene
Nachahmung wird in dem Moment zu einem Unterscheider, in dem die reale Population
weiterzieht — eine kleinere, veraltetere Herde ist ein *helleres* Signal, kein
dunkleres. Es gibt keine Version, bei der die Arbeit getan ist. Gegen JA4 zählt die
Reihenfolge nicht mehr, aber die Cipher-/Erweiterungs-*Mengen* driften weiterhin mit
jedem Release, sodass die Tretmühle langsamer ist als sie gegen JA3 war, aber nicht
stoppt. Das Projekt bekommt nicht die Chance, dies zu gewinnen; es bekommt die Chance,
darauf zu laufen oder davon abzusteigen, und CT-16 ist die Entscheidung, das Absteigen
überlebbar zu machen.

**ECHs Realität von 2026 (CT-11).** ECH verbirgt den SNI nur dort, wo Provider, Client
*und die verschlüsselte DNS-Abfrage* alle gelingen, und 2026 ist das eine Minderheit
der Ziele. "ECH vollständig blockieren" ist bereits von einem nationalen Zensor gegen
den größten Fronting-Provider eingesetzt worden, dem ECH nichts entgegensetzen kann.
ECH ist eine opportunistische Verbesserung, begrenzt durch die Bereitstellung; die
Untergrenze ist der Degradations-Pfad, niemals ECH.

**Das ökonomische Argument und seine Gegenbeispiele (CT-13/CT-14).** "Mich zu
blockieren kostet mehr, als es einbringt" ist ein echtes Abschreckungsmittel und eine
falsche Garantie. Der Rekord von 2026 hat wiederholte Gegenbeispiele von Zensoren, die
große Kollateralkosten zahlen, statt Umgehung zu erlauben: eine nationale
Regulierungsbehörde, die ECH zu einem großen Provider blockiert (ab Ende 2024); eine
National-Netzwerk-**Protokoll-Whitelist**, die nur eine kurze Allow-Liste erlaubt
(Iran, 2025–2026); und **totale Internet-Abschaltungen** während Unruhen (Iran, Mitte
2025 und erneut Anfang 2026). Jedes ist ein Zensor, der Kontrolle über Kommerz wählt.
Die ökonomische Wette ist probabilistisch: Sie funktioniert gegen einen Zensor, der
das Kollateral schätzt, und scheitert gegen einen, der gezeigt hat, dass er es nicht
tut. Wir geben dies an, statt die Ökonomie als abgeschlossen wegzuwinken. *(Diese sind
als Kategorien beobachteten Verhaltens zitiert; eine konforme Niederschrift sollte
Daten und Jurisdiktionen beifügen und MUSS (MUST) jedes Gegenbeispiel fallen lassen,
hinter dem sie nicht stehen kann — ein falsches Gegenbeispiel ist schlimmer als
keines, CT-14.)*

**Die unbequeme Frage, beantwortet (das zentrale deklarierte Residuum).** *Hat ein
pseudonymes Freiwilligen-Projekt die Dauer-Wartungs-Kapazität, die ein
Transport-Wettrüsten verlangt?* Tor hat bezahltes Personal, ein finanziertes
Pluggable-Transport-Ökosystem und Jahre institutionellen Gedächtnisses, und es
verliert *dennoch* Runden gegen entschlossene Zensoren. Ein pseudonymes
Projekt-ohne-Namensliste — eines, das per Entwurf (I-3 und die Governance der Teile
10/11) die zentrale Koordination verweigert, die es ihm erlauben würde, ein
Transport-Update allen auf einmal zu pushen — hat **weniger** dieser Kapazität, nicht
mehr. Die ehrliche Antwort ist daher **nein, nicht verlässlich.** Das
Transport-Wettrüsten belohnt genau die finanzierte, koordinierte,
identitäts-gebundene Wartung, die das Projekt aus prinzipiellen Gründen entsagt hat.
Wir sollten erwarten, dass die Nachahmungs-Schicht zurückfällt.

**Und darum sitzt nichts Tragendes auf ihr.** Die Wartungs-Kapazität, um ein
Transport-Wettrüsten zu gewinnen, ist genau das, was wir nicht haben, und genau das,
was die Untergrenze nicht verlangt. Wir erwarten, dass die Nachahmungs-Schicht
zurückfällt; die Architektur ist eine Wette, dass sie es darf — dieselbe Wette, die
die Architektur bereits für den Onion-Gürtel macht ("wenn diese ganze
Berechnungsschicht eines Tages fällt, wird das Netzwerk nicht lesbar — es wird weniger
bequem") und die die Teile 10/11 für Updates machen (verweigere den Push, bezahle die
Latenz, gib es an). Das ist ehrlicher Pessimismus über eine Kapazität, die uns fehlt,
umgewandelt in die Entwurfs-Begründung, die den Fehlbetrag nicht-katastrophal macht —
nicht Defätismus.

**Der Boden der Leiter, eingeräumt (CT-18a).** Die Degradations-Leiter L1→L2→L3→L4 hat
einen Boden, und der Boden hat einen Boden. Bei einer **vollständigen Abschaltung ohne
physischen Mesh-Nachbarn in Reichweite** erreicht kein Transport irgendetwas und
**keine Nachricht wird zugestellt — Punkt.** Wir machen *das* nicht überlebbar. Die
I-2-Inhalts-Untergrenze hält immer noch (nichts wird *offenbart*; was nicht gesendet
werden kann, kann nicht gelesen werden), aber die Erreichbarkeit ist null, und die
Untergrenze ist an diesem Punkt *intakt und nutzlos*: perfekte Vertraulichkeit einer
Nachricht, die das Gerät nicht verlassen kann. Die ehrliche Behauptung ist nicht
"Kommunikation kommt immer durch" — sie ist "Vertraulichkeit hängt nie vom Transport
ab, und wenn der Transport stirbt, stirbt das Geheimnis mit ihm, unzugestellt, nicht
offengelegt." Ein Mesh-Knoten in einem heißen Blackout ist selbst ein physisch
lokalisierbarer Akt (Teil 5, OP-6), sodass selbst die letzte Sprosse ein
ausdrückliches, gefährliches Opt-in ist, keine Garantie.

## 9. Der Invariantenschutz

- **CT-16 (die Untergrenze hängt nicht vom Gewinnen des Rennens ab; Vertraulichkeit ≠
  Verfügbarkeit). [normativ]** Keine Vertraulichkeits- oder Dispersions-Garantie (I-2)
  MUSS (MUST) vom Gelingen irgendeines Chamäleon-Transports, vom Aktuell-Bleiben einer
  Nachahmung (CT-9), von der Verfügbarkeit von ECH (CT-11) oder vom Halten des
  ökonomischen Arguments (CT-14) abhängen. Transporte erkaufen **nur Erreichbarkeit**.
  I-2 garantiert **Vertraulichkeit** (Inhalt unterhalb von `k` ist unlesbar), eine
  *zugestellt-gegen-unzugestellt*-Eigenschaft, die darüber schweigt, ob überhaupt
  etwas zugestellt wird — **keine** lesbar-gegen-unlesbar-Garantie der Zustellung.
  Transport-Versagen MUSS (MUST) die Leiter hinab degradieren (L1→L2→L3→L4), und am
  Boden auf null Erreichbarkeit (CT-18a), **niemals** indem es Inhalt unterhalb von `k`
  kompromittiert. Ein Entwurf, in dem das Verlieren des Transport-Rennens die
  Untergrenze verliert, ist nicht konform.
- **CT-17 (minimiere die Abhängigkeit; versprich nicht zu gewinnen). [normativ]** Eine
  konforme Haltung MUSS (MUST) die Abhängigkeit der Untergrenze von Nachahmung
  minimieren, statt zu versprechen, sie aufrechtzuerhalten. Wo Nachahmung und
  Degradation beide einer Bedrohung begegnen, MUSS (MUST) der Teil den
  Degradations-Pfad als die Garantie bevorzugen und die Nachahmung als die
  Bequemlichkeit behandeln (die eigene Maxime der Architektur: Alles, was ablaufen
  kann, ist eine Bequemlichkeit).
- **CT-18 (die deklarierte Obergrenze: keine Wettrüsten-Sieg-Behauptung). [normativ]**
  Teil 4 DARF NICHT (MUST NOT) behaupten, dass ScrambNet das Zensur-Wettrüsten gewinnt
  oder durchhält. Die einzige Behauptung, die er macht, ist die von CT-16: Die
  Transportschicht *darf verlieren*, ohne dass die Untergrenze verliert. Jeglicher
  Text, UI oder README, der Unbesiegbarkeit auf Transport-Ebene, einen "nachhaltigen"
  Wettrüsten-Sieg oder ECH-als-gelöst behauptet, ist nicht konform und MUSS (MUST)
  korrigiert werden — einschließlich der Nationaler-Zensor-Zeile des Bedrohungsmodells,
  die dieser Teil revidiert, um *Erreichbarkeit* (umkämpft, kann auf null fallen) von
  *Inhalt* (bedingungslos geschützt, unabhängig vom Transport) zu trennen.
- **CT-18a (der Terminalfall wird angegeben, nicht verborgen). [normativ]** Eine
  konforme Niederschrift MUSS (MUST) den Terminalfall von CT-18 ausdrücklich angeben:
  Bei einer vollständigen Abschaltung ohne Mesh-Reichweite ist die Erreichbarkeit null
  und keine Nachricht wird zugestellt; die Inhalts-Untergrenze hält, ist aber für diese
  unzugestellte Nachricht nutzlos. "Wir machen das Verlieren des Transport-Rennens
  überlebbar *für die Vertraulichkeit*, nicht für die Zustellung" ist die exakte
  Behauptung, und nichts darf so formuliert werden, dass es impliziert, die Zustellung
  sei garantiert.

## 10. Operative Ehrlichkeitsfläche

- **CT-19 (mache die Transport-Haltung ehrlich sichtbar). [normativ]** Ein konformer
  Client MUSS (MUST) seine aktuelle Transport-Haltung auf der bestehenden
  Ehrlichkeitsfläche (PS-9) sichtbar machen: welches Cover er nutzt, ob ECH
  *tatsächlich* in Kraft ist (nicht bloß versucht), und dass die
  Transport-Erreichbarkeit — anders als die I-2-Untergrenze — **keine** Garantie trägt
  und auf null scheitern kann. Die Botschaft, die die UI angibt: *deine
  Inhalts-Untergrenze hält; deine Fähigkeit, das Netzwerk zu erreichen, nicht.*
- **CT-20 (deklariere die Nachahmungs-Veraltung). [normativ]** Eine konforme
  Bereitstellung SOLLTE (SHOULD) angeben, wie aktuell ihr Nachahmungs-Ziel ist (CT-9),
  das Transport-Analogon zur gemessenen Fehlerrate der Karte (ID-12), sodass der Nutzer
  und der Simulator eine veraltete Nachahmung als den Fingerabdruck behandeln können,
  der sie ist, statt ihr stillschweigend zu vertrauen.

## 11. Ein erkundetes und verworfenes Design: der polymorphe QUIC-Transport

Dieser Abschnitt hält ein konkretes Transport-Design fest, das architektiert,
rotgeteamt und **verworfen wurde, bevor irgendein Mechanismus festgelegt war**. Es
wird aufbewahrt, nicht gelöscht, aus demselben Grund, aus dem der Inferenz-Datensatz
PS-11/PS-12 und ID-8a aufbewahrt: Ein angegriffenes und fallengelassenes Design ist
ein Ergebnis, und festzuhalten, *warum* es scheiterte, hält das Projekt — und den
nächsten Leser — davon ab, es erneut vorzuschlagen. Keine der `CT-n` unten ist
normativ; das Design wird nicht ausgeliefert. Die drei Fehlschläge wurden gegen
Primärquellen verifiziert, nicht behauptet.

**Das Design.** Ein *polymorpher* Transport, dessen Polymorphismus eine **Auswahl
über eine kleine Menge echter, wie-bereitgestellter Templates verbreiteter Protokolle**
ist (niemals Per-Byte-Randomisierung — CT-6 macht Zufälligkeit bereits zu einem
helleren Signal), wobei die Nachahmungs-Zielklasse **QUIC / HTTP-3** sein sollte: ein
populationsstarkes Datagramm-Protokoll, unter der Prämisse, dass das Verstecken in der
QUIC-Menge die Entropie-Heuristik umgeht und dass eine aus einem vorab geteilten
Brücken-Geheimnis abgeleitete Pro-Verbindungs-Template-Auswahl dem Template-Pinning
widersteht. Der Endpunkt wäre ein **echter H3-Origin**, betrieben vom Betreiber, sodass
eine aktive Sonde (CT-5) auf eine echte Website trifft und nichts Verdecktes erfährt
(CT-10-Modell).

**Warum es verworfen wurde — drei Fehlschläge, jeder verifiziert:**

- **Die Entropie-Umgehungs-Begründung ist ein Kategorienfehler über einer falschen
  Prämisse.** Der "Vollständig-verschlüsselter-Verkehr"-Detektor, den sie zu umgehen
  behauptete (USENIX Security 2023, Wu et al.), operiert auf dem **ersten TCP-Paket**
  (ein Bits-pro-Byte-Popcount-Test und Regeln für druckbare-ASCII-Präfixe); er ist kein
  QUIC-Detektor, sodass ein QUIC-Transport ihn weder umgeht noch umgehen muss. Und die
  Unter-Prämisse — "echtes QUIC ist bereits hochentropisch, also mischen wir uns
  darunter" — ist falsch für genau den Teil, den ein billiger Klassifikator zuerst
  liest: QUIC-v1-Header-Schutz maskiert nur die niederwertigen Bits des ersten Bytes
  und die Paketnummer (RFC 9001 §5.4), während die **Version** des Long-Headers (die
  feste `0x00000001` in 2026), die Längen-Bytes der Connection-ID und die Token-Länge
  **Klartext** sind, und die Nutzlast des Initial-Pakets ist AEAD-versiegelt unter einem
  Schlüssel, der aus einem **öffentlichen** Salt und der Klartext-Destination-Connection-ID
  abgeleitet wird (RFC 9001 §5.2) — sodass jeder Beobachter den ClientHello entschlüsseln
  kann. Ein QUIC-Initial ist eine **reiche Fingerabdruck-Fläche**, keine Wand aus
  Zufallsbytes. Die reale QUIC-Bedrohung ist Initial-/ClientHello-Fingerabdruck (die
  JA4-Familie, einschließlich ihrer QUIC-Variante, plus Transport-Parameter), die CT-3
  bereits benennt — nicht Entropie.

- **Der verdeckte Selektor überlebt ein Paket.** Die Template-Auswahl aus der
  QUIC-Destination-Connection-ID abzuleiten, die der Client wählt, war undurchführbar:
  RFC 9000 §7.2 verlangt, dass diese erste Client-DCID **"ein Wert, der nicht
  vorhergesagt werden kann"** ist (das Gegenteil einer deterministischen
  Schlüsselableitung), mindestens 8 Bytes lang, und der Client nutzt sie **nur, bis der
  Server antwortet** — nach dem ersten Initial des Servers (und sofort bei einem Retry,
  noch bevor der Handshake überhaupt abgeschlossen ist) ist die Connection-ID
  server-gewählt. Ein Pro-Verbindungs-Selektor, der in einem Feld lebt, das das
  Protokoll innerhalb eines Roundtrips überschreibt, ist kein Selektor. (Ein vorab
  geteiltes Geheimnis gibt beiden Parteien den Template-Index bereits; ihn durch ein
  beobachtbares Feld zu routen brachte nichts ein und riskierte eine Abweichung vom
  wie-bereitgestellten QUIC, die selbst ein Fingerabdruck unter CT-8 ist.)

- **QUIC / UDP ist das *erste*, was ein nationaler Zensor blockiert, und das billig.**
  Dies ist der entscheidende, weil er genau den Nutzer betrifft, für den dieses Netzwerk
  existiert. Russland ließ am 2022-03-04 **sämtliches** internationales QUIC mit einem
  UDP/443-Filter fallen (erstes Paket ≥ 1001 Bytes, das den QUIC-v1-Versions-Header
  trägt → das 4-Tupel für 420 s verworfen), später verengt auf QUIC-SNI-Filterung, in
  2026 noch aktiv; Iran ging in einem Pre-Shutdown-Scan von 2025 von einer blockierten
  QUIC-Domain auf rund neuntausend (≈ 100 %) über vollständige UDP-Initial-Verwürfe.
  Weil Browser automatisch auf TCP zurückfallen, trägt das Blockieren von UDP/443 fast
  kein Kollateral — also wird es **früh** getan. QUIC zu wählen tauscht daher einen
  nicht-existenten Gewinn gegen die Entropie-Heuristik gegen einen *schnelleren* realen
  Verlust gegen UDP-Blockierung und Protokoll-Whitelisting (CT-7b) ein. QUIC ist nicht
  unbrauchbar — QUIC v2 umgeht Russlands Nur-Version-1-Filter, und die H3-Herde ist real
  —, aber es ist bestenfalls **ein als widerlegbar deklariertes Template aus Gründen der
  CT-9a-Herdengröße, dort, wo UDP nicht bereits verworfen wird**, niemals der Anker. Ein
  TCP/HTTP-2-Nachahmer eines erlaubten Ziels überlebt strikt mehr der Regimes, für die
  dieser Teil geschrieben ist.

**Drei Residuen, die das QUIC-Design überlebten und jeden künftigen polymorphen
Transport binden, QUIC oder nicht:**

- **Mengenzugehörigkeit ist eine Handshake-Eigenschaft, niemals eine Fluss-Eigenschaft
  — und darf niemals als Tarnung verkauft werden.** "In der Menge stehen" verbirgt die
  Handshake-Bytes; es verbirgt **nicht** die Flussform (Paketgrößen-Sequenz, Timing,
  Burst-Struktur, Pro-Nachricht-`n`-Anteils-Volumen), die ScrambNet-förmig bleibt und
  genau das ist, worauf CT-6 / CT-12 klassifizieren. Jede Behauptung, dass
  Mengenzugehörigkeit einen Fluss unbeobachtbar macht, ist die Tarnungs-Überhöhung, die
  CT-15a verbietet, in einem neuen Kostüm.

- **Die Echte-Website-Sonden-Antwort ist nicht nur eine Pool-Ausdünnungs-Kosten
  (CT-10b); sie ist eine neue Deanonymisierungs-Fläche und eine neue rechtliche Fläche.**
  Die öffentliche Seite eines Betreibers und ihr verdeckter Kanal teilen eine Adresse,
  ein Zertifikat, einen Endpunkt, sodass Verdeckt-Last-Stau die öffentliche Seite in ein
  Timing-Orakel auf den Betreiber verwandelt (das Problem der nicht-rotierbaren Identität
  von BL-18a, das auf der Transportschicht wiederkehrt), und der Betrieb echter
  gehosteter Inhalte trägt eine Missbrauchs-/Takedown-Exposition, die die
  "trägt-Pakete-keine-Meinungen"-Haltung des Bedrohungsmodells und von OPERATORS.md nicht
  abdeckt. Beide MÜSSEN von jedem Design deklariert werden, das eine Sonde mit einem
  echten Dienst beantwortet.

- **Pro-Verbindungs-Auswahl über eine kleine Template-Menge ist selbst ein
  Populations-Ebene-Fingerabdruck.** Eine uniforme `1/T`-Wahl über `T` Templates passt
  nicht zur marktanteils-verzerrten, geografisch und zeitlich variierenden Verteilung
  realer Client-Stacks, sodass die *Auswahl-Verteilung* — lernbar durch Aggregation
  vieler Verbindungen — zur ScrambNet-Signatur wird, die der Polymorphismus entfernen
  sollte. Ein künftiges Design MUSS (MUST) die Mischung zur realen Population hin
  gewichten und dennoch das Residuum deklarieren, dass die gewichtete Mischung eine
  globale Konstante über Clients hinweg ist, die Nachahmung nicht schließen kann.

Das nützliche negative Resultat ist dasselbe, das das Bedrohungsmodell bereits trägt:
Die bindende Beschränkung der Erreichbarkeit dieses Netzwerks ist nicht die
Handshake-Tarnung, sondern **Endpunkt-Entdeckung und -Aufzählung (CT-7 / CT-7a →
OP-7)**, die keine Transport-Nachahmung adressiert. Ein perfektes Chamäleon kommt
dennoch an einer Adresse an, die ein Zensor erlernen und en gros blockieren kann. Das
ist die Bootstrap-Frontlinie, als offen deklariert.

## 12. Hier eingeführte Anforderungen

- **CT-1 / CT-2 / CT-3 / CT-4 / CT-5** — erkläre-was-du-widerstehst; passives DPI;
  JA4-TLS-Fingerabdruck (Mengen + GREASE, nicht Reihenfolge); SNI/ECH-Inspektion;
  aktives Sondieren.
- **CT-6 / CT-6a** — passive statistische/Entropie-/ML-Flussklassifikation
  (Zufälligkeit ist ein helleres Signal); TLS-in-TLS-verschachtelte-Erkennung — beide
  Residuen, die Nachahmung nicht schließen kann.
- **CT-7 / CT-7a / CT-7b** — Endpunkt-Aufzählung gegen Endpunkt-*Entdeckung* (die
  OP-7-Bootstrap-Frontlinie, als offen deklariert); Protokoll-Whitelisting.
- **CT-8 / CT-9 / CT-9a** — keine statische Signatur; die uTLS-Drift-Tretmühle;
  bevorzuge ein populationsstarkes Ziel aus Gründen der Anonymitätsmenge, kein
  ökonomisches Versprechen.
- **CT-10 / CT-10a / CT-10b** — überlebe eine Sonde mit echtem Cover (Schweigen ist ein
  Fingerabdruck); das vorab geteilte Geheimnis ist eine Brücken-Linie, deren Verteilung
  OP-7 ist; die Kosten dünnen den Betreiber-Pool aus.
- **CT-11 / CT-11a** — ECH ist opportunistisch, DNS-abhängig, Block-ECH-beobachtet,
  keine Untergrenze; degradiere, statt Klartext-SNI zu lecken.
- **CT-12** — Nachahmung kann die Flussform/Verschachtelung/Korrelation nicht besiegen;
  die Antworten liegen auf anderen Schichten, niemals in der Nachahmung.
- **CT-15 / CT-15a / CT-15b** — Multi-Cover-Dispersion hilft der Verfügbarkeit, schadet
  der Unbeobachtbarkeit, fügt eine Cover-übergreifende Korrelationsfläche hinzu;
  verkaufe sie als Erreichbarkeit, nicht als Tarnung; Behauptungen durch tatsächlich
  betriebene Cover begrenzt.
- **CT-16 / CT-17 / CT-18 / CT-18a** — die Untergrenze hängt nie vom Transport ab;
  Vertraulichkeit ≠ Verfügbarkeit; keine Wettrüsten-Sieg-Behauptung; der
  Null-Erreichbarkeits-Terminalfall angegeben, nicht verborgen.
- **CT-19 / CT-20** — ehrliche Transport-Haltung auf PS-9; deklarierte
  Nachahmungs-Veraltung.

CT-16 und CT-18 sind die tragenden zwei: Die Untergrenze hängt nicht vom Gewinnen des
Transport-Rennens ab, und der Teil macht keine Behauptung, dass das Rennen gewonnen
ist. Die Transportschicht ist diejenige, auf der das Projekt erwartet, Runden zu
verlieren, und sie ist so architektiert, dass das Verlieren von ihnen *Erreichbarkeit*
kostet, niemals *Vertraulichkeit* — bis hinab zum Terminalfall, in dem die
Erreichbarkeit null ist und das unzugestellte Geheimnis immer noch ein Geheimnis ist
(CT-18a). Brich diesen Teil, indem du eine Zensor-Fähigkeit benennst, die CT-2…CT-7b
verfehlt, eine Klausel, die verspricht, das Wettrüsten über CT-18 hinaus zu gewinnen
oder durchzuhalten, eine Stelle, an der die I-2-Untergrenze vom Gelingen eines
Transports abhängig gemacht wird, oder einen Weg, auf dem Multi-Cover-Dispersion über
CT-15a hinaus als Tarnung verkauft wird. Das ist die Einladung, in der Hausstimme.
