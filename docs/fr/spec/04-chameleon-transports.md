# Spécification ScrambNet — Partie 4 : Transports caméléon

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/04-chameleon-transports.md)).

**Statut : BROUILLON (DRAFT), et la partie la plus susceptible de pourrir.** Cette partie énonce un
modèle de menace de transport et une évaluation honnête du réalisme. Elle n'engage aucun mécanisme
extérieur et ne promet aucune victoire dans la course aux armements de la censure. Lisez d'abord le §1 et
l'évaluation du réalisme (§8) : entre les deux, ils disent la seule chose étroite que cette partie est
disposée à affirmer, et la chose bien plus grande qu'elle refuse d'affirmer. Les valeurs d'homme de paille
sont marquées `(s)`.

Les couches d'architecture L1 (caméléon) et L3 (transports éphémères) vivent ici ; le transport est la
chose qui porte les octets d'une part au-delà d'un censeur. Cette partie est classée sous OP-7
(accessibilité et amorçage), et elle dépend du — plutôt qu'elle ne résout le — problème d'amorçage
sans contact (OP-7, GR-10).

## 1. La décision, en deux phrases

- **Cette partie ne prétend pas que ScrambNet gagne ou soutient la course aux armements de la
  censure.** Elle prétend l'opposé quant à sa propre importance : le plancher de confidentialité et
  de dispersion (I-2) ne dépend **pas** du tout de la couche de transport. Un transport achète
  l'*accessibilité* — la capacité d'acheminer les octets d'une part jusqu'à un relais — et
  l'accessibilité a le droit d'échouer, en descendant l'échelle de dégradation de l'architecture
  (L1→L2→L3→L4) et, lors d'une coupure totale sans voisin de maillage, jusqu'à zéro, **sans que le
  plancher du contenu ne bouge jamais** (CT-16).
- **L'affirmation honnête et défendable est donc étroite et ne doit pas être élargie :** *nous ne
  rendons pas impossible de perdre la course du transport ; nous rendons sa perte non catastrophique
  pour la confidentialité.* Un censeur peut réduire l'accessibilité à zéro ; un censeur ne peut
  toujours pas lire le contenu en dessous de `k` parts, parce que cette protection n'a jamais chevauché
  le transport (CT-16, CT-18, CT-18a).

Tout ce qui suit est le modèle de menace qui justifie cette affirmation étroite et l'évaluation du
réalisme (§8) qui en est l'épine dorsale — la section la plus importante de la partie, non une annexe.

## 2. Le modèle de menace de transport (ce que le censeur de 2026 fait réellement)

- **CT-1 (déclarez ce à quoi vous résistez ; le silence est une concession). [normatif]** Une
  description de transport conforme DOIT (MUST) énoncer lesquelles des capacités adverses CT-2…CT-7a
  elle prétend repousser et lesquelles elle concède. Une capacité non déclarée est traitée comme
  concédée (la règle de complétude I-1, pour les transports) — un transport qui ne nomme pas une
  attaque ne s'en est pas défendu.
- **CT-2 (DPI passif / empreinte de protocole).** Le censeur classe les flux par signatures d'octets
  et de structure sans lire le contenu ; le travail du caméléon est de ne présenter aucune signature
  distinctive propre (CT-8).
