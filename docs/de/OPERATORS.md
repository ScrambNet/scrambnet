# Einen ScrambNet-Knoten betreiben — Exposition und die Haltung der Neutralität

> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../en/OPERATORS.md)).

**Jeden ScrambNet-Knoten zu betreiben ist ein sichtbarer, bewusster Akt mit
realem und von null verschiedenem Risiko.** Dieses Dokument ist darüber
ehrlich. Was folgt, sagt dir, was jede Rolle preisgibt und was sie beweisbar
nicht preisgeben kann, damit du entscheiden kannst. Es ist eine Aussage über
Technik und Haltung, **keine Rechtsberatung**: dieses Projekt ist pseudonym und
kann weder deine Rechtsordnung noch deinen Gegner noch dein Recht kennen. Wo der
Einsatz es rechtfertigt, hole dir deinen eigenen rechtlichen Rat ein.

Dies ist ein informativer Überblick, kein normativer Spezifikationsteil. Er
stützt sich auf Aussagen, die die Spezifikation bereits trifft — die Invarianten
`I-1…I-4`, die Dead-Drop-Regeln (Part 6), die Reste der Pfadauswahl (Part 3),
die Reste des Inferenz-Datensatzes (Part 8) — und er verweist auf sie, statt sie
zu wiederholen. Wo die Spezifikation einen Rest offen erklärt, trägt dieser
Überblick ihn ebenso offen; er beschönigt nicht.

## Was jede Rolle sieht, und was sie nicht sehen kann

Jede Aussage hat dieselbe Form: **was die Rolle sieht · was sie beweisbar nicht
sehen kann, und die genaue Grenze dieser Behauptung · der ehrliche Rest.** Die
Rollen sind jene, die die Architektur definiert („Wer betreibt was“); nichts
hier erfindet eine Rolle, die das Netz nicht hat.

### Reiner Client

Als Client bist du die Rolle mit der geringsten Exposition — „nahezu
unsichtbar“, auf Bridges und Chamäleon-Transporten reitend — aber **nicht mit
null Exposition**, und dieser Überblick wird nichts anderes vorgeben. Dein
**Guard** (dein erster Hop) sieht deine echte IP-Adresse und wann du aktiv bist
(siehe unten); das ist eine clientseitige Exposition, nicht bloß eine
Eigenschaft eines Guards. Auch der Abruf hat laufende Kosten und eine
Metadaten-Oberfläche: ein Client pollt seine Drops nach einem verpflichtenden
festen Zeitplan (`RZ-9`), ~212 MB/Monat über vier Drops, bevor du überhaupt
etwas sendest (`RZ-16b`), und dieser Zeitplan — nicht der Inhalt — ist
beobachtbar. Du bist niedrig exponiert; du bist nicht unsichtbar.

### Guard (der erste Hop eines Clients)

Ein Guard ist das eine Relais, das die echte IP-Adresse eines Clients und das
Timing seiner Aktivität sieht. Wenn du einen Guard betreibst, erfährst du, dass
eine bestimmte IP mit dir ScrambNet gesprochen hat, und wann. Du erfährst
**nicht**, wohin dieser Verkehr ging oder was er enthielt: nach `I-4` ist jedes
Paket, das dich durchquert, Rauschen fester Größe, nicht unterscheidbar von
gleichverteilten Zufallsbytes, und du hältst nur einen Anteil einer Nachricht,
die einen von mehreren Pfaden reist.

Die genaue Grenze von „du kannst die Nachricht nicht rekonstruieren“. Der
Inhaltsboden (`I-2`) ist unbedingt **unterhalb von `k` erfassten Positionen**:
halte weniger als `k` Anteile, und sie sind informationstheoretisch Rauschen,
ohne rechnerisches oder quantenmechanisches Entkommen. Aber *diesen* Boden zu
erreichen hängt davon ab, dass die `n` Pfade echt **disjunkt** sind, und
Disjunktheit ist **gefolgert, nicht bewiesen** (`OP-1`; `PS-11`, „geglaubte
Disjunktheit ist nicht reale Disjunktheit“). Eine gewählte, feindliche Karte
kann die Relais eines Gegners in Position *lenken* und die Inhaltserfassung „von
~0 % auf 100 % bei ~15 % Besitz“ treiben (`PS-12`/`ID-8a` — ein Befund, den das
Projekt offen trägt, nachdem eine frühere Übertreibung gebrochen wurde). Die
ehrliche Behauptung lautet also nicht „ein Guard kann nicht rekonstruieren“,
Punkt; sie lautet „keine Koalition rekonstruiert **unterhalb von `k` erfassten
Positionen**, und ob deine Pfade diesen Boden wirklich erreichen, ist eine
unverifizierte Eigenschaft, die ein lenkender Gegner oberhalb einer Schwelle
besiegen kann.“

