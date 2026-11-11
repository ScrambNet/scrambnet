# ScrambNet-Spezifikation — Teil 7: Das Sicherheitsargument für I-2
> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../../en/spec/07-security-argument.md)).

**Status: ENTWURF (DRAFT).** Dieser Teil beweist oder begrenzt die eine Behauptung, auf der alles andere ruht: die bedingungslose Inhalts-Untergrenze (I-2). Er ist normativ, wo er eine Anforderung angibt (`SA-n`), und erläuternd im Übrigen. Ist das Argument hier falsch, ist das Projekt falsch, und der schnellste Weg, das herauszufinden, ist, *diese Datei* anzugreifen.

Die Behauptung ist bewusst eng gefasst. Lies zuerst die zwei Sätze in §1; alles danach ist ihre Rechtfertigung und ihr Preis.

## 1. Was bewiesen wird, in zwei Sätzen

- **Bedingungslose Stufe (die Untergrenze).** Ein Gegner, der beliebige `k−1` der `n` Anteile einer Nachricht beobachtet, erfährt **nichts** über den Ende-zu-Ende-Schlüsseltext — nicht "nichts Machbares", sondern überhaupt nichts, gegen unbeschränkte Berechnung und jeden künftigen Quantencomputer — weil die `k−1` Anteile *statistisch unabhängig vom Geheimnis* sind (Shamir, bewiesen in §3).
- **Rechnerische Stufe (der Gürtel).** Ein Gegner, der `k` oder mehr Anteile erlangt, rekonstruiert den Schlüsseltext und steht dann dem Ende-zu-Ende-AEAD gegenüber; von da an ist die Inhaltsvertraulichkeit genau die Vertraulichkeit von ChaCha20-Poly1305 unter einem Schlüssel, den der Gegner nicht besitzt (SP-1a), was **eine** rechnerische Annahme ist.

Diese beiden Stufen sind **disjunkt und erschöpfend**: Jeder Gegner hält entweder `< k` Anteile (Stufe 1) oder `≥ k` (Stufe 2), und die Garantie in jeder ist ohne Bezug auf die andere formuliert. Der Rest dieses Teils beweist Stufe 1 rigoros, gibt präzise an, warum Stufe 2 nicht bedingungslos sein kann, und fixiert die eine Stelle, an der die beiden Stufen ineinander durchsickern könnten (§4: der AEAD-Schlüssel muss unterhalb von `k` unsichtbar sein).

## 2. Modell und Gegner

- Eine **Nachricht** ist eine Byte-Zeichenkette `M`. Der Absender berechnet zuerst den Schlüsseltext `C = AEAD-Seal(K, N, M)` (SP-1a), wobei `K = HKDF(kpair, "e2e-content")` und `N` die Nachrichten-Nonce ist. `C` — niemals `M` — ist das, was in die Streuung eingeht.
- Die Streuung ist `(n, k)` Shamir über GF(2⁸), **je Byte**: Für Byte-Position `j` ist das Geheimnis-Byte `c_j` der konstante Term eines unabhängigen, gleichverteilt zufälligen Polynoms vom Grad `(k−1)` `f_j`, und Anteil `i` an Position `j` ist `f_j(i)` für verschiedene von null verschiedene Auswertungspunkte `x_1,…,x_n ∈ GF(2⁸)\{0}` (die Anteil-Indizes). "Unabhängig, gleichverteilt" ist tragend und ist selbst eine Anforderung (SA-3 unten).
- Der **Unter-`k`-Gegner** sieht: beliebige `k−1` vollständige Anteile (jede Byte-Position dieser `k−1` Indizes) sowie alles Öffentliche — die Spezifikation, die Auswertungspunkte, `n`, `k`, die Draht-Bytes anderer Pakete. Er sieht **nicht** `K`, `N` oder irgendeinen Anteil über seine `k−1` hinaus. Er verfügt über unbeschränkte Berechnung.
- Wir beweisen eine Eigenschaft von `C` (dem Schlüsseltext). Was der Gegner letztlich will, ist `M`; §4 zeigt, dass sich das Ergebnis auf `C`-Ebene auf `M` überträgt, weil `K` nicht in der Sicht des Gegners liegt.

