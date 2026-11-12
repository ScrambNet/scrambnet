# Spécification ScrambNet — Partie 5 : Blackout et diversité de liens en maillage mixte

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/05-blackout-mesh.md)).

**Statut : BROUILLON (DRAFT), et un risque de recherche déclaré.** C'est la plus grande
conception non écrite du projet, et cette partie renvoie — comme la feuille de route le permet — un
résultat *partiel* : un modèle de réseau mixte solide et une idée réellement porteuse
(la dispersion sur passerelles indépendantes, en tant que propriété de *disponibilité*), enveloppée
autour de résidus qu'elle nomme à pleine force et qu'elle ne prétend pas refermer. Elle
n'engage **aucune pile de maillage concrète** et ne fait **aucune affirmation d'anonymat pour la couche
radio** ; c'est une partie de posture et de modèle, exactement comme la Partie 4. Les valeurs d'homme de paille
sont marquées `(s)`.

Lisez d'abord le §3 (l'évaluation du réalisme) — c'est l'épine dorsale, et il dit la chose bien
plus grande que cette partie refuse d'affirmer. La seule affirmation positive porteuse est
étroite : *la dispersion sur des passerelles indépendantes étend I-3 à la sortie du voisinage physique
en tant que propriété de disponibilité, et rien dans le maillage n'est
autorisé à déplacer le plancher du contenu I-2* (BL-16) — le maillage est aussi indépendant du
plancher que la Partie 4 garde le transport (CT-16). Cette partie est l'échelon L4 auquel
le CT-18a de la Partie 4 passe le relais, et elle reste cohérente avec cette concession
(BL-17) : lorsqu'il n'y a pas de voisin, rien n'est livré.

## 1. Le modèle de réseau mixte et les rôles

- **BL-1 (le maillage est une couche, non un mode). [normatif]** Un nœud conforme DOIT (MUST)
  traiter les liens radio locaux et les liens internet comme des types de liens coexistant *à tout
  moment*, non comme un « mode blackout » entré lors de la perte d'infrastructure. Perdre la
  liaison montante DOIT (MUST) être un changement de *route* (un saut de plus vers une passerelle), jamais un changement
  de protocole, d'identité ou de posture de sécurité. Une conception avec un « mode maillage »
  distinct que l'utilisateur bascule est non conforme à ce cadrage (OP-6).
