# ScrambNet-Spezifikation — Teil 10: Reproduzierbarer Build und Lieferkette
> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../../en/spec/10-reproducible-build.md)).

**Status: ENTWURF (DRAFT).** Dieser Teil entscheidet, wie eine Partei eine
ScrambNet-**Binärdatei** erhält, der sie vertrauen kann, *ohne demjenigen zu
vertrauen, der sie gebaut hat*, unter I-3 — keine Autorität — gegen ein Projekt,
dessen Mitwirkende **pseudonym** sind und daher keine Identität tragen, die ein
Nutzer verifizieren könnte. Es ist das Software-Analogon zu Teil 8: dort wird
einer *Karte* vertraut, weil sie aus öffentlichen Eingaben neu baut; hier wird
einer *Binärdatei* vertraut, weil sie aus öffentlichem Quellcode neu baut.
Strohmann-Werte sind mit `(s)` markiert.

Teil 9 sagt, *was der Code des Knotens tun muss*; dieser Teil sagt, *wie dieser
Code zu einer Binärdatei wird, von der du verifizieren kannst, dass du sie
ausführst*. Lies zuerst §1 und §10: zusammen sagen sie, was dieser Teil einbringt
(Reproduktion, nicht Signatur, als Schiedsrichter) und was er einräumt, nicht
einbringen zu können (eine Hintertür in getreu reproduziertem Quellcode; einen
reproduzierbar fehlkompilierenden Compiler; und, für den Nutzer, der nicht neu
bauen kann, eine Reduktion auf OP-2 — dieselbe Reduktion, mit der Teil 8 endet).

Dieser Teil entscheidet Reproduzierbarkeit als den Vertrauens-**Anker**. Er
entscheidet **nicht**, *wer ein Release signiert oder wie Signierer gewählt und
ersetzt werden* — das ist Punkt 4.1 (OP-8), ein eigener Teil. Die Naht zwischen
ihnen ist §9, und sie spiegelt ID-11/ID-11a von Teil 8 per Verweis.

## 1. Die Entscheidung, in zwei Sätzen

- **Es gibt keine Release-Autorität.** Eine ScrambNet-Binärdatei ist ein
  **reproduzierbares, inhaltsadressiertes Artefakt**, das jede Partei Byte für
  Byte aus getaggtem öffentlichem Quellcode und fixierten öffentlichen Eingaben
  neu baut; zwei Parteien einigen sich, dass eine Binärdatei ehrlich ist, nicht
  weil eine vertrauenswürdige Partei sie signiert hat, sondern weil sie das
  **gleiche `BLAKE2s`** berechnet haben (RB-1, RB-9). Eine von einer festen
  Signierer-Menge gesegnete Binärdatei wäre eine Release-Autorität unter anderem
  Namen, und I-3 verbietet das.
- **Übereinstimmung erfolgt durch Reproduktion; Signaturen *lokalisieren* nur
  einen Build, sie *autorisieren* ihn nie; Vertrauen in einen Build, den der
  Nutzer selbst nicht reproduzieren kann, reduziert sich auf
  Bestätigung-durch-Zählung, was OP-2 ist.** Das ist die ehrliche Gestalt, und
  sie wird vorweg angegeben, nicht vergraben: Für die Partei mit einer
  Baumaschine trägt die Reproduktion das ganze Vertrauen; für das Telefon, das
  nicht neu bauen kann — der modale Nutzer —, ruht Vertrauen auf einer Zählung
  unabhängiger Reproduzierer, genau wie Teil 8s nicht neu bauender Client auf
  einem per Gossip verbreiteten Quorum ruht (RB-7b, §10).

Das ehrliche Ergebnis ist also dasselbe, das Teil 8 für die Karte erreichte:
**reproduziere sie selbst, und das Vertrauen ist autoritätsfrei; kannst du sie
nicht reproduzieren, bist du zurück bei einem Bestätigungs-Quorum, das OP-2
unterliegt.** Alles Weitere unten macht "reproduziere sie selbst und erkenne
jeden, der log" konkret, und §10 ist das Residuum, das keine noch so große
Konstruktion beseitigt.

## 2. Geltungsbereich und die Falle, die dieser Teil vermeidet

Ein pseudonymes Projekt kann den Nutzer nicht bitten, seinen Autoren zu vertrauen
— es gibt keinen Autor, dem zu vertrauen wäre. Der naive "vertrauenslose" Entwurf
ist eine von den Maintainern des Projekts signierte Binärdatei; das importiert
genau die Autorität wieder, die I-3 versagt. Die Falle: Ein Signierer, der still
eine bösartige Binärdatei unter einem vertrauenswürdigen Schlüssel ausliefern
kann, ist der Not-Aus-Schalter, zu dessen Vermeidung Punkt 4.1 existiert.
Vertrauen darf also nicht durch *wer signiert hat* fließen; es fließt durch *baut
sie neu*.

- **RB-1 (keine Release-Autorität; Reproduktion ist der Schiedsrichter).
  [normativ]** Kein Schritt des Erhaltens oder Validierens eines Builds MUSS
  (MUST) darauf vertrauen, dass eine bestimmte Partei ihn kompiliert, signiert
  oder gesegnet hat. Die einzigen vertrauenswürdigen Operationen sind (a) das
  Neuberechnen von `BLAKE2s` und (b) das Neubauen des Artefakts aus getaggtem
  Quellcode und fixierten Eingaben und das Vergleichen. Jedes Entwurfselement, das
  nicht durch einen nicht vertrauten Ersatz ersetzt werden kann, der (a) oder (b)
  ausführt, ist ein Defekt unter I-3 und MUSS (MUST) entfernt oder in §10 erklärt
  werden. (Operation (b), neubauen-und-vergleichen, ist vertrauenswürdig **modulo**
  des Werkzeug-Residuums: Der Build führt den fixierten Compiler aus, den RB-3b als
  "trusting-trust"-Residuum erklärt — der Neubau reduziert das Vertrauen auf den
  Compiler, er beseitigt es nicht. RB-1 ist die Zwei-Operationen-Behauptung,
  gelesen mit diesem Querverweis, nicht ohne ihn.)
