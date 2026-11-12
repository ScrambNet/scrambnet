# Spécification ScrambNet — Partie 10 : Construction reproductible et chaîne d'approvisionnement

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/10-reproducible-build.md)).

**Statut : BROUILLON (DRAFT).** Cette partie décide comment une partie obtient un **binaire** ScrambNet
auquel elle peut faire confiance *sans faire confiance à qui l'a construit*, sous I-3 — aucune autorité —
face à un projet dont les contributeurs sont **pseudonymes** et ne portent donc aucune
identité qu'un utilisateur pourrait vérifier. C'est l'analogue logiciel de la Partie 8 : là, une
*carte* est digne de confiance parce qu'elle se reconstruit à partir d'entrées publiques ; ici, un *binaire* est
digne de confiance parce qu'il se reconstruit à partir de sources publiques. Les valeurs d'homme de paille sont marquées `(s)`.

La Partie 9 dit *ce que le code du nœud doit faire* ; cette partie dit *comment ce code devient
un binaire dont vous pouvez vérifier que c'est celui que vous exécutez*. Lisez d'abord le §1 et le §10 : ensemble ils
disent ce que cette partie achète (la reproduction, non la signature, comme arbitre) et ce qu'elle
admet ne pas pouvoir acheter (une porte dérobée dans une source fidèlement reproduite ; un
compilateur qui mé-compile de façon reproductible ; et, pour l'utilisateur qui ne peut pas reconstruire, une
réduction à OP-2 — la même réduction sur laquelle s'achève la Partie 8).

Cette partie décide la reproductibilité comme **ancre** de confiance. Elle ne décide **pas**
*qui signe une publication ni comment les signataires sont choisis et remplacés* — c'est l'item 4.1
(OP-8), une partie distincte. La couture entre eux est le §9, et elle reflète les
ID-11/ID-11a de la Partie 8 par citation.

## 1. La décision, en deux phrases

- **Il n'y a pas d'autorité de publication.** Un binaire ScrambNet est un **artefact reproductible,
  adressé par contenu** que n'importe quelle partie reconstruit octet par octet à partir de sources publiques
  taguées et d'entrées publiques épinglées ; deux parties s'accordent sur le fait qu'un binaire est honnête
  non parce qu'une partie de confiance l'a signé mais parce qu'elles ont calculé le **même
  `BLAKE2s`** (RB-1, RB-9). Un binaire béni par un ensemble de signataires fixe serait une
  autorité de publication sous un autre nom, et I-3 l'interdit.
- **L'accord se fait par reproduction ; les signatures ne font que *localiser* une construction, elles ne l'*autorisent* jamais ; la confiance en une construction que l'utilisateur ne peut pas lui-même reproduire se réduit à
  la corroboration-par-le-nombre, c.-à-d. OP-2.** C'est la forme honnête et elle est
  énoncée d'emblée, non enfouie : pour la partie dotée d'une machine de construction, la reproduction
  porte toute la confiance ; pour le téléphone qui ne peut pas reconstruire — l'utilisateur modal —
  la confiance repose sur un décompte de reproducteurs indépendants, exactement comme le client
  de la Partie 8 qui ne reconstruit pas repose sur un quorum diffusé par gossip (RB-7b, §10).

Ainsi l'issue honnête est la même que celle que la Partie 8 a atteinte pour la carte : **reproduisez-le
vous-même et la confiance est sans autorité ; vous ne pouvez pas le reproduire, et vous retombez sur un
quorum de corroboration soumis à OP-2.** Tout ce qui suit rend concret « reproduis-le
toi-même, et détecte quiconque a menti », et le §10 est le résidu qu'aucune quantité de
construction ne retire.

## 2. Portée et le piège que cette partie évite

Un projet pseudonyme ne peut pas demander à l'utilisateur de faire confiance à ses auteurs — il n'y a pas
d'auteur à qui faire confiance. La conception naïve « sans confiance » est un binaire signé par les
mainteneurs du projet ; cela réimporte précisément l'autorité que I-3 refuse. Le piège : un
signataire qui peut livrer discrètement un binaire malveillant sous une clé de confiance est l'interrupteur de coupure
que l'item 4.1 existe pour éviter. Donc la confiance ne doit pas passer par *qui a signé* ; elle
passe par *est-ce que ça se reconstruit*.

- **RB-1 (aucune autorité de publication ; la reproduction est l'arbitre). [normatif]** Aucune
  étape de l'obtention ou de la validation d'une construction NE DOIT (MUST NOT) exiger de faire confiance au fait qu'une partie
  particulière l'a compilée, signée ou bénie. Les seules opérations de confiance sont (a)
  recalculer `BLAKE2s`, et (b) reconstruire l'artefact à partir des sources taguées et des
  entrées épinglées et comparer. Tout élément de conception qui ne peut être remplacé par un
  substitut non fiable effectuant (a) ou (b) est un défaut sous I-3 et DOIT (MUST) être
  retiré ou déclaré au §10. (L'opération (b), reconstruire-et-comparer, est de confiance
  **modulo** le résidu de chaîne d'outils : exécuter la construction exécute le compilateur
  épinglé, que RB-3b déclare comme un résidu « trusting-trust » — reconstruire réduit la confiance
  au compilateur, cela ne l'élimine pas. RB-1 est l'affirmation aux deux opérations, lue
  avec ce renvoi, non sans lui.)
- **RB-2 (la reproductibilité autorise ; les signatures ne font que localiser). [normatif]** Cette
  partie ne décide rien quant à *qui signe une publication ni comment les signataires sont choisis et
  remplacés* — c'est l'item 4.1. Une signature sur une construction, s'il en existe une du tout,
  DOIT (MUST) être traitée comme un **localisateur** (« une construction avec ce `H_build` a été annoncée
  ici, à ce moment, par cette main pseudonyme »), jamais comme une **autorisation** (« voici
  la construction à exécuter »). Un client conforme NE DOIT PAS (MUST NOT) adopter une construction *parce qu'*elle a été
  signée ; *quelle* construction adopter est l'affaire de l'item 4.1 et est locale au client et
  optionnelle. Lier l'honnêteté-de-construction à un ensemble de signataires réimporte l'autorité que I-3
  interdit (la règle ID-11a, pour le logiciel).
- **RB-2a (outillage partagé, non autorité partagée).** Cette partie PEUT (MAY) réutiliser la
  construction de journal de transparence de la Partie 8 (ID-6) et le canal de gossip GR-6 pour publier et
  diffuser par gossip les hachages de construction (RB-14) — partager un *mécanisme* ne coûte rien (ID-11a). Elle
  NE DOIT PAS (MUST NOT) partager avec la carte un ensemble de parties — **liste de signataires ou d'appendeurs de journal** —
  dont le rôle est porteur à la fois pour la carte et pour le code, car cet ensemble
  serait l'interrupteur de coupure que I-3 interdit, désormais capable de faire basculer à la fois l'inférence
  géographique et le logiciel. Le journal partagé n'introduit aucune autorité **parce que** les deux parties
  font passer la confiance par la reproduction, non par le journal, et le journal reste sans permission
  (ID-7).

## 3. La chaîne d'outils, épinglée par le contenu

- **RB-3 (la chaîne d'outils est épinglée par le contenu, non par un nom de canal). [normatif]**
  La construction DOIT (MUST) épingler une chaîne d'outils *exacte* — une publication stable spécifique (homme de paille :
  `rust 1.xx.y` dans `rust-toolchain.toml` avec `channel = "1.xx.y"`, jamais
  `stable`/`latest`/`beta`/`nightly`) — **et** épingler les artefacts binaires de cette chaîne d'outils
  par `BLAKE2s` dans le manifeste de construction (RB-8). « La chaîne d'outils » est un ensemble d'octets
  hachés, non un nom qu'un miroir peut résoudre différemment. Un reconstructeur récupère la
  chaîne d'outils depuis **n'importe quel** miroir et vérifie les hachages (I-3 : le distributeur
  est remplaçable ; les octets sont épinglés — le motif ID-3 appliqué au
  compilateur).
- **RB-3a (épingler toute la surface de compilation).** L'épinglage DOIT (MUST) couvrir chaque outil dont la
  sortie atteint l'artefact : `rustc`, `cargo`, les bibliothèques précompilées `std`/`core`
  effectivement liées, l'éditeur de liens (homme de paille : un `lld`/`mold` épinglé (s), non
  le `ld` ambiant de l'hôte), la libc/le sysroot, et tout outil qu'un `build.rs` invoque. Un
  outil laissé à l'hôte est une entrée non épinglée et un risque de déterminisme (RB-6, RB-18).
- **RB-3b (le compilateur est un binaire récupéré — « trusting-trust » est un résidu
  déclaré). [normatif]** Le `rustc` épinglé est un *binaire récupéré*, non quelque chose que
  ce pipeline construit depuis les sources. Lui faire confiance est un **résidu déclaré** (§10,
  « trusting-trust ») : RB-3 épingle *quels* octets de compilateur tout le monde utilise, de sorte que tous les
  reconstructeurs partagent le *même* résidu et toute *substitution* est détectable par
  divergence ; cela ne rend **pas** le compilateur honnête. L'épinglage prouve la
  **provenance**, non l'**honnêteté** (voir RB-18). Un chemin d'amorçage-depuis-les-sources ou de
  double-compilation-diverse, s'il est un jour adopté, est nommé comme travail futur, non
  exigé ici.

## 4. La construction hermétique

La construction est une **fonction pure du manifeste vers un artefact identique octet par octet**.
Le déterminisme est tout l'enjeu : si deux constructeurs honnêtes peuvent diverger, l'égalité de hachage
(RB-9) cesse de signifier « même binaire » et des constructeurs honnêtes se font signaler comme une attaque
(RB-7, RB-15) — la leçon de la Partie 8 (préambule d'ID-4), que ne pas apprendre ici serait fatal.

```
  LA CONSTRUCTION EST UNE FONCTION PURE DU MANIFESTE (RB-8)

  ┌──────────────────────── manifeste (RB-8) ─────────────────────────┐
  │  commit/tag source · hachages de chaîne d'outils (RB-3) · hachage │
  │  de contenu de chaque dépendance (RB-5) · env. fixé (RB-4b) ·     │
  │  triplet cible · SOURCE_DATE_EPOCH (dérivé, RB-4b) · H_build      │
  │  attendu                                                          │
  └────────────────────────────┬──────────────────────────────────────┘
                               ▼
            ┌──────────────────────────────────────────┐
            │  CONSTRUCTION HERMETIQUE (fn pure, RB-4) │
            │  pas de réseau (RB-4a), pas d'état hôte  │
            │  ambiant, env. fixé (RB-4b), indéter-    │
            │  minisme éliminé selon l'ensemble de     │
            │  risques épinglé (RB-6, versionné par la │
            │  chaîne d'outils)                        │
            └──────────────────┬───────────────────────┘
                               ▼
                    artefact (pour UN triplet cible)
                               │
                               ▼
              H_build = BLAKE2s(artifact)   ← le SEUL nom de la construction (RB-6a)
                                              défini par (source, manifeste,
                                              triplet cible) — RB-6b

  Alice ─ même manifeste, même triplet ─▶ H_A   Deux constructeurs honnêtes s'accordent
  Bob   ─ même manifeste, même triplet ─▶ H_B   par H_build égal. La reproduction est
                                                l'arbitre (RB-7), non un signataire.
```

- **RB-4 (construction hermétique, hors ligne, sans ambiant). [normatif]** La construction DOIT (MUST) s'exécuter
  avec **aucun accès réseau** et **aucun état hôte ambiant** : aucune lecture de `$HOME`,
  des variables d'environnement de l'hôte (au-delà d'une liste d'autorisation explicite, RB-4b), de l'horloge
  système pour une quelconque valeur embarquée, des noms d'utilisateur/de groupe, du nom d'hôte, du nombre de CPU là où
  cela affecterait la sortie, ou de tout chemin hors du bac à sable. Substrats conformes : une
  dérivation pure de style Nix/`crane`, **ou** un bac à sable conteneur/`bwrap` avec l'espace de noms
  réseau retiré et un environnement minimal fixé. Cette partie spécifie les
  **propriétés** et ne mandate aucun des deux substrats (I-1 : un implémenteur hostile
  construit un constructeur conforme à partir des propriétés) ; Nix et un conteneur en bac à sable sont
  nommés comme les deux substrats de référence conformes. Une partie qui adopte un
  substrat DOIT (MUST) *l*'épingler aussi (une chaîne d'outils Nix est elle-même un épinglage RB-3).
- **RB-4a (aucune récupération réseau au moment de la construction, jamais). [normatif]** La construction NE DOIT PAS (MUST NOT)
  récupérer quoi que ce soit — aucun accès à un registre, aucune résolution de dépendance git, aucun
  téléchargement par `build.rs`, aucun tirage de chaîne d'outils. Chaque récupération se produit *avant* l'étape
  hermétique, épinglée par hachage, et est remise via le manifeste. Une construction qui *peut* atteindre
  le réseau est non conforme même s'il se trouve qu'elle ne l'utilise pas, car son
  déterminisme dépend alors d'un serveur (l'interdiction des entrées flottantes ID-4c, pour le
  logiciel).
- **RB-4b (environnement fixé, déclaré, dérivé). [normatif]** L'environnement de
  construction DOIT (MUST) être fixé dans, et uniquement dans, le manifeste : locale `C`/`C.UTF-8`,
  `TZ=UTC`, umask, la liste d'autorisation d'env., et `SOURCE_DATE_EPOCH`. `SOURCE_DATE_EPOCH`
  DOIT (MUST) être **dérivé de façon déterministe du commit tagué** (la date de commit (committer date)
  du tag épinglé), de sorte que ce soit une fonction d'une entrée épinglée, non une
  assertion de manifeste flottante qu'un constructeur pourrait fixer à sa guise. Une date de commit falsifiée n'est pas
  un gain silencieux : elle change `H_build` et est donc attrapée par divergence (RB-7),
  exactement comme n'importe quel autre changement d'entrée l'est.

## 5. L'arbre de dépendances

- **RB-5 (arbre de dépendances minimal, audité, embarqué (vendored), épinglé par contenu).
  [normatif]** Les dépendances DOIVENT (MUST) être (a) *minimisées* — chacune justifiée contre
  le fait de ne pas l'avoir, car chaque crate est un auteur non fiable dans la chaîne de confiance
  (RB-16, OP-10) ; (b) *embarquées (vendored)* — la source exacte de chaque dépendance transitive
  épinglée dans les entrées de construction, non résolue en direct (RB-4a) ; et (c) *épinglées par
  contenu* — `Cargo.lock` commité, **et** chaque crate en outre épinglé par
  `BLAKE2s` de sa source dans le manifeste (RB-8), sans faire confiance à la somme de contrôle propre du registre
  seule. Un registre qui peut changer les octets sous un nom est une autorité ;
  le hachage de contenu le supprime et fait du registre un CDN remplaçable.
- **RB-5a (le fichier de verrouillage est nécessaire, non suffisant).** `Cargo.lock` épingle les
  versions et les sommes de contrôle du registre ; il ne rend pas à lui seul la *construction*
  reproductible (l'unification de fonctionnalités, `cfg`, les différences d'hôte mordent encore — RB-6)
  ni ne supprime la confiance en le registre. L'épinglage par contenu de RB-5 et l'hermétisme de RB-4 comblent
  cet écart. Une construction qui n'épingle que le fichier de verrouillage est non conforme.
- **RB-5b (les scripts de construction et les proc-macros sont du calcul de confiance, non des données inertes).
  [normatif]** Les scripts `build.rs` et les macros procédurales exécutent du code arbitraire
  *au moment de la construction* ; ils DOIVENT (MUST) s'exécuter à l'intérieur du bac à sable RB-4 sous les mêmes
  règles sans-réseau/sans-ambiant, et ils sont dans le périmètre de l'audit RB-16 exactement comme
  le code d'exécution l'est. Un proc-macro qui lit l'horloge ou le réseau est un
  risque de déterminisme et une surface de chaîne d'approvisionnement en un.

## 6. Risques de déterminisme et comment la construction les épingle

Chaque risque ci-dessous est un endroit où deux constructeurs honnêtes pourraient produire des octets différents.
La construction DOIT (MUST) éliminer chacun ; une construction qui ne le fait pas est non conforme car elle
ne peut pas soutenir RB-9, et sa divergence est mal lue par RB-7 comme une attaque.

- **RB-6 (l'ensemble de risques est normatif, versionné par la chaîne d'outils). [normatif]** La
  construction DOIT (MUST) éliminer chaque risque de l'**ensemble de risques épinglé** pour la version de chaîne d'outils
  utilisée. Cet ensemble est normatif-à-la-date-d'une-chaîne-d'outils-épinglée, non pour toujours (résidu
  §10.7 : le déterminisme est une cible mouvante face à la rotation de la chaîne d'outils), et le
  manifeste DOIT (MUST) référencer la version de l'ensemble de risques contre laquelle il a été construit. L'ensemble au
  minimum DOIT (MUST) épingler :
  - **les horodatages** — `SOURCE_DATE_EPOCH` issu du commit tagué (RB-4b) ; aucun mtime
    dans aucune archive émise ;
  - **les chemins de construction** — `--remap-path-prefix` vers une racine `/build` fixe, de sorte qu'aucun
    chemin absolu, `$HOME`, ou nom d'utilisateur ne soit embarqué dans les infos de débogage ou les chaînes
    de panic ;
  - **le parallélisme et l'ordonnancement** — l'ordre des unités de codegen, l'ordre de liaison, l'ordre de la
    table de symboles, l'ordre des membres d'archive, et tout ordre d'itération de table de hachage qui atteint
    la sortie DOIVENT (MUST) être rendus déterministes (fixés ou triés) ;
  - **la dérivation de `-C metadata` / `-C extra-filename`** — dérivée de façon déterministe
    à partir d'entrées épinglées, jamais d'une valeur variant selon l'hôte ;
  - **la locale/l'encodage** — `LC_ALL=C` ;
  - **les infos de débogage et les symboles** — déterministes, ou retirés (stripped) ; s'ils sont gardés, déterministes ;
  - **la disposition (layout) aléatoire et les graines** — `-Z randomize-layout` désactivé ; tout
    codegen amorcé par RNG épinglé ;
  - **l'encadrement d'archive/de paquet** — un codec fixe à un niveau fixe, sans aucun
    nom de fichier, horodatage, ni uid/gid dans les métadonnées du conteneur (la règle ID-4d du conteneur
    canonique, pour l'empaquetage logiciel).

  L'analogue du risque de décodage non épinglé de la Partie 8 (note ID-4d §10) s'applique ici
  et est nommé, non caché : **le codegen dépendant de la version de LLVM et l'unification de
  `cfg`/fonctionnalités dépendante de l'hôte** (admise dans RB-5a) ne sont reproductibles que *à la date de
  la chaîne d'outils épinglée et de la résolution de fonctionnalités épinglée* ; chaque montée de version de chaîne d'outils est une
  nouvelle obligation d'audit de déterminisme (§10.7), non un ticket gratuit.
- **RB-6a (l'artefact est adressé par contenu ; `H_build` est son seul nom).
  [normatif]** L'artefact de publication est adressé par `H_build = BLAKE2s(artifact)`
  (le hachage de suite, Partie 0). `H_build` est le seul nom faisant autorité de la construction ; une
  chaîne de version lisible par un humain (`v1.2.3`) est une étiquette de commodité et NE DOIT PAS (MUST NOT) être
  tenue pour fiable à la place de `H_build` (la règle ID-2 « le hachage est le seul nom »). La fraîcheur —
  *quelle* version un client devrait exécuter — est une propriété distincte, portée par RB-8a,
  non par la chaîne de version.
- **RB-6b (`H_build` est par cible ; l'accord est défini au sein d'un triplet).
  [normatif]** Une publication se reproduit vers des octets *différents* par cible
  (`aarch64-linux-android`, `x86_64-unknown-linux-gnu`, `armv7-…`, …) à partir de la
  *même* source, de sorte que `H_build` est une fonction de **(source taguée, manifeste, triplet
  cible)**. Le manifeste DOIT (MUST) épingler le triplet cible ; l'accord (RB-9) est défini
  **uniquement au sein d'un triplet fixe** ; et RB-7/RB-15 DOIVENT (MUST) ne comparer que les `H_build`
  de même triplet. Un client qui compare son propre hachage de triplet à un hachage publié d'un
  triplet différent NE DOIT PAS (MUST NOT) lever une anomalie de divergence de construction — c'est une erreur de
  catégorie, non une attaque. La partie épingle aussi exactement quels octets `H_build` couvre pour chaque
  artefact livré (le binaire du nœud, et séparément tout installeur ou bibliothèque), de sorte que deux
  reconstructeurs hachent le même objet.

## 7. Comment deux parties s'accordent sur le fait qu'elles détiennent le même binaire

- **RB-7 (la procédure reconstruire-et-comparer d'un inconnu). [normatif]** La procédure
  qu'une partie *sans relation avec aucun contributeur* exécute pour obtenir un artefact
  identique bit à bit et le vérifier :
  1. récupérer la source taguée et le manifeste (RB-8) depuis **n'importe quel** miroir ;
  2. vérifier chaque entrée contre son `BLAKE2s` de manifeste (RB-3, RB-5) ;
  3. exécuter la construction hermétique (RB-4) pour le triplet cible (RB-6b) ;
  4. calculer `H_build` ;
  5. comparer par égalité `BLAKE2s` au hachage publié (RB-14) et à tout hachage de même triplet
     d'un pair.

  Un `H_build` égal est une preuve du même binaire ; inégal est une preuve qu'ils diffèrent et
  DOIT (MUST) être fait remonter comme une **divergence de construction** (RB-15), jamais réconcilié silencieusement. Le
  litige est résoluble par n'importe qui sans appel à une autorité : reconstruire et voir ce que
  la source publique produit (l'arbitre ID-5a, pour le logiciel). C'est le critère « done » de 4.2 :
  deux parties sur des machines différentes produisent des artefacts identiques en hachage à partir de la source
  taguée via une procédure ne nommant aucun singleton de confiance.
- **RB-7a (une publication qui ne se reproduit pas est rejetée, non rafistolée). [normatif]**
  Un artefact publié dont le `H_build` ne peut être reproduit à partir de son manifeste déclaré
  n'est, par définition, pas la construction de cette source : un vérificateur conforme qui *peut*
  reconstruire DOIT (MUST) le rejeter et DEVRAIT (SHOULD) diffuser l'écart par gossip comme une anomalie de construction
  (RB-15). « Ça construit sur la machine du mainteneur mais nulle part ailleurs » est un échec de
  reproductibilité — un défaut — non un état acceptable (la règle ID-5b, pour le
  logiciel).
- **RB-7b (le client qui ne peut pas reconstruire — l'utilisateur modal). [normatif]** Presque
  chaque utilisateur réel exécute le client sur un téléphone sans chaîne d'outils, sans disque, et sans
  bande passante pour compiler l'arbre de dépendances ; il *ne peut pas* effectuer l'opération (b) de
  RB-1. Un tel client DOIT (MUST) suivre chaque binaire qu'il exécute comme
  **`reproduit-par-d'autres-non-vérifié`** jusqu'à ce que lui (ou un pair dont il concorde ensuite
  le `H_build`) reconstruise, DOIT (MUST) traiter la corroboration comme un décompte de reproducteurs
  **vérifiés indépendamment** sous la règle RB-10 (jamais un décompte brut d'attestations), et
  la partie l'énonce clairement : **pour le client qui ne reconstruit pas, la confiance-de-construction ne
  découle pas de la reproduction — elle se réduit à la corroboration-par-le-nombre, c.-à-d. OP-2**,
  exactement comme la confiance-de-carte de la Partie 8 se réduit à OP-2 pour le client de carte qui ne
  reconstruit pas (§10, ID-5b/§10). Le client DOIT (MUST) faire remonter cet état ; il NE DOIT PAS (MUST NOT) présenter un
  binaire non reconstruit comme si l'utilisateur l'avait vérifié.

## 8. Le manifeste, l'accord et la fraîcheur

- **RB-8 (le manifeste est la recette de reproduction). [normatif]** Chaque publication
  DOIT (MUST) livrer un **manifeste** : le commit/tag source, les hachages de chaîne d'outils épinglés
  (RB-3), le hachage de contenu de chaque dépendance (RB-5), l'environnement fixé (RB-4b), le
  triplet cible (RB-6b), `SOURCE_DATE_EPOCH` (dérivé, RB-4b), la version de l'ensemble de risques
  (RB-6), et le `H_build` attendu. Le manifeste — non un serveur, non une
  personne — définit la construction (le manifeste ID-3, pour le logiciel).
- **RB-8a (le manifeste est canonique et adressé par contenu ; la fraîcheur est un champ
  vérifiable). [normatif]** Le manifeste DOIT (MUST) avoir une **sérialisation
  canonique** (réutiliser le profil CBOR canonique de la Partie 2, GR-21..GR-30) et est
  lui-même adressé par contenu par `manifest-hash = BLAKE2s(manifeste canonique)` ;
  sinon deux parties honnêtes produisent des manifest-hash différents pour la même recette et la
  corroboration du journal (RB-14) se scinde sur une différence de formatage — la
  leçon GR-21 non apprise. Le manifeste DOIT (MUST) porter un **index de publication monotone**
  lié ensemble à la date de commit dérivée, et la feuille de journal de transparence
  (RB-13) DOIT (MUST) préserver cet ordonnancement, de sorte que la *récence* soit une propriété vérifiable de
  l'artefact. Cela comble l'écart de couture avec 4.1 que 4.1 ne peut pas combler plus tard (le
  schéma de manifeste est un artefact de 4.2) : voir RB-9a.
- **RB-9 (l'accord est l'égalité de hachage, rien de plus). [normatif]** Deux parties détiennent
  le même binaire **si et seulement si** leurs `H_build` de même triplet sont égaux (RB-6b).
  La comparaison est un test sur 32 octets ; elle ne nécessite ni signataire, ni quorum, ni autorité (la
  règle ID-5, pour le logiciel).
- **RB-9a (la reproductibilité prouve binaire-concorde-avec-source, non source-est-courante —
  le résidu de fraîcheur). [normatif]** `H_build` authentifie *que les octets
  concordent avec la source* ; il ne dit rien quant à *quelle source est celle à exécuter*. Une
  **attaque de déclassement reproductible** — alimenter un client avec un ancien tag comportant une
  vulnérabilité connue, qui se reproduit parfaitement et passe chaque vérification RB ci-dessus — n'est
  déjouée **que** par une règle de fraîcheur. Cette partie fournit l'entrée vérifiable pour
  cette règle (l'index de publication monotone + la date dérivée de RB-8a, ordonnés dans le
  journal, RB-13) ; la *politique d'adoption* qui l'utilise (rejeter un index inférieur à un
  déjà vu ; avertir en cas de péremption) est l'item 4.1 et est locale au client. Le résidu :
  la reproductibilité seule ne déjoue pas le déclassement ; le champ de manifeste que cette partie
  mandate est ce qui rend *possible* à 4.1 de le déjouer (l'epoch ID-4, pour les
  publications).

## 9. La couture de fusion avec la gouvernance des mises à jour (OP-8 / item 4.1)

Les signataires de publication et les publicateurs de racines de la carte semblent n'être qu'un seul mécanisme.
**Position, reflétant le §9 de la Partie 8 : les garder séparés en confiance, même s'ils partagent
l'outillage.**

- **RB-10 (une attestation est une affirmation de reproduction, pondérée par la re-reproduction
  indépendante, non par qui l'a émise). [normatif]** Une **attestation** de construction est une
  déclaration *« j'ai reconstruit le manifeste M pour le triplet T et j'ai obtenu `H_build` »* — un
  **rapport de reproduction**, non une autorisation. Son poids vient d'être
  **vérifiable indépendamment** (n'importe qui réexécute RB-7 et le confirme ou le réfute), non
  de l'identité de l'attesteur : une attestation signée par un pseudonyme et une non signée
  portent le **même** poids une fois qu'un tiers a reproduit l'affirmation ; la
  signature ne fait que *localiser* l'affirmation (RB-2). La corroboration DOIT (MUST) suivre la
  discipline de la Partie 2 exactement : **ne compter que les reproductions vérifiées indépendamment, jamais un
  décompte brut d'attestations** (la règle GR-20 / PS-10 « ne compter que les vérifiées, jamais les
  brutes »). Et la partie concède ce que GR-19a prouve déjà : **l'indépendance des
  reproducteurs n'est pas vérifiable à partir des seules attestations** — vous ne pouvez pas distinguer 10 000
  reproducteurs d'une seule partie portant 10 000 masques — donc un décompte de reproducteurs est un
  signal *faible* qui se réduit à OP-2, et le signal *fort* est la reconstruction propre du client
  (RB-7). Une conception dans laquelle l'acceptation d'une attestation dépend de
  l'identité de l'attesteur, ou dans laquelle un décompte brut d'attestations non vérifiées
  corrobore une construction, est non conforme (RB-1, et c'est l'autorité majoritaire votable par
  sybil que RB-10 existe pour interdire).
- **RB-10a (format d'attestation canonique, déduplication par reproducteur). [normatif]**
  Les attestations traversent le fil (RB-14) et alimentent un décompte (RB-10), donc elles DOIVENT (MUST) avoir un
  encodage canonique (réutiliser le CBOR canonique, GR-21..GR-30) sinon deux attesteurs honnêtes
  produisent des octets non concordants et le comptage casse. Les attestations DOIVENT (MUST) être dédupliquées
  par `(identité de reproduction, M, triplet, H_build)`, et le poids est
  **par-reproducteur-indépendant, jamais par-chaîne-d'octets-d'attestation**, de sorte qu'un
  adversaire ne puisse pas gonfler la corroboration en frappant des variantes distinctes en octets d'une seule
  affirmation (bourrage de format).
- **RB-11 (la chaîne d'outils doit construire de façon déterministe-utilisable ; un vecteur de test
  inter-hôtes existe). [normatif]** Parce que la chaîne d'outils épinglée peut elle-même embarquer
  de l'indéterminisme (codegen parallèle, `OUT_DIR`, triplet hôte dans les métadonnées), la partie
  DOIT (MUST) épingler les drapeaux et modes qui lui font produire une sortie identique à travers les hôtes
  (RB-6), et un **vecteur de test de construction inter-hôtes** (manifeste → `H_build` attendu pour
  un triplet fixe) DOIT (MUST) exister pour qu'une seconde machine prouve qu'elle reproduit l'artefact
  identique (la règle ID-4d du vecteur de test de carte ; se rattache au harnais de conformité de la
  feuille de route 3.2). C'est l'analogue RB du RI-1b de la Partie 9 : *un test fonctionnel qui passe
  prouve que le binaire s'exécute, non qu'il est identique bit à bit* — la reproductibilité est
  vérifiée par reconstruire-et-comparer, jamais supposée à partir de « ça a compilé ».
- **RB-12 (les contributeurs sont pseudonymes ; la confiance ne passe que par la reproductibilité).
  [normatif]** ScrambNet n'a **aucune clé de signature liée à une identité** et aucune identité
  d'auteur de confiance. La confiance en un binaire DOIT (MUST) découler **entièrement** de (a) la source
  étant publique et révisable (I-1) et (b) le binaire se reproduisant à partir de cette source
  (RB-7) — **jamais** de *qui* l'a écrit, commité, tagué, ou signé. Une étape qui
  nécessite une identité d'auteur, de mainteneur ou de signataire de confiance pour accepter une construction est
  non conforme sous à la fois RB-1 et la règle de pseudonymat du projet. C'est la
  résolution de la tension centrale de cette partie : *l'auteur est non fiable par
  construction ; le binaire est de confiance par reproduction.*
- **RB-12a (à quoi servent les clés de pseudonyme — et la précondition sur laquelle elles reposent).** Une
  clé de contributeur, si elle est utilisée du tout, authentifie *la continuité d'un pseudonyme* et
  *localise* le travail (ce commit, cette attestation, viennent de la même main pseudonyme) — une
  commodité pour le gossip et pour le rôle de localisateur de 4.1 (RB-2), jamais une racine
  de confiance-de-construction. Perdre, faire tourner, ou remplacer une telle clé NE DOIT PAS (MUST NOT) invalider aucun
  binaire qui se reproduit encore. Un détenteur d'une clé compromise ne peut pas livrer un
  binaire malveillant-mais-se-reproduisant qui **survit à un réviseur honnête plus un
  reproducteur honnête** — mais cette protection est *leur existence*, non la clé :
  en l'absence d'un réviseur honnête de la source (I-1) et d'un reproducteur honnête que le client
  peut atteindre (RB-7/RB-10), la clé compromise *peut* livrer un binaire malveillant à un
  client qui ne révise ni ne reconstruit (RB-7b). Donc la protection se réduit à
  I-1 (révision) et OP-2 (accessibilité d'un reproducteur honnête) ; ce n'est pas une
  propriété inconditionnelle de la clé. (Cela énonce la précondition explicitement, de sorte que l'affirmation
  n'est pas circulaire.)
- **RB-12b (la reproductibilité prouve binaire-concorde-avec-source, ne dit rien quant à
  source-honnête).** La reproductibilité et la révision sont des **axes orthogonaux**.
  La reproductibilité prouve que le binaire concorde avec la source ; elle ne dit rien quant à
  savoir si la source est honnête. Le pseudonymat (RB-12) retire « un auteur de confiance a
  attesté la source », de sorte que l'honnêteté-de-source repose sur **la révision publique (I-1)** et
  rien d'autre. La partie l'énonce clairement de sorte qu'aucun lecteur ne confonde « reproductible »
  avec « sûr » ou « révisé » : une construction fidèlement reproduite d'une source avec porte dérobée est une
  reproduction fidèle d'une porte dérobée (§10, OP-10).
- **RB-13 (les hachages et les manifestes sont publiés dans un journal sans permission, ordonnés par
  index de publication).** Les tuples de publication `(triplet, H_build, manifest-hash, release-index,
  committer-date)` DEVRAIENT (SHOULD) être annoncés aux mêmes journaux de transparence en ajout seul et sans permission
  utilisés pour les cartes (ID-6/ID-7), préservant l'ordonnancement RB-8a,
  de sorte que les annonces de construction soient horodatées et que l'équivocation soit détectable avec
  **aucun appendeur privilégié** (ID-7). Le journal ne *bénit* pas une construction — la reproduction
  le fait (RB-7) — il rend détectable « un binaire différent montré à des personnes différentes » et
  donne à la fraîcheur (RB-9a) un ordre témoigné. Selon RB-2a la *construction* du journal est
  partagée avec la carte ; les *instances/ensembles* DEVRAIENT (SHOULD) rester indépendants (ID-7b
  « plusieurs journaux, aucun canonique ») de sorte que les deux domaines de disponibilité ne s'effondrent
  pas en un seul opérateur porteur.
- **RB-14 (diffuser par gossip le tuple de construction ; détecter la vue dédoublée). [normatif]** Les clients et
  les reconstructeurs DEVRAIENT (SHOULD) diffuser par gossip `(triplet, H_build, manifest-hash, release-index)` sur
  GR-6 sous le mélange de sources GR-8, et exiger des preuves de cohérence de journal de transparence, de sorte qu'un
  adversaire servant le binaire X à Alice et le binaire Y à Bob (même triplet, même ou
  conflictuel index) soit attrapé par toute partie détenant les deux (la défense contre l'équivocation ID-7a,
  pour les constructions). Un journal filtrant les ajouts de construction derrière un ensemble de signataires est
  non conforme (RB-2a/ID-7).
- **RB-15 (les anomalies de construction sont diffusées par gossip, non supprimées). [normatif]** Quatre événements
  sont des anomalies de construction que tout vérificateur DOIT (MUST) diffuser par gossip à la détection, en comparant uniquement
  les hachages de même triplet (RB-6b) : (a) un `H_build` qui échoue à la reproduction depuis son
  manifeste (RB-7a) ; (b) un journal de transparence présentant des racines incohérentes sur les annonces
  de construction (équivocation prouvée) ; (c) une divergence `H_build` persistante de même triplet
  face à des reproducteurs indépendants ; (d) une **régression d'index de publication** —
  un tag présenté avec un index inférieur à un déjà témoigné pour cette ligne de
  publication (la signature de déclassement, RB-9a). Un vérificateur NE DOIT PAS (MUST NOT) supprimer une anomalie pour
  faire paraître une publication en bonne santé (la règle ID-10 du signal immunitaire, pour les constructions).

## 10. Ce que cette partie ne résout pas (le résidu déclaré)

Cette partie fait que deux parties qui *reconstruisent toutes deux* s'accordent de façon prouvable ou détectent de façon prouvable
qu'elles diffèrent, et elle déplace la confiance de *qui l'a construit* vers *est-ce que ça se reconstruit* — une
réduction réelle et grande, la bonne pour un projet pseudonyme. Elle ne rend
**pas** le binaire *sûr*. Les lacunes sont réelles et sont déclarées, non escamotées :

- **§10.1 — Une porte dérobée dans une dépendance épinglée est reproduite fidèlement, non
  attrapée.** Si un crate embarqué (vendored) contient du code hostile, chaque reconstructeur obtient le
  binaire malveillant identique et RB-7 *confirme* la concordance — la reproduction fonctionne
  exactement comme conçu et est aveugle à la malveillance. Le binaire reflète honnêtement une source qui
  comporte honnêtement une porte dérobée. Les seules défenses sont **la révision publique (I-1), l'audit (RB-16),
  et la minimisation de la surface de dépendances (RB-5/RB-17)** — des processus humains qui *bornent*
  la surface, aucun un contrôle cryptographique sans autorité. **C'est le résidu primaire, il n'a
  aucun substitut non fiable, et c'est le problème récurrent du projet portant un quatrième masque —
  OP-10.** La proposition de valeur est honnête précisément ici : la reproductibilité ne
  défend **pas** contre l'attaque la plus probable du monde réel, et n'a jamais été censée le faire —
  mais elle change *quel genre* d'attaque est requis. Sans elle, un attaquant empoisonne
  **un binaire pour une cible**, de façon invisible et inattribuable. Avec elle, un binaire
  malveillant doit tracer jusqu'à une **source publique** que **tout le monde peut réviser** et qui
  **se reproduit à l'identique pour tout le monde** — forçant l'attaque de « empoisonner
  le binaire » (invisible, par cible) à « empoisonner la source publique ou une dépendance
  publique » (révisable, universel, exposé au maximum à l'unique réviseur honnête). Cette
  transformation est la valeur de la partie ; attraper la source empoisonnée est OP-10 et I-1, non
  la reproductibilité.
- **§10.2 — Une chaîne d'outils compromise qui mé-compile de façon reproductible.** Un
  `rustc`/LLVM avec porte dérobée peut insérer un comportement absent de la source, de façon déterministe, de sorte que
  chaque reconstructeur reproduit le binaire défectueux identique et l'égalité `H_build` tient.
  L'épinglage (RB-3) fait que tout le monde partage un compilateur et rend son *échange*
  détectable ; il ne rend pas le compilateur épinglé honnête. **Aucun substitut non fiable**
  en deçà de l'amorçage-depuis-les-sources ou de la double-compilation-diverse, que cette partie nomme comme
  travail futur (RB-3b), non une exigence courante.
- **§10.3 — « Trusting-trust » (Thompson).** Le cas général de §10.2 : un compilateur qui
  pose une porte dérobée *et* propage la porte dérobée dans les compilateurs qu'il construit. Épingler les
  octets du compilateur ne brise pas la boucle ; cela garantit que tout le monde est à l'intérieur de la
  *même* boucle. Déclaré, non résolu. (C'est pourquoi RB-18 dit « chaque octet de sortie
  trace jusqu'à une entrée *épinglée* » — provenance — et explicitement **pas** « jusqu'à une entrée
  honnête » : un compilateur haché, épinglé, avec porte dérobée satisfait la traçabilité et est tout de même
  malveillant.)
- **§10.4 — Reproductible ≠ sûr ; reproductible ≠ révisé.** Une construction parfaitement
  reproductible d'une source d'apparence honnête mais subtilement fausse est parfaitement
  reproductible. Le pseudonymat (RB-12) signifie qu'aucun auteur de confiance n'atteste la source,
  de sorte que l'honnêteté-de-source repose entièrement sur la révision publique (I-1) ; la reproductibilité et la
  révision sont orthogonales (RB-12b).
- **§10.5 — La corroboration-par-le-nombre se réduit à OP-2 ; le client qui ne reconstruit pas est
  l'utilisateur modal.** « N reconstructeurs indépendants ont obtenu `H_build` » n'est aussi fort que
  l'*indépendance* des N (RB-10, GR-19a). Une seule re-reproduction honnête
  réfute une fausse affirmation avec certitude (plus fort que le cas de la carte, puisque la source est
  déterministe), mais un client qui **ne peut pas reconstruire** (RB-7b — le téléphone, c.-à-d.
  presque chaque utilisateur) s'appuie sur le décompte d'attestations, qui est un quorum votable par
  sybil : un adversaire frappe des attestations pseudonymes pour un mauvais `H_build`, et un
  client **éclipsé** ne voit que des attestations de l'adversaire et ne rencontre jamais un reproducteur
  honnête. Donc pour le client qui ne reconstruit pas ou qui est éclipsé, « aucune autorité » signifie
  « faire confiance au quorum de reproducteurs vérifiés », et cela ne tient qu'aussi loin qu'**OP-2**
  tient. Cette partie **réduit** l'autorité-de-construction à OP-2 pour le client qui ne reconstruit pas ; elle ne
  la dissout pas — la réduction identique sur laquelle la Partie 8 s'achève (ID-1 → OP-2).
- **§10.6 — L'arbitre est borné en vivacité ; le séquestre doit être répliqué ou c'est un
  singleton.** Reconstruire-et-comparer est l'arbitre sans autorité **uniquement tant que
  les entrées épinglées sont encore récupérables**. Les binaires de chaîne d'outils et l'arbre complet de crates
  sont volumineux et périssables : un **crate retiré (yanked)** ou une **publication de chaîne d'outils dé-publiée**
  rend `rebuild(manifest)` inexécutable, et alors l'unique opération de confiance
  a disparu — au pire pour exactement les litiges forensiques (« v1.2 avait-elle une
  porte dérobée ? ») qui en ont le plus besoin. Un déploiement conforme DEVRAIT (SHOULD) mettre en séquestre les octets
  d'entrée épinglés dans un stockage adressé par contenu **répliqué sur le même
  ensemble de miroirs sans permission** que les constructions ; un séquestre à une seule réplique est
  adressé par contenu (donc il ne peut pas *mentir*) mais c'est un **singleton de vivacité** (il peut
  *disparaître*), et I-3 couvre la vivacité. En l'absence de réplication, RB-7 est déclaré
  **borné en vivacité**, non inconditionnel (le résidu de vivacité ID-5a, pour les constructions).
- **§10.7 — Le déterminisme est une cible mouvante face à la rotation de la chaîne d'outils.** De nouvelles
  versions de `rustc`/LLVM introduisent de nouvelles sources d'indéterminisme (nouvelles passes parallèles,
  nouvelles métadonnées, nouveau comportement de `cfg`). L'ensemble de risques de RB-6 est **courant**, non clos ; une
  chaîne d'outils épinglée est reproductible *telle qu'épinglée*, mais chaque montée de version de chaîne d'outils est une nouvelle
  obligation d'audit de déterminisme, et le manifeste enregistre contre quelle version d'ensemble de risques il
  a été construit (RB-6, RB-8). « Reproductible une fois » ne signifie pas « reproductible
  pour toujours ».
- **§10.8 — TOFU de première construction : un premier binaire malveillant ment sur sa propre
  reproduction.** Le *premier* binaire client d'un nouvel utilisateur ne peut pas être reproduit avant d'être
  utilisé pour amorcer (vous avez besoin d'un client fonctionnel pour récupérer la source, la chaîne d'outils,
  et atteindre les journaux et les pairs). Le premier binaire est adopté par confiance-à-la-première-utilisation
  exactement comme la première carte de la Partie 8 l'est (ID-8) — et en pire : un premier binaire compromis
  possède ensuite tout l'appareil de reproduction et de gossip de l'utilisateur, de sorte qu'il peut
  **mentir sur sa propre reproduction** (« je me suis reconstruit moi-même ; `H_build` concorde »). Un
  client ne peut donc pas honnêtement vérifier *sa propre* reproduction ; la confiance de premier binaire
  repose sur un **reproducteur indépendant hors bande** — une machine/chaîne d'outils différente
  à laquelle l'utilisateur fait plus confiance qu'au binaire testé. C'est la frontière « trusting-trust » /
  hôte-compromis (§10.9) ; c'est un résidu déclaré, énoncé ici plutôt
  qu'avalé silencieusement par « hors de portée ».
- **§10.9 — Ce que cette partie n'essaie même pas.** La compromission à l'exécution de la
  machine de l'utilisateur ; une *construction malveillante d'une source honnête par l'utilisateur lui-même* sur un
  hôte compromis (la reproduction confirme la concordance ; l'hôte possède tout de même le
  processus) ; et tout ce qui est au-dessus de la frontière de l'artefact — l'installation, et l'*adoption*
  des mises à jour (quelle construction exécuter et quand), qui est l'item 4.1. La partie est
  artefact-identique-bit-à-bit uniquement ; elle nomme cela comme hors de portée, non comme résolu.

Le résumé honnête : les constructions reproductibles déplacent la confiance de *qui l'a construit* vers *est-ce que ça se
reconstruit* — réel et grand. Mais elles sont **muettes** sur l'honnêteté de la source
(§10.1, §10.4), **aveugles** à une porte dérobée reproductible de compilateur/dépendance (§10.1,
§10.2, §10.3), **bornées en vivacité** en tant qu'arbitre (§10.6), **réduites à OP-2** pour le
client qui ne reconstruit pas ou qui est éclipsé (§10.5) — l'utilisateur modal (RB-7b) — et en
**TOFU** sur le premier binaire (§10.8). Ce sont le prix du refus d'une autorité de
publication. La bonne réponse est de les borner — minimiser et auditer la base de calcul de
confiance, répliquer le séquestre, encourager les reconstructions indépendantes, porter
l'index de fraîcheur — et de les énoncer, non de les cacher.

## 11. Hygiène de chaîne d'approvisionnement qui borne le résidu

- **RB-16 (l'audit des dépendances et de la chaîne d'outils est obligatoire et dans le périmètre).** Parce que
  la reproduction ne peut pas voir une porte dérobée que chaque reconstructeur reproduit fidèlement
  (§10.1), la partie DOIT (MUST) exiger une piste d'audit commitée et révisable pour l'ensemble
  de dépendances et la chaîne d'outils (des enregistrements de style `cargo-vet`/`cargo-audit`, épinglés
  par contenu), traitée comme **preuve de révision (I-1), non comme autorité**. L'audit
  réduit la surface d'attaque de §10.1 ; il ne la supprime pas, et la partie le dit.
- **RB-17 (minimiser la base de calcul de confiance).** La partie DEVRAIT (SHOULD) exiger de rétrécir
  activement ce qui doit être de-confiance-et-audité : moins de dépendances (RB-5), moins de
  `build.rs`/proc-macros (RB-5b), une plus petite surface de chaîne d'outils (RB-3a),
  `#![forbid(unsafe_code)]` là où c'est faisable — car chaque élément de la base de calcul de
  confiance est un résidu de §10.1 que l'audit doit couvrir et que la reproduction ne peut pas.
  Note honnête : « minimal » n'est pas « petit » — un vrai nœud async + crypto (un
  runtime async, une pile Sphinx/X25519, CBOR, …) traîne des *centaines* de crates transitifs,
  beaucoup avec des scripts de construction, de sorte que le résidu de porte-dérobée-de-dépendance de §10.1 n'est pas un cas
  limite mais la surface d'attaque **attendue**. C'est le cadrage honnête d'OP-10.
- **RB-18 (toute la chaîne est épinglée ou elle n'est pas épinglée — et épinglé signifie
  provenance, non honnêteté). [normatif]** Une seule entrée non épinglée où que ce soit — un
  composant de chaîne d'outils non haché, une dépendance flottante, un `build.rs` qui lit
  l'hôte, une image de base de conteneur récupérée par tag — annule l'affirmation de reproductibilité pour
  l'artefact entier, car cette seule entrée réintroduit un serveur ou un hôte comme
  partie de confiance (RB-1). Le manifeste DOIT (MUST) être **complet** : si un octet de sortie
  ne peut être tracé jusqu'à une entrée *épinglée*, la construction est non conforme (la règle ID-4c,
  pour le logiciel). **C'est une affirmation de déterminisme/de provenance, non une affirmation de confiance :** une
  entrée épinglée peut être malveillante (§10.1, §10.2, §10.3) ; l'épinglage rend la malveillance
  identique pour tout le monde et toute *divergence par rapport à une entrée honnête* détectable — il ne
  rend **pas** l'entrée honnête. « Épinglé » ne signifie jamais « sûr ».

## 12. Exigences introduites ici

- **RB-1 / RB-2 / RB-2a** — aucune autorité de publication, la reproduction est l'arbitre ;
  les signatures ne font que localiser, jamais autoriser ; outillage partagé avec la carte, jamais
  autorité partagée.
- **RB-3 / RB-3a / RB-3b** — chaîne d'outils épinglée par contenu à travers toute la surface de
  compilation ; le compilateur épinglé est un résidu « trusting-trust » déclaré (provenance,
  non honnêteté).
- **RB-4 / RB-4a / RB-4b** — construction hermétique, hors ligne, sans ambiant ; aucune récupération au moment de la
  construction ; un environnement fixé avec `SOURCE_DATE_EPOCH` **dérivé** du commit
  tagué.
- **RB-5 / RB-5a / RB-5b** — arbre de dépendances minimal, embarqué (vendored), épinglé par contenu ;
  fichier de verrouillage nécessaire-non-suffisant ; les scripts de construction et les proc-macros sont du calcul de confiance en
  bac à sable.
- **RB-6 / RB-6a / RB-6b** — ensemble de risques d'indéterminisme normatif, versionné par la chaîne d'outils ;
  `H_build` est le seul nom ; `H_build` est par-(source, manifeste, triplet
  cible) et l'accord est au sein d'un triplet.
- **RB-7 / RB-7a / RB-7b** — le reconstruire-et-comparer de l'inconnu ; rejeter
  l'irreproductible ; l'utilisateur modal qui ne reconstruit pas suit `reproduit-par-d'autres-
  non-vérifié` et se réduit à OP-2.
- **RB-8 / RB-8a / RB-9 / RB-9a** — le manifeste est la recette, canonique et
  adressée par contenu, portant un index de publication monotone ; l'accord est l'égalité de hachage de
  même triplet ; le résidu de fraîcheur (déclassement reproductible) avec le champ de manifeste
  dont 4.1 a besoin.
- **RB-10 / RB-10a** — une attestation est une affirmation de reproduction pondérée par la
  re-reproduction indépendante (ne compter que les vérifiées, jamais les brutes ; l'indépendance est
  OP-2) ; format canonique, déduplication par reproducteur.
- **RB-11 / RB-12 / RB-12a / RB-12b** — vecteur de test de construction inter-hôtes ; la confiance ne passe
  que par la reproductibilité ; les clés de pseudonyme localisent, jamais n'enracinent la confiance (avec la
  précondition rendue explicite, non circulaire) ; reproductibilité ⊥ révision.
- **RB-13 / RB-14 / RB-15** — journal sans permission de tuples de construction ordonnés par index de
  publication ; gossip + détection de vue dédoublée ; quatre anomalies obligatoires y compris la
  signature de déclassement.
- **RB-16 / RB-17 / RB-18** — audit obligatoire comme preuve de révision ; minimiser la TCB
  (qui reste grande) ; toute la chaîne épinglée, où épinglé est provenance, non
  honnêteté.

RB-1 et RB-7 sont les deux porteurs : aucune autorité, et la reproduction est l'
arbitre. Les deux sont bornés, non absolus — RB-1 se réduit à OP-2 pour le client qui
ne reconstruit pas (§10.5, l'utilisateur modal), et RB-7 est borné en vivacité (§10.6).
Le résidu le plus aigu, énoncé et non caché, est §10.1 : **la reproductibilité n'attrape pas
une dépendance avec porte dérobée, qui est l'attaque réelle la plus probable — elle force l'
attaque dans une source publique, révisable, universelle, ce qui est le but, et l'attraper
là est OP-10, non cette partie.** Cassez cette partie en nommant une étape de construction qui
nécessite une partie de confiance, un artefact publié qui ne peut être reconstruit à partir de son
manifeste, un risque de déterminisme que RB-6 manque, un moyen pour une signature de faire passer en contrebande
une autorisation au-delà de RB-2, ou un moyen pour le client qui ne reconstruit pas d'être laissé à faire confiance à
une majorité qui n'est pas OP-2. Telle est l'invitation, dans la voix de la Partie 8.
