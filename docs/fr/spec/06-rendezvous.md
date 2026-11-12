# Spécification ScrambNet — Partie 6 : Rendezvous et livraison

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/06-rendezvous.md)).

**Statut : BROUILLON (DRAFT).** Valeurs homme de paille marquées `(s)`. Les questions de
métadonnées de récupération et d'économie que cette partie ouvre sont OP-9 et délibérément non résolues.

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
  expiration de slot `7` jours (s), éviction du plus ancien d'abord. Le plafond borne le
  **stockage**, non la **livraison** sous flooding — voir RZ-15.

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
  c'est le résidu assumé par conception, borné par RZ-10 et désormais chiffré dans RZ-16 :
  l'indépendance de l'horaire DOIT (MUST) être stricte (RZ-16a) et le coût en leurres/octets est
  quantifié (RZ-16b).
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
  borne les dégâts d'inondation **au stockage d'une relation**, mais non la **livraison** de cette
  relation — RZ-15 montre qu'un inondateur de classe téléphone refuse la récupération dans une
  seule période de sondage, et que cette tarification des dépôts (énigmes client) ne peut combler
  l'écart ; la défense suffisante (contrôle d'admission des dépôts) est un résidu OP-9 non résolu.
  Les incitations de stockage des drops restent ouvertes (OP-9).

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

## 8. Économie et métadonnées de récupération, chiffrées (OP-9)

L'item 4.3 de la feuille de route a mis des chiffres sur les deux questions OP-9 que RZ-7/RZ-9
laissaient ouvertes — le flooding et les métadonnées de sondage — avec le simulateur
`poc/dropecon_sim.py` (`test_dropecon_sim.py` verrouille les chiffres). Le résultat honnête est que
l'une des deux défenses que le projet espérait ne tient **pas** ; le §9 la porte comme un
résidu déclaré plutôt que de la cacher.

- **RZ-15 (flooding : ni le plafond ni une énigme ne défendent la *livraison* ; c'est un résidu
  déclaré). [normatif]** Le plafond par boîte de RZ-7 borne le **stockage** à
  `BOX_CAP × SLOT_BYTES = 115 KiB` par boîte `(pair, drop, epoch)`, un plafond indépendant du budget
  de l'attaquant. Il ne borne **pas** la **livraison**. Parce qu'un sondage ne renvoie que les
  `B_SLOTS = 8` plus anciens slots survivants (RZ-8) et que les dépôts évincent le plus ancien d'abord
  (RZ-7), un attaquant qui enfouit un slot honnête frais derrière `≥ 8` slots indésirables plus récents
  en refuse la récupération **sans même atteindre le plafond** — et le simulateur montre qu'un
  inondateur de **classe téléphone** (`2 × 10⁶ H/s`) y parvient en `~17 s`, bien à l'intérieur d'un
  sondage de `POLL_PERIOD = 900 s`, à toute dureté d'énigme utilisable. Une énigme de proof-of-work
  côté dépôt ne sauve pas cela : aucune dureté `z` n'est à la fois dissuasive pour un botnet et
  abordable pour un téléphone — l'écart ARM-contre-GPU est de `~25 000×`, de sorte qu'à `z = 20` (le
  dernier point abordable pour un téléphone, `0,52 s/dépôt`) un seul GPU remplit encore une boîte
  `~1,7 × 10⁸` fois/heure, tandis que forcer un GPU à `1 s/dépôt` coûte au téléphone `~9,5 heures/dépôt`.
  Une énigme PEUT (MAY) être exigée à faible dureté (`z ≤ 20` (s)) comme ralentisseur contre le
  remplissage trivial, mais on ne s'y **fie pas**. La dispersion `n = 4, k = 3` ne fait qu'élever la
  barre à l'inondation de `≥ n − k + 1 = 2` des drops d'une paire à la fois. **Le flooding de livraison
  n'a donc aucune défense suffisante dans cette partie :** il nécessite un contrôle d'**admission** des
  dépôts que le projet n'a pas encore conçu (une direction candidate, non une décision : un jeton
  d'admission par relation dérivé de la carte, de sorte que seul un détenteur de carte dépose et
  seulement à un débit borné). Tant que cela n'existe pas, le flooding de livraison est un résidu OP-9
  déclaré, quantifié au §9.

