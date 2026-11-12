# ScrambNet-Spezifikation — Teil 5: Blackout und Link-Diversität im gemischten Mesh
> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../../en/spec/05-blackout-mesh.md)).

**Status: ENTWURF (DRAFT), und ein deklariertes Forschungsrisiko.** Dies ist der
größte ungeschriebene Entwurf im Projekt, und dieser Teil liefert — wie es die
Roadmap erlaubt — ein *partielles* Ergebnis: ein solides Modell gemischter Netze und
eine einzige wahrhaft tragende Idee (Dispersion über unabhängige Gateways, als eine
*Verfügbarkeits*-Eigenschaft), gewickelt um Residuen, die er in voller Stärke benennt
und nicht zu schließen beansprucht. Er verpflichtet sich auf **keinen konkreten
Mesh-Stack** und macht **keine Anonymitätsbehauptung für die Funkschicht**; er ist ein
Haltungs-und-Modell-Teil, genau wie Teil 4 es ist. Strohmann-Werte sind mit `(s)`
markiert.

Lies §3 (die Realismus-Einschätzung) zuerst — sie ist das Rückgrat, und sie sagt das
viel größere Ding, das dieser Teil zu behaupten verweigert. Die eine tragende positive
Behauptung ist eng: *Dispersion über unabhängige Gateways erweitert I-3 auf den
physischen Nachbarschafts-Austritt als eine Verfügbarkeits-Eigenschaft, und nichts im
Mesh darf die I-2-Inhalts-Untergrenze bewegen* (BL-16) — das Mesh ist so unabhängig von
der Untergrenze, wie Teil 4 den Transport hält (CT-16). Dieser Teil ist die L4-Sprosse,
an die das CT-18a von Teil 4 übergibt, und er bleibt mit jenem Zugeständnis konsistent
(BL-17): Wenn es keinen Nachbarn gibt, wird nichts zugestellt.

## 1. Das Modell gemischter Netze und die Rollen

- **BL-1 (das Mesh ist eine Schicht, kein Modus). [normativ]** Ein konformer Knoten
  MUSS (MUST) lokale Funklinks und Internet-Links als Link-Typen behandeln, die *zu
  jeder Zeit* koexistieren, nicht als einen "Blackout-Modus", der bei Verlust der
  Infrastruktur betreten wird. Den Uplink zu verlieren MUSS (MUST) eine Änderung der
  *Route* sein (ein Hop mehr zu einem Gateway), niemals eine Änderung von Protokoll,
  Identität oder Sicherheitshaltung. Ein Entwurf mit einem eigenen "Mesh-Modus", den der
  Nutzer umschaltet, ist zu dieser Rahmung nicht konform (OP-6).
- **BL-2 (Rollen, nach Hardware-Realität). [normativ]** Ein Knoten MUSS (MUST) sich,
  aus seiner tatsächlichen Funkfähigkeit, als genau einen der folgenden
  selbstklassifizieren: **Blatt** (ein Telefon: STA+AP- oder Wi-Fi-Aware-Nebenläufigkeit,
  akku-gebunden, kein Root), **Backbone** (ein Dual-Radio-PC/-SBC, der echtes 802.11s
  betreibt, kontinuierliches Store-and-Forward) oder **Gateway** (ein Backbone oder Blatt,
  das gerade einen Uplink hält und ihn ankündigt). Rollen sind fähigkeits-abgeleitet und
  zeitvariabel — ein Gateway, das seinen Uplink verliert, wird Backbone oder Blatt —,
  niemals eine feste Stufe.
- **BL-3 (Opt-in ist eine Vorbedingung jedes Funklinks). [normativ]** Ein Knoten DARF
  NICHT (MUST NOT) über einen lokalen Funklink Verkehr originieren, weiterleiten oder
  gatewayen ohne ein vorheriges, ausdrückliches, informiertes Opt-in *speziell für die
  Mesh-Teilnahme* und getrennt von jedem Relais-Opt-in, weil Mesh-Sichtbarkeit physisch
  ist (BL-18) und eine Funkschicht-Identität trägt, die das Overlay nicht rotieren kann
  (BL-18a). Schweigen, oder das Erben des Relais-Opt-ins, ist nicht konform.
- **BL-4 (ehrliches Akku- und Speicher-Budget). [normativ]** Ein Blatt-Knoten MUSS
  (MUST) vor dem Opt-in die Akku- und Speicherkosten offenlegen, die er tatsächlich
  tragen wird (Strohmann: eine begrenzte Store-and-Forward-Quote und ein getakteter
  Funk-Zeitplan), und DARF NICHT (MUST NOT) eine kontinuierliche Backbone-Verfügbarkeit
  versprechen, die er auf Akku nicht aufrechterhalten kann. Das konkrete Budget ist OP-6
  offen und MUSS (MUST) deklariert, nicht geraten werden (BL-20).

## 2. Dispersion über unabhängige Gateways, Adressierung, Beförderung und Mixing

### 2.1 Dispersion über unabhängige Gateways (die tragende Idee, als Verfügbarkeit)