**Der ehrliche Rest:** du siehst sehr wohl Client-IPs. Das ist die schärfste
Exposition jeder Relais-Rolle, und sie ist strukturell, kein zu behebendes Leck.
Die IPs von Menschen, die ScrambNet nutzen, laufen durch deinen Knoten und sind
für jeden sichtbar, der seine Verbindungen beobachten kann.

### Mittleres Relais

Ein mittleres Relais sieht keines der beiden Enden. Durch die Sphinx-Konstruktion
und `I-4` kann es nicht erkennen, ob sein Vorgänger der ursprüngliche Client oder
ein weiteres Relais ist, noch ob sein Nachfolger der letzte Hop ist. Es sieht
keine Client-IP (das ist die Position des Guards), kein Ziel, keinen Inhalt; es
hält einen verschlüsselten Anteil. Es ist die Relais-Rolle mit der geringsten
Information — Rauschen, das zwischen zwei anderen Maschinen hindurchgeht. Seine
Exposition ist die allgemeine, die jede Rolle teilt (unten): es zu betreiben ist
ein sichtbarer Akt, und es leitet Verkehr weiter, den du nicht inspizieren kannst.

### Drop (Dead-Drop-Speicher, Part 6)

Ein Drop speichert Anteile, die in Postfächer eingezahlt werden, und liefert sie
aus, wenn gepollt wird. Was er speichert, ist nach `I-2`
informationstheoretisch unlesbar: jeder gespeicherte Anteil liegt unterhalb von
`k` und ist für jeden — **einschließlich dir, dem Betreiber** —
ununterscheidbar von Zufallsrauschen, ohne die anderen Anteile, die auf anderen
Drops liegen, die du nicht kontrollierst (`RZ-5`: kein einzelner Drop hält je
zwei Anteile einer Nachricht; der Drop-Satz ist `d = n = 4`, `k = 3`, also hält
ein Drop genau einen Anteil, `< k`). Du kannst nicht lesen, was du speicherst,
kannst die Inhalte zweier Postfächer nicht auseinanderhalten und kannst eine
Einzahlung keinem Absender zuordnen (`RZ-2`/`RZ-10`, `SP-7`). Diese Behauptung
ist exakt und wird nicht beschönigt: ein Drop-Betreiber ist wirklich
inhaltsblind.

**Inhaltsblind ist nicht dasselbe wie zustellungsneutral, und das ist der
ehrliche Rest.** Ein Drop sieht **Timing**: den öffentlichen Polling-Takt
(`RZ-9`) und die Einzahlungszeiten in die Postfächer, die er hält, innerhalb
einer Epoche; ein Drop, der mehrere Postfächer hält, kann Einzahlungs-*Zeitstempel*
über sie hinweg korrelieren, selbst unter perfekter Poll-Unabhängigkeit
(`RZ-16`/`OP-9`, in der Rendezvous-Spezifikation §9 offen getragen). Und ein
Drop *kann* die **Zustellung** verweigern, ohne irgendetwas zu lesen:
Ältestes-zuerst-Räumung plus das 8-slot-Abruffenster bedeutet, dass ein Flooder
— sogar ein billiges Telefon — ehrliche Post in ~17 Sekunden hinter das Fenster
vergraben kann (`RZ-15`), ein Zustellungs-Flooding-Rest, von dem die
Spezifikation erklärt, dass er noch keine hinreichende Verteidigung hat
(`OP-9`). Also: du speicherst unlesbares Rauschen, aber du beobachtest, *dass*
dieses Rauschen ankam und abgeholt wurde und wann, und die Speichermechanik ist
eine Zustellungsoberfläche. Diese Timing-und-Zustellungs-Exposition ist der echte
Rest des Drops, erklärt und nicht verborgen.

