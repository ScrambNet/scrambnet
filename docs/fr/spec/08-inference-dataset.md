# Spécification ScrambNet — Partie 8 : Le jeu de données d'inférence

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/08-inference-dataset.md)).

**Statut : BROUILLON (DRAFT), et un risque de recherche déclaré.** Cette partie décide comment un client obtient la carte IP-vers-AS (et de juridiction grossière) dont la Partie 3 infère (PS-4), sous I-3 — aucune autorité — face à des relais et des hébergeurs de jeux de données qui mentent sur tout, sauf sur ce qu'un hachage ou une signature lie. Les valeurs d'homme de paille sont marquées `(s)`. L'*usage* de la carte pour la vérification de disjonction est OP-1 ; sa *distribution* est l'item de roadmap 2.3.

La décision principale est énoncée au §1 et défendue dans tout le reste. Lisez d'abord le §1 et le §9 (le résidu) : ensemble ils disent ce que cette partie achète et ce qu'elle admet ne pas pouvoir acheter.

## 1. La décision, en deux phrases

- **Il n'y a pas de carte canonique ni d'autorité de carte.** Le jeu de données est un **artefact reproductible, adressé par contenu** que n'importe quelle partie reconstruit octet par octet à partir d'entrées publiques ; deux clients s'accordent non parce qu'ils font confiance à un signataire mais parce qu'ils ont calculé le **même hachage** (ID-1, ID-5). Une racine canonique signée par un ensemble fixe serait une autorité d'annuaire sous un autre nom, et I-3 l'interdit.
- **L'accord se fait par reproduction ; la publication se fait par un journal de transparence en ajout seul que n'importe qui peut écrire ; la confiance à la première récupération est TOFU, déclarée comme telle.** Le journal ne *bénit* pas une carte — il l'horodate et rend l'équivocation détectable (ID-6, ID-7). La première carte d'un nouveau client est un moment de confiance-à-la-première-utilisation que le gossip ultérieur lui permet de **détecter** comme mauvaise, non de **prévenir** (§7).

Ainsi l'issue honnête que la roadmap a signalée est la vraie : **carte TOFU + journal de transparence + gossip d'anomalies, pas une carte canonique.** Tout ce qui suit est la construction qui rend concret « reproduis-la toi-même, et détecte quiconque a menti », et le §9 est le résidu qu'aucune quantité de construction ne retire.

## 2. Portée et le piège que cette partie évite

La Partie 3 (PS-4, PS-5) exige de chaque client qu'il infère l'AS et la juridiction grossière d'un relais *à partir de ses `addrs`*, en utilisant le jeu de données **propre** au client, jamais l'auto-déclaration d'un relais (GR-3). Cette partie porte uniquement sur **d'où vient ce jeu de données et comment deux clients savent qu'ils détiennent le même** sans aucune partie de confiance où que ce soit dans la chaîne — construction, publication ou amorçage.

Le piège est subtil et doit être nommé : la conception « sans confiance » la plus facile est un instantané canonique signé publié par un petit ensemble de mainteneurs. C'est exactement l'autorité Walking-Onions que ce projet s'est refusée pour les relais (portée GR-1), désormais réintroduite en contrebande pour la géographie. Un signataire de carte capable de livrer discrètement une carte qui étiquette à tort un bloc d'AS peut faire *paraître* disjoints, à chaque client, des relais co-localisés de l'adversaire — une éclipse à granularité géographique qui défait la Partie 3 aussi sûrement que le ferait un mauvais annuaire de relais. Donc l'ensemble des signataires est la menace, et la conception ne doit pas en avoir un doté de ce pouvoir.

- **ID-1 (aucune autorité de carte). [normatif]** Aucune étape de l'obtention, de la validation ou de la mise à jour du jeu de données NE DOIT (MUST NOT) exiger de faire confiance au fait qu'une partie particulière a produit, signé ou béni la carte ; de façon équivalente, l'obtention et la validation de la carte DOIVENT (MUST) être possibles en n'utilisant que des substituts non fiables. Les seules opérations de confiance sont : (a) recalculer un hachage, et (b) reconstruire l'artefact à partir d'entrées publiques et comparer. Tout élément de conception qui ne peut être remplacé par un substitut non fiable effectuant (a) ou (b) est un défaut sous I-3 et DOIT (MUST) être retiré ou déclaré au §9.

## 3. Ce qu'est la carte