- **BL-5 (Anteile SOLLTEN durch unabhängige Gateways austreten). [normativ]** Wenn die
  `n` Anteile einer Nachricht (SP-2) das lokale Mesh zu einem Uplink durchqueren, SOLLTE
  (SHOULD) ein konformer Client sie so routen, dass sie durch *verschiedene* Gateways
  austreten, und so I-3 (kein Single Point) auf den physischen Nachbarschafts-Austritt
  erweitern. Ein Gateway, das `k` der `n` Anteile trägt, ist ein Single Point und MUSS
  (MUST) vermieden werden, wo ≥2 unabhängig-*geschätzte* Gateways (BL-6) erreichbar
  sind. In einem tiefen Blackout kann die Unabhängigkeitsschätzung leer sein (BL-6);
  BL-5 degradiert dann **standardmäßig** zu BL-7, nicht als Grenzfall. Der hier
  behauptete Nutzen ist **Verfügbarkeit**, nicht Unbeobachtbarkeit (§3): Kein Ausfall,
  keine Blockade und keine Sybil-Übernahme eines einzelnen Gateways tötet die Zustellung
  — das ist das CT-15-Urteil für Transporte, im Mesh-Raum.
- **BL-6 (was "unabhängig" auf der Funkschicht bedeuten kann — angegeben, nicht gelöst).
  [normativ, Residuum-erklärend]** Ein konformer Client DARF NICHT (MUST NOT) Gateways
  auf *Selbstdeklaration* hin als unabhängig behandeln (GR-3, im Funkraum).
  "Unabhängig" kann nur aus *beobachtbaren, nicht-selbstdeklarierten* Signalen geschätzt
  werden — verschiedene Uplink-ASes *dort, wo eine AS-Karte (Teil 8) erreichbar ist*,
  verschiedene Funk-Next-Hops, verschiedene physische Richtung —, von denen jedes
  schwach, fälschbar oder **innerhalb eines Blackouts unverfügbar** ist (die AS-Karte,
  das stärkste Signal, ist oft das Erste, was fort ist). Die ehrliche Bedeutung von
  "unabhängiges Gateway" ist daher eine **begrenzte Vertrauensschätzung**, keine
  verifizierte Tatsache (§4b); ein Client MUSS (MUST) sie als solche präsentieren und
  DARF NICHT (MUST NOT) verifizierte Gateway-Unabhängigkeit behaupten. Siehe BL-21 — dies
  ist das wiederkehrende Unabhängigkeitsproblem im Funkraum.
- **BL-7 (zu wenige — oder null — unabhängige Gateways degradieren, scheitern nie
  offen). [normativ]** Wo weniger als zwei unabhängig-geschätzte Gateways erreichbar
  sind, DARF NICHT (MUST NOT) ein Client `k` Anteile stillschweigend durch eines
  schieben, als hielte die Dispersion; er MUSS (MUST) Anteile für einen späteren
  unabhängigen Austritt halten (begrenzt durch die BL-12-TTL), sie über die Zeit
  verteilen oder offenlegen, dass der physische Austritt für diese Nachricht ein Single
  Point ist (BL-19). Die Untergrenze (I-2) ist in beiden Fällen unberührt (BL-16).

### 2.2 Adressierung ohne globale Erreichbarkeit

- **BL-8 (Namen überleben; globale Routen nicht). [normativ]** Die
  Relais-/Empfänger-Ed25519-`id` (Teil 2) und die `box_id`/das Rendezvous von Teil 6
  MÜSSEN (MUST) innerhalb eines Blackouts die stabilen Namen bleiben; was bricht, ist die
  globale *Erreichbarkeit*, nicht die Benennung. Ein Knoten DARF NICHT (MUST NOT) für die
  Next-Hop-Auswahl im Mesh von einer erreichbaren DHT oder irgendeiner globalen Route
  abhängen.
- **BL-9 (Next-Hop ohne eine DHT — die Auswahl und ihre Kosten).** Ohne eine globale
  Route wird ein Mesh-Next-Hop durch eine kostenbegrenzte lokale Methode gewählt:
  epidemisches Flooding hin zu irgendeinem Uplink (billig, kein Zielwissen, hohe
  Funkkosten); ein Erreichbarkeits-*Gradient*, bei dem Nachbarn Erreichbarkeit *hin zu
  einem Gateway* ankündigen — niemals hin zum benannten Empfänger, was ein Selektor wäre
  (I-4/SP-7); oder physische Beförderung (Store-and-Forward, bis ein Gateway in
  Reichweite kommt). Diese Klausel benennt die Auswahl; die Wahl ist ein Strohmann
  (BL-20), und jede Option MUSS (MUST) SP-7 (keine pfadübergreifende Verknüpfbarkeit auf
  den Bytes) und I-4 (BL-15) bewahren.
- **BL-10 (die Zustellung läuft weiterhin über die Drops von Teil 6, niemals zu einem
  benannten Gerät). [normativ]** Die Aufgabe des Mesh endet am *Uplink*: Sobald Anteile
  das Internet erreichen, treten sie wieder in das Overlay ein und werden an dispergierte
  Dead Drops (Teil 6) genau wie zuvor zugestellt. Das Mesh DARF NICHT (MUST NOT)
  versuchen, direkt an ein benanntes Empfänger-*Gerät* zuzustellen — das würde die
  Zustellung auf eine Person zielen lassen und den Teil-6-Vertrag verletzen (RZ-1). Der
  wahrhaft-rein-lokale Fall (Sender, Drop und Empfänger alle im Mesh, kein Uplink) wird
  dadurch bedient, dass auch der **Drop** des Empfängers mesh-erreichbar ist —
  Einzahlung und Abfrage laufen beide über das Mesh *zu einem Drop*, niemals zum
  Empfängergerät —, was das offene Element ist, das Teil 6 §9 als "Abfrage über das Mesh
  während des Blackouts (OP-6)" auflistet. Das Routing zu einem benannten Empfängergerät
  bleibt als Selektor verboten.

