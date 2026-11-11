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
  unten). Wir bemühen uns, den Eingang in angemessener Zeit zu bestätigen; bedenke ein
  pseudonymes, in Freiwilligen-Tempo laufendes Projekt.

Bitte nimm deine rechtliche Identität nicht in eine Meldung auf, es sei denn, du willst sie
öffentlich. Pseudonyme Meldungen sind willkommen und erhalten dieselbe Beachtung.

## Geltungsbereich

Im Geltungsbereich: die Spezifikation in `docs/`, der PoC in `poc/`. Außerhalb: die
Sicherheit des eigenen Geräts oder Kontos eines Beitragenden; die GitHub-Plattform selbst; Denial
of Service gegen dieses Repository.

## Projektschlüssel

Ein PGP-Schlüssel für `scrambnet@proton.me` für verschlüsselte Meldungen wird hier und im
Repository veröffentlicht. Bis ein signierter Schlüssel in dieser Datei aufgeführt ist, behandle
E-Mail als vertraulich-aber-nicht-authentifiziert und hebe die heikelsten Einzelheiten
für einen Kanal auf, den du verifizieren kannst.

## Offenlegung

Koordinierte Offenlegung für alles, was Nutzer eines künftigen Einsatzes gefährden könnte;
sofortige öffentliche Diskussion für alles in diesem Pre-Alpha-Stadium, wo es keine Nutzer zu
gefährden gibt und das Ziel darin besteht, den Entwurf zu brechen, bevor sich jemand auf ihn
verlässt.
