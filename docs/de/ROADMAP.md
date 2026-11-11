# ScrambNet — Fahrplan

**Status: lebendes Dokument.** Dies ist der Arbeitsplan, kein Versprechen von Daten — ein
pseudonymes Freiwilligenprojekt bewegt sich, wenn Hände frei sind. Es ist geordnet nach
Abhängigkeit und Ehrlichkeit: Die Punkte, die das Projekt als *falsch* erweisen könnten, kommen
zuerst, denn wenn die tragende Behauptung nicht hält, zählt nichts stromabwärts.
Jeder Punkt benennt, wie „erledigt" aussieht, damit der Fortschritt prüfbar ist, nicht
behauptet.

Er wurde aus drei parallelen Reviews gebaut — Netzentwurf, Kryptografie und
Sicherheit/Betrieb — und die härtesten Befunde werden in vollem Blick gehalten statt
geglättet. Die Punkte verweisen auf die Spezifikationsteile (`SP-n`, `GR-n`,
`PS-n`, `RZ-n`), die Invarianten (`I-1…I-4`) und die offenen Probleme
(`OP-1…OP-9`).

Aufwandsskala: **S** ≈ Tage · **M** ≈ 1–2 Wochen · **L** ≈ Wochen, echtes Entwurfs-
risiko · **XL** ≈ ein Forschungs-Teilprojekt, das ein teilweises oder negatives Ergebnis
zurückgeben kann. Die letzten beiden sind keine zu vermeidenden Fehlschläge; sie sind die ehrliche Gestalt
ungelöster Probleme.

---

## Stufe 0 — Berichtigen, was wir bereits als falsch kennen (jetzt)

Diese kamen aus den Reviews als konkrete Defekte oder Überbehauptungen. Sie sind billig
und sie schützen die Glaubwürdigkeit des Projekts, die in diesem Stadium sein einziger echter Aktivposten
ist.

- **0.1 — Öffentliche Behauptungen mit dem bewiesenen Umfang in Einklang bringen.** `[behauptungskritisch]`
  Die Inhalts-Untergrenze ist informationstheoretisch **nur unterhalb von `k` Anteilen**; oberhalb von
  `k` ist die Inhaltsgeheimhaltung rechnerisch (das AEAD). Und „jetzt ernten, später
  entschlüsseln" ist **nur** für den Gegner unterhalb von `k` abgewehrt — ein `≥k`-, alles-
  aufzeichnender, künftig-quantenfähiger Gegner bricht den Inhalt weiterhin, *es sei denn, die
  Ende-zu-Ende-Schlüsseleinigung ist selbst postquanten oder vorab geteilt*. README,
  COMPARISON und das Bedrohungsmodell müssen das Regime (unterhalb-`k` vs. oberhalb-`k`)
  und die Annahme (Geheimhaltung des AEAD-Schlüssels) in jedem Satz über die Untergrenze nennen.
  **Erledigt:** kein unqualifizierter „informationstheoretischer Inhaltsschutz" bleibt in
  irgendeinem öffentlichen Dokument. **Aufwand S.**

