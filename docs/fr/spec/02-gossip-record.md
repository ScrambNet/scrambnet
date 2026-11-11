# Spécification ScrambNet — Partie 2 : Enregistrement de gossip

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/02-gossip-record.md)).

**Statut : BROUILLON (DRAFT).** Valeurs homme de paille marquées `(s)`. Les questions de sybil/éclipse sur lesquelles cette
partie s'appuie sont OP-2 et délibérément ouvertes.

## 1. Portée

L'enregistrement de gossip est le descripteur auto-signé par lequel un relais existe. Il n'y a
pas d'annuaire, pas d'autorité, pas d'inscription (I-3) : un relais est l'ensemble des enregistrements
qu'il signe, et la carte du réseau est l'échantillon vérifiable que chaque client détient.

## 2. Format de l'enregistrement

- **GR-1.** Un enregistrement est une carte CBOR canonique (RFC 8949 §4.2.1), d'au plus
  `1024` octets (s) une fois encodée. Les enregistrements plus grands DOIVENT (MUST) être écartés sans être lus.
- **GR-2.** Champs (clés entières ; les clés inconnues DOIVENT (MUST) être ignorées pour la
  compatibilité ascendante, mais sont couvertes par la signature) :

| Clé | Nom | Type | Notes |
|---|---|---|---|
| 0 | `v` | uint | version de format, `1` |
| 1 | `id` | bytes(32) | clé publique d'identité Ed25519 — le nom du relais |
| 2 | `onion` | bytes(32) | clé X25519 pour les poignées de main de circuit ; DOIT (MUST) tourner ≤ 7 jours (s) |
| 3 | `addrs` | array | points d'accès : paires `[transport-id uint, blob bytes]` |
| 4 | `bw` | uint | bande passante soutenue annoncée, ko/s — une *annonce*, voir GR-7 |
| 5 | `created` | uint | temps unix, DOIT (MUST) être arrondi à l'heure inférieure (GR-5) |
| 6 | `expiry` | uint | temps unix, DOIT (MUST) être ≤ `created` + 7 jours (s) |
| 7 | `sig` | bytes(64) | Ed25519 sur l'encodage canonique avec la clé 7 absente |

- **GR-3.** Un relais NE DOIT PAS (MUST NOT) publier d'affirmations géographiques ou juridictionnelles sur
  lui-même. Les clients infèrent l'AS et la juridiction depuis `addrs` avec leurs propres données
  (OP-1) ; une localisation auto-déclarée est une surface d'attaque, non une information.
- **GR-4.** La validité de la signature, le plafond de taille, l'expiration et l'arrondi de l'horodatage DOIVENT (MUST) tous
  être vérifiés avant qu'un enregistrement ne soit stocké ou retransmis ; les échecs sont écartés
  silencieusement — aucune erreur distinguant « malformé » d'« expiré » ne peut être
  observable par l'expéditeur de l'enregistrement.
- **GR-5.** L'arrondi de `created` existe pour empêcher le profilage des relais par dérive d'horloge.
  Les clients DOIVENT (MUST) traiter deux enregistrements de même `id` comme un seul relais et
  ne garder que le `created` le plus frais.

## 3. Échange et échantillonnage

- **GR-6.** Les enregistrements voyagent sur des circuits établis et sur le maillage local
  (Partie 5), portés en appoint dans des lots de taille fixe : un lot de gossip fait `8` enregistrements (s)
  complétés à taille constante, échangés au plus une fois par pair et par `10` minutes (s).
  Un nœud répond à une demande d'échantillon par un échantillon uniforme de ses enregistrements stockés ;
  il NE DOIT PAS (MUST NOT) répondre par un échantillon biaisé par l'identité du demandeur (le
  levier d'éclipse évident).
- **GR-7.** `bw` est une annonce. Les clients DEVRAIENT (SHOULD) vérifier les annonces par sondage aléatoire
  sur des circuits qui ne révèlent pas le sondeur, et DEVRAIENT (SHOULD) pondérer la sélection des chemins
  par la bande passante vérifiée, non annoncée. La conception du sondage est ouverte (OP-2).
- **GR-8 (mélange des sources).** L'échantillon stocké d'un client DOIT (MUST) mélanger des enregistrements de
  classes de sources indépendantes — au minimum : pont par graphe social (à la Lox),
  échange de gossip et sondage direct — et NE DOIT PAS (MUST NOT) permettre à une seule classe de
  dépasser une fraction configurable (homme de paille 1/2) de l'échantillon. C'est la
  défense contre l'éclipse jusqu'à ce qu'OP-2 produise quelque chose de plus fort.