### 2.3 Store-and-Forward und das Rahmungs-Urteil

- **BL-11 (Sphinx-Gültigkeit, nicht Bytes, ist die Beschränkung langer Beförderung).
  [normativ, Residuum-erklärend]** Das 2048-Byte-Sphinx-Paket (SP-3) ist in *Bytes*
  selbsttragend, aber nicht in *Gültigkeit*: Seine Hop-Sicherheit bindet an die ≤7-Tage-
  `onion`-Epoche eines Relais (CH-5) und an den Replay-Cache je Epoche (SP-5, SP-7b). Ein
  Paket, das über Stunden-bis-Tage über intermittierende Links getragen wird, DARF (MAY)
  die Epoche überleben, die sein erster Hop annahm, oder ankommen, nachdem der
  Replay-Zustand rotiert oder über Neustarts verloren wurde. Ein konformer Entwurf MUSS
  (MUST) dies angeben und DARF NICHT (MUST NOT) annehmen, dass ein Sphinx-Paket unbegrenzt
  unverändert beförderbar ist.
- **BL-12 (das Urteil: Blackout braucht seinen eigenen Store-and-Forward-Umschlag).
  [normativ]** Wegen BL-11, und weil Store-and-Forward Felder braucht, für die das feste
  2048-Byte-Paket keinen Platz hat (eine begrenzte Time-to-live, Fragmentierung und
  Reassemblierung für intermittierende Links, Custody-Signalisierung je Hop), ist das
  Urteil für diesen Entwurf, dass **die Blackout-Beförderung ihre eigene äußere Rahmung
  braucht** — ein DTN-artiges Bundle (Vorarbeit: RFC 4838/5050), das das unveränderte
  innere Sphinx-Paket *umwickelt*, selbst auf feste Länge aufgefüllt ist und dessen
  Metadaten AEAD-geschützt sind, niemals Klartext. Das innere Paket ist unberührt; der
  Umschlag ist neu und lebt nur auf Blackout-Links. Dies ist ein Strohmann-Urteil
  (BL-20), nur durch ein Argument umzustoßen, das BL-11 schließt, welches dieser Entwurf
  nicht hat.
- **BL-13 (der Umschlag darf kein Selektor werden — und erbt das Verschachtelungs-
  Residuum von CT-6a). [normativ, Residuum-erklärend]** Die TTL-, Fragmentindex- und
  Custody-Felder des Umschlags sind genau die Klartext-Metadaten, die I-4 verbietet; sie
  MÜSSEN (MUST) innerhalb eines AEAD-geschützten, festgroßen, uniform-aussehenden Rahmens
  (SP-4-Disziplin) leben und DÜRFEN NICHT (MUST NOT) einem Funkbeobachter erlauben, zwei
  Fragmente einer Nachricht oder zwei Anteile einer Nachricht besser zu verknüpfen, als
  es SP-7 auf dem Overlay bereits erlaubt. **Ehrliches Residuum, geerbt von Teil 4:** Ein
  I-4-uniformes inneres Paket innerhalb eines äußeren Bundles zu umwickeln erschafft die
  **CT-6a-Verschachtelungsstruktur-Fläche** im Funkraum neu — ein festgroßer äußerer
  Rahmen, dessen Größe/Timing/Fragmentierung verraten kann, dass er eine *zweite* feste
  Einheit trägt, und die Uniformität je Schicht macht die Verschachtelung für einen
  RF-Beobachter **nicht** unentdeckbar. Dies ist ein deklariertes Residuum, von der
  Rahmung nicht geschlossen. Es ist nur in dem Sinne überlebbar, in dem hier alles
  überlebbar ist: Der Blackout-RF-Gegner ist *lokal*, sodass Verschachtelungs-Erkennung
  *Beobachtbarkeit-der-Teilnahme* kostet — die BL-18 ohnehin als verloren einräumt — und
  die I-2-Inhalts-Untergrenze **nicht** berührt.

### 2.4 Mixing auf der Funkschicht gegen das Sybil-Gateway

- **BL-14 (das Sybil-Gateway ist eine physische Eklipse; die Antwort ist partiell).
  [normativ, Residuum-erklärend]** Ein Knoten, der "Ich habe Uplink" ankündigt, zieht den
  Verkehr der Nachbarschaft an, und ein Sybil-Gateway (oder eine Koalition) ist eine
  *physische Eklipse* — die Funkschicht-Instanz des Eklipse-Residuums von Teil 2 (OP-2).
  Die partielle Antwort ist (i) Quellen-Mixing auf der Funkschicht (BL-15), sodass ein
  Gateway einen Anteil nicht trivial seinem originierenden Nachbarn *auf der Rahmenschicht*
  zuordnen kann, zusammengesetzt mit (ii) Dispersion über unabhängige Gateways (BL-5),
  sodass kein einzelnes Gateway `k` sieht. Eine konforme Beschreibung MUSS (MUST) diese
  Antwort als **partiell** deklarieren: Sie erhöht die Kosten des Sybils, sie entfernt die
  Eklipse nicht, und sie reduziert sich auf OP-1/OP-2, die auf der Funkschicht
  wiederkehren (BL-6, BL-21).
