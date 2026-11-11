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
  sont normatives : (a) l'erreur érode **la liaison bien plus vite que le
  contenu** — une rupture de contenu exige toujours que l'adversaire soit sur
  `≥ k` circuits à la fois, de sorte que le plancher tient tandis que les
  métadonnées se dégradent d'abord ; l'UI NE DOIT PAS (MUST NOT) présenter un
  faible chiffre de rupture de contenu comme s'il bornait aussi la liaison ;
  (b) un **échantillon de gossip** plus mince (PS-10, I-3) force le repli plus
  tôt : un client qui connaît trop peu de relais ne peut pas construire du tout
  de circuits disjoints par AS et retombe à `none`, où le taux de rupture bondit
  (§2). L'estimation de taille viable (PS-10) DOIT (MUST) par conséquent tenir
  compte de l'échantillon *atteignable*, non du réseau entier. Les chiffres à
  erreur nulle et vue complète sont le meilleur cas ; un client conforme DOIT
  (MUST) présenter le niveau atteint (PS-9) depuis sa vue réelle, bruitée et
  partielle.

## 6. Ce que cette partie ne décide pas

La distribution sans confiance du jeu de données de disjonction, et la
vérification formelle qu'un ensemble choisi est aussi disjoint qu'affirmé
(OP-1) ; les seuils honnêtes de taille viable et la question de savoir si
`n = 2, k = 2` vaut même la peine d'être exécuté (OP-3) ; l'économie du
renouvellement des gardes ; la sélection des chemins sur le maillage de blackout,
où AS et juridiction ne signifient rien (OP-6). `poc/network_sim.py` est la
valeur provisoire exécutable derrière cette partie — attaquez son modèle, puis
ce texte.
