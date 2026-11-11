# Spécification ScrambNet — Partie 6 : Rendezvous et livraison

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/06-rendezvous.md)).

**Statut : BROUILLON (DRAFT).** Valeurs homme de paille marquées `(s)`. Les questions de métadonnées de récupération et
d'économie que cette partie ouvre sont OP-9 et délibérément non résolues.

## 1. Portée

Comment un message atteint quelqu'un qui n'est pas — et ne doit pas être — dans la carte de qui que ce soit.
Les destinataires n'ont pas d'emplacements réseau ; ils ont des **cartes de contact** et des
**dead-drops**. L'expéditeur dépose des parts ; le destinataire les récupère depuis
derrière ses propres circuits. Nul ne livre jamais *à* une personne.

## 2. Personne ne gossipe à propos des gens

- **RZ-1.** Un destinataire NE DOIT PAS (MUST NOT) être découvrable par le gossip. Seuls les relais
  publient des enregistrements (Partie 2). Tout ce qui rend la participation d'une personne
  interrogeable est un défaut (comparez L0 : il n'y a pas de liste d'utilisateurs parce qu'il
  n'y a aucun moment où un utilisateur s'inscrit).

## 3. Cartes de contact

- **RZ-2.** Une carte de contact est **par relation** : la carte donnée au
  correspondant A DOIT (MUST) être non reliable à la carte donnée au correspondant B —
  clé de paire distincte, boîtes distinctes. La compromission d'un correspondant expose
  une relation, non le monde du destinataire.
- **RZ-3.** Contenu de la carte (CBOR canonique, comme en Partie 2) :

| Clé | Nom | Type | Notes |
|---|---|---|---|
| 0 | `v` | uint | version de format, `1` |
| 1 | `id` | bytes(32) | clé d'identité Ed25519 du destinataire |
| 2 | `kpair` | bytes(32) | secret de paire ; tout ce qui suit en dérive |
| 3 | `drops` | array | `d` enregistrements de relais intégrés (enregistrements complets de la Partie 2) |
| 4 | `validity` | uint | expiration unix ; DEVRAIT (SHOULD) suivre l'expiration des enregistrements intégrés |

  Dérivations (HKDF-BLAKE2s, suite 0x01) : la clé d'étiquette SP-7 pour cette paire est
  `K_tag = HKDF(kpair, "tag")` ; les identifiants de boîte sont
  `box_id(drop, epoch) = PRF(kpair, "box" ‖ drop_index ‖ epoch)` tronqués à
  16 octets, avec `epoch = floor(unix_time / 86400)` (s). L'index du drop DOIT (MUST)
  entrer dans la dérivation : avec un seul id par époque, deux drops conspirant pourraient
  relier les boîtes de la paire au sein de cette époque.
- **RZ-4.** Les cartes voyagent hors bande (QR code, chaîne imprimée, un ami) ou
  sur un canal ScrambNet existant. Un seul contact est le plancher, comme en GR-10.

## 4. Drops et dépôt

- **RZ-5.** L'ensemble de drops contient `d = n = 4` (s) relais, choisis par le
  *destinataire*, qui DEVRAIENT (SHOULD) être mutuellement indépendants au sens où la sélection de chemins
  l'exige (OP-1 s'applique aussi aux drops). Les `n` parts d'un message
  DOIVENT (MUST) être déposées à `n` drops distincts — SP-7 étendu au stockage : aucun
  drop ne détient jamais deux parts de quoi que ce soit.
- **RZ-6.** Un dépôt est un paquet ordinaire de la Partie 1 dont le circuit se termine au
  drop. Le texte clair du dernier saut de `delta` est `box_id` (16 o) ‖ `slot`
  (1840 o) ; le slot est la charge utile de part de la Partie 1 §4 avec son pad de queue
  plus court de 16 octets. Le drop stocke le slot sous `box_id` tel quel : il ne peut
  lire ni la sémantique de l'étiquette ni le contenu de la part (une part < `k`, et SP-7
  rend les parts mutuellement non reliables même entre drops conspirant).
- **RZ-7.** Les dépôts sont du type « tire et oublie ». Le drop NE DOIT PAS (MUST NOT) émettre de réponse
  qui distingue succès, boîte inconnue ou boîte pleine (uniformité silencieuse, comme en
  GR-4). Règles de stockage : slots fixes de 1840 o, au plus `64` (s) slots par boîte,
  expiration de slot `7` jours (s), éviction du plus ancien d'abord.

## 5. Récupération

- **RZ-8.** Le destinataire sonde chacun de ses drops sur ses propres circuits.
  La connaissance de `box_id` autorise la récupération (il est dérivé du secret et
  indevinable) ; les slots sont supprimés à l'expiration, non à la récupération (la sémantique
  de suppression-à-la-récupération relève d'OP-9 : un adversaire qui vole un `box_id` ne doit pas
  pouvoir manger du courrier silencieusement).