- **BL-15 (Quellen-Mixing auf der Funkschicht ist eine Verfügbarkeits-/Anti-Eklipse-
  Maßnahme, kein Ursprungs-Verbergen). [normativ]** Verkehr auf einem lokalen Funklink
  MUSS (MUST) I-4 gegenüber einem Funkbeobachter auf den Bytes erfüllen (festgroße
  uniforme Rahmen, BL-13) und SOLLTE (SHOULD) Quellen-Mixing anwenden, sodass der
  unmittelbare rahmen-ebene Sender eines Anteils nicht durch den Rahmen als dessen
  Originator markiert wird. Dies ist **nicht** die GR-8-Verzeichnis-Stichproben-
  Verteidigung (GR-8 mischt die *gespeicherte Stichprobe* eines Clients über Quellklassen
  gegen eine Karten-Eklipse — ein anderer Mechanismus gegen einen anderen Gegner) und
  DARF NICHT (MUST NOT) deren Namen oder deren Zusicherungen entleihen. Und es DARF NICHT
  (MUST NOT) als Verbergen des *physischen* Originators präsentiert werden: Ein lokaler
  Gegner mit Funkpeilung kennt den physischen Emitter einer Übertragung ungeachtet des
  Rahmeninhalts (BL-18), sodass Funk-Quellen-Mixing *Anti-Eklipse-Kosten gegen ein
  Sybil-Gateway* erkauft, niemals Ursprungs-Anonymität — dieselbe
  Verknüpfung-gegen-Verfügbarkeit-Disziplin, die CT-15a für Transporte durchsetzt.

## 3. Die ehrliche Realismus-Einschätzung (das Rückgrat)

*(Geschrieben in der §Residuum-Stimme der Teile 4, 8 und 11. Dies ist der Teil, kein
Anhang.)*

**Was wahrhaft entwerfbar und real ist.** Drei Dinge. Erstens das *Modell gemischter
Netze* (BL-1): Funk und Internet als koexistierende Link-Typen zu behandeln, sodass der
Verlust eines Uplinks ein Hop mehr ist, keine andere Welt, ist sauber, baubar und
vorarbeits-gedeckt (Briar, Reticulum, Yggdrasil/cjdns, Freifunk demonstrieren Teile).
Zweitens — die Idee, die dem Paradigma seinen Unterhalt verdient — *Dispersion über
unabhängige Gateways* (BL-5): Die klassische tödliche Schwäche jedes Gateway-Mesh ist,
dass das Gateway alles sieht, und ScrambNet antwortet ihr mit dem Mechanismus, der das
ganze Netzwerk definiert, indem es die `n` Anteile über Gateways verteilt, sodass kein
einzelner physischer Austritt `k` sieht. Drittens der *Invariantenschutz* (BL-16): die
I-2-Untergrenze gänzlich unabhängig davon zu halten, ob das Mesh sich bildet, ist nicht
bloß entwerfbar, es ist erzwungen, und es ist dieselbe Disziplin, die Teil 4 auf
Transporte anwendet. Diese drei sind solide.

**Aber die gute Idee ist eine *Verfügbarkeits*-Idee und muss als nichts mehr verkauft
werden.** Dispersion über unabhängige Gateways tut wenig für das *Wer* oder *Wo* im
Hot-Blackout-Bedrohungsmodell, weil zwei Residuen und ein Identitätsleck sie als
Anonymitätsmechanismus untergraben: Du kannst die Gateway-Unabhängigkeit in einem
Blackout nicht verifizieren (BL-6), der Emitter ist physisch lokalisierbar (BL-18), und
die Funkschicht trägt eine Identität, die das Overlay nicht rotieren kann (BL-18a). Was
die Dispersion *liefert*, und wahrhaft liefert, ist Verfügbarkeit: Kein Ausfall, keine
Blockade und keine Sybil-Übernahme eines einzelnen Gateways tötet die Zustellung, und
das gilt selbst, wenn jede Anonymitätseigenschaft kollabiert ist. Dies ist genau das
CT-15-Urteil für Multi-Cover-Transporte — Verfügbarkeit ja, Tarnung nein — und der Teil
pinnt es dorthin (BL-16). Als Anonymität verkauft wäre es eine Überbehauptung; als
Verfügbarkeit verkauft ist es eine reale, nicht-leere Eigenschaft.

**Was nur partiell ist.** Das Sybil-Gateway- / Physische-Eklipse-Problem (BL-14).
Quellen-Mixing auf der Funkschicht plus Dispersion über unabhängige Gateways erhöht die
Kosten einer Sybil-Eklipse; es entfernt sie nicht. Eine Gateway-Koalition, die `k` der
erreichbaren Austritte in einem kleinen Nachbarschafts-Mesh kontrolliert, verfinstert
einen Sender genau so, wie eine Relais-Koalition es auf dem Overlay tut — OP-1 und OP-2,
die im Funkraum wiederkehren, keine neue Verteidigung. "Partiell" ist das richtige Wort.

**Was nicht gelöst ist — in voller Stärke deklariert, drei Residuen.**