- **GR-9.** Les nouvelles identités sont bon marché par conception (pas d'inscription), aussi rien dans
  cette partie ne peut-il supposer une résistance aux sybils à partir du coût d'identité. Tout mécanisme qui
  a besoin de résistance aux sybils doit l'obtenir de ressources vérifiées (bande passante,
  disponibilité à long terme observée par le client lui-même) ou du graphe social — jamais
  de l'enregistrement seul.

## 4. Amorçage

- **GR-10.** Un client frais DOIT (MUST) pouvoir démarrer depuis une seule ligne de pont hors
  bande (un QR code, une chaîne imprimée, un message d'un ami) contenant
  un enregistrement plus un indice de transport. L'amorçage sans aucun contact est OP-7 et ouvert.

## 5. Le protocole de sondage de bande passante (clôt GR-7)

GR-7 dit que `bw` est une annonce et DEVRAIT (SHOULD) être vérifiée par « sondage
aléatoire sur des circuits qui ne révèlent pas le sondeur », puis déclare la
conception du sondage ouverte. Cette section est cette conception. Le sondage
répond à exactement une question — *quel débit puis-je, moi, ce client, pousser à
travers ce relais en ce moment, sur un circuit qui ne me nomme pas ?* — et il y
répond pour le seul client qui demande. Il n'y a **aucun** chiffre de bande
passante publié, partagé ou faisant autorité : les autorités de bande passante de
Tor sont précisément l'allocateur central que I-3 nous refuse (PS-10, GR-9),
aussi chaque client dérive-t-il son propre chiffre vérifié et pondère-t-il sa
propre sélection de chemins (PS-7) d'après lui.

### 5.1 La mesure, et de quoi elle est une pure fonction

- **GR-11 (la bande passante vérifiée est une auto-mesure par client, jamais un
  chiffre publié).** `[claim-critical]` La bande passante vérifiée d'un client pour
  le relais `R`, notée `vbw(R)`, DOIT (MUST) être calculée comme une fonction
  déterministe d'entrées que le client a observées **lui-même** :
  ```
      vbw(R, epoch) = probe(circuits_through_R, bytes_sent, timestamps_seen)
  ```
  et de rien que ne puisse affirmer un relais, un pair ou un tiers quelconque.
  `vbw` est une variable locale, non une valeur de réseau : deux clients honnêtes
  sondant le même `R` dériveront des `vbw(R)` **différents** (leurs chemins, leur
  congestion, leur instant), et c'est correct — il n'y a pas de vrai scalaire
  « bande passante de `R` » sur lequel s'accorder, seulement *le débit qu'un
  client donné a atteint sur un chemin donné à un instant donné* (GR-18). Un
  client DOIT (MUST) traiter l'annonce `bw` d'un relais non sondé comme le
  **plancher de bande passante par défaut** (PS-7), jamais comme son chiffre ; une
  annonce que le client n'a pas mesurée lui-même porte un poids nul dans la
  sélection.

- **GR-12 (le sondage est un aller-retour scellé sur un circuit — le sondeur n'est
  jamais nommé).** `[claim-critical]` Un sondage DOIT (MUST) être transporté comme
  du trafic de circuit ordinaire : le client construit un circuit dont le **relais
  mesuré `R` est le saut du milieu**, envoie un train borné de cellules en forme de
  paquets de partage (Partie 1 : taille fixe `P = 2048` octets, SP-3) adressées à
  travers `R`, et mesure le débit aller-retour du train tandis qu'il revient sur le
  même circuit. `R` voit une cellule arriver de son prédécesseur et repartir vers
  son successeur — exactement ce qu'il voit pour du vrai trafic relayé — et **ne
  peut pas voir le client** : le sondeur se tient au moins un saut au-delà de la vue
  de `R`, comme dans tout circuit Sphinx (SP-4). Le sondage NE DOIT PAS (MUST NOT)
  utiliser de type de cellule, de drapeau, de longueur ou de cadence qui le
  distingue du trafic utilisateur relayé (I-4, et GR-13 ci-dessous). Un relais qui
  pourrait distinguer un sondage d'une charge utile pourrait réussir le sondage et
  échouer la charge utile ; aussi, par construction, ne peut-on lui en donner la
  possibilité.

```
  LE SONDAGE SUR UN CIRCUIT  (R est mesuré ; le sondeur n'est jamais dans la vue de R)

   client (sondeur)       garde G        relais R  (sous test)        queue T
   ────────────────       ───────        ──────────────────         ──────
        │                    │                  │                      │
        │  construit le circuit  C = [ G , R , T ]  (R est le saut du MILIEU)  │
        │───────────────────▶│                  │                      │
        │     train de N cellules de taille fixe, indiscernables du    │
        │     vrai trafic de paquets de partage relayés (SP-3/SP-4, I-4)│
        │════════════════════╪═════════════════▶│═════════════════════▶│
        │                    │                  │   T renvoie en écho le train │
        │◀═══════════════════╪══════════════════╪══════════════════════│
        │   mesure : bytes_acked / (t_last − t_first)  = l'échantillon  │
        │            de débit de ce sondage pour R, CE chemin, CET instant │
        │                    │                  │                      │
      vbw(R) ← agrégat robuste de nombreux échantillons de ce type dans le temps (GR-16) │

   Ce que R voit :  des cellules de G  →  des cellules vers T.   Identique au transport
   de vrai trafic.  R ne voit PAS « client », ne voit PAS « ceci est un sondage », et
   ne peut pas bien se comporter seulement-quand-observé car il ne peut pas dire qu'il
   est observé.  Le coût est PAYÉ par le sondeur : il envoie N·P octets qu'il ne
   récupérera pas en travail utile (GR-14).  R ne peut pas être amené à inonder une
   victime, car le train revient au SONDEUR, jamais à un tiers nommé par l'attaquant (GR-15).
```

### 5.2 Les cinq propriétés que le sondage doit avoir

- **GR-13 (indiscernabilité — un relais ne peut pas bien se comporter seulement
  quand il est observé).** `[claim-critical]` La propriété anti-triche est
  l'uniformité sur le fil (I-4) : **le trafic de sondage DOIT (MUST) être
  indiscernable octet pour octet et temporisation pour temporisation du vrai trafic
  relayé qu'on demande à un relais de porter**, de sorte que le relais ne puisse pas
  conditionner son relayage à « suis-je en train d'être mesuré ? ». Concrètement,
  les cellules de sondage DOIVENT (MUST) être des paquets de partage de Partie 1
  complets (`P = 2048` octets, SP-3), DOIVENT (MUST) être émises sous la même
  discipline de lotissement/gigue qu'un vrai émetteur utilise (SP-6, SP-9), et NE
  DOIVENT PAS (MUST NOT) porter de marqueur propre au sondage. Un relais qui
  sous-sert le vrai trafic et sur-sert les sondages devrait les distinguer ; I-4 lui
  refuse l'information pour le faire. Le `vbw(R)` mesuré est donc une borne
  inférieure de ce que `R` *relaierait* pour le vrai trafic de ce client, car `R` ne
  peut pas distinguer les deux — ce qui est tout l'intérêt : *attaquez ceci en
  trouvant un bit sur lequel le relais peut se caler.*

- **GR-14 (le sondage coûte au sondeur une quantité bornée, prépayée).** Un seul
  sondage de `R` DOIT (MUST) envoyer au plus `B_probe` octets (homme de paille :
  `B_probe = 1 MiB` étalé sur `≥ τ` secondes, `τ = 4 s` (s)) et DOIT (MUST) être
  limité en débit à au plus un sondage en vol par relais cible et au plus `Q`
  sondages concurrents au total par client (homme de paille `Q = 8` (s)). Le sondeur
  dépense de vrais octets qu'il ne récupère pas en travail utile ; c'est le coût qui
  rend le sondage auto-limitant. Un client NE DOIT PAS (MUST NOT) sonder un relais
  plus souvent qu'une fois par `T_probe` (homme de paille : des heures, pas des
  minutes (s)) — la bande passante change lentement par rapport à la vitesse à
  laquelle une mesure vieillit, aussi un re-sondage fréquent rapporte-t-il peu et
  coûte-t-il linéairement (GR-16).