- **RZ-9 (discipline de sondage).** Le sondage DOIT (MUST) suivre un horaire indépendant de
  l'activité de l'utilisateur : cadence fixe avec gigue (homme de paille : toutes les `15` minutes ±
  uniforme `5`), se poursuivant quand l'utilisateur est inactif, avec des sondages leurres vers des
  box ids leurres à la même cadence. Une réponse de récupération fait toujours exactement `b = 8`
  (s) slots, complétée de slots factices indiscernables des vrais. Le
  drop apprend la cadence de sondage d'une boîte et les temps de dépôt au sein d'une époque —
  c'est le résidu assumé par conception, borné par RZ-10 et attaqué dans OP-9.
- **RZ-10 (époques).** `box_id` tourne par époque. Un drop NE DOIT PAS (MUST NOT) pouvoir
  relier les boîtes d'une même paire à travers les époques ; rien dans le protocole de récupération
  ne peut porter une valeur stable à travers les époques.

## 6. Renouvellement et défaillance

- **RZ-11.** Une carte est renouvelée en bande : le destinataire dépose la carte suivante
  (nouvelle `kpair`, nouveaux drops) dans les boîtes existantes de la paire comme un message
  ordinaire, avant que `validity` ne s'écoule. Si chaque drop d'une paire est mort ou que la
  carte a expiré, la paire ré-échange hors bande : un seul contact est le
  plancher, de nouveau.
- **RZ-12.** Quiconque détient une carte peut remplir ses boîtes. Le plafond par boîte (RZ-7)
  borne les dégâts d'inondation à une relation ; la tarification des dépôts (énigmes
  client ?) et l'économie de stockage des drops sont ouvertes (OP-9).

## 7. Dérivation des clés et frontières d'époque

- **RZ-13 (une seule discipline de KDF).** Toute clé et tout identifiant qu'une paire dérive
  de `kpair` DOIT (MUST) provenir d'une discipline unique : HKDF-BLAKE2s avec une étiquette
  distincte liant l'usage. Concrètement : la clé de contenu est `HKDF(kpair, "e2e-content")`
  (SP-1a), la clé d'étiquette SP-7 est `HKDF(kpair, "tag")`, et l'identifiant de boîte est
  `box_id = HKDF(kpair, "box" ‖ drop_index ‖ epoch)` tronqué à `BOX_ID_BYTES`. Aucune valeur
  n'est dérivée par un BLAKE2s à clé brut sur `kpair` ni par une quelconque seconde
  construction — un brouillon antérieur dérivait `box_id` de cette manière, ce que cette
  exigence abolit. La séparation par étiquette signifie que la capture ou la faiblesse d'une clé
  dérivée n'apprend rien à un adversaire sur ses sœurs, et toute la relation est gouvernée par
  une seule dérivation auditable (l'argument de séparation des clés `SA-4`, Partie 7, dépend
  exactement de cela).
- **RZ-13a (largeur de box_id).** `BOX_ID_BYTES = 16` (128 bits) (s). Un drop ne voit que ce
  descripteur opaque, jamais `kpair` ; 128 bits sont sûrs vis-à-vis des collisions pour le
  nombre de boîtes `(pair, drop, epoch)` que tout réseau réaliste détient et maintiennent la
  charge utile `box_id ‖ slot` dans un seul `delta`.
- **RZ-14 (grâce de frontière d'époque UTC).** Comme `box_id` tourne par époque UTC (RZ-10), un
  expéditeur déposant à 23:59 (époque `E`) et un destinataire sondant à 00:01 (époque `E+1`)
  adresseraient des boîtes différentes et le destinataire manquerait silencieusement le courrier.
  Pour l'éviter, un destinataire sondant dans une fenêtre de grâce autour d'une frontière d'époque
  DOIT (MUST) sonder les boîtes des **deux** époques adjacentes : l'époque courante toujours,
  l'époque précédente si l'on est dans la fenêtre de grâce après une frontière, et l'époque
  suivante si l'on est dans la fenêtre de grâce avant une frontière. La fenêtre de grâce DOIT
  (MUST) excéder le pire décalage d'horloge expéditeur/destinataire plus la latence
  dépôt-à-sondage (homme de paille `EPOCH_GRACE_SECONDS = 3600` (s)), et `SLOT_TTL_EPOCHS` (RZ-7)
  DOIT (MUST) maintenir une boîte lisible au moins une époque au-delà de la sienne, afin que la
  boîte supplémentaire détienne encore le courrier. Les expéditeurs déposent sous l'unique
  `epoch_of(now)` ; la grâce est une règle de lecture côté destinataire. Démontré dans
  `poc/rendezvous.py` (`epochs_to_poll`, test `test_deposit_before_boundary_polled_after_boundary`).

## 8. Ce que cette partie ne décide pas

La minimisation des métadonnées de récupération (récupération plus maligne que le sondage, astuces
de style PIR et leurs coûts réels), la sémantique de suppression, la tarification des dépôts, les incitations
des drops (OP-9) ; la vérification de l'indépendance de l'ensemble de drops (OP-1) ; le sondage sur
le maillage pendant un blackout (OP-6). Des issues numérotées existent pour chacun.