- **CT-3 (correspondance d'empreinte TLS). [normatif]** Le censeur prend l'empreinte du ClientHello
  TLS. La base de référence de 2026 est **JA4 / JA4+** (FoxIO), non le JA3 retiré : JA4 **trie** les
  suites de chiffrement et les extensions avant le hachage et ignore GREASE, de sorte qu'il est robuste
  à la *randomisation* de l'ordre des extensions que les navigateurs grand public font désormais. Une
  imitation conforme DOIT donc (MUST) faire correspondre l'*ensemble* des suites de chiffrement de la
  cible, l'*ensemble* des extensions, l'ALPN, les versions prises en charge et le *motif* GREASE — non
  simplement son ordre, que JA4 ne distingue plus. (Une imitation qui ne randomise que l'ordre n'est
  pas pour autant cachée.)
- **CT-4 (inspection SNI / ECH).** Le censeur lit le SNI en clair pour apprendre le nom de
  destination. ECH peut le cacher, mais seulement conditionnellement (CT-11).
- **CT-5 (sondage actif / connexion de retour).** Le censeur se connecte à un point d'accès suspecté
  et vérifie s'il se comporte comme ce qu'il prétend être ; la survie exige CT-10.
- **CT-6 (classification statistique passive de la forme du flux). [normatif, déclare-résidu]** Le
  censeur classe les flux par *statistiques*, non par octets : temporisation, volume, direction,
  structure de rafales, **et entropie** — et l'ensemble de caractéristiques est ouvert et choisi par
  l'adversaire, y compris des classifieurs appris (ML). En particulier, la **détection de « trafic
  entièrement chiffré » à haute entropie** bloque les flux qui semblent *trop aléatoires* sans sondage
  ni correspondance d'empreinte (observée sur le GFW depuis fin 2021). Cela a une conséquence
  contre-intuitive dont dépend le reste de la partie : **une couverture randomisée ou à haute entropie
  est un signal *plus vif*, non plus terne** — la couverture la plus sûre ressemble à un protocole réel
  très courant, jamais à du bruit. CT-6 ne peut être refermé par un mimétisme au niveau de l'octet
  (CT-8) ; ses réponses honnêtes sont à d'autres couches (CT-12, CT-15).
- **CT-6a (détection TLS-dans-TLS / chiffrement imbriqué). [normatif, déclare-résidu]** Un transport
  qui tunnelise le trafic de parts I-4-uniforme déjà chiffré de ScrambNet *à l'intérieur* d'un flux TLS
  externe imité laisse des motifs caractéristiques de taille d'enregistrement et de temporisation — un
  flux TLS qui *porte une autre poignée de main TLS* — que le DPI peut signaler même lorsque la poignée
  de main externe est parfaite à l'octet (CT-3/CT-4 propres). C'est l'attaque vedette contre le
  contournement imbriqué et elle DOIT (MUST) être déclarée : une imitation peut être parfaite à la
  poignée de main et tout de même être attrapée à la structure du flux. C'est un résidu que le
  mimétisme d'octets ne peut refermer (il appartient à CT-12) ; le nommer est exigé par CT-1.
- **CT-7 (énumération de points d'accès — bloquer ce qui est connu). [normatif]** Le censeur découvre
  et bloque en gros les points d'accès/ponts connus. La dispersion (CT-15) et la distribution de ponts
  le long du graphe social (architecture L2, Lox) en élèvent le coût ; le mimétisme ne traite pas du
  tout l'énumération.
- **CT-7a (découverte de points d'accès — la ligne de front de l'amorçage, déclarée ouverte).**
  Distincte de CT-7 : *comment un utilisateur censuré obtient un point d'accès non bloqué en premier
  lieu, plus vite que le censeur ne l'énumère.* C'est le problème de distribution de ponts (Lox /
  graphe social) et il se réduit à **OP-7 (amorçage sans contact), qui est ouvert.** La Partie 4 ne le
  résout pas ; elle y renvoie (GR-10, OP-7), et toute affirmation selon laquelle les points d'accès
  sont découvrables de façon fiable est une promesse non étayée que cette partie refuse de faire.
- **CT-7b (liste blanche de protocoles — le cas limite).** Le censeur ne permet qu'une liste
  d'autorisation de protocoles/destinations et rejette le reste (observé : la liste blanche du réseau
  national iranien, 2025–2026). Contre cela, le mimétisme d'une destination *autorisée* est le seul
  coup à jouer, et même lui échoue lorsque le censeur accepte le coût collatéral (§8, CT-14) — jusqu'à
  une coupure totale, où aucun transport n'atteint quoi que ce soit (CT-18a).

## 3. Discipline de l'imitation (le tapis roulant, rendu normatif)

- **CT-8 (aucune signature de projet statique ; imiter tel que déployé). [normatif]** Un transport
  caméléon NE DOIT PAS (MUST NOT) présenter une signature sur le fil statique et propre au projet, et
  DOIT (MUST) imiter un protocole cible *tel qu'il est réellement déployé*, non un protocole idéalisé.
  Une pile artisanale ou figée est elle-même une empreinte et est non conforme.
- **CT-9 (la clause de dérive uTLS). [normatif]** Une imitation de style uTLS DOIT (MUST) suivre le
  ClientHello *actuellement déployé* de la cible et DOIT (MUST) déclarer la version de la cible qu'elle
  imite (CT-20). Contre JA4 (CT-3), le distinguant est la divergence dans les *ensembles* de
  chiffrements et d'extensions, l'ALPN, les versions prises en charge et le motif GREASE — ceux-ci
  dérivent à chaque publication de navigateur, de sorte qu'une imitation figée à la version N devient
  un distinguant une fois que la population réelle passe à N+1. C'est un **tapis roulant de maintenance
  sans état terminal** : il n'y a aucune version à laquelle le travail est terminé (§8). Le plancher NE
  DOIT PAS (MUST NOT) dépendre du fait de suivre son allure (CT-16).
- **CT-9a (préférer une cible à forte population — pour des raisons d'ensemble d'anonymat, non
  économiques). [normatif]** Un déploiement conforme DEVRAIT (SHOULD) imiter une cible à forte
  population et à évolution rapide (le TLS d'un navigateur grand public) plutôt qu'une cible de niche,
  pour deux raisons *mécaniques* : le grand troupeau est un meilleur ensemble d'anonymat (plus de flux
  réels parmi lesquels se cacher), et une cible à correction rapide raccourcit la fenêtre de péremption
  de CT-9. Cette clause ne fait **aucune** affirmation économique selon laquelle le troupeau serait
  « trop coûteux à bloquer » — ce pari est CT-13, déclaré réfutable, et le bilan de 2026 (un censeur
  national a bloqué le plus grand troupeau ECH, §8) montre qu'il peut être perdu.

## 4. Survie au sondage actif

- **CT-10 (survivre à un sondage par connexion de retour ; le silence est lui-même une empreinte).
  [normatif]** Un point d'accès caméléon DOIT (MUST) survivre à un sondage actif : il DOIT (MUST)
  compléter une poignée de main *réelle* et valide du protocole qu'il imite et servir un comportement
  de couverture plausible à un sondeur non authentifié (p. ex. une véritable terminaison TLS faisant
  proxy vers du contenu d'apparence réelle), ne révélant le service clandestin qu'à un client prouvant
  un secret pré-partagé. Le modèle moderne est terminer-le-vrai-TLS-et-faire-proxy-vers-un-vrai-site,
  **non** l'ancien modèle rester-silencieux : *rester silencieux face à un sondeur non authentifié est
  lui-même un comportement détectable* (délais d'attente caractéristiques, seuils d'acceptation
  d'octets, traitement du rejeu) et est non conforme.
- **CT-10a (le secret pré-partagé est une ligne de pont — sa distribution est ouverte). [normatif]**
  Le secret qui distingue un vrai client d'un sondeur dans CT-10 est une **ligne de pont**, et **sa
  distribution est OP-7 / GR-10, déclarée ouverte.** CT-10 suppose un secret déjà livré ; il ne résout
  **pas** la livraison. La résistance au sondage et l'amorçage sont des problèmes distincts, et les
  confondre (supposer que le secret est d'une manière ou d'une autre déjà partout) est l'erreur que
  CT-7a interdit.
- **CT-10b (le coût amincit le vivier d'opérateurs).** Un contenu de couverture réel, des certificats
  réels et une terminaison réelle sont une charge opérationnelle permanente par point d'accès. Élever
  cette barre est exactement ce qui rétrécit le vivier d'opérateurs volontaires — ce qui est le
  problème de maintenance soutenue (§8) portant une casquette opérationnelle.

## 5. Posture ECH (sans surenchère)

- **CT-11 (ECH est opportuniste et borné par la disponibilité, jamais un plancher). [normatif]** Une
  description conforme NE DOIT PAS (MUST NOT) présenter ECH (Encrypted Client Hello) comme une défense
  SNI résolue. Elle énonce : (a) ECH ne cache le SNI que là où le fournisseur de façade le déploie, le
  client le prend en charge, **et la recherche DNS chiffrée qui porte la configuration ECH réussit** —
  bloquez ou rétrogradez ce DNS et ECH ne s'engage silencieusement pas, ce qui est le mode d'échec réel
  de 2026 ; (b) le déploiement côté serveur en 2026 est une tranche *minoritaire-mais-croissante*,
  concentrée chez quelques grands fournisseurs de façade, non la longue traîne, de sorte que « le SNI
  est caché » est faux pour la plupart des destinations la plupart du temps ; (c) **« bloquer ECH
  entièrement » est une réponse de censeur observée** (un censeur national bloquant les connexions ECH
  vers un fournisseur majeur depuis fin 2024), à laquelle ECH par construction ne peut contrer. ECH est
  une amélioration opportuniste, non une garantie. *(La spécification ECH est le travail ESNI/ECH du
  groupe de travail TLS de l'IETF ; cette partie ne fixe pas un numéro de RFC publié, qui n'était pas
  encore confirmé au moment de la rédaction — citez le document actuel, non un numéro qui pourrait être
  erroné.)*
- **CT-11a (dégrader, ne pas fuir). [normatif]** Là où ECH est indisponible ou bloqué, un transport
  conforme DOIT (MUST) se dégrader vers l'échelon suivant de l'échelle (ponts éphémères L2) plutôt que
  de se replier vers un flux à SNI en clair distinguable. Le chemin de dégradation, non ECH, est la
  garantie.

## 6. Le résidu de corrélation de flux

- **CT-12 (le mimétisme ne peut vaincre la forme du flux ; dites-le). [normatif, déclare-résidu]** Le
  mimétisme au niveau de l'octet NE DOIT PAS (MUST NOT) être présenté comme vainquant la corrélation de
  forme de flux (CT-6), la détection TLS imbriqué (CT-6a), ou un observateur passif global corrélant
  l'entrée et la sortie. La temporisation, le volume, la direction, la structure de rafales et
  l'imbrication fuient à travers une imitation parfaite. Ce sont des résidus que le mimétisme *ne peut*
  refermer et qui DOIVENT (MUST) être déclarés, non cachés. Les seules réponses honnêtes sont à
  d'autres couches — la dispersion répartit la forme d'un message sur plusieurs couvertures (CT-15, une
  propriété de *disponibilité*, non de dissimulation de forme) et le mixage en mode paranoïaque
  (architecture L2) échange de la latence contre de la résistance de forme — jamais l'imitation
  elle-même. Les attaques d'oracle de site web et de confirmation côté entrée se réduisent à ce même
  résidu de corrélation et à la ligne de l'adversaire passif global que le modèle de menace déclare
  déjà hors du périmètre du mode rapide.

## 7. Dispersion de parts sur des couvertures diverses (le verdict normatif)

- **CT-15 (le verdict : la diversité aide la disponibilité, nuit à l'inobservabilité ; achetez la
  première, payez et déclarez la seconde). [normatif]** Porter les `n` parts d'un message sur des
  *types de couverture différents* (une en TLS, une en WebRTC, une sur le maillage) est une décision à
  double tranchant, résolue comme suit :
  (a) elle NE DOIT PAS (MUST NOT) être supposée améliorer l'**inobservabilité** — `n` couvertures sont
  `n` empreintes à réussir (CT-3), `n` tapis roulants (CT-9), et un préjudice véritablement nouveau :
  une **surface de corrélation inter-couvertures**. Un adversaire qui voit un flux TLS, un flux WebRTC
  et une rafale de maillage qui sont corrélés en temporisation/volume (CT-6) peut les lier comme les
  parts d'un même message *sans briser aucune imitation isolée* — la diversité n'atténue pas ce signal,
  elle peut l'aviver ;
  (b) elle est permise et valorisée **strictement en tant que mesure de disponibilité** : aucun blocage
  d'une seule couverture ne tue la livraison (`k < n` achète déjà cela), et l'énumération de points
  d'accès (CT-7) doit désormais réussir contre les couvertures *individuellement* — ce qui élève le
  coût du censeur contre un censeur qui bloque les couvertures *une à la fois*, et ne procure **aucun**
  bénéfice contre une liste blanche de protocoles (CT-7b) ou une coupure totale (CT-18a), qui bloquent
  toutes les couvertures en un seul acte.
- **CT-15a (vendez-la comme accessibilité, jamais comme camouflage). [normatif]** Un client conforme
  NE DOIT PAS (MUST NOT) présenter la dispersion multi-couvertures à l'utilisateur comme un *camouflage
  plus fort* ; il PEUT (MAY) la présenter comme une *accessibilité plus forte*. Confondre les deux est
  la même erreur de catégorie liaison-vs-contenu que ID-12a interdit pour la carte, réénoncée pour les
  transports : le multi-couvertures améliore une propriété de disponibilité et n'améliore pas une
  propriété de mimétisme.
- **CT-15b (ensemble de couvertures minimal laissé ouvert ; affirmations bornées par ce qui est
  réellement exécuté). [normatif]** La Partie 4 ne mandate **pas** un ensemble de couvertures minimal —
  mandater `n` couvertures mandate `n` tapis roulants de maintenance que le projet pourrait ne pas être
  en mesure de doter en personnel (§8). Un client avec un ensemble de couvertures ouvert/non spécifié
  NE DOIT PAS (MUST NOT) revendiquer une quelconque propriété de disponibilité *quantitative* (pas de
  « résiste à l'énumération sur N couvertures » sans un N énoncé et réellement exécuté) ; il PEUT (MAY)
  revendiquer seulement le *qualitatif* « aucun blocage d'une seule couverture ne tue la livraison », et
  seulement lorsqu'il exécute réellement ≥2 couvertures indépendantes avec `k < n`. Exiger ou non ≥2
  couvertures pour le défaut de livraison dispersée est une décision du propriétaire (§8).

## 8. L'évaluation honnête du réalisme (l'épine dorsale)

*(Cette section est la partie, non une annexe. Elle est écrite dans la §voix de résidu des Parties 8 et
11.)*

**Cette partie n'engage aucun mécanisme extérieur et ne doit pas prétendre le contraire.** C'est un
verdict sur l'endroit où le projet est fragile, énoncé à pleine force : **la couche de transport est la
couche la plus faible et la plus susceptible de pourrir du projet, et la posture honnête est de le dire
et de concevoir de sorte que le plancher n'en dépende jamais.**

**Le tapis roulant de dérive uTLS (CT-9).** Une imitation figée à une version de navigateur devient un
distinguant au moment où la population réelle passe à autre chose — un troupeau plus petit et plus périmé
est un signal *plus vif*, non plus terne. Il n'y a aucune version à laquelle le travail est terminé.
Contre JA4 l'ordre n'importe plus, mais les *ensembles* de chiffrements/extensions dérivent encore à
chaque publication, de sorte que le tapis roulant est plus lent qu'il ne l'était contre JA3 mais ne
s'arrête pas. Le projet n'a pas le droit de gagner cela ; il a le droit de courir dessus ou d'en
descendre, et CT-16 est la décision de rendre la descente survivable.

**La réalité d'ECH en 2026 (CT-11).** ECH ne cache le SNI que là où le fournisseur, le client *et la
recherche DNS chiffrée* réussissent tous, et en 2026 c'est une minorité de destinations. « Bloquer ECH
entièrement » a déjà été utilisé par un censeur national contre le plus grand fournisseur de façade, ce
à quoi ECH ne peut contrer. ECH est une amélioration opportuniste bornée par le déploiement ; le
plancher est le chemin de dégradation, jamais ECH.

**L'argument économique et ses contre-exemples (CT-13/CT-14).** « Me bloquer coûte plus que cela ne
rapporte » est un dissuasif réel et une fausse garantie. Le bilan de 2026 a des contre-exemples répétés
de censeurs payant de grands coûts collatéraux plutôt que de permettre le contournement : un régulateur
national bloquant ECH vers un fournisseur majeur (depuis fin 2024) ; une **liste blanche de
protocoles** de réseau national ne permettant qu'une courte liste d'autorisation (Iran, 2025–2026) ; et
des **coupures totales d'Internet** durant les troubles (Iran, mi-2025 et de nouveau début 2026).
Chacun est un censeur choisissant le contrôle plutôt que le commerce. Le pari économique est
probabiliste : il fonctionne contre un censeur qui valorise le collatéral et échoue contre un censeur
qui a montré qu'il ne le fera pas. Nous énonçons cela plutôt que d'agiter la main sur l'économie comme
réglée. *(Ceux-ci sont cités comme catégories de comportement observé ; une rédaction conforme devrait
y attacher des dates et des juridictions et DOIT (MUST) abandonner tout contre-exemple qu'elle ne peut
soutenir — un contre-exemple erroné est pire qu'aucun, CT-14.)*

**La question inconfortable, répondue (le résidu central déclaré).** *Un projet de volontaires
pseudonyme a-t-il la capacité de maintenance soutenue qu'une course aux armements de transport exige ?*
Tor a du personnel rémunéré, un écosystème de transports enfichables financé et des années de mémoire
institutionnelle, et il *perd tout de même* des rounds contre des censeurs déterminés. Un projet
pseudonyme et sans registre — un projet qui par conception (I-3, et la gouvernance des Parties 10/11)
refuse la coordination centrale qui lui permettrait de pousser (push) une mise à jour de transport à
tout le monde d'un coup — a **moins** de cette capacité, non plus. La réponse honnête est donc **non,
pas de façon fiable.** La course aux armements de transport récompense exactement la maintenance
financée, coordonnée et liée à l'identité que le projet a renoncée pour des raisons de principe. Nous
devrions nous attendre à ce que la couche de mimétisme prenne du retard.

**Et c'est pourquoi rien de porteur ne repose dessus.** La capacité de maintenance pour gagner une
course aux armements de transport est exactement ce que nous n'avons pas et exactement ce que le
plancher n'exige pas. Nous nous attendons à ce que la couche de mimétisme prenne du retard ;
l'architecture est un pari qu'elle le peut — le même pari que l'architecture fait déjà pour la ceinture
en oignon (« si toute cette couche calculatoire tombe un jour, le réseau ne devient pas lisible — il
devient moins commode ») et que les Parties 10/11 font pour les mises à jour (refuser le push, payer la
latence, l'énoncer). C'est un pessimisme honnête sur une capacité qui nous manque, converti en la
justification de conception qui rend le déficit non catastrophique — non un défaitisme.

**Le bas de l'échelle, concédé (CT-18a).** L'échelle de dégradation L1→L2→L3→L4 a un fond, et le fond a
un fond. Lors d'une **coupure totale sans voisin de maillage physique à portée**, aucun transport
n'atteint quoi que ce soit et **aucun message n'est livré — point final.** Nous ne rendons pas *cela*
survivable. Le plancher du contenu I-2 tient toujours (rien n'est *révélé* ; ce qui ne peut être envoyé
ne peut être lu), mais l'accessibilité est nulle, et le plancher à ce point est *intact et inutile* :
confidentialité parfaite d'un message qui ne peut quitter l'appareil. L'affirmation honnête n'est pas
« la communication passe toujours » — c'est « la confidentialité ne dépend jamais du transport, et quand
le transport meurt le secret meurt avec lui non livré, non exposé ». Un nœud de maillage dans un
blackout brûlant est lui-même un acte physiquement localisable (Partie 5, OP-6), de sorte que même le
dernier échelon est une adhésion volontaire explicite et dangereuse, non une garantie.

## 9. Le garde d'invariant

- **CT-16 (le plancher ne dépend pas du fait de gagner la course ; confidentialité ≠ disponibilité).
  [normatif]** Aucune garantie de confidentialité ou de dispersion (I-2) NE DOIT (MUST) dépendre de la
  réussite d'un transport caméléon, du fait qu'une imitation reste à jour (CT-9), de la disponibilité
  d'ECH (CT-11), ou du maintien de l'argument économique (CT-14). Les transports achètent
  l'**accessibilité uniquement**. I-2 garantit la **confidentialité** (le contenu en dessous de `k` est
  illisible), une propriété *livré-vs-non-livré* qui est muette sur le fait de savoir si quoi que ce
  soit est livré — **non** une garantie lisible-vs-illisible de livraison. L'échec du transport DOIT
  (MUST) se dégrader en descendant l'échelle (L1→L2→L3→L4), et au fond jusqu'à une accessibilité nulle
  (CT-18a), **sans jamais** compromettre le contenu en dessous de `k`. Une conception dans laquelle
  perdre la course du transport perd le plancher est non conforme.
- **CT-17 (minimisez la dépendance ; ne promettez pas de gagner). [normatif]** Une posture conforme
  DOIT (MUST) minimiser la dépendance du plancher au mimétisme plutôt que de promettre de le soutenir.
  Là où le mimétisme et la dégradation répondent tous deux à une menace, la partie DOIT (MUST) préférer
  le chemin de dégradation comme garantie et traiter l'imitation comme la commodité (la maxime propre à
  l'architecture : tout ce qui peut expirer est une commodité).
- **CT-18 (le plafond déclaré : aucune affirmation de victoire dans la course aux armements).
  [normatif]** La Partie 4 NE DOIT PAS (MUST NOT) prétendre que ScrambNet gagne ou soutient la course
  aux armements de la censure. La seule affirmation qu'elle fait est celle de CT-16 : la couche de
  transport a *le droit de perdre* sans que le plancher ne perde. Tout texte, interface ou README
  affirmant une invincibilité au niveau du transport, une victoire « soutenable » dans la course aux
  armements, ou ECH-comme-résolu est non conforme et DOIT (MUST) être corrigé — y compris la ligne du
  censeur national du modèle de menace, que cette partie révise pour scinder l'*accessibilité*
  (contestée, peut atteindre zéro) du *contenu* (protégé inconditionnellement, indépendant du
  transport).
- **CT-18a (le cas terminal est énoncé, non caché). [normatif]** Une rédaction conforme DOIT (MUST)
  énoncer explicitement le cas terminal de CT-18 : lors d'une coupure totale sans portée de maillage,
  l'accessibilité est nulle et aucun message n'est livré ; le plancher du contenu tient mais est inutile
  pour ce message non livré. « Nous rendons la perte de la course du transport survivable *pour la
  confidentialité*, non pour la livraison » est l'affirmation exacte, et rien ne peut être formulé de
  manière à impliquer que la livraison est garantie.

## 10. Surface d'honnêteté opérationnelle

- **CT-19 (exposez la posture de transport honnêtement). [normatif]** Un client conforme DOIT (MUST)
  exposer sa posture de transport courante sur la surface d'honnêteté existante (PS-9) : quelle
  couverture il utilise, si ECH est *réellement* en effet (non simplement tenté), et que
  l'accessibilité du transport — contrairement au plancher I-2 — ne porte **aucune** garantie et peut
  échouer jusqu'à zéro. Le message que l'interface énonce : *votre plancher du contenu tient ; votre
  capacité à atteindre le réseau, non.*
- **CT-20 (déclarez la péremption de l'imitation). [normatif]** Un déploiement conforme DEVRAIT
  (SHOULD) déclarer à quel point sa cible d'imitation est à jour (CT-9), l'analogue de transport du taux
  d'erreur mesuré de la carte (ID-12), de sorte que l'utilisateur et le simulateur puissent traiter une
  imitation périmée comme l'empreinte qu'elle est plutôt que de lui faire silencieusement confiance.

## 11. Une conception explorée et rejetée : le transport polymorphe QUIC

Cette section consigne une conception de transport concrète qui a été architecturée, soumise à une
équipe rouge, et **rejetée avant qu'aucun mécanisme ne soit engagé**. Elle est conservée, non supprimée,
pour la même raison que le jeu de données d'inférence conserve PS-11/PS-12 et ID-8a : une conception
attaquée et abandonnée est un résultat, et consigner *pourquoi* elle a échoué empêche le projet — et le
prochain lecteur — de la re-proposer. Aucun des `CT-n` ci-dessous n'est normatif ; la conception n'est
pas livrée. Les trois échecs ont été vérifiés contre des sources primaires, non affirmés.

**La conception.** Un transport *polymorphe* dont le polymorphisme est une **sélection sur un petit
ensemble de modèles réels, tels que déployés, de protocoles communs** (jamais une randomisation
octet-par-octet — CT-6 fait déjà de l'aléatoire un signal plus vif), avec la classe de cible d'imitation
choisie pour être **QUIC / HTTP-3** : un protocole de datagrammes à forte population, sur la prémisse que
se cacher dans le troupeau QUIC déjoue l'heuristique d'entropie et que la sélection de modèle par
connexion dérivée d'un secret de pont pré-partagé résiste à l'épinglage de modèle. Le point d'accès
serait une **véritable origine H3** exploitée par l'opérateur, de sorte qu'un sondage actif (CT-5)
rencontre un véritable site web et n'apprend rien de secret (modèle CT-10).

**Pourquoi elle a été rejetée — trois échecs, chacun vérifié :**

- **La justification d'évasion d'entropie est une erreur de catégorie reposant sur une fausse prémisse.**
  Le détecteur de « trafic entièrement chiffré » qu'elle prétendait déjouer (USENIX Security 2023, Wu et
  al.) opère sur le **premier paquet TCP** (un test de popcount bits-par-octet et des règles de préfixe
  ASCII imprimable) ; ce n'est pas un détecteur QUIC, de sorte qu'un transport QUIC ne le déjoue ni n'a
  besoin de le déjouer. Et la sous-prémisse — « le vrai QUIC est déjà à forte entropie, donc nous nous y
  fondons » — est fausse pour la part que lit en premier un classifieur bon marché : la protection
  d'en-tête de QUIC v1 ne masque que les bits de poids faible du premier octet et le numéro de paquet
  (RFC 9001 §5.4), tandis que la **version** à en-tête long (le `0x00000001` fixe en 2026), les octets de
  longueur de l'identifiant de connexion, et la longueur du jeton sont **en clair**, et la charge utile
  du paquet Initial est scellée par AEAD sous une clé dérivée d'un sel **public** et de l'identifiant de
  connexion de destination en clair (RFC 9001 §5.2) — de sorte que tout observateur peut déchiffrer le
  ClientHello. Un Initial QUIC est une **riche surface d'empreinte**, non un mur d'octets aléatoires. La
  véritable menace QUIC est la correspondance d'empreinte de l'Initial / du ClientHello (la famille JA4,
  y compris sa variante QUIC, plus les paramètres de transport), que CT-3 nomme déjà — non l'entropie.

- **Le sélecteur secret survit à un seul paquet.** Dériver le modèle de l'identifiant de connexion de
  destination (DCID) QUIC que le client choisit était impraticable : RFC 9000 §7.2 exige que ce premier
  DCID client soit **« une valeur qui ne peut être prédite »** (le contraire d'une dérivation de clé
  déterministe), d'au moins 8 octets, et le client ne l'utilise **que jusqu'à ce que le serveur
  réponde** — après le premier Initial du serveur (et immédiatement lors d'un Retry, avant même que la
  poignée de main ne s'achève), l'identifiant de connexion est choisi par le serveur. Un sélecteur par
  connexion logé dans un champ que le protocole écrase en un seul aller-retour n'est pas un sélecteur.
  (Un secret pré-partagé donne déjà aux deux parties l'index du modèle ; le router à travers un champ
  observable n'achetait rien et risquait une divergence d'avec le QUIC tel que déployé, qui est elle-même
  une empreinte au titre de CT-8.)

- **QUIC / UDP est la *première* chose qu'un censeur national bloque, et à bas coût.** C'est l'échec
  décisif, car il concerne l'utilisateur exact pour lequel ce réseau existe. La Russie, le 2022-03-04, a
  rejeté **tout** le QUIC international avec un filtre UDP/443 (premier paquet ≥ 1001 octets portant
  l'en-tête de version QUIC v1 → le 4-uplet rejeté pendant 420 s), se restreignant plus tard au filtrage
  QUIC-SNI, toujours actif en 2026 ; l'Iran, lors d'un balayage pré-coupure de 2025, est passé d'un seul
  domaine QUIC bloqué à environ neuf mille (≈ 100 %) via des rejets complets d'Initial-UDP. Parce que
  les navigateurs se replient automatiquement sur TCP, bloquer UDP/443 ne porte presque aucun collatéral
  — c'est donc fait **tôt**. Choisir QUIC échange dès lors une victoire inexistante contre l'heuristique
  d'entropie contre une perte réelle *plus rapide* contre le blocage UDP et la liste blanche de
  protocoles (CT-7b). QUIC n'est pas inutilisable — QUIC v2 déjoue le filtre version-1-seulement de la
  Russie, et le troupeau H3 est réel — mais c'est au mieux **un modèle déclaré-défaisible sur les bases
  de taille de troupeau de CT-9a, là où UDP n'est pas déjà rejeté**, jamais l'ancre. Une imitation
  TCP/HTTP-2 d'une destination autorisée survit à strictement plus des régimes pour lesquels cette partie
  est écrite.

**Trois résidus qui ont survécu à la conception QUIC et qui lient tout futur transport polymorphe, QUIC
ou non :**

- **L'appartenance au troupeau est une propriété de poignée de main, jamais une propriété de flux — et ne
  doit jamais être vendue comme camouflage.** « Se tenir dans le troupeau » cache les octets de la
  poignée de main ; cela ne cache **pas** la forme du flux (séquence de tailles de paquets, temporisation,
  structure de rafales, volume de `n` parts par message), qui reste de forme ScrambNet et est exactement
  ce sur quoi CT-6 / CT-12 classent. Toute affirmation que l'appartenance au troupeau rend un flux
  inobservable est la surenchère de camouflage que CT-15a interdit, dans un nouveau costume.

- **La réponse de sondage par véritable site web n'est pas seulement un coût d'amincissement du vivier
  (CT-10b) ; c'est une nouvelle surface de désanonymisation et une nouvelle surface légale.** Le site
  public d'un opérateur et son canal secret partagent une adresse, un certificat, un point d'accès, de
  sorte que la congestion de charge secrète transforme le site public en oracle de temporisation sur
  l'opérateur (le problème d'identité non-rotatable de BL-18a, récurrent à la couche de transport), et
  exploiter du contenu hébergé réel comporte une exposition à l'abus/au retrait que la posture « transporte
  des paquets, non des opinions » du modèle de menace et d'OPERATORS.md ne couvre pas. Les deux doivent
  être déclarées par toute conception qui répond à un sondage avec un véritable service.

- **La sélection par connexion sur un petit ensemble de modèles est elle-même une empreinte au niveau de
  la population.** Un choix uniforme `1/T` sur `T` modèles ne correspond pas à la distribution — biaisée
  par la part de marché, variant géographiquement et temporellement — des piles clientes réelles, de sorte
  que la *distribution de sélection* — apprenable en agrégeant de nombreuses connexions — devient la
  signature ScrambNet que le polymorphisme était censé supprimer. Une future conception DOIT (MUST)
  pondérer le mélange vers la population réelle et tout de même déclarer le résidu que le mélange pondéré
  est une constante globale à travers les clients, que le mimétisme ne peut refermer.

Le résultat négatif utile est le même que celui que le modèle de menace porte déjà : la contrainte
liante sur l'accessibilité de ce réseau n'est pas le camouflage de poignée de main mais la **découverte
et l'énumération de points d'accès (CT-7 / CT-7a → OP-7)**, à quoi aucun mimétisme de transport ne
répond. Un caméléon parfait arrive tout de même à une adresse qu'un censeur peut apprendre et bloquer en
gros. Telle est la ligne de front d'amorçage, déclarée ouverte.

## 12. Exigences introduites ici

- **CT-1 / CT-2 / CT-3 / CT-4 / CT-5** — déclarez-ce-à-quoi-vous-résistez ; DPI passif ; empreinte TLS
  JA4 (ensembles + GREASE, non l'ordre) ; inspection SNI/ECH ; sondage actif.
- **CT-6 / CT-6a** — classification de flux statistique/entropique/ML passive (l'aléatoire est un
  signal plus vif) ; détection TLS-dans-TLS imbriqué — deux résidus que le mimétisme ne peut refermer.
- **CT-7 / CT-7a / CT-7b** — énumération de points d'accès vs *découverte* de points d'accès (la ligne
  de front d'amorçage OP-7, déclarée ouverte) ; liste blanche de protocoles.
- **CT-8 / CT-9 / CT-9a** — aucune signature statique ; le tapis roulant de dérive uTLS ; préférer une
  cible à forte population pour des raisons d'ensemble d'anonymat, non une promesse économique.
- **CT-10 / CT-10a / CT-10b** — survivre à un sondage avec une couverture réelle (le silence est une
  empreinte) ; le secret pré-partagé est une ligne de pont dont la distribution est OP-7 ; le coût
  amincit le vivier d'opérateurs.
- **CT-11 / CT-11a** — ECH est opportuniste, dépendant du DNS, blocage-ECH-observé, non un plancher ;
  dégrader plutôt que fuir un SNI en clair.
- **CT-12** — le mimétisme ne peut vaincre la forme de flux/l'imbrication/la corrélation ; les réponses
  sont à d'autres couches, jamais l'imitation.
- **CT-15 / CT-15a / CT-15b** — la dispersion multi-couvertures aide la disponibilité, nuit à
  l'inobservabilité, ajoute une surface de corrélation inter-couvertures ; vendez-la comme
  accessibilité, non comme camouflage ; affirmations bornées par les couvertures réellement exécutées.
- **CT-16 / CT-17 / CT-18 / CT-18a** — le plancher ne dépend jamais du transport ; confidentialité ≠
  disponibilité ; aucune affirmation de victoire dans la course aux armements ; le cas terminal
  d'accessibilité nulle énoncé, non caché.
- **CT-19 / CT-20** — posture de transport honnête sur PS-9 ; péremption d'imitation déclarée.

CT-16 et CT-18 sont les deux porteurs : le plancher ne dépend pas du fait de gagner la course du
transport, et la partie ne fait aucune affirmation que la course est gagnée. La couche de transport est
celle sur laquelle le projet s'attend à perdre des rounds, et elle est architecturée de sorte que les
perdre coûte de l'*accessibilité*, jamais de la *confidentialité* — jusqu'au cas terminal où
l'accessibilité est nulle et le secret non livré est toujours un secret (CT-18a). Cassez cette partie en
nommant une capacité de censeur que CT-2…CT-7b manque, une clause qui promet de gagner ou de soutenir la
course aux armements au-delà de CT-18, un endroit où le plancher I-2 est fait pour dépendre de la
réussite d'un transport, ou un moyen par lequel la dispersion multi-couvertures est vendue comme
camouflage au-delà de CT-15a. Telle est l'invitation, dans la voix de la maison.
