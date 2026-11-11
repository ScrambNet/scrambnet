# Sicherheitsrichtlinie

ScrambNet ist Pre-Alpha: eine Spezifikation und ein Proof of Concept, noch kein System, mit
dem man echte Geheimnisse schützt. Der wertvollste Beitrag, den du leisten kannst, ist ein
Bruch.

## Was als Fund zählt

- Ein Fehler im **Entwurf**: ein Weg, Inhalt unterhalb von `k` erbeuteten Anteilen zu lesen; ein
  Weg, die Anteile einer Nachricht zu verknüpfen (SP-7); ein Eclipse-, Sybil- oder
  disjunktheitsbrechender Angriff auf Entdeckung oder Pfadauswahl; alles, was eine
  Invariante verletzt (I-1…I-4).
- Ein Fehler im Code des **Proof of Concept** unter `poc/`. Beachte, dass der PoC
  bewusst nicht-konstantzeitige Arithmetik und Spielzeugkonstruktionen verwendet; das sind
  dokumentierte Nicht-Ziele, keine Funde. Eine Abweichung von der Spezifikation, oder ein
  Spezifikationsfehler, den der Code aufdeckt, ist ein Fund.

## Wie man meldet

- **Entwurfsfehler und PoC-Probleme, die nicht heikel sind:** öffne ein öffentliches Issue.
  Offene Diskussion ist der Sinn dieses Repositories.
- **Alles, von dem du glaubst, es sollte zuerst privat behandelt werden:** schreibe an
  `scrambnet@proton.me`. Verschlüssele heikle Meldungen mit dem Projektschlüssel (siehe
  unten). Wir bemühen uns, den Eingang **innerhalb von 7 Tagen** zu bestätigen; wenn du
  bis dahin keine Antwort erhalten hast, betrachte sie als in der pseudonymen Verrohrung
  verloren gegangen und melde dich erneut über ein öffentliches Issue (ohne die heikle
  Einzelheit), damit wir es bemerken.

Bitte nimm deine rechtliche Identität nicht in eine Meldung auf, es sei denn, du willst sie
öffentlich. Pseudonyme Meldungen sind willkommen und erhalten dieselbe Beachtung.

## Geltungsbereich

Im Geltungsbereich: die Spezifikation in `docs/`, der PoC in `poc/`. Außerhalb: die
Sicherheit des eigenen Geräts oder Kontos eines Beitragenden; die GitHub-Plattform selbst; Denial
of Service gegen dieses Repository.

## Projektschlüssel

Ein PGP-Schlüssel für `scrambnet@proton.me` ist im Repository als
[`scrambnet-pubkey.asc`](../../scrambnet-pubkey.asc) veröffentlicht. Verschlüssele heikle
Meldungen damit.

```
Fingerprint: E5B5 399D 751F 830D 35CB  5F4A 3087 9F3B F93D 44F7
Algorithm:   Ed25519 (sign) + Cv25519 (encrypt)
Created:     2026-11-11   Expires: 2028-11-10
```

Überprüfe den Fingerabdruck anhand dieser Datei (und idealerweise anhand einer zweiten Kopie
dieses Dokuments auf einem anderen Mirror), bevor du dem Schlüssel vertraust — der Sinn der
Veröffentlichung im Text *und* als eingecheckte Datei ist, dass die beiden übereinstimmen
müssen.

So verwendest du ihn:

```
gpg --import scrambnet-pubkey.asc
gpg --fingerprint scrambnet@proton.me     # muss mit der obigen Zeile übereinstimmen
gpg --encrypt --armor -r scrambnet@proton.me your-report.txt
```

**Rotation (warum der Schlüssel abläuft, Invariante I-3).** Der Schlüssel läuft in zwei Jahren
ab; er ist bewusst kein unsterblicher Einzelschlüssel. Bevor er verfällt, wird der nächste
Schlüssel hier veröffentlicht und **von diesem signiert**, solange dieser noch gültig ist, sodass
die Übergabe überprüfbar ist statt ein Vertrauensakt. Sollte dieser Schlüssel jemals vor Ablauf
verloren gehen oder kompromittiert werden, wird ein Widerrufszertifikat (bei der Erstellung
offline erzeugt und aufbewahrt) hier veröffentlicht und an `keys.openpgp.org` übermittelt, und
ein neuer Schlüssel auf demselben Weg angekündigt. Kein einzelner Offenlegungsschlüssel ist ein
dauerhafter Vertrauensanker.

## Offenlegung

Koordinierte Offenlegung für alles, was Nutzer eines künftigen Einsatzes gefährden könnte;
sofortige öffentliche Diskussion für alles in diesem Pre-Alpha-Stadium, wo es keine Nutzer zu
gefährden gibt und das Ziel darin besteht, den Entwurf zu brechen, bevor sich jemand auf ihn
verlässt.
