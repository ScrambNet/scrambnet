# ScrambNet-Spezifikation — Teil 1: Anteil-Paket
> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../../en/spec/01-share-packet.md)).

**Status: ENTWURF (DRAFT).** Strohmann-Größen sind mit `(s)` markiert. Greife sie per Anforderungsnummer an.

## 1. Geltungsbereich

Das Anteil-Paket ist die einzige Einheit, die das Overlay kreuzt: es trägt einen Anteil
einer Nachricht durch einen Zwiebel-Circuit. Alles in diesem Teil dient zwei Zielen:
der bedingungslosen Untergrenze (I-2) und der Draht-Uniformität (I-4).

## 2. Schichtung

```
Klartext-Nachricht
  └─ Ende-zu-Ende-AEAD (vorab geteilter Paarschlüssel, SP-1a)  [rechnerisch]
       └─ Shamir-Teilung: n Anteile, Schwelle k          [bedingungslose Untergrenze]
            └─ Zwiebel-Verschlüsselung je Anteil, eigener Circuit, Sphinx-Format
                 └─ Chamäleon-Transport (Teil 4)
```

- **SP-1.** Der Absender MUSS (MUST) die Ende-zu-Ende-Verschlüsselung *vor* der Streuung anwenden, und
  die Streuung MUSS (MUST) auf den Ende-zu-Ende-Chiffretext angewandt werden. Mit weniger als `k`
  Anteilen erfährt der Gegner nichts über den Chiffretext, bedingungslos
  (Shamir); mit `k` oder mehr Anteilen steht er immer noch dem Ende-zu-Ende-AEAD gegenüber. Die
  bedingungslose Untergrenze und der rechnerische Gürtel komponieren; keiner ersetzt den
  anderen. Der Gürtel wird in `poc/e2e.py` durchgängig (Ende-zu-Ende) vorgeführt
  (verschlüsseln → teilen → rekonstruieren → entschlüsseln, fail-closed bei Manipulation).
- **SP-1a (Aufbau des Inhaltsschlüssels und die post-quanten Konsequenz).** Der
  Ende-zu-Ende-AEAD-Schlüssel MUSS (MUST) aus dem **vorab geteilten symmetrischen
  Paargeheimnis** `kpair`, das von der Kontaktkarte getragen wird (Teil 6, RZ-2),
  mittels einer label-getrennten KDF abgeleitet werden:
  `content_key = HKDF-BLAKE2s(kpair, "e2e-content")`, verschieden vom SP-7-Tag-Schlüssel
  und vom Box-ID-Schlüssel, die aus demselben `kpair` abgeleitet werden. Im Inhaltspfad
  DARF ES KEINE (MUST NOT) asymmetrische Schlüsseleinigung geben. Dies ist eine bewusste
  Wahl mit einer tragenden Konsequenz: ein `≥k`-Gegner, der alles aufzeichnet und über
  einen künftigen großskaligen Quantencomputer verfügt, kann den Inhalt dennoch nicht
  lesen, denn es gibt kein Diffie-Hellman-Transkript, das Shor brechen könnte — nur ein
  symmetrisches Geheimnis, das die Parteien bereits teilen, und Grover kostet das AEAD
  höchstens eine Halbierung seiner Schlüsselstärke (daher ist ein abgeleiteter Schlüssel
  mit ≥256 Bit EMPFOHLEN (RECOMMENDED), wo die Reserve zählt). "Harvest now, decrypt
  later" (jetzt ernten, später entschlüsseln) wird daher auf **beiden** Stufen vereitelt:
  unterhalb von `k` durch Shamir (bedingungslos), bei oder oberhalb von `k` durch ein
  symmetrisches AEAD unter einem vorab geteilten Schlüssel (keine Public-Key-Annahme zum
  Ernten). Der ehrliche Preis ist der **Bootstrap**: `kpair` muss den Empfänger zuerst
  über einen vorherigen vertraulichen Kanal erreichen (der außerbandige Austausch der
  Kontaktkarte, Teil 6). Jede verbleibende Public-Key- oder PQ-KEM-Annahme lebt dort, im
  Kartenaustausch — nicht im Inhaltspfad — und einen Kartenaustausch zu tragen, der selbst
  post-quanten ist, ist eine orthogonale, geschichtete Wahl, keine Voraussetzung für die
  Untergrenze. Die AEAD-Suite ist ChaCha20-Poly1305 (Suite `0x01`); `msg_nonce` (SP-7) ist
  die AEAD-Nonce, die die beiden Schichten bindet und eine wiederverwendete Nonce doppelt
  fatal macht (SP-7-Tag-Kollision *und* Verlust der AEAD-Vertraulichkeit — siehe SP-7).