- **RZ-16 (métadonnées de sondage : deux fuites, deux leviers). [normatif]** L'observation au sein d'une
  époque d'un drop profileur (bornée à travers les époques par RZ-10) se décompose en deux fuites à
  deux défenses indépendantes, et le simulateur chiffre les deux.
  - **RZ-16a (fuite du schéma d'activité — défendue gratuitement par une indépendance stricte).
    [normatif]** Le fait que le destinataire ait *réagi* à un dépôt est la seule fuite identifiant
    l'utilisateur, et elle est défendue en rendant l'horaire de sondage **strictement indépendant**
    des dépôts et de l'activité de l'utilisateur (RZ-9) : l'horaire NE DOIT PAS (MUST NOT) être avancé,
    déclenché ou remodelé par un dépôt ou un événement d'application, de sorte que la latence
    `dépôt → sondage suivant` reste à la moyenne de paradoxe de l'inspection propre à l'horaire
    (`≈ 467 s` pour `POLL_PERIOD = 900, POLL_JITTER = 300`) et soit décorrélée du temps de dépôt. Un
    drop détecte une violation non par la moyenne (trop grossière — un horaire à moitié réactif se lit
    encore comme quasi-indépendant sur la moyenne) mais par la **queue** `P[latency < 60 s]`, que le
    simulateur montre s'élevant du bruit à l'indépendance vers un signal clair dès une fraction
    réactive de `5 %`. Cette défense est **obligatoire et gratuite en octets**.
  - **RZ-16b (fuite de quelle boîte — défendue par des leurres à un coût réel en octets). [normatif]**
    Laquelle de plusieurs boîtes détenues est la vraie boîte du destinataire est défendue par des
    sondages leurres à un multiplicateur `r` (s : `r = 1`), une question à laquelle la non-liabilité
    RZ-2/RZ-10 répond déjà largement, de sorte que la confidentialité marginale par octet est faible.
    Chaque sondage circule en Sphinx — `B_SLOTS + 1 = 9` paquets de `2048 o` sur le saut d'entrée
    mesuré, `~18,4 KiB`, non les octets bruts de slot — de sorte qu'à travers `d = 4` drops à la
    cadence de RZ-9 le coût permanent est de `~212 MB/mois` à `r = 0` (avant le côté dépôt/envoi) et de
    `~425 MB/mois` à la valeur par défaut `r = 1`. `r = 0` est un mode faible-données explicite.
    Démontré dans `poc/dropecon_sim.py` (Scénario B).

## 9. Ce que cette partie ne décide pas (le résidu OP-9 déclaré)

La minimisation des métadonnées de récupération (récupération plus maligne que le sondage, astuces
de style PIR et leurs coûts réels), la sémantique de suppression, et les incitations des drops
(pourquoi un relais stocke le bruit d'un inconnu) restent véritablement ouvertes (OP-9) ; la
vérification de l'indépendance de l'ensemble de drops (OP-1) ; le sondage sur le maillage pendant un
blackout (OP-6). Des issues numérotées existent pour chacun. Trois résultats du §8 sont portés
ouvertement comme des résidus déclarés, avec les chiffres qui les prouvent :

- **Le flooding de livraison n'a ici aucune défense suffisante.** Ni le plafond de RZ-7
  (stockage seul) ni une énigme de proof-of-work (aucune dureté abordable pour un téléphone et
  dissuasive pour un botnet n'existe — l'écart ARM-contre-GPU de `~25 000×`) n'empêche un attaquant
  d'enfouir du courrier honnête au-delà de la fenêtre de récupération à 8 slots en `~17 s`, bien à
  l'intérieur d'un sondage de 900 s, avec du matériel de classe téléphone (RZ-15). Il nécessite un
  contrôle d'admission que le projet n'a pas encore construit ; jusque-là c'est un résidu déclaré.
- **Le plancher de profilage au sein d'une époque est réel.** L'indépendance stricte (RZ-16a)
  retire la seule fuite identifiant l'utilisateur, mais un drop apprend encore la cadence publique de
  RZ-9 et les temps de dépôt dans les boîtes qu'il détient ; les leurres n'atteignent que la question
  de quelle boîte (RZ-16b). Un drop multi-boîtes conspirant peut aussi corréler les horodatages de
  *dépôt* à travers ses boîtes même sous une indépendance de sondage parfaite — la non-liabilité
  RZ-2/RZ-10 couvre les identifiants, non le *timing* des dépôts.
- **La ligne de base de sondage de RZ-9 est lourde pour la cible mobile.** Même avec les leurres
  désactivés (`r = 0`), le sondage obligatoire à cadence fixe à travers `d = 4` drops coûte
  `~212 MB/mois` (RZ-16b) — le prix de la défense du schéma d'activité, payé en octets, avant qu'aucun
  message ne soit envoyé.
