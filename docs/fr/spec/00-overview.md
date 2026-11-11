# Spécification ScrambNet — Partie 0 : Conventions et structure

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/00-overview.md)).

**Statut : BROUILLON (DRAFT).** Chaque nombre de cette spécification est un homme de paille à attaquer,
non une décision. Attaquez-le par les issues ; changez-le par les PR.

## Comment lire cette spécification

- Les mots-clés **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, **MAY** doivent être
  interprétés comme décrit dans la RFC 2119.
- Les exigences sont numérotées et stables : `SP-n` (paquet de part, Partie 1), `GR-n`
  (enregistrement de gossip, Partie 2). Les issues et les PR référencent les exigences par numéro.
- Les références `OP-n` pointent vers la liste des problèmes ouverts dans
  [threat-model.md](../threat-model.md#open-problems).
- Une implémentation conforme implémente chaque MUST de chaque partie qu'elle revendique.

## Invariants de conception

Ces quatre invariants l'emportent sur tout le reste de la spécification. Une proposition qui en viole
un est rejetée, quel que soit ce qu'elle achète.

- **I-1 (Kerckhoffs).** La spécification est complète : un implémenteur hostile muni de
  ce document et d'aucune autre connaissance DOIT (MUST) pouvoir construire un nœud interopérable et
  également sûr. Si un détail doit rester secret pour que le système fonctionne, le
  détail est un défaut.
- **I-2 (Plancher inconditionnel).** La confidentialité du contenu d'un message face à un
  adversaire tenant moins de `k` parts NE DOIT PAS (MUST NOT) dépendre d'aucune hypothèse
  calculatoire. Les couches au-dessus de la dispersion PEUVENT (MAY) être calculatoires ; le plancher ne l'est pas.
- **I-3 (Aucun point unique).** Aucune étape du protocole ne peut exiger une partie, une clé ou une adresse
  qui ne puisse être remplacée par un substitut non fiable. Cela inclut la découverte,
  les mises à jour et l'amorçage.
- **I-4 (Uniformité).** Tout ce qui est observable sur le fil par une partie dépourvue des
  clés pertinentes DOIT (MUST) être indiscernable d'octets aléatoires uniformes de longueur
  fixe. Pas de versions, drapeaux ou longueurs en clair.

## Suite cryptographique

Les identifiants de suite tiennent sur un octet, négociés nulle part : la suite est fixée par époque
de réseau et portée implicitement par la version du paquet (I-4 interdit la négociation en
clair). Suite `0x01` (homme de paille) :

| Rôle | Primitive |
|---|---|
| Poignée de main de circuit | Schéma Noise `XK`, `Noise_XK_25519_ChaChaPoly_BLAKE2s` |
| Échange de clés | X25519 |
| AEAD | ChaCha20-Poly1305 |
| Hachage / KDF / PRF | BLAKE2s / HKDF-BLAKE2s |
| Signatures (enregistrements de gossip) | Ed25519 |
| Format de paquet | Paramètres Sphinx (Danezis–Goldberg 2009), Partie 1 |
| Dispersion | Partage de secret de Shamir sur GF(2^8), par octet |

Justification : rapide sans accélération matérielle (un anonymat qui ne tourne que sur un
ordinateur portable neuf n'est pas pour ceux qui en ont le plus besoin), rien d'exotique, chaque primitive a
une décennie d'attaques publiques derrière elle. Note post-quantique : par I-2 le plancher de
confidentialité survit déjà à un adversaire quantique ; une poignée de main PQ (suite `0x02`) est une
amélioration planifiée, non une urgence.

## Conventions d'encodage

- Tous les entiers sont non signés, en ordre d'octets réseau (big-endian).
- Tailles fixes partout où un champ traverse le fil (I-4). Les données de longueur variable
  n'existent qu'à l'intérieur de charges utiles protégées par AEAD, préfixées en longueur sur 2 octets.
- Les enregistrements de gossip utilisent le CBOR canonique (RFC 8949 §4.2.1) — Partie 2.

## Parties

1. [Partie 1 — Paquet de part](01-share-packet.md) : l'unité de taille fixe qui transporte
   une part d'un message à travers un circuit.
2. [Partie 2 — Enregistrement de gossip](02-gossip-record.md) : le descripteur de relais auto-signé
   et les règles pour les échanger et les échantillonner.
3. [Partie 3 — Construction des circuits et sélection des chemins](03-path-selection.md) :
   objectifs de disjonction, inférence sans auto-déclaration, gardes, et le
   repli pour petit réseau (OP-1).
4. [Partie 6 — Rendezvous et livraison](06-rendezvous.md) : cartes de contact,
   dead-drops dispersés, et récupération par sondage.

Planifiées, pas encore ébauchées : Partie 4 — transports caméléon ; Partie 5 — encadrement du
mode blackout.
