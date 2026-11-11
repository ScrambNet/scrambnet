# ScrambNet — Modèle de menace

> Un réseau qui promet une protection totale ment, et les personnes qui courent de vrais risques
> méritent de savoir exactement où s'arrête le parapluie. Ce document est le contrat.

## Adversaires et résultats

| Adversaire | Capacité | Réponse du réseau | Résultat |
|---|---|---|---|
| Observateur local (votre FAI, un Wi-Fi de bureau) | Surveiller votre trafic | Voit un flux TLS ordinaire vers une adresse ordinaire | **Protégé** |
| Censeur national | Bloquer des IP, faire correspondre des empreintes DPI, énumérer des ponts | Transports caméléon ; ponts distribués le long du graphe social avec des niveaux de confiance à la Lox | **Protégé** (une course aux armements, mais soutenable) |
| Relais malveillant sur un chemin | Observer ce qui le traverse | Voit un saut d'une part ; les paquets Sphinx sont identiques partout | **Protégé** |
| Opérateur de la garde *et* de la sortie d'un circuit | Corréler le temps entrée/sortie | Ce circuit transporte une part, non le message ; les gardes sont stables pendant des mois ; le mode paranoïaque ajoute des délais de mixage | **Atténué** |
| Adversaire à `k` chemins (tient garde+sortie sur `k` des `n` chemins de parts simultanément) | Corrélation temporelle complète plus capture de parts | La sélection des chemins impose des gardes, des AS et des juridictions disjoints, faisant de `k` positions simultanées un problème d'occupation | **Atténué** — c'est le risque résiduel assumé par conception ; augmentez `n`, `k` à votre goût |
| Adversaire passif global (voit tout le trafic partout) | Tout corréler | Mode rapide : rien. Mode paranoïaque : mixnet avec délais et trafic de couverture | **Hors modèle (mode rapide)** — déclaré, comme Tor le déclare |

## Ce que la dispersion change, précisément

Le routage en oignon classique échoue *catastrophiquement* sur un seul mauvais tirage : contrôlez la garde et
la sortie de l'unique circuit et vous obtenez à la fois la liaison (qui parle à qui) **et**, là où le
chiffrement propre à la destination est absent ou cassé, le contenu. Sous dispersion :

- Le **contenu** est inconditionnellement protégé en dessous de `k` parts capturées. Aucune hypothèse
  calculatoire n'est en jeu. Ce plancher ne peut être érodé par la cryptanalyse ni par les progrès du quantique.
- La **liaison** (métadonnées) sur un unique chemin de part violé reste une vraie perte : l'adversaire
  apprend qu'*un certain* flux a circulé entre vous et le collecteur de parts d'une destination.
  La dispersion rétrécit ce qu'un seul circuit trahit ; elle ne l'annule pas. Des gardes stables,
  une sélection de chemins disjoints par AS et le mixage du mode paranoïaque sont les atténuations.

## Hypothèses

1. Les réseaux sous-jacents (FAI, IXP, câbles, nuages) sont hostiles ou compromis.
2. La conception, le code et tous les documents sont pleinement connus de chaque adversaire (Kerckhoffs).
3. Les relais sont tenus par des inconnus ; une fraction constante est malveillante et conspire.
4. Les extrémités sont honnêtes : un téléphone compromis a perdu avant que le premier paquet ne parte.
   La sécurité de l'appareil est hors périmètre, énoncé sans faux-semblant.
5. Les utilisateurs peuvent obtenir le client. Les compilations reproductibles plus une spécification publique (quiconque peut
   réimplémenter de zéro) sont la réponse à l'empoisonnement des binaires et à la disparition
   de tout canal de distribution officiel.

## Non-objectifs

- Protéger un utilisateur dont l'appareil est compromis.
- Masquer *qu*'une région utilise des outils de contournement dans l'ensemble (mode rapide).
- La modération de contenu à la couche réseau. Le réseau transporte des paquets, pas des opinions ;
  il protège les dissidents et leurs adversaires avec les mêmes mathématiques. Une infrastructure
  n'est crédible que si elle ne peut pas choisir son camp.

<a id="open-problems"></a>
## Problèmes ouverts

Marqués pour l'attaque. Chaque problème se discute à **un** seul endroit : une
unique [issue](https://github.com/ScrambNet/scrambnet/issues) par problème, avec
le texte anglais et toutes les traductions dans le même fil. Lisez le problème
ici dans votre langue ; discutez-en là, dans l'unique issue, pour qu'aucune
discussion ne se disperse.

1. **Imposition de la disjonction.** Un premier mécanisme de sélection de chemins existe désormais en brouillon
   ([spécification Partie 3](spec/03-path-selection.md)) avec un homme de paille exécutable dans
   `poc/network_sim.py` ; ce qui reste ouvert est le cœur difficile : comment un client *vérifie-t-il*
   que `n` chemins ne partagent pas un AS, une juridiction, un centre de données — en n'utilisant que son échantillon
   de gossip et un jeu de données d'inférence distribué sans confiance (I-3), face à des relais qui peuvent mentir
   sur tout sauf sur leurs signatures ?
2. **Résistance aux sybils et aux éclipses** de l'échantillonnage de gossip sans allocateur central.
   Walking Onions suppose un instantané signé par une autorité ; nous avons retiré l'autorité. Qu'est-ce qui
   remplace sa fonction anti-sybil — preuve de clés à long terme ? pondération par le graphe social ?
   vérification de la bande passante par sondage aléatoire ?
3. **Économie des paramètres.** Valeurs par défaut de `n`, `k` par classe de trafic ; quand la dispersion d'information de Rabin
   (moins chère, calculatoire) remplace-t-elle Shamir (inconditionnel) pour les données de volume, et cette
   dégradation est-elle jamais acceptable par défaut ?
4. **Corrélation temporelle des parts.** La non-liaison du contenu entre les parts (SP-7) est réglée et
   implémentée dans la PoC ; le *temps* ne l'est pas. `n` parts entrant dans le réseau en l'espace de
   quelques millisecondes sont elles-mêmes une empreinte. Gigue, regroupement, parts leurres : que coûte chacun
   en latence, et qu'achète-t-il réellement face à un adversaire qui surveille plusieurs
   sorties ?
5. **Économie du trafic de couverture** en mode paranoïaque sur des connexions mobiles à forfait limité.
6. **Adressage en blackout.** Routage par identité sur un maillage store-and-forward sans
   DHT atteignable depuis l'intérieur du blackout.
7. **Amorçage sans aucun contact** pour la distribution des ponts par le graphe social.
8. **Gouvernance des mises à jour.** Versions à multi-signature réparties entre juridictions : combien de signataires,
   comment choisis, comment remplacés — sans créer le comité qui devient le bouton d'arrêt.
9. **Métadonnées et économie des dead-drops.** Un drop voit les temps de dépôt et la cadence de sondage d'une
   boîte au sein d'une même époque (spécification Partie 6). Distributions de sondage et coût des leurres sur des connexions
   à forfait limité, sémantique de suppression, tarification des dépôts contre l'inondation, incitations au stockage :
   que coûte chaque défense, et que fuite chacune ?
