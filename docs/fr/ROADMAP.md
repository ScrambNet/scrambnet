# ScrambNet — Feuille de route

**Statut : document vivant.** Ceci est le plan de travail, non une promesse de dates — un
projet bénévole pseudonyme avance quand des mains se libèrent. Il est ordonné par
dépendance et par honnêteté : les éléments qui pourraient prouver que le projet a *tort* viennent
en premier, car si l'affirmation porteuse ne tient pas, rien en aval n'a
d'importance. Chaque élément nomme ce à quoi « fait » ressemble, de sorte que le progrès soit vérifiable, non
asséné.

Il a été bâti à partir de trois revues parallèles — conception réseau, cryptographie et
sécurité/opérations — et les constats les plus durs sont gardés bien en vue plutôt que
lissés. Les éléments renvoient aux parties de la spécification (`SP-n`, `GR-n`,
`PS-n`, `RZ-n`), aux invariants (`I-1…I-4`) et aux problèmes ouverts
(`OP-1…OP-9`).

Échelle d'effort : **S** ≈ jours · **M** ≈ 1–2 semaines · **L** ≈ semaines, vrai risque de
conception · **XL** ≈ un sous-projet de recherche qui peut rendre un résultat partiel ou négatif.
Les deux derniers ne sont pas des échecs à éviter ; ils sont la forme honnête des
problèmes non résolus.

---

## Palier 0 — Corriger ce que nous savons déjà faux (maintenant)

Ceux-ci sont ressortis des revues comme des défauts concrets ou des sur-affirmations. Ils sont bon marché
et ils protègent la crédibilité du projet, qui est son seul véritable actif à ce
stade.