- **SP-2.** Standard-Streuungsparameter für Messaging: `n = 4`, `k = 3` (s).
  Massentransfer-Profile DÜRFEN (MAY) stattdessen Rabins IDA statt Shamir nutzen und MÜSSEN (MUST)
  in der Client-Oberfläche als rechnerisch gekennzeichnet werden, denn IDA hat keine bedingungslose
  Untergrenze (OP-3).

## 3. Draht-Format

- **SP-3.** Jedes Paket auf jeder Verbindung MUSS (MUST) genau `P = 2048` Bytes sein (s).
- **SP-4.** Jedes Byte des Pakets MUSS (MUST) für einen Beobachter ohne die relevanten Schlüssel
  an jedem Hop von gleichverteilt zufällig nicht zu unterscheiden sein (Sphinx-
  Eigenschaft; I-4). Insbesondere gibt es keine Klartext-Version, -Suite, -Länge,
  keinen Hop-Zähler und keinen Anteil-Index.

Anordnung (Größen Strohmann, maximal 3 Hops):

| Feld | Größe (s) | Sichtbar für |
|---|---|---|
| `alpha` — Sphinx-Gruppenelement (X25519) | 32 B | alle (gleichverteilt) |
| `beta` — Sphinx-Routing-Info, 3 × 48 B, aufgefüllt | 144 B | je Hop abgeschält |
| `gamma` — MAC je Hop | 16 B | aktueller Hop |
| `delta` — Nutzlast, je Hop AEAD-umhüllt | 1856 B | Strecke Ausgang → Empfänger |

- **SP-5.** Relais MÜSSEN (MUST) einen Wiederholungs-Cache gesehener `gamma`-Werte je
  Schlüssel-Epoche führen und MÜSSEN (MUST) Wiederholungen still verwerfen (Standard-Sphinx-Wiederholungsabwehr).
- **SP-6.** Relais MÜSSEN (MUST) Pakete in Chargen konstanter Größe mit
  implementierungsdefiniertem Jitter im schnellen Modus ausgeben und MÜSSEN (MUST) der Mix-Strategie
  (Stop-and-Go oder Poisson-Mix, offen) im paranoiden Modus folgen. Die Strategiewahl ist
  OP-5-Gebiet und hier absichtlich ungelöst.

## 4. Anteil-Nutzlast (innerhalb von `delta`, am Ende des Circuits)

Nur vom Empfänger entschlüsselt:

| Feld | Größe (s) | Anmerkungen |
|---|---|---|
| `tag` | 16 B | empfängergeschlüsseltes PRF-Tag, siehe SP-7 |
| `index` | 1 B | Anteil-Index `1..n` |
| `params` | 1 B | gepacktes `k`, `n` (je 4 Bit) |
| `share` | 1792 B | Shamir-Anteil-Bytes |
| `pad` | Rest | zufällig |

- **SP-7 (keine pfadübergreifende Verknüpfbarkeit).** Zwei Anteile derselben Nachricht DÜRFEN NICHT
  (MUST NOT) irgendeinen gleichen oder korrelierbaren Wert tragen, der von jemand anderem als dem
  Empfänger beobachtbar ist. Die Zugehörigkeit zum Anteil-Satz wird nur durch `tag` signalisiert:
  `tag = PRF(K_r, msg_nonce ‖ index)`, wobei `K_r` ein empfängergehaltener Schlüssel ist und
  `msg_nonce` innerhalb der Ende-zu-Ende-Schicht getragen wird. Ein Ausgangsrelais oder eine
  Koalition von Ausgängen DARF NICHT (MUST NOT) erkennen können, ob zwei Pakete zur
  selben Nachricht gehören. Diese Anforderung ist tragend: ohne sie degradiert die Streuung
  zu einer Aufzählungsbequemlichkeit für den Gegner.