- **0.2 — Die Ende-zu-Ende-AEAD-Schicht spezifizieren und vorführen.** `[behauptungskritisch]`
  SP-1 („vor der Streuung verschlüsseln") ist die ganze Kompositionsbehauptung, aber der PoC
  teilt *Klartext* — nirgends gibt es ein AEAD, also wird die Komposition behauptet,
  nie gezeigt. Spezifiziere die e2e-Schicht (Schlüsselaufbau aus dem `kpair` der Kontaktkarte
  vs. ein ephemerer Austausch — eine Wahl, die die Postquanten-Geschichte entscheidet),
  und erweitere den PoC, damit er tatsächlich verschlüsselt → teilt → rekonstruiert → entschlüsselt.
  **Erledigt:** der PoC führt SP-1 Ende zu Ende vor; die Wahl des Schlüsselaufbaus ist
  getroffen und ihre PQ-Folge festgehalten. **Aufwand M.**

- **0.3 — Anteil-Integrität unter einem bösartigen Drop.** `[Stichhaltigkeit]`
  Das SP-7-Tag sagt, *zu welcher* Nachricht ein Paket zu gehören behauptet, aber nichts
  authentifiziert die Anteil-Bytes oder das `k,n`-Byte. Ein einzelner feindlicher Drop oder Ausgang
  kann Bits in einem Anteil kippen; Shamir kann es nicht erkennen, also rekonstruieren `k` korrupt-konsistente
  Anteile zu Müll (das AEAD darüber fängt es ab — fail-closed — aber
  dies ist eine billige *gezielte Dienstverweigerung* auf einem Postfach). Entscheide: explizite
  Anteil-weise Bindung oder ein akzeptierter-und-dokumentierter Fail-closed-mit-Retry-Rest.
  **Erledigt:** ein Urteil mit der Konstruktion, falls nötig, in SP-7 geschrieben. **Aufwand M.**

- **0.4 — Den PGP-Schlüssel des Projekts veröffentlichen.** `[OpSec, unmittelbare Lücke]`
  SECURITY.md *verspricht* einen Schlüssel, der nicht existiert. Die erste Welle von Reviewern
  (die Mailinglisten) hat keinen vertraulichen Kanal. Erzeuge einen pseudonymgebundenen
  Schlüssel für `scrambnet@proton.me`, committe seinen Fingerabdruck, ersetze das vage
  „angemessene Zeit" durch ein echtes Offenlegungsfenster, und nenne, wie der Schlüssel selbst
  rotiert (auch der Offenlegungsschlüssel darf kein unersetzbarer Singleton sein, I-3).
  **Erledigt:** ein sensibler Bericht kann heute an einen echten, veröffentlichten Schlüssel verschlüsselt werden.
  **Aufwand S.**

*(Der Nibble-Reihenfolge-Parser-Bug von 0.1 und die im Review gefundene Polling-Lücke an der
UTC-Epochengrenze sind bereits für die Testvektoren in 3.2 und den KDF-Punkt in 2.2 vermerkt.)*

---

## Stufe 1 — Die tragende Behauptung beweisen oder brechen (kryptografisches Rückgrat)

Das gesamte Unterscheidungsmerkmal des Projekts ist I-2. Diese vier Punkte, der Reihe nach,
etablieren es entweder rigoros oder enthüllen, wo es übertrieben ist. Nichts anderes
lohnt sich zu bauen, bis dieses Rückgrat hält.

- **1.1 — Die Verschlüsseln-dann-Shamir-Komposition formalisieren.** `[behauptungskritisch]`
  Ein geschriebenes Theorem (oder Gegenbeispiel), das *genau* angibt, was bedingungslos ist
  (der Chiffretext ist unterhalb von `k` verborgen, ohne rechnerische Annahme) und was
  nicht (der Klartext oberhalb von `k` ruht auf dem AEAD). Bestätige, dass der AEAD-Schlüssel nie
  in etwas erscheint, das ein Gegner unterhalb von `k` sieht. **Erledigt:** ein präziser Satz
  je für die bedingungslose und die rechnerische Stufe, beweisbar disjunkt.
  **Aufwand M.**

- **1.2 — Die Untergrenze über das ganze Geheimnis beweisen, nicht ein Byte.** `[behauptungskritisch]`
  Die Brute-Force-Demo des PoC deckt ein *einzelnes Byte* ab; die Eigenschaftstests prüfen
  nur eine Randverteilung. Beweise die gemeinsame Unabhängigkeit beliebiger `k−1` Anteile über das
  vollständige Geheimnis (Standard, bei unabhängigen gleichverteilten Koeffizienten je Position), und füge
  einen Test hinzu, der unter Koeffizienten-Wiederverwendung oder einem RNG niedriger Entropie fehlschlüge. Dokumentiere
  **„die Zufälligkeit der Koeffizienten ist untergrenzen-kritisch"** als erstklassige Anforderung.
  **Erledigt:** zitierter Beweis gemeinsamer Unabhängigkeit + ein Test, der RNG-Versagen fängt.
  **Aufwand S–M.**

- **1.3 — SP-7-Tag: Wiederholung, Fälschung, Drop-übergreifende Verknüpfbarkeit.** `[Stichhaltigkeit]`
  Die Eigenschaft, die nicht versagen darf: zwei Anteile einer Nachricht dürfen niemals einen
  gleichen beobachtbaren Wert über kolludierende Drops tragen. Anteile an verschiedene Drops nutzen
  verschiedene Indizes, also unterscheiden sich die Tags — *beweise*, dass kein `(nonce, index)`-Paar je
  über Drops hinweg wiederverwendet wird, oder behebe es. Außerdem: Nonce-Eigentumsregeln (ein wiederverwendetes
  `msg_nonce` kollidiert sowohl Tags als auch bricht das AEAD katastrophal), und
  Wiederholungs-/Räumungsverteidigungen auf der Speicherschicht. **Erledigt:** Beweisskizze von Kein-gleiches-Tag,
  Nonce-Disziplin in SP-7 geschrieben, Wiederholung am Drop behandelt. **Aufwand M–L.**

- **1.4 — Die Schlüsselableitungs-Disziplin des Rendezvous vereinheitlichen.** `[Stichhaltigkeit]`
  Heute kommt `K_tag` aus HKDF-BLAKE2s, aber `box_id` aus rohem geschlüsseltem BLAKE2s, beide
  auf demselben `kpair` — prinzipienlos. Leite einen Master-PRK aus `kpair` ab, dann
  label-getrennte Unterschlüssel. Spezifiziere die **UTC-Epochengrenzen-Gnadenregel** (ein
  Absender, der um 23:59 ablegt, und ein Empfänger, der um 00:01 pollt, dürfen keine Post verpassen —
  ein echter Zustellbug). Begründe die 16-Byte-Breite von `box_id`. **Erledigt:** eine KDF-
  Disziplin, die Epochen-Gnadenregel, regenerierte Vektoren. **Aufwand M.**

---

## Stufe 2 — Das zentrale Netzproblem (OP-1) und sein Apparat

Die Untergrenze ist nur *operativ* real, wenn die `n` Pfade wirklich disjunkt sind.
Das aus den eigenen Daten eines Clients zu verifizieren — gegen Relais, die über
alles außer ihren Signaturen lügen — ist das erklärte zentrale Problem des Projekts. Der
tiefste ehrliche Punkt, den die Ergebnisse laut aussprechen müssen: **Vom
Overlay aus kannst du *wahre* Disjunktheit nicht verifizieren, nur Konsistenz gegen einen
Datensatz begrenzten Vertrauens; ein Gegner, der Relais ko-lokalisiert, während er disjunkte
Präfixe bewirbt, ist wahrscheinlich nicht entdeckbar.** Die Aufgabe ist, zu begrenzen, was dieser
Gegner gewinnt, nicht ihn wegzuwünschen.

- **2.1 — Realismus-Durchgang des Simulators.** `[Schlussstein]`
  Heute nutzt `network_sim.py` *Ground-Truth*-AS-Labels — d. h. es nimmt an, dass das
  Verifikationsproblem bereits gelöst ist. Füge hinzu: eine **AS/Jurisdiktions-Inferenz-
  Schicht mit injizierbarem Fehler** (damit „unbekannt ⇒ nimm geteilt an" ausgeübt wird),
  **persistente Wächter** über einen Nachrichtenstrom (ein schlechter Wächter ist monatelang schlecht),
  eine **partielle Gossip-Stichprobe** je Client statt des Gottessicht-Pools, und einen
  **aufgewerteten Gegner** (AS-weite Korrelation, der Drop als Ausgangs-Beobachtungspunkt gezählt,
  optionale Mittel-Hop-Bestätigung). **Erledigt:** Bruch- und Verknüpfungskurven
  als Funktion der Inferenz-Fehlerrate, die zeigen, dass die heutigen Null-Fehler-Zahlen
  optimistisch waren. **Aufwand L.** Entsperrt fast alles weiter unten.

- **2.2 — Das Verifikationsverfahren von Teil 3 entwerfen.** `[Flaggschiff]`
  Die Erweiterung, die das OP-1-Issue verlangt: Gegeben eine Stichprobe, einen Inferenz-Datensatz und
  die Zuversicht je Relais, erzeuge `n` Circuits **und ein maschinenprüfbares
  Zertifikat der erreichten Disjunktheitsstufe, mit einer Zuversicht** — nie eine
  Annahme. Nenne die Grenze ehrlich („disjunkt unter Datensatz D mit Ds Fehler-
  balken"), und benenne den Ko-Lokalisierungs-tricksenden Gegner als erklärten Rest,
  quantifiziert durch 2.1. **Erledigt:** ein feindlicher Implementierer kann den Selektor aus
  dem Text bauen; jede Schwelle zitiert eine Simulator-Zahl. **Aufwand L.** Hängt ab von
  2.1 und 2.3.

- **2.3 — Der vertrauenslose IP-zu-AS-Inferenz-Datensatz.** `[Forschungsrisiko]` `I-3`
  Wie man eine IP-zu-AS-Karte (und grobe Jurisdiktion) ohne eine einzige Autorität
  verteilt und authentifiziert: reproduzierbare Schnappschüsse aus öffentlichen BGP/RIR-Daten, eine
  Art, wie zwei Clients erkennen, dass sie *dieselbe* Karte halten (Inhaltsadressierung +
  Transparenzlog + gegossippte Wurzeln), und eine ehrliche Behandlung des Bootstrap-Paradoxons
  (ein frischer Client holt die Karte über Pfade, die er noch nicht bewerten kann — ein
  Vertrauen-beim-ersten-Gebrauch-Moment). **Verschmelzungsnaht:** die Unterzeichnermenge der Karte und die
  Unterzeichnermenge des Software-Releases (OP-8, Punkt 4.1) wollen vielleicht derselbe
  Mechanismus sein. **Erledigt:** zwei ehrliche Clients halten beweisbar dieselbe Karte oder erkennen,
  dass nicht; die Fehlerrate der Karte speist 2.1s Inferenz-Knopf. **Aufwand XL** —
  das ehrliche Ergebnis mag „TOFU-Karte + Transparenzlog + Anomalie-Gossip" sein, keine
  kanonische Karte.

- **2.4 — Entdeckungs-Robustheit: Sybil und Eclipse (OP-2).**
  Modelliere die abgetastete Sicht unter GR-6/GR-8 mit Gegneranteilen je Quellklasse,
  Fluktuation und der Obergrenze „keine Klasse > ½"; implementiere Eclipse- und Sybil-
  Gegner; prüfe, ob PS-10s „zähle nur verifizierte Relais" die Sybil-Größeninflation
  tatsächlich abstumpft. Dann spezifiziere das Bandbreiten-Sondierprotokoll (GR-7) — eine
  Sonde, die ein Relais misst, ohne den Sondierer preiszugeben oder zu einem DoS-Verstärker zu werden,
  der schwierige Ersatz für Tors Bandbreiten-Autorität, die wir uns selbst versagt haben.
  **Erledigt:** Eclipse-Wahrscheinlichkeits- und Sybil-Inflationskurven; eine baubare Sonden-
  Spezifikation. **Aufwand L.**

---

## Stufe 3 — Die Konstruktionen für eine echte Implementierung härten

- **3.1 — Krypto-Anforderungen der Referenzimplementierung.** `[Stichhaltigkeit]`
  Was ein echter Knoten tun muss, das das Spielzeug auslässt, jedes an eine Bedrohung gebunden:
  **konstantzeitiges GF(2⁸)** (die Tabellennachschläge des PoC sind ein Cache-Timing-Kanal über
  die geheimen Anteil-Bytes — ein Timing-Leck würde genau die Untergrenze untergraben, die das Projekt
  verkauft), **CSPRNG-Disziplin** (die Untergrenze ist genau so stark wie der Koeffizienten-RNG),
  Nonce-/Schlüssel-Rotations-Verwaltung über Neustarts, Persistenz des Wiederholungs-Caches,
  Missbrauchs-Resistenz (die API muss Klartext-ohne-AEAD ablehnen — was der PoC
  selbst derzeit tut), und Speicher-Nullsetzung. **Erledigt:** eine bedrohungsgebundene
  Checkliste, die ein Implementierer erfüllen muss. **Aufwand L.**

- **3.2 — Formale Testvektoren und implementierungsübergreifende Konformität.** `I-1`
  Erweitere `vectors.json`, um jede geschlüsselte Konstruktion abzudecken (HKDF-PRK, Box-IDs
  über Epochen, den Ende-zu-Ende-Pfad Verschlüsseln→Teilen→Ablegen→Pollen→Rekonstruieren→Entschlüsseln,
  Ed25519 + kanonische-CBOR-Einträge, das Noise-Handshake-Transkript, sobald spezifiziert),
  fixiere die GF-Tabellen als normativ, und **vektor-sperre die `k,n`-Nibble-Reihenfolge**
  (die beiden PoC-Parser waren uneins — nun behoben; ein Vektor muss sie
  ehrlich halten). **Erledigt:** eine zweite Implementierung in einer anderen Sprache besteht jeden
  Vektor. **Aufwand M.** Inkrementell: füge Vektoren hinzu, sobald jede Konstruktion sich setzt.

- **3.3 — Den Circuit-Handshake (Noise XK) und seine Forward Secrecy spezifizieren.**
  Die Suite nennt `Noise_XK_25519_ChaChaPoly_BLAKE2s`, aber nichts spezifiziert es,
  und Sphinx macht bereits Hop-weise Schlüsseleinigung — also **wofür ist Noise XK da?**
  Löse die scheinbare Redundanz auf (ein feindlicher Implementierer kann derzeit keinen
  interoperablen Knoten bauen, was I-1 verletzt), nenne die Forward-Secrecy-Eigenschaften und
  das ≤7-Tage-Expositionsfenster des statischen Schlüssels, und entscheide, ob XKs Initiator-Verbergung
  überhaupt nötig ist oder ein einfacheres Muster genügt. **Erledigt:** der Handshake ist
  bis zur I-1-Vollständigkeit spezifiziert, seine Beziehung zu Sphinx eindeutig. **Aufwand L.**

- **3.4 — Gossip-Eintrag-Signaturen und kanonisches CBOR.** `I-1`
  Kanonisches CBOR ist signaturkritisch: zwei Implementierungen, die über die Map-
  Ordnung uneins sind, lehnen die gültigen Einträge der jeweils anderen ab. Fixiere die genaue Kanonisierung,
  schreibe ein striktes Ed25519-Verifikationsprofil vor, und stelle implementierungsübergreifende Vektoren bereit.
  **Erledigt:** Kanonisierung fixiert, Vektoren vorhanden. **Aufwand S.** Parallelisierbar.

---

## Stufe 4 — Governance und Betrieb (schützt das Projekt jetzt und die Nutzer später)

Die Reviews stimmten in einer Rahmung überein: Das Projekt hat **noch keine Nutzer**, was ein
Geschenk ist — das Governance- und Build-Vertrauens-Skelett kann *jetzt* in Ruhe gelegt werden,
während es zu ändern niemanden bricht. Der teure Fehler ist, einen Referenz-Knoten
mit einer Ad-hoc-Update-Geschichte auszuliefern und dann eine autoritätsförmige Migration zu
brauchen, um es zu beheben.

- **4.1 — Update-Governance ohne Kill-Switch (OP-8).** `[wichtigster Nicht-Krypto-Punkt]`
  Ein Entwurfsentscheidungs-Protokoll, das die *Gestalt* fixiert: reproduzierbare Builds sind der Vertrauens-
  anker; Signaturen *lokalisieren* nur einen Build; die Update-Annahme ist client-lokal
  und opt-in, nie ein Push. Die harten 80 % sind menschlich, nicht kryptografisch — *wer* signiert,
  wie sie pseudonym gewählt und ersetzt werden, und wie ein Quorum vermeidet, still
  zur Directory Authority zu werden, die I-3 verbietet. **Die stärkste Antwort mag
  minimalistisch sein:** reproduzierbare Builds + kreuzveröffentlichte Hashes + *kein* Auto-Update
  und *keine* autoritative Unterzeichnermenge, denn jede Unterzeichnermenge ist ein Zwangsziel.
  **Erledigt:** das Dokument übersteht eine feindliche Lesung, die die Hintertür-Autorität jagt;
  die I-3-Selbstprüfung benennt den nicht vertrauten Ersatz für jede Partei. **Aufwand L.**

- **4.2 — Reproduzierbare-Build-Pipeline und Lieferkette.** `I-1, I-3`
  Entwurf (bereit für den Start des Rust-Knotens): Toolchain-Fixierung, ein hermetischer oder
  Nix-artiger Build, ein `rebuild-and-compare`, das ein Fremder ausführen kann, kreuzveröffentlichte
  Attestierungen, ein minimaler und vendorierter Abhängigkeitsbaum, und die explizite
  Versöhnung von „Beitragende müssen pseudonym sein (keine identitätsgebundenen Signierschlüssel)" mit „verifiziere das
  Artefakt" — alles Vertrauen fließt durch Reproduzierbarkeit, keins durch Autoren-Identität.
  **Erledigt:** zwei Parteien auf verschiedenen Maschinen erzeugen hash-identische Artefakte aus dem
  getaggten Quellcode, über ein Verfahren, das keinen vertrauten Singleton benennt. **Aufwand L.**

- **4.3 — Dead-Drop-Ökonomie und Abrufmetadaten (OP-9).**
  Simuliere einen Flutungsangriff mit einem Preisschild (Client-Puzzles vs. die RZ-7-Obergrenzen),
  ehrlich über die Lücke, dass ein Puzzle, das hart genug ist, um ein Botnet abzuschrecken, auf dem
  billigen Telefon, dem das Projekt zu dienen behauptet, unerschwinglich sein mag. Simuliere die
  Polling-Disziplin (RZ-9) gegen einen Drop, der ein Postfach *profiliert*, und ihre Kosten auf
  volumenbasiertem Mobilfunk. **Erledigt:** verteidigte Parameter mit dem Rest in
  Zahlen genannt. **Aufwand M.**

- **4.4 — Betreiber-Exposition und die Neutralitätshaltung.** `[politisch heikel]`
  Ein ehrliches (keine Rechtsberatung) Briefing darüber, was das Betreiben jeder Rolle offenbart und riskiert,
  gestützt auf die wahre Behauptung, dass ein Drop unlesbares Rauschen speichert und ein Relais
  Rauschen fester Größe ohne Clear-Web-Ausgang weiterleitet; plus eine geschriebene Missbrauchs-Handhabungs-
  Haltung — was das Projekt tun und nicht tun wird, wenn das Netz zum
  Schaden genutzt wird, angesichts dessen, dass es den Inhalt *nicht* lesen oder ins Visier nehmen *kann* qua Entwurf, und warum diese
  Unfähigkeit eine Sicherheitseigenschaft ist, keine Ausflucht. **Erledigt:** jede Rolle hat eine
  klarsprachliche Expositionserklärung; die Haltung ist mit der Neutralitäts-
  klausel vereinbar und führt keinen Moderationshebel ein. **Aufwand M.**

---

## Stufe 5 — Die noch ungeschriebenen Schichten

- **5.1 — Chamäleon-Transporte (Teil 4, OP-7).** `[Wettrüsten]`
  Ein Transport-Bedrohungsmodell und eine ehrliche Realismus-Bewertung: uTLS-Fingerabdruck-
  Drift, ECHs Einsatzrealität 2026, aktives Sondieren, Fluss-Korrelation. Das
  ökonomische Argument „mich zu blockieren kostet mehr, als es einbringt" hat echte historische
  Gegenbeispiele — benenne sie, und stelle die unbequeme Frage, ob ein pseudonymes
  Freiwilligenprojekt die Kapazität zur *dauerhaften Wartung* hat, die ein Wettrüsten
  verlangt. Kläre, ob die Anteil-Streuung über diverse Deckungen *hilft* (mehr Deckungs-
  typen) oder *schadet* (mehr Fingerabdrücke, die man falsch machen kann). **Aufwand L.**

- **5.2 — Blackout / Mixed-Mesh-Verbindungsvielfalt (Teil 5, OP-6).** `[Forschungsrisiko]`
  Der größte ungeschriebene Entwurf: Telefone als batteriegebundene Blätter,
  Dualradio-PCs/-SBCs als 802.11s-Rückgrat, und **Streuung über unabhängige Gateways**,
  die I-3 auf den physischen Nachbarschaftsausgang ausdehnt. Die harten Teile: Adressierung
  ohne globale Erreichbarkeit; die Gateway-Unabhängigkeit verifizieren, wenn die AS-Karte
  im Blackout unerreichbar ist und der Standort selbstdeklariert ist (OP-1 kehrt im
  Funkraum wieder); ob das 2048-Byte-Sphinx-Paket stundenlanges
  Store-and-Forward übersteht oder seine eigene Rahmung braucht. Und der nicht reduzierbare Rest, den man
  nennen, nicht lösen muss: **ein Mesh-Knoten in einem heißen Blackout ist eine physisch lokalisierbare Handlung**,
  die kein Overlay verbergen kann — also ist die Mesh-Teilnahme stets eine ausdrückliche
  Zustimmung. **Aufwand XL.**

---

## Dasselbe Problem mit drei Masken

Ein Befund kehrte in allen drei Reviews wieder und verdient, benannt zu werden: die
Unfähigkeit, **die Unabhängigkeit einer Partei ohne Selbstdeklaration zu verifizieren**, erscheint
für *Relais* (OP-1 Pfad-Disjunktheit), für *Release-Unterzeichner* (OP-8 jurisdiktionelle
Vielfalt) und für *Mesh-Gateways* (OP-6 physische Unabhängigkeit). Eine Lösung für
eins mag sich auf die anderen übertragen. Es ist, wohl begründbar, das tiefste offene Problem im
ganzen Projekt — und die ehrliche Antwort in jedem Fall mag ein *begrenzter, erklärter Rest*
statt einer Verifikation sein. Das ist mit der einen Regel über allen
anderen hier vereinbar: **nenne, wo der Schirm endet.**

---

## Vorgeschlagener kritischer Pfad

**Jetzt:** Stufe 0 (0.1–0.4) — berichtige die bekannten Überbehauptungen und den fehlenden Schlüssel.
**Dann das Rückgrat:** 1.1 → 1.2 → 1.3 → 1.4 (I-2 beweisen oder brechen), mit 0.2 (dem
e2e-AEAD) hineingefaltet, da es die echte Kompositions-Demo entsperrt.
**Dann parallel:** 2.1 (Simulator-Schlussstein) und 2.3 (der XL-Datensatz, früh
begonnen) → 2.2 (Flaggschiff-Verifikation von Teil 3); 4.1 (Governance) und 4.2
(reproduzierbare Builds) können jederzeit unabhängig voranschreiten.
**Abschluss:** 2.4, Härtung von Stufe 3, Ökonomie von Stufe 4, dann die ungeschriebenen
Stufen 5.1 und 5.2.

Zwei Punkte tragen eine echte Chance auf ein *teilweises oder negatives* Ergebnis — 2.3 (vertrauenslose
reproduzierbare BGP-Daten sind vielleicht nicht vollständig erreichbar) und 5.2 (ein invariantenerhaltendes
Mesh ist vielleicht nur teilweise erreichbar). Das ist kein Grund, sie aufzuschieben; es ist der
Grund, über sie ehrlich zu sein, in einem Dokument, das keine Glaubensakte verspricht.
