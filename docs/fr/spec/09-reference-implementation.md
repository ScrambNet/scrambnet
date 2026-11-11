# Spécification ScrambNet — Partie 9 : Exigences d'implémentation de référence

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/09-reference-implementation.md)).

**Statut : BROUILLON (DRAFT).** Cette partie énonce, sous forme d'exigences numérotées
(`RI-n`), ce qu'un véritable nœud DOIT (MUST) faire et que la preuve de concept omet
délibérément — chaque règle étant rattachée à la menace à laquelle elle répond et, là où
cela s'applique, à l'invariant (I-1…I-4) qu'elle protège. Le jouet dans `poc/` est une
*spécification exécutable*, non un nœud : il le dit dans ses toutes premières lignes
(« NOT PRODUCTION CODE. No constant-time arithmetic, no networking, no onion layer »). Tout
ce qui suit est la distance entre ce jouet et quelque chose que vous pourriez pointer vers
un réseau hostile. Chaque chiffre est un homme de paille à attaquer par numéro d'exigence ;
l'invitation la plus aiguë est au §1, et le §11 nomme ce qui reste ouvert.

## 1. La tension centrale : un plancher informationnellement sûr n'est inconditionnel qu'autant que le code qui le calcule

ScrambNet vend un plancher de contenu **inconditionnel** (I-2, prouvé dans la Partie 7) : en
dessous de `k` parts, le texte chiffré est *statistiquement indépendant* du secret, face à
un calcul illimité et à n'importe quel ordinateur quantique. Cette preuve porte sur des
**valeurs** — les octets de part que détient un adversaire ne portent aucune information sur
le secret. Elle ne dit rien sur **la façon dont une machine réelle calcule ces octets**, et
c'est là que le plancher peut être perdu sans qu'un seul théorème ne soit faux.

Une multiplication en GF(2⁸) par recherche de table (les tables `_EXP`/`_LOG` de la PoC,
`poc/dispersal.py`) indexe la mémoire à une adresse qui **dépend d'un octet de part secret**.
Sur du matériel réel, l'état du cache rend cet accès observable en temps par un attaquant
co-résident. La recherche divulgue donc, à travers un canal auxiliaire temporel, les octets
mêmes que le plancher est construit pour cacher. Le plancher serait alors *inconditionnel en
théorie et récupérable en pratique*.

C'est la phrase la plus importante de cette partie, énoncée comme un principe :

> **Un canal auxiliaire de temporisation ou de divulgation mémoire qui révèle des octets de
> part secrets, des coefficients ou la clé de contenu n'est pas une rupture « calculatoire »
> qu'I-2 serait autorisé à subir. C'est une rupture d'I-2 elle-même.** La Partie 7 autorise
> exactement une hypothèse calculatoire — l'AEAD de bout en bout *au-dessus* de `k` (SP-1a) —
> et rien d'autre. Un canal auxiliaire qui divulgue des octets secrets sous `k` ne coûte pas
> à l'adversaire « du travail sous une hypothèse » ; il lui remet les octets. La preuve de
> SA-1/SA-2 suppose que l'adversaire voit **seulement** les `k−1` valeurs de part et les
> paramètres publics. Un canal auxiliaire ajoute une vue que la preuve n'a jamais concédée, et
> la preuve ne la couvre pas.

Deux conséquences, que le reste de cette partie rend normatives :

- Le **chemin de calcul** du plancher — chaque opération GF(2⁸) sur des données dépendant du
  secret dans la découpe de Shamir, la reconstruction, et l'interpolation de Lagrange — DOIT
  (MUST) être à temps constant (RI-1). Ce n'est pas un durcissement ; c'est la condition sous
  laquelle SA-1/SA-2 décrivent le système réel, exactement comme SA-3 (l'aléa des
  coefficients) l'est.
- Le **résidu mémoire** du plancher — parts, coefficients, clés dérivées — NE DOIT PAS (MUST
  NOT) survivre pour être lu depuis un vidage de tas, un fichier d'échange ou un vidage de
  cœur (core dump) (RI-9). Un plancher qui est informationnellement sûr sur le fil mais
  récupérable depuis `/proc` n'est pas un plancher.

La PoC est honnête sur le fait qu'elle échoue aux deux : ce sont des recherches de table en
pur Python sans mise à zéro, correctes mais fuyantes, et elle le dit. Cette partie est la
liste qu'un véritable nœud doit satisfaire à la place. Là où la PoC impose *déjà* une règle
(elle refuse de disperser du texte en clair qui n'est pas passé par l'AEAD — `send()` scelle
avant de découper), c'est le barème, non une amabilité, et RI-6 l'élève à un DOIT (MUST).

**Portée.** Cette partie contraint l'*implémentation* de constructions fixées ailleurs ; elle
n'introduit aucun nouveau format sur le fil et ne change aucun octet sur le fil (ce serait un
changement I-1/I-4 et cela relève des Parties 1 à 6). Elle NE DOIT PAS (MUST NOT) être lue
comme relâchant une quelconque exigence qu'elle référence ; là où elle semble le faire, la
partie référencée l'emporte et la contradiction est un défaut à signaler.

## 2. Arithmétique de corps à temps constant (le chemin de calcul du plancher)

