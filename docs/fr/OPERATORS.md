# Faire tourner un nœud ScrambNet — exposition et posture de neutralité

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../en/OPERATORS.md)).

**Faire tourner un nœud ScrambNet, quel qu'il soit, est un acte visible et délibéré,
porteur d'un risque réel et non nul.** Ce document est honnête à ce sujet. Ce qui suit
vous dit ce que chaque rôle révèle et ce qu'il ne peut prouvablement pas révéler, afin que
vous puissiez décider. C'est une déclaration technique et de posture, **pas un avis
juridique** : ce projet est pseudonyme et ne peut connaître votre juridiction, votre
adversaire ni votre loi. Là où les enjeux le justifient, consultez votre propre conseil.

Ceci est une note informative, non une partie normative de la spécification. Elle s'appuie
sur des affirmations que la spécification pose déjà — les invariants `I-1…I-4`, les règles de
dead-drop (Part 6), les résidus de sélection de chemins (Part 3), les résidus du jeu de
données d'inférence (Part 8) — et elle pointe vers elles plutôt que de les redire. Là où la
spécification déclare un résidu ouvertement, cette note le porte ouvertement aussi ; elle
n'adoucit pas.

## Ce que chaque rôle voit, et ce qu'il ne peut pas voir

Chaque énoncé a la même forme : **ce que le rôle voit · ce qu'il ne peut prouvablement pas
voir, et la limite exacte de cette affirmation · le résidu honnête.** Les rôles sont ceux que
l'architecture définit (« Qui exécute quoi ») ; rien ici n'invente un rôle que le réseau n'a
pas.

### Client pur

En tant que client, vous êtes le rôle de plus faible exposition — « quasi invisible », circulant
sur les ponts et les transports caméléon — mais **pas à exposition nulle**, et cette note ne
prétendra pas le contraire. Votre **garde** (votre premier saut) voit votre véritable adresse
IP et le moment où vous êtes actif (voir ci-dessous) ; c'est une exposition côté client, et non
une simple propriété de la garde. La récupération a elle aussi un coût permanent et une surface
de métadonnées : un client sonde ses drops selon un horaire fixe obligatoire (`RZ-9`),
~212 MB/mois à travers quatre drops avant même que vous n'envoyiez quoi que ce soit (`RZ-16b`),
et cet horaire — non le contenu — est observable. Vous êtes à faible exposition ; vous n'êtes
pas invisible.

### Garde (le premier saut d'un client)

Une garde est l'unique relais qui voit la véritable adresse IP d'un client et le timing de son
activité. Si vous faites tourner une garde, vous apprenez qu'une IP particulière vous a parlé
ScrambNet, et quand. Vous n'apprenez **pas** où allait ce trafic ni ce qu'il contenait : par
`I-4`, chaque paquet qui vous traverse est un bruit de taille fixe indiscernable d'octets
aléatoires uniformes, et vous ne détenez qu'une seule part d'un seul message voyageant sur l'un
de plusieurs chemins.

