# Spécification ScrambNet — Partie 3 : Construction des circuits et sélection des chemins

**Statut : BROUILLON (DRAFT), et la partie la moins stabilisée de la
spécification.** C'est le mur porteur de la sécurité *opérationnelle* (le
contenu garanti par I-2 tient sans elle, mais la protection contre la
corrélation et toute l'histoire des k-chemins vivent ici). Les valeurs
provisoires sont marquées `(s)`. Le problème de la vérification de la disjonction
est OP-1 et ouvertement non résolu ; cette partie énonce l'objectif et un
premier mécanisme à attaquer.

## 1. Portée et pourquoi c'est difficile

La dispersion (Partie 1) rend le contenu inconditionnellement sûr en dessous de
`k` parts capturées. Cette garantie n'est *opérationnellement* réelle que si les
`n` circuits des parts sont réellement disjoints — sinon un seul point
d'observation de l'adversaire voit `k` parts, et le seuil garanti, bien que
mathématiquement intact, n'est jamais atteint. Cette partie décide comment un
client, qui ne détient que son propre échantillon de gossip vérifiable
(Partie 2) et aucune carte de confiance, sélectionne `n` circuits sur lesquels
un adversaire ne peut pas se poster à bas coût. Tout ce qui suit doit tenir face
à des relais qui mentent sur tout sauf sur ce que leurs signatures engagent
(GR-2).

## 2. Objectifs de disjonction

- **PS-1.** Les `n` circuits d'un message DOIVENT (MUST) être *disjoints par
  nœud* : aucun relais n'apparaît sur deux d'entre eux. C'est le seuil
  plancher, toujours imposable si l'échantillon est assez grand.
- **PS-2.** Le client DEVRAIT (SHOULD) en outre rechercher, par ordre
  décroissant de valeur et croissant de difficulté : **disjoints par AS** (aucun
  couple de circuits ne partage un système autonome à la garde ou à la sortie),
  puis **disjoints par juridiction** (aucun couple ne partage une juridiction
  légale). Chaque niveau qu'il ne peut atteindre DOIT (MUST) être signalé à
  l'utilisateur, non sauté en silence (PS-9).
- **PS-3.** Au sein d'un même circuit, la garde, le nœud du milieu et la sortie
  DOIVENT (MUST) être distincts par nœud, et DEVRAIENT (SHOULD) être distincts
  par AS. Un circuit dont la garde et la sortie partagent un AS est un cadeau à
  la corrélation de bout en bout et NE DOIT PAS (MUST NOT) être utilisé dès lors
  qu'une alternative existe.

## 3. Inférence sans auto-déclaration

- **PS-4.** GR-3 interdit aux relais de déclarer leur emplacement, aussi le
  client infère-t-il l'AS et la juridiction de chaque relais à partir de ses
  `addrs` en utilisant son *propre* jeu de données (par exemple une carte
  IP-vers-AS rafraîchie périodiquement), jamais à partir de ce que le relais
  affirme. La distribution du jeu de données DOIT (MUST) elle-même obéir à I-3 :
  aucune source faisant autorité unique (les conceptions candidates sont OP-1).
- **PS-5.** L'inférence est incertaine, et le client DOIT (MUST) la traiter
  comme telle : lorsque l'AS ou la juridiction d'un relais est inconnu, il
  compte comme *potentiellement partagé* avec tout autre inconnu — l'hypothèse
  conservatrice, jamais l'optimiste.

## 4. Gardes

- **PS-6.** Chaque client maintient un petit ensemble de **relais de garde**
  (valeur provisoire : une garde primaire par position de circuit, renouvelée
  sur une cadence de mois, non de minutes), suivant la logique des gardes de
  Tor : renouveler vite les points d'entrée multiplie la probabilité de finir
  par en tirer un hostile. Les gardes DOIVENT (MUST) être choisies disjointes
  par AS les unes des autres, afin que les `n` circuits ne soient pas canalisés
  à travers un unique AS à l'entrée.
- **PS-7.** La sélection des gardes est pondérée par la bande passante
  *vérifiée* (GR-7), jamais déclarée ; un relais dont l'affirmation n'est pas
  vérifiable est traité comme à faible bande passante, non à haute.

## 5. Petits réseaux : dégrader, et le dire

- **PS-8.** Lorsque l'échantillon vérifié du client ne peut fournir `n` circuits
  disjoints par AS, il DOIT (MUST) se replier dans un ordre fixe — disjoints par
  AS → disjoints par nœud → tirages indépendants — et NE DOIT PAS (MUST NOT)
  poursuivre en silence comme si la propriété la plus forte était tenue. Les
  paramètres PEUVENT (MAY) être réduits (mode petit réseau : `n = 2, k = 2` avec
  disjonction au mieux) lorsque la taille viable estimée n'est pas atteinte.