- **SP-7a (Anteil-Integrität: akzeptiertes fail-closed-Restrisiko).** Das `tag` sagt,
  *zu welcher* Nachricht ein Paket zu gehören behauptet; es authentifiziert **nicht** die
  `share`-Bytes oder das `params`-Byte (`k,n`). Die Shamir-Rekonstruktion hat keine
  eigene Integrität, sodass ein feindlicher Drop oder Ausgang, der Bits in einem Anteil
  kippt — oder über `k,n` lügt —, einen konsistenten-aber-falschen Klartext-Kandidaten
  erzeugt, den Shamir nicht erkennen kann. Dies wird **eine Schicht höher abgefangen**:
  das Ende-zu-Ende-AEAD (SP-1a) scheitert mit seinem Tag bei jeder beschädigten
  Rekonstruktion, und der Empfänger verwirft die Nachricht, statt auf Müll zu reagieren
  (vorgeführt in `poc/dispersal.py`, Test `test_tampered_share_fails_closed`). Das
  Restrisiko ist daher **kein Verlust der Vertraulichkeit, sondern eine gezielte
  Dienstverweigerung (DoS)**: ein einzelner bösartiger Aussichtspunkt auf einem der `n`
  Anteil-Pfade kann eine bestimmte Nachricht an der Rekonstruktion scheitern lassen, zum
  Preis eines einzigen gekippten Bits. Das Urteil für diesen Entwurf ist, dieses
  Restrisiko zu **akzeptieren und zu dokumentieren**, statt einen MAC je Anteil
  hinzuzufügen, aus zwei Gründen: (1) ein Authentikator je Anteil würde Nutzlast-Bytes
  verbrauchen und einen zweiten zu verwaltenden Schlüssel einführen, ohne die DoS zu
  beseitigen — ein Drop, der einen Anteil beschädigen kann, kann ihn ebenso gut
  *fallenlassen*, und `n−k` solcher Verluste werden ohnehin per Entwurf toleriert; (2) das
  AEAD macht das Scheitern bereits sicher (fail-closed), sodass die offene Frage die
  Verfügbarkeit ist, nicht die Geheimhaltung. Die ehrlichen Gegenmaßnahmen sind Redundanz
  (`n−k`-Reserve), Pfad-Disjunktheit, sodass kein einzelner Aussichtspunkt auf `k` der `n`
  Pfade sitzt (OP-1), und ein erneuter Versuch über frische Pfade. Eine künftige Revision
  DARF (MAY) eine optionale Bindung je Anteil für verfügbarkeitskritische Profile
  hinzufügen; sie wird hier bewusst nicht vorgeschrieben. `k,n` ist vektorverriegelt
  (Nibble-Reihenfolge, Vektoren aus Teil 3 §3.2), sodass eine Implementierung nicht
  *versehentlich* widersprechen kann, nur eine bösartige Partei kann lügen.