### Bridge (entlang des sozialen Graphen verteilter Einstiegspunkt)

Eine Bridge ist ein Einstiegspunkt, der von Person zu Person weitergereicht wird,
wo das offene Netz blockiert ist (Lox-artige Vertrauensstufen). Sie sieht
Information auf Guard-Niveau für die Clients, die sie erreichen (ihre IP, nichts
stromabwärts). Ihre besondere Exposition ist, **als Bridge auffindbar zu sein**:
ein Zensor, der sich erfolgreich als Nutzer ausgibt, kann die Adresse deiner
Bridge erfahren und sie blockieren oder beobachten. Die Verteilung über den
sozialen Graphen begrenzt, wie schnell und wie weit eine Adresse durchsickert —
„ein Zensor kann sich als ein Nutzer ausgeben; er kann sich nicht als der Freund
von allen ausgeben“ — macht eine Bridge aber nicht unauffindbar.

**Der ehrliche Rest:** eine Bridge zu betreiben bedeutet, dass eine deiner
Adressen bauartbedingt unter Fremden-von-Fremden zirkuliert, von denen einige
Gegner sein können. Die Widerstandsfähigkeit gegen Enumeration ist ein
Wettrüsten, das das Bedrohungsmodell als tragbar bezeichnet, nicht als gewonnen.

### Mesh-Knoten / Gateway (Blackout-Schicht)

Ein Mesh-Knoten leitet Gerät zu Gerät über Wi-Fi Direct / Bluetooth während eines
Blackouts weiter; ein Gateway überbrückt das Mesh zurück ins Internet, wenn eine
Route existiert. Seine Inhaltsexposition ist dieselbe wie bei jedem Relais —
Anteile fester Größe, die es nicht lesen kann (`I-2`/`I-4`). Seine besondere
Exposition ist **physisch und lokal**: seine Sichtbarkeit ist ein Funksignal im
Maßstab der Nachbarschaft, korrelierbar mit einem Ort und möglicherweise einer
Person, genau dann und dort, wo ein Gegner das Internet abgeschaltet hat und am
stärksten motiviert ist. Darum macht die Architektur es stets zu einer
ausdrücklichen Opt-in-Entscheidung. Ein **Gateway** trägt *beide* Expositionen
zugleich: die physisch/lokale Exposition auf der Mesh-Seite **und** die
gewöhnliche Relais-Exposition auf seiner Internet-Seite — seine zum Internet
gewandte IP ist für seinen eigenen ISP ein beobachtbarer ScrambNet-Knoten —,
während es dennoch nie ein Clear-Web-Exit ist (unten).

**Der ehrliche Rest:** von allen Rollen tauscht diese die stärkste
Inhaltsblindheit gegen die schwächste Betreiber-Anonymität. Die Bytes sind
Rauschen; der Sender ist an einem Ort. Keine Invariante schützt die physische
Ortbarkeit eines Funks.

### Der Clear-Web-Exit, den es nicht gibt

ScrambNet hat **keine Clear-Web-Exit-Rolle**, und das zählt für Betreiber am
meisten. Der Clear-Web-Exit ist die am stärksten exponierte Rolle in Tor: die IP
eines Tor-Exits erscheint als die scheinbare Quelle von allem, was seine Nutzer
ins offene Internet senden, und dieser Betreiber erhält die
Missbrauchsbeschwerden, Takedown-Benachrichtigungen und die Aufmerksamkeit der
Strafverfolgung für Verkehr, den er weder gewählt hat noch sehen kann. ScrambNet
hat kein Gegenstück. Der Endhop einer Nachricht stellt einen Anteil in einen
Dead-Drop zu (Part 6) — unlesbares Rauschen in projektinternem Speicher —, nicht
hinaus zu einem beliebigen Dritthost. **Keine Adresse eines ScrambNet-Knotens
erscheint als Ursprung zurechenbaren Verkehrs, der bei einem externen Dienst
ankommt** (das Mesh-Gateway berührt das Internet, aber es trägt
ScrambNet-internes Rauschen zu einem Relais hin, nicht den Verkehr eines Nutzers
hinaus zu einem Clear-Web-Host). Darum erklärt die Architektur, dass die
Exposition eines Relais-/Drop-Betreibers „strukturell geringer als die eines
Tor-Exits“ ist — ein Vergleich der **technischen** Exposition, nie eine
Behauptung über deine rechtliche Haftung. Genau gesagt: dies entfernt die
*spezifische* Exit-Knoten-Exposition; es macht keine Rolle risikofrei, und es
macht ScrambNet nicht zu einem Exit-Proxy — es ist strukturell keiner, und diese
Abwesenheit ist ein Merkmal, auch für dich.