- **BL-2 (les rôles, par la réalité matérielle). [normatif]** Un nœud DOIT (MUST) se classer lui-même,
  d'après sa capacité radio réelle, comme exactement l'un des suivants : **feuille** (un téléphone : concurrence STA+AP
  ou Wi-Fi Aware, lié à la batterie, sans root), **dorsale** (un PC/SBC bi-radio
  exécutant un vrai 802.11s, store-and-forward continu), ou **passerelle** (une
  dorsale ou une feuille tenant actuellement une liaison montante et l'annonçant). Les rôles sont
  dérivés de la capacité et variables dans le temps — une passerelle qui perd sa liaison montante devient
  dorsale ou feuille — jamais un palier fixe.
- **BL-3 (l'opt-in est une précondition de tout lien radio). [normatif]** Un nœud NE DOIT
  PAS (MUST NOT) originer, relayer ou passer en passerelle un quelconque trafic sur un lien radio local sans un
  opt-in préalable, explicite et éclairé *propre à la participation au maillage* et distinct
  de tout opt-in de relais, parce que la visibilité du maillage est physique (BL-18) et porte une
  identité de couche radio que l'overlay ne peut faire tourner (BL-18a). Le silence, ou hériter de
  l'opt-in de relais, est non conforme.
- **BL-4 (budget honnête de batterie et de stockage). [normatif]** Un nœud feuille DOIT (MUST)
  exposer, avant l'opt-in, le coût de batterie et de stockage qu'il encourra réellement
  (homme de paille : un quota de store-and-forward borné et un calendrier radio à cycle de service),
  et NE DOIT PAS (MUST NOT) promettre une disponibilité continue de qualité dorsale qu'il ne peut soutenir sur
  batterie. Le budget concret est OP-6 ouvert et DOIT (MUST) être déclaré, non deviné
  (BL-20).

## 2. Dispersion sur passerelles indépendantes, adressage, acheminement et mixage

### 2.1 Dispersion sur passerelles indépendantes (l'idée porteuse, en tant que disponibilité)

- **BL-5 (les parts DEVRAIENT sortir par des passerelles indépendantes). [normatif]** Lorsque les
  `n` parts d'un message (SP-2) traversent le maillage local jusqu'à une liaison montante, un client conforme
  DEVRAIT (SHOULD) les router de sorte qu'elles sortent par des passerelles *différentes*, étendant
  I-3 (aucun point unique) à la sortie du voisinage physique. Une passerelle portant
  `k` des `n` parts est un point unique et DOIT (MUST) être évitée là où ≥2
  passerelles *estimées* indépendantes (BL-6) sont accessibles. Dans un blackout profond
  l'estimation d'indépendance peut être vide (BL-6) ; BL-5 se dégrade alors vers BL-7 **par
  défaut**, non comme un cas limite. Le bénéfice revendiqué ici est la **disponibilité**, non
  l'inobservabilité (§3) : aucune défaillance, obstruction ou capture sybil d'une seule passerelle
  ne tue la livraison — c'est le verdict CT-15 pour les transports, dans l'espace du maillage.
- **BL-6 (ce que « indépendant » peut signifier à la couche radio — énoncé, non résolu).
  [normatif, déclare-résidu]** Un client conforme NE DOIT PAS (MUST NOT) traiter les passerelles comme
  indépendantes sur *auto-déclaration* (GR-3, dans l'espace radio). « Indépendant » ne peut être
  estimé qu'à partir de signaux *observables, non auto-déclarés* — des AS de liaison montante distincts *là
  où une carte des AS (Partie 8) est accessible*, des sauts radio suivants distincts, une
  direction physique distincte — dont chacun est faible, falsifiable ou **indisponible à l'intérieur
  d'un blackout** (la carte des AS, le signal le plus fort, est souvent la première chose disparue).
  La signification honnête de « passerelle indépendante » est donc une **estimation à confiance
  bornée**, non un fait vérifié (§4b) ; un client DOIT (MUST) la présenter comme telle et NE DOIT
  PAS (MUST NOT) revendiquer une indépendance de passerelle vérifiée. Voir BL-21 — c'est le problème récurrent
  d'indépendance dans l'espace radio.
- **BL-7 (trop peu — ou zéro — passerelles indépendantes se dégrade, n'échoue jamais ouvert).
  [normatif]** Là où moins de deux passerelles estimées indépendantes sont accessibles,
  un client NE DOIT PAS (MUST NOT) pousser silencieusement `k` parts à travers une seule comme si la dispersion tenait ; il
  DOIT (MUST) retenir les parts pour une sortie indépendante ultérieure (borné par le TTL BL-12), les répartir
  dans le temps, ou exposer que la sortie physique est un point unique pour ce message (BL-19). Le
  plancher (I-2) est inaffecté dans les deux cas (BL-16).

### 2.2 Adressage sans accessibilité globale

- **BL-8 (les noms survivent ; les routes globales non). [normatif]** L'`id` Ed25519
  du relais/destinataire (Partie 2) et le `box_id`/rendez-vous de la Partie 6 DOIVENT (MUST) rester les
  noms stables à l'intérieur d'un blackout ; ce qui casse est l'*accessibilité* globale, non le nommage.
  Un nœud NE DOIT PAS (MUST NOT) dépendre d'un DHT accessible ni d'aucune route globale pour la sélection du
  saut suivant sur le maillage.
- **BL-9 (saut suivant sans DHT — le menu et ses coûts).** En l'absence d'une route
  globale, un saut suivant de maillage est choisi par une méthode locale à coût borné : inondation
  épidémique vers n'importe quelle liaison montante (bon marché, aucune connaissance de la destination, coût radio élevé) ; un
  *gradient* d'accessibilité où les voisins annoncent l'accessibilité *vers une
  passerelle* — jamais vers le destinataire nommé, ce qui serait un sélecteur
  (I-4/SP-7) ; ou le portage physique (store-and-forward jusqu'à ce qu'une passerelle entre à portée).
  Cette clause nomme le menu ; le choix est un homme de paille (BL-20), et chaque option
  DOIT (MUST) préserver SP-7 (aucune liaison inter-chemins sur les octets) et I-4 (BL-15).
- **BL-10 (la livraison passe toujours par les dépôts de la Partie 6, jamais vers un appareil nommé).
  [normatif]** Le travail du maillage se termine à la *liaison montante* : une fois que les parts atteignent
  internet, elles ré-entrent dans l'overlay et sont livrées à des dead drops dispersés
  (Partie 6) exactement comme avant. Le maillage NE DOIT PAS (MUST NOT) tenter de livrer à un *appareil*
  destinataire nommé directement — cela ferait de la livraison une cible sur une personne,
  violant le contrat de la Partie 6 (RZ-1). Le cas véritablement-tout-local (expéditeur, dépôt
  et destinataire tous dans le maillage, sans liaison montante) est servi par le fait que le **dépôt** du destinataire soit lui aussi
  accessible par le maillage — le dépôt et le relevé passent tous deux par le maillage *vers un dépôt*, jamais
  vers l'appareil destinataire — ce qui est l'élément ouvert que la Partie 6 §9 liste comme « relevé sur
  le maillage pendant un blackout (OP-6). » Le routage vers un appareil destinataire nommé reste
  interdit en tant que sélecteur.

### 2.3 Store-and-forward et le verdict de cadrage

- **BL-11 (la validité Sphinx, non les octets, est la contrainte du portage long).
  [normatif, déclare-résidu]** Le paquet Sphinx de 2048 octets (SP-3) est
  autosuffisant en *octets* mais non en *validité* : sa sécurité de saut se lie à l'époque
  `onion` ≤7 jours d'un relais (CH-5) et au cache de rejeu par époque (SP-5,
  SP-7b). Un paquet porté des heures à des jours à travers des liens intermittents PEUT (MAY) survivre à
  l'époque que son premier saut a supposée, ou arriver après que l'état de rejeu a tourné ou été
  perdu à travers des redémarrages. Une conception conforme DOIT (MUST) énoncer cela et NE DOIT PAS (MUST NOT) supposer qu'un
  paquet Sphinx est indéfiniment portable inchangé.
- **BL-12 (le verdict : le blackout a besoin de sa propre enveloppe de store-and-forward).
  [normatif]** À cause de BL-11, et parce que le store-and-forward a besoin de champs que le
  paquet fixe de 2048 octets n'a pas la place de contenir (un temps-de-vie borné, la fragmentation et
  le réassemblage pour les liens intermittents, la signalisation de garde par saut), le verdict de
  ce brouillon est que l'**acheminement en blackout a besoin de son propre cadrage externe** — un
  bundle de style DTN (prior art : RFC 4838/5050) qui *enveloppe* le paquet Sphinx interne inchangé,
  est lui-même bourré à longueur fixe, et dont les métadonnées sont protégées par AEAD, jamais en
  clair. Le paquet interne est intact ; l'enveloppe est nouvelle et vit seulement sur les
  liens de blackout. C'est un verdict d'homme de paille (BL-20), renversé seulement par un argument
  qui referme BL-11, que ce brouillon n'a pas.
- **BL-13 (l'enveloppe ne doit pas devenir un sélecteur — et hérite du résidu d'imbrication de CT-6a).
  [normatif, déclare-résidu]** Le TTL, l'index de fragment et les champs
  de garde de l'enveloppe sont exactement les métadonnées en clair qu'I-4 interdit ; ils DOIVENT (MUST) vivre
  à l'intérieur d'une trame protégée par AEAD, de taille fixe et d'apparence uniforme (discipline SP-4), et
  NE DOIVENT PAS (MUST NOT) laisser un observateur radio lier deux fragments d'un message, ou deux parts
  d'un message, mieux que SP-7 ne le permet déjà sur l'overlay. **Résidu
  honnête, hérité de la Partie 4 :** envelopper un paquet interne I-4-uniforme à l'intérieur d'un
  bundle externe recrée la **surface de structure imbriquée CT-6a** dans l'espace radio — une
  trame externe de taille fixe dont la taille/temporisation/fragmentation peut trahir qu'elle porte une
  *seconde* unité fixe, et l'uniformité par couche ne rend **pas** l'imbrication
  indétectable à un observateur RF. C'est un résidu déclaré, non refermé par le
  cadrage. Il n'est survivable qu'au sens où tout l'est ici : l'adversaire RF de blackout
  est *local*, de sorte que la détection d'imbrication coûte l'*observabilité-de-participation*
  — qui, BL-18 le concède déjà, est perdue — et ne touche **pas** le plancher du contenu I-2.

### 2.4 Mixage de couche radio vs la passerelle sybil

- **BL-14 (la passerelle sybil est une éclipse physique ; la réponse est partielle).
  [normatif, déclare-résidu]** Un nœud annonçant « j'ai une liaison montante » attire le
  trafic du voisinage, et une passerelle sybil (ou coalition) est une *éclipse physique*
  — l'instance de couche radio du résidu d'éclipse de la Partie 2 (OP-2). La
  réponse partielle est (i) le mixage de source de couche radio (BL-15) de sorte qu'une passerelle ne puisse
  trivialement attribuer une part à son voisin d'origine *à la couche trame*, composé
  avec (ii) la dispersion sur passerelles indépendantes (BL-5) de sorte qu'aucune passerelle unique ne voie
  `k`. Une description conforme DOIT (MUST) déclarer cette réponse **partielle** : elle élève le
  coût du sybil, elle ne supprime pas l'éclipse, et elle se réduit à OP-1/OP-2
  récurrents à la couche radio (BL-6, BL-21).
- **BL-15 (le mixage de source de couche radio est une mesure de disponibilité/anti-éclipse, non
  de dissimulation d'origine). [normatif]** Le trafic sur un lien radio local DOIT (MUST) satisfaire I-4 à un
  observateur radio sur les octets (trames uniformes de taille fixe, BL-13) et DEVRAIT (SHOULD) appliquer un
  mixage de source de sorte que l'expéditeur immédiat au niveau trame d'une part ne soit pas, par la trame,
  marqué comme son originateur. Ce n'est **pas** la défense d'échantillonnage d'annuaire GR-8
  (GR-8 mixe l'*échantillon stocké* d'un client à travers des classes de source contre l'éclipse de carte
  — un mécanisme différent contre un adversaire différent) et il NE DOIT PAS (MUST NOT) emprunter son
  nom ni ses assurances. Et il NE DOIT PAS (MUST NOT) être présenté comme cachant l'originateur
  *physique* : un adversaire local avec de la radiogoniométrie connaît l'émetteur physique
  d'une transmission indépendamment du contenu de la trame (BL-18), de sorte que le mixage de source radio
  achète un *coût anti-éclipse contre une passerelle sybil*, jamais l'anonymat d'origine — la
  même discipline liaison-vs-disponibilité que CT-15a impose pour les transports.

## 3. L'évaluation honnête du réalisme (l'épine dorsale)

*(Écrite dans la §voix de résidu des Parties 4, 8 et 11. C'est la partie, non une
annexe.)*

**Ce qui est véritablement concevable, et réel.** Trois choses. D'abord, le *modèle de réseau
mixte* (BL-1) : traiter la radio et l'internet comme des types de liens coexistants de sorte que perdre
une liaison montante soit un saut de plus, non un monde différent, est propre, constructible, et
étayé par le prior art (Briar, Reticulum, Yggdrasil/cjdns, Freifunk démontrent des morceaux).
Deuxièmement — l'idée qui gagne au paradigme sa subsistance — la *dispersion sur passerelles indépendantes*
(BL-5) : la faiblesse fatale classique de tout maillage à passerelle est que la passerelle voit
tout, et ScrambNet y répond avec le mécanisme qui définit tout le
réseau, répartissant les `n` parts à travers les passerelles de sorte qu'aucune sortie physique unique ne voie
`k`. Troisièmement, le *garde d'invariant* (BL-16) : garder le plancher I-2 entièrement indépendant
du fait que le maillage se forme n'est pas seulement concevable, c'est forcé, et c'est la même
discipline que la Partie 4 applique aux transports. Ces trois sont solides.

**Mais la bonne idée est une idée de *disponibilité*, et ne doit être vendue rien de plus.**
La dispersion sur passerelles indépendantes fait peu pour le *qui* ou le *où* dans le modèle de menace
blackout-brûlant, parce que deux résidus et une fuite d'identité la minent comme mécanisme
d'anonymat : vous ne pouvez pas vérifier l'indépendance de passerelle dans un blackout (BL-6), l'émetteur
est localisable physiquement (BL-18), et la couche radio porte une identité que l'overlay
ne peut faire tourner (BL-18a). Ce que la dispersion *livre*, et livre véritablement, c'est
la disponibilité : aucune défaillance, obstruction ou capture sybil d'une seule passerelle ne tue la livraison,
et cela tient même quand toute propriété d'anonymat s'est effondrée. C'est exactement le
verdict CT-15 pour les transports à couvertures multiples — disponibilité oui, camouflage non — et la
partie l'épingle là (BL-16). Vendue comme anonymat ce serait une surenchère ; vendue comme
disponibilité c'est une propriété réelle et non vide.

**Ce qui n'est que partiel.** Le problème de la passerelle sybil / éclipse physique (BL-14).
Le mixage de source de couche radio plus la dispersion sur passerelles indépendantes élève le coût d'une
éclipse sybil ; il ne la supprime pas. Une coalition de passerelles contrôlant `k` des
sorties accessibles dans un petit maillage de voisinage éclipse un expéditeur exactement comme une coalition
de relais le fait sur l'overlay — OP-1 et OP-2 récurrents dans l'espace radio, non une nouvelle
défense. « Partiel » est le mot correct.

**Ce qui n'est pas résolu — déclaré à pleine force, trois résidus.**

*D'abord, la vérification d'indépendance de passerelle (BL-6, BL-21).* Vous ne pouvez pas vérifier à partir
de quoi que ce soit qu'une passerelle auto-déclare que deux passerelles sont indépendantes, et à l'intérieur d'un
blackout c'est pire que sur l'overlay : la carte des AS (Partie 8) qui permettrait à un client
d'*inférer* l'indépendance à partir de données non auto-déclarées est elle-même souvent inaccessible — le seul
outil disparu exactement quand il est nécessaire, de sorte que l'estimation peut être quasi-vide dans un blackout
profond (BL-5 se dégrade vers BL-7 par défaut). Ce n'est pas un orphelin de la Partie 5 : le modèle de menace
le nomme comme une face du problème récurrent le plus profond du projet — vérifier
l'indépendance d'une partie sans faire confiance à son auto-déclaration — partagé avec les relais
(OP-1), les signataires de publication (OP-8), et les auteurs de dépendances (OP-2/RB). La réponse honnête est
la même que là-bas : un *résidu borné, déclaré* alimentant une *estimation* de confiance avec une
erreur attachée (style ID-12), non une vérification cryptographique. La Partie 5 n'a pas le droit d'être
là où ceci est enfin résolu.

*Deuxièmement, et irréductiblement, la localisabilité physique (BL-18).* Un nœud de maillage dans un blackout
brûlant est un émetteur radio dans un lieu physique, et **aucun overlay ne cache un émetteur
radio à un adversaire muni d'un radiogoniomètre.** C'est catégoriquement plus difficile que
quoi que ce soit d'autre dans la spécification, parce que toute autre menace dans ScrambNet est un
adversaire *distant* raisonnant sur des octets, et c'est un adversaire *local* avec une
antenne — présent précisément parce qu'il a imposé le blackout. Tout l'édifice cryptographique
opère sur *ce que les octets révèlent* ; la localisabilité ne concerne pas les octets du
tout, c'est le fait électromagnétique de la transmission. La partie ne doit pas promettre que le
maillage préserve l'anonymat, et elle ne le fait pas.

*Troisièmement — la fuite que l'overlay travaille le plus dur à prévenir et que la radio défait (BL-18a).*
La localisabilité est *où vous êtes* ; l'identité est *qui vous êtes*, et la couche radio fuit
les deux. Une radio Wi-Fi/802.11s émet des identifiants de couche 2 persistants que l'overlay ScrambNet
ne touche jamais — une adresse MAC (et l'appairage 802.11s peut exiger une stable), des IDs de service et
d'appareil Wi-Fi Direct/Aware, des empreintes de probe-request, et, contre un adversaire capable, une
*empreinte RF matérielle* (imperfections d'oscillateur) qui survit entièrement à la
randomisation MAC. Ainsi toute l'histoire de l'overlay — `id` tournant, `box_id` par époque,
cartes par relation (RZ-2), inliabilité de parts SP-7 — repose *au-dessus* d'un pseudonyme de couche 2
qu'un renifleur local lit directement, et la rotation d'overlay ne peut le faire tourner. Et la *topologie*
du maillage elle-même est une carte RF observable : qui relaie à qui est visible sur
les ondes même sous trames uniformes. C'est le seul résidu que le premier brouillon de cette partie a omis ;
il est nommé ici à pleine force parce qu'il est sans doute pire que la localisabilité — vous
n'êtes pas seulement repérable pendant la transmission, vous portez un pseudonyme radio stable chaque fois
que vous rejoignez.

**Le maillage peut-il préserver les invariants dont il hérite ? Partiellement, et voici l'honnête
registre.** **I-2 (plancher du contenu) :** préservé proprement — le plancher n'a jamais chevauché le maillage
pas plus qu'il n'a chevauché le transport (BL-16) ; c'est l'énoncé le plus fort et le plus vrai
que fait la partie. **I-4 (uniformité du fil) et SP-7 (inliabilité de parts) :**
préservés **à la couche octet seulement** — une trame uniforme est toujours une émission détectable
(BL-18), et deux parts d'un message émises depuis le *même appareil physique dans la même
fenêtre* sont corrélées par radiogoniométrie et temporisation (la radio relie à nouveau ce que
l'overlay délie) ; la partie NE DOIT PAS (MUST NOT) prétendre que l'inliabilité-octet héritée survit à
la couche RF. **I-3 (aucun point unique) :** *étendu*, comme propriété de disponibilité au mieux,
à travers la dispersion sur passerelles indépendantes (BL-5) — mais seulement dans la mesure où l'estimation de
BL-6 est digne de confiance, ce qui est le résidu non résolu. Donc : I-2 préservé, I-4/SP-7
préservés-sur-les-octets-seulement, I-3 étendu-mais-estimé. Voilà le registre, et il est
anti-triomphal à dessein.

**Cohérence avec CT-18a.** La Partie 4 a concédé qu'à une coupure totale sans voisin de maillage,
la livraison est nulle et le plancher est intact-et-inutile. La Partie 5 est l'échelon
*en dessous* de cette concession — ce que vous faites *quand il y a* un voisin — et elle ne la
rétracte pas. Elle étend l'accessibilité d'une couche plus bas ; elle ne rend pas la livraison
garantie (BL-17). L'affirmation honnête n'est pas « la communication passe toujours sur le
maillage » — c'est : *quand un voisin de maillage et une passerelle existent, un message peut traverser la ville
à la vitesse d'un bus ; quand aucun n'existe, le secret reste à la maison, non livré et
non exposé ; et dans les deux cas, transmettre sur le maillage est un acte physiquement localisable,
radio-identifiable que l'overlay ne peut cacher.*

C'est un élément XL / risque-de-recherche, et il renvoie, comme la feuille de route le permet, un résultat
*partiel* : un modèle de réseau mixte solide et une véritable idée de disponibilité, autour de résidus
(indépendance de passerelle, localisabilité physique, identité radio) nommés à pleine force
et non prétendus refermés.

## 4. Les deux verdicts raisonnés

**(a) Le paquet Sphinx de 2048 octets survit-il à un store-and-forward de plusieurs heures, ou le
blackout a-t-il besoin de son propre cadrage ? → Il a besoin de son propre cadrage (BL-11, BL-12).** Le paquet
est bon en *octets* mais échoue en *validité et fonction* sur trois comptes indépendants :
(1) sa sécurité de saut se lie à une époque `onion` ≤7 jours (CH-5), qu'un portage de plusieurs jours
peut survivre, arrivant à une clé tournée et remise à zéro ; (2) SP-5/SP-7b exigent un état de
rejeu par époque survivant aux redémarrages, et les nœuds radio intermittents perdent le courant et les caches
exactement à travers l'horizon de plusieurs heures ; (3) la disposition fixe de 2048 octets (SP-3) n'a aucun
champ de rechange pour le TTL, la fragmentation et la signalisation de garde dont les liens intermittents ont besoin,
et ne peut en faire croître un en clair (I-4). La résolution propre est un bundle externe
de style DTN enveloppant le paquet interne inchangé (BL-12/BL-13), avec le résidu d'imbrication CT-6a
déclaré. C'est un verdict d'homme de paille, renversé seulement en refermant BL-11.

**(b) L'indépendance de passerelle peut-elle être vérifiée à la couche radio ? → Non ; c'est un résidu
déclaré alimentant une estimation à confiance bornée (BL-6, BL-21).** « Indépendant » devrait être
établi sans faire confiance à ce que dit la passerelle (GR-3, dans l'espace radio), et chaque
signal disponible est faible ou disparu : des AS de liaison montante distincts ont besoin de la carte de la Partie 8,
*inaccessible à l'intérieur du blackout même où l'indépendance importe le plus* ; une direction physique
distincte est falsifiable et grossière ; un saut radio suivant distinct prouve la topologie, non l'indépendance
de sortie. Il n'y a aucune vérification cryptographique que deux passerelles ont des liaisons montantes indépendantes — le même
mur qu'OP-1 heurte pour la disjonction de relais et qu'OP-8 heurte pour la juridiction du signataire. Donc l'honnête
architecture est identique à celle de la carte des AS (ID-12) : ne pas revendiquer de vérification, produire
une estimation à confiance bornée à partir d'observables non auto-déclarés (qui peuvent être quasi-vides dans un
blackout profond), attacher l'incertitude, l'exposer (BL-19), et laisser la dispersion (BL-5)
et la répartition dans le temps (BL-7) borner — non supprimer — le préjudice quand l'estimation est fausse.

## 5. Les gardes d'invariant et d'honnêteté

- **BL-16 (le plancher est indépendant de la réussite du maillage — l'analogue de CT-16).
  [normatif]** Aucune garantie de confidentialité ou de dispersion (I-2) NE DOIT (MUST) dépendre de la
  formation du maillage, de l'accessibilité d'une passerelle, du fait que les passerelles soient véritablement indépendantes
  (BL-6), ni de la livraison de l'enveloppe de blackout. Le maillage achète l'**accessibilité
  uniquement** — le même mot que la Partie 4 utilise pour les transports. Une conception dans laquelle perdre le maillage
  perd le plancher est non conforme.
- **BL-17 (cohérence avec CT-18a : le fond est toujours un fond, trois états).
  [normatif]** La Partie 5 étend l'accessibilité d'un échelon en dessous de CT-18a et NE DOIT PAS (MUST NOT) être formulée
  de manière à le contredire. Les trois états, tous explicites : (1) **aucun voisin à portée** →
  CT-18a, livraison nulle, plancher intact-et-inutile ; (2) **voisin(s) à portée mais aucune
  passerelle accessible nulle part dans le maillage** → *aussi* livraison nulle, atteinte via le maillage
  plutôt que directement — le store-and-forward PEUT (MAY) retenir des parts contre une passerelle *future*
  dans le TTL BL-12, mais cela NE DOIT PAS (MUST NOT) être présenté comme une livraison ; (3) **≥1 passerelle
  accessible** → dispersion BL-5/BL-7 ou dégradation. L'état (2) s'effondre vers le même résultat
  que (1) ; seul le chemin diffère. La Partie 5 rend la livraison *possible* d'une couche plus bas,
  jamais *probable* et jamais *garantie*.
- **BL-18 (résidu de localisabilité physique — énoncé à pleine force, jamais résolu).
  [normatif, déclare-résidu]** Un nœud de maillage transmettant dans un blackout brûlant est un
  **acte physiquement localisable** : un émetteur radio dans un lieu, au moment exact où l'adversaire
  local qui a imposé le blackout est le plus agressif et le plus disposé à utiliser la
  radiogoniométrie et des tactiques de style IMSI-catcher. **Aucun overlay, mixage, dispersion ni
  cadrage dans cette spécification ne cache cela, et cette partie NE DOIT PAS (MUST NOT) prétendre ou impliquer qu'il
  le fait.** C'est la raison pour laquelle la participation au maillage DOIT (MUST) être un opt-in explicite, éclairé,
  par contexte (BL-3), et la raison pour laquelle l'affirmation honnête de cette partie est étroite (§3).
- **BL-18a (résidu d'identité de couche radio — déclaré, non résolu). [normatif,
  déclare-résidu]** La participation au maillage expose des identifiants de couche 2 persistants que l'overlay
  ne peut faire tourner : une adresse MAC (l'appairage 802.11s peut en exiger une stable), des IDs d'appareil et de service
  Wi-Fi Direct/Aware, des empreintes de probe-request, et — contre un adversaire
  capable — une *empreinte RF matérielle* qui survit à la randomisation MAC. Chacun
  est un pseudonyme stable pour l'*appareil*, indépendant de toute rotation d'overlay
  (`id`, `box_id`, cartes RZ-2, SP-7). La randomisation MAC aide contre la première classe
  et en rien contre l'empreinte RF. La *topologie* du maillage est de même une carte RF observable
  — qui relaie à qui est visible sur les ondes même sous trames uniformes. La partie
  NE DOIT PAS (MUST NOT) impliquer que l'inliabilité d'overlay s'étend à l'émetteur radio. C'est la deuxième
  face, aux côtés de l'indépendance de passerelle (BL-21), du problème récurrent d'identité/indépendance
  dans l'espace radio, déclaré et non refermé.
- **BL-19 (exposez la posture du maillage honnêtement — l'analogue de CT-19). [normatif]** Un
  client conforme DOIT (MUST) exposer, sur la surface d'honnêteté existante (PS-9/CT-19) : qu'un
  lien radio est en usage ; que ce lien est *physiquement localisable* (BL-18) **et
  radio-identifiable** (BL-18a) ; si sa sortie de passerelle est unique ou
  plurielle-et-*estimée*-indépendante (BL-6/BL-7) ; et que l'accessibilité du maillage — contrairement
  au plancher I-2 — ne porte **aucune** garantie et peut être nulle. Le message que l'interface énonce :
  *votre plancher du contenu tient ; sur le maillage vous pouvez être localisé et votre appareil reconnu
  sur les ondes là où vous vous tenez.*
- **BL-20 (pile concrète laissée ouverte ; affirmations bornées par ce qui est exécuté). [normatif]** La Partie 5
  ne mandate **pas** une pile radio spécifique, une méthode de routage (BL-9), un dimensionnement TTL/fragment
  (BL-12), ni un budget de batterie (BL-4) ; ce sont des hommes de paille et des décisions du propriétaire. Un client
  avec une pile de maillage non spécifiée NE DOIT PAS (MUST NOT) revendiquer une quelconque propriété de disponibilité de maillage
  *quantitative* ; il PEUT (MAY) revendiquer seulement le *qualitatif* « un nœud qui perd sa liaison montante peut prendre un
  saut de plus vers une passerelle voisine, et les parts DEVRAIENT (SHOULD) sortir par des passerelles
  estimées indépendantes », et seulement là où il exécute réellement ≥2 passerelles estimées indépendantes avec
  `k < n`.
- **BL-21 (le problème récurrent d'indépendance est déclaré, non refermé). [normatif,
  déclare-résidu]** Vérifier l'indépendance de passerelle sans une carte accessible et avec la
  localisation auto-déclarée (BL-6) est le **même problème qui apparaît pour les relais (OP-1),
  les signataires de publication (OP-8), et les auteurs de dépendances (OP-2/RB)** — vérifier l'indépendance
  d'une partie sans faire confiance à son auto-déclaration — portant maintenant son masque de couche radio
  à l'intérieur d'un blackout, où la carte des AS (Partie 8) est elle-même inaccessible. La Partie 5 ne le
  résout **pas** ; elle le réduit à ce résidu récurrent déclaré et alimente une estimation à confiance
  bornée, exactement comme la carte en alimente une avec un taux d'erreur déclaré (ID-12).

## 6. Exigences introduites ici

- **BL-1 / BL-2 / BL-3 / BL-4** — le maillage est une couche non un mode ; des rôles dérivés de la capacité
  variables dans le temps ; un opt-in explicite par contexte avant tout lien radio ; un budget honnête de
  batterie/stockage.
- **BL-5 / BL-6 / BL-7** — la dispersion sur passerelles indépendantes comme disponibilité ; « indépendant »
  est une estimation à confiance bornée, jamais auto-déclarée et quasi-vide dans un blackout profond ;
  trop peu/zéro passerelles se dégradent, n'échouent jamais ouvert.
- **BL-8 / BL-9 / BL-10** — les noms survivent, les routes non ; le saut suivant sans DHT et ses
  coûts ; la livraison passe toujours par les dépôts de la Partie 6, jamais vers un appareil nommé, et le
  cas tout-local est servi par un dépôt accessible par le maillage.
- **BL-11 / BL-12 / BL-13** — la validité Sphinx (non les octets) borne le portage long ; le blackout
  a besoin de sa propre enveloppe de style DTN ; l'enveloppe ne doit pas être un sélecteur et hérite du
  résidu d'imbrication de CT-6a.
- **BL-14 / BL-15** — la passerelle sybil est une éclipse physique, répondue seulement partiellement ;
  le mixage de source radio est une mesure de disponibilité/anti-éclipse, **non** GR-8 et **non**
  dissimulation d'origine.
- **BL-16 / BL-17** — le plancher est indépendant du maillage ; cohérence avec CT-18a, les
  trois états de livraison, le fond est toujours un fond.
- **BL-18 / BL-18a / BL-19** — la localisabilité physique et l'identité radio, toutes deux déclarées
  à pleine force et jamais résolues ; posture de maillage honnête sur PS-9.
- **BL-20 / BL-21** — pile concrète laissée ouverte ; le problème récurrent d'indépendance
  déclaré, non refermé.

BL-16 et BL-18/BL-18a sont les trois porteurs : le plancher ne dépend pas du
maillage, et le maillage ne peut cacher que vous transmettez ni que votre appareil est reconnaissable
sur les ondes. L'affirmation honnête est étroite et de forme disponibilité : *le maillage
étend l'accessibilité d'un échelon en dessous d'une coupure et garde le plancher du contenu dont il hérite,
mais il ne cache ni l'émetteur, ni l'appareil, ni la topologie, et il ne garantit pas la
livraison.* Cassez cette partie en nommant un anonymat de couche maillage que les clauses
promettent au-delà de BL-18/BL-18a, un endroit où le plancher I-2 est fait pour dépendre du maillage
réussissant au-delà de BL-16, un moyen par lequel BL-17 est lu comme élevant « possible » à « probable », ou une
fuite de couche radio que BL-18/BL-18a manquent. Telle est l'invitation, dans la voix de la maison — et sur
cette partie en particulier, la réponse honnête à « est-ce que cela résout le blackout ? » est « partiellement,
et voici exactement là où cela ne le fait pas. »