## 3. Die Untergrenze: beliebige `k−1` Anteile sind unabhängig vom Geheimnis (Stufe 1)

**SA-1 (perfekte Geheimhaltung je Byte).** Fixiere eine Byte-Position `j`. Sei das Geheimnis-Byte `s = c_j` und das Polynom `f_j(x) = s + a_1 x + … + a_{k−1} x^{k−1}` mit `a_1,…,a_{k−1}` unabhängig und gleichverteilt über GF(2⁸). Für jede Menge von `k−1` verschiedenen von null verschiedenen Punkten `x_{i_1},…,x_{i_{k−1}}` und beliebige Zielwerte `y_1,…,y_{k−1}`:

> ist die Anzahl der Koeffizienten-Tupel `(a_1,…,a_{k−1})`, die mit `f_j(x_{i_t}) = y_t` für alle `t` konsistent sind, **genau eins, für jeden Kandidaten `s`**.

*Beweis.* Fixiere `s`. Die `k−1` Gleichungen `f_j(x_{i_t}) = y_t` sind linear in den `k−1` Unbekannten `a_1,…,a_{k−1}`; ihre Koeffizientenmatrix ist die Vandermonde-Matrix auf den verschiedenen von null verschiedenen Punkten `x_{i_t}` (Spalten `x, x², …, x^{k−1}`), die über dem Körper invertierbar ist. Also gibt es für jedes `s` genau eine Lösung. Daher ist `Pr[shares = (y_1,…,y_{k−1}) | secret = s]` für jedes `s` gleich (`= 1 / 256^{k−1}`): die Anteile sind **unabhängig von `s`**. ∎

Dies ist die Aufzählung, die der PoC per Brute Force für `k = 3` ausführt (`poc/dispersal.py`, `floor_demo()` — alle 256 Kandidaten-Bytes kommen gleich konsistent zurück, jeweils auf genau eine Weise). SA-1 ist die allgemeine Aussage dessen, was diese Demo für einen Fall prüft.

**SA-2 (das ganze Geheimnis, nicht ein Byte — gemeinsame Unabhängigkeit).** Sei der Schlüsseltext `C = c_1 c_2 … c_L` (alle `L` Bytes). Der Absender zieht die Koeffizienten-Tupel für die `L` Positionen **unabhängig** (SA-3). Dann ist die vollständige `k−1`-Anteil-Sicht — die Byte-Zeichenketten der Länge `L`, die an `k−1` Indizes gehalten werden — *gemeinsam* unabhängig von `C`:

> `Pr[view = v | C = c]` ist für jedes `c ∈ (GF(2⁸))^L` identisch.

*Beweis.* Die Sicht faktorisiert über die Positionen: Die Bytes, die der Gegner an Position `j` sieht, hängen nur von `(c_j, a^{(j)}_1,…,a^{(j)}_{k−1})` ab, und über die Positionen hinweg sind die Koeffizientenziehungen unabhängig (SA-3). Also ist `Pr[view = v | C = c] = ∏_{j=1}^{L} Pr[view_j = v_j | c_j]`, und nach SA-1 ist jeder Faktor gleich `1/256^{k−1}`, unabhängig von `c_j`. Das Produkt ist daher `1/256^{(k−1)L}` für **jedes** `c`. Die Unabhängigkeit von `C` folgt. ∎

SA-2 ist der Schritt, den die alten Tests des PoC **nicht** abdeckten: `floor_demo()` ist ein Byte, und die statistischen Tests prüften nur eine Randverteilung (die Verteilung einer Position). Das Argument des Produkts über die Positionen ist das, was die Untergrenze zu einer Aussage über die *Nachricht* macht, und es gilt **nur, weil** die Koeffizienten je Position unabhängig sind — was genau der Fehlermodus ist, den SA-3 absichert.