- **0.1 — Réconcilier les affirmations publiques avec le périmètre prouvé.** `[claim-critical]`
  Le plancher de contenu est informationnel-théorique **seulement en dessous de `k` parts** ; au-dessus de
  `k`, le secret du contenu est calculatoire (l'AEAD). Et « récolter maintenant, déchiffrer
  plus tard » n'est défait **que** pour l'adversaire en dessous de `k` — un adversaire `≥k`, qui
  enregistre tout et dispose du quantique futur casse toujours le contenu *à moins que
  l'accord de clés de bout en bout ne soit lui-même post-quantique ou pré-partagé*. Le README, la
  COMPARISON et le modèle de menace doivent énoncer le régime (en dessous de `k` vs au-dessus de `k`)
  et l'hypothèse (secret de la clé AEAD) sur chaque phrase qui parle du plancher.
  **Fait :** aucune « protection de contenu informationnelle-théorique » non qualifiée ne subsiste dans
  aucun document public. **Effort S.**

- **0.2 — Spécifier et démontrer la couche AEAD de bout en bout.** `[claim-critical]`
  SP-1 (« chiffrer avant la dispersion ») est toute l'affirmation de composition, mais la PoC
  découpe du *texte clair* — il n'y a d'AEAD nulle part, de sorte que la composition est affirmée,
  jamais montrée. Spécifier la couche de bout en bout (établissement des clés à partir de la `kpair` de la carte de
  contact vs un échange éphémère — un choix qui décide de l'histoire post-quantique), et
  étendre la PoC pour réellement chiffrer → découper → reconstituer → déchiffrer.
  **Fait :** la PoC démontre SP-1 de bout en bout ; le choix d'établissement des clés est
  fait et sa conséquence PQ enregistrée. **Effort M.**

- **0.3 — Intégrité des parts sous un drop malveillant.** `[soundness]`
  L'étiquette SP-7 indique *à quel* message un paquet prétend appartenir, mais rien
  n'authentifie les octets de la part ni l'octet `k,n`. Un seul drop ou une seule sortie hostile
  peut inverser des bits dans une part ; Shamir ne peut pas le détecter, de sorte que `k` parts
  corrompues-cohérentes se reconstituent en charabia (l'AEAD au-dessus le rattrape — échec fermé — mais
  c'est un *déni de service ciblé* bon marché sur une boîte). Décider : liaison
  explicite par part, ou un résidu échec-fermé-avec-reprise accepté-et-documenté. **Fait :** un verdict
  avec la construction si nécessaire, inscrit dans
  SP-7. **Effort M.**

- **0.4 — Publier la clé PGP du projet.** `[opsec, lacune immédiate]`
  SECURITY.md *promet* une clé qui n'existe pas. La première vague de relecteurs
  (les listes de diffusion) n'a aucun canal confidentiel. Générer une clé liée à un pseudonyme
  pour `scrambnet@proton.me`, valider son empreinte, remplacer le geste évasif du « délai
  raisonnable » par une vraie fenêtre de divulgation, et énoncer comment la clé elle-même
  tourne (même la clé de divulgation ne doit pas être un singleton irremplaçable, I-3).
  **Fait :** un rapport sensible peut être chiffré vers une vraie clé publiée dès aujourd'hui.
  **Effort S.**

*(Le bug d'ordre des quartets du parseur de 0.1 et la lacune de sondage à la frontière d'époque UTC trouvés en
revue sont déjà notés pour les vecteurs de test en 3.2 et l'élément KDF en 2.2.)*

---

## Palier 1 — Prouver ou casser l'affirmation porteuse (épine dorsale cryptographique)

Tout le différenciateur du projet est I-2. Ces quatre éléments, en séquence,
soit l'établissent rigoureusement, soit révèlent où il est exagéré. Rien d'autre n'est
digne d'être construit tant que cette épine ne tient pas.

- **1.1 — Formaliser la composition chiffrement-puis-Shamir.** `[claim-critical]`
  Un théorème écrit (ou un contre-exemple) énonçant *exactement* ce qui est inconditionnel
  (le texte chiffré est caché en dessous de `k`, sans aucune hypothèse calculatoire) et ce qui ne l'est
  pas (le texte clair au-dessus de `k` repose sur l'AEAD). Confirmer que la clé AEAD n'apparaît jamais
  dans rien de ce qu'un adversaire en dessous de `k` voit. **Fait :** une phrase précise
  pour chacun des niveaux inconditionnel et calculatoire, démontrablement disjoints.
  **Effort M.**

- **1.2 — Prouver le plancher sur tout le secret, non sur un octet.** `[claim-critical]`
  La démo par force brute de la PoC couvre un *seul octet* ; les tests de propriété ne vérifient
  qu'une marginale. Prouver l'indépendance jointe de `k−1` parts quelconques sur le secret
  complet (standard, étant donné des coefficients uniformes et indépendants par position), et ajouter
  un test qui échouerait sous réutilisation de coefficients ou avec un RNG de faible entropie. Documenter
  **« l'aléa des coefficients est critique pour le plancher »** comme une exigence de premier rang.
  **Fait :** preuve d'indépendance jointe citée + un test qui attrape la défaillance du RNG.
  **Effort S–M.**

- **1.3 — Étiquette SP-7 : rejeu, forge, liaison inter-drops.** `[soundness]`
  La propriété qui ne doit pas échouer : deux parts d'un message ne doivent jamais porter une
  valeur observable égale à travers des drops conspirant. Les parts vers des drops distincts utilisent
  des indices distincts, donc les étiquettes diffèrent — *prouver* qu'aucune paire `(nonce, index)` n'est jamais
  réutilisée entre drops, ou le corriger. En plus : règles de propriété du nonce (un
  `msg_nonce` réutilisé à la fois fait entrer en collision les étiquettes et casse l'AEAD de façon
  catastrophique), et défenses de rejeu/éviction à la couche de stockage. **Fait :** esquisse de preuve de non-égalité des étiquettes,
  discipline du nonce inscrite dans SP-7, rejeu traité au drop. **Effort M–L.**

- **1.4 — Unifier la discipline de dérivation de clés du rendezvous.** `[soundness]`
  Aujourd'hui `K_tag` provient de HKDF-BLAKE2s mais `box_id` d'un BLAKE2s à clé brut, tous deux
  sur la même `kpair` — sans principe. Dériver une PRK maîtresse unique depuis `kpair`, puis
  des sous-clés séparées par étiquette. Spécifier la **règle de grâce à la frontière d'époque UTC** (un
  expéditeur déposant à 23:59 et un destinataire sondant à 00:01 ne doivent pas manquer de courrier —
  un vrai bug de livraison). Justifier la largeur de 16 octets de `box_id`. **Fait :** une discipline de KDF,
  la règle de grâce d'époque, des vecteurs régénérés. **Effort M.**

---

## Palier 2 — Le problème central du réseau (OP-1) et son appareil

Le plancher n'est *opérationnellement* réel que si les `n` chemins sont réellement disjoints.
Le vérifier à partir des propres données d'un client — face à des relais qui mentent sur
tout sauf sur leurs signatures — est le problème central déclaré du projet. Le point
honnête le plus profond, que les livrables doivent énoncer à voix haute : **depuis la
surcouche, vous ne pouvez pas vérifier la *vraie* disjonction, seulement la cohérence face à un
jeu de données à confiance bornée ; un adversaire qui co-localise des relais tout en annonçant des
préfixes disjoints est probablement indétectable.** Le travail est de borner ce que cet
adversaire gagne, non de le nier.

- **2.1 — Passe de réalisme du simulateur.** `[keystone]`
  Aujourd'hui `network_sim.py` utilise des étiquettes d'AS *de vérité-terrain* — c.-à-d. il suppose que le
  problème de vérification est déjà résolu. Ajouter : une **couche d'inférence AS/juridiction
  avec erreur injectable** (pour que « inconnu ⇒ supposer partagé » soit exercé),
  des **gardes persistantes** sur un flux de messages (une mauvaise garde est mauvaise pendant des mois),
  un **échantillon de gossip partiel** par client au lieu du bassin en vue d'ensemble, et un
  **adversaire amélioré** (corrélation au niveau de l'AS, le drop compté comme point d'observation de
  sortie, confirmation optionnelle au saut du milieu). **Fait :** courbes de rupture et de liaison
  en fonction du taux d'erreur d'inférence, montrant que les chiffres à erreur nulle d'aujourd'hui étaient
  optimistes. **Effort L.** Débloque presque tout ce qui suit.

- **2.2 — Ébaucher la procédure de vérification de la Partie 3.** `[flagship]`
  L'extension que demande l'issue OP-1 : étant donné un échantillon, un jeu de données d'inférence et
  une confiance par relais, produire `n` circuits **et un certificat vérifiable par machine
  du niveau de disjonction atteint, avec une confiance** — jamais une hypothèse.
  Énoncer la limite honnêtement (« disjoint sous le jeu de données D avec les barres d'erreur de D »), et nommer
  l'adversaire qui triche par co-localisation comme un résidu déclaré, quantifié par 2.1. **Fait :** un
  implémenteur hostile peut construire le sélecteur à partir du texte ; chaque seuil cite une figure du
  simulateur. **Effort L.** Dépend de 2.1 et 2.3.

- **2.3 — Le jeu de données d'inférence IP-vers-AS sans confiance.** `[research risk]` `I-3`
  Comment distribuer et authentifier une carte IP-vers-AS (et une juridiction grossière)
  sans autorité unique : instantanés reproductibles à partir de données publiques BGP/RIR, un
  moyen pour deux clients de savoir qu'ils détiennent la *même* carte (adressage par contenu +
  journal de transparence + racines gossipées), et un traitement honnête du paradoxe d'amorçage
  (un client frais récupère la carte sur des chemins qu'il ne peut pas encore évaluer — un
  moment de confiance-à-la-première-utilisation). **Couture de fusion :** le jeu de signataires de la carte et le
  jeu de signataires des versions logicielles (OP-8, élément 4.1) voudront peut-être être le *même*
  mécanisme. **Fait :** deux clients honnêtes détiennent démontrablement la même carte ou détectent
  qu'ils ne la détiennent pas ; le taux d'erreur de la carte alimente le bouton d'inférence de 2.1. **Effort XL** —
  le résultat honnête pourrait être « carte TOFU + journal de transparence + gossip d'anomalies », non une
  carte canonique.

- **2.4 — Robustesse de la découverte : sybil et éclipse (OP-2).**
  Modéliser la vue échantillonnée sous GR-6/GR-8 avec des fractions d'adversaire par classe de source,
  du roulement et le plafond « aucune classe > ½ » ; implémenter des adversaires par éclipse et par sybil ;
  vérifier si le « ne compter que les relais vérifiés » de PS-10 émousse réellement
  le gonflement de taille par sybils. Puis spécifier le protocole de sondage de bande passante (GR-7) — un
  sondage qui mesure un relais sans révéler le sondeur ni devenir un amplificateur de DoS,
  le remplacement difficile de l'autorité de bande passante de Tor que nous nous sommes
  refusée. **Fait :** courbes de probabilité d'éclipse et de gonflement par sybil ; une
  spécification de sondage constructible. **Effort L.**

---

## Palier 3 — Durcir les constructions pour une vraie implémentation

- **3.1 — Exigences cryptographiques de l'implémentation de référence.** `[soundness]`
  Ce qu'un vrai nœud doit faire que le jouet omet, chacun lié à une menace :
  **GF(2⁸) à temps constant** (les consultations de table de la PoC sont un canal de synchronisation par cache sur les
  octets secrets des parts — une fuite temporelle saperait le plancher même que le projet
  vend), **discipline du CSPRNG** (le plancher est exactement aussi fort que le RNG des coefficients),
  gestion de la rotation nonce/clé à travers les redémarrages, persistance du cache de rejeu,
  résistance au mésusage (l'API doit refuser le texte-clair-sans-AEAD — ce que la PoC
  elle-même fait actuellement), et mise à zéro de la mémoire. **Fait :** une liste de contrôle liée aux
  menaces qu'un implémenteur doit satisfaire. **Effort L.**

- **3.2 — Vecteurs de test formels et conformité inter-implémentations.** `I-1`
  Étendre `vectors.json` pour couvrir chaque construction à clé (PRK HKDF, box ids
  à travers les époques, le chemin de bout en bout chiffrer→découper→déposer→sonder→reconstituer→déchiffrer,
  enregistrements Ed25519 + CBOR canonique, la transcription de poignée de main Noise une fois spécifiée),
  figer les tables GF comme normatives, et **verrouiller par vecteur l'ordre des quartets de `k,n`**
  (les deux parseurs de la PoC divergeaient — désormais corrigé ; un vecteur doit les maintenir
  honnêtes). **Fait :** une seconde implémentation dans un autre langage passe chaque
  vecteur. **Effort M.** Incrémental : ajouter des vecteurs à mesure que chaque construction se stabilise.

- **3.3 — Spécifier la poignée de main de circuit (Noise XK) et son secret persistant.**
  La suite nomme `Noise_XK_25519_ChaChaPoly_BLAKE2s` mais rien ne la spécifie,
  et Sphinx fait déjà un accord de clés par saut — alors **à quoi sert Noise XK ?**
  Résoudre la redondance apparente (un implémenteur hostile ne peut actuellement pas construire
  un nœud interopérable, violant I-1), énoncer les propriétés de secret persistant et
  la fenêtre d'exposition de clé statique ≤7 jours, et décider si le masquage de l'initiateur par XK
  est même nécessaire ou si un schéma plus simple suffit. **Fait :** la poignée de main est
  spécifiée à la complétude I-1, sa relation à Sphinx non ambiguë. **Effort L.**

- **3.4 — Signatures des enregistrements de gossip et CBOR canonique.** `I-1`
  Le CBOR canonique est critique pour la signature : deux implémentations qui divergent sur l'ordre des
  cartes rejettent les enregistrements valides l'une de l'autre. Figer la canonicalisation exacte,
  imposer un profil strict de vérification Ed25519, et fournir des vecteurs inter-implémentations.
  **Fait :** canonicalisation figée, vecteurs existants. **Effort S.** Parallélisable.

---

## Palier 4 — Gouvernance et opérations (protège le projet maintenant et les utilisateurs plus tard)

Les revues se sont accordées sur un cadrage : le projet n'a **encore aucun utilisateur**, ce qui est un
cadeau — le squelette de gouvernance et de confiance de compilation peut être posé calmement *maintenant*,
tant que le changer ne casse personne. L'erreur coûteuse est de livrer un nœud de référence
avec une histoire de mise à jour improvisée, puis d'avoir besoin d'une migration en forme d'autorité pour la
corriger.

- **4.1 — Gouvernance des mises à jour sans bouton d'arrêt (OP-8).** `[élément non-crypto le plus important]`
  Un relevé de décision de conception fixant la *forme* : les compilations reproductibles sont l'ancre de
  confiance ; les signatures ne font que *localiser* une compilation ; l'adoption des mises à jour est locale au client et
  volontaire, jamais imposée. Les 80 % difficiles sont humains, non cryptographiques — *qui* signe,
  comment on les choisit et les remplace pseudonymement, et comment un quorum évite de devenir discrètement
  l'autorité d'annuaire qu'I-3 interdit. **La réponse la plus forte pourrait être
  minimaliste :** compilations reproductibles + empreintes co-publiées + *pas* d'auto-mise à jour
  et *pas* de jeu de signataires faisant autorité, car chaque jeu de signataires est une cible de
  coercition. **Fait :** le document survit à une lecture hostile en quête de l'autorité
  dérobée ; l'auto-audit I-3 nomme le substitut non fiable pour chaque
  partie. **Effort L.**

- **4.2 — Chaîne de compilation reproductible et chaîne d'approvisionnement.** `I-1, I-3`
  Conception (prête pour quand le nœud Rust démarre) : épinglage de la chaîne d'outils, une compilation hermétique ou
  de style Nix, un `rebuild-and-compare` qu'un inconnu peut exécuter, des attestations
  co-publiées, un arbre de dépendances minimal et embarqué, et la réconciliation explicite de
  « les contributeurs doivent être pseudonymes (pas de clés de signature liées à une identité) » avec
  « vérifier l'artefact » — toute la confiance passe par la reproductibilité,
  aucune par l'identité de l'auteur. **Fait :** deux parties sur des machines différentes
  produisent des artefacts à empreinte identique depuis la source étiquetée, via une procédure ne nommant
  aucun singleton de confiance. **Effort L.**

- **4.3 — Économie des dead-drops et métadonnées de récupération (OP-9).**
  Simuler une attaque par inondation avec une étiquette de prix (énigmes client vs les plafonds RZ-7),
  honnête quant à l'écart : une énigme assez dure pour dissuader un botnet peut être
  inabordable sur le téléphone bon marché que le projet prétend servir. Simuler la
  discipline de sondage (RZ-9) face à un drop qui *profile* une boîte, et son coût sur
  le mobile à forfait limité. **Fait :** des paramètres défendus avec le résidu énoncé en
  chiffres. **Effort M.**

- **4.4 — Exposition de l'opérateur et posture de neutralité.** `[politiquement épineux]`
  Un exposé honnête (non juridique) sur ce que l'exécution de chaque rôle révèle et risque,
  s'appuyant sur l'affirmation vraie qu'un drop stocke du bruit illisible et qu'un relais
  retransmet du bruit de taille fixe sans sortie en clair-web ; plus une posture écrite de gestion
  des abus — ce que le projet fera et ne fera pas quand le réseau est utilisé pour
  nuire, étant donné qu'il *ne peut pas* lire ni cibler le contenu par conception, et pourquoi cette
  incapacité est une propriété de sécurité, non une esquive. **Fait :** chaque rôle a une
  déclaration d'exposition en langage clair ; la posture est cohérente avec la clause de
  neutralité et n'introduit aucun levier de modération. **Effort M.**

---

## Palier 5 — Les couches encore non écrites

- **5.1 — Transports caméléon (Partie 4, OP-7).** `[course aux armements]`
  Un modèle de menace du transport et une évaluation honnête du réalisme : dérive de l'empreinte
  uTLS, réalité de déploiement d'ECH en 2026, sondage actif, corrélation de flux. L'argument
  économique « me bloquer coûte plus que cela ne rapporte » a de vrais contre-exemples
  historiques — nommez-les, et posez la question inconfortable de savoir si un
  projet bénévole pseudonyme a la capacité de *maintenance soutenue* qu'une course aux
  armements exige. Résoudre si la dispersion des parts à travers des couvertures diverses *aide*
  (plus de types de couverture) ou *nuit* (plus d'empreintes à ne pas rater). **Effort L.**

- **5.2 — Diversité des liens en blackout / maillage mixte (Partie 5, OP-6).** `[research risk]`
  La plus grande conception non écrite : des téléphones en feuilles contraintes par la batterie,
  des PC/SBC à double radio en ossature 802.11s, et **la dispersion à travers des passerelles indépendantes**
  étendant I-3 à la sortie physique du quartier. Les parties difficiles : adresser
  sans atteignabilité globale ; vérifier l'indépendance des passerelles quand la carte des AS
  est inatteignable à l'intérieur d'un blackout et que la localisation est auto-déclarée (OP-1 récidive
  dans l'espace radio) ; si le paquet Sphinx de 2048 octets survit à un store-and-forward de plusieurs
  heures ou s'il a besoin de son propre encadrement. Et le résidu irréductible à
  énoncer, non à résoudre : **un nœud de maillage dans un blackout brûlant est un acte physiquement
  localisable** qu'aucune surcouche ne peut masquer — aussi la participation au maillage est-elle toujours un choix explicite.
  **Effort XL.**

---

## Le même problème portant trois masques

Un constat a récidivé à travers les trois revues et mérite d'être nommé : l'incapacité à
**vérifier l'indépendance d'une partie sans auto-déclaration** apparaît
pour les *relais* (disjonction des chemins OP-1), pour les *signataires de version* (diversité
juridictionnelle OP-8) et pour les *passerelles de maillage* (indépendance physique OP-6). Une solution à
l'un peut se transférer aux autres. C'est, sans doute, le problème ouvert le plus profond du
projet entier — et la réponse honnête dans chaque cas pourrait être un *résidu borné et déclaré*
plutôt qu'une vérification. C'est cohérent avec la règle au-dessus
de toutes les autres ici : **énoncer où s'arrête le parapluie.**

---

## Chemin critique suggéré

**Maintenant :** Palier 0 (0.1–0.4) — corriger les sur-affirmations connues et la clé manquante.
**Puis l'épine :** 1.1 → 1.2 → 1.3 → 1.4 (prouver ou casser I-2), avec 0.2 (l'AEAD de
bout en bout) replié dedans puisqu'il débloque la vraie démo de composition.
**Puis en parallèle :** 2.1 (clé de voûte du simulateur) et 2.3 (le jeu de données XL, commencé
tôt) → 2.2 (vérification phare de la Partie 3) ; 4.1 (gouvernance) et 4.2
(compilations reproductibles) peuvent avancer indépendamment à tout moment.
**En clôture :** 2.4, durcissement du Palier 3, économie du Palier 4, puis les Paliers non écrits
5.1 et 5.2.

Deux éléments portent une vraie chance de résultat *partiel ou négatif* — 2.3 (des données BGP
reproductibles sans confiance pourraient ne pas être pleinement atteignables) et 5.2 (un maillage préservant
les invariants pourrait n'être que partiellement atteignable). Ce n'est pas une raison de les différer ; c'est la
raison d'être honnête à leur sujet dans un document qui ne promet aucun acte de foi.