- **RI-1 (GF(2⁸) à temps constant, protège I-2).** Toute l'arithmétique GF(2⁸) appliquée à des
  données dépendant du secret — la découpe Shamir `split` (évaluation de polynôme sur des
  coefficients secrets et le terme constant secret), `reconstruct`/l'interpolation de Lagrange
  (y compris l'**inversion** de corps `gf_inv` dans le dénominateur de la base), et toute
  multiplication dont l'opérande est un octet de part, un coefficient ou un octet de secret
  reconstruit — DOIT (MUST) être calculée **sans branchement dépendant du secret et sans accès
  à une adresse mémoire dépendant du secret**. Concrètement, une implémentation NE DOIT PAS
  (MUST NOT) indexer une table (`_EXP`/`_LOG`, une S-box, ou tout tableau) à un décalage dérivé
  d'une valeur secrète. Les techniques conformes sont une multiplication à temps constant
  bitsliced ou en corps-tour (tower-field), une réduction par multiplication sans retenue
  (`CLMUL`), ou un corps fourni par une bibliothèque qui *documente* un comportement à temps
  constant pour ces opérations. Menace : un adversaire co-résident ou à temporisation à distance
  récupère des octets de part secrets depuis le cache ou la temporisation des branchements —
  une **rupture directe d'I-2** (voir §1), non une rupture calculatoire. Cela s'applique
  symétriquement à **la découpe et à la reconstruction** : une extrémité qui reconstruit
  divulgue le secret qu'elle vient de récupérer exactement comme un découpeur divulgue celui
  qu'il disperse.
- **RI-1a (l'inversion et la division ne sont pas exemptées).** L'inverse du dénominateur de
  Lagrange (`gf_inv` dans `poc/dispersal.py`, y calculé comme `_EXP[255 − _LOG[a]]`) opère sur
  une valeur dérivée de l'ensemble de parts secret et DOIT (MUST) être à temps constant ; une
  exponentiation dépendant des données ou un inverse par recherche de table n'est pas conforme.
  Une implémentation DEVRAIT (SHOULD) préférer une interpolation sans inversion (p. ex. en
  regroupant les dénominateurs et en inversant une seule fois par Fermat `a^{254}` au moyen
  d'une chaîne d'additions fixe, ou par l'astuce de Montgomery) de sorte qu'aucune division
  dépendant du secret ne subsiste. Les points d'évaluation `x_1…x_n` sont **publics** (Partie 7
  §2), de sorte que l'arithmétique sur *eux seuls* n'a pas besoin d'être à temps constant ; dès
  qu'un point public est multiplié dans un secret, le produit est secret.
- **RI-1b (les vecteurs ne certifient pas la temporisation).** Passer les vecteurs de test GF de
  la feuille de route 3.2 prouve qu'une multiplication est *correcte*, non qu'elle est *à temps
  constant* : les tables fuyantes de la PoC passent ces mêmes vecteurs. Une implémentation NE
  DOIT PAS (MUST NOT) traiter la conformité aux vecteurs comme une preuve de conformité à RI-1.
  Le comportement à temps constant DEVRAIT (SHOULD) être vérifié par un outil d'analyse
  temporelle ou statistique (p. ex. des tests de fuite de type dudect) et, là où la plateforme
  le permet, en désactivant les transformations du compilateur qui réintroduisent des
  branchements dépendant du secret (RI-9b).
- **RI-1c (toute la durée de vie du secret est à temps constant, pas seulement ses opérations de
  corps, protège I-2).** La discipline du temps constant est définie par le **flux de données,
  non par le fait de nommer les opérations GF** : toute valeur contaminée par un octet de part,
  un coefficient ou un octet de secret reconstruit hérite de l'obligation RI-1 jusqu'à sa mise à
  zéro (RI-9), et cette obligation s'étend *au-delà* de la couche de corps. En particulier, le
  préfixe de longueur du secret reconstruit (SP-8) DOIT (MUST) être analysé, et le texte en
  clair récupéré copié, découpé et validé, **sans branchement dépendant du secret et sans accès
  mémoire dépendant de la longueur secrète** ; `unpad` NE DOIT PAS (MUST NOT) se brancher sur la
  longueur décodée d'une manière qu'un observateur peut temporiser, et aucune comparaison,
  vérification de bornes ou déplacement de tampon sur un secret ne PEUT (MAY) dépendre des
  données. Menace : le principe propre du §1 — « une extrémité qui reconstruit divulgue le
  secret qu'elle vient de récupérer exactement comme un découpeur divulgue celui qu'il
  disperse » — n'est imposé que si la manipulation *entière* du secret récupéré est à temps
  constant, et non seulement son arithmétique GF. Un nœud qui utilise un corps à temps constant
  vérifié (RI-1) et un AEAD à temps constant éprouvé (RI-8) mais qui ensuite se branche sur une
  longueur récupérée satisfait tous les autres DOIT (MUST) tout en divulguant la structure du
  secret récupéré par temporisation, ce qui est une rupture directe d'I-2 par le même argument
  que RI-1.

## 3. Discipline du CSPRNG (le plancher est exactement aussi fort que son aléa)

Le plancher n'est pas plus fort que l'aléa des coefficients de Shamir : SA-3 de la Partie 7 est
le « composant à la plus haute assurance » de toute la spécification, et
`test_properties.test_coefficient_reuse_breaks_the_floor` montre que la réutilisation divulgue
le secret avec certitude. La même discipline gouverne tout autre secret que le nœud tire.

- **RI-2 (DRBG cryptographique issu de l'OS, protège I-2 via SA-3).** Tout aléa secret — les
  coefficients de Shamir (SA-3), l'éphémère de circuit par paquet `x` de CH-3,
  `msg_nonce`/les compteurs de messages là où ils ne sont pas déterministes, la génération de
  `kpair`, et tout sel de `box_id` — DOIT (MUST) être produit par un DRBG cryptographiquement
  sûr amorcé depuis le CSPRNG du système d'exploitation (`getrandom`/`getentropy`,
  `/dev/urandom` une fois le pool initialisé, ou une source équivalente bloquant jusqu'à ce
  qu'elle soit initialisée). Une implémentation NE DOIT PAS (MUST NOT) utiliser un PRNG non
  cryptographique (un LCG, un Mersenne Twister, `rand()`, un hachage-de-compteur, ou un flux
  réutilisé comme « aléa ») pour une quelconque valeur de cette liste.
- **RI-2a (sûreté face au fork et au clone — la catastrophe classique).** Un processus qui fait
  un `fork()`, qui est restauré depuis un point de contrôle, qui est migré, ou qui est cloné
  comme image de VM ou de conteneur NE DOIT PAS (MUST NOT) réutiliser un état de DRBG qui a
  produit une sortie avant la scission. L'implémentation DOIT (MUST) se réamorcer depuis l'OS au
  fork/à la restauration (p. ex. une discipline `pthread_atfork`/`MADV_WIPEONFORK`, ou un tirage
  OS par appel) de sorte que deux processus n'émettent jamais le même flux de coefficients ni le
  même éphémère `x`. Menace : deux clones de VM identiques découpent des messages *différents*
  sous les **mêmes coefficients**, et par SA-3 la paire d'ensembles de parts devient corrélée
  avec les deux secrets — la catastrophe d'aléa des manuels, et une rupture directe d'I-2.
  C'est signalé spécifiquement parce que c'est invisible pour tout test mono-processus.
- **RI-2b (vérifications de santé et de démarrage).** Avant d'émettre la première valeur
  secrète, un nœud DOIT (MUST) confirmer que la source d'entropie de l'OS est amorcée (il NE
  DOIT PAS (MUST NOT) se rabattre sur une source à faible entropie si le pool n'est pas prêt) et
  DEVRAIT (SHOULD) exécuter un auto-test de démarrage sur le DRBG. Un nœud DEVRAIT (SHOULD)
  effectuer un test continu de répétition/sortie bloquée sur l'entropie brute là où il y a
  accès, et DOIT (MUST) échouer en mode fermé — refuser de découper ou de construire un paquet —
  plutôt que de poursuivre avec un générateur suspect. Un générateur qui ne peut pas être
  vérifié est traité comme défaillant.
- **RI-2c (pas de coefficients injectables en production — mais les vecteurs de conformité
  s'exécutent tout de même).** Le paramètre `split(..., coeffs=...)` de la PoC n'existe que pour
  que les vecteurs puissent être déterministes et que la rupture par réutilisation soit
  démontrée. Un artefact de production NE DOIT PAS (MUST NOT) exposer un quelconque chemin —
  drapeau, configuration, variable d'environnement, ou symbole — qui laisse un appelant fournir,
  journaliser ou épingler des coefficients de Shamir ou l'éphémère `x` ; un tel chemin est un
  piège (foot-gun) pour SA-3. La réconciliation avec les vecteurs de conformité de la feuille de
  route 3.2 (RI-10), qui exigent des coefficients injectés déterministes pour se reproduire, est
  une **barrière de test au moment de la compilation** : le chemin d'injection PEUT (MAY)
  exister *uniquement* derrière une barrière qui est **absente de tout artefact de production**
  et inatteignable à l'exécution en production. Les vecteurs sont confrontés à une compilation de
  test qui active la barrière ; la compilation de production DOIT (MUST) lui être identique à
  l'absence près du code barré, et cette équivalence DEVRAIT (SHOULD) être vérifiée par la
  compilation (p. ex. un diff reproductible des deux). « Compilé hors du binaire, non simplement
  déconseillé » signifie exactement ceci : présent pour le binaire de test, physiquement absent
  de celui qui est livré — jamais un interrupteur à l'exécution.

## 4. État des nonces et de la rotation de clé à travers les redémarrages

Deux secrets différents ne doivent jamais être réutilisés à travers un redémarrage : le nonce
d'AEAD/d'étiquette (SP-7b) et l'époque statique `onion` du relais (CH-5). Un redémarrage est le
moment où un nœud est le plus tenté de « repartir à neuf » et de réutiliser une valeur qu'il a
déjà utilisée.

- **RI-3 (la ligne de crue monotone du nonce survit aux redémarrages, protège SP-7b et SP-1a).**
  Par `kpair`, le `msg_nonce` de l'expéditeur (un compteur de messages strictement croissant,
  SP-7b) DOIT (MUST) être persisté et NE DOIT PAS (MUST NOT) revenir en arrière à travers un
  redémarrage, un plantage ou un changement d'horloge. L'implémentation DOIT (MUST) `fsync` (ou
  la barrière de durabilité équivalente de la plateforme) la ligne de crue **vers un stockage
  stable avant que le nonce qu'elle couvre ne soit utilisé sur le fil**, de sorte qu'un plantage
  entre l'usage et la persistance ne puisse que *sauter* des nonces, jamais les répéter. Un nœud
  NE DOIT PAS (MUST NOT) réutiliser ni décrémenter un `msg_nonce` sous un même `kpair`. Menace :
  un `msg_nonce` réutilisé est **doublement fatal** (SP-7b) — il fait collisionner les
  étiquettes SP-7 (rendant un ensemble de parts liable à travers des drops en collusion) **et**,
  parce que `msg_nonce` est le nonce de ChaCha20-Poly1305 (SP-1a), détruit la confidentialité de
  l'AEAD comme un masque jetable réutilisé deux fois. Faire revenir le compteur en arrière après
  une sauvegarde restaurée est la défaillance réaliste, et c'est une rupture de confidentialité,
  non un simple accroc.
- **RI-3a (réserver à l'avance pour borner le coût du fsync).** Une implémentation PEUT (MAY)
  persister la ligne de crue par blocs (réserver `B` nonces en une écriture durable, les
  distribuer depuis la mémoire, persister de nouveau avant l'épuisement du bloc) pour éviter un
  fsync par message. Un plantage ne gâche alors au plus que la queue inutilisée d'un bloc —
  acceptable, car l'espace de compteur est grand et sauter est sûr tandis que répéter est fatal.
  Elle NE DOIT PAS (MUST NOT), sous aucun chemin de récupération après plantage, distribuer un
  nonce au niveau ou en deçà de la dernière marque durablement persistée.
- **RI-3b (une restauration n'est pas un redémarrage — détecter le retour en arrière ou retirer
  la clé, protège SP-7b/SP-1a).** RI-3/RI-3a défendent contre un *plantage* (la marque persistée
  ne fait jamais qu'avancer) ; elles ne défendent **pas** contre un instantané (snapshot) de VM,
  un instantané de système de fichiers, ou une **restauration** de sauvegarde qui rembobine la
  marque persistée elle-même — précisément le « faire revenir le compteur en arrière après une
  sauvegarde restaurée » que RI-3 nomme comme la défaillance réaliste. Un nœud NE DOIT PAS (MUST
  NOT) supposer que son magasin de nonces persisté est monotone à travers une telle restauration.
  Il DOIT (MUST) donc soit (a) lier la ligne de crue à un **sel** de nonce par
  démarrage/par restauration (ou un compteur de génération monotone) persisté dans la *même
  écriture durable* que la réservation, de sorte qu'un magasin rembobiné soit détectable, et à la
  détection **retirer le `kpair`** — dériver une clé de contenu/d'étiquette fraîche, traitant un
  sel réutilisé sous un compteur rembobiné comme une compromission — soit (b) refuser d'émettre
  sous le `kpair` affecté au moindre signe de restauration (l'horloge système reculant, ou le
  compteur de génération persisté décroissant) jusqu'à ce qu'un `kpair` frais soit négocié hors
  bande (Partie 6). La réservation à l'avance (RI-3a) DOIT (MUST) porter le compteur de
  génération dans l'écriture durable de la réservation, de sorte qu'une restauration ne puisse
  pas rejouer un bloc réservé entier sans être détectée. Menace : sans cela, une restauration
  d'instantané réémet un bloc entier de valeurs `msg_nonce` déjà utilisées — le masque jetable
  deux fois doublement fatal de RI-3, sur un chemin que la garde réservée aux plantages de RI-3a
  ne peut pas voir.
- **RI-4 (état de l'époque statique `onion` et retrait sûr, protège CH-5/CH-6).** Un relais DOIT
  (MUST) persister dans quelle époque statique `onion` il se trouve (la clé privée active, ses
  `created`/`expiry`, et la fenêtre de grâce des paquets en vol) de sorte qu'un redémarrage ne
  republie pas silencieusement une clé expirée, ne ressuscite pas une clé retirée, ni ne frappe
  une seconde statique « fraîche » à l'intérieur de la même époque déclarée. À la rotation (≤7
  days, CH-5) le relais DOIT (MUST), une fois la grâce des paquets en vol passée, **mettre à
  zéro la moitié privée de la statique retirée** (RI-9) et NE DOIT PAS (MUST NOT) la conserver ;
  un relais qui garde d'anciennes statiques agrandit sa propre fenêtre d'exposition à la liaison
  CH-6 et n'est pas conforme. Les clients restent liés par GR-4/CH-5 à rejeter tout
  enregistrement dont l'`expiry` dépasse `created + 7 days` (GR-2 clé 6), de sorte qu'un nœud qui
  oublie son époque ne peut pas étendre la fenêtre en republiant. Menace : un redémarrage qui
  fait revenir la statique dans une fenêtre que le client a déjà vue, ou qui ne détruit pas une
  statique retirée, rouvre exactement l'exposition à la liaison CH-5a que le plafond de rotation
  existe pour borner.

## 5. Persistance du cache de rejeu

ScrambNet rejette les rejeux à deux couches, et les deux sont à état : la couche circuit écarte
un `gamma` vu par époque de clé (SP-5), et la couche de stockage écarte un re-dépôt d'un
`(box_id, slot)` déjà stocké (SP-7b, RZ-7). Un redémarrage qui oublie cet état rouvre une
fenêtre de rejeu.

- **RI-5 (l'état de rejeu survit aux redémarrages, borné à l'époque, protège SP-5 / SP-7b).** Un
  relais DOIT (MUST) persister, ou reconstruire de façon sûre et complète, son cache de rejeu
  Sphinx des valeurs `gamma` vues **pour l'époque de clé courante**, et un drop DOIT (MUST)
  persister son ensemble de dépôts `(box_id, slot)` stockés, de sorte qu'un redémarrage ou un
  plantage n'accepte pas un paquet ou un dépôt qu'il a déjà vu à l'intérieur de l'époque vivante.
  Menace : un relais qui redémarre avec un cache de rejeu vide réadmettra tout paquet qu'un
  adversaire a capturé et réinjecte à l'intérieur de l'époque — une fenêtre de rejeu rouverte,
  qui à la couche de drop peut aussi multiplier ou déplacer le courrier honnête face au plafond
  par boîte RZ-7.
- **RI-5a (le cache est borné — par deux fenêtres de rétention *différentes*, non « l'époque »).**
  Les deux caches de rejeu sont chacun bornés en mémoire, mais par des fenêtres **distinctes**
  qu'une implémentation NE DOIT PAS (MUST NOT) confondre :
    - le cache de `gamma` Sphinx est borné par l'**époque de clé statique en oignon** (CH-5, ≤7
      days) — un `gamma` n'est rejouable que tant que la clé qui l'a clavé est vivante ;
    - l'ensemble de déduplication des dépôts `(box_id, slot)` est borné par l'**expiration du
      slot** (RZ-7, 7 days), **non** par la rotation de `box_id` d'1 jour (RZ-10). L'identifiant
      de boîte tourne quotidiennement pour l'*adressage*, mais un slot déposé est *stocké*
      pendant jusqu'à 7 days (plus la grâce de frontière RZ-14), de sorte qu'un re-dépôt est
      écartable aussi longtemps que le slot qu'il entrerait en collision peut encore être
      stocké — jusqu'à ~7 époques de boîte. Dimensionner cet ensemble à un jour le sous-dimensionne
      d'environ 7×.
  Une implémentation DOIT (MUST) écarter l'état de chaque cache une fois sa propre fenêtre passée
  (le cache de `gamma` à la fin de l'époque de clé, l'ensemble de dépôts à l'expiration du slot),
  ce qui plafonne la mémoire à peu près au volume de paquets de l'époque de clé et au volume de
  dépôts de 7 days respectivement. Elle PEUT (MAY) borner davantage la mémoire avec une structure
  de comptage (p. ex. un filtre de Bloom/cuckoo dimensionné) **uniquement si** elle est réglée de
  sorte que les faux positifs restent sous un taux opérationnellement négligeable ; un faux
  positif écarte un paquet honnête (un DoS auto-infligé), un faux négatif admet un rejeu (une
  défaillance de sécurité), de sorte que la structure DOIT (MUST) être dimensionnée pour rendre
  le second impossible dans sa fenêtre de rétention et le premier rare. Un nœud qui ne peut pas
  persister un cache DOIT (MUST) échouer en mode fermé pour une fenêtre qu'il ne peut pas couvrir
  (traiter l'intervalle oublié comme rejouable et, pour le cache de `gamma`, faire tourner
  l'époque de clé) plutôt que d'accepter silencieusement des rejeux.
- **RI-5b (la reconstruction doit être complète, ou traitée comme une rotation — et une
  restauration n'est pas une reconstruction).** Une implémentation qui reconstruit l'état de
  rejeu après un plantage (plutôt que de le persister en continu) DOIT (MUST) soit le
  reconstruire complètement pour la fenêtre vivante, soit traiter l'écart comme le début d'une
  nouvelle époque de clé (de nouvelles clés, de sorte que les anciennes valeurs `gamma` ne sont
  plus acceptables). Une reconstruction partielle qui laisse une partie de la fenêtre non
  protégée n'est pas conforme. De plus, une **restauration** de VM/de système de fichiers qui
  rembobine le cache vers un état *antérieur, d'apparence complète* n'est pas un plantage et la
  vérification de complétude de RI-5b ne peut pas la détecter : un relais restauré revient avec un
  cache d'*avant* les paquets qu'un adversaire a capturés, et les réadmet. Un nœud DOIT (MUST)
  traiter tout signe de restauration (le même recul d'horloge ou décroissance du compteur de
  génération que RI-3b) comme une **rotation d'époque de clé** obligatoire, de sorte que les
  valeurs `gamma` d'avant la restauration ne soient plus acceptables quel que soit le contenu du
  cache rembobiné.

## 6. API résistante au mésusage (rendre impossible la chose non sûre)

I-1 et la discipline `[soundness]` exigent que l'API rende l'opération non sûre
*non représentable*, non pas seulement documentée comme imprudente. L'ordonnancement de SP-1
(chiffrer **puis** découper) et la règle de fermeture sûre de SP-7a sont les deux endroits où
une API s'inverse le plus facilement.

- **RI-6 (l'API DOIT refuser le texte en clair sans AEAD, protège SP-1/SP-1a).** Le point
  d'entrée de dispersion DOIT (MUST) refuser toute entrée qui n'est pas déjà passée par l'AEAD de
  bout en bout (SP-1a) : il disperse **du texte chiffré uniquement**, jamais du texte en clair.
  Il NE DOIT PAS (MUST NOT) y avoir de chemin public « découper ces octets bruts » qui contourne
  l'ordonnancement chiffrer-puis-découper de SP-1 — c.-à-d. aucun moyen d'atteindre `split()`
  sans le scellement AEAD devant lui. La PoC satisfait déjà ce barème : `send()` appelle
  `e2e.seal` avant `disperse`, et `dispersal.py` est documenté comme « never touch plaintext ».
  Un véritable nœud DOIT (MUST) garder cette porte fermée au niveau des types, non par
  convention. Menace : découper directement du texte en clair détruit la *ceinture
  calculatoire* (niveau 2 de la Partie 7) — les parts reconstruisent alors directement vers du
  texte en clair pour tout adversaire `≥k`, sans AEAD derrière elles — et inverse la composition
  sur laquelle repose toute la conception.
- **RI-6a (séparer par type le texte chiffré du texte en clair).** Une implémentation DEVRAIT
  (SHOULD) représenter le « texte en clair » et le « texte chiffré de bout en bout » comme des
  types distincts et non interchangeables, de sorte que l'ordonnancement SP-1 ne puisse pas être
  inversé en passant le mauvais tampon et qu'un appel « découper des octets bruts » soit une
  erreur à la compilation plutôt qu'une vérification à l'exécution. Là où le langage ne peut pas
  imposer cela, le nœud DOIT (MUST) interposer une garde à l'exécution qui est activée par défaut
  et ne peut pas être désactivée par configuration.
- **RI-6b (les points d'entrée bruts du corps DOIVENT être privés au module).** La séparation par
  type (RI-6a) ne suffit pas à elle seule : le `split`/`reconstruct` brut et tout point d'entrée
  direct du corps DOIVENT (MUST) être privés au module (non exportés), de sorte que les *seuls*
  symboles publics de dispersion soient celui qui prend le type texte-chiffré-AEAD (RI-6) et celui
  qui retourne un résultat d'ouverture authentifiée (RI-7). Un symbole public `split(raw_bytes)`
  ou `reconstruct(...)` est lui-même le défaut, indépendamment de ce qu'un appelant lui passe —
  dans un langage où `bytes` est `bytes`, une découpe brute exportée laisse un appelant de plus
  bas niveau contourner la barrière AEAD tout en vérifiant proprement les types. La PoC les expose
  à la portée du module *parce que c'est une spécification exécutable* ; un véritable nœud NE DOIT
  PAS (MUST NOT).
- **RI-7 (la reconstruction DOIT échouer en mode fermé, à temps constant, protège SP-7a).**
  L'étiquette AEAD est l'arbitre d'intégrité **unique** (SP-7a) : la reconstruction de Shamir n'a
  aucune intégrité propre, de sorte qu'un octet de part inversé ou un `(k,n)` sur lequel on a
  menti produit un candidat cohérent-mais-faux que seul l'AEAD rejette. L'API de reconstruction
  DOIT (MUST) retourner un message **uniquement** après que l'AEAD de bout en bout a vérifié, et
  DOIT (MUST) écarter — jamais faire remonter, journaliser, ni agir sur — tout candidat dont
  l'étiquette échoue. Elle NE DOIT PAS (MUST NOT) exposer un résultat de « reconstruction non
  authentifiée » au code applicatif. **L'écartement en mode fermé DOIT (MUST) aussi être à temps
  constant par rapport à *pourquoi* il a échoué :** le chemin reconstruire-puis-ouvrir DOIT (MUST)
  prendre un temps indiscernable et n'émettre aucune réponse discernable (CH-9/I-4) que
  l'étiquette AEAD ait vérifié, que l'octet `(k,n)` ait été menti (RI-7a), ou que les octets de
  part aient été corrompus — un adversaire qui peut alimenter des candidats de reconstruction
  (le résidu de drop hostile de SP-7a, ou une coalition `≥k` rejouant des ensembles de parts) NE
  DOIT PAS (MUST NOT) apprendre lequel, par temporisation ni par réponse, sinon le chemin de rejet
  devient un distingueur de type oracle de remplissage (padding oracle) alors même que la
  *comparaison* d'étiquette (RI-8) est à temps constant. La PoC épingle le comportement de
  fermeture sûre (`receive()` écarte sur le `ValueError` d'`e2e.open_`,
  `test_tampered_share_fails_closed`) ; un véritable nœud NE DOIT PAS (MUST NOT) ajouter un chemin
  qui le contourne, ni une porte dérobée temporelle qui le traverse. Menace : faire remonter une
  reconstruction non authentifiée transforme le résidu accepté de déni de service de SP-7a en la
  livraison d'ordures choisies par l'attaquant ; temporiser le rejet le transforme en oracle.
- **RI-7a (analyser l'octet `params` de façon défensive, ne pas lui faire confiance).** L'octet
  `(k,n)` est contrôlé par l'attaquant sur une part hostile (SP-7a) et verrouillé par vecteurs
  quant à l'ordre des quartets (SP-7a / feuille de route 3.2). Une implémentation DOIT (MUST) le
  valider contre l'ordre verrouillé par vecteurs et contre `1 ≤ k ≤ n ≤ 15` (comme le fait
  `_check_params`) avant usage, et DOIT (MUST) traiter une reconstruction sous un `(k,n)` menti
  comme un écartement ordinaire en mode fermé (RI-7), jamais comme une raison d'allouer une
  mémoire non bornée ou d'indexer hors des bornes.

## 7. L'AEAD et la comparaison d'étiquette (la ceinture doit aussi être à temps constant)

La ceinture calculatoire (niveau 2, Partie 7 §5) n'est aussi sûre que son implémentation.
L'AEAD de la PoC est correct au regard de la RFC 8439 mais n'est explicitement **pas** à temps
constant (« it is correct … but leaks through timing, so a real node MUST use a vetted
constant-time library »).

- **RI-8 (AEAD à temps constant et comparaison d'étiquette, protège SP-1a / SP-7).** Un nœud DOIT
  (MUST) utiliser une implémentation de ChaCha20-Poly1305 dont le chemin de données et dont la
  **comparaison d'étiquette d'authentification** sont à temps constant, et DOIT (MUST) comparer
  l'étiquette de part SP-7 et l'étiquette AEAD SP-7a avec une primitive d'égalité à temps constant
  (pas de `memcmp` à sortie anticipée, pas de branchement dépendant des données sur les octets
  d'étiquette). Menace : une vérification d'étiquette non à temps constant est un oracle de
  falsification classique — une temporisation octet par octet sur la comparaison laisse un
  adversaire forger une étiquette valide — ce qui attaque directement la ceinture (SP-1a) et
  l'étiquette de reconnaissance de part (SP-7). L'arithmétique de Poly1305 et de X25519 DOIT
  (MUST) de même être à temps constant (RI-11) ; une implémentation à temps variable de l'une ou
  l'autre divulgue du matériel de clé par temporisation.

## 8. La couche en oignon que le jouet omet

La PoC n'a « no onion layer » : `dispersal.py` opère uniquement sur la part de la charge utile
`delta`, et l'en-tête Sphinx (`alpha`/`beta`/`gamma`) et sa cryptographie par saut n'existent que
comme la spécification de la Partie 1 §5. Un véritable nœud DOIT (MUST) implémenter cette couche,
et sa cryptographie est dans le périmètre ici parce qu'elle porte du matériel secret (les secrets
de saut et l'éphémère client) sous la même menace de canal auxiliaire que le plancher.

- **RI-10 (implémenter la dérivation par saut CH-2, protège I-1/I-4).** Un nœud DOIT (MUST)
  implémenter le handshake de circuit Sphinx de la Partie 1 §5 exactement : par saut, dériver le
  secret partagé `s_i = X25519(alpha_i, onion_i)` à partir de l'élément de groupe aveuglé et de la
  statique du relais (CH-2), et dériver la clé de flux de l'info de routage, la clé de MAC `gamma`,
  et la clé d'AEAD `delta` de `s_i` par HKDF-BLAKE2s sous les étiquettes fixes `sphinx-rho`,
  `sphinx-mu`, `sphinx-delta` (CH-2 ; octets exacts d'étiquette et chaînage verrouillés par
  vecteurs sous la feuille de route 3.2). Il DOIT (MUST) effectuer l'aveuglement Sphinx (re-
  randomiser `alpha` par saut) et imposer la discipline de rejeu de SP-5. Il n'y a **aucune
  transcription de handshake séparée** (CH-1) ; un nœud qui émet ou attend un quelconque message
  Noise/de handshake sur un circuit n'est pas conforme (CH-1). *Signalement :* les vecteurs de
  test inter-implémentations pour cette dérivation relèvent de la feuille de route 3.2 et DOIVENT
  (MUST) être confrontés une fois publiés ; jusque-là, deux implémentations ne sont pas encore
  prouvées interopérables à cette couche (I-1), et cela est énoncé ouvertement plutôt que supposé.
- **RI-11 (X25519 à temps constant et la discipline de l'éphémère sans clé, protège
  CH-3/CH-6/I-2).** La multiplication scalaire X25519 à chaque saut DOIT (MUST) être à temps
  constant (une implémentation en échelle de Montgomery sans branchement ni accès mémoire dépendant
  du secret) ; un X25519 à temps variable divulgue le scalaire de saut et donc le secret de saut.
  Le scalaire éphémère client par paquet `x` derrière `alpha_0` (CH-3) DOIT (MUST) être fraîchement
  tiré du CSPRNG (RI-2) par paquet, NE DOIT PAS (MUST NOT) être réutilisé d'un paquet à l'autre, et
  DOIT (MUST) être mis à zéro immédiatement après la construction du paquet (RI-9) — sa destruction
  est ce qui rend réelle la forward secrecy à granularité d'époque de CH-6 (un `x` conservé laisse
  une saisie ultérieure de la statique de relais recalculer le secret de saut que la conception
  promet disparu). Un relais DOIT (MUST) de même garder sa statique `onion` sous la manipulation
  de clé de RI-2 et la rotation/le retrait de RI-4, et calculer avec elle à temps constant.
- **RI-11a (rejeter le secret partagé dégénéré, de la façon correcte pour X25519).** X25519
  n'expose délibérément aucun test bon marché d'appartenance à la courbe/à l'ordre (RFC 7748), de
  sorte que « valider le point `alpha` » n'est pas la vérification constructible ; celle qui est
  exigée et constructible est : calculer `s_i = X25519(alpha_i, onion_i)` et, **à temps constant,
  rejeter si le secret partagé résultant est entièrement nul** (l'issue de petit ordre / petit
  sous-groupe) *avant* de dériver une quelconque clé de saut de lui. Cela refuse à un prédécesseur
  malveillant un saut à petit ordre forcé ou à clé connue. Parce que chaque octet sur le fil est
  uniforme (SP-4/I-4), la vérification porte sur le *secret calculé*, non sur un drapeau en clair,
  et un relais DOIT (MUST) traiter un `alpha` rejeté en un temps et des octets **indiscernables
  d'un écartement de rejeu ordinaire** (SP-5/CH-9/I-4) — aucune réponse discernable, aucun indice
  temporel. La règle complète de validation/d'encodage de point est verrouillée par vecteurs sous
  la feuille de route 3.2, mais le rejet de sortie entièrement nulle est normatif *ici* de sorte
  que l'exigence soit constructible sans attendre ce fichier (I-1).

## 9. Mise à zéro de la mémoire, échange (swap) et sûreté face aux défaillances

Un plancher qui est inconditionnel sur le fil mais récupérable depuis un vidage de tas, un
fichier d'échange ou un vidage de cœur n'est pas un plancher (§1). La divulgation mémoire révèle
les octets mêmes en dessous de `k` qu'I-2 protège, de sorte que la mise à zéro est une exigence
d'I-2, non de l'hygiène.

- **RI-9 (tenir les secrets dans un stockage à mise à zéro possible et les effacer après usage,
  protège I-2).** Les parts de Shamir, les coefficients de polynôme, le secret reconstruit,
  chaque clé dérivée (`content_key`, la clé de `tag` SP-7, la clé de `box_id`, chaque clé de saut
  Sphinx `s_i` et ses dérivées), le `kpair` pré-partagé, l'éphémère client `x` (RI-11), et la
  statique `onion` du relais (RI-4) DOIVENT (MUST) être tenus dans un stockage que le nœud peut
  écraser sur place et DOIVENT (MUST) être mis à zéro dès qu'ils ne sont plus nécessaires.
  L'obligation est énoncée comme un *choix de stockage d'abord* parce qu'une simple « mise à zéro »
  est **physiquement impossible** dans certains des langages cibles de cette spécification même :
  en CPython (le langage de la PoC de référence) un secret dans un objet `bytes` immuable peut
  être interné, copié par l'allocateur, et libéré sans aucun écrasement atteignable, et un GC à
  copie/compactage (Go, Java, …) peut relocaliser un secret de sorte qu'aucun effacement unique
  n'atteigne chaque copie. Par conséquent :
    - Dans un runtime qui fournit un stockage secret **mutable sur place et déterministe**, le nœud
      DOIT (MUST) mettre à zéro avec une primitive que le compilateur ne peut pas éliminer comme un
      stockage mort (`explicit_bzero`/`memset_s`/`SecureZeroMemory`/une barrière `volatile` ou le
      `Zeroize` audité du langage) — un `memset` ordinaire sur un tampon à libérer est
      régulièrement optimisé et supprimé.
    - Là où le langage **ne peut pas** le garantir (chaînes d'octets immuables, un GC à
      copie/compactage, une sémantique de copie de valeur), le nœud DOIT (MUST) tenir chaque secret
      dans une mémoire **épinglée/native/hors-tas** qu'il *peut* mettre à zéro (la clause de
      mémoire native de RI-9b est alors un **DOIT (MUST)**, non un DEVRAIT (SHOULD)) et NE DOIT PAS
      (MUST NOT) du tout garder le secret dans un objet géré par le runtime (un `bytes`/`str`, un
      tableau de tas GC).
  L'exigence est donc « utiliser un stockage à mise à zéro possible, puis l'effacer » —
  satisfaisable dans tout langage — plutôt que « effacer un objet que le runtime ne vous laissera
  pas atteindre ». Menace : ce sont exactement les octets secrets sous `k` que le plancher cache ;
  les laisser dans un tas libéré, un tampon réutilisé, une copie GC relocalisée, ou une structure
  journalisée laisse une lecture mémoire ultérieure les reconstruire, ce qui est une rupture d'I-2
  par divulgation mémoire.
- **RI-9a (garder les secrets hors de l'échange et des vidages de cœur).** Les tampons secrets
  DEVRAIENT (SHOULD) être verrouillés en RAM (`mlock`/`mlockall`/`VirtualLock`) de sorte qu'ils ne
  soient jamais paginés vers un fichier d'échange persistant, et le processus DEVRAIT (SHOULD)
  désactiver les vidages de cœur (`RLIMIT_CORE = 0` ou l'équivalent de la plateforme) ou en
  exclure les pages secrètes. Un nœud qui ne peut pas empêcher l'échange des pages secrètes
  DEVRAIT (SHOULD) utiliser un déploiement à échange chiffré et DOIT (MUST) documenter le résidu.
  Menace : un fichier d'échange ou un vidage de plantage est une copie durable, résidente sur
  disque, des octets sous `k` — le plancher, déversé sur un stockage où il survit longtemps au
  processus.
- **RI-9b (déjouer les dangers de l'optimiseur et du langage).** Une implémentation DOIT (MUST)
  s'assurer que le compilateur et le runtime du langage ne réintroduisent pas les fuites que ces
  règles interdisent : aucun branchement dépendant du secret ressuscité par l'optimisation
  (RI-1), aucun secret copié-et-oublié depuis un conteneur à ré-allocation, une valeur déplacée,
  un tas à ramasse-miettes ou à GC à copie, l'internement de chaînes, ou une exception/une trace
  de pile qui capture un tampon secret. Dans les langages à mémoire gérée où un tampon peut être
  copié par le runtime, un nœud DEVRAIT (SHOULD) tenir les secrets dans une mémoire
  épinglée/native qu'il peut mettre à zéro de façon déterministe, et NE DOIT PAS (MUST NOT) se
  fier au ramasse-miettes pour les effacer.
- **RI-12 (sûreté face aux défaillances et aux exceptions — aucun artefact partiel ou liable,
  protège I-2/I-4).** Un plantage, une exception ou une annulation **en cours de découpe** NE DOIT
  PAS (MUST NOT) émettre un ensemble de parts partiel, un sous-ensemble de parts sur le fil, ni
  aucun artefact qui lie les parts d'un même message, et NE DOIT PAS (MUST NOT) laisser un état
  secret non mis à zéro. Une implémentation DOIT (MUST) construire les `n` parts et s'engager à
  l'émission comme une étape tout-ou-rien relativement à la défaillance, mettant à zéro les
  coefficients et les parts sur tout chemin d'erreur avant le dépilement. Menace : un expéditeur
  qui plante après avoir émis certaines parts mais pas toutes, ou qui journalise une part
  intermédiaire dans une trace de pile, remet à un observateur un sous-ensemble corrélé (sapant la
  non-liabilité de SP-7 et, s'il révèle `≥k` d'un même message, le plancher) — et un dépilement
  non mis à zéro laisse le secret en mémoire (RI-9). La gestion des défaillances DOIT (MUST)
  échouer en mode fermé : sur toute erreur pendant la découpe, la dispersion ou la reconstruction,
  ne produire rien et effacer, plutôt que de produire quelque chose de partiel.

## 10. Comment ces exigences se rattachent aux invariants et aux menaces

| `RI` | Protège | Menace qu'elle refuse (l'attaque sur un véritable nœud) |
|---|---|---|
| RI-1 / 1a / 1b / 1c | I-2 | récupération par temporisation de cache/de branchement des octets sous `k`, y compris la manipulation du secret récupéré au-delà des opérations de corps |
| RI-2 / 2a / 2b / 2c | I-2 (SA-3) | RNG faible/forké/clonable → coefficients corrélés |
| RI-3 / 3a / 3b | SP-7b, SP-1a | retour en arrière du nonce au redémarrage **ou à la restauration d'instantané/de sauvegarde** → collision d'étiquette + masque jetable deux fois |
| RI-4 | CH-5 / CH-6 | retour en arrière de l'époque statique ou statique retirée conservée |
| RI-5 / 5a / 5b | SP-5, SP-7b | un état de rejeu oublié (ou rembobiné par restauration) rouvre la fenêtre de rejeu ; les deux caches ont des fenêtres de rétention différentes |
| RI-6 / 6a / 6b | SP-1 / SP-1a | découper-avant-chiffrer détruit la ceinture calculatoire ; un symbole public de découpe brute contourne la barrière |
| RI-7 / 7a | SP-7a | une reconstruction non authentifiée **ou discernable par temporisation** livre des ordures / devient un oracle |
| RI-8 | SP-1a, SP-7 | vérification d'étiquette non à temps constant → oracle de falsification |
| RI-10 | I-1, I-4 | la couche en oignon non implémentée, construite de façon interopérable |
| RI-11 / 11a | CH-3 / CH-6, I-2 | X25519 à temps variable ou un éphémère réutilisé/conservé |
| RI-9 / 9a / 9b | I-2 | divulgation par tas/échange/vidage de cœur des octets sous `k` |
| RI-12 | I-2, I-4 | artefact partiel/liable ou dépilement de plantage non mis à zéro |

Le fil conducteur : tout ce qui touche à une valeur secrète sous `k` (part, coefficient, octet
reconstruit, clé de contenu, secret de saut, éphémère client) est tenu au propre standard du
plancher — le calculer à temps constant (RI-1/8/11), le générer depuis un CSPRNG sain et sûr face
au fork (RI-2), ne persister aucun secret réutilisable à travers un redémarrage (RI-3/4/5), ne
jamais laisser l'API sauter l'AEAD (RI-6/7), et l'effacer avant qu'il puisse être relu (RI-9/12).
Un réviseur casse cette partie en trouvant un chemin sur un véritable nœud où une telle valeur
est calculée en temps variable, tirée d'un flux réutilisé, répétée à travers un redémarrage, fait
remonter non authentifiée, ou laissée lisible en mémoire — et ce chemin est alors une rupture
d'I-2, non un simple manque de durcissement.

## 11. Ce que cette partie **ne décide pas**

- **Réseau, transport et mise en forme du trafic.** Le transport caméléon (Partie 4), la
  stratégie de lot/mixage et la gigue (SP-6/OP-5), et la temporisation d'émission des parts
  (SP-9/OP-4) sont hors périmètre ici ; cette partie contraint l'implémentation *cryptographique*,
  non l'ordonnanceur. Le résidu de corrélation temporelle entre parts reste OP-4, non traité par
  aucun RI-n (SA-2 et cette partie portent sur les valeurs, non sur les temps d'émission).
- **Sélection de chemin et disjonction.** Vérifier que les `n` chemins de part ne partagent pas un
  AS ou une juridiction (OP-1, Partie 3) n'est pas une question d'implémentation-d'une-primitive
  et n'est pas exigé ici ; RI-7a ne garde que contre le fait de *faire confiance* à un `(k,n)`
  menti, non contre un ensemble de chemins non disjoints.
- **Sybil/eclipse et la couche de gossip.** La cryptographie correcte d'un nœud conforme ne
  résiste pas à elle seule à un adversaire bien doté achetant une position (OP-2, GR-20a) ; ce
  résidu réside dans la Partie 2 et n'est pas touché par cette partie.
- **Le dimensionnement exact de la structure de rejeu et le mécanisme de détection de fork.** RI-5a
  borne le cache de rejeu à l'époque et interdit un filtre sujet aux faux négatifs, mais la
  structure de données concrète, ses paramètres et le médium de persistance sont des choix
  d'implémentation à épingler contre les vecteurs de la feuille de route 3.2 et le volume de
  paquets du déploiement, non fixés ici.
- **Vecteurs de test et conformité.** Les vecteurs qui certifient que deux implémentations
  interopèrent — les tables GF comme normatives, la dérivation par saut Sphinx, le chemin
  chiffrer→découper→déposer→sonder→reconstruire→déchiffrer — relèvent de la **feuille de route
  3.2** et sont référencés (RI-1b, RI-7a, RI-10, RI-11a) mais non reproduits ici. RI-1b est
  explicite sur le fait que ces vecteurs certifient la correction, jamais la temporisation ; une
  suite de tests de canal auxiliaire est une obligation séparée et recommandée (RI-1b) que cette
  partie demande mais ne spécifie pas.
- **Remplacement de primitive post-quantique.** La suite `0x02` (une KEM de saut PQ, fin de la
  Partie 1 §5) change quelle primitive RI-11 contraint, non l'exigence qu'elle soit à temps
  constant ; le plancher I-2 est PQ-sûr quoi qu'il en soit (SP-1a), de sorte que rien ici n'en
  dépend.

## 12. Exigences introduites ici

- **RI-1 / RI-1a / RI-1b / RI-1c** — multiplication, inverse et division GF(2⁸) à temps constant,
  **étendus à toute la durée de vie du secret récupéré** (l'analyse de longueur SP-8 et toute
  manipulation d'un octet reconstruit), non seulement les opérations de corps ; les vecteurs
  certifient la correction, non la temporisation. **[protects I-2]**
- **RI-2 / RI-2a / RI-2b / RI-2c** — discipline du CSPRNG : DRBG cryptographique issu de l'OS,
  sûreté face au fork/clone, vérifications de santé, pas de coefficients injectables (barré en
  test, non livré). **[protects I-2 via SA-3]**
- **RI-3 / RI-3a / RI-3b** — ligne de crue `msg_nonce` persistée et sans retour en arrière, fsync
  avant usage, **et un instantané/une restauration est traité comme un retour en arrière**
  (détecter ou retirer le `kpair`). **[protects SP-7b / SP-1a]**
- **RI-4** — état d'époque statique `onion` persisté et retrait avec mise à zéro. **[protects
  CH-5 / CH-6]**
- **RI-5 / RI-5a / RI-5b** — état de rejeu persisté pour `gamma` (borné par l'époque de clé) et
  `(box_id, slot)` (borné par l'**expiration de slot de 7 days**, non par la rotation de boîte
  d'1 jour) ; une restauration qui rembobine un cache est une rotation d'époque de clé
  obligatoire. **[protects SP-5 / SP-7b]**
- **RI-6 / RI-6a / RI-6b** — l'API refuse le texte en clair sans AEAD ; séparation par type du
  texte chiffré ; `split`/`reconstruct` bruts privés au module. **[protects SP-1 / SP-1a]**
- **RI-7 / RI-7a** — reconstruction à fermeture sûre **et à rejet à temps constant** ; analyse
  défensive de `(k,n)`. **[protects SP-7a]**
- **RI-8** — AEAD à temps constant et comparaison d'étiquette à temps constant. **[protects
  SP-1a / SP-7]**
- **RI-9 / RI-9a / RI-9b** — stockage à mise à zéro possible d'abord (épinglé/natif là où le
  runtime interdit l'effacement sur place), puis mise à zéro anti-stockage-mort ; pas d'échange,
  pas de vidages de cœur ; dangers de l'optimiseur/du GC. **[protects I-2]**
- **RI-10** — implémenter la dérivation par saut Sphinx CH-2 et la discipline de
  rejeu/d'aveuglement ; les vecteurs relèvent de la feuille de route 3.2. **[protects I-1 / I-4]**
- **RI-11 / RI-11a** — X25519 à temps constant ; éphémère sans clé, par paquet, mis à zéro ;
  rejeter le secret partagé entièrement nul à temps constant. **[protects CH-3 / CH-6 / I-2]**
- **RI-12** — sûreté face aux défaillances/exceptions : aucun artefact partiel ou liable, mise à
  zéro au dépilement, fermeture sûre. **[protects I-2 / I-4]**

Aucune de celles-ci n'est un théorème ; chacune est une condition sous laquelle les théorèmes de
la Partie 7 et les garanties des Parties 1 à 6 décrivent un **véritable nœud** plutôt que le
jouet. Le jouet omet chacune d'elles à dessein et le dit. Cassez cette partie en nommant un
chemin de code sur un véritable nœud qui calcule, stocke ou divulgue un secret sous `k` d'une
façon qu'aucun RI-n ci-dessus n'interdit — ce chemin est un plancher cassé en pratique, et le
trouver est l'invitation.