### Mehr als eine Rolle betreiben

Die meisten der obigen Aussagen beschreiben eine einzelne Rolle für sich. Eine
Maschine betreibt häufig mehrere — Guard, Relais und Drop zusammen — und die
Zusammenlegung erzeugt Korrelationen, die keine der Einzelrollen-Aussagen zeigt.
Ein Drop, der mehrere Postfächer hält, korreliert das Einzahlungs-Timing über sie
hinweg (`RZ-16` §9); ein Relais, das **auch ein Nutzer** ist und „genau dann
online ist, wenn sein Betreiber chattet, ist ein Schnittmengenangriff auf sich
selbst“ (die Architektur benennt dies direkt). Die Disziplin, die die Architektur
vorschreibt, ist die Minderung: ein stets-aktiver Zeitplan, der von deiner
eigenen Nutzung unabhängig ist, sodass deine Betriebszeit nichts über deine
Aktivität aussagt. Wenn du mehr als eine Rolle betreibst, ist deine Exposition
nicht das Minimum der Rollen — sie ist ihre Kombination.

## Die Haltung zum Umgang mit Missbrauch

Dies ist der Teil, den ein feindlicher Leser am härtesten prüfen wird, darum ruht
jeder einzelne Satz davon auf einer echten Unfähigkeit, und keiner davon führt
einen Hebel ein.

**(a) Die Unfähigkeit, als Sicherheitseigenschaft formuliert.** ScrambNet kann
keine Nachricht, keinen Nutzer und keinen Inhalt lesen, identifizieren, ins
Visier nehmen oder inhaltsselektiv blockieren oder priorisieren. Das ist keine
Richtlinie, die wir annehmen und umkehren könnten; es ist eine Eigenschaft des
Entwurfs. Ein Drop speichert Anteile, die unterhalb von `k`
informationstheoretisch unlesbar sind (`I-2`); ein Relais leitet Rauschen fester
Größe weiter, das es von jedem anderen nicht unterscheiden kann (`I-4`); es gibt
keine Nutzerliste (es gibt keine Anmeldung), keine Verzeichnisautorität und keine
privilegierte Partei irgendwo im Protokoll (`I-3`). Das Projekt hat keinen
Schlüssel, keinen Schalter und keine Position im Netz, von der aus Inhalt
inspiziert oder gefiltert werden *könnte*. Dieselbe Mathematik schützt jeden,
weil sie niemanden auseinanderhalten kann, und diese Unterschiedslosigkeit ist
es, was den Schutz vertrauenswürdig macht: ein Netz, das Partei ergreifen
*könnte*, ist eines, das ein mächtiger Gegner dazu *bringen* könnte, Partei zu
ergreifen. (Eine ehrliche Einschränkung der Reichweite: Inhaltsblindheit ist
nicht Zustellungsneutralität — die Speichermechanik eines Drops ist eine
Zustellungsoberfläche, `RZ-15` — darum bedeutet „kann nicht blockieren“ hier
*kann nicht inhaltsselektiv blockieren*, was die Eigenschaft ist, auf die es für
die Neutralität ankommt.)