*Erstens, die Verifikation der Gateway-Unabhängigkeit (BL-6, BL-21).* Du kannst aus
nichts, was ein Gateway selbstdeklariert, verifizieren, dass zwei Gateways unabhängig
sind, und innerhalb eines Blackouts ist es schlimmer als auf dem Overlay: Die AS-Karte
(Teil 8), die einem Client erlauben würde, Unabhängigkeit aus nicht-selbstdeklarierten
Daten *abzuleiten*, ist selbst oft unerreichbar — das eine Werkzeug, das genau dann fort
ist, wenn es gebraucht wird, sodass die Schätzung in einem tiefen Blackout nahezu leer
sein kann (BL-5 degradiert standardmäßig zu BL-7). Dies ist kein Teil-5-Waisenkind: Das
Bedrohungsmodell benennt es als eine Facette des tiefsten wiederkehrenden Problems des
Projekts — die Unabhängigkeit einer Partei zu verifizieren, ohne ihrer Selbstdeklaration
zu vertrauen — geteilt mit Relais (OP-1), Release-Signierern (OP-8) und
Abhängigkeits-Autoren (OP-2/RB). Die ehrliche Antwort ist dieselbe wie dort: ein
*begrenztes, deklariertes Residuum*, das eine Vertrauens-*Schätzung* mit einem
angehängten Fehler speist (im ID-12-Stil), keine kryptografische Prüfung. Teil 5 ist
nicht der Ort, an dem dies endlich gelöst wird.

*Zweitens, und irreduzibel, physische Lokalisierbarkeit (BL-18).* Ein Mesh-Knoten in
einem heißen Blackout ist ein Funksender an einem physischen Ort, und **kein Overlay
verbirgt einen Funkemitter vor einem Gegner mit einem Funkpeiler.** Dies ist kategorisch
schwerer als alles andere in der Spezifikation, weil jede andere Bedrohung in ScrambNet
ein *entfernter* Gegner ist, der über Bytes räsoniert, und dies ein *lokaler* Gegner mit
einer Antenne ist — anwesend genau deshalb, weil er den Blackout auferlegte. Das ganze
kryptografische Gebäude operiert auf *dem, was die Bytes offenbaren*; Lokalisierbarkeit
handelt überhaupt nicht von den Bytes, sie ist die elektromagnetische Tatsache der
Übertragung. Der Teil darf nicht versprechen, dass das Mesh Anonymität bewahrt, und er
tut es nicht.

*Drittens — das Leck, das zu verhindern das Overlay am härtesten arbeitet und das der
Funk rückgängig macht (BL-18a).* Lokalisierbarkeit ist *wo du bist*; Identität ist *wer
du bist*, und die Funkschicht leckt beides. Ein Wi-Fi/802.11s-Funk emittiert persistente
Layer-2-Identifikatoren, die das ScrambNet-Overlay nie berührt — eine MAC-Adresse (und
802.11s-Peering kann eine stabile erfordern), Wi-Fi-Direct/Aware-Dienst- und
Geräte-IDs, Probe-Request-Fingerabdrücke und, gegen einen fähigen Gegner, einen
*Hardware-RF-Fingerabdruck* (Oszillator-Imperfektionen), der die MAC-Randomisierung
gänzlich überlebt. So sitzt die ganze Overlay-Geschichte — rotierende `id`, `box_id` je
Epoche, Karten je Beziehung (RZ-2), SP-7-Anteils-Unverknüpfbarkeit — *über* einem
Layer-2-Pseudonym, das ein lokaler Sniffer direkt liest, und die Overlay-Rotation kann es
nicht rotieren. Und die Mesh-*Topologie selbst* ist eine beobachtbare RF-Karte: Wer wem
weiterleitet, ist auf dem Äther sichtbar, selbst unter uniformen Rahmen. Dies ist das
einzige Residuum, das der erste Entwurf dieses Teils ausließ; es wird hier in voller
Stärke benannt, weil es wohl schlimmer ist als Lokalisierbarkeit — du bist nicht nur
auffindbar, während du sendest, du trägst jedes Mal, wenn du beitrittst, ein stabiles
Funk-Pseudonym.

**Kann das Mesh die Invarianten bewahren, die es erbt? Partiell, und hier ist das
ehrliche Hauptbuch.** **I-2 (Inhalts-Untergrenze):** sauber bewahrt — die Untergrenze
ritt nie auf dem Mesh, so wenig, wie sie auf dem Transport ritt (BL-16); dies ist die
stärkste und wahrste Aussage, die der Teil macht. **I-4 (Draht-Uniformität) und SP-7
(Anteils-Unverknüpfbarkeit):** bewahrt **nur auf der Byte-Schicht** — ein uniformer
Rahmen ist immer noch eine erkennbare Emission (BL-18), und zwei Anteile einer Nachricht,
die vom *selben physischen Gerät im selben Fenster* emittiert werden, sind durch
Funkpeilung und Timing korreliert (der Funk re-verknüpft, was das Overlay entknüpft); der
Teil DARF NICHT (MUST NOT) behaupten, dass geerbte Byte-Unverknüpfbarkeit bis zur
RF-Schicht überlebt. **I-3 (kein Single Point):** *erweitert*, als eine
Best-Effort-Verfügbarkeits-Eigenschaft, durch Dispersion über unabhängige Gateways
(BL-5) — aber nur in dem Maße, in dem die Schätzung von BL-6 vertrauenswürdig ist, was
das ungelöste Residuum ist. Also: I-2 bewahrt, I-4/SP-7 nur-auf-den-Bytes-bewahrt, I-3
erweitert-aber-geschätzt. Das ist das Hauptbuch, und es ist absichtlich anti-triumphal.