- **SP-7b (kein gleicher `tag` über kolludierende Drops hinweg, und Nonce-Eigentümerschaft).**
  Die Eigenschaft, die gelten MUSS (MUST): keine zwei Pakete, die eine Koalition von Drops
  sehen kann, tragen einen gleichen `tag`, es sei denn, der Absender hat ein
  `(msg_nonce, index)`-Paar wiederverwendet. *Argument:* `tag = PRF(K_r, msg_nonce ‖ index)`
  mit `msg_nonce` als festen 8 Bytes und `index` als festem 1 Byte, sodass die PRF-Eingabe
  eine eindeutige Festbreiten-Kodierung von `(msg_nonce, index)` ist — die Abbildung
  `(msg_nonce, index) ↦ input` ist injektiv. Eine geschlüsselte BLAKE2s-PRF liefert gleiche
  Ausgaben nur bei gleichen Eingaben (abgesehen von einer ~`2^-128`-Kollision), also
  implizieren gleiche Tags ein gleiches `(msg_nonce, index)`. Die `n` Anteile einer Nachricht
  teilen ein `msg_nonce`, verwenden aber *verschiedene* Indizes `1..n`, daher verschiedene
  Eingaben, daher verschiedene Tags: eine Koalition von Drops kann zwei Anteile einer
  Nachricht nicht von zwei unverwandten Paketen unterscheiden. Zwei *verschiedene* Nachrichten
  kollidieren einen `tag` nur, wenn sie ein `msg_nonce` wiederverwenden. Daher ist
  **Nonce-Eigentümerschaft ein MUSS (MUST)**: ein Absender DARF NICHT (MUST NOT) ein
  `msg_nonce` unter einem `kpair` wiederverwenden. Wiederverwendung ist doppelt fatal — sie
  kollidiert SP-7-Tags (wodurch ein Anteil-Satz verknüpfbar wird) *und*, weil `msg_nonce` die
  AEAD-Nonce ist (SP-1a), zerstört sie die ChaCha20-Poly1305-Vertraulichkeit (ein Two-Time-Pad,
  festgepinnt durch `test_nonce_reuse_is_detectable_catastrophe`). Ein streng steigender
  Nachrichtenzähler je `kpair` erfüllt dies; der Höchststand (High-Water-Mark) des Zählers
  MUSS (MUST) Neustarts überleben. Auf der Speicherschicht MUSS (MUST) ein Drop eine erneute
  Hinterlegung eines bereits gespeicherten `(box_id, slot)` verwerfen (Replay) und räumt unter
  der Je-Box-Obergrenze das Älteste zuerst aus (RZ-7), sodass eine wiederholte Hinterlegung
  ehrliche Post weder vervielfacht noch über die deklarierte Obergrenze hinaus verdrängt.
- **SP-8.** Eine Nachricht, die die Anteil-Nutzlast (`1792` Bytes, abzüglich
  des 2-Byte-Längenpräfixes) nicht füllt, MUSS (MUST) vor dem Teilen mit Zufallsbytes aufgefüllt werden;
  eine Nachricht, die sie überschreitet, wird auf einer Schicht oberhalb dieser fragmentiert
  (Fragmentierungsentwurf offen, interagiert mit OP-4). Shamirs ehrlicher Preis: jeder
  Anteil ist so lang wie das Geheimnis, also überträgt eine (n, k)-Streuung das ×`n`-fache
  Chiffretext-Volumen (OP-3).
- **SP-9 (Timing).** Der Absender DARF NICHT (MUST NOT) die `n` Anteile als gleichzeitigen
  Ausbruch ausgeben. Anteile SOLLTEN (SHOULD) mit randomisierter Verzögerung je Anteil ausgegeben werden; die
  Verteilung und ihre Kosten an Latenz sind OP-4 und ungelöst. Clients DÜRFEN (MAY)
  Köder-Anteile (Pakete mit zufälligem `tag`) mit einer konfigurierbaren Rate ausgeben.

## 5. Der Circuit-Handshake (es gibt keinen — er ist Sphinx)

Die Suite benannte einst `Noise_XK_25519_ChaChaPoly_BLAKE2s` als einen
"Circuit-Handshake", den nichts spezifizierte — ein I-1-Defekt: ein feindlicher
Implementierer konnte keinen interoperablen Knoten bauen, weil es kein Transkript
gab, das er hätte bauen können. **Die Auflösung besteht darin, die Zeile zu
löschen.** Sphinx führt die Schlüsseleinigung je Hop, die ein Circuit braucht,
bereits durch, sodass ein separater Noise-Handshake ein Überrest ist — höchst­
wahrscheinlich aus der WireGuard-"Noise-Handshake"-Linie ererbt, ohne zu bemerken,
dass Sphinx die Aufgabe bereits verschlungen hatte. Dieser Abschnitt hält diese
Entscheidung fest und spezifiziert normativ den Handshake, der Sphinx *ist*, sodass
I-1 durch Spezifikation erfüllt wird, nicht durch ein zweites Protokoll.