**SA-3 (Koeffizienten-Zufälligkeit ist untergrenzen-kritisch). [normativ]** Die Polynom-Koeffizienten `a^{(j)}_t` MÜSSEN (MUST) aus einem kryptografisch sicheren RNG gezogen werden, unabhängig sowohl über den Koeffizienten-Index `t` als auch die Byte-Position `j`. Die Untergrenze ist genau so stark wie diese Zufälligkeit und nicht stärker:

- **Wiederverwendung über Positionen** (z. B. ein Koeffizienten-Tupel für jedes Byte wiederverwendet, oder ein kurzer sich wiederholender Schlüsselstrom von Koeffizienten) bricht die Unabhängigkeit von SA-2: Die Faktorisierung scheitert, die `k−1` Anteile werden mit `C` *korreliert*, und ein Gegner kann Information über `C` gewinnen, indem er Positionen kreuzkorreliert. Eine auf wiederverwendeten Koeffizienten aufgebaute Untergrenze ist keine Untergrenze.
- **RNG mit geringer Entropie** (ein schwacher oder vorhersagbarer Generator) lässt die gleichverteilte Ziehung von SA-1 zusammenbrechen: Kann der Gegner die Koeffizientenverteilung vorhersagen oder aufzählen, ist die Zählung "genau ein konsistentes Tupel je `s`" nicht mehr gleichverteilt über `s`, und die Anteile sickern durch.

Dies ist die einzelne wichtigste Implementierungsanforderung in der gesamten Spezifikation. Sie ist billig zu erfüllen und katastrophal, wenn man sie falsch macht, und anders als eine AEAD-Schwäche kann sie nicht durch späteres Rotieren eines Schlüssels behoben werden — eine unter schlechten Koeffizienten aufgeteilte Nachricht ist für immer kompromittiert. Eine konforme Implementierung MUSS (MUST) den Koeffizienten-RNG als ihre Komponente mit der höchsten Sicherheitszusicherung behandeln (siehe auch die Referenz-Krypto-Anforderungen, roadmap 3.1).

## 4. Die Naht: der AEAD-Schlüssel muss unterhalb von `k` unsichtbar sein (kein Durchsickern zwischen Stufen)

SA-2 beweist, dass die `k−1` Anteile unabhängig vom **Schlüsseltext `C`** sind. Der Gegner will den **Klartext `M`**. Die Brücke ist, dass `M = AEAD-Open(K,N,C)` und der Unter-`k`-Gegner `K` nicht besitzt. Das ist nur dann wahr, wenn `K` niemals in irgendetwas auftaucht, das dieser Gegner sieht — was eine Anforderung ist, kein Zufall:

**SA-4 (Schlüsseltrennung über die Untergrenze). [normativ]** Kein durch einen Unter-`k`-Gegner ableitbarer Wert darf `K = HKDF(kpair, "e2e-content")` oder `kpair` offenbaren. Insbesondere:

- `K` DARF NICHT (MUST NOT) in irgendeinen Anteil, ein Tag oder ein Paketfeld gelegt werden. (In diesem Entwurf ist es das nicht: `K` wird nur an den Endpunkten verwendet, um `C` zu versiegeln und zu öffnen; die Anteile tragen Bytes von `C`, und das SP-7-Tag wird aus einem *label-getrennten* Schlüssel `HKDF(kpair, "tag")` abgeleitet, nicht aus `K` — siehe §5 und SP-7a.)
- Daher ist die Sicht eines Unter-`k`-Gegners unabhängig von `C` (SA-2) **und** trägt keine Information über `K`. Er kann weder `C` lesen (dort ist nichts) noch `K` erlangen, um ein künftiges `C` anzugreifen. Die beiden Stufen sickern nicht ineinander durch.

Wäre SA-4 verletzt — wäre irgendein unter-`k`-beobachtbarer Wert eine Funktion von `K` —, so würde die Untergrenze *dieses* `C` immer noch verbergen, aber der Gegner könnte `K` ernten und es in dem Moment lesen, in dem er später `k` Anteile erlangt, oder *andere* Nachrichten unter demselben `K` lesen. SA-4 ist das, was verhindert, dass die bedingungslose Stufe stillschweigend rechnerisch wird.