- **PS-9.** Le client DOIT (MUST) exposer le niveau de disjonction réellement
  atteint pour un message, en des termes qu'un non-expert lit correctement : la
  foule est petite aujourd'hui ; voilà ce que vous achetez. Le contenu garanti
  (I-2) et le niveau de corrélation sont des énoncés distincts et DOIVENT (MUST)
  être montrés séparément.
- **PS-10 (estimation de taille résistante aux sybils).** L'estimation de la
  taille viable DOIT (MUST) ne compter que les relais vérifiés de façon
  indépendante et la diversité d'AS observée, jamais le décompte brut des
  enregistrements, afin qu'un adversaire ne puisse gonfler le réseau avec des
  sybils pour duper les clients et leur faire adopter des paramètres pleins dont
  la diversité est fausse (se rattache à OP-2).
- **PS-11 (la disjonction supposée n'est pas la disjonction réelle).** La
  protection qu'un client construit ne vaut que ce que vaut son jeu de données
  d'inférence, et le client DOIT (MUST) traiter le taux d'erreur du jeu de
  données comme un paramètre de sécurité de premier plan, non comme un détail
  d'implémentation. Le simulateur (`poc/network_sim.py`, §1) sépare la *vérité
  de terrain* — que l'adversaire exploite — de la *croyance* du client, et
  balaie le taux d'erreur d'inférence : à mesure que l'erreur croît, la sélection
  disjointe par AS devient en partie illusoire et tant le taux de rupture du
  contenu que la fuite de liaison croissent de façon monotone. Deux conséquences
  sont normatives : (a) pour une erreur d'inférence **aléatoire** (du bruit,
  une carte simplement inexacte), l'erreur érode **la liaison bien plus vite que
  le contenu** — une rupture de contenu exige toujours que l'adversaire soit sur
  `≥ k` circuits à la fois, de sorte que le plancher tient tandis que les
  métadonnées se dégradent d'abord ; l'UI NE DOIT PAS (MUST NOT) présenter un
  faible chiffre de rupture de contenu comme s'il bornait aussi la liaison. Cette
  asymétrie ne tient **que pour une erreur aléatoire** ; une carte *choisie par
  l'adversaire* n'est pas du bruit (voir PS-12) ;
  (b) un **échantillon de gossip** plus mince (PS-10, I-3) force le repli plus
  tôt : un client qui connaît trop peu de relais ne peut pas construire du tout
  de circuits disjoints par AS et retombe à `none`, où le taux de rupture bondit
  (§2). L'estimation de taille viable (PS-10) DOIT (MUST) par conséquent tenir
  compte de l'échantillon *atteignable*, non du réseau entier. Les chiffres à
  erreur nulle et vue complète sont le meilleur cas ; un client conforme DOIT
  (MUST) présenter le niveau atteint (PS-9) depuis sa vue réelle, bruitée et
  partielle.
- **PS-12 (une carte hostile ne doit pas orienter la sélection vers
  l'adversaire).** `[claim-critical]` Une carte *choisie par l'adversaire* n'est
  pas une erreur aléatoire, et l'asymétrie de PS-11(a) ne protège **pas** contre
  elle. Une carte que l'adversaire contrôle dispose de deux leviers sur la
  sélection disjointe par AS : donner aux propres relais co-localisés de
  l'adversaire des AS fictifs *distincts* (pour qu'ils ne s'excluent jamais
  mutuellement), et donner aux relais *honnêtes* des AS fictifs *entrant en
  collision* (de sorte qu'une fois que le circuit 1 a choisi un relais honnête,
  tout autre relais honnête paraisse partager un AS et soit filtré). Le vivier de
  candidats honnêtes s'effondre alors après le premier tirage et le client
  sélectionne les circuits 2…`n` presque entièrement parmi les relais de
  l'adversaire — plaçant l'adversaire sur la garde **et** la sortie de `≥ k`
  circuits **de façon déterministe**, une rupture de *contenu*, alors que le
  client croit toujours avoir atteint la disjonction par AS et ne lève aucun
  avertissement de repli. Démontré face à `poc/network_sim.py` : une carte
  d'orientation fait passer le taux de rupture de contenu de ~0 % à **100 % à
  ~15 %** de possession adverse (contre un taux à un seul chiffre pour une carte
  honnête à 35 %). Donc **une mauvaise carte PEUT atteindre le contenu, pas
  seulement la liaison** (ceci corrige une surestimation antérieure ; la Partie 8
  ID-8a est corrigée en conséquence). Les défenses qu'un client conforme DOIT
  (MUST) appliquer :
  1. **Ne pas laisser la carte seule effondrer le vivier honnête.** Un client NE
     DOIT PAS (MUST NOT) construire un ensemble de circuits dans lequel plus
     qu'une fraction bornée des circuits dépend, pour leur disjonction mutuelle
     affirmée, de relais que le client ne peut corroborer *indépendamment* comme
     distincts (mélange de sources GR-8, PS-10 « ne compter que les sources
     vérifiées indépendamment »). Si la sélection disjointe-selon-la-croyance
     devait tirer les circuits 2…`n` d'un vivier que la carte a rendu
     suspicieusement petit, le client DOIT (MUST) traiter cela comme une
     condition de repli/anomalie (PS-8, PS-9), non comme un succès.
  2. **Une carte qui implique une structure d'AS invraisemblable est elle-même
     une anomalie.** Une carte sous laquelle l'*échantillon honnête atteignable*
     du client s'effondre à un seul ou quelques AS tandis que le reste façonné
     par l'adversaire est maximalement divers est une signature d'orientation ;
     le client DEVRAIT (SHOULD) la diffuser par gossip comme une anomalie de
     carte (Partie 8 ID-10) et se replier.
  3. **La reconstruction est la vraie défense.** Une carte d'orientation n'est
     pas reproductible à partir d'entrées publiques (Partie 8 ID-5a) ; un client
     qui reconstruit, ou qui s'accorde avec un pair honnête qui l'a fait, la
     rejette. Jusque-là, le client DOIT (MUST) traiter les affirmations de
     disjonction d'une carte non vérifiée comme non vérifiées, non comme atteintes
     (PS-9).
  Le résidu honnête demeure : dans la fenêtre d'éclipse d'un client qui a accepté
  une carte d'orientation non vérifiée et ne peut pas encore reconstruire, le
  plancher de contenu peut tomber. Ceci est borné par la marge `k`/`n` et par les
  défenses ci-dessus, non par une affirmation que cela ne peut pas se produire.