**Die Entscheidung, in einem Absatz.** `alpha` (SP-3, 32 B, X25519) ist ein
*ephemerer Client-Wert pro Paket*; jedes Relais leitet das Hop-Geheimnis aus
`alpha` und seinem statischen `onion`-Schlüssel (GR-2 Schlüssel 2) ab. Das ist
ephemer–statisches Diffie-Hellman je Hop, forward-secret *mit Epochen-Granularität*
(CH-6), relais-authentifiziert durch die Ed25519-Signatur des Gossip-Datensatzes —
genau das, was ein Circuit braucht, und alles, was er braucht. Ein zweiter
zustandsbehafteter `Noise_XK`-Handshake würde dasselbe DH erneut ausführen,
Round-Trips hinzufügen, die ein einmaliger gestreuter Anteil sich nicht leisten
kann, ein zweites Draht-Format auf die Verbindung legen, das I-4 dann waschen
müsste, und **eine** Eigenschaft erkaufen, die Sphinx fehlt: das Verbergen des
statischen Schlüssels des *Initiators*. Der Circuit-Client von ScrambNet hat
**überhaupt keinen statischen Schlüssel** (er ist konstruktionsbedingt anonym),
sodass diese Eigenschaft gegenstandslos ist. `XK` authentifiziert Maschinerie für
einen Schlüssel, der nicht existiert. Sphinx durch XK zu ersetzen (mehr Round-Trips
für weniger), oder XK für einen Seitenkanal zu nutzen (jeder zustandsbehaftete
Client↔Relais-Fluss — Gossip GR-6, Probing GR-12/GR-13 — wird absichtlich *durch*
Sphinx getunnelt, damit der Client unbenannt bleibt, sodass kein solcher Kanal eine
direkte Sitzung will), scheitern beide bei der Prüfung. Die Spezifikation ist besser
dran, wenn die Zeile gelöscht wird.

```
  DER "HANDSHAKE" IST DER SPHINX-HEADER. NICHTS ANDERES EXISTIERT.

  Client (kein Static-Key)   Guard G          Middle M          Exit X
  ─────────────────────     ───────          ────────          ──────
   pro Paket: wähle EINEN ephemeren x ; alpha_0 = x·B   (B = X25519-Basis)
        │
        │  Anteil-Paket  [ alpha_0 | beta | gamma | delta ]   (SP-3)
        │────────────────────────▶│
        │     G: s_G = DH(alpha_0, onion_G) ─► Hop-Schlüssel; eine beta-Schicht abschälen
        │     G: alpha_1 = blind(alpha_0)   (Sphinx-Re-Randomisierung)
        │                          │────────────────▶│
        │                          │  M: s_M = DH(alpha_1, onion_M) ─► Hop-Schlüssel
        │                          │                  │──────────▶│
        │                          │                  │  X: s_X = DH(alpha_2, onion_X)
        ▼                          ▼                  ▼           ▼
   KEINE Handshake-RTT. KEIN zweites Draht-Format. KEINE Noise-Nachricht. Das DH ist
   ephemer(Client)·statisch(Relais) an JEDEM Hop, vollständig in `alpha` getragen.

   Was Noise XK hinzugefügt hätte, und warum es gelöscht ist:
      → e ; ← e,ee,s,es ; → s,se   (zusätzliche RTT, Relais benennt eine Sitzung, und die
      dritte Nachricht trägt den INITIATOR-Statik, den XK zu verbergen existiert — den unser
      schlüsselloser Client nicht hat, sodass nichts zu senden ist und kein Grund, es auszuführen)
```

- **CH-1 (den Überrest löschen).** Suite `0x01` hat **keinen** Noise-Handshake;
  die Suite-Tabellenzeile aus Teil 0 wird entfernt. Eine Implementierung DARF NICHT
  (MUST NOT) irgendeine Noise-Handshake-Nachricht auf einem Circuit aussenden,
  erwarten oder aushandeln; ein Paket, das kein Anteil-Paket aus Teil 1 ist, ist
  nicht Teil dieses Protokolls. *Greife dies an, indem du eine Circuit-Operation
  benennst, die der Sphinx-Header nicht ausführen kann — eine feindliche
  Überprüfung versuchte es und fand keine.*