- **GR-15 (le sondage ne peut pas devenir un amplificateur de DoS).**
  `[claim-critical]` Le relais mesuré NE DOIT (MUST) jamais renvoyer de trafic de
  sondage qu'**au sondeur, sur le même circuit par lequel il est arrivé** — jamais à
  une adresse que les cellules du sondeur pourraient nommer. Parce que le saut de
  queue `T` renvoie le train en écho le long de `C` vers le client qui a construit
  `C`, un sondage est une **boucle fermée** : le travail qu'un sondage induit est
  borné par ce que le sondeur lui-même a envoyé (facteur d'amplification ≤ 1 par
  construction, non par politique), et il n'y a aucun champ dans lequel un attaquant
  pourrait écrire l'adresse d'une victime pour faire inonder celle-ci par `R`. C'est
  la différence structurelle avec toute conception du type « demander au relais
  d'envoyer un flux de test à l'adresse X », qui serait un réflecteur et est
  **interdite** : un sondage NE DOIT PAS (MUST NOT) accepter une destination qu'il ne
  termine pas lui-même. Une implémentation qui laisse le sondage cibler un tiers est
  non conforme.

- **GR-16 (un sondage mesure un chemin-instant ; `vbw` est un agrégat robuste de
  plusieurs).** Un seul sondage est un échantillon d'*un chemin à un instant*,
  contaminé par la capacité propre de la garde et de la queue, par le trafic croisé
  et par la congestion n'importe où sur `C`. Un client DOIT (MUST) donc (a) sonder
  `R` à travers **plusieurs circuits indépendants** (gardes et queues distinctes,
  mélangées par source selon GR-8 là où c'est possible), (b) attribuer à `R` le
  **débit soutenu maximal observé** sur ces circuits au cours d'une fenêtre (le
  maximum, parce que le goulet d'étranglement de tout circuit unique est une borne
  *inférieure* de `R` — le chemin le plus rapide isole le mieux la capacité propre de
  `R`), et (c) traiter le résultat comme une **estimation dont la confiance décroît
  avec l'âge** (homme de paille : demi-vie de quelques époques (s)). `vbw(R)` DOIT
  (MUST) être planchée de façon conservatrice : un sondage unique non corroboré
  compte comme bas, non comme haut (discipline PS-7).