**Konsistenz mit CT-18a.** Teil 4 räumte ein, dass bei einer vollständigen Abschaltung
ohne Mesh-Nachbarn die Zustellung null und die Untergrenze intakt-und-nutzlos ist. Teil 5
ist die Sprosse *unter* jenem Zugeständnis — was du tust, *wenn es* einen Nachbarn gibt —
und er nimmt es nicht zurück. Er erweitert die Erreichbarkeit eine Schicht tiefer; er
macht die Zustellung nicht garantiert (BL-17). Die ehrliche Behauptung ist nicht
"Kommunikation kommt auf dem Mesh immer durch" — sie ist: *Wenn ein Mesh-Nachbar und ein
Gateway existieren, kann eine Nachricht die Stadt mit der Geschwindigkeit eines Busses
durchqueren; wenn keiner existiert, bleibt das Geheimnis zu Hause, unzugestellt und nicht
offengelegt; und in jedem Fall ist das Senden auf dem Mesh ein physisch lokalisierbarer,
funk-identifizierbarer Akt, den das Overlay nicht verbergen kann.*

Dies ist ein XL- / Forschungsrisiko-Element, und es liefert, wie die Roadmap erlaubt, ein
*partielles* Ergebnis: ein solides Modell gemischter Netze und eine echte
Verfügbarkeits-Idee, um Residuen herum (Gateway-Unabhängigkeit, physische
Lokalisierbarkeit, Funk-Identität), die in voller Stärke benannt und nicht als
geschlossen beansprucht werden.

## 4. Die zwei begründeten Urteile

**(a) Überlebt das 2048-Byte-Sphinx-Paket stundenlanges Store-and-Forward, oder braucht
der Blackout seine eigene Rahmung? → Er braucht seine eigene Rahmung (BL-11, BL-12).** Das
Paket ist in *Bytes* in Ordnung, scheitert aber in *Gültigkeit und Funktion* an drei
unabhängigen Punkten: (1) Seine Hop-Sicherheit bindet an eine ≤7-Tage-`onion`-Epoche
(CH-5), die eine tagelange Beförderung überleben kann, sodass sie an einem rotierten,
genullten Schlüssel ankommt; (2) SP-5/SP-7b erfordern einen Replay-Zustand je Epoche, der
Neustarts überlebt, und intermittierende Funkknoten verlieren Strom und Caches genau über
den stundenlangen Horizont; (3) das feste 2048-Byte-Layout (SP-3) hat kein freies Feld für
die TTL-, Fragmentierungs- und Custody-Signalisierung, die intermittierende Links
brauchen, und darf keines im Klartext wachsen lassen (I-4). Die saubere Auflösung ist ein
DTN-artiges äußeres Bundle, das das unveränderte innere Paket umwickelt (BL-12/BL-13), mit
dem deklarierten CT-6a-Verschachtelungs-Residuum. Dies ist ein Strohmann-Urteil, nur durch
das Schließen von BL-11 umzustoßen.

**(b) Kann die Gateway-Unabhängigkeit auf der Funkschicht verifiziert werden? → Nein; es
ist ein deklariertes Residuum, das eine begrenzte Vertrauensschätzung speist (BL-6,
BL-21).** "Unabhängig" müsste begründet werden, ohne dem zu vertrauen, was das Gateway
sagt (GR-3, im Funkraum), und jedes verfügbare Signal ist schwach oder fort: Verschiedene
Uplink-ASes brauchen die Teil-8-Karte, *unerreichbar innerhalb genau des Blackouts, in dem
Unabhängigkeit am meisten zählt*; verschiedene physische Richtung ist fälschbar und grob;
verschiedener Funk-Next-Hop beweist Topologie, nicht Austritts-Unabhängigkeit. Es gibt
keine kryptografische Prüfung, dass zwei Gateways unabhängige Uplinks haben — dieselbe
Wand, gegen die OP-1 für Relais-Disjunktheit und OP-8 für Signierer-Jurisdiktion läuft. Die
ehrliche Architektur ist also identisch mit der der AS-Karte (ID-12): Behaupte keine
Verifikation, produziere eine begrenzte Vertrauensschätzung aus nicht-selbstdeklarierten
Beobachtbaren (die in einem tiefen Blackout nahezu leer sein kann), hänge die Unsicherheit
an, lege sie offen (BL-19), und lass Dispersion (BL-5) und Verteilung über die Zeit (BL-7)
den Schaden begrenzen — nicht entfernen —, wenn die Schätzung falsch ist.

## 5. Die Invarianten- und Ehrlichkeitsschütze

- **BL-16 (die Untergrenze ist unabhängig vom Gelingen des Mesh — das CT-16-Analogon).
  [normativ]** Keine Vertraulichkeits- oder Dispersions-Garantie (I-2) MUSS (MUST) davon
  abhängen, dass das Mesh sich bildet, dass ein Gateway erreichbar ist, dass Gateways
  wahrhaft unabhängig sind (BL-6) oder dass der Blackout-Umschlag zugestellt wird. Das
  Mesh erkauft **nur Erreichbarkeit** — dasselbe Wort, das Teil 4 für Transporte nutzt. Ein
  Entwurf, in dem der Verlust des Mesh die Untergrenze verliert, ist nicht konform.