- **RB-2 (Reproduzierbarkeit autorisiert; Signaturen lokalisieren nur).
  [normativ]** Dieser Teil entscheidet nichts darüber, *wer ein Release signiert
  oder wie Signierer gewählt und ersetzt werden* — das ist Punkt 4.1. Eine
  Signatur über einen Build, falls überhaupt eine existiert, MUSS (MUST) als
  **Lokalisierer** behandelt werden ("ein Build mit diesem `H_build` wurde hier,
  dann, von dieser pseudonymen Hand angekündigt"), niemals als **Autorisierung**
  ("dies ist der Build, den man ausführen soll"). Ein konformer Client DARF NICHT
  (MUST NOT) einen Build übernehmen, *weil* er signiert wurde; *welchen* Build man
  übernimmt, ist das Anliegen von Punkt 4.1, und es ist client-lokal und
  opt-in. Build-Ehrlichkeit an eine Signierer-Menge zu binden, importiert die von
  I-3 verbotene Autorität wieder (die ID-11a-Regel, für Software).
- **RB-2a (geteilte Werkzeuge, nicht geteilte Autorität).** Dieser Teil DARF (MAY)
  die Transparenz-Log-Konstruktion von Teil 8 (ID-6) und den GR-6-Gossip-Kanal
  wiederverwenden, um Build-Hashes zu veröffentlichen und zu gossippen (RB-14) —
  das Teilen von *Mechanismus* kostet nichts (ID-11a). Er DARF NICHT (MUST NOT)
  mit der Karte eine Menge von Parteien teilen — eine **Signierer- oder
  Log-Anfüger-Liste** —, deren Rolle sowohl für die Karte als auch für den Code
  tragend ist, denn diese Menge wäre der von I-3 verbotene Not-Aus-Schalter, nun
  fähig, sowohl die Geografie-Inferenz als auch die Software umzulegen. Der
  geteilte Log führt keine Autorität ein, **weil** beide Teile Vertrauen durch
  Reproduktion leiten, nicht durch den Log, und der Log erlaubnisfrei bleibt
  (ID-7).

## 3. Die Werkzeugkette, per Inhalt fixiert

- **RB-3 (die Werkzeugkette wird per Inhalt fixiert, nicht per Kanalname).
  [normativ]** Der Build MUSS (MUST) eine *exakte* Werkzeugkette fixieren — ein
  bestimmtes stabiles Release (Strohmann: `rust 1.xx.y` in `rust-toolchain.toml`
  mit `channel = "1.xx.y"`, niemals `stable`/`latest`/`beta`/`nightly`) — **und**
  die Binär-Artefakte dieser Werkzeugkette per `BLAKE2s` im Build-Manifest fixieren
  (RB-8). "Die Werkzeugkette" ist eine Menge gehashter Bytes, kein Name, den ein
  Spiegel unterschiedlich auflösen kann. Ein Neubauer holt die Werkzeugkette von
  **irgendeinem** Spiegel und verifiziert die Hashes (I-3: der Distributor ist
  ersetzbar; die Bytes sind fixiert — das ID-3-Muster, auf den Compiler angewandt).
- **RB-3a (die ganze Kompilier-Fläche fixieren).** Die Fixierung MUSS (MUST) jedes
  Werkzeug abdecken, dessen Ausgabe das Artefakt erreicht: `rustc`, `cargo`, die
  tatsächlich gelinkten vorgebauten `std`/`core`-Bibliotheken, den Linker
  (Strohmann: ein fixiertes `lld`/`mold` (s), nicht das Umgebungs-`ld` des Hosts),
  die libc/den sysroot und jedes Werkzeug, das eine `build.rs` aufruft. Ein dem
  Host überlassenes Werkzeug ist eine nicht fixierte Eingabe und eine
  Determinismus-Gefahr (RB-6, RB-18).
- **RB-3b (der Compiler ist eine geholte Binärdatei — "trusting-trust" ist ein
  erklärtes Residuum). [normativ]** Der fixierte `rustc` ist eine *geholte
  Binärdatei*, nicht etwas, das diese Pipeline aus Quellcode baut. Ihm zu vertrauen
  ist ein **erklärtes Residuum** (§10, "trusting-trust"): RB-3 fixiert, *welche*
  Compiler-Bytes alle verwenden, sodass alle Neubauer dasselbe Residuum teilen und
  jede *Substitution* durch Divergenz erkennbar ist; es macht den Compiler **nicht**
  ehrlich. Fixierung beweist **Provenienz**, nicht **Ehrlichkeit** (siehe RB-18).
  Ein Bootstrap-aus-Quellcode- oder Diverse-Double-Compilation-Pfad, falls je
  übernommen, ist als zukünftige Arbeit benannt, hier nicht erforderlich.

## 4. Der hermetische Build

Der Build ist eine **reine Funktion des Manifests auf ein byte-identisches
Artefakt**. Determinismus ist das ganze Spiel: Können zwei ehrliche Bauer
auseinanderdriften, hört Hash-Gleichheit (RB-9) auf, "gleiche Binärdatei" zu
bedeuten, und ehrliche Bauer werden als Angriff markiert (RB-7, RB-15) — die Lehre
von Teil 8 (ID-4-Präambel), hier unverstanden, wäre fatal.

```
  DER BUILD IST EINE REINE FUNKTION DES MANIFESTS (RB-8)

  ┌──────────────────────── Manifest (RB-8) ────────────────────────┐
  │  Quell-Commit/-Tag · Werkzeugketten-Hashes (RB-3) · Inhalts-    │
  │  Hash jeder Abhängigkeit (RB-5) · feste Umgebung (RB-4b) · Ziel-│
  │  Triple · SOURCE_DATE_EPOCH (abgeleitet, RB-4b) · erwartetes    │
  │  H_build                                                        │
  └────────────────────────────┬────────────────────────────────────┘
                               ▼
            ┌─────────────────────────────────────────┐
            │  HERMETISCHER BUILD (reine Fn, RB-4)    │
            │  kein Netz (RB-4a), kein Host-Zustand,  │
            │  feste Umgebung (RB-4b),                │
            │  Nichtdeterminismus beseitigt gemäß der │
            │  fixierten Gefahrenmenge (RB-6,         │
            │  versioniert per Werkzeugkette)         │
            └───────────────────┬─────────────────────┘
                               ▼
                    Artefakt (für EIN Ziel-Triple)
                               │
                               ▼
              H_build = BLAKE2s(artifact)   ← der EINZIGE Name des Builds (RB-6a)
                                              definiert per (Quellcode, Manifest,
                                              Ziel-Triple) — RB-6b

  Alice ─ gleiches Manifest, gleiches Triple ─▶ H_A   Zwei ehrliche Bauer einigen
  Bob   ─ gleiches Manifest, gleiches Triple ─▶ H_B   sich per gleichem H_build.
                                                      Reproduktion ist der
                                                      Schiedsrichter (RB-7), kein
                                                      Signierer.
```

- **RB-4 (hermetischer, offline-, umgebungsfreier Build). [normativ]** Der Build
  MUSS (MUST) **ohne Netzzugang** und **ohne Umgebungs-Host-Zustand** laufen: kein
  Lesen von `$HOME`, Host-Umgebungsvariablen (über eine explizite Erlaubnisliste
  hinaus, RB-4b), der Systemuhr für irgendeinen eingebetteten Wert, Nutzer-/
  Gruppennamen, Hostnamen, CPU-Zahl, wo sie die Ausgabe beeinflussen würde, oder
  irgendeinem Pfad außerhalb der Sandbox. Konforme Substrate: eine reine
  Nix-/`crane`-Derivation **oder** eine Container-/`bwrap`-Sandbox mit entferntem
  Netz-Namespace und einer festen minimalen Umgebung. Dieser Teil spezifiziert die
  **Eigenschaften** und schreibt keines der Substrate vor (I-1: Ein feindlicher
  Implementierer baut ein konformes Bau-Werkzeug aus den Eigenschaften); Nix und
  ein gesandboxter Container sind als die zwei referenz-konformen Substrate benannt.
  Eine Partei, die ein Substrat übernimmt, MUSS (MUST) *es* ebenfalls fixieren
  (eine Nix-Werkzeugkette ist selbst eine RB-3-Fixierung).
- **RB-4a (kein Netz-Abruf zur Bauzeit, niemals). [normativ]** Der Build DARF NICHT
  (MUST NOT) irgendetwas abrufen — kein Registry-Zugriff, keine
  Git-Abhängigkeitsauflösung, kein `build.rs`-Download, kein Werkzeugketten-Pull.
  Jeder Abruf geschieht *vor* dem hermetischen Schritt, per Hash fixiert, und wird
  über das Manifest hineingereicht. Ein Build, der das Netz *erreichen kann*, ist
  nicht konform, selbst wenn er es zufällig nicht nutzt, weil sein Determinismus
  dann von einem Server abhängt (das ID-4c-Verbot fließender Eingaben, für
  Software).
- **RB-4b (feste, erklärte, abgeleitete Umgebung). [normativ]** Die Bau-Umgebung
  MUSS (MUST) im, und nur im, Manifest fixiert sein: Locale `C`/`C.UTF-8`,
  `TZ=UTC`, umask, die Umgebungs-Erlaubnisliste und `SOURCE_DATE_EPOCH`.
  `SOURCE_DATE_EPOCH` MUSS (MUST) **deterministisch aus dem getaggten Commit
  abgeleitet** werden (das Committer-Datum des fixierten Tags), sodass es eine
  Funktion einer fixierten Eingabe ist, keine frei flottierende Manifest-Behauptung,
  die ein Bauer beliebig setzen könnte. Ein gefälschtes Committer-Datum ist kein
  stiller Gewinn: Es ändert `H_build` und wird daher durch Divergenz gefangen
  (RB-7), genau wie jede andere Eingabeänderung.

## 5. Der Abhängigkeitsbaum

- **RB-5 (minimaler, auditierter, vendorter, inhaltsfixierter Abhängigkeitsbaum).
  [normativ]** Abhängigkeiten MÜSSEN (MUST) (a) *minimiert* sein — jede gegen ihr
  Nichtvorhandensein gerechtfertigt, weil jeder Crate ein nicht vertrauter Autor in
  der Vertrauenskette ist (RB-16, OP-10); (b) *vendort* sein — die exakte Quelle
  jeder transitiven Abhängigkeit in die Build-Eingaben fixiert, nicht live
  aufgelöst (RB-4a); und (c) *per Inhalt fixiert* sein — `Cargo.lock` committet,
  **und** jeder Crate zusätzlich per `BLAKE2s` seiner Quelle im Manifest fixiert
  (RB-8), nicht allein der eigenen Prüfsumme der Registry vertraut. Eine Registry,
  die Bytes unter einem Namen ändern kann, ist eine Autorität; der Inhalts-Hash
  entfernt sie und macht die Registry zu einem ersetzbaren CDN.
- **RB-5a (die Lockdatei ist notwendig, nicht hinreichend).** `Cargo.lock` fixiert
  Versionen und Registry-Prüfsummen; es macht den *Build* für sich allein nicht
  reproduzierbar (Feature-Unifikation, `cfg`, Host-Unterschiede beißen weiterhin —
  RB-6) und entfernt das Vertrauen in die Registry nicht. Die Inhaltsfixierung von
  RB-5 und die Hermetik von RB-4 schließen diese Lücke. Ein Build, der nur die
  Lockdatei fixiert, ist nicht konform.
- **RB-5b (Build-Skripte und Proc-Macros sind vertrautes Rechnen, keine inerten
  Daten). [normativ]** `build.rs`-Skripte und prozedurale Makros führen *zur
  Bauzeit* beliebigen Code aus; sie MÜSSEN (MUST) innerhalb der RB-4-Sandbox unter
  denselben Kein-Netz-/Keine-Umgebung-Regeln laufen, und sie sind für das
  RB-16-Audit genau wie Laufzeit-Code im Geltungsbereich. Ein Proc-Macro, das die
  Uhr oder das Netz liest, ist eine Determinismus-Gefahr und eine
  Lieferketten-Fläche in einem.

## 6. Determinismus-Gefahren und wie der Build sie fixiert

Jede Gefahr unten ist eine Stelle, an der zwei ehrliche Bauer verschiedene Bytes
erzeugen könnten. Der Build MUSS (MUST) jede beseitigen; ein Build, der das nicht
tut, ist nicht konform, weil er RB-9 nicht stützen kann, und seine Divergenz wird
von RB-7 als Angriff fehlgelesen.

- **RB-6 (die Gefahrenmenge ist normativ, versioniert per Werkzeugkette).
  [normativ]** Der Build MUSS (MUST) jede Gefahr in der **fixierten Gefahrenmenge**
  für die verwendete Werkzeugketten-Version beseitigen. Diese Menge ist
  normativ-ab-einer-fixierten-Werkzeugkette, nicht für immer (Residuum §10.7:
  Determinismus ist ein bewegliches Ziel gegen Werkzeugketten-Wandel), und das
  Manifest MUSS (MUST) die Gefahrenmengen-Version referenzieren, gegen die es
  gebaut wurde. Die Menge MUSS (MUST) mindestens fixieren:
  - **Zeitstempel** — `SOURCE_DATE_EPOCH` aus dem getaggten Commit (RB-4b); keine
    mtimes in irgendeinem erzeugten Archiv;
  - **Build-Pfade** — `--remap-path-prefix` auf einen festen `/build`-Wurzelpfad,
    sodass kein absoluter Pfad, `$HOME` oder Nutzername in Debug-Info oder
    Panic-Strings eingebettet wird;
  - **Parallelität und Reihenfolge** — Codegen-Unit-Reihenfolge, Link-Reihenfolge,
    Symboltabellen-Reihenfolge, Archiv-Member-Reihenfolge und jede
    Hash-Map-Iterationsreihenfolge, die die Ausgabe erreicht, MÜSSEN (MUST)
    deterministisch gemacht werden (fixiert oder sortiert);
  - **`-C metadata` / `-C extra-filename`-Ableitung** — deterministisch aus
    fixierten Eingaben abgeleitet, niemals aus einem host-variierenden Wert;
  - **Locale/Kodierung** — `LC_ALL=C`;
  - **Debug-Info und Symbole** — deterministisch, oder gestrippt; falls behalten,
    deterministisch;
  - **randomisiertes Layout und Seeds** — `-Z randomize-layout` aus; jede
    RNG-geseedete Codegen fixiert;
  - **die Archiv-/Paket-Rahmung** — ein fester Codec auf einer festen Stufe, ohne
    Dateinamen, Zeitstempel oder uid/gid in den Container-Metadaten (die
    ID-4d-Kanonischer-Container-Regel, für Software-Paketierung).

  Das Analogon zu Teil 8s nicht fixierter Dekodier-Gefahr (ID-4d-§10-Anmerkung)
  gilt hier und ist benannt, nicht verborgen: **LLVM-versionsabhängige Codegen und
  host-abhängige `cfg`-/Feature-Unifikation** (in RB-5a eingeräumt) sind nur
  reproduzierbar *ab der fixierten Werkzeugkette und der fixierten
  Feature-Auflösung*; jede Werkzeugketten-Anhebung ist eine frische
  Determinismus-Audit-Verpflichtung (§10.7), keine Freifahrt.
- **RB-6a (das Artefakt ist inhaltsadressiert; `H_build` ist sein einziger Name).
  [normativ]** Das Release-Artefakt wird durch `H_build = BLAKE2s(artifact)`
  adressiert (der Suite-Hash, Teil 0). `H_build` ist der einzige maßgebliche Name
  des Builds; eine menschenlesbare Versions-Zeichenkette (`v1.2.3`) ist ein
  Komfort-Etikett und DARF NICHT (MUST NOT) anstelle von `H_build` vertraut werden
  (die ID-2-"der Hash ist der einzige Name"-Regel). Frische — *welche* Version ein
  Client ausführen sollte — ist eine separate Eigenschaft, getragen von RB-8a,
  nicht von der Versions-Zeichenkette.
- **RB-6b (`H_build` ist pro-Ziel; Übereinstimmung ist innerhalb eines Triples
  definiert). [normativ]** Ein Release reproduziert zu *verschiedenen* Bytes pro
  Ziel (`aarch64-linux-android`, `x86_64-unknown-linux-gnu`, `armv7-…`, …) aus
  *demselben* Quellcode, sodass `H_build` eine Funktion von **(getaggter Quellcode,
  Manifest, Ziel-Triple)** ist. Das Manifest MUSS (MUST) das Ziel-Triple fixieren;
  Übereinstimmung (RB-9) ist **nur innerhalb eines festen Triples** definiert; und
  RB-7/RB-15 MÜSSEN (MUST) nur `H_build` gleichen Triples vergleichen. Ein Client,
  der seinen Eigen-Triple-Hash mit einem veröffentlichten Hash eines anderen
  Triples vergleicht, DARF NICHT (MUST NOT) eine Build-Divergenz-Anomalie auslösen —
  das ist ein Kategorienfehler, kein Angriff. Der Teil fixiert außerdem genau,
  welche Bytes `H_build` für jedes ausgelieferte Artefakt abdeckt (die
  Knoten-Binärdatei und, separat, jeder Installer oder jede Bibliothek), sodass zwei
  Neubauer dasselbe Objekt hashen.

## 7. Wie zwei Parteien übereinkommen, dass sie dieselbe Binärdatei halten

- **RB-7 (die Neubau-und-Vergleich-Prozedur eines Fremden). [normativ]** Die
  Prozedur, die eine Partei mit *keiner Beziehung zu irgendeinem Mitwirkenden*
  ausführt, um ein bit-identisches Artefakt zu erhalten und zu verifizieren:
  1. hole den getaggten Quellcode und das Manifest (RB-8) von **irgendeinem**
     Spiegel;
  2. verifiziere jede Eingabe gegen ihr Manifest-`BLAKE2s` (RB-3, RB-5);
  3. führe den hermetischen Build (RB-4) für das Ziel-Triple aus (RB-6b);
  4. berechne `H_build`;
  5. vergleiche per `BLAKE2s`-Gleichheit mit dem veröffentlichten Hash (RB-14) und
     mit dem Hash gleichen Triples eines Peers.

  Gleiches `H_build` ist Beweis derselben Binärdatei; ungleiches ist Beweis, dass
  sie sich unterscheiden, und MUSS (MUST) als **Build-Divergenz** sichtbar gemacht
  werden (RB-15), niemals stillschweigend abgeglichen. Der Streit ist von jedem
  auflösbar, ohne Berufung auf eine Autorität: neu bauen und sehen, was der
  öffentliche Quellcode erzeugt (der ID-5a-Schiedsrichter, für Software). Das ist
  das "erledigt"-Kriterium von 4.2: Zwei Parteien auf verschiedenen Maschinen
  erzeugen hash-identische Artefakte aus dem getaggten Quellcode über eine
  Prozedur, die keinen vertrauenswürdigen Einzelpunkt nennt.
- **RB-7a (ein nicht reproduzierendes Release wird abgelehnt, nicht übertüncht).
  [normativ]** Ein ausgeliefertes Artefakt, dessen `H_build` aus seinem angegebenen
  Manifest nicht reproduziert werden kann, ist per Definition nicht der Build dieses
  Quellcodes: Ein konformer Verifizierer, der neu bauen *kann*, MUSS (MUST) es
  ablehnen und SOLLTE (SHOULD) die Diskrepanz als Build-Anomalie per Gossip
  verbreiten (RB-15). "Es baut auf der Maschine des Maintainers, aber sonst
  nirgends" ist ein Reproduzierbarkeits-Versagen — ein Defekt — kein akzeptabler
  Zustand (die ID-5b-Regel, für Software).
- **RB-7b (der Client, der nicht neu bauen kann — der modale Nutzer). [normativ]**
  Fast jeder echte Nutzer führt den Client auf einem Telefon ohne Werkzeugkette,
  ohne Platte und ohne die Bandbreite aus, den Abhängigkeitsbaum zu kompilieren; er
  *kann* Operation (b) von RB-1 nicht ausführen. Ein solcher Client MUSS (MUST)
  jede Binärdatei, die er ausführt, als **`reproduced-by-others-unverified`**
  führen, bis er (oder ein Peer, dessen `H_build` er dann abgleicht) neu baut, MUSS
  (MUST) Bestätigung als Zählung **unabhängig verifizierter** Reproduzierer unter
  der RB-10-Regel behandeln (niemals eine rohe Attestierungs-Summe), und der Teil
  sagt klar: **Für den nicht neu bauenden Client fließt Build-Vertrauen nicht aus
  Reproduktion — es reduziert sich auf Bestätigung-durch-Zählung, was OP-2 ist**,
  genau wie Teil 8s Karten-Vertrauen sich für den nicht neu bauenden Karten-Client
  auf OP-2 reduziert (§10, ID-5b/§10). Der Client MUSS (MUST) diesen Zustand
  sichtbar machen; er DARF NICHT (MUST NOT) eine nicht neu gebaute Binärdatei so
  darstellen, als hätte der Nutzer sie verifiziert.

## 8. Das Manifest, Übereinstimmung und Frische

- **RB-8 (das Manifest ist das Reproduktions-Rezept). [normativ]** Jedes Release
  MUSS (MUST) ein **Manifest** ausliefern: den Quell-Commit/-Tag, die fixierten
  Werkzeugketten-Hashes (RB-3), den Inhalts-Hash jeder Abhängigkeit (RB-5), die
  feste Umgebung (RB-4b), das Ziel-Triple (RB-6b), `SOURCE_DATE_EPOCH` (abgeleitet,
  RB-4b), die Gefahrenmengen-Version (RB-6) und das erwartete `H_build`. Das
  Manifest — nicht ein Server, nicht eine Person — definiert den Build (das
  ID-3-Manifest, für Software).
- **RB-8a (das Manifest ist kanonisch und inhaltsadressiert; Frische ist ein
  prüfbares Feld). [normativ]** Das Manifest MUSS (MUST) eine **kanonische
  Serialisierung** haben (verwende das kanonische CBOR-Profil von Teil 2 wieder,
  GR-21..GR-30) und ist selbst inhaltsadressiert per
  `manifest-hash = BLAKE2s(canonical manifest)`; andernfalls erzeugen zwei ehrliche
  Parteien verschiedene Manifest-Hashes für dasselbe Rezept, und die
  Log-Bestätigung (RB-14) spaltet sich an einem Formatierungs-Unterschied — die
  GR-21-Lehre unverstanden. Das Manifest MUSS (MUST) einen **monotonen
  Release-Index** tragen, der zusammen mit dem abgeleiteten Committer-Datum gebunden
  ist, und das Transparenz-Log-Blatt (RB-13) MUSS (MUST) diese Ordnung bewahren,
  sodass *Aktualität* eine prüfbare Eigenschaft des Artefakts ist. Das schließt die
  Nahtlücke mit 4.1, die 4.1 nicht später schließen kann (das Manifest-Schema ist
  ein 4.2-Artefakt): siehe RB-9a.
- **RB-9 (Übereinstimmung ist Hash-Gleichheit, nichts weiter). [normativ]** Zwei
  Parteien halten dieselbe Binärdatei **genau dann, wenn** ihre `H_build` gleichen
  Triples gleich sind (RB-6b). Der Vergleich ist eine 32-Byte-Prüfung; er braucht
  keinen Signierer, kein Quorum, keine Autorität (die ID-5-Regel, für Software).
- **RB-9a (Reproduzierbarkeit beweist Binärdatei-passt-zum-Quellcode, nicht
  Quellcode-ist-aktuell — das Frische-Residuum). [normativ]** `H_build`
  authentifiziert, *dass die Bytes zum Quellcode passen*; es sagt nichts darüber,
  *welcher Quellcode der auszuführende ist*. Ein **reproduzierbarer
  Downgrade-Angriff** — einem Client einen alten Tag mit einer bekannten
  Schwachstelle zuzuführen, der perfekt reproduziert und jede RB-Prüfung oben
  besteht — wird **nur** durch eine Frische-Regel besiegt. Dieser Teil liefert die
  prüfbare Eingabe für diese Regel (der monotone Release-Index + das abgeleitete
  Datum von RB-8a, im Log geordnet, RB-13); die *Übernahme-Richtlinie*, die ihn
  nutzt (lehne einen niedrigeren Index ab als einen bereits gesehenen; warne bei
  Veraltung), ist Punkt 4.1 und ist client-lokal. Das Residuum:
  Reproduzierbarkeit allein besiegt Downgrade nicht; das Manifest-Feld, das dieser
  Teil vorschreibt, ist das, was es für 4.1 *möglich* macht, ihn zu besiegen (die
  ID-4-epoch, für Releases).

## 9. Die Verschmelzungsnaht mit der Update-Governance (OP-8 / Punkt 4.1)

Die Release-Signierer und die Wurzel-Veröffentlicher der Karte sehen aus wie ein
Mechanismus. **Position, Teil 8s §9 spiegelnd: sie im Vertrauen getrennt halten,
auch wenn sie Werkzeuge teilen.**

- **RB-10 (eine Attestierung ist eine Reproduktions-Behauptung, gewichtet durch
  unabhängige Re-Reproduktion, nicht durch den Aussteller). [normativ]** Eine
  Build-**Attestierung** ist eine Aussage *"Ich habe Manifest M für Triple T neu
  gebaut und `H_build` erhalten"* — ein **Reproduktionsbericht**, keine
  Autorisierung. Ihr Gewicht kommt davon, **unabhängig prüfbar** zu sein (jeder
  führt RB-7 erneut aus und bestätigt oder widerlegt sie), nicht von der Identität
  des Attestierers: Eine pseudonym signierte Attestierung und eine unsignierte
  tragen **dasselbe** Gewicht, sobald eine dritte Partei die Behauptung reproduziert
  hat; die Signatur *lokalisiert* die Behauptung nur (RB-2). Die Bestätigung MUSS
  (MUST) der Disziplin von Teil 2 exakt folgen: **zähle nur unabhängig verifizierte
  Reproduktionen, niemals eine rohe Attestierungszahl** (die GR-20-/PS-10-"zähle
  nur verifizierte, niemals rohe"-Regel). Und der Teil räumt ein, was GR-19a bereits
  beweist: **Reproduzierer-Unabhängigkeit ist aus Attestierungen allein nicht
  verifizierbar** — du kannst 10 000 Reproduzierer nicht von einer Partei
  unterscheiden, die 10 000 Masken trägt —, sodass eine Reproduzierer-Zählung ein
  *schwaches* Signal ist, das sich auf OP-2 reduziert, und das *starke* Signal ist
  der eigene Neubau des Clients (RB-7). Ein Entwurf, in dem die Annahme einer
  Attestierung von der Identität des Attestierers abhängt, oder in dem eine rohe
  Zählung unverifizierter Attestierungen einen Build bestätigt, ist nicht konform
  (RB-1, und es ist die sybil-wählbare Mehrheits-Autorität, zu deren Verbot RB-10
  existiert).
- **RB-10a (kanonisches Attestierungsformat, Dedup per Reproduzierer). [normativ]**
  Attestierungen überqueren den Draht (RB-14) und speisen eine Zählung (RB-10),
  also MÜSSEN (MUST) sie eine kanonische Kodierung haben (verwende kanonisches CBOR
  wieder, GR-21..GR-30), sonst erzeugen zwei ehrliche Attestierer nicht übereinstim-
  mende Bytes und die Zählung bricht. Attestierungen MÜSSEN (MUST) per
  `(Reproduktions-Identität, M, Triple, H_build)` dedupliziert werden, und das
  Gewicht ist **pro unabhängigem Reproduzierer, niemals pro
  Attestierungs-Byte-String**, sodass ein Gegner die Bestätigung nicht aufblähen
  kann, indem er byte-verschiedene Varianten einer Behauptung prägt
  (Format-Stuffing).
- **RB-11 (die Werkzeugkette muss deterministisch-nutzbar bauen; ein
  Host-übergreifender Testvektor existiert). [normativ]** Weil die fixierte
  Werkzeugkette selbst Nichtdeterminismus einbetten kann (parallele Codegen,
  `OUT_DIR`, Host-Triple in Metadaten), MUSS (MUST) der Teil die Flags und Modi
  fixieren, die sie über Hosts hinweg identische Ausgabe erzeugen lassen (RB-6), und
  ein **Host-übergreifender Build-Testvektor** (Manifest → erwartetes `H_build` für
  ein festes Triple) MUSS (MUST) existieren, damit eine zweite Maschine beweisen
  kann, dass sie das identische Artefakt reproduziert (die
  ID-4d-Karten-Testvektor-Regel; bindet an die Konformitäts-Harness von Roadmap
  3.2). Das ist das RB-Analogon zu RI-1b von Teil 9: *Ein bestandener funktionaler
  Test beweist, dass die Binärdatei läuft, nicht, dass sie bit-identisch ist* —
  Reproduzierbarkeit wird per neubauen-und-vergleichen geprüft, niemals aus "es
  kompilierte" angenommen.
- **RB-12 (Mitwirkende sind pseudonym; Vertrauen fließt nur durch
  Reproduzierbarkeit). [normativ]** ScrambNet hat **keine identitätsgebundenen
  Signierschlüssel** und keine vertrauenswürdige Autoren-Identität. Vertrauen in
  eine Binärdatei MUSS (MUST) **vollständig** aus (a) dem öffentlichen und
  überprüfbaren Quellcode (I-1) und (b) der Binärdatei, die aus diesem Quellcode
  reproduziert (RB-7), stammen — **niemals** aus *wer* sie geschrieben, committet,
  getaggt oder signiert hat. Ein Schritt, der eine vertrauenswürdige Autoren-,
  Maintainer- oder Signierer-Identität verlangt, um einen Build zu akzeptieren, ist
  sowohl unter RB-1 als auch unter der Pseudonymitätsregel des Projekts nicht
  konform. Das ist die Auflösung der zentralen Spannung dieses Teils: *dem Autor
  wird durch Konstruktion nicht vertraut; der Binärdatei wird durch Reproduktion
  vertraut.*
- **RB-12a (wofür Pseudonym-Schlüssel da sind — und die Vorbedingung, auf der sie
  ruhen).** Ein Mitwirkenden-Schlüssel, falls überhaupt genutzt, authentifiziert
  *Kontinuität eines Pseudonyms* und *lokalisiert* Arbeit (dieser Commit, diese
  Attestierung kam von derselben pseudonymen Hand) — eine Bequemlichkeit für Gossip
  und für die Lokalisierer-Rolle von 4.1 (RB-2), niemals eine Wurzel des
  Build-Vertrauens. Das Verlieren, Rotieren oder Ersetzen eines solchen Schlüssels
  DARF NICHT (MUST NOT) irgendeine Binärdatei invalidieren, die noch reproduziert.
  Ein Halter eines kompromittierten Schlüssels kann keine bösartige-aber-
  reproduzierende Binärdatei ausliefern, die **einen ehrlichen Überprüfer plus einen
  ehrlichen Reproduzierer überlebt** — aber dieser Schutz ist *deren Existenz*,
  nicht der Schlüssel: Fehlt ein ehrlicher Überprüfer des Quellcodes (I-1) und ein
  ehrlicher Reproduzierer, den der Client erreichen kann (RB-7/RB-10), *kann* der
  kompromittierte Schlüssel eine bösartige Binärdatei an einen Client ausliefern,
  der weder überprüft noch neu baut (RB-7b). Der Schutz reduziert sich also auf I-1
  (Überprüfung) und OP-2 (Erreichbarkeit eines ehrlichen Reproduzierers); er ist
  keine bedingungslose Eigenschaft des Schlüssels. (Dies gibt die Vorbedingung
  explizit an, damit die Behauptung nicht zirkulär ist.)
- **RB-12b (Reproduzierbarkeit beweist Binärdatei-passt-zum-Quellcode, sagt nichts
  über Quellcode-Ehrlichkeit).** Reproduzierbarkeit und Überprüfung sind
  **orthogonale Achsen**. Reproduzierbarkeit beweist, dass die Binärdatei zum
  Quellcode passt; sie sagt nichts darüber, ob der Quellcode ehrlich ist.
  Pseudonymität (RB-12) entfernt "ein vertrauenswürdiger Autor bürgte für den
  Quellcode", sodass Quellcode-Ehrlichkeit auf **öffentlicher Überprüfung (I-1)**
  und nichts sonst ruht. Der Teil sagt das klar, damit kein Leser "reproduzierbar"
  mit "sicher" oder "überprüft" verwechselt: Ein getreu reproduzierter Build von
  hintertürigem Quellcode ist eine getreue Reproduktion einer Hintertür (§10,
  OP-10).
- **RB-13 (Hashes und Manifeste werden in einen erlaubnisfreien Log veröffentlicht,
  geordnet nach Release-Index).** Release-Tupel
  `(Triple, H_build, manifest-hash, release-index, committer-date)` SOLLTEN (SHOULD)
  in dieselben erlaubnisfreien, anfügbaren (append-only) Transparenz-Logs
  angekündigt werden, die für Karten genutzt werden (ID-6/ID-7), unter Bewahrung der
  RB-8a-Ordnung, sodass Build-Ankündigungen zeitgestempelt und
  Equivocation-erkennbar sind mit **keinem privilegierten Anfüger** (ID-7). Der Log
  *segnet* einen Build nicht — das tut die Reproduktion (RB-7) — er macht
  "verschiedene Binärdatei verschiedenen Leuten gezeigt" erkennbar und gibt der
  Frische (RB-9a) eine bezeugte Ordnung. Gemäß RB-2a ist die Log-*Konstruktion* mit
  der Karte geteilt; die *Instanzen/Mengen* SOLLTEN (SHOULD) unabhängig bleiben
  (ID-7b "mehrere Logs, kein kanonischer"), sodass die zwei Verfügbarkeits-Domänen
  nicht in einen einzigen tragenden Betreiber kollabieren.
- **RB-14 (das Build-Tupel gossippen; Split-View erkennen). [normativ]** Clients
  und Neubauer SOLLTEN (SHOULD) `(Triple, H_build, manifest-hash, release-index)`
  über GR-6 unter GR-8-Quellenmischung gossippen und
  Transparenz-Log-Konsistenzbeweise verlangen, sodass ein Gegner, der Binärdatei X
  an Alice und Binärdatei Y an Bob ausliefert (gleiches Triple, gleicher oder
  widersprüchlicher Index), von jeder Partei gefangen wird, die beide hält (die
  ID-7a-Equivocation-Verteidigung, für Builds). Ein Log, der Build-Anfügungen hinter
  eine Signierer-Menge sperrt, ist nicht konform (RB-2a/ID-7).
- **RB-15 (Build-Anomalien werden gegossippt, nicht unterdrückt). [normativ]** Vier
  Ereignisse sind Build-Anomalien, die jeder Verifizierer bei Erkennung gossippen
  MUSS (MUST), unter Vergleich nur von Hashes gleichen Triples (RB-6b): (a) ein
  `H_build`, das die Reproduktion aus seinem Manifest scheitern lässt (RB-7a); (b)
  ein Transparenz-Log, der inkonsistente Wurzeln über Build-Ankündigungen vorlegt
  (bewiesene Equivocation); (c) eine persistente `H_build`-Divergenz gleichen
  Triples gegen unabhängige Reproduzierer; (d) eine **Release-Index-Regression** —
  ein Tag, der mit einem niedrigeren Index vorgelegt wird als einem bereits für jene
  Release-Linie bezeugten (die Downgrade-Signatur, RB-9a). Ein Verifizierer DARF
  NICHT (MUST NOT) eine Anomalie unterdrücken, um ein Release gesund aussehen zu
  lassen (die ID-10-Immunsignal-Regel, für Builds).

## 10. Was dieser Teil nicht löst (das erklärte Residuum)

Dieser Teil lässt zwei Parteien, die *beide neu bauen*, beweisbar übereinstimmen
oder beweisbar erkennen, dass sie sich unterscheiden, und er verschiebt Vertrauen
von *wer sie gebaut hat* auf *baut sie neu* — eine echte und große Reduktion, die
richtige für ein pseudonymes Projekt. Er macht die Binärdatei **nicht** *sicher*.
Die Lücken sind real und werden erklärt, nicht geglättet:

- **§10.1 — Eine Hintertür in einer fixierten Abhängigkeit wird getreu reproduziert,
  nicht gefangen.** Enthält ein vendorter Crate feindlichen Code, erhält jeder
  Neubauer die identische bösartige Binärdatei und RB-7 *bestätigt* die
  Übereinstimmung — die Reproduktion arbeitet genau wie entworfen und ist blind für
  die Bosheit. Die Binärdatei spiegelt ehrlich Quellcode, der ehrlich hintertürig
  ist. Die einzigen Verteidigungen sind **öffentliche Überprüfung (I-1), Audit
  (RB-16) und das Minimieren der Abhängigkeits-Fläche (RB-5/RB-17)** — menschliche
  Prozesse, die die Fläche *begrenzen*, keiner eine autoritätsfreie kryptografische
  Prüfung. **Das ist das primäre Residuum, es hat keinen nicht vertrauten Ersatz,
  und es ist das wiederkehrende Problem des Projekts in seiner vierten Maske —
  OP-10.** Das Wertversprechen ist genau hier ehrlich: Reproduzierbarkeit
  verteidigt **nicht** gegen den wahrscheinlichsten realen Angriff und war nie dazu
  gedacht — aber sie ändert, *welche Art* Angriff erforderlich ist. Ohne sie
  vergiftet ein Angreifer **eine Binärdatei für ein Ziel**, unsichtbar und nicht
  zuordenbar. Mit ihr muss eine bösartige Binärdatei auf **öffentlichen Quellcode**
  zurückführbar sein, den **jeder überprüfen kann** und der **für jeden identisch
  reproduziert** — was den Angriff von "vergifte die Binärdatei" (unsichtbar,
  pro-Ziel) zu "vergifte den öffentlichen Quellcode oder eine öffentliche
  Abhängigkeit" (überprüfbar, universell, dem einen ehrlichen Überprüfer maximal
  ausgesetzt) zwingt. Diese Transformation ist der Wert des Teils; den vergifteten
  Quellcode zu fangen ist OP-10 und I-1, nicht Reproduzierbarkeit.
- **§10.2 — Eine kompromittierte Werkzeugkette, die reproduzierbar fehlkompiliert.**
  Ein hintertüriger `rustc`/LLVM kann Verhalten einfügen, das im Quellcode fehlt,
  deterministisch, sodass jeder Neubauer die identische schlechte Binärdatei
  reproduziert und `H_build`-Gleichheit hält. Fixierung (RB-3) lässt alle einen
  Compiler teilen und macht sein *Austauschen* erkennbar; sie macht den fixierten
  Compiler nicht ehrlich. **Kein nicht vertrauter Ersatz** diesseits von
  Bootstrap-aus-Quellcode oder Diverse-Double-Compilation, die dieser Teil als
  zukünftige Arbeit benennt (RB-3b), keine aktuelle Anforderung.
- **§10.3 — "Trusting-trust" (Thompson).** Der allgemeine Fall von §10.2: ein
  Compiler, der hintertürt *und* die Hintertür in Compiler propagiert, die er baut.
  Die Compiler-Bytes zu fixieren bricht die Schleife nicht; es garantiert, dass
  jeder in *derselben* Schleife ist. Erklärt, nicht gelöst. (Deshalb sagt RB-18
  "jedes Ausgabe-Byte führt auf eine *fixierte* Eingabe zurück" — Provenienz — und
  ausdrücklich **nicht** "auf eine ehrliche Eingabe": Ein gehashter, fixierter,
  hintertüriger Compiler erfüllt Nachverfolgbarkeit und ist dennoch bösartig.)
- **§10.4 — Reproduzierbar ≠ sicher; reproduzierbar ≠ überprüft.** Ein perfekt
  reproduzierbarer Build von ehrlich-aussehendem-aber-subtil-falschem Quellcode ist
  perfekt reproduzierbar. Pseudonymität (RB-12) bedeutet, dass kein
  vertrauenswürdiger Autor für den Quellcode bürgt, sodass Quellcode-Ehrlichkeit
  vollständig auf öffentlicher Überprüfung (I-1) ruht; Reproduzierbarkeit und
  Überprüfung sind orthogonal (RB-12b).
- **§10.5 — Bestätigung-durch-Zählung reduziert sich auf OP-2; der nicht neu
  bauende Client ist der modale Nutzer.** "N unabhängige Neubauer erhielten
  `H_build`" ist nur so stark wie die *Unabhängigkeit* der N (RB-10, GR-19a). Eine
  einzige ehrliche Re-Reproduktion widerlegt eine falsche Behauptung mit Gewissheit
  (stärker als der Karten-Fall, da Quellcode deterministisch ist), aber ein Client,
  der **nicht neu bauen kann** (RB-7b — das Telefon, d. h. fast jeder Nutzer), lehnt
  sich an die Attestierungszahl, die ein sybil-wählbares Quorum ist: Ein Gegner
  prägt pseudonyme Attestierungen für ein schlechtes `H_build`, und ein
  **eklipster** Client sieht nur Gegner-Attestierungen und trifft nie einen
  ehrlichen Reproduzierer. Für den nicht neu bauenden oder eklipsten Client bedeutet
  "keine Autorität" also "vertraue dem Quorum verifizierter Reproduzierer", und das
  hält nur so weit wie **OP-2**. Dieser Teil **reduziert** Build-Autorität für den
  nicht Neubauenden auf OP-2; er löst sie nicht auf — die identische Reduktion, mit
  der Teil 8 endet (ID-1 → OP-2).
- **§10.6 — Der Schiedsrichter ist lebendigkeits-begrenzt; der Treuhand-Speicher
  muss repliziert sein, sonst ist er ein Einzelpunkt.** Neubauen-und-vergleichen ist
  der autoritätsfreie Schiedsrichter **nur, solange die fixierten Eingaben noch
  abrufbar sind**. Die Werkzeugketten-Binärdateien und der volle Crate-Baum sind
  groß und vergänglich: Ein **zurückgezogener Crate** oder ein **depubliziertes
  Werkzeugketten-Release** macht `rebuild(manifest)` nicht ausführbar, und dann ist
  die eine vertrauenswürdige Operation weg — am schlimmsten für genau die
  forensischen Streitfälle ("war v1.2 hintertürig?"), die sie am meisten brauchen.
  Eine konforme Bereitstellung SOLLTE (SHOULD) die fixierten Eingabe-Bytes in einem
  inhaltsadressierten Speicher hinterlegen, der **über dieselbe erlaubnisfreie
  Spiegel-Menge** wie die Builds repliziert wird; ein Einzel-Replika-Treuhand ist
  inhaltsadressiert (er kann also nicht *lügen*), aber er ist ein
  **Lebendigkeits-Einzelpunkt** (er kann *verschwinden*), und I-3 deckt
  Lebendigkeit. Fehlt Replikation, ist RB-7 als **lebendigkeits-begrenzt** erklärt,
  nicht unbedingt (das ID-5a-Lebendigkeits-Residuum, für Builds).
- **§10.7 — Determinismus ist ein bewegliches Ziel gegen Werkzeugketten-Wandel.**
  Neue `rustc`/LLVM-Versionen führen neue Nichtdeterminismus-Quellen ein (neue
  parallele Durchläufe, neue Metadaten, neues `cfg`-Verhalten). Die Gefahrenmenge
  von RB-6 ist **aktuell**, nicht abgeschlossen; eine fixierte Werkzeugkette ist
  *wie fixiert* reproduzierbar, aber jede Werkzeugketten-Anhebung ist eine frische
  Determinismus-Audit-Verpflichtung, und das Manifest hält fest, gegen welche
  Gefahrenmengen-Version es gebaut wurde (RB-6, RB-8). "Einmal reproduzierbar"
  bedeutet nicht "für immer reproduzierbar".
- **§10.8 — First-Build-TOFU: Eine bösartige erste Binärdatei lügt darüber, sich
  selbst zu reproduzieren.** Die *erste* Client-Binärdatei eines frischen Nutzers
  kann nicht reproduziert werden, bevor sie zum Bootstrappen genutzt wird (du
  brauchst einen funktionierenden Client, um den Quellcode, die Werkzeugkette zu
  holen und die Logs und Peers zu erreichen). Die erste Binärdatei wird auf
  Trust-on-First-Use übernommen, genau wie Teil 8s erste Karte (ID-8) — und
  schlimmer: Eine kompromittierte erste Binärdatei besitzt danach den gesamten
  Reproduktions- und Gossip-Apparat des Nutzers, sodass sie **über ihre eigene
  Reproduktion lügen** kann ("Ich habe mich selbst neu gebaut; `H_build` passt").
  Ein Client kann daher seine *eigene* Reproduktion nicht ehrlich verifizieren;
  Vertrauen in die erste Binärdatei ruht auf einem **außerbandigen unabhängigen
  Reproduzierer** — einer anderen Maschine/Werkzeugkette, der der Nutzer mehr
  vertraut als der zu testenden Binärdatei. Das ist die "trusting-trust"-/
  kompromittierter-Host-Grenze (§10.9); es ist ein erklärtes Residuum, hier
  angegeben statt still von "außerhalb des Geltungsbereichs" verschluckt.
- **§10.9 — Was dieser Teil nicht einmal versucht.** Laufzeit-Kompromittierung der
  Maschine des Nutzers; ein bösartiger *Build ehrlichen Quellcodes durch den Nutzer
  selbst* auf einem kompromittierten Host (die Reproduktion bestätigt die
  Übereinstimmung; der Host besitzt dennoch den Prozess); und alles oberhalb der
  Artefakt-Grenze — Installation und Update-*Übernahme* (welchen Build man wann
  ausführt), was Punkt 4.1 ist. Der Teil ist nur bit-identisches-Artefakt; er
  benennt diese als außerhalb des Geltungsbereichs, nicht als gelöst.

Die ehrliche Zusammenfassung: Reproduzierbare Builds verschieben Vertrauen von *wer
sie gebaut hat* auf *baut sie neu* — echt und groß. Aber sie sind **stumm** dazu,
ob der Quellcode ehrlich ist (§10.1, §10.4), **blind** für eine reproduzierbare
Compiler-/Abhängigkeits-Hintertür (§10.1, §10.2, §10.3), **lebendigkeits-begrenzt**
als Schiedsrichter (§10.6), **auf OP-2 reduziert** für den nicht neu bauenden oder
eklipsten Client (§10.5) — den modalen Nutzer (RB-7b) — und **TOFU** auf der ersten
Binärdatei (§10.8). Das ist der Preis dafür, eine Release-Autorität zu verweigern.
Die richtige Antwort ist, sie zu begrenzen — die vertraute Rechenbasis minimieren
und auditieren, den Treuhand-Speicher replizieren, unabhängige Neubauten fördern,
den Frische-Index mitführen — und sie anzugeben, nicht zu verbergen.

## 11. Lieferketten-Hygiene, die das Residuum begrenzt

- **RB-16 (Abhängigkeits- und Werkzeugketten-Audit ist verpflichtend und im
  Geltungsbereich).** Weil die Reproduktion eine Hintertür nicht sehen kann, die
  jeder Neubauer getreu reproduziert (§10.1), MUSS (MUST) der Teil einen committeten,
  überprüfbaren Audit-Pfad für die Abhängigkeitsmenge und die Werkzeugkette
  verlangen (`cargo-vet`-/`cargo-audit`-artige Aufzeichnungen, per Inhalt fixiert),
  behandelt als **Überprüfungs-Evidenz (I-1), nicht als Autorität**. Das Audit
  reduziert die §10.1-Angriffsfläche; es entfernt sie nicht, und der Teil sagt das.
- **RB-17 (die vertraute Rechenbasis minimieren).** Der Teil SOLLTE (SHOULD)
  verlangen, aktiv zu verkleinern, was vertraut-und-auditiert sein muss: weniger
  Abhängigkeiten (RB-5), weniger `build.rs`/Proc-Macros (RB-5b), eine kleinere
  Werkzeugketten-Fläche (RB-3a), `#![forbid(unsafe_code)]` wo machbar — weil jedes
  Element der vertrauten Rechenbasis ein §10.1-Residuum ist, das das Audit abdecken
  muss und die Reproduktion nicht kann. Ehrliche Anmerkung: "minimal" ist nicht
  "klein" — ein echter async + crypto-Knoten (eine async-Laufzeit, ein
  Sphinx-/X25519-Stack, CBOR, …) schleppt *Hunderte* transitiver Crates mit, viele
  mit Build-Skripten, sodass das §10.1-Abhängigkeits-Hintertür-Residuum kein
  Randfall, sondern die **erwartete** Angriffsfläche ist. Das ist die ehrliche
  Einordnung von OP-10.
- **RB-18 (die ganze Kette ist fixiert, oder sie ist nicht fixiert — und fixiert
  bedeutet Provenienz, nicht Ehrlichkeit). [normativ]** Eine einzige nicht fixierte
  Eingabe irgendwo — eine nicht gehashte Werkzeugketten-Komponente, eine flottierende
  Abhängigkeit, eine `build.rs`, die den Host liest, ein per Tag geholtes
  Container-Basis-Image — macht die Reproduzierbarkeits-Behauptung für das ganze
  Artefakt ungültig, weil diese eine Eingabe einen Server oder einen Host als
  vertrauenswürdige Partei wiedereinführt (RB-1). Das Manifest MUSS (MUST)
  **vollständig** sein: Kann ein Ausgabe-Byte nicht auf eine *fixierte* Eingabe
  zurückgeführt werden, ist der Build nicht konform (die ID-4c-Regel, für Software).
  **Das ist eine Determinismus-/Provenienz-Behauptung, keine Vertrauens-Behauptung:**
  Eine fixierte Eingabe kann bösartig sein (§10.1, §10.2, §10.3); Fixierung macht die
  Bosheit für jeden identisch und jede *Abweichung von einer ehrlichen Eingabe*
  erkennbar — sie macht die Eingabe **nicht** ehrlich. "Fixiert" bedeutet niemals
  "sicher".

## 12. Hier eingeführte Anforderungen

- **RB-1 / RB-2 / RB-2a** — keine Release-Autorität, Reproduktion ist der
  Schiedsrichter; Signaturen lokalisieren nur, autorisieren nie; geteilte Werkzeuge
  mit der Karte, niemals geteilte Autorität.
- **RB-3 / RB-3a / RB-3b** — Werkzeugkette per Inhalt fixiert über die ganze
  Kompilier-Fläche; der fixierte Compiler ist ein erklärtes "trusting-trust"-Residuum
  (Provenienz, nicht Ehrlichkeit).
- **RB-4 / RB-4a / RB-4b** — hermetischer, offline-, umgebungsfreier Build; kein
  Abruf zur Bauzeit; eine feste Umgebung mit `SOURCE_DATE_EPOCH`, das aus dem
  getaggten Commit **abgeleitet** ist.
- **RB-5 / RB-5a / RB-5b** — minimaler, vendorter, inhaltsfixierter
  Abhängigkeitsbaum; Lockdatei notwendig-nicht-hinreichend; Build-Skripte und
  Proc-Macros sind gesandboxtes vertrautes Rechnen.
- **RB-6 / RB-6a / RB-6b** — normative, werkzeugketten-versionierte
  Nichtdeterminismus-Gefahrenmenge; `H_build` ist der einzige Name; `H_build` ist
  pro-(Quellcode, Manifest, Ziel-Triple) und Übereinstimmung ist innerhalb eines
  Triples.
- **RB-7 / RB-7a / RB-7b** — das Neubauen-und-Vergleichen des Fremden; das
  Unreproduzierbare ablehnen; der nicht neu bauende modale Nutzer führt
  `reproduced-by-others-unverified` und reduziert sich auf OP-2.
- **RB-8 / RB-8a / RB-9 / RB-9a** — das Manifest ist das Rezept, kanonisch und
  inhaltsadressiert, mit einem monotonen Release-Index; Übereinstimmung ist
  Hash-Gleichheit gleichen Triples; das Frische-Residuum (reproduzierbarer
  Downgrade) mit dem Manifest-Feld, das 4.1 braucht.
- **RB-10 / RB-10a** — eine Attestierung ist eine Reproduktions-Behauptung,
  gewichtet durch unabhängige Re-Reproduktion (zähle nur verifizierte, niemals rohe;
  Unabhängigkeit ist OP-2); kanonisches Format, Dedup per Reproduzierer.
- **RB-11 / RB-12 / RB-12a / RB-12b** — Host-übergreifender Build-Testvektor;
  Vertrauen fließt nur durch Reproduzierbarkeit; Pseudonym-Schlüssel lokalisieren,
  wurzeln nie Vertrauen (mit explizit gemachter, nicht-zirkulärer Vorbedingung);
  Reproduzierbarkeit ⊥ Überprüfung.
- **RB-13 / RB-14 / RB-15** — erlaubnisfreier Log von Build-Tupeln, geordnet nach
  Release-Index; Gossip + Split-View-Erkennung; vier obligatorische Anomalien
  einschließlich der Downgrade-Signatur.
- **RB-16 / RB-17 / RB-18** — verpflichtendes Audit als Überprüfungs-Evidenz;
  minimiere die TCB (die immer noch groß ist); die ganze Kette fixiert, wobei
  fixiert Provenienz ist, nicht Ehrlichkeit.

RB-1 und RB-7 sind die tragenden zwei: keine Autorität, und Reproduktion ist der
Schiedsrichter. Beide sind begrenzt, nicht absolut — RB-1 reduziert sich für den
Client, der nicht neu baut, auf OP-2 (§10.5, der modale Nutzer), und RB-7 ist
lebendigkeits-begrenzt (§10.6). Das schärfste Residuum, angegeben und nicht
verborgen, ist §10.1: **Reproduzierbarkeit fängt keine hintertürige Abhängigkeit,
die der wahrscheinlichste reale Angriff ist — sie zwingt den Angriff in
öffentlichen, überprüfbaren, universellen Quellcode, was der Punkt ist, und ihn
dort zu fangen ist OP-10, nicht dieser Teil.** Brich diesen Teil, indem du einen
Build-Schritt benennst, der eine vertrauenswürdige Partei braucht, ein
ausgeliefertes Artefakt, das aus seinem Manifest nicht neu gebaut werden kann, eine
Determinismus-Gefahr, die RB-6 übersieht, einen Weg, auf dem eine Signatur
Autorisierung an RB-2 vorbei zurückschmuggelt, oder einen Weg, auf dem der nicht
neu bauende Client einer Mehrheit vertrauend zurückgelassen wird, die nicht OP-2
ist. Das ist die Einladung, in der Stimme von Teil 8.