## 5. Warum Stufe 2 rechnerisch ist, ehrlich formuliert

Bei `k` oder mehr Anteilen rekonstruiert der Gegner `C` exakt (Lagrange-Interpolation — dies ist der *beabsichtigte* Weg, so liest der Empfänger die Post). Von `C` aus ist die Vertraulichkeit von `M` genau die Vertraulichkeit von ChaCha20-Poly1305 unter `K`. Das ist eine rechnerische Annahme: Sie kann im Prinzip durch Kryptanalyse der Chiffre gebrochen werden. Sie wird **nicht** durch einen künftigen Quantencomputer via Shor gebrochen, weil `K` aus einem vorab geteilten *symmetrischen* Geheimnis stammt, ohne Diffie-Hellman-Transkript, das zu invertieren wäre (SP-1a); Grover kostet höchstens eine Halbierung der effektiven Schlüssellänge, daher die Empfehlung von ≥256 Bit. Die ehrliche Aussage zu Stufe 2 lautet also: *so stark wie ein symmetrisches AEAD unter einem Schlüssel, den der Gegner nicht hat, und nicht stärker* — eine echte, konventionelle, quantenbewusste rechnerische Garantie, keine bedingungslose. Das Projekt behauptet nie etwas anderes, und jedes öffentliche Dokument gibt nun das Regime an (roadmap 0.1).

## 6. Was dieser Teil **nicht** beweist

- **Verknüpfung / Metadaten.** I-2 betrifft den Inhalt, nicht, wer mit wem spricht. Nichts hier verbirgt, dass *irgendein* Fluss auf einem erfassten Anteil-Pfad stattfand; das ist das eingeräumte Residuum des Bedrohungsmodells, durch die Streuung verengt, nicht aufgehoben.
- **Verfügbarkeit.** Eine feindliche Partei auf einem Anteil-Pfad kann einen Anteil verfälschen oder verwerfen; das AEAD scheitert geschlossen (SP-7a), also ist dies Dienstverweigerung, keine Offenlegung. SA-1…SA-4 sagen nichts über das *Ankommen* der Nachricht, nur darüber, was ein Unter-`k`-Gegner *erfährt*, falls sie es nicht tut.
- **Zeitliche Korrelation zwischen Anteilen (SP-9 / OP-4).** SA-2 betrifft die *Werte* der Anteile, nicht ihre Emissionszeiten. `n` Anteile, die innerhalb von Millisekunden ins Netz eintreten, sind ein Fingerabdruck, auch wenn ihre Bytes unabhängig von `C` sind. Das ist ein offenes Problem, nicht etwas, das dieser Beweis behandelt.
- **Das AEAD selbst.** Stufe 2 erbt, was auch immer für ChaCha20-Poly1305 gilt. Fällt diese Chiffre, fällt Stufe 2; die Untergrenze (Stufe 1) nicht.

## 7. Hier eingeführte Anforderungen

- **SA-1** — perfekte Geheimhaltung je Byte beliebiger `k−1` Anteile (bewiesen).
- **SA-2** — gemeinsame Unabhängigkeit über das ganze Geheimnis (bewiesen, gegeben SA-3).
- **SA-3** — *Koeffizienten-Zufälligkeit ist untergrenzen-kritisch*: CSPRNG, unabhängig je Position und je Koeffizient. **[normativ, höchste Sicherheitszusicherung]**
- **SA-4** — Schlüsseltrennung über die Untergrenze: kein unter-`k`-beobachtbarer Wert offenbart `K` oder `kpair`. **[normativ]**

SA-1 und SA-2 sind Theoreme; SA-3 und SA-4 sind die beiden Bedingungen, unter denen die Theoreme das reale System beschreiben. Brich eine der vier — finde eine Sicht, die der Beweis übersah, eine Korrelation, die SA-3 durchlässt, ein Feld, das `K` trägt — und du hast I-2 gebrochen. Das ist die Einladung.
