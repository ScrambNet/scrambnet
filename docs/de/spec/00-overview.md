# ScrambNet-Spezifikation — Teil 0: Konventionen und Struktur
> **Informative Übersetzung.** Maßgeblich und normativ ist die englische Fassung ([en](../../en/spec/00-overview.md)).

**Status: ENTWURF (DRAFT).** Jede Zahl in dieser Spezifikation ist ein anzugreifender Strohmann,
keine Entscheidung. Greife sie über die Issues an; ändere sie über PRs.

## Wie man diese Spezifikation liest

- Die Schlüsselwörter **MUST** (MUSS), **MUST NOT** (DARF NICHT), **SHOULD** (SOLLTE),
  **SHOULD NOT** (SOLLTE NICHT), **MAY** (DARF) sind wie in RFC 2119 beschrieben zu
  interpretieren.
- Anforderungen sind nummeriert und stabil: `SP-n` (Anteil-Paket, Teil 1), `GR-n`
  (Gossip-Eintrag, Teil 2), `PS-n` (Pfadauswahl, Teil 3), `RZ-n` (Rendezvous, Teil 6),
  `SA-n` (Sicherheitsargument, Teil 7), `ID-n` (Inferenz-Datensatz, Teil 8). Issues und PRs verweisen auf Anforderungen per Nummer.
- `OP-n`-Verweise zeigen auf die Liste offener Probleme in
  [threat-model.md](../threat-model.md#offene-probleme).
- Eine konforme Implementierung implementiert jedes MUST jedes Teils, den sie beansprucht.

## Entwurfsinvarianten

Diese vier Invarianten rangieren über allem anderen in der Spec. Ein Vorschlag, der
eine von ihnen verletzt, wird abgelehnt, egal was er einbringt.

- **I-1 (Kerckhoffs).** Die Spezifikation ist vollständig: Ein feindlicher Implementierer mit
  diesem Dokument und keinem weiteren Wissen MUSS (MUST) einen interoperablen, gleich
  sicheren Knoten bauen können. Muss ein Detail geheim bleiben, damit das System funktioniert, dann ist das
  Detail ein Fehler.
- **I-2 (Bedingungslose Untergrenze).** Die Vertraulichkeit des Nachrichteninhalts gegen einen
  Gegner, der weniger als `k` Anteile hält, DARF NICHT (MUST NOT) von irgendeiner rechnerischen
  Annahme abhängen. Schichten oberhalb der Streuung DÜRFEN (MAY) rechnerisch sein; die Untergrenze nicht.
- **I-3 (Kein einzelner Punkt).** Kein Protokollschritt darf eine Partei, einen Schlüssel oder eine Adresse
  erfordern, die nicht durch einen nicht vertrauten Ersatz ersetzt werden kann. Das schließt Entdeckung,
  Updates und Bootstrap ein.
- **I-4 (Uniformität).** Alles, was auf dem Draht von einer Partei ohne die
  relevanten Schlüssel beobachtbar ist, MUSS (MUST) von gleichverteilten Zufallsbytes fester
  Länge nicht zu unterscheiden sein. Keine Klartext-Versionen, -Flags oder -Längen.

## Kryptografische Suite

Suite-Bezeichner sind ein Byte, nirgends verhandelt: die Suite ist je Netz-Epoche
fest und wird implizit durch die Paketversion getragen (I-4 verbietet Klartext-
Verhandlung). Suite `0x01` (Strohmann):

| Rolle | Primitive |
|---|---|
| Circuit-Handshake | Noise-`XK`-Muster, `Noise_XK_25519_ChaChaPoly_BLAKE2s` |
| Schlüsselaustausch | X25519 |
| AEAD | ChaCha20-Poly1305 |
| Hash / KDF / PRF | BLAKE2s / HKDF-BLAKE2s |
| Signaturen (Gossip-Einträge) | Ed25519 |
| Paketformat | Sphinx-Parameter (Danezis–Goldberg 2009), Teil 1 |
| Streuung | Shamirs Secret Sharing über GF(2^8), je Byte |

Begründung: schnell ohne Hardware-Beschleunigung (Anonymität, die nur auf einem neuen
Laptop läuft, ist nichts für die, die sie am dringendsten brauchen), nichts Exotisches, jede Primitive hat
ein Jahrzehnt öffentlicher Angriffe hinter sich. Postquanten-Anmerkung: nach I-2 übersteht die
Vertraulichkeits-Untergrenze bereits einen Quantengegner; ein PQ-Handshake (Suite `0x02`) ist ein
geplantes Upgrade, kein Notfall.

## Kodierungs-Konventionen

- Alle Ganzzahlen sind vorzeichenlos, in Netz-Byte-Reihenfolge (Big-Endian).
- Feste Größen überall, wo ein Feld den Draht kreuzt (I-4). Daten variabler Länge
  existieren nur innerhalb AEAD-geschützter Nutzlasten, längenpräfigiert mit 2 Bytes.
- Gossip-Einträge nutzen kanonisches CBOR (RFC 8949 §4.2.1) — Teil 2.

## Teile

1. [Teil 1 — Anteil-Paket](01-share-packet.md): die Einheit fester Größe, die
   einen Anteil einer Nachricht durch einen Circuit trägt.
2. [Teil 2 — Gossip-Eintrag](02-gossip-record.md): der selbstsignierte Relais-Deskriptor
   und die Regeln zum Austauschen und Abtasten.
3. [Teil 3 — Circuit-Aufbau und Pfadauswahl](03-path-selection.md):
   Disjunktheitsziele, Schlussfolgerung ohne Selbstdeklaration, Wächter und der
   Kleinnetz-Rückfall (OP-1).
4. [Teil 6 — Rendezvous und Zustellung](06-rendezvous.md): Kontaktkarten,
   verstreute Dead-Drops und Abruf per Polling.
5. [Teil 7 — Das Sicherheitsargument für I-2](07-security-argument.md): der Beweis,
   dass beliebige `k−1` Anteile unabhängig vom Geheimnis sind, die zwei Bedingungen,
   auf denen er ruht (Koeffizienten-Zufälligkeit, Schlüsseltrennung), und eine ehrliche
   Angabe dessen, was nicht bewiesen ist.
6. [Teil 8 — Der Inferenz-Datensatz](08-inference-dataset.md): wie ein Client die
   IP-zu-AS- und Grob-Jurisdiktions-Karte erhält, aus der Teil 3 schlussfolgert, ohne
   Autorität — ein reproduzierbares, inhaltsadressiertes Artefakt, ein
   erlaubnisfreier Transparenz-Log, erklärtes Trust-on-First-Use und die
   Fehlerrate, die die Karte einräumt und dem Simulator zuführt (OP-1-Verteilung,
   Roadmap 2.3).

Geplant, noch nicht entworfen: Teil 4 — Chamäleon-Transporte; Teil 5 — Blackout-
Modus-Rahmung.