- **BL-17 (Konsistenz mit CT-18a: der Boden ist immer noch ein Boden, drei Zustände).
  [normativ]** Teil 5 erweitert die Erreichbarkeit eine Sprosse unter CT-18a und DARF NICHT
  (MUST NOT) so formuliert sein, dass es ihm widerspricht. Die drei Zustände, alle
  ausdrücklich: (1) **kein Nachbar in Reichweite** → CT-18a, null Zustellung, Untergrenze
  intakt-und-nutzlos; (2) **Nachbar(n) in Reichweite, aber kein Gateway irgendwo im Mesh
  erreichbar** → *auch* null Zustellung, erreicht über das Mesh statt direkt —
  Store-and-Forward DARF (MAY) Anteile gegen ein *zukünftiges* Gateway innerhalb der
  BL-12-TTL halten, aber dies DARF NICHT (MUST NOT) als Zustellung präsentiert werden; (3)
  **≥1 Gateway erreichbar** → BL-5/BL-7-Dispersion oder Degradation. Zustand (2) kollabiert
  zum selben Ausgang wie (1); nur der Pfad unterscheidet sich. Teil 5 macht die Zustellung
  eine Schicht tiefer *möglich*, niemals *wahrscheinlich* und niemals *garantiert*.
- **BL-18 (Physische-Lokalisierbarkeits-Residuum — in voller Stärke angegeben, nie
  gelöst). [normativ, Residuum-erklärend]** Ein Mesh-Knoten, der in einem heißen Blackout
  sendet, ist ein **physisch lokalisierbarer Akt**: ein Funkemitter an einem Ort, genau in
  dem Moment, in dem der lokale Gegner, der den Blackout auferlegte, am aggressivsten und am
  bereitwilligsten ist, Funkpeilung und IMSI-catcher-artige Taktiken zu nutzen. **Kein
  Overlay, Mixing, keine Dispersion und keine Rahmung in dieser Spezifikation verbirgt
  dies, und dieser Teil DARF NICHT (MUST NOT) behaupten oder implizieren, dass er es tut.**
  Es ist der Grund, warum die Mesh-Teilnahme ein ausdrückliches, informiertes Opt-in je
  Kontext sein MUSS (MUST) (BL-3), und der Grund, warum die ehrliche Behauptung dieses Teils
  eng ist (§3).
- **BL-18a (Funkschicht-Identitäts-Residuum — deklariert, nicht gelöst). [normativ,
  Residuum-erklärend]** Die Mesh-Teilnahme exponiert persistente Layer-2-Identifikatoren,
  die das Overlay nicht rotieren kann: eine MAC-Adresse (802.11s-Peering kann eine stabile
  erfordern), Wi-Fi-Direct/Aware-Geräte- und -Dienst-IDs, Probe-Request-Fingerabdrücke
  und — gegen einen fähigen Gegner — einen *Hardware-RF-Fingerabdruck*, der die
  MAC-Randomisierung überlebt. Jeder ist ein stabiles Pseudonym für das *Gerät*, unabhängig
  von jeder Overlay-Rotation (`id`, `box_id`, RZ-2-Karten, SP-7). Die MAC-Randomisierung
  hilft gegen die erste Klasse und nichts gegen RF-Fingerabdruck. Die Mesh-*Topologie* ist
  ebenso eine beobachtbare RF-Karte — wer wem weiterleitet, ist auf dem Äther sichtbar,
  selbst unter uniformen Rahmen. Der Teil DARF NICHT (MUST NOT) implizieren, dass die
  Overlay-Unverknüpfbarkeit sich auf den Funkemitter erstreckt. Dies ist die zweite Facette,
  neben der Gateway-Unabhängigkeit (BL-21), des wiederkehrenden
  Identitäts-/Unabhängigkeits-Problems im Funkraum, deklariert und nicht geschlossen.
- **BL-19 (lege die Mesh-Haltung ehrlich offen — das CT-19-Analogon). [normativ]** Ein
  konformer Client MUSS (MUST) auf der bestehenden Ehrlichkeitsfläche (PS-9/CT-19)
  offenlegen: dass ein Funklink in Gebrauch ist; dass dieser Link *physisch lokalisierbar*
  (BL-18) **und funk-identifizierbar** (BL-18a) ist; ob sein Gateway-Austritt einzeln oder
  plural-und-unabhängig-*geschätzt* ist (BL-6/BL-7); und dass die Mesh-Erreichbarkeit —
  anders als die I-2-Untergrenze — **keine** Garantie trägt und null sein kann. Die
  Botschaft, die die UI angibt: *deine Inhalts-Untergrenze hält; auf dem Mesh kannst du
  lokalisiert und dein Gerät auf dem Äther dort, wo du stehst, erkannt werden.*