- **GR-17 (les résultats de sondage ne sont pas colportés comme bande passante ;
  seule la discipline est partagée).** Un client NE DOIT PAS (MUST NOT) publier,
  colporter ou accepter d'un pair un scalaire « bande passante vérifiée de `R` » —
  cela reconstruirait l'autorité de bande passante que I-3 interdit (un chiffre
  rapporté par un pair est une annonce pas meilleure que `bw` elle-même, GR-9). Ce
  qui PEUT (MAY) être colporté, c'est l'**atteignabilité/vivacité** d'un relais comme
  une classe de source parmi les classes de GR-8, et un client PEUT (MAY) utiliser
  l'accord d'un pair selon lequel un relais *existe et répond* comme point de vue
  corroborant (du style PS-15), mais le **chiffre de débit que chaque client utilise
  pour la pondération DOIT (MUST) être le sien** (GR-11). Des pairs sybils peuvent
  gonfler *combien* de rapports disent « `R` est rapide », mais ne peuvent pas gonfler
  ce que le propre sondage du client a mesuré — c'est la règle GR-9/PS-10 « ne
  compter que le vérifié » appliquée à la bande passante.

### 5.3 Ce qu'un sondage peut et ne peut pas vous dire (dégrader honnêtement)

- **GR-18 (un sondage mesure le débit, non l'honnêteté, non la localisation, non
  l'identité).** Un sondage répond à *« ce chemin peut-il déplacer des octets ? »* et
  à rien d'autre. Il NE DOIT PAS (MUST NOT) être lu comme une preuve que :
  - **le relais est honnête** — un relais peut relayer le trafic de sondage
    parfaitement et malgré tout journaliser, retarder ou corréler le vrai trafic ;
    le débit est orthogonal à la menace de corrélation garde+sortie (modèle de
    menace), que la *disjonction* des chemins (Partie 3) adresse, non la bande
    passante ;
  - **le relais est là où la carte le dit** — un sondage chronomètre un aller-retour ;
    il ne localise pas `R` dans un AS ou une juridiction (c'est la carte de la
    Partie 8, PS-4, avec sa propre erreur déclarée), et un sondage rapide ne dit rien
    sur la colocalisation (Partie 8 §10) ;
  - **le relais est une seule partie distincte** — un opérateur sybil doté de
    capacité réelle sonde *aussi* vite qu'il l'est, parce qu'il a réellement la bande
    passante (voir §6 : un adversaire bien doté n'est pas un sybil, c'est un adversaire
    réel et coûteux).
  Un client conforme DOIT (MUST) présenter la bande passante vérifiée seulement pour
  ce qu'elle est — une estimation de débit décroissant en fraîcheur, contaminée par
  le chemin, que le client a mesurée lui-même — et NE DOIT PAS (MUST NOT) laisser un
  `vbw` élevé se substituer à la disjonction (Partie 3) ou à la diversité (GR-8) dans
  une quelconque décision de sélection.

---

## 6. Sybil et éclipse, bornés (resserre GR-8/GR-9)

Les identités sont gratuites (GR-9), aussi un adversaire gonfle-t-il le décompte
**brut** d'enregistrements à volonté. Les défenses ci-dessous n'arrêtent pas cela ;
elles bornent ce que le gonflement *achète*, et la borne est la courbe que le
simulateur mesure (§7.1).

### 6.1 La borne d'éclipse par mélange des sources

- **GR-19 (le plafond de GR-8 donne une borne d'éclipse énoncée ; l'hypothèse est
  l'indépendance des classes).** `[claim-critical]` Soit le client mélangeant son
  échantillon à travers `m` classes de sources indépendantes (GR-8 : au minimum pont
  par graphe social, échange de gossip, sondage direct — donc `m ≥ 3`), avec le
  plafond par classe qu'**aucune classe unique ne contribue plus que la fraction
  `f`** de l'échantillon stocké (homme de paille `f = 1/2` (s)). Soit un adversaire
  contrôlant pleinement `a` de ces `m` classes (tout enregistrement livré par une
  classe contrôlée est adversarial) et rien dans les autres. Alors la part de
  l'échantillon du client que détient l'adversaire est bornée par
  ```
        A(a, f)  ≤  min( 1 ,  a · f ).
  ```
  Une **éclipse totale** — l'adversaire fournissant toute la vue du client, de sorte
  que tout relais honnête soit invisible et que la sélection des chemins ne tire que
  des circuits adversariaux — requiert `A = 1`, d'où
  ```
        a  ≥  ⌈ 1 / f ⌉       classes sous contrôle adverse total.
  ```
  Avec l'homme de paille `f = 1/2`, **une éclipse totale requiert que l'adversaire
  possède au moins 2 des ≥3 classes** ; posséder une **seule** classe plafonne
  l'adversaire à `f = 1/2` de l'échantillon et une éclipse totale est
  **structurellement impossible** (les classes honnêtes livrent encore ≥ `1 − f` de
  la vue). C'est la quantité exacte que GR-8 affirmait sans l'énoncer : le plafond
  convertit « éclipse » de « posséder assez de relais » en « posséder assez de
  *classes indépendantes* », ce qui est un problème strictement plus dur, et
  différemment doté en ressources.

- **GR-19a (nommer l'hypothèse, et là où elle échoue).** La borne de GR-19 tient
  **seulement si les classes sont véritablement indépendantes** — si compromettre la
  distribution des ponts par graphe social ne dit rien à l'adversaire sur, et ne lui
  donne aucun contrôle sur, les pairs de gossip ou les cibles de sondage. Elle
  **échoue** précisément quand une partie contrôle plus d'une classe à la fois :
  - un adversaire qui possède **à la fois** le pont par graphe social **et** les pairs
    de gossip contrôle `a = 2` classes et, à `f = 1/2`, atteint `A = 1` — une éclipse
    totale que le plafond n'empêche pas, car le plafond borne *par classe*, et deux
    classes qui sont secrètement une seule partie ne sont pas deux classes ;
  - une défaillance corrélée (un seul hébergeur, une seule juridiction, une seule
    monoculture logicielle derrière deux classes nominales) fait s'effondrer `m` vers
    1 silencieusement.
  Par conséquent la protection du plafond est **exactement aussi forte que
  l'indépendance des classes**, et un client conforme DOIT (MUST) (a) sourcer ses
  classes depuis des origines de confiance manifestement différentes (un pont
  introduit par un ami n'est pas indépendant du gossip si l'ami est le pair de
  gossip), et (b) traiter un échantillon dans lequel les classes *s'accordent trop
  parfaitement* sur une vue inhabituelle comme le même signal d'anomalie que la
  Partie 8 utilise pour la divergence de carte (ID-10) et que la Partie 3 utilise
  pour le pilotage (PS-17) — colportez-le, ne lui faites pas confiance.
  L'indépendance est une **hypothèse que le client doit activement maintenir**, non
  une propriété qu'il obtient gratuitement en comptant les classes.

### 6.2 La borne de sybil

- **GR-20 (les sybils gonflent le décompte brut, jamais les ressources vérifiées ni
  les vraies arêtes).** `[claim-critical]` Parce que les identités sont gratuites
  (GR-9), un adversaire sybil règle le **décompte brut d'enregistrements** à la valeur
  qu'il veut. Deux quantités côté client qu'il **ne peut pas** gonfler bornent les
  dégâts :
  1. **Une bande passante vérifiée qu'il n'a pas.** `vbw` (GR-11) est la propre mesure
     du client ; un sybil de 10 000 identités à bande passante nulle se mesure comme
     10 000 relais de ~0 bande passante vérifiée et porte ~0 poids de sélection
     (PS-7). Pour gagner du *poids*, l'adversaire doit réellement déplacer les octets
     — voir GR-20a.
  2. **De vraies arêtes de graphe social.** Une classe de ponts à la Lox (GR-8)
     transmet la confiance le long d'arêtes *humaines* ; un sybil peut frapper des
     identités mais pas les arêtes qui les introduisent, aussi la classe de graphe
     social n'admet-elle de sybils qu'au rythme où de vraies personnes se portent
     garantes d'eux (ce qui est toute la raison d'être de cette classe).
  La conséquence opérationnelle est **PS-10, désormais quantifiée** : l'estimation de
  taille viable DOIT (MUST) ne compter **que les relais indépendamment vérifiés et la
  diversité d'AS observée**, de sorte que gonfler le décompte brut de `N` à `10N`
  sybils déplace l'estimation de taille vérifiée de **0** (aucun des sybils ne passe
  la vérification), et un client ne peut pas être trompé pour adopter des paramètres
  `n, k` complets dont la diversité est factice. Ce que « ne compter que le vérifié »
  achète, en une ligne : **la taille qui pilote le choix des paramètres est invariante
  sous gonflement sybil** — l'adversaire peut faire *paraître* le réseau arbitrairement
  grand et ne change rien sur quoi un client agit.

- **GR-20a (un adversaire bien doté n'est pas un sybil — c'est un adversaire réel,
  coûteux, accepté).** `[claim-critical]` Le revers de GR-20 est énoncé honnêtement :
  un adversaire qui **a réellement** la bande passante, le cautionnement social et la
  diversité d'AS/de juridiction n'est **pas** vaincu par une quelconque défense anti
  sybil, car il **n'est pas un sybil** — c'est un véritable adversaire à `k` chemins
  qui a payé ses positions. C'est le risque résiduel conçu que le modèle de menace
  accepte déjà (la ligne de l'adversaire à `k` chemins : « monter `n`, `k` à
  convenance »), non une faille de cette partie. Les défenses anti sybil haussent le
  coût de l'adversaire de *gratuit* (frapper des identités) à *de vraies ressources
  proportionnelles à l'influence recherchée* ; elles ne rendent pas et ne peuvent pas
  rendre l'influence inachetable. Un client NE DOIT PAS (MUST NOT) présenter
  « résistant aux sybils » comme « un adversaire doté de ressources réelles ne peut pas
  gagner de position » — le premier est vrai, le second est faux et est une menace
  différente, nommée et acceptée.

---

## 7. Ce que ceci ne résout pas (OP-2 reste ouverte)

**OP-2 n'est pas résolue ici, et aucune exigence ci-dessus ne prétend qu'elle
l'est.** Un allocateur central — l'autorité de bande passante de Tor, l'instantané
signé de Walking Onions — *résoudrait* le sybil et l'éclipse par décret : il
publierait une vue de confiance unique, et les sybils ne pourraient pas s'y injecter
ni un adversaire ne pourrait en fournir à une victime une vue privée. I-3 interdit
cet allocateur, parce que la partie qui peut publier l'unique vue de confiance est
aussi la partie qui peut être contrainte, assignée en justice ou saisie pour en
publier une *empoisonnée*, et un mécanisme de découverte avec ce point unique est le
coupe-circuit que tout le projet refuse. L'ayant refusé, il nous reste une **borne,
non un remède** :

- **Il n'existe pas de mécanisme purement sur-réseau qui rende l'échantillonnage de
  gossip pleinement à l'épreuve du sybil/de l'éclipse.** Chaque défense ci-dessus est
  une *discipline côté client de vérification de ressources ou de mélange des
  sources*, et chacune a une couture déclarée :
  - la borne d'éclipse (GR-19) tient seulement sous l'indépendance des classes, et
    **s'effondre quand une partie possède ≥ `⌈1/f⌉` classes** (GR-19a) — un adversaire
    assez riche pour être l'ami qui vous tend le pont **et** les pairs avec qui vous
    colportez vous éclipse, et le sur-réseau ne peut pas distinguer « deux classes »
    de « une partie portant deux casquettes » ;
  - la borne de sybil (GR-20) arrête le gonflement *gratuit* mais non la position
    *payée* (GR-20a) — la vérification hausse le coût, elle ne le plafonne pas ;
  - le sondage de bande passante (§6) mesure le débit, non l'honnêteté ni la
    localisation (GR-18) — un relais peut réussir haut la main chaque sondage et être
    quand même celui de l'adversaire, et un sybil rapide doté de capacité réelle est
    un adversaire réel (GR-20a). Un sondage clôt la question de *conception* de GR-7 ;
    il ne clôt pas OP-2.
- **L'amorçage sous éclipse est le résidu difficile.** Un client éclipsé dès son
  premier contact (GR-10) ne voit que des classes adversariales, ne mesure que des
  relais adversariaux comme « rapides » et n'entend qu'un accord adversarial — tout
  mécanisme de corroboration de cette partie a besoin d'*un point de vue honnête* pour
  fonctionner, et un adversaire qui fournit le monde entier du client dès le premier
  paquet le lui refuse. C'est la même forme que l'amorçage TOFU de la Partie 8 (ID-8) :
  les défenses **détectent** une mauvaise vue dès qu'une source honnête est atteinte
  et rendent *coûteux* de maintenir un client éclipsé *pour toujours* — elles
  n'**empêchent** pas l'éclipse initiale. « Détecter et rendre coûteuse une éclipse
  permanente », non « empêcher l'éclipse », est l'affirmation honnête, et c'est
  l'affirmation que l'interface énonce.

**Ce que la conception fait, précisément, c'est borner l'attaque selon trois
axes :** la vérification de ressources (GR-11/GR-20 : les sybils gratuits n'achètent
rien), le mélange des sources (GR-19 : l'éclipse a besoin de ≥ `⌈1/f⌉` classes
indépendantes, non simplement de nombreux relais) et le graphe social (GR-20 : les
arêtes ne peuvent pas être frappées). Le résidu qui demeure après les trois est :
**un adversaire doté de ressources réelles, d'un cautionnement social réel à travers
plusieurs classes qui paraissent véritablement indépendantes, et de la capacité de
fournir toute la première vue d'un client frais peut gonfler par sybil une influence
qu'il a payée et éclipser un client qu'il encercle — et le sur-réseau ne peut pas, de
l'intérieur, prouver qu'il est encerclé.** Ce résidu est OP-2, et il est ouvert.

### 7.1 Les bornes sont les courbes du simulateur

Ces exigences sont falsifiables, non rhétoriques : un modèle de sybil/éclipse est en
cours de mesure par `poc/sybil_sim.py` aux côtés du balayage `infer_error` existant de
`network_sim.py` (le simulateur modélise déjà un `gossip_sample` partiel par client —
la vue exacte qu'un adversaire d'éclipse façonne — et sépare déjà la vérité de terrain
de la croyance du client). Les bornes de la conception sont les courbes qu'il DOIT
(MUST) mesurer :

- **la courbe d'éclipse :** fraction d'échantillon de l'adversaire `A` en fonction du
  nombre de classes contrôlées `a`, qui DOIT (MUST) suivre `min(1, a·f)` de GR-19 et
  DOIT (MUST) montrer le coude à `a = ⌈1/f⌉` (éclipse totale) — et DOIT (MUST) montrer
  qu'à `a = 1` la vue honnête ne descend jamais sous `1 − f` ;
- **la courbe de gonflement sybil :** estimation de taille vérifiée (PS-10) en fonction
  du décompte brut de sybils, qui DOIT (MUST) être **plate** — l'affirmation GR-20 selon
  laquelle gonfler le décompte brut déplace l'estimation vérifiée de zéro est exactement
  cette platitude, et une courbe non plate falsifie GR-20 ;
- **l'interaction de churn :** probabilité d'éclipse en fonction du taux de churn
  d'échantillon, puisqu'un client qui ré-échantillonne plus vite rencontre un point de
  vue honnête plus tôt (l'affirmation « détecter, rendre coûteuse une éclipse permanente »
  est un taux, et le simulateur doit en donner un chiffre).

Si le simulateur montre la courbe d'éclipse battant `min(1, a·f)`, ou la courbe de
gonflement sybil montant en pente, la borne est fausse et cette extension est cassée —
attaquez le modèle, puis ce texte. La seule chose qu'on ne peut pas transformer en
courbe est l'éclipse de premier contact d'un client sans aucun point de vue honnête :
cela n'a aucune mesure interne au sur-réseau, car la victime, par définition, ne peut
pas voir au-delà du monde de l'adversaire. C'est le résidu d'OP-2, déclaré, et c'est
pourquoi cette partie dit *borner*, non *résoudre*.

---

## Exigences introduites ici

- **GR-11** — la bande passante vérifiée est une auto-mesure par client (`vbw`), jamais
  un chiffre publié ou partagé ; les annonces non sondées comptent comme basses.
- **GR-12** — le sondage est un aller-retour scellé avec le relais mesuré comme saut du
  milieu ; le sondeur n'est jamais dans la vue du relais.
- **GR-13** — indiscernabilité : le trafic de sondage DOIT (MUST) être identique octet
  et temporisation au vrai trafic relayé (I-4), de sorte qu'un relais ne puisse pas servir
  les sondages et affamer les charges utiles.
- **GR-14** — un sondage coûte au sondeur un budget d'octets borné et prépayé, limité en
  débit par cible et en agrégat.
- **GR-15** — le sondage est une boucle fermée (ne revient qu'au sondeur) ; il ne peut
  nommer aucune destination tierce, aussi ne peut-il pas s'amplifier en réflecteur de DoS.
- **GR-16** — `vbw` est un agrégat robuste sur plusieurs circuits indépendants, prenant le
  débit soutenu maximal, avec une confiance décroissant avec l'âge et un plancher conservateur.
- **GR-17** — les chiffres de débit ne sont jamais colportés comme bande passante ; seule la
  vivacité/atteignabilité est une classe de source partageable — chaque client pondère d'après sa propre mesure.
- **GR-18** — dégradation honnête : un sondage mesure le débit, non l'honnêteté, non la
  localisation, non l'identité distincte.
- **GR-19** — le plafond de GR-8 donne la borne d'éclipse `A ≤ min(1, a·f)` ; une éclipse totale
  a besoin de `a ≥ ⌈1/f⌉` classes contrôlées (≥2 à `f = 1/2`).
- **GR-19a** — la borne suppose l'indépendance des classes et échoue quand une partie possède
  ≥ `⌈1/f⌉` classes ; l'indépendance se maintient, elle n'est pas gratuite.
- **GR-20** — les sybils gonflent le décompte brut d'enregistrements mais jamais la bande passante
  vérifiée ni les vraies arêtes sociales ; l'estimation de taille vérifiée (PS-10) est invariante sous gonflement sybil.
- **GR-20a** — un adversaire bien doté n'est pas un sybil mais un vrai adversaire à `k` chemins,
  coûteux et accepté ; la vérification hausse le coût, elle ne rend pas la position inachetable.

GR-11 et GR-19 sont les deux porteuses : chaque client mesure sa propre bande passante
(pas d'autorité), et le plafond de mélange des sources convertit l'éclipse de « posséder
assez de relais » en « posséder assez de classes indépendantes ». Les deux sont
**bornées, non absolues** — le sondage de GR-11 ne peut pas lire l'honnêteté ni la
localisation (GR-18), et GR-19 s'effondre quand les classes sont secrètement une seule
partie (GR-19a). OP-2 n'est pas résolue : il n'existe pas de mécanisme purement
sur-réseau qui rende l'échantillonnage de gossip pleinement à l'épreuve du
sybil/de l'éclipse, et un client éclipsé dès son premier contact n'a aucun point de vue
honnête pour le détecter. La conception borne l'attaque depuis la vérification de
ressources, le mélange des sources et le graphe social ; elle ne l'élimine pas. C'est le
résidu honnête, et les courbes du simulateur sont là où il est tenu à ses propres
chiffres. Cassez-le de la même manière que le reste de la spécification est cassé :
trouvez un bit de sondage sur lequel un relais peut se caler (défaisant GR-13), une façon
dont le sondage nomme une victime (défaisant GR-15), un sybil qui déplace l'estimation de
taille vérifiée (défaisant GR-20), ou une éclipse qui bat `min(1, a·f)` sous des classes
véritablement indépendantes (défaisant GR-19) — et vous avez cassé cette extension.

## 8. Ce que cette partie ne décide pas

La résistance aux sybils/éclipses au-delà de GR-8/GR-9 (OP-2), le protocole de sondage (GR-7),
l'amorçage sans aucun contact (OP-7). Des issues numérotées existent pour chacun.