**(b) Was das Projekt wirklich tun kann.** Was wir tun können, tun wir offen: den
vollständigen Entwurf veröffentlichen, damit jeder ihn studieren, angreifen oder
neu implementieren kann (`I-1`); **Verwundbarkeits**-Meldungen unter der
Sicherheitsrichtlinie (SECURITY.md) entgegennehmen und auf sie reagieren; Mängel
beheben; und weiterhin klar sagen, was das Netz schützt und was nicht. Das ist
die ganze Liste. Nichts davon beinhaltet, auf den Verkehr von irgendwem zu
schauen, nach ihm zu greifen oder auf ihn zu reagieren, weil der Entwurf uns
keinen Weg dazu gibt — und der Verwundbarkeits-Kanal ist für Mängel im Entwurf
und im Code, nie ein Kanal, um Verkehr oder Nutzer zu melden, denn es gibt
nichts, was wir mit einer solchen Meldung tun könnten, und ihre Existenz darf
nichts anderes nahelegen.

**(c) Was das Projekt zu bauen verweigert, und warum.** Wir werden keine
Moderationsfähigkeit, keine Melde-Hintertür, keinen Inhaltsfilter, keine
Nutzer-Sperrliste, keinen „rechtmäßigen Zugriffs“-Abgriff oder irgendeinen
anderen Mechanismus bauen, der es dem Projekt, einem Betreiber oder sonst jemandem
erlaubt, Inhalt oder Nutzer zu lesen, ins Visier zu nehmen oder zu unterdrücken.
Wir verweigern das nicht aus Gleichgültigkeit gegenüber Schaden, sondern weil ein
solcher Mechanismus aus sich selbst heraus selbstzerstörerisch ist. Jeder Hebel,
der auf Inhalt gerichtet werden kann, den man „Missbrauch“ nennt, ist derselbe
Hebel, andersherum gerichtet, gerichtet auf Inhalt, den man „Widerspruch“ nennt —
es ist eine Fähigkeit, und wer ihren Einsatz erzwingen kann, entscheidet, worauf
sie zielt. Es wäre genau der einzelne Kontrollpunkt, den `I-3` verbietet, und das
Parteiergreifen, das das Bedrohungsmodell aus dem Geltungsbereich ausschließt. In
dem Moment, in dem ein solcher Hebel existiert, ist das Versprechen des Netzes für
jeden falsch, auch für die Menschen, die es zu schützen gebaut wurde; der Gegner
muss nicht mehr die Mathematik brechen, nur noch den Hebel an sich reißen. Die
Abwesenheit eines Moderationsmechanismus ist keine Lücke, die zu füllen uns
misslang — sie ist eine tragende Sicherheitseigenschaft, die wir zu zerstören uns
weigern. (Jede Flooding-Zulassungskontrolle, die das Projekt je annimmt — die
offene `OP-9`-Frage, die `RZ-15` ungelöst lässt — MUSS bauartbedingt inhaltsblind
und identitätsblind sein, und der führende Kandidat prüft am Besitz einer
je-Beziehung-Kontaktkarte, nicht an der Sichtweise; eine Zulassungsregel, die
*einen Absender identifizieren* oder *eine Einzahlung inspizieren* müsste, wäre
ein Hebel und ist unter derselben Haltung verboten.)

**(d) Der ehrliche Preis.** Das ist nicht umsonst, und wir werden nichts anderes
vorgeben. Ein Netz, das nicht Partei ergreifen kann, kann auch nicht *gegen*
Schaden Partei ergreifen. ScrambNet kann für Dinge genutzt werden, die seine
Autoren abstoßend finden, und das Projekt kann das bauartbedingt nicht
verhindern. Die üblichen Analogien — das Postsystem kann nicht jeden Brief lesen,
ein Telefonnetz kann nicht nach „schlechten“ Anrufen horchen, TLS kann sich nicht
weigern, die Verbindung eines Kriminellen zu verschlüsseln — tragen die Form des
Punktes, aber **untertreiben** ihn, und der Unterschied ist die ganze Behauptung:
Post-, Telefon- und TLS-Endpunkte *können* per Durchsuchungsbefehl gezwungen
werden, ein bestimmtes Ziel abzufangen, weil ein Aussichtspunkt und ein Schlüssel
existieren. ScrambNets „kann nicht“ ist **stärker** — es gibt keine Position, von
der aus ein gezwungener Betreiber Inhalt unterhalb von `k` übergeben *könnte*
(`I-2`), und keine einzelne Partei, der befohlen werden *könnte*, eine vergiftete
Sicht auf das Netz zu veröffentlichen (`I-3`; die Spezifikation benennt die
Wirklichkeit von „gezwungen, vorgeladen oder beschlagnahmt“ direkt). Die Schutze
sind unterschiedslos, weil selektiver Schutz kein Schutz ist — er ist eine Liste
derer, denen erlaubt ist, sicher zu sein, geführt von dem, der den Stift hält.
Wir nehmen den Preis mit offenen Augen an: ein Werkzeug, das mächtig genug ist,
die Ohnmächtigen vor den Mächtigen zu schützen, kann nicht mit einem Schalter
kommen, den die Mächtigen umlegen können. Die ehrliche Zusammenfassung lautet
nicht „ScrambNet verhindert Missbrauch“. Sie lautet: **ScrambNet schützt
Kommunikation, und dieser Schutz kommt ohne Not-Aus-Schalter — für niemanden,
gegen niemanden, auch nicht für uns.**