- **ID-2 (forme de l'artefact).** Le jeu de données est un unique artefact compressé, la **carte**, contenant, pour l'espace IPv4 et IPv6 :
  - une table **préfixe-IP → AS-d'origine** (recherche par correspondance de préfixe le plus long), et
  - une table **AS → juridiction-grossière**, où « juridiction » est une étiquette **au niveau du pays** dérivée de l'allocation RIR, délibérément grossière — une granularité plus fine est du bruit que cette partie ne prétendra pas résoudre (§9).
  La carte porte un en-tête auto-descriptif : version de format `1`, l'**epoch** de l'instantané (ID-4), le manifeste exact des entrées (ID-3), et la version de l'outil de construction. L'artefact est adressé par `H = BLAKE2s(artifact)` (le hachage de suite, Partie 0) ; `H` est le seul nom de la carte. Il n'y a aucune chaîne de version lisible par un humain à laquelle on pourrait faire confiance à la place de `H`.
- **ID-2a (la recherche est totale).** Toute recherche DOIT (MUST) retourner soit un `(AS, juridiction)` concret, soit la valeur explicite **`unknown`**. `unknown` est une réponse de première classe, pas une erreur, et la Partie 3 (PS-5) la traite déjà de façon conservatrice (`unknown` partage avec tout). La carte NE DOIT PAS (MUST NOT) deviner pour éviter un `unknown` ; une réponse fabriquée est pire qu'une lacune admise, car elle défait silencieusement PS-5.

## 4. Comment la carte est construite (de façon reproductible, à partir d'entrées publiques)

La construction est une **fonction pure d'entrées publiques nommées vers un artefact identique octet par octet**. Le déterminisme est tout l'enjeu : si deux parties honnêtes peuvent diverger, l'égalité de hachage (ID-5) cesse de signifier « même carte » et la conception s'effondre, nécessitant une autorité pour départager.

```
  ENTREES PUBLIQUES (épinglées par hachage de contenu dans le manifeste, ID-3)
  ┌────────────────────────┐   ┌────────────────────────┐
  │ RouteViews + RIPE RIS  │   │ 5 fichiers délég. RIR  │
  │ dumps BGP MRT RIB      │   │ (AS → pays)            │
  │ (préfixe → AS-origine) │   │                        │
  └───────────┬────────────┘   └───────────┬────────────┘
              │     epoch = dernier dump ≤ limite 00:00 UTC (ID-4)
              └───────────────┬───────────────┘
                              ▼
          ┌───────────────────────────────────────┐
          │  CONSTRUCTION DETERMINISTE (fn pure)  │
          │  ordre fixe (ID-4a), départage        │
          │  fixe (ID-4b), pas d'entrées          │
          │  flottantes (ID-4c), conteneur        │
          │  canonique (ID-4d)                    │
          └───────────────────┬───────────────────┘
                              ▼
                      artefact carte
                              │
                              ▼
                   H = BLAKE2s(artifact)   ← le SEUL nom de la carte (ID-2)

  Alice ─ mêmes entrées ─▶ H_A         Deux parties honnêtes qui épinglent les
  Bob   ─ mêmes entrées ─▶ H_B         mêmes entrées obtiennent H_A == H_B.
                                       L'accord est l'égalité de hachage
                                       (ID-5), non la confiance en un
                                       signataire. La reproduction est l'arbitre.
```

- **ID-3 (entrées publiques, épinglées par le contenu). [normatif]** La carte DOIT (MUST) être construite uniquement à partir d'entrées qui sont publiques, reproductibles, et elles-mêmes épinglées par contenu dans le manifeste de l'artefact par leurs propres hachages :
  - **Tables de routage BGP** pour l'AS d'origine : les collecteurs du projet **RouteViews** et les collecteurs **RIPE RIS** (dumps MRT `RIB`). Ce sont les archives BGP publiques, multi-points-d'observation, standard ; utiliser plusieurs collecteurs des deux projets est en soi une mesure de diversité (la vue d'aucun collecteur unique ne fait autorité, ID-3a).
  - **Statistiques de délégation RIR** pour la correspondance AS → pays : les fichiers **delegated-extended** publiés par les cinq RIR (ARIN, RIPE NCC, APNIC, LACNIC, AFRINIC). Ils donnent les codes-pays d'allocation pour les numéros d'AS et les blocs d'adresses sans que personne s'auto-déclare.
  Le manifeste DOIT (MUST) lister chaque fichier d'entrée par hachage de contenu indépendant de l'URL et par son horodatage déclaré à la source, de sorte que les entrées — non un serveur — définissent la construction. Une partie reconstruit en récupérant les entrées avec ces hachages depuis **n'importe quel** miroir (I-3 : la source est remplaçable ; les octets sont épinglés).
- **ID-3a (résolution d'origine multi-points-d'observation).** L'AS d'origine d'un préfixe DOIT (MUST) être résolu à travers **tous** les collecteurs du manifeste par une règle fixe (ID-4b), non à partir d'un seul collecteur. Un préfixe vu avec des origines conflictuelles entre points d'observation est résolu de façon déterministe et, là où le conflit est réel (MOAS — multiple-origin AS), enregistré comme un **ensemble**, que la Partie 3 traite comme « possiblement n'importe lequel de ceux-ci », c.-à-d. partagé de façon conservatrice (§9). La carte NE DOIT PAS (MUST NOT) en choisir un silencieusement.

### 4.1 Risques de déterminisme et comment la construction les épingle

Chaque risque ci-dessous est un endroit où deux constructeurs honnêtes pourraient produire des octets différents. La procédure de construction DOIT (MUST) éliminer chacun ; une construction qui ne le fait pas est non conforme parce qu'elle ne peut pas soutenir ID-5.