La limite exacte de « vous ne pouvez pas reconstruire le message ». Le plancher de contenu
(`I-2`) est inconditionnel **en dessous de `k` positions capturées** : détenez moins de `k`
parts et elles sont, au sens théorie de l'information, du bruit, sans échappatoire
computationnelle ni quantique. Mais *atteindre* ce plancher dépend du fait que les `n` chemins
soient réellement **disjoints**, et la disjonction est **inférée, non prouvée** (`OP-1` ;
`PS-11`, « la disjonction supposée n'est pas la disjonction réelle »). Une carte choisie et
hostile peut *orienter* les relais d'un adversaire en position et pousser la capture de contenu
« de ~0 % à 100 % à ~15 % de possession » (`PS-12`/`ID-8a` — une conclusion que le projet porte
ouvertement après qu'une surestimation antérieure a été brisée). L'affirmation honnête n'est
donc pas « une garde ne peut pas reconstruire », point final ; c'est « aucune coalition ne
reconstruit **en dessous de `k` positions capturées**, et savoir si vos chemins atteignent
vraiment ce plancher est une propriété non vérifiée qu'un adversaire orienteur peut défaire
au-delà d'un seuil. »

**Le résidu honnête :** oui, vous voyez les IP des clients. C'est l'exposition la plus aiguë de
tous les rôles de relais, et elle est structurelle, non une fuite à corriger. Les IP des
personnes qui utilisent ScrambNet passent par votre nœud et sont visibles de quiconque peut
observer ses connexions.

### Nœud du milieu

Un nœud du milieu ne voit aucune des deux extrémités. Par la construction Sphinx et `I-4`, il ne
peut dire si son prédécesseur est le client d'origine ou un autre relais, ni si son successeur
est le dernier saut. Il ne voit aucune IP de client (c'est la position de la garde), aucune
destination, aucun contenu ; il détient une seule part chiffrée. C'est le rôle de relais de plus
faible information — du bruit qui passe entre deux autres machines. Son exposition est celle,
générale, que tout rôle partage (ci-dessous) : le faire tourner est un acte visible, et il
retransmet un trafic que vous ne pouvez pas inspecter.

### Drop (stockage dead-drop, Part 6)

Un drop stocke les parts déposées dans des boîtes et les sert quand on les sonde. Ce qu'il
stocke est, par `I-2`, illisible au sens théorie de l'information : chaque part stockée est en
dessous de `k` et indiscernable d'un bruit aléatoire pour quiconque — **y compris vous,
l'opérateur** — sans les autres parts, qui sont sur d'autres drops que vous ne contrôlez pas
(`RZ-5` : aucun drop ne détient jamais deux parts d'un même message ; l'ensemble de drops est
`d = n = 4`, `k = 3`, de sorte qu'un drop détient exactement une part, `< k`). Vous ne pouvez
pas lire ce que vous stockez, ne pouvez pas distinguer le contenu de deux boîtes, et ne pouvez
pas relier un dépôt à un expéditeur (`RZ-2`/`RZ-10`, `SP-7`). Cette affirmation est exacte et
n'est pas adoucie : un opérateur de drop est véritablement aveugle au contenu.

**Aveugle au contenu n'est pas la même chose que neutre à la livraison, et c'est là le résidu
honnête.** Un drop voit le **timing** : la cadence publique de sondage (`RZ-9`) et les temps de
dépôt dans les boîtes qu'il détient, au sein d'une époque ; un drop détenant plusieurs boîtes
peut corréler les *horodatages* de dépôt à travers elles même sous une indépendance de sondage
parfaite (`RZ-16`/`OP-9`, porté ouvertement dans la spécification de rendezvous §9). Et un drop
*peut* refuser la **livraison** sans rien lire : l'éviction du plus ancien d'abord jointe à la
fenêtre de récupération à 8-slot signifie qu'un inondateur — même un téléphone bon marché — peut
enfouir du courrier honnête au-delà de la fenêtre en ~17 secondes (`RZ-15`), un résidu de
flooding de livraison que la spécification déclare sans défense suffisante à ce jour (`OP-9`).
Donc : vous stockez un bruit illisible, mais vous observez *que* ce bruit est arrivé, a été
collecté, et quand, et la mécanique de stockage est une surface de livraison. Cette exposition
au timing et à la livraison est le résidu véritable du drop, déclaré et non caché.

### Pont (point d'entrée distribué le long du graphe social)

Un pont est un point d'entrée remis de personne à personne là où le réseau ouvert est bloqué
(niveaux de confiance à la Lox). Il voit une information de niveau garde pour les clients qui
l'atteignent (leur IP, rien en aval). Son exposition distinctive est **d'être découvrable en
tant que pont** : un censeur qui parvient à se faire passer pour un utilisateur peut apprendre
l'adresse de votre pont et le bloquer ou le surveiller. La distribution le long du graphe social
limite la vitesse et l'ampleur de la fuite d'une adresse — « un censeur peut se faire passer
pour un utilisateur ; il ne peut se faire passer pour l'ami de tout le monde » — mais ne rend
pas un pont indécouvrable.

**Le résidu honnête :** faire tourner un pont signifie qu'une de vos adresses circule, par
conception, parmi des inconnus-d'inconnus, dont certains peuvent être des adversaires. La
résistance à l'énumération est une course aux armements que le modèle de menace qualifie de
soutenable, non de gagnée.

### Nœud de maillage / passerelle (couche de blackout)

Un nœud mesh relaie d'appareil à appareil par Wi-Fi Direct / Bluetooth pendant un blackout ; une
passerelle fait le pont du maillage vers internet quand une route existe. Son exposition au
contenu est celle de tout relais — des parts de taille fixe qu'il ne peut lire (`I-2`/`I-4`).
Son exposition distinctive est **physique et locale** : sa visibilité est un signal radio à
l'échelle du quartier, corrélable à un lieu et potentiellement à une personne, précisément quand
et où un adversaire a coupé internet et est le plus motivé. C'est pourquoi l'architecture en fait
toujours un choix explicite. Une **passerelle** porte les *deux* expositions à la fois :
l'exposition physique/locale côté maillage, **et** l'exposition ordinaire de relais côté internet
— son IP tournée vers internet est un nœud ScrambNet observable pour son propre FAI — tout en
n'étant jamais une sortie clear-web (ci-dessous).

**Le résidu honnête :** de tous les rôles, celui-ci échange la plus forte cécité au contenu
contre la plus faible anonymité de l'opérateur. Les octets sont du bruit ; l'émetteur est dans un
lieu. Aucun invariant ne protège la localisabilité physique d'une radio.

### La sortie clear-web qui n'existe pas

ScrambNet n'a **aucun rôle de sortie clear-web**, et cela importe le plus aux opérateurs. La
sortie clear-web est le rôle le plus exposé de Tor : l'IP d'une sortie Tor apparaît comme la
source apparente de tout ce que ses utilisateurs envoient vers l'internet ouvert, et cet
opérateur reçoit les plaintes pour abus, les avis de retrait et l'attention des forces de l'ordre
pour un trafic qu'il n'a ni choisi ni ne peut voir. ScrambNet n'a pas d'équivalent. Le saut
terminal d'un message livre une part dans un dead-drop (Part 6) — du bruit illisible dans un
stockage interne au projet — et non vers un hôte tiers arbitraire. **L'adresse d'aucun nœud
ScrambNet n'apparaît comme l'origine d'un trafic attribuable arrivant à un service extérieur**
(la passerelle de maillage touche internet, mais elle porte un bruit interne à ScrambNet vers un
relais, non le trafic d'un utilisateur vers un hôte clear-web). C'est pourquoi l'architecture
énonce que l'exposition d'un opérateur de relais/drop est « structurellement plus basse que celle
d'une sortie Tor » — une comparaison d'exposition **technique**, jamais une affirmation sur votre
responsabilité juridique. Dit précisément : ceci retire l'exposition *spécifique* au nœud de
sortie ; cela ne rend **aucun** rôle sans risque, et cela ne fait pas de ScrambNet un proxy de
sortie — structurellement il n'en est pas un, et cette absence est une fonctionnalité, y compris
pour vous.

### Faire tourner plus d'un rôle

La plupart des énoncés ci-dessus décrivent un rôle isolé. Une machine fait couramment tourner
plusieurs rôles — garde, relais et drop ensemble — et la co-localisation crée des corrélations
qu'aucun des énoncés à rôle unique ne montre. Un drop détenant plusieurs boîtes corrèle le timing
de dépôt à travers elles (`RZ-16` §9) ; un relais qui est **aussi un utilisateur** et qui « est
en ligne exactement quand son opérateur discute est une attaque par intersection contre
lui-même » (l'architecture le nomme directement). La discipline que l'architecture prescrit est
la mitigation : un horaire toujours actif, indépendant de votre propre usage, de sorte que votre
temps de fonctionnement ne dise rien de votre activité. Si vous faites tourner plus d'un rôle,
votre exposition n'est pas le minimum des rôles — c'est leur combinaison.

## La posture face à l'abus

C'est la partie qu'un lecteur hostile mettra le plus à l'épreuve, aussi chacune de ses phrases
est-elle bâtie sur une incapacité vraie, et aucune n'introduit de levier.

**(a) L'incapacité, énoncée comme une propriété de sécurité.** ScrambNet ne peut lire, identifier,
cibler, ni bloquer ou prioriser de façon sélective selon le contenu aucun message, utilisateur
ou contenu. Ce n'est pas une politique que nous adoptons et pourrions renverser ; c'est une
propriété de la conception. Un drop stocke des parts illisibles au sens théorie de l'information
en dessous de `k` (`I-2`) ; un relais retransmet un bruit de taille fixe qu'il ne peut distinguer
d'aucun autre (`I-4`) ; il n'y a pas de registre d'utilisateurs (il n'y a pas d'inscription), pas
d'autorité d'annuaire, et pas de partie privilégiée nulle part dans le protocole (`I-3`). Le
projet n'a pas de clé, pas de commutateur, et aucune position dans le réseau depuis laquelle le
contenu *pourrait* être inspecté ou filtré. Les mêmes mathématiques protègent tout le monde
parce qu'elles ne peuvent distinguer personne, et cette indiscrimination est ce qui rend la
protection digne de confiance : un réseau qui *pourrait* choisir des camps est un réseau qu'un
adversaire puissant pourrait *faire* choisir des camps. (Une note de portée honnête : la cécité
au contenu n'est pas la neutralité à la livraison — la mécanique de stockage d'un drop est une
surface de livraison, `RZ-15` — donc « ne peut bloquer » signifie ici *ne peut bloquer de façon
sélective selon le contenu*, qui est la propriété qui importe pour la neutralité.)

**(b) Ce que le projet peut véritablement faire.** Ce que nous pouvons faire, nous le faisons au
grand jour : publier la conception complète afin que quiconque puisse l'étudier, l'attaquer ou la
réimplémenter (`I-1`) ; recevoir des rapports de **vulnérabilité** et y donner suite dans le cadre
de la politique de sécurité (SECURITY.md) ; corriger les défauts ; et continuer de dire clairement
ce que le réseau protège et ne protège pas. C'est toute la liste. Rien là-dedans n'implique de
regarder, d'atteindre ou d'agir sur le trafic de quiconque, parce que la conception ne nous en
donne aucun moyen — et le canal de vulnérabilité est pour les défauts de la conception et du
code, jamais un canal pour signaler du trafic ou des utilisateurs, parce qu'il n'y a rien que
nous puissions faire d'un tel signalement et que son existence ne doit pas laisser entendre le
contraire.

**(c) Ce que le projet refuse de construire, et pourquoi.** Nous ne construirons pas de capacité
de modération, de porte dérobée de signalement, de filtre de contenu, de liste de blocage
d'utilisateurs, de robinet d'« accès légal », ni aucun autre mécanisme qui permette au projet, à
un opérateur, ou à quiconque, de lire, cibler ou supprimer du contenu ou des utilisateurs. Nous
refusons non par indifférence au tort mais parce qu'un tel mécanisme est auto-destructeur en ses
propres termes. Tout levier qui peut être pointé vers un contenu appelé « abus » est le même
levier, pointé dans l'autre sens, visant un contenu appelé « dissidence » — c'est une seule
capacité, et quiconque peut en imposer l'usage décide de ce qu'elle vise. Ce serait précisément
le point de contrôle unique que `I-3` interdit et le choix de camp que le modèle de menace met
hors de portée. Dès l'instant où un tel levier existe, la promesse du réseau est fausse pour tout
le monde, y compris les personnes qu'il a été bâti pour protéger ; l'adversaire n'a plus à briser
les mathématiques, seulement à s'emparer du levier. L'absence d'un mécanisme de modération n'est
pas une lacune que nous aurions échoué à combler — c'est une propriété de sécurité porteuse que
nous refusons de détruire. (Tout contrôle d'admission anti-flooding que le projet adopterait un
jour — la question ouverte `OP-9` que `RZ-15` laisse non résolue — DOIT (MUST) être aveugle au
contenu et aveugle à l'identité par construction, et le candidat de tête filtre par la possession
d'une carte de contact par relation, non par le point de vue ; une règle d'admission qui devrait
*identifier un expéditeur* ou *inspecter un dépôt* serait un levier et est interdite sous cette
même posture.)

**(d) Le coût honnête.** Ceci n'est pas gratuit, et nous ne prétendrons pas le contraire. Un
réseau qui ne peut choisir de camp ne peut pas non plus choisir *contre* le tort. ScrambNet peut
être utilisé pour des choses que ses auteurs trouvent répugnantes, et le projet ne peut l'empêcher
par conception. Les analogies habituelles — le système postal ne peut lire chaque lettre, un
réseau téléphonique ne peut écouter à la recherche d'« mauvais » appels, TLS ne peut refuser de
chiffrer la connexion d'un criminel — portent la forme de l'argument mais le **sous-estiment**,
et la différence est toute l'affirmation : les points terminaux du courrier, du téléphone et de
TLS *peuvent* être contraints par mandat d'intercepter une cible précise, parce qu'un point
d'observation et une clé existent. Le « ne peut pas » de ScrambNet est **plus fort** — il n'y a
aucune position depuis laquelle un opérateur contraint *pourrait* remettre du contenu en dessous
de `k` (`I-2`), et aucune partie unique à laquelle on *pourrait* ordonner de publier une vue
empoisonnée du réseau (`I-3` ; la spécification nomme directement la réalité « contraint, assigné
à comparaître, ou saisi »). Les protections sont indiscriminées parce qu'une protection sélective
n'est pas une protection — c'est une liste de qui a le droit d'être en sécurité, tenue par
quiconque détient la plume. Nous acceptons le coût les yeux ouverts : un outil assez puissant
pour protéger les sans-pouvoir des puissants ne peut venir avec un commutateur que les puissants
peuvent actionner. Le résumé honnête n'est pas « ScrambNet empêche l'abus ». C'est :
**ScrambNet protège la communication, et cette protection ne vient pas avec un interrupteur
d'arrêt — pour personne, contre personne, nous y compris.**

## Là où vous êtes exposé malgré tout

Énoncé clairement et laissé debout — sans « mais ne vous inquiétez pas », sans sécurité
sous-entendue.

- **Faire tourner un nœud, quel qu'il soit, est un acte visible.** Un relais publie une adresse ;
  un pont en fait circuler une ; un nœud mesh émet un signal radio. Les mathématiques protègent
  le *contenu et la liaison du trafic*, non le *fait que votre machine est sur le réseau*. Si
  être vu faire tourner de l'infrastructure d'anonymat est en soi votre risque, aucun invariant
  ne le retire.
- **Une garde voit les IP des clients.** Structurel, non un bug. Les IP des utilisateurs de
  ScrambNet passent par votre garde et sont visibles de quiconque peut observer ses connexions.
- **Un drop voit le timing et façonne la livraison.** Contenu illisible, oui — mais les temps de
  dépôt et de sondage au sein d'une époque, la corrélation du timing de dépôt entre boîtes, et la
  surface de livraison d'éviction/flooding sont des résidus réels et déclarés
  (`RZ-15`/`RZ-16`/`OP-9`).
- **Un pont est découvrable.** Par conception, il est remis à des inconnus ; certains peuvent être
  des adversaires. La résistance à l'énumération est une course aux armements, non une garantie.
- **Un nœud mesh est physiquement localisable.** Les octets sont du bruit ; l'émetteur est dans un
  lieu, précisément quand un adversaire a coupé internet.
- **Atteindre le plancher de contenu dépend d'une disjonction que vous ne pouvez vérifier.** Le
  plancher `I-2` en dessous de `k` est inconditionnel ; que vos chemins ou vos drops soient
  vraiment indépendants est inféré, non prouvé (`OP-1`/`PS-11`), et une carte orientante peut le
  défaire au-delà d'un seuil (`PS-12`). Faites tourner en le sachant.
- **Votre loi locale peut vous contraindre quels que soient les octets.** Ce projet ne peut vous
  dire ce qu'une autorité peut exiger de vous, et il ne prétendra pas que la cécité au contenu du
  réseau est un bouclier juridique — c'est un fait technique sur les octets, non une conclusion
  juridique propre à une juridiction. Qu'un drop *ne puisse* lire ce qu'il stocke est vrai et peut
  importer, ou non, selon une loi que ce projet pseudonyme ne peut connaître. **C'est là que vous
  avez besoin de votre propre conseil, non du nôtre.** Nous énonçons ce qui est techniquement
  révélé ; ce que cela signifie pour vous, juridiquement, est à vous de le découvrir.
