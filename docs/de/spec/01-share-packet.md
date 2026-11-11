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
  └─ Ende-zu-Ende-AEAD (Empfängerschlüssel)              [rechnerisch]
       └─ Shamir-Teilung: n Anteile, Schwelle k          [bedingungslose Untergrenze]
            └─ Zwiebel-Verschlüsselung je Anteil, eigener Circuit, Sphinx-Format
                 └─ Chamäleon-Transport (Teil 4)
```

- **SP-1.** Der Absender MUSS (MUST) die Ende-zu-Ende-Verschlüsselung *vor* der Streuung anwenden, und
  die Streuung MUSS (MUST) auf den Ende-zu-Ende-Chiffretext angewandt werden. Mit weniger als `k`
  Anteilen erfährt der Gegner nichts über den Chiffretext, bedingungslos
  (Shamir); mit `k` oder mehr Anteilen steht er immer noch dem Ende-zu-Ende-AEAD gegenüber. Die
  bedingungslose Untergrenze und der rechnerische Gürtel komponieren; keiner ersetzt den
  anderen.
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

## 5. Was dieser Teil nicht entscheidet

Pfadauswahl und Durchsetzung der Disjunktheit (OP-1), Mix-Parameter (OP-5),
Fragmentierung (SP-8), Köder-Ökonomie (SP-9) sind absichtlich offen. Jedes hat ein
nummeriertes Issue; argumentiere dort, mit Zahlen.