- **BL-20 (konkreter Stack offen gelassen; Behauptungen durch das Tatsächlich-Betriebene
  begrenzt). [normativ]** Teil 5 schreibt **keinen** spezifischen Funk-Stack, keine
  Routing-Methode (BL-9), keine TTL/Fragment-Dimensionierung (BL-12) und kein Akku-Budget
  (BL-4) vor; diese sind Strohmänner und Eigner-Entscheidungen. Ein Client mit einem nicht
  spezifizierten Mesh-Stack DARF NICHT (MUST NOT) irgendeine *quantitative*
  Mesh-Verfügbarkeits-Eigenschaft behaupten; er DARF (MAY) nur das *qualitative* "ein
  Knoten, der den Uplink verliert, kann einen Hop mehr zu einem Nachbar-Gateway nehmen, und
  Anteile SOLLTEN durch unabhängig-geschätzte Gateways austreten" behaupten, und nur dort,
  wo er tatsächlich ≥2 unabhängig-geschätzte Gateways mit `k < n` betreibt.
- **BL-21 (das wiederkehrende Unabhängigkeitsproblem ist deklariert, nicht geschlossen).
  [normativ, Residuum-erklärend]** Die Gateway-Unabhängigkeit ohne eine erreichbare Karte
  und mit selbstdeklariertem Standort zu verifizieren (BL-6) ist das **gleiche Problem, das
  für Relais (OP-1), Release-Signierer (OP-8) und Abhängigkeits-Autoren (OP-2/RB)
  auftaucht** — die Unabhängigkeit einer Partei zu verifizieren, ohne ihrer
  Selbstdeklaration zu vertrauen — nun seine Funkschicht-Maske innerhalb eines Blackouts
  tragend, wo die AS-Karte (Teil 8) selbst unerreichbar ist. Teil 5 löst es **nicht**; er
  reduziert es auf jenes deklarierte wiederkehrende Residuum und speist eine begrenzte
  Vertrauensschätzung, genau wie die Karte eine mit einer deklarierten Fehlerrate speist
  (ID-12).

## 6. Hier eingeführte Anforderungen

- **BL-1 / BL-2 / BL-3 / BL-4** — das Mesh ist eine Schicht, kein Modus;
  fähigkeits-abgeleitete, zeitvariable Rollen; ausdrückliches Opt-in je Kontext vor jedem
  Funklink; ein ehrliches Akku-/Speicher-Budget.
- **BL-5 / BL-6 / BL-7** — Dispersion über unabhängige Gateways als Verfügbarkeit;
  "unabhängig" ist eine begrenzte Vertrauensschätzung, niemals selbstdeklariert und in
  einem tiefen Blackout nahezu leer; zu-wenige/null Gateways degradieren, scheitern nie
  offen.
- **BL-8 / BL-9 / BL-10** — Namen überleben, Routen nicht; Next-Hop ohne eine DHT und
  seine Kosten; die Zustellung läuft weiterhin über die Drops von Teil 6, niemals zu einem
  benannten Gerät, und der rein-lokale Fall wird durch einen mesh-erreichbaren Drop bedient.
- **BL-11 / BL-12 / BL-13** — Sphinx-Gültigkeit (nicht Bytes) begrenzt lange Beförderung;
  der Blackout braucht seinen eigenen DTN-artigen Umschlag; der Umschlag darf kein Selektor
  sein und erbt das Verschachtelungs-Residuum von CT-6a.
- **BL-14 / BL-15** — das Sybil-Gateway ist eine physische Eklipse, nur partiell
  beantwortet; Funk-Quellen-Mixing ist eine Verfügbarkeits-/Anti-Eklipse-Maßnahme, **nicht**
  GR-8 und **kein** Ursprungs-Verbergen.
- **BL-16 / BL-17** — die Untergrenze ist unabhängig vom Mesh; Konsistenz mit CT-18a, die
  drei Zustellungs-Zustände, der Boden ist immer noch ein Boden.
- **BL-18 / BL-18a / BL-19** — physische Lokalisierbarkeit und Funk-Identität, beide in
  voller Stärke deklariert und nie gelöst; ehrliche Mesh-Haltung auf PS-9.
- **BL-20 / BL-21** — konkreter Stack offen gelassen; das wiederkehrende
  Unabhängigkeitsproblem deklariert, nicht geschlossen.

BL-16 und BL-18/BL-18a sind die tragenden drei: Die Untergrenze hängt nicht vom Mesh ab,
und das Mesh kann nicht verbergen, dass du sendest oder dass dein Gerät auf dem Äther
erkennbar ist. Die ehrliche Behauptung ist eng und verfügbarkeits-geformt: *Das Mesh
erweitert die Erreichbarkeit eine Sprosse unter eine Abschaltung und bewahrt die
Inhalts-Untergrenze, die es erbt, aber es verbirgt weder den Emitter noch das Gerät noch
die Topologie, und es garantiert keine Zustellung.* Brich diesen Teil, indem du eine
Mesh-ebene Anonymität benennst, die die Klauseln über BL-18/BL-18a hinaus versprechen,
eine Stelle, an der die I-2-Untergrenze über BL-16 hinaus vom Gelingen des Mesh abhängig
gemacht wird, einen Weg, auf dem BL-17 als Hochstufung von "möglich" zu "wahrscheinlich"
gelesen wird, oder ein Funkschicht-Leck, das BL-18/BL-18a verfehlen. Das ist die Einladung,
in der Hausstimme — und bei diesem Teil besonders ist die ehrliche Antwort auf "löst es den
Blackout?" "teilweise, und hier ist genau, wo es das nicht tut".
