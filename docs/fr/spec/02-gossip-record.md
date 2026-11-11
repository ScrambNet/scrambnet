# Spécification ScrambNet — Partie 2 : Enregistrement de gossip

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/02-gossip-record.md)).

**Statut : BROUILLON (DRAFT).** Valeurs homme de paille marquées `(s)`. Les questions de sybil/éclipse sur lesquelles cette
partie s'appuie sont OP-2 et délibérément ouvertes.

## 1. Portée

L'enregistrement de gossip est le descripteur auto-signé par lequel un relais existe. Il n'y a
pas d'annuaire, pas d'autorité, pas d'inscription (I-3) : un relais est l'ensemble des enregistrements
qu'il signe, et la carte du réseau est l'échantillon vérifiable que chaque client détient.

## 2. Format de l'enregistrement

- **GR-1.** Un enregistrement est une carte CBOR canonique (RFC 8949 §4.2.1), d'au plus
  `1024` octets (s) une fois encodée. Les enregistrements plus grands DOIVENT (MUST) être écartés sans être lus.
- **GR-2.** Champs (clés entières ; les clés inconnues DOIVENT (MUST) être ignorées pour la
  compatibilité ascendante, mais sont couvertes par la signature) :

| Clé | Nom | Type | Notes |
|---|---|---|---|
| 0 | `v` | uint | version de format, `1` |
| 1 | `id` | bytes(32) | clé publique d'identité Ed25519 — le nom du relais |
| 2 | `onion` | bytes(32) | clé X25519 pour les poignées de main de circuit ; DOIT (MUST) tourner ≤ 7 jours (s) |
| 3 | `addrs` | array | points d'accès : paires `[transport-id uint, blob bytes]` |
| 4 | `bw` | uint | bande passante soutenue annoncée, ko/s — une *annonce*, voir GR-7 |
| 5 | `created` | uint | temps unix, DOIT (MUST) être arrondi à l'heure inférieure (GR-5) |
| 6 | `expiry` | uint | temps unix, DOIT (MUST) être ≤ `created` + 7 jours (s) |
| 7 | `sig` | bytes(64) | Ed25519 sur l'encodage canonique avec la clé 7 absente |

- **GR-3.** Un relais NE DOIT PAS (MUST NOT) publier d'affirmations géographiques ou juridictionnelles sur
  lui-même. Les clients infèrent l'AS et la juridiction depuis `addrs` avec leurs propres données
  (OP-1) ; une localisation auto-déclarée est une surface d'attaque, non une information.
- **GR-4.** La validité de la signature, le plafond de taille, l'expiration et l'arrondi de l'horodatage DOIVENT (MUST) tous
  être vérifiés avant qu'un enregistrement ne soit stocké ou retransmis ; les échecs sont écartés
  silencieusement — aucune erreur distinguant « malformé » d'« expiré » ne peut être
  observable par l'expéditeur de l'enregistrement.
- **GR-5.** L'arrondi de `created` existe pour empêcher le profilage des relais par dérive d'horloge.
  Les clients DOIVENT (MUST) traiter deux enregistrements de même `id` comme un seul relais et
  ne garder que le `created` le plus frais.

## 3. Échange et échantillonnage

- **GR-6.** Les enregistrements voyagent sur des circuits établis et sur le maillage local
  (Partie 5), portés en appoint dans des lots de taille fixe : un lot de gossip fait `8` enregistrements (s)
  complétés à taille constante, échangés au plus une fois par pair et par `10` minutes (s).
  Un nœud répond à une demande d'échantillon par un échantillon uniforme de ses enregistrements stockés ;
  il NE DOIT PAS (MUST NOT) répondre par un échantillon biaisé par l'identité du demandeur (le
  levier d'éclipse évident).
- **GR-7.** `bw` est une annonce. Les clients DEVRAIENT (SHOULD) vérifier les annonces par sondage aléatoire
  sur des circuits qui ne révèlent pas le sondeur, et DEVRAIENT (SHOULD) pondérer la sélection des chemins
  par la bande passante vérifiée, non annoncée. La conception du sondage est ouverte (OP-2).
- **GR-8 (mélange des sources).** L'échantillon stocké d'un client DOIT (MUST) mélanger des enregistrements de
  classes de sources indépendantes — au minimum : pont par graphe social (à la Lox),
  échange de gossip et sondage direct — et NE DOIT PAS (MUST NOT) permettre à une seule classe de
  dépasser une fraction configurable (homme de paille 1/2) de l'échantillon. C'est la
  défense contre l'éclipse jusqu'à ce qu'OP-2 produise quelque chose de plus fort.
- **GR-9.** Les nouvelles identités sont bon marché par conception (pas d'inscription), aussi rien dans
  cette partie ne peut-il supposer une résistance aux sybils à partir du coût d'identité. Tout mécanisme qui
  a besoin de résistance aux sybils doit l'obtenir de ressources vérifiées (bande passante,
  disponibilité à long terme observée par le client lui-même) ou du graphe social — jamais
  de l'enregistrement seul.

## 4. Amorçage

- **GR-10.** Un client frais DOIT (MUST) pouvoir démarrer depuis une seule ligne de pont hors
  bande (un QR code, une chaîne imprimée, un message d'un ami) contenant
  un enregistrement plus un indice de transport. L'amorçage sans aucun contact est OP-7 et ouvert.

## 5. Ce que cette partie ne décide pas

La résistance aux sybils/éclipses au-delà de GR-8/GR-9 (OP-2), le protocole de sondage (GR-7),
l'amorçage sans aucun contact (OP-7). Des issues numérotées existent pour chacun.
