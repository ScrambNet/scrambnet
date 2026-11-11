# Spécification ScrambNet — Partie 1 : Paquet de part

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/01-share-packet.md)).

**Statut : BROUILLON (DRAFT).** Les tailles homme de paille sont marquées `(s)`. Attaquez-les par numéro d'exigence.

## 1. Portée

Le paquet de part est la seule unité qui traverse la surcouche : il transporte une part d'un
message à travers un circuit en oignon. Tout dans cette partie sert deux objectifs :
le plancher inconditionnel (I-2) et l'uniformité sur le fil (I-4).

## 2. Mise en couches

```
message en clair
  └─ AEAD de bout en bout (clé de paire pré-partagée, SP-1a)  [calculatoire]
       └─ découpe de Shamir : n parts, seuil k           [plancher inconditionnel]
            └─ chiffrement en oignon par part, circuit propre, format Sphinx
                 └─ transport caméléon (Partie 4)
```

- **SP-1.** L'expéditeur DOIT (MUST) appliquer le chiffrement de bout en bout *avant* la dispersion, et
  la dispersion DOIT (MUST) être appliquée au texte chiffré de bout en bout. Avec moins de `k`
  parts, l'adversaire n'apprend rien sur le texte chiffré, inconditionnellement
  (Shamir) ; avec `k` parts ou plus, il affronte encore l'AEAD de bout en bout. Le
  plancher inconditionnel et la ceinture calculatoire se composent ; aucun ne remplace
  l'autre. La ceinture est démontrée de bout en bout dans `poc/e2e.py` (chiffrer →
  découper → reconstruire → déchiffrer, fermeture sûre en cas d'altération).