## 6. La procédure de vérification (PS-13…PS-19)

### 6.1 La procédure et son certificat

- **PS-13 (la procédure est une fonction pure de trois entrées déclarées).**
  `[claim-critical]` La construction des circuits DOIT (MUST) pouvoir s'exprimer
  comme une fonction déterministe
  ```
      verify(sample, map, corroboration, n, k)  ->  (circuits, certificate)
  ```
  d'exactement trois entrées côté client, et rien d'autre :
  - **`sample`** — l'échantillon de gossip vérifié des relais du client (Partie 2,
    décompté sous PS-10 : *uniquement les relais vérifiés de façon indépendante*) ;
  - **`map`** — la carte d'inférence de la Partie 8, nommée par son hachage `H` et
    portant son propre taux d'erreur mesuré `e` (ID-12) ;
  - **`corroboration`** — un nombre par relais `c_j ∈ [0,1]` indiquant à quel point
    l'AS/la juridiction inféré(e) du relais est corroboré(e) de façon indépendante
    (PS-15).
  La sortie est de `n` circuits **et** un **certificat de disjonction** (PS-14).
  Aucune étape ne peut lire l'emplacement auto-déclaré du relais (GR-3, PS-4), un
  annuaire de confiance (I-3), ni la vérité de terrain (il n'y en a aucune à lire —
  c'est tout le problème). Une implémentation conforme qui ne peut pas exprimer sa
  sélection sous la forme de cette fonction pure ne peut pas émettre de certificat
  vérifiable et est non conforme : un implémenteur disposant de cette spécification
  et des trois mêmes entrées DOIT (MUST) pouvoir reconstruire la même décision
  circuits-et-certificat (I-1).

- **PS-14 (ce que contient le certificat — et comment il est vérifiable par
  machine).** `[claim-critical]` Le certificat est un enregistrement en CBOR
  canonique (encodage de la Partie 0) portant **exactement** les champs dont une
  seconde partie a besoin pour le **recalculer et le confirmer**, et aucun champ qui
  demande qu'on lui fasse confiance :
  1. **`map_hash`** — le `H` contre lequel le certificat a été calculé (ID-2). Le
     certificat n'a aucun sens sans lui : *« disjoint par AS »* n'est jamais une
     affirmation autonome, seulement *« disjoint par AS sous la carte `H` »*.
  2. **`map_error`** — le couple `(mismap_rate, unknown_rate)` fourni par la carte
     (ID-12), copié verbatim afin que le vérificateur n'ait pas à le remesurer. Leur
     somme est l'erreur par recherche `e` utilisée ci-dessous.
  3. **`circuits`** — pour chacun des `n` circuits, les identifiants des relais
     (empreintes de clés GR-2) à la garde/au milieu/à la sortie, et pour les
     **pivots** (garde et sortie — les deux positions qu'un adversaire au niveau AS
     corrèle, PS-3) le couple `(AS, juridiction)` **cru** que la carte a attribué,
     ou `unknown`.
  4. **`corroboration`** — le `c_j` par pivot utilisé (PS-15), afin que le
     vérificateur recalcule avec les mêmes réductions.
  5. **`class`** — la classe de disjonction atteinte, l'une de `as` / `node` /
     `none` (ordre PS-2), c'est-à-dire la propriété la *plus forte* que l'ensemble
     satisfait réellement sous la carte, non celle qui a été demandée.
  6. **`confidence`** — un nombre dans `[0,1]` (PS-16), la borne inférieure
     conservatrice sur la probabilité que l'affirmation de `class` tienne, compte
     tenu des marges d'erreur de la carte et de la corroboration.
  7. **`steering_flag`** — le verdict du détecteur de PS-12 sur l'**échantillon
     atteignable complet** du client (PS-17), et le ratio de survie du vivier qui le
     sous-tend.
  Un vérificateur **détenant la même carte `H`** DOIT (MUST) pouvoir : (a)
  re-rechercher le couple `(AS, juridiction)` de chaque pivot dans `H` et confirmer
  qu'il correspond au champ 3 ; (b) recalculer `class` à partir de ces recherches
  par le test de disjonction PS-2 ; (c) recalculer `confidence` à partir des champs
  2, 4, 5 et 7 par la formule PS-16 **telle que déclarée** ; et (d) confirmer que
  l'enregistrement est cohérent en interne. Si un recalcul est en désaccord, le
  certificat est **invalide** et DOIT (MUST) être rejeté (il a été calculé contre
  une carte différente, ou falsifié). Le certificat n'engage aucune signature :
  comme la carte elle-même (ID-11), **c'est la reproduction, non la signature, qui
  arbitre.**

  **Ce que le vérificateur peut et ne peut pas redériver — énoncé honnêtement (une
  conclusion d'une relecture hostile).** Deux champs sont des *entrées que le client
  d'origine a mesurées*, non des quantités qu'un vérificateur distant peut recalculer
  à partir de `H` seul : `steering_flag`/`pool_survival` sont des fonctions de
  l'**échantillon de gossip atteignable complet de ce client** (PS-17), qui n'est pas
  un champ du certificat ; et chaque `c_j` est la **mesure de corroboration** de ce
  client (PS-15), elle non plus pas redérivable à partir de `H`. Le certificat est
  donc vérifiable **relativement à ses entrées déclarées** — un vérificateur confirme
  que la confiance découle des `map_error`, `corroboration` et `steering_flag`
  énoncés par la formule PS-16 — mais ce n'est **pas** une preuve inconditionnelle :
  un client qui **ment** sur son propre `c_j` à la hausse, ou qui omet un drapeau
  d'orientation que son échantillon aurait levé, produit un certificat qui se
  recalcule *de façon cohérente* et reste néanmoins faux. Les défenses contre cela ne
  sont pas dans le certificat mais dans le réseau : un client indépendant sur la même
  `H` et un échantillon qui se recoupe dérive un certificat **différent**, et la
  divergence est diffusée par gossip comme une anomalie (PS-19, ID-10) exactement
  comme l'est une divergence de carte. Le certificat supprime le « disjoint par AS :
  oui » *silencieux* ; il ne rend pas la confiance d'un client menteur auto-probante.
  C'est une limite déclarée (§6.6), non une limite cachée.

### 6.2 Corroboration : l'entrée de confiance par relais

- **PS-15 (la corroboration par relais est un accord indépendant, décomptée comme
  PS-10).** L'entrée `c_j` d'un relais n'est **pas** un score de confiance et NE DOIT
  PAS (MUST NOT) provenir du relais ni d'une quelconque partie unique. C'est le degré
  auquel l'AS inféré du relais est **corroboré de façon indépendante** — la même
  discipline « ne compter que ce qui est vérifié de façon indépendante » que PS-10
  applique aux estimations de taille et que GR-8 applique au gossip :
  - `c_j = 0` — l'AS du relais provient de la carte `H` **et de rien d'autre** ; le
    client n'a aucun second point de vue. C'est la valeur par défaut et le plancher
    conservateur.
  - `c_j` monte vers `1` à mesure que des points de vue **indépendants et à sources
    mélangées** (GR-8) s'accordent sur le même AS inféré pour ce relais : une seconde
    carte reconstructible depuis un ensemble de collecteurs disjoint (ID-3a), une
    observation hors bande du préfixe annoncé du relais, un pivot de certificat
    diffusé par un pair qui correspond. Valeur provisoire (s) : `c_j = 1 − 2^(−v)`
    pour `v` points de vue corroborants indépendants (un point de vue ⇒ 0,5, deux ⇒
    0,75, …), plafonné sous `1` car aucun nombre fini de points de vue de l'overlay
    ne voit la baie (§6.6).
  Un relais que la carte étiquette `unknown` a `c_j = 0` **et** contribue un AS-cru
  `unknown` déjà conservateur (PS-5) : il entre en collision avec tout, de sorte
  qu'il survit rarement jusqu'à une position de pivot, et lorsqu'il le fait la formule
  de confiance le traite déjà comme pleinement incertain (PS-16). La corroboration NE
  DOIT PAS (MUST NOT) être inférée du *nombre* de pairs qui rapportent une valeur
  avant que le mélange de sources GR-8/PS-10 soit appliqué — un sybil ne peut pas
  voter l'AS d'un relais en forte corroboration par la seule masse du nombre (se
  rattache à OP-2, exactement comme ID-9).

### 6.3 La formule de confiance

- **PS-16 (la confiance est une borne inférieure conservatrice sur un mauvais
  étiquetage indépendant).** `[claim-critical]` Soit les **pivots** d'un ensemble de
  circuits les relais distincts à la garde ou à la sortie à travers les `n` circuits
  (au plus `2n`, moins après déduplication). La disjonction affirmée tient
  **uniquement si aucun pivot n'est mal étiqueté** d'une façon qui transforme un
  couple cru-distinct en un couple réellement-en-collision. La carte fournit l'erreur
  par recherche `e = mismap_rate + unknown_rate` (ID-12) ; la corroboration réduit la
  probabilité **effective** de mauvais étiquetage d'un pivot à
  ```
      p_j = e · (1 − c_j).
  ```
  En traitant les mauvais étiquetages par pivot comme **indépendants**, la
  `confidence` du certificat pour `class = as` est le produit
  ```
      confidence  =  Π_j ( 1 − e · (1 − c_j) )       sur les pivots j,
  ```
  rabaissée à `0` par le filtre d'orientation de PS-17. Pour `class = node`, la
  disjonction ne dépend pas du tout de la carte (l'identité de nœud est engagée par
  GR-2, non inférée), donc `confidence = 1 − (filtre PS-17)`. Pour `class = none`,
  `confidence = 0` par définition : aucune disjonction n'est affirmée, donc aucune
  n'est attestée.

  **L'hypothèse d'indépendance, nommée et justifiée comme conservatrice.** Les
  mauvais étiquetages réels des pivots ne sont **pas** indépendants : un seul préfixe
  BGP erroné dans la carte mal étiquette d'un coup chaque relais qui en dépend
  (corrélation positive). Nous supposons l'indépendance malgré tout, et elle est
  **conservatrice dans la direction qui compte** pour une *borne inférieure* : le
  produit `Π(1 − p_j)` sous-compte le cas *corrélé* où plusieurs pivots partagent une
  seule cause de mauvais étiquetage — lorsque les mauvais étiquetages sont corrélés,
  la probabilité qu'*au moins un* pivot soit erroné est **plus faible** que ne
  l'implique le produit indépendant, de sorte que la vraie probabilité « tous les
  pivots corrects » est **plus élevée** que notre borne. Le produit est donc un
  plancher sur la confiance, c'est-à-dire qu'il ne surestime jamais la sécurité. Là où
  l'indépendance nous rendrait *sur*-confiants, c'est face à une cause *honnête*
  partagée (un seul AS correct géant), qui ne menace pas la disjonction ; la cause
  partagée adverse — une seule carte effondrant le vivier — n'est pas du tout traitée
  par ce produit mais par le filtre de PS-17, qui rabaisse la confiance à 0 quel que
  soit le produit. Les deux formes de défaillance sont donc proprement séparées :
  **erreur de carte aléatoire/corrélée → le produit (conservateur) ; structure de
  carte adverse → le filtre (plancher dur).**

  Ancrage (non éludé). Face à `poc/network_sim.py`, sans corroboration (`c_j = 0`,
  donc `p_j = e`), `1 − confidence` borne supérieurement le taux de collision
  d'AS-réel **observé** des pivots à chaque niveau d'erreur — par exemple à
  `e = 0.2`, `1 − confidence ≈ 0.83` face à un échec de disjonction réelle observé de
  `≈ 0.18` : pessimiste, ce qui est la bonne direction pour un plancher de sécurité,
  jamais optimiste. La corroboration le récupère de façon monotone (à `e = 0.2`, la
  confiance moyenne monte `0.17 → 0.43 → 0.84 → 0.99` à mesure que `c_j` uniforme va
  de `0 → 0.5 → 0.9 → 1.0`). Un client conforme DEVRAIT (SHOULD) présenter ce
  pessimisme honnête plutôt que de resserrer la borne avec un modèle qui suppose plus
  que ne le justifient les trois entrées déclarées — un plancher défendable vaut mieux
  qu'une fausse précision (PS-11).

### 6.4 Robustesse face à PS-12, par construction

- **PS-17 (le filtre d'orientation rabaisse la confiance — sur le bon signal, sur
  l'échantillon atteignable COMPLET).** `[claim-critical]` Avant que le produit de
  PS-16 ne soit rapporté, la procédure DOIT (MUST) appliquer le détecteur de la
  défense 2 de PS-12 (`detect_steering`) à l'**échantillon de gossip atteignable
  entier** du client, non aux `2n` pivots choisis — la structure vit dans la
  *population* et a disparu des pivots au moment où ils sont tirés (vérifier les seuls
  pivots n'attrape une carte d'orientation que sur ~la moitié des messages). **Le
  signal doit être celui que l'adversaire ne peut pas éviter.** Une première version
  de ce détecteur se fondait sur « un seul AS-cru géant détenant le vivier honnête
  effondré, entouré de singletons », et une relecture hostile l'a **contourné** en
  effondrant le vivier honnête en *quelques* faux AS plutôt qu'un seul géant — pas
  d'AS géant, détecteur silencieux, contenu rompu sur ~30 % des messages. Le signal
  correct et porteur est la **fraction anormale de singletons** : pour que ses relais
  co-localisés paraissent disjoints par AS, l'adversaire DOIT (MUST) donner à chacun
  un faux AS distinct, c'est-à-dire en faire des singletons, et un réseau réel a très
  peu d'AS singletons. Le détecteur DOIT (MUST) donc se déclencher lorsque les relais
  singletons dépassent une petite fraction de l'échantillon **et** que les relais non
  singletons tiennent dans trop peu d'AS encombrés pour construire `n` circuits
  disjoints (la seconde clause empêche le *bruit* d'inférence, qui crée lui aussi des
  singletons, de le déclencher). Mesuré face à `poc/network_sim.py`
  (`make_steering_map(honest_groups=g)` / le `detect_steering` corrigé) : ceci attrape
  le régime d'orientation **effectif** (`g = 1…5`, une rupture de contenu de 10–100 %)
  à ~100 % avec **0 %** de faux positifs sur les cartes honnêtes même à une erreur
  d'inférence jusqu'à 0,4. Par conséquent :
  - Si le détecteur se déclenche sur l'échantillon atteignable, le certificat DOIT
    (MUST) fixer `steering_flag = true`, `class = none` et `confidence = 0`, et le
    client DOIT (MUST) traiter le résultat comme la condition de repli/anomalie de
    PS-12 (le diffuser par gossip, ID-10 ; dégrader et le dire, PS-8/PS-9) — il NE
    DOIT PAS (MUST NOT) émettre un certificat `as`.
  - **Résidu déclaré :** une carte d'orientation *marginale* qui répartit le vivier
    honnête sur assez de faux AS (`g ≥ 8`) pour construire des circuits réellement
    disjoints échappe au détecteur — mais là sa rupture de contenu n'est que de ~5 %,
    indiscernable d'un petit réseau légitime, et bornée par la marge `k`/`n` et la
    confiance PS-16, non par une affirmation que cela ne peut pas se produire (§6.6).

- **PS-18 (précondition d'effondrement du vivier — défense 1 de PS-12, repliée comme
  une entrée de confiance).** `[claim-critical]` Indépendamment du détecteur
  structurel, la procédure DOIT (MUST) calculer le **ratio de survie du vivier
  honnête** : la fraction de l'échantillon atteignable et corroboré de façon
  indépendante (PS-10, PS-15 avec `c_j > 0`) qui demeure un candidat
  *cru-distinct-par-AS* **après** le tirage du premier circuit. Un certificat NE DOIT
  PAS (MUST NOT) affirmer `class = as` lorsque les circuits `2…n` ont été tirés d'un
  vivier que la carte a effondré sous une fraction bornée (valeur provisoire (s) :
  survie `< 1/n` de l'échantillon honnête corroboré), car alors la disjonction
  mutuelle affirmée de l'ensemble repose sur des relais que le client ne peut pas
  corroborer *indépendamment* comme distincts — exactement la défense 1 de PS-12. Dans
  ce cas la procédure DOIT (MUST) soit abaisser `class` à `node` (en abandonnant
  entièrement l'affirmation dépendante de la carte), soit poser la condition d'anomalie
  comme dans PS-17. **La confiance est FAIBLE exactement quand PS-12 dit que le client
  est orienté :** le filtre la met à zéro sur la signature structurelle, et la
  précondition de survie retire l'affirmation `as` quand le vivier est
  suspicieusement mince — de sorte qu'une carte d'orientation ne peut pas gagner de
  certificat `as` à forte confiance par l'un ou l'autre levier (AS fictifs distincts
  de l'adversaire ou AS honnêtes fictifs en collision). C'est la propriété non
  négociable, et elle est vérifiée, non affirmée : le même filtre que les tests de
  PS-12 montrent transformer une rupture de contenu de 100 % en un repli de 100 %
  pousse la confiance du certificat à 0 sur 100 % des cartes d'orientation.

### 6.5 Un certificat détaillé

Entrées : `n = 4`, `k = 3` ; un échantillon sain ; une carte `H = 0x9f2c…a17b`
fournissant `map_error = (0.04, 0.03)` donc `e = 0.07` ; les 8 pivots (4 gardes +
4 sorties) — 6 corroborés par un point de vue indépendant supplémentaire
(`c_j = 0.5`), 2 reposant sur la carte seule (`c_j = 0.0`) ; le détecteur
d'orientation ne se déclenche **pas** sur l'échantillon atteignable. Alors
`p_j = 0.035` pour les six et `0.07` pour les deux, et
`confidence = (1−0.035)^6 · (1−0.07)^2 = 0.698`.

```
disjointness-certificate (canonical CBOR; shown as a record):
  map_hash      : 0x9f2c3e...a17b
  map_error     : { mismap: 0.04, unknown: 0.03 }         # e = 0.07 (ID-12)
  class         : "as"                                     # le plus fort atteint, PS-2
  confidence    : 0.698                                    # produit PS-16, filtre=1
  steering_flag : false                                    # PS-17, contrôle vue complète
  pool_survival : 0.61                                     # PS-18, > 1/n = 0.25 OK
  circuits:
    - { guard: 4a1f.., mid: 7c02.., exit: e9d3..,
        pivots:[{as:3356, jur:"US", c:0.5},{as:1299, jur:"SE", c:0.5}] }
    - { guard: b17c.., mid: 02aa.., exit: 55f1..,
        pivots:[{as:3320, jur:"DE", c:0.5},{as:9002, jur:"GB", c:0.0}] }
    - { guard: cc90.., mid: 1d44.., exit: a7e8..,
        pivots:[{as:6830, jur:"NL", c:0.5},{as:2914, jur:"JP", c:0.5}] }
    - { guard: 3e5b.., mid: f108.., exit: 9b22..,
        pivots:[{as:174,  jur:"US", c:0.0},{as:8075, jur:"IE", c:0.5}] }
```
Lu correctement (PS-9) : *« Ces 4 circuits sont disjoints par AS **sous la carte
`H`**, laquelle admet un taux d'erreur de 7 % ; vu à quel point l'AS de chaque relais
est corroboré de façon indépendante, il y a au moins **70 % de chances** que la
disjonction par AS soit réelle et non un artefact d'un mauvais étiquetage. Ce n'est
pas une garantie, et cela ne dit rien d'un centre de données que la carte ne peut pas
voir (§6.6). »* Si le détecteur d'orientation s'était déclenché, chaque nombre
ci-dessus serait remplacé par `class: none, confidence: 0, steering_flag: true` et un
avertissement de repli — il n'existe pas de certificat à forte confiance pour un
client orienté.

```
  LE FLUX PRODUIRE-CIRCUITS-ET-CERTIFICAT

   sample (PS-10)      map H + e (ID-12)      corroboration c_j (PS-15)
        │                   │                        │
        └─────────┬─────────┴───────────┬────────────┘
                  ▼                      ▼
        ┌───────────────────┐   ┌─────────────────────────────┐
        │ detect_steering    │   │ sélection disjointe AS-crue │
        │ sur échantillon    │   │ (ordre PS-2 : as→node→none) │
        │ COMPLET            │   │  + survie du vivier (PS-18, │
        │ (PS-17, défense 2) │   │     défense 1)              │
        └─────────┬─────────┘   └──────────────┬──────────────┘
                  │                            │ n circuits + pivots
         déclen.? │                            ▼
         ┌────────┴────────┐       ┌────────────────────────────┐
       oui               non       │ confidence = Π(1−e(1−c_j))  │ PS-16
         │                 └─────▶ │ class = le plus fort atteint│
         ▼                         └──────────────┬─────────────┘
  class=none, conf=0                              ▼
  steering_flag=true         ┌─────────────────────────────────────┐
  → repli + gossip           │ CERTIFICAT {map_hash, map_error,     │
    (PS-8/9, ID-10)          │  circuits, corroboration, class,     │
                             │  confidence, steering_flag}          │
                             └──────────────┬──────────────────────┘
                                            ▼
                     un vérificateur avec le MÊME H recalcule et confirme
                     (la reproduction arbitre — aucune signature, ID-11)
```

- **PS-19 (le certificat est pour l'utilisateur et le pair, les deux).** La
  `confidence` et la `class` DOIVENT (MUST) piloter la surface d'honnêteté PS-9 que
  lit l'utilisateur (*la foule est disjointe à ce point aujourd'hui, avec cette
  certitude-là*), et le certificat DOIT (MUST) être diffusable par gossip pour qu'un
  pair détenant la même `H` puisse le redériver (PS-14) et pour qu'une divergence —
  deux clients, même `H` et même échantillon, certificat différent — soit attrapée et
  diffusée par gossip comme une anomalie (ID-10), le même signal immunitaire que la
  Partie 8 emploie pour la divergence de carte. L'UI NE DOIT PAS (MUST NOT) citer
  `confidence` comme si elle bornait la liaison : elle borne l'affirmation de
  disjonction du **contenu** ; les métadonnées se dégradent plus vite (PS-11(a)), et
  une forte confiance en `class = as` ne signifie pas une faible fuite de liaison.

### 6.6 Ce que cela ne résout pas

Le certificat atteste une **cohérence contre un jeu de données à confiance bornée,
non une disjonction vraie** (Partie 8 §10), et l'honnêteté de toute cette procédure
tient à le dire sur chaque enregistrement. Un adversaire qui co-localise des relais
dans une seule baie tout en annonçant un espace d'adressage que les données
publiques BGP/RIR attribuent **véritablement** à des AS différents est étiqueté
disjoint par la carte **correcte** — de sorte que les recherches correspondent à `H`,
le détecteur d'orientation ne se déclenche pas (la structure n'est pas une signature
d'orientation, c'est la véritable table de routage publique), le vivier ne s'effondre
pas, et les pivots sont bien corroborés **parce que chaque point de vue honnête
s'accorde avec la carte**. La procédure émet donc un **certificat `as` à forte
confiance qui est néanmoins faux** : `confidence` mesure la chance que l'ensemble soit
disjoint *sous la carte*, et ici la carte est juste et l'overlay ne peut toujours pas
voir la baie. C'est le résidu de co-localisation de la Partie 8 §10, et c'est la seule
limitation que le certificat **ne peut pas** supprimer — aucune quantité de
corroboration ne la referme, car la corroboration ne confirme qu'un accord *avec les
données publiques*, et les données publiques elles-mêmes sont ce que l'adversaire a
satisfait. Son ampleur est exactement l'écart du simulateur entre l'AS cru et l'AS
vrai à `infer_error = 0` : le certificat affiche 1.0, la réalité peut quand même entrer
en collision, et seul un relèvement de la marge `k`/`n` — non un quelconque champ du
certificat — borne la perte. Le don du certificat est qu'il ne **cache** jamais cela :
il énonce ses propres marges d'erreur, se rabaisse à zéro sous orientation (PS-17/18),
et est vérifiable par quiconque détient la carte (PS-14). Il transforme « disjoint par
AS : oui » — un mensonge — en « disjoint par AS sous la carte `H` avec erreur `e`,
confiance `c` » — un énoncé vrai dont le seul angle mort restant est nommé ici et
nulle part caché.

Trois limites supplémentaires qu'une relecture hostile a fait émerger, déclarées ici
plutôt que maquillées :

- **L'orientation marginale échappe au détecteur.** Une carte d'orientation qui
  répartit le vivier honnête sur assez de faux AS (`g ≥ 8`) construit des circuits
  réellement disjoints et ne déclenche donc pas le détecteur de fraction de singletons
  (PS-17) — mais sa rupture de contenu n'est alors que de ~5 %, le niveau d'un petit
  réseau légitime, bornée par la marge `k`/`n` et la confiance PS-16. Le détecteur
  attrape le régime d'orientation *effectif* (rupture de 10–100 %), non toute carte.
- **La confiance d'un client menteur n'est pas auto-probante.** `confidence` n'est
  qu'aussi honnête que les `c_j` et `steering_flag` que le client d'origine a mesurés
  et mis dans le certificat ; un client qui surestime sa propre corroboration, ou qui
  omet un drapeau, émet un certificat qui se recalcule de façon cohérente et reste
  néanmoins faux (PS-14). La parade est sociale, non arithmétique : un client
  indépendant sur la même `H` dérive un certificat différent, et la divergence est
  diffusée par gossip comme une anomalie (PS-19). Le certificat supprime le mensonge
  *silencieux*, non un mensonge *détectable*.
- **Le produit de confiance borne les collisions de couples de pivots, non toute
  collision.** PS-16 mesure la chance qu'un *couple* de pivots cru-disjoint soit
  réellement en collision. Un mauvais étiquetage qui met un pivot en collision avec un
  nœud du *milieu*, ou qui confond juridiction et AS, est hors du produit et doit être
  attrapé par le test de disjonction PS-2 sur le circuit complet, non lu sur le nombre
  de confiance.


## 7. Ce que cette partie ne décide pas

La distribution sans confiance du jeu de données de disjonction, et la
vérification formelle qu'un ensemble choisi est aussi disjoint qu'affirmé
(OP-1) ; les seuils honnêtes de taille viable et la question de savoir si
`n = 2, k = 2` vaut même la peine d'être exécuté (OP-3) ; l'économie du
renouvellement des gardes ; la sélection des chemins sur le maillage de blackout,
où AS et juridiction ne signifient rien (OP-6). `poc/network_sim.py` est la
valeur provisoire exécutable derrière cette partie — attaquez son modèle, puis
ce texte.