- **ID-4 (epoch d'instantané — moment du dump). [normatif]** Les données BGP et RIR changent continuellement, donc « le dump actuel » n'est pas une fonction. La construction DOIT (MUST) épingler une seule **limite d'epoch** : un instant UTC sur une cadence fixe (homme de paille : l'instantané de **00:00 UTC** sur une cadence **hebdomadaire (s)** — les commits de la Partie 0 utilisent déjà UTC), et DOIT (MUST) utiliser, pour chaque collecteur/RIR du manifeste, le **dernier dump dont l'horodatage déclaré à la source est ≤ la limite d'epoch**. Deux constructeurs visant le même epoch sélectionnent donc les mêmes fichiers d'entrée quel que soit le moment où ils s'exécutent. L'epoch est dans l'en-tête de l'artefact (ID-2) et dans la préimage de `H`.
- **ID-4a (ordonnancement).** Toutes les tables DOIVENT (MUST) être émises dans un **ordre total fixe** : préfixes triés par (famille d'adresses, adresse réseau numérique, longueur de préfixe) ; entrées d'AS par ASN numérique ; juridictions par leur chaîne de code-pays fixe. Aucun ordre d'itération de map, ordre de table de hachage ou ordre de fichier d'entrée ne peut atteindre la sortie.
- **ID-4b (le départage est spécifié, non défini par l'implémentation). [normatif]** Chaque endroit où la donnée est ambiguë DOIT (MUST) avoir une règle écrite dans cette partie, sans aucun « choisis-en un » laissé à l'implémenteur :
  - *AS d'origine entre collecteurs :* prendre l'ensemble d'origines observé ; s'il s'agit d'un seul AS, l'émettre ; s'il y en a plusieurs (MOAS), émettre l'ensemble complet trié par ordre croissant. Ne jamais réduire un MOAS à un seul AS par popularité — c'est une devinette (§9).
  - *Préfixes chevauchants :* la sémantique de correspondance de préfixe le plus long est préservée en stockant tous les préfixes ; c'est la recherche, non la construction, qui résout la spécificité.
  - *Conflit AS-vers-pays entre RIR :* si les fichiers de délégation sont en désaccord sur le pays d'un AS, émettre `unknown` pour la juridiction de cet AS. Un désaccord entre registres publics est exactement un cas que la carte ne doit pas résoudre par décret.
- **ID-4c (entrées flottantes interdites).** La construction NE DOIT PAS (MUST NOT) consulter une entrée absente du manifeste — pas de DNS en direct, pas de WHOIS au moment de la construction, pas de base de géolocalisation sous une licence qui interdit la redistribution ou n'est pas reproductible, pas de flux commercial de renseignement IP. Chaque octet de sortie se trace jusqu'à une entrée publique hachée. (Cela exclut les flux commodes-mais-invérifiables ; leur exactitude ne vaut pas l'autorité qu'ils réintroduisent.)
- **ID-4d (conteneur canonique).** La compression et l'encadrement de l'artefact DOIVENT (MUST) être déterministes (codec fixe, niveau fixe, pas d'horodatages ni de noms de fichiers dans les métadonnées du conteneur). La construction est spécifiée assez strictement pour qu'un outil de construction conforme soit lui-même reproductible (roadmap 4.2), et un **vecteur de test de carte** inter-implémentations (un manifeste d'entrées → `H` attendu) DOIT (MUST) exister pour qu'une seconde implémentation puisse prouver qu'elle construit l'artefact identique (se rattache à la roadmap 3.2).

## 5. Comment deux clients s'accordent sur le fait qu'ils détiennent la même carte

- **ID-5 (l'accord est l'égalité de hachage, rien de plus). [normatif]** Deux clients détiennent la même carte **si et seulement si** leurs hachages d'artefact `H` sont égaux. La comparaison est un test d'égalité sur 32 octets ; elle ne nécessite ni signataire, ni quorum, ni autorité. Les clients diffusent `H` par gossip (ID-8) ; un `H` égal est une preuve de la même carte, un `H` inégal est une preuve qu'ils diffèrent et DOIT (MUST) être signalé à l'utilisateur comme une **divergence** (ID-9), jamais réconcilié silencieusement vers l'un ou l'autre côté.
- **ID-5a (la reconstruction est l'arbitre).** Quand deux clients détiennent des `H` différents pour le même epoch, le litige est résoluble par **n'importe qui**, sans appel à une autorité : reconstruire à partir des entrées du manifeste (ID-3) et voir quel `H` les entrées publiques produisent réellement. Une carte dont le `H` ne peut être reproduit depuis son manifeste déclaré n'est, par définition, pas la carte de ces entrées, et DOIT (MUST) être rejetée (ID-5b). C'est la propriété qui permet au système de n'avoir aucune autorité : *la vérité est la reproductibilité, non la signature.*
- **ID-5b (rejeter l'irreproductible).** Un client qui a les entrées (ou les récupère) et constate que `H ≠ BLAKE2s(rebuild(manifest))` DOIT (MUST) écarter cette carte et DEVRAIT (SHOULD) diffuser l'écart par gossip comme une anomalie (ID-10). Un client sans la bande passante pour reconstruire PEUT (MAY) accepter une carte sur la base de termes TOFU/consensus (§6, §7) mais DOIT (MUST) la suivre comme **non vérifiée** jusqu'à ce que lui (ou un pair avec qui il s'accorde ensuite) reconstruise.

## 6. Le journal de transparence (et pourquoi il n'est pas l'autorité)

L'égalité de hachage indique à deux clients qu'ils *diffèrent* ; elle ne défend pas en soi contre un adversaire qui alimente **différents** clients avec **différentes** cartes en gardant chaque client cohérent en interne — une **attaque à vue dédoublée (équivocation)**. Le journal de transparence existe pour exactement cette menace et pour rien de plus.

```
  L'ATTAQUE A VUE DEDOUBLEE, ET COMMENT LE GOSSIP LA PREND

  Un journal hostile tente de montrer deux vues qui ne se rencontrent jamais :

     journal ─racine X (carte H_good)─▶  Alice  « ma carte est corroborée »
             └racine Y (carte H_bad )─▶  Bob    « ma carte est corroborée »

  Chaque client, seul, voit une histoire cohérente. Mais les racines sont
  diffusées par gossip sur le canal GR-6 (ID-7a), donc un troisième client
  Carol les entend TOUTES DEUX :

        Alice ──racine X──┐
                          ├──▶  Carol exige une PREUVE DE COHERENCE
        Bob   ──racine Y──┘     entre X et Y.
                               Si X et Y ne sont pas des extensions d'un
                               seul arbre en ajout seul, la preuve ECHOUE :
                               ✗  preuve cryptographique que le journal a
                                  équivoqué
                                  → journal marqué hostile, gossipé (ID-10)

  Le journal ne dit jamais quelle carte est BONNE — la reproduction le fait
  (ID-5a). Il rend seulement détectable le mensonge à plusieurs à la fois.
  N'importe qui peut ajouter (ID-7, sans permission), donc le journal est
  un tableau d'affichage, non une autorité — ce qui le tient à l'écart de I-3.
```

- **ID-6 (ce qu'est le journal).** Le journal est un **arbre de Merkle en ajout seul** (structure RFC 6962 / Certificate-Transparency : un arbre de Merkle sur une séquence de feuilles, avec des preuves d'inclusion et des preuves de cohérence entre deux tailles d'arbre). Chaque **feuille** est une annonce de carte : `(epoch, H, input-manifest-hash)`. L'état du journal est résumé par sa **tête d'arbre signée** — ici, un **hachage de racine** à une taille d'arbre. Le journal prouve deux choses cryptographiquement : qu'un `H` donné **est inclus** (preuve d'inclusion) et que le journal **n'a fait que croître, sans jamais réécrire l'histoire** (preuve de cohérence). Il ne prouve rien quant à savoir si `H` est une *bonne* carte — c'est la reproduction (ID-5a) qui le fait.
- **ID-7 (qui peut ajouter — sans permission, donc ce n'est pas une autorité). [normatif]** **N'importe qui** PEUT (MAY) ajouter une feuille annonçant une carte qu'il a construite ; il n'y a pas d'appendeur privilégié, pas de liste d'autorisation, pas d'ensemble de signataires dont la signature rend une carte officielle. Le journal n'est donc **pas** la chose à laquelle on fait confiance — c'est un **tableau d'affichage témoigné, inviolable en apparence (tamper-evident)**. Son seul pouvoir est de rendre l'équivocation *détectable* ; il n'a **aucun pouvoir de choisir la carte**, ce qui le tient à l'écart de l'interdiction I-3. Un journal qui filtrerait les ajouts derrière un ensemble de signataires SERAIT l'autorité d'annuaire que I-3 interdit, et une telle conception est non conforme (ID-1).
- **ID-7a (détection d'équivocation via racines diffusées par gossip). [normatif]** La défense contre une vue dédoublée n'est **pas** de faire confiance à l'opérateur du journal ; c'est de **diffuser par gossip les têtes d'arbre signées du journal sur le canal de gossip GR existant** (GR-6) et d'exiger des **preuves de cohérence** entre deux racines quelconques qu'un client voit. Si un journal présente jamais deux têtes d'arbre qui ne sont pas des extensions cohérentes l'une de l'autre — la signature de l'équivocation — tout client qui observe les deux (directement ou via une racine diffusée par un pair) détient une **preuve cryptographique** que le journal a menti, et DOIT (MUST) traiter ce journal comme hostile (ID-10). Comme les racines sont diffusées largement (GR-6 mélange les sources, GR-8), un journal ne peut pas montrer longtemps la racine X au client A et la racine Y au client B sans qu'un client détienne les deux et le prenne en flagrant délit.
- **ID-7b (plusieurs journaux, aucun canonique). [normatif]** Il n'y a **pas de journal unique.** Les clients DOIVENT (MUST) prendre en charge **plusieurs journaux indépendants** et ne traiter une carte comme corroborée par les journaux que si elle apparaît, avec des racines diffusées cohérentes, dans un quorum configurable des journaux que le client surveille (homme de paille : **≥2 des journaux de son ensemble (s)**). Cela supprime le dernier point unique : aucun opérateur de journal unique n'est porteur, et l'ensemble de journaux d'un client — comme son échantillon de relais — est divers et remplaçable (justification GR-8 appliquée aux journaux). Un journal qui s'éteint est contourné, exactement comme l'est un relais qui s'éteint.
- **ID-7c (le journal stocke des engagements, non la carte).** Les feuilles portent `(epoch, H, manifest-hash)` — des dizaines d'octets — jamais l'artefact. La carte elle-même est récupérée de façon adressée par contenu par `H` depuis n'importe quel miroir ou pair (ID-8) ; le journal atteste seulement *quelles* valeurs `H` ont été annoncées et *quand*, de sorte que le stockage du journal reste trivial et qu'aucun journal ne devienne le goulot d'étranglement de la distribution.

## 7. Le paradoxe de l'amorçage, énoncé honnêtement

Un nouveau client n'a pas d'échantillon de relais qu'il puisse évaluer ni de carte antérieure ; il doit récupérer sa **première** carte par des chemins dont il **ne peut pas encore vérifier** la disjonction (cette vérification a besoin de la carte même qu'il récupère). C'est une dépendance circulaire authentique, et cette partie ne prétend pas la briser.

```
  LA PREMIERE CARTE EST CONFIANCE-A-LA-PREMIERE-UTILISATION (ID-8) —
  ET SES DEGATS SONT BORNES

  nouveau client ──▶ récupère la 1re carte par des canaux encore inévaluables
                   │
                   ▼
        ┌───────────────────────────┐
        │  état : NON-VERIFIE-TOFU   │  UI : « vous faites confiance à votre
        │  (montré à l'utilisateur)  │       première carte ; pas encore
        └─────────────┬─────────────┘        corroborée »
                      │  au fil des epochs suivants, SOIT :
         ┌────────────┴─────────────┐
         ▼                          ▼
   reconstruire d'entrées     gossip racines + H des pairs
   (ID-5a) : H concorde ?     accord au-dessus du seuil ?
         │                          │
    oui ─┴─ non                oui ─┴─ non (continue de diverger)
     ▼       ▼                  ▼        ▼
  VERIFIE  ANOMALIE          VERIFIE   ANOMALIE gossipée (ID-10),
           (ID-5b,10)                  utilisateur averti (ID-8b)

  Même une première carte PLEINEMENT adversariale est bornée (ID-8a) :
    1. le plancher I-2 reste intact, MAIS une carte d'*orientation* peut
       manœuvrer l'adversaire au-delà de k (effondrer le vivier honnête,
       PS-12) -> le contenu PEUT tomber pour une carte non vérifiée au-dessus
       d'un seuil de possession de ~15 %. Pas seulement des métadonnées. Borné
       par la marge k/n + les défenses PS-12, non par « impossible ».
    2. temporaire + détectable — l'adversaire doit éclipser le client POUR
       TOUJOURS pour la garder cachée (c'est OP-2, non une faiblesse nouvelle).
    3. infalsifiable — l'adversaire ne peut faire que des entrées publiques se
       reconstruisent vers un mauvais H. Une reconstruction, ou un pair honnête
       qui l'a faite, converge vers la vérité.
```

- **ID-8 (l'amorçage est confiance-à-la-première-utilisation, déclarée). [normatif]** La première carte qu'un nouveau client obtient est une décision **TOFU**. Le client DOIT (MUST) l'obtenir par autant de canaux **indépendants** qu'il en a (homme de paille : la ligne de pont hors-bande de GR-10, plus deux miroirs publics ou plus atteints via des réseaux distincts (s)), DOIT (MUST) exiger le **même `H`** de tous avant une acceptation provisoire, et DOIT (MUST) enregistrer la carte comme **non-vérifiée-TOFU** jusqu'à ce que, soit (a) il reconstruise à partir des entrées (ID-5a), soit (b) il accumule des racines diffusées cohérentes et un accord de `H` entre pairs (ID-7a, ID-9) au-dessus d'un seuil de confiance. Le client DOIT (MUST) faire remonter cet état : *vous faites confiance à votre première carte ; elle n'a pas encore été corroborée.*
- **ID-8a (borne sur ce qu'une mauvaise première carte rapporte à l'adversaire). [normatif]** Un adversaire qui contrôle toute la première récupération d'un nouveau client peut lui remettre une carte qui étiquette à tort des AS de sorte que des relais co-localisés paraissent disjoints. La borne sur les dégâts est triple et DOIT (MUST) être préservée par la conception :
  1. **Le plancher I-2 lui-même reste intact ; mais une carte hostile PEUT atteindre le contenu par orientation.** Le plancher de Shamir en dessous de `k` est mathématique et une mauvaise carte ne peut l'abaisser. Ce qu'une mauvaise carte *peut* faire — et ceci corrige une surestimation antérieure — est de **manœuvrer l'adversaire au-delà de `k`** : une carte qui donne aux relais co-localisés de l'adversaire des AS fictifs distincts et donne aux relais honnêtes des AS fictifs entrant en collision effondre le vivier de candidats honnêtes et oriente la sélection disjointe par AS vers `≥ k` circuits adverses de façon déterministe (la construction complète et ses défenses sont **PS-12** ; démontré face au simulateur, ~100 % de rupture de contenu à ~15 % de possession). Donc une mauvaise carte n'est **pas** une attaque de métadonnées uniquement : pour un client qui a accepté une carte non vérifiée et ne peut pas encore reconstruire, le plancher de contenu peut tomber. La borne honnête est donc conditionnelle, non absolue : une mauvaise carte atteint le contenu **seulement** quand l'adversaire possède déjà assez de l'échantillon *atteignable* du client pour dominer le vivier post-effondrement (territoire de seuil, PS-12) **et** que les défenses de PS-12 ne sont pas appliquées. Une inexactitude aléatoire (du bruit) érode toujours la liaison bien plus vite que le contenu ; une carte *choisie* non. Les affirmations 2 et 3 ci-dessous sont ce qui garde même ceci borné.
  2. **Elle est temporaire et détectable, non permanente.** À l'instant où le client diffuse sa racine/`H` (ID-9) ou reconstruit (ID-5a), une carte qu'aucun pair honnête ni entrée publique ne corrobore ressort. L'adversaire doit maintenir le client éclipsé **à jamais** pour garder la mauvaise carte non exposée — ce qui est le problème d'éclipse OP-2, non une nouvelle faiblesse que cette partie introduit.
  3. **Elle ne peut pas falsifier la reproduction.** L'adversaire peut livrer un mauvais `H`, mais il ne peut pas faire que les entrées publiques se reconstruisent vers ce `H` (ID-5a). Un client qui reconstruit un jour, ou qui rencontre un jour un pair qui l'a fait, converge vers la vraie carte.
- **ID-8b (détecter, ne pas prétendre prévenir). [normatif]** Cette partie fournit une **détection d'un mauvais amorçage après coup**, non une prévention de celui-ci. Un client conforme NE DOIT PAS (MUST NOT) présenter une carte TOFU comme vérifiée, DOIT (MUST) la réévaluer au fur et à mesure du gossip et (optionnellement) accumuler des reconstructions, et DOIT (MUST) avertir si la corroboration n'arrive pas dans une fenêtre configurable (homme de paille : quelques epochs (s)). « Nous ne pouvons pas prévenir une mauvaise première carte ; nous rendons coûteux, et à terme impossible, de la garder non détectée » est l'affirmation honnête, et c'est l'affirmation que l'UI énonce.

## 8. Vivre avec : gestion du rafraîchissement et de la divergence

- **ID-9 (fraîcheur de la carte et gossip).** Les clients DOIVENT (MUST) se rafraîchir vers la carte de l'epoch courant (cadence ID-4) et DOIVENT (MUST) diffuser par gossip leur `(epoch, H)` courant et les racines de journal qu'ils détiennent dans les lots GR-6, sous réserve du mélange de sources GR-8 afin qu'aucune classe unique de pair ne puisse dominer la vue d'un client sur quelle carte est courante (la même défense anti-éclipse, réutilisée). Un client NE DOIT PAS (MUST NOT) pondérer une carte par le nombre de pairs qui la rapportent *avant* d'appliquer la règle « ne compter que les sources vérifiées indépendamment » de GR-8/PS-10 — un sybil ne peut pas voter une mauvaise carte dans le consensus par le seul nombre (se rattache à OP-2).
- **ID-9a (la divergence est montrée, non cachée).** Quand le `H` d'un client diffère d'un quorum corroboré (ID-7b) pour le même epoch, il DOIT (MUST) traiter sa propre carte comme suspecte, tenter une reconstruction ou une re-récupération, et signaler la divergence à l'utilisateur dans la surface d'honnêteté existante de la Partie 3 (PS-9) : *votre vue de la géographie du réseau est en désaccord avec celle de vos pairs ; les jugements de disjonction peuvent être erronés.* Le silence ici laisserait une éclipse-géographie courir sans être vue.
- **ID-10 (gossip d'anomalies). [normatif]** Trois événements sont des **anomalies** que tout client DOIT (MUST) diffuser par gossip quand il les détecte, car ce sont les signatures observables des attaques que cette partie ne peut pas prévenir, seulement faire remonter : (a) un `H` qui échoue à la reproduction depuis son manifeste (ID-5b) ; (b) un journal qui présente des racines incohérentes, c.-à-d. une équivocation prouvée (ID-7a) ; (c) une divergence `H` persistante face à un quorum corroboré (ID-9a). Le gossip d'anomalies est le signal immunitaire du réseau ; un client NE DOIT PAS (MUST NOT) le supprimer pour paraître en bonne santé.

## 9. La couture de fusion avec la gouvernance des mises à jour (OP-8 / item 4.1)

Les publicateurs de racines de la carte et les signataires de publication logicielle semblent pouvoir n'être qu'un seul mécanisme. **Position : les garder séparés en confiance, même s'ils partagent l'outillage.** Le raisonnement est qu'ils ont des **formes de confiance opposées** :

- **ID-11 (la confiance en la carte est la reproduction, non la signature). [normatif]** On fait confiance à la carte parce qu'elle **se reconstruit à partir d'entrées publiques** (ID-5a) ; sa correction ne repose **pas** sur *qui* l'a publiée. Un binaire de publication, en revanche, est digne de confiance parce qu'il **se reconstruit à partir de sources publiques** (constructions reproductibles, roadmap 4.1/4.2) — également de la reproduction, également pas de la signature. Donc l'*ancre de confiance* est la même — **la reproductibilité, jamais l'identité de l'auteur** — et le projet DOIT (MUST) faire passer les deux par elle. Mais les **ensembles de signataires/appendeurs DOIVENT (MUST) rester distincts** : lier les appendeurs du journal de la carte aux signataires de publication créerait une liste unique dont la compromission empoisonne *à la fois* l'inférence géographique *et* le logiciel, c.-à-d. exactement la cible concentrée de coercition que l'item 4.1 est conçu pour éviter. Le journal de la carte est sans permission (ID-7) ; le processus de publication peut avoir un ensemble de signataires nommé (pseudonyme) qui ne fait que *localiser* une construction qu'il ne peut pas falsifier. Les fusionner échange l'absence de permission de la carte contre la liste du processus de publication — la mauvaise direction.
- **ID-11a (un outillage partagé convient ; une autorité partagée non).** Les deux PEUVENT (MAY) réutiliser la même construction de journal de transparence (ID-6) et le même canal de gossip (GR-6) — partager un *mécanisme* ne coûte rien. Ce qu'ils NE DOIVENT PAS (MUST NOT) partager est un ensemble de parties dont la signature est porteuse pour les deux, car cet ensemble serait l'interrupteur de coupure que I-3 interdit, désormais capable de faire basculer à la fois la carte et le code.

## 10. Ce que cette partie ne résout pas (le résidu déclaré)

Cette partie fait que deux clients honnêtes s'accordent de façon prouvable ou détectent de façon prouvable qu'ils diffèrent. Elle ne rend **pas** la carte *vraie*. L'écart entre « la carte sur laquelle chaque client honnête s'accorde » et « où les relais se trouvent physiquement » est le résidu, et il est réel :

- **La co-localisation derrière des préfixes disjoints est indétectable ici.** Un adversaire qui exploite des relais dans un seul centre de données tout en annonçant un espace d'adresses que les données publiques BGP/RIR attribuent à des AS **différents** sera étiqueté disjoint par la carte **correcte**. Aucune construction reproductible de données publiques ne peut voir au travers d'une annonce BGP d'apparence véridique jusqu'au rack derrière elle. C'est énoncé dans le point le plus profondément honnête de la roadmap et cela tient : **depuis l'overlay vous vérifiez la cohérence face à un jeu de données à confiance bornée, non une vraie disjonction.** Pour ce cas *passif* — une carte correcte qui se trouve simplement mal étiqueter des relais co-localisés — l'attaque est métadonnées/liaison, car la carte honnête n'effondre pas le vivier honnête. (Le cas *actif*, une carte choisie pour l'effondrer, est pire et atteint le contenu : PS-12 et le résidu d'orientation de contenu ci-dessous.) Le travail est de borner ce que l'adversaire gagne, non de prétendre l'escamoter.
- **BGP est par endroits authentiquement ambigu.** Les préfixes MOAS (un préfixe légitimement originé par plusieurs AS), les **AS frères** sous un seul opérateur (ASN distincts, une seule partie contrôlante — la carte voit deux AS là où la réalité de disjonction en est un), et l'**anycast** (un préfixe, de nombreux sites physiques) ne sont pas des bugs de jeu de données ; ils sont le territoire. La carte les gère de façon conservatrice (ID-3a, ID-4b : MOAS → ensemble, conflit de registre → `unknown`), ce qui coûte de la disponibilité (plus d'`unknown` ⇒ plus de repli, PS-11) plutôt que de la sécurité. La détection des AS frères est explicitement **hors de portée** d'une construction BGP/RIR pure et est laissée comme un angle mort déclaré : deux AS frères sont comptés comme disjoints alors qu'ils ne le sont pas.
- **La juridiction est grossière par décision.** Les étiquettes au niveau du pays dérivées des RIR sont le plancher de résolution auquel cette partie s'engage. Un raisonnement juridictionnel plus fin (blocs de coopération juridique, réalité de l'entraide judiciaire) n'est délibérément **pas** encodé — ce serait un jugement de valeur qu'aucune construction reproductible ne peut faire sans importer une opinion de confiance, ce que ID-1 interdit.
- **Une carte adversariale peut atteindre le contenu, pas seulement les métadonnées.** Le résidu de co-localisation ci-dessus est une erreur *passive* (la carte correcte se trouve mal étiqueter). Une carte *activement choisie* est pire : elle peut orienter la sélection disjointe par AS vers `≥ k` circuits adverses et rompre le contenu, pas seulement la liaison (PS-12, qui porte les défenses). Cette partie ne **prétend pas** qu'une mauvaise carte est métadonnées-uniquement ; cette affirmation antérieure était fausse. Le résidu est borné par la marge `k`/`n`, par les défenses d'effondrement de vivier de PS-12, et par la reconstruction (ID-5a) — non par l'impossibilité.
- **La reproduction (ID-5a) n'est l'arbitre que tant que les entrées sont récupérables — une borne de vivacité.** La reconstruction ne résout un litige que si les entrées publiques épinglées peuvent encore être récupérées depuis une source honnête. Les dumps MRT RouteViews / RIPE RIS et les fichiers de délégation RIR ne sont **pas** des archives permanentes assorties d'une garantie de rétention envers ce projet ; une fois qu'une entrée épinglée disparaît de tous les miroirs, `rebuild(manifest)` est inexécutable et un litige sur cet epoch n'a **aucun arbitre** — au pire pour exactement les litiges forensiques d'ancien epoch qui en ont besoin. Un déploiement conforme DEVRAIT (SHOULD) mettre en séquestre les octets d'entrée épinglés dans un stockage adressé par contenu répliqué sur le même ensemble de miroirs sans permission que la carte, afin que l'arbitre hérite de la propre disponibilité de la carte ; à défaut, ID-5a est déclaré **borné en vivacité**, non inconditionnel. (Risques de déterminisme liés non encore épinglés au §4.1 : l'élagage dépendant du miroir rendant « dernier dump ≤ limite » dépendant du miroir ; la mutation RIR d'un fichier unique par jour par opposition à une série de dumps ; la divergence de *décodage d'entrée* MRT entre versions d'analyseur, que la canonicalisation de sortie d'ID-4d ne couvre pas.)
- **ID-1 relocalise l'autorité vers OP-2 ; il n'élimine pas la confiance.** Aucune partie ne *signe* la carte (ID-1 tient à la lettre, et pour tout client qui **reconstruit**, la reproduction seule le porte). Mais un client qui ne reconstruit pas (ID-5b le permet) repose sur la corroboration par quorum diffusé (ID-7b, ID-9), dont le vote est sans autorité **seulement si** le sybil/l'éclipse peut être résisté — ce qui est **OP-2, ouvert**. Sous éclipse, la détection d'équivocation (ID-7a) ne peut pas se déclencher (la victime ne touche aucune racine honnête), un quorum de journaux adverses peut faire paraître une mauvaise carte corroborée, et — la direction inverse, sous-défendue — un adversaire peut faire paraître une *bonne* carte locale *non corroborée* et forcer la victime à l'abandonner via le « traiter votre carte comme suspecte, re-récupérer » d'ID-9a (un déclassement à travers la machinerie d'honnêteté elle-même). Donc pour le client qui ne reconstruit pas ou qui est éclipsé, « aucune autorité » signifie « faire confiance au quorum », et cela ne tient qu'aussi loin qu'OP-2. Cette partie **réduit** le problème d'autorité de carte à OP-2 ; elle ne le dissout pas.

Le résumé honnête : **le taux d'erreur du jeu de données est un résidu déclaré, non nul, non un défaut à corriger jusqu'à zéro** — et, comme les trois points qui viennent d'être ajoutés le rendent explicite, le sont aussi le plafond d'orientation du contenu (PS-12), la borne de vivacité sur l'arbitre, et la réduction de l'autorité de carte à OP-2. Ce sont le prix du refus d'une autorité. La bonne réponse n'est pas de les cacher mais de les borner, de fournir le taux d'erreur au simulateur, et de montrer à l'utilisateur le niveau atteint (PS-9, PS-11).

## 11. Le taux d'erreur alimente le simulateur (pas d'effet de manche)

Le résidu du §10 n'est pas rhétorique ; c'est la quantité exacte que le simulateur consomme déjà. `poc/network_sim.py` expose **`infer_error`** — la probabilité que l'AS inféré par un client pour un relais soit **faux** (la moitié du temps un mauvais AS, la moitié du temps `unknown`), modélisant un jeu de données qui à la fois mal-mappe et comporte des lacunes (network_sim.py, `Network.random`). La carte spécifiée ici **est** ce jeu de données, et son résidu mesuré **est** ce bouton :

- **ID-12 (la carte déclare un taux d'erreur mesuré). [normatif]** Une publication de carte conforme DOIT (MUST) être livrée avec une **estimation d'erreur mesurée** — son taux de désaccord face à des échantillons de vérité-terrain publics indépendants et sa fraction d'`unknown` — dérivée de façon reproductible à partir de données publiques, de sorte que le nombre lui-même n'ait aucune autorité derrière lui. Cette paire mesurée (taux de mauvais mappage, taux d'`unknown`) est la valeur qu'un client fournit à la machinerie de confiance de la Partie 3 (roadmap 2.2) et la valeur que le simulateur balaie comme `infer_error`.
- **ID-12a (le cas d'erreur nulle est le meilleur cas, jamais celui attendu).** Selon PS-11, les chiffres à erreur nulle et vue complète du simulateur sont le **meilleur** cas ; un client conforme DOIT (MUST) présenter le niveau de disjonction atteint (PS-9) en utilisant l'erreur déclarée de sa carte **réelle**, et l'UI NE DOIT PAS (MUST NOT) citer un chiffre de rupture de contenu comme s'il bornait aussi la liaison (PS-11) — l'asymétrie qui rend une mauvaise carte survivable (ID-8a) est la même asymétrie que l'UI ne doit pas rapporter à tort comme de la sécurité.

## 12. Exigences introduites ici

- **ID-1** — aucune autorité de carte : ne faire confiance qu'à la reproduction et au hachage.
- **ID-2 / ID-2a** — forme de l'artefact (préfixe→AS, AS→juridiction grossière), adressé par contenu par `H` ; recherches totales, `unknown` de première classe.
- **ID-3 / ID-3a** — uniquement des entrées publiques épinglées (BGP RouteViews + RIPE RIS, cinq fichiers de délégation RIR) ; résolution d'origine multi-points-d'observation, MOAS gardé comme un ensemble.
- **ID-4 / ID-4a–d** — déterminisme : l'epoch UTC épingle le moment du dump, ordre total fixe, départage spécifié, pas d'entrées flottantes, conteneur canonique + un vecteur de test de carte.
- **ID-5 / ID-5a / ID-5b** — l'accord est l'égalité de hachage ; la reconstruction à partir des entrées est l'arbitre sans autorité ; rejeter l'irreproductible.
- **ID-6 / ID-7 / ID-7a–c** — journal de transparence de Merkle en ajout seul, sans permission, de `(epoch, H, manifest-hash)` ; équivocation attrapée par racines diffusées + preuves de cohérence ; plusieurs journaux, aucun canonique ; le journal détient des engagements, non la carte.
- **ID-8 / ID-8a / ID-8b** — l'amorçage est un TOFU déclaré ; les dégâts d'une mauvaise première carte sont bornés mais **pas métadonnées-uniquement** — une carte d'orientation peut atteindre le contenu (PS-12), donc la borne est conditionnelle (marge k/n + défenses PS-12 + reconstruction), détectable, et la reproduction ne peut être falsifiée ; détecter, ne pas prétendre prévenir.
- **ID-9 / ID-9a / ID-10** — rafraîchissement et gossip de `(epoch, H)` et des racines sous GR-8 ; divergence montrée via PS-9 ; gossip d'anomalies obligatoire pour les trois signatures d'attaque.
- **ID-11 / ID-11a** — couture de fusion : même ancre de confiance (reproductibilité) que la gouvernance de publication, mais ensembles de signataires/appendeurs **séparés** ; outillage partagé oui, autorité partagée non.
- **ID-12 / ID-12a** — la carte livre une estimation d'erreur mesurée, reproductible, qui alimente le bouton `infer_error` du simulateur et la confiance de la Partie 3 ; le cas d'erreur nulle est le meilleur cas, jamais celui attendu.

ID-1 et ID-5a sont les deux porteurs : aucune autorité, et la reproduction est l'arbitre. Les deux sont bornés, non absolus — ID-1 se réduit à OP-2 pour un client qui ne reconstruit pas, et ID-5a est borné en vivacité (§10). La troisième affirmation que cette partie faisait à l'origine — qu'une mauvaise carte ne peut atteindre le contenu — a été **cassée** par une revue hostile : une carte d'orientation manœuvre l'adversaire au-delà de `k` et rompt le contenu, pas seulement la liaison. Plutôt que de le cacher, cette partie le porte désormais ouvertement : la défense est PS-12 et le résidu est déclaré au §10. Cassez le reste de la même manière — trouvez une étape qui nécessite une partie de confiance, une carte qui ne peut être reconstruite à partir de ses entrées, une lacune de vivacité que nous avons manquée, ou un *nouveau* moyen pour une mauvaise carte d'atteindre le contenu au-delà des défenses de PS-12 — et vous aurez cassé cette partie. Telle est l'invitation, et elle a déjà été relevée une fois. Le balayage `infer_error` de `poc/network_sim.py` (et la construction d'orientation de PS-12) est l'homme de paille exécutable derrière le §11 ; attaquez le modèle, puis ce texte.