- **CH-2 (der Circuit-Handshake ist der Sphinx-Header).** Die Schlüsseleinigung je
  Hop MUSS (MUST) die Sphinx-Konstruktion aus SP-3/SP-4 sein: für jeden Hop `i`
  berechnet das Relais `s_i = X25519(alpha_i, onion_i)`, wobei `alpha_i` das
  geblindete Gruppenelement ist, das es empfängt, und `onion_i` sein statischer
  Schlüssel (GR-2 Schlüssel 2). Alle Hop-Schlüssel (Stromchiffre der Routing-Info,
  der `gamma`-MAC, das `delta`-AEAD) MÜSSEN (MUST) aus `s_i` mittels HKDF-BLAKE2s
  mit verschiedenen festen Labels (`"sphinx-rho"`, `"sphinx-mu"`, `"sphinx-delta"`
  — exakte Bytes vektorverriegelt unter Roadmap 3.2) abgeleitet werden. Es gibt
  keine andere Schlüsseleinigung in der Circuit-Schicht.
- **CH-3 (der Initiator ist konstruktionsbedingt schlüssellos).** Ein
  Circuit-Client DARF NICHT (MUST NOT) irgendeinen langlebigen statischen Schlüssel
  auf dem Circuit-Pfad besitzen oder vorzeigen. Sein einziges asymmetrisches
  Geheimnis ist der **ephemere Skalar pro Paket** `x` hinter `alpha_0`, der frisch
  aus einem CSPRNG je Paket entnommen werden MUSS (MUST) (Roadmap 3.1 gilt — die
  nachstehende Forward Secrecy ist exakt so stark wie dieser RNG) und nach dem Bau
  des Pakets vernichtet wird. Ohne statischen Client-Schlüssel hat kein
  Initiator-verbergendes Muster etwas zu verbergen; `XK`/`IK`/`KK` sind alle auf den
  Circuit-Pfad unanwendbar (CH-7).
- **CH-4 (statische Relais-Authentifizierung, ohne Handshake-Signatur).** Ein Client
  MUSS (MUST) den statischen `onion`-Schlüssel jedes Relais *nur* aus einem
  Gossip-Datensatz beziehen, dessen Ed25519-Signatur (GR-2 Schlüssel 7) über die
  kanonische Kodierung — die Schlüssel 2 abdeckt — er verifiziert hat (GR-4). Die
  Relais-Authentifizierung ist **offline und übertragbar**: einmal, wenn der
  Datensatz validiert wird, nicht interaktiv je Circuit. Es DARF NICHT (MUST NOT)
  eine in-Circuit-Relais-Signatur geben (sie wäre ein Selektor und ein
  Draht-Fingerabdruck, I-4). Die ehrliche Grenze: ein Client authentifiziert *den
  Schlüssel*, nicht eine *Identität über diese Signatur hinaus* — das
  Sybil-/Eclipse-Restrisiko lebt in Teil 2 (OP-2, GR-19a/GR-20a), nicht hier.
- **CH-5 (Rotation statischer Schlüssel — das ≤7-Tage-Expositionsfenster).** Ein
  Relais MUSS (MUST) seinen statischen `onion`-Schlüssel mindestens alle `7 days`
  (s) rotieren und MUSS (MUST) die private Hälfte eines ausgemusterten Schlüssels
  nullen (zeroize), sobald die Nachlauffrist für in-Flight-Pakete verstrichen ist;
  ein Relais, das alte Statika behält, vergrößert sein eigenes Expositionsfenster
  und ist nicht konform. Clients MÜSSEN (MUST) einen Datensatz ablehnen, dessen
  `expiry` `created + 7 days` übersteigt (GR-2 Schlüssel 6). Die Rotations-Obergrenze
  wird an beiden Enden durchgesetzt und ist die Obergrenze für das
  Statik-Kompromittierungsfenster (CH-6).