## Wo du ohnehin exponiert bist

Klar gesagt und so stehen gelassen — kein „aber keine Sorge“, keine angedeutete
Sicherheit.

- **Jeden Knoten zu betreiben ist ein sichtbarer Akt.** Ein Relais
  veröffentlicht eine Adresse; eine Bridge zirkuliert eine; ein Mesh-Knoten
  sendet ein Funksignal aus. Die Mathematik schützt den *Inhalt und die
  Verknüpfung von Verkehr*, nicht die *Tatsache, dass deine Maschine im Netz ist*.
  Wenn es selbst dein Risiko ist, dabei gesehen zu werden, wie du
  Anonymitäts-Infrastruktur betreibst, entfernt keine Invariante das.
- **Ein Guard sieht Client-IPs.** Strukturell, kein Fehler. IPs von
  ScrambNet-Nutzern laufen durch deinen Guard und sind für jeden sichtbar, der
  seine Verbindungen beobachten kann.
- **Ein Drop sieht Timing und formt die Zustellung.** Unlesbarer Inhalt, ja —
  aber Einzahlungs- und Polling-Zeiten innerhalb einer Epoche, die Korrelation des
  Einzahlungs-Timings über Postfächer hinweg und die
  Räumungs-/Flooding-Zustellungsoberfläche sind reale, erklärte Reste
  (`RZ-15`/`RZ-16`/`OP-9`).
- **Eine Bridge ist auffindbar.** Bauartbedingt wird sie Fremden
  weitergereicht; einige mögen Gegner sein. Die Widerstandsfähigkeit gegen
  Enumeration ist ein Wettrüsten, keine Garantie.
- **Ein Mesh-Knoten ist physisch ortbar.** Die Bytes sind Rauschen; der Sender
  ist an einem Ort, genau dann, wenn ein Gegner das Internet abgeschaltet hat.
- **Den Inhaltsboden zu erreichen hängt von einer Disjunktheit ab, die du nicht
  verifizieren kannst.** Der `I-2`-Boden unterhalb von `k` ist unbedingt; dass
  deine Pfade oder Drops wirklich unabhängig sind, ist gefolgert, nicht bewiesen
  (`OP-1`/`PS-11`), und eine steuernde Karte kann es oberhalb einer Schwelle
  besiegen (`PS-12`). Betreibe im Wissen darum.
- **Dein lokales Recht kann dich zwingen, gleich was die Bytes sind.** Dieses
  Projekt kann dir nicht sagen, was irgendeine Behörde von dir verlangen mag, und
  es wird nicht vorgeben, die Inhaltsblindheit des Netzes sei ein rechtlicher
  Schutzschild — sie ist eine technische Tatsache über die Bytes, keine
  rechtsordnungsspezifische rechtliche Schlussfolgerung. Dass ein Drop *nicht*
  lesen kann, was er speichert, ist wahr und mag von Belang sein, oder auch nicht,
  je nach einem Recht, das dieses pseudonyme Projekt nicht kennen kann. **Hier
  brauchst du deinen eigenen rechtlichen Rat, nicht unseren.** Wir benennen, was
  technisch preisgegeben wird; was es rechtlich für dich bedeutet,
  herauszufinden, ist deine Sache.
