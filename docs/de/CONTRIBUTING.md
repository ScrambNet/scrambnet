# Zu ScrambNet beitragen

Das Projekt befindet sich im Stadium vor der Spezifikation. Die wertvollsten Beiträge im
Moment, der Reihe nach:

1. **Greif das Bedrohungsmodell an.** Öffne ein Issue gegen jede Behauptung in
   [docs/threat-model.md](threat-model.md), besonders gegen die Liste der offenen Probleme.
2. **Schlag Spezifikationstext vor.** PRs gegen `docs/` — im RFC-Stil, ein Mechanismus pro PR.
3. **Übersetze.** Die READMEs gibt es in sechs Sprachen; `docs/` ist bisher nur auf Englisch.
   Übersetzungen und Korrekturen durch Muttersprachler sind erstklassige Beiträge.
4. **Hinweise auf Vorarbeiten.** Wenn hier etwas das Rad neu erfindet, nenne das Rad. Die
   Entwurfsphilosophie ist, veröffentlichte, angegriffene Arbeit zu komponieren, niemals zu
   erfinden, wo eine Quellenangabe genügt.

## Wie wir arbeiten

- Ein Thema pro Issue. Entwurfsdebatten leben in den Issues, Entscheidungen werden in `docs/`
  festgehalten.
- Englisch ist die kanonische Sprache von `docs/`; wenn du ein README in einer Sprache
  bearbeitest, aktualisiere entweder die anderen oder sag in der PR, dass sie nun veraltet sind.
- Kein Code, bis sich das Bedrohungsmodell und die Wire-Spezifikation stabilisiert haben.
  Wenn der Code beginnt: ein einziger kleiner, langweiliger, mobile-first Referenz-Client.

## Pseudonymitätsrichtlinie

Echte Namen sind nicht erforderlich und werden es nie sein. Pseudonyme und anonyme Beiträge
sind erstklassig. Es gibt kein CLA; mit deinem Beitrag gibst du deinen Beitrag zur
Dokumentation unter [CC0 1.0](LICENSE) frei.

Wenn dein eigenes Bedrohungsmodell es verlangt, schütze dich:

- Verwende die noreply-Adresse deiner Forge in Commits:
  `git config user.email "USERNAME@users.noreply.github.com"`
- Commit in UTC, damit deine Zeitzone nicht durchsickert:
  `git config alias.ci '!TZ=UTC git commit'`
- Signiere Commits nicht mit einem Schlüssel, der an deine rechtliche Identität gebunden ist;
  wenn du signierst, verwende einen Schlüssel, der allein für dieses Pseudonym erstellt wurde.
- Verwende keine Spitznamen von anderswo wieder, und denk daran, dass der Prosastil ein
  Fingerabdruck ist.

## Neutralität

Dieses Netz transportiert Pakete, keine Meinungen. Es schützt Dissidenten und ihre Gegner mit
derselben Mathematik; politische Gegner sind keine Feinde. Vorschläge, die das Netz bestimmte
Sichtweisen, Herkünfte oder Ziele bevorzugen oder benachteiligen lassen würden, werden
unabhängig von der Sichtweise abgelehnt — diese Neutralität ist das Sicherheitsargument des
Projekts ebenso wie seine Ethik.