- **CH-5a (die `ee`-Lücke und der Fix, der nicht XK ist).** Eine feindliche
  Überprüfung benannte die eine Eigenschaft, die die Löschung kostet: weil das
  Hop-DH ephemer(Client)·**statisch**(Relais) ist, kann ein Gegner, der den
  Verbindungsverkehr eines Relais aufzeichnet und dann dessen `onion`-Statik
  *innerhalb der laufenden Epoche* ergreift, die Geheimnisse je Hop dieser Epoche
  neu berechnen und die **Verknüpfung** eines Hops für bis zu 7 Tage aufgezeichneter
  Pakete wiederherstellen (niemals Inhalt — CH-6). Ein Noise-`ee` würde selbst das
  verweigern. Dies ist eine echte Regression gegenüber einem *vollständig
  interaktiven* Handshake, aber es ist **kein** Grund, `XK` zu behalten (dessen
  Initiator-Verbergen sie nicht schließt), und ist ohne einen Handshake schließbar:
  ein Deployment, das das Fenster für zu weit befindet, MUSS (MUST) entweder (a) die
  **Rotation** unter 7 Tage **verkürzen** (CH-5 ist eine Obergrenze, kein Ziel) oder
  (b) einen **optionalen Relais-Pre-Key `ee`** hinzufügen — einen kurzlebigen
  ephemeren Pre-Key, im Gossip-Datensatz veröffentlicht, mit **null** zusätzlichen
  Round-Trips in das Hop-Geheimnis gemischt — rotiert und vernichtet, sodass eine
  späte Statik-Ergreifung für dessen Lebensdauer nichts einbringt. Das
  Datensatzfeld des Pre-Keys und seine Rotation gehören zu GR-2, falls ein
  Deployment ihn übernimmt; CH-5a klärt nur, dass die Lücke real, auf Verknüpfung
  begrenzt und ohne den gelöschten Handshake schließbar ist.
- **CH-6 (die Forward-Secrecy-Aussage, präzise).** `[claim-critical]` Ein Gegner,
  der den **statischen** `onion`-Privatschlüssel von Relais `R` zum Zeitpunkt `T`
  kompromittiert (und nichts sonst — Ephemera verließen nie die Clients und wurden
  vernichtet, CH-3): (a) **Vergangener Verkehr ist epochenübergreifend sicher** —
  Pakete, deren Hop an `R` eine frühere, rotierte-und-vernichtete Statik nutzte,
  sind nicht entschlüsselbar (der Schlüssel ist weg, CH-5; der diskrete Logarithmus
  des Client-Ephemers ist weg, CH-3); Forward Secrecy besteht mit
  Epochen-Granularität, wobei die ≤7-Tage-Rotation diese Granularität ist. (b)
  **Innerhalb der laufenden Epoche ist die Exposition die *Verknüpfung* eines Hops,
  niemals Inhalt** — für Pakete, die gesendet wurden, während die ergriffene Statik
  live war, berechnet der Gegner `s_i` für Hops an `R` neu und schält die Schicht
  von `R` ab, wodurch er `R`s Vorgänger/Nachfolger erfährt, d. h. die Metadaten, die
  ein bösartiges Relais ohnehin sieht. Es bringt **keinen** Inhalt ein:
  bedingungslos unterhalb von `k` (I-2, Teil 7), und oberhalb von `k` ist das
  Ende-zu-Ende-AEAD aus einem vorab geteilten symmetrischen `kpair` geschlüsselt,
  ohne DH-Transkript, das der ergriffene Schlüssel berühren könnte (SP-1a). Eine
  ergriffene Statik erkauft *die Verknüpfung eines Hops auf den Paketen einer
  Epoche* — genau die Guard+Exit-Korrelation, die der Streuungs-/Disjunktheitsentwurf
  bereits als *gemildert, nicht beseitigt* behandelt; die Statik zu kompromittieren
  bringt den Gegner nicht weiter, als es das *Betreiben* dieses Relais bereits tut.