- **SP-1a (établissement de la clé de contenu, et la conséquence post-quantique).** La clé
  AEAD de bout en bout DOIT (MUST) être dérivée du **secret symétrique de paire pré-partagé**
  `kpair` porté par la carte de contact (Partie 6, RZ-2), au moyen d'une KDF séparée par
  étiquette : `content_key = HKDF-BLAKE2s(kpair, "e2e-content")`, distincte de la clé
  d'étiquette SP-7 et de la clé d'identifiant de boîte dérivées du même `kpair`. Il NE DOIT
  PAS (MUST NOT) y avoir d'accord de clé asymétrique dans le chemin du contenu. C'est un choix
  délibéré à la conséquence porteuse : un adversaire `≥k` qui enregistre tout et dispose d'un
  futur ordinateur quantique à grande échelle ne peut toujours pas lire le contenu, car il
  n'existe aucune transcription Diffie-Hellman que Shor puisse casser — seulement un secret
  symétrique que les parties partagent déjà, et Grover coûte à l'AEAD au plus une division par
  deux de la force de sa clé (d'où une clé dérivée de ≥256 bits RECOMMANDÉE là où la marge
  importe). « Harvest now, decrypt later » (récolter maintenant, déchiffrer plus tard) est donc
  défait aux **deux** niveaux : en dessous de `k` par Shamir (inconditionnel), à `k` ou au-delà
  par un AEAD symétrique sous une clé pré-partagée (aucune hypothèse de clé publique à
  récolter). Le prix honnête est le **bootstrap** : `kpair` doit d'abord parvenir au destinataire
  par un canal confidentiel préalable (l'échange hors bande de carte de contact, Partie 6).
  Toute hypothèse résiduelle de clé publique ou de PQ-KEM réside là, dans l'échange de carte —
  pas dans le chemin du contenu — et acheminer un échange de carte lui-même post-quantique est
  un choix orthogonal et en couches, non une condition préalable au plancher. La suite AEAD est
  ChaCha20-Poly1305 (suite `0x01`) ; `msg_nonce` (SP-7) est le nonce de l'AEAD, ce qui lie les
  deux couches et rend un nonce réutilisé doublement fatal (collision d'étiquette SP-7 *et*
  perte de confidentialité de l'AEAD — voir SP-7).
- **SP-2.** Paramètres de dispersion par défaut pour la messagerie : `n = 4`, `k = 3` (s).
  Les profils de transfert de volume PEUVENT (MAY) utiliser la dispersion d'information de Rabin au lieu de Shamir, et DOIVENT (MUST) être
  étiquetés comme calculatoires dans l'IU du client, car l'IDA n'a aucun plancher
  inconditionnel (OP-3).

## 3. Format sur le fil

- **SP-3.** Chaque paquet sur chaque lien DOIT (MUST) faire exactement `P = 2048` octets (s).
- **SP-4.** Chaque octet du paquet DOIT (MUST) être indiscernable d'un aléa uniforme
  pour un observateur dépourvu des clés pertinentes, à chaque saut (propriété de
  Sphinx ; I-4). En particulier, il n'y a pas de version, de suite, de longueur, de
  compteur de sauts ni d'index de part en clair.

Disposition (tailles homme de paille, maximum 3 sauts) :

| Champ | Taille (s) | Visible par |
|---|---|---|
| `alpha` — élément de groupe Sphinx (X25519) | 32 o | tout le monde (uniforme) |
| `beta` — info de routage Sphinx, 3 × 48 o, complétée | 144 o | pelée par saut |
| `gamma` — MAC par saut | 16 o | saut courant |
| `delta` — charge utile, enveloppée par AEAD à chaque saut | 1856 o | segment sortie → destinataire |

- **SP-5.** Les relais DOIVENT (MUST) maintenir un cache de rejeu des valeurs `gamma` vues par époque
  de clé et DOIVENT (MUST) écarter les rejeux silencieusement (défense de rejeu Sphinx standard).
- **SP-6.** Les relais DOIVENT (MUST) émettre les paquets en lots de taille constante avec une gigue
  définie par l'implémentation en mode rapide, et DOIVENT (MUST) suivre la stratégie de mixage
  (stop-and-go ou mixage de Poisson, à déterminer) en mode paranoïaque. Le choix de la stratégie est
  du ressort d'OP-5 et délibérément non résolu ici.

## 4. Charge utile de la part (à l'intérieur de `delta`, fin du circuit)

Déchiffrée par le destinataire seul :

| Champ | Taille (s) | Notes |
|---|---|---|
| `tag` | 16 o | étiquette PRF à clé du destinataire, voir SP-7 |
| `index` | 1 o | index de part `1..n` |
| `params` | 1 o | `k`, `n` empaquetés (4 bits chacun) |
| `share` | 1792 o | octets de la part de Shamir |
| `pad` | reste | aléatoire |

- **SP-7 (aucune liaison inter-chemins).** Deux parts du même message NE DOIVENT PAS (MUST NOT)
  porter une valeur égale ou corrélable observable par quiconque sauf le
  destinataire. L'appartenance à un ensemble de parts n'est signalée que par `tag` :
  `tag = PRF(K_r, msg_nonce ‖ index)` où `K_r` est une clé détenue par le destinataire et
  `msg_nonce` est porté à l'intérieur de la couche de bout en bout. Un relais de sortie, ou une
  coalition de sorties, NE DOIT PAS (MUST NOT) pouvoir dire si deux paquets appartiennent au
  même message. Cette exigence est porteuse : sans elle, la dispersion
  se dégrade en une commodité d'énumération pour l'adversaire.
- **SP-8.** Un message qui ne remplit pas la charge utile de la part (`1792` octets, moins
  le préfixe de longueur de 2 octets) DOIT (MUST) être complété d'octets aléatoires avant la découpe ;
  un message qui la dépasse est fragmenté à une couche au-dessus de celle-ci
  (conception de la fragmentation à déterminer, interagit avec OP-4). Le prix honnête de Shamir : chaque
  part est aussi longue que le secret, de sorte qu'une dispersion (n, k) transmet ×`n` le
  volume de texte chiffré (OP-3).
- **SP-9 (temps).** L'expéditeur NE DOIT PAS (MUST NOT) émettre les `n` parts en une rafale
  simultanée. Les parts DEVRAIENT (SHOULD) être émises avec un délai aléatoire par part ; la
  distribution et son coût en latence relèvent d'OP-4 et sont non résolus. Les clients PEUVENT (MAY)
  émettre des parts leurres (paquets à `tag` aléatoire) à un débit configurable.

## 5. Ce que cette partie ne décide pas

La sélection des chemins et l'imposition de la disjonction (OP-1), les paramètres de mixage (OP-5),
la fragmentation (SP-8), l'économie des leurres (SP-9) sont ouverts à dessein. Chacun a une
issue numérotée ; argumentez là, avec des chiffres.