- **CH-7 (Initiator-Verbergen wird nicht gebraucht; der Hop ist `N`-förmig, nicht
  `XK`).** `[claim-critical]` Braucht der Client die Eigenschaft von XK, den
  Initiator-Statik zu verbergen? **Nein**, dispositiv: der Client hat keinen
  statischen Initiator-Schlüssel (CH-3), sodass die Eigenschaft gegenstandslos ist.
  Im Vokabular von Noise ist der einmalige Hop eine einseitige Einigung mit
  ephemerem Initiator und bekanntem statischem Responder — die Form von Noise `N`
  (`→ e, es`), nicht `XK`. Der Circuit nutzt keine wörtliche Noise-Nachricht (CH-2:
  es ist Sphinx, das diese Form subsumiert); die zwei Nachrichten, die XK über `N`
  hinaus hinzufügt, tragen nichts und existieren nur, um einen Schlüssel zu
  authentifizieren, den wir nicht haben. Initiator-Verbergen wird von Sphinx bereits
  stärker bereitgestellt (SP-4-Uniformität; der Client ist nie ein Endpunkt, den ein
  Relais benennen kann, GR-12). Wir ersetzten das Initiator-Verbergen von XK durch
  *"der Initiator ist anonym und schlüssellos"*, was kein Muster braucht, um zu
  verbergen, was nicht da ist.
- **CH-8 (Relais↔Relais-Sitzungen, falls überhaupt, sind außerhalb dieses Teils und
  nicht `XK`).** Ein künftiger Steuerungs- oder Peering-Kanal, der eine
  zustandsbehaftete, bidirektionale, gegenseitig authentifizierte Sitzung zwischen
  zwei **benannten** Parteien braucht (z. B. Relais-zu-Relais-Verbindungs­
  verschlüsselung), ist ein separates Dokument und MUSS (MUST) weiterhin I-4
  erfüllen (CH-9). Selbst dort ist `XK` falsch: die Statika beider Relais sind in
  ihren Gossip-Datensätzen **öffentlich**, sodass es nichts zu verbergen gibt und
  ein Muster mit bereits bekannter Statik (`IK`/`KK`) passt. Dieser Abschnitt
  spezifiziert keinen solchen Kanal; er schließt lediglich das reflexartige
  Wieder-Importieren von `XK` aus.
- **CH-9 (I-4 dadurch, kein zweites Draht-Format zu haben).** `[claim-critical]` Die
  Circuit-Schicht legt nichts auf den Draht außer Anteil-Paketen aus Teil 1, jedes
  Byte uniform (SP-4). Es gibt **keine** Noise-Handshake-Nachricht, die man uniform
  machen müsste — das sauberste I-4-Ergebnis, erreicht dadurch, *kein* zweites
  Protokoll zu haben. Ein Noise-XK-Transkript hat erkennbare Struktur
  (Nachrichtenlängen-Muster, `e`/`s`-Public-Key-Felder); XK zu behalten hätte eine
  Verschleierungsanforderung *hinzugefügt*, die die Löschung beseitigt. Jeder
  künftige Sitzungskanal (CH-8) erbt diese Verpflichtung in seinem eigenen Dokument.

**Was Abschnitt 5 nicht entscheidet.** Die Sphinx-Parameter selbst (Gruppe,
Blinding, MAC, exakte HKDF-Labels und Verkettung) sind §3 und die Vektoren von
Roadmap 3.2; CH-2 referenziert sie. Post-Quanten: Suite `0x02` DARF (MAY) das
X25519-Hop-DH durch ein PQ-KEM ersetzen — die *Form* der Forward Secrecy von CH-6
ist unverändert (ephemer + ≤7-Tage-Statik-Rotation), das Primitiv ändert sich, und
die I-2-Inhalts-Untergrenze ist ungeachtet dessen PQ-sicher (SP-1a). Der
Relais↔Relais-Kanal (CH-8) und das optionale Pre-Key-`ee`-Feld (CH-5a) bleiben
künftigen Teilen überlassen. CH-4 authentifiziert einen *Schlüssel, den ein
Datensatz signierte*, nicht eine Identität darüber hinaus: das Gossip-/Eclipse-
Restrisiko ist das von Teil 2 (OP-2).

## 6. Was dieser Teil nicht entscheidet

Pfadauswahl und Durchsetzung der Disjunktheit (OP-1), Mix-Parameter (OP-5),
Fragmentierung (SP-8), Köder-Ökonomie (SP-9) sind absichtlich offen. Jedes hat ein
nummeriertes Issue; argumentiere dort, mit Zahlen.
