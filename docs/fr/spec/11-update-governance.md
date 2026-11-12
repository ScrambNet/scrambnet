# Spécification ScrambNet — Partie 11 : Gouvernance des mises à jour

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/11-update-governance.md)).

**Statut : BROUILLON (DRAFT).** Cette partie décide comment un client en vient à exécuter un binaire
ScrambNet **plus récent** *sans faire confiance à qui l'a publié*, sous I-3 — aucune autorité —
et sous deux contraintes imposées par le propriétaire du projet : **aucun ensemble de signataires faisant autorité**,
et **aucun push d'aucune sorte**. C'est la couche d'adoption que le §10.9 de la Partie 10 nomme comme hors
de son propre périmètre. La Partie 10 décide *ce binaire est-il la construction de cette source* ; cette
partie décide *quelle construction exécuter, et quand*. Les valeurs d'homme de paille sont marquées `(s)`.

Lisez d'abord le §1 et le §10. Ensemble ils disent ce que cette partie achète (la reproduction
et la fraîcheur, non la signature, comme arbitre de l'adoption) et ce qu'elle concède d'emblée :
refuser à la fois une autorité et un push achète la **latence de correctif** comme son résidu central —
un client vulnérable peut n'être jamais corrigé, et dans le pire cas
(un client déjà compromis par le bug même qu'un correctif réparerait) il peut de façon prouvable
n'entendre jamais même parler du correctif (§10.1). Le projet accepte ce coût délibérément,
parce que l'alternative — une partie ou un canal qui peut pousser (push) une publication à tout le monde
d'un coup — est exactement l'interrupteur de coupure (kill switch) concentré que tout le projet existe pour refuser.

Cette partie réutilise plutôt que de réinventer : l'index de fraîcheur de la Partie 10 (RB-8a), le journal
de publication (RB-13), le gossip (RB-14), la discipline ne-compter-que-les-vérifiées (RB-10/RB-10a) et
l'état du client qui ne reconstruit pas (RB-7b) ; le journal de transparence sans permission de la Partie 8
(ID-6/ID-7), la défense contre l'équivocation de racine diffusée par gossip (ID-7a), la règle des journaux multiples
(ID-7b), et le TOFU déclaré (ID-8) ; le mélange de sources de la Partie 2 (GR-8) ; la surface d'honnêteté
de la Partie 3 (PS-9). La couture avec la Partie 10 est citée, non re-décidée (RB-2, Partie 10 §9).

## 1. La décision, en deux phrases

- **Il n'y a pas d'autorité de publication, et il n'y a pas de push.** Une publication plus récente est un
  artefact reproductible, adressé par contenu, annoncé par un ajout sans permission à un journal
  (UG-2) ; un client *apprend* qu'elle peut exister uniquement en tirant (pull) et en diffusant par gossip selon
  son propre calendrier (UG-3), *décide* de l'adopter par un acte manuel, local, volontaire (UG-4),
  et lie cette décision à la reproduction (RB-7) et à la fraîcheur (RB-9a),
  **jamais** à qui l'a annoncée ou signée (UG-1a, RB-2).
- **La confiance d'adoption passe par la reproduction et la fraîcheur ; la révocation ne peut qu'informer,
  jamais forcer ; et le prix — un client non corrigé ou compromis qui
  n'adopte jamais — est un résidu déclaré, non un problème résolu.** Aucune signature
  ne conditionne l'adoption (UG-2a) ; aucun mécanisme ne retire un mauvais binaire d'un client
  en cours d'exécution (UG-8a) ; le signal known-bad est un signalement sans permission, sans force, ignorable,
  jamais une autorité (UG-8).

Ainsi l'issue honnête : **l'adoption est aussi libre d'autorité que la reproduction la rend,
et aussi fiable qu'un utilisateur qui choisit d'agir et n'est pas éclipsé — pas davantage.** Le §10
est le résidu qu'aucune construction ici ne retire.

## 2. Annoncer une publication sans signataire

- **UG-1 (aucune autorité de publication ; l'adoption est un acte local au client). [normatif]** Aucune
  étape de l'*apprentissage de l'existence*, de la *validation*, ou de l'*adoption* d'une publication plus récente
  NE DOIT (MUST NOT) exiger de faire confiance au fait qu'une partie particulière l'a publiée, annoncée, signée ou bénie.
  Les seules opérations de confiance sont celles que la Partie 10 définit — recalculer `BLAKE2s`,
  reconstruire-et-comparer (RB-1) — plus comparer des index de publication monotones sur une ligne
  (RB-8a, UG-2c). Tout élément qui ne peut être remplacé par un substitut non fiable effectuant
  celles-ci est un défaut sous I-3 et DOIT (MUST) être retiré ou déclaré au §10 (la règle ID-1 /
  RB-1, pour l'adoption des mises à jour).
- **UG-1a (l'adoption se lie à la reproduction, jamais à la publication). [normatif]**
  *Quelle* construction exécuter est décidé par l'ancre de confiance de la Partie 10 — se reproduit-elle
  (RB-7), est-elle fraîche (RB-9a) — et par rien quant à *qui* l'a annoncée. Un client
  NE DOIT PAS (MUST NOT) adopter une construction *parce qu'*elle a été annoncée par une quelconque partie, clé, canal ou
  liste. Cela réénonce RB-2 (les signatures localisent, jamais n'autorisent) à la frontière
  d'adoption que RB-2 défère à cette partie.
- **UG-2 (l'annonce est un ajout sans permission à un journal, aucun appendeur privilégié).
  [normatif]** Une publication est annoncée en ajoutant son tuple de la Partie 10
  `(triple, H_build, manifest-hash, release-index, committer-date)` (RB-8/RB-8a) au(x)
  journal(ux) de transparence sans permission et en ajout seul de RB-13 / ID-6 — la même
  *construction* que le journal de carte, réutilisée comme outillage (RB-2a / ID-11a), jamais comme
  autorité partagée. **N'importe qui PEUT (MAY) ajouter** ; il n'y a pas de liste d'autorisation ni d'ensemble de signataires
  dont l'ajout rend une publication officielle (ID-7). Un journal qui filtrerait les ajouts de publication
  derrière une liste serait l'autorité d'annuaire que I-3 interdit et est
  non conforme (ID-7, RB-2a).
- **UG-2a (aucune signature faisant autorité ; par défaut, aucune). [normatif]** Une publication
  conforme ne porte **aucune signature faisant autorité**. Si une signature pseudonyme
  apparaît, elle n'est qu'un pur localisateur RB-2 — elle attribue une construction à une main
  pseudonyme continue pour la commodité du gossip — et un client DOIT (MUST) traiter une annonce signée et
  une non signée du même `(triple, H_build, release-index)` comme
  portant un **poids d'adoption identique** une fois que la reproduction les corrobore
  (RB-10). Une conception dans laquelle l'acceptation d'une annonce dépend de l'identité d'un
  signataire est non conforme (RB-1, RB-12).
- **UG-2b (la ligne de version n'est possédée par aucune partie). [normatif]** L'index de
  RB-8a est monotone *au sein d'une ligne de version*. Une ligne DOIT (MUST) être définie de sorte qu'aucune
  partie ne possède le droit de l'étendre ; sinon « ajouter un index supérieur » devient une
  autorité de déclarer la publication suivante (l'autorité d'annuaire que I-3 interdit,
  portant un numéro de version). UG-2c donne la construction.
- **UG-2c (l'identité de ligne est une chaîne de manifestes vérifiable par reproduction depuis une
  genèse). [normatif]** Une ligne est identifiée par `line_id = BLAKE2s` de son
  **manifeste de genèse** (le manifeste canonique de la première publication, RB-8a). Une publication
  **étend** `line_id` si et seulement si son manifeste porte le manifest-hash de la publication précédente
  comme champ de prédécesseur explicite **et** que sa source taguée se reproduit vers l'avant (RB-7)
  à partir d'une lignée de sources dont le tag antérieur est celui du prédécesseur — de sorte
  qu'« étendre la ligne » est un **acte sans permission, vérifiable par reproduction** :
  quiconque peut produire un manifeste successeur se reproduisant peut ajouter un index supérieur, et
  aucun dépôt, committer ou clé ne possède la ligne. Un **fork** est tout manifeste qui ne
  s'enchaîne pas à `line_id` ; il porte nécessairement un `line_id` différent et est donc
  **visible comme une ligne distincte**, jamais un index supérieur silencieux injecté dans celle qui est
  suivie (la règle ID-2 « le hachage est le seul nom », pour la lignée de publication). `line_id` est stable
  à travers les publications honnêtes (le hachage de genèse ne change pas) tout en n'étant possédé par personne
  (la chaîne est publique et vérifiée par reproduction) — les deux propriétés que UG-2b exige.

## 3. Découverte sans push

- **UG-3 (la découverte est pull/gossip uniquement ; aucun chemin de push n'existe). [normatif]** Un
  client apprend qu'une publication plus récente *peut* exister **uniquement** en (a) tirant (pull) l'index de fraîcheur
  (RB-8a) et les tuples de journal de la ligne (RB-13) selon son propre calendrier, et en (b)
  diffusant par gossip `(line_id, triple, H_build, release-index)` sur GR-6 sous le mélange de sources GR-8
  (RB-14). Aucun mécanisme de cette partie — et aucun qu'un déploiement conforme
  PEUT (MAY) ajouter — ne pousse (push) une publication, une notification, ou une invite à un client.
  Le chemin plus faible « notifier-la-disponibilité » n'est **explicitement pas adopté** : la fraîcheur
  est tirée (pull) et diffusée par gossip, jamais livrée (la contrainte liante du propriétaire, énoncée
  de façon normative pour qu'un implémenteur ne puisse pas réintroduire un push et rester conforme).
- **UG-3a (aucune source unique ne conditionne la fraîcheur). [normatif]** Un client NE DOIT PAS (MUST NOT) traiter
  le release-index le plus élevé qu'il a vu comme courant sur la parole d'un seul pair,
  journal ou miroir avant d'appliquer GR-8 / PS-10 « ne compter que les sources vérifiées
  indépendamment » (RB-14, ID-9). Sa vue de *ce qui est courant* est une observation à sources mélangées
  sous la même défense contre l'éclipse que ses vues de carte et d'échantillon de relais.
- **UG-3b (la cadence de découverte est locale au client et bornée en confidentialité). [normatif]**
  La cadence de tirage (pull) est une politique locale au client (homme de paille : opportuniste, repliée dans
  les lots de gossip GR-6 existants, jamais une balise distinctive (s)). Le trafic de tirage de fraîcheur
  NE DOIT PAS (MUST NOT) devenir une empreinte ; il chevauche le canal de gossip que le client
  utilise déjà (la discipline de métadonnées GR-8 / Partie 6, appliquée à la découverte de
  mise à jour).
- **UG-3c (un client tire (pull) sur sa propre horloge, jamais en réaction à un signal d'un pair).
  [normatif]** Un client PEUT (MAY) initier une récupération **uniquement** sur sa propre cadence bornée
  en confidentialité (UG-3b) ou sur une action utilisateur explicite. Il NE DOIT PAS (MUST NOT) initier une récupération *en
  réponse à* une divergence, un signal known-bad, ou une équivocation rapportés par un pair : ce
  déclencheur réactif est la rétrogradation de re-récupération ID-9a (le §10 de la Partie 8 signale « traite ta
  carte comme suspecte, re-récupère » comme une direction sous-défendue qu'un adversaire pilote), et
  pour les mises à jour c'est un **push déguisé** (UG-5a). Les anomalies sont remontées et
  diffusées par gossip (UG-7), jamais actionnées par une récupération. C'est la frontière entre « mon
  tirage programmé a remarqué un index supérieur » (autorisé) et « un pair m'a fait aller regarder »
  (interdit).

## 4. Décider d'adopter (choix volontaire manuel, aucun verrou de signature)

- **UG-4 (l'adoption est un acte manuel, local, volontaire). [normatif]** Remplacer le
  binaire en cours d'exécution par un plus récent découvert est une décision que l'**utilisateur** prend
  localement ; aucun client conforme n'adopte une publication automatiquement, sur une minuterie, ou en
  atteignant un quelconque seuil de corroboration. Le seuil régit *ce que le client peut
  proposer ou faire remonter*, jamais *ce qu'il installe*. « Corroborée » est une précondition que le
  client vérifie ; « adopter » est un acte que l'utilisateur pose (la posture ID-8b « détecter, ne pas
  prétendre prévenir », déplacée de la détection vers l'adoption).
- **UG-4a (la liste de contrôle d'adoption — aucun verrou de signature). [normatif]** Avant
  de faire remonter une publication découverte comme *adoptable*, un client DOIT (MUST) avoir, pour son propre
  triple cible et son `line_id` suivi :
  1. **corroboration par reproduction** — `H_build` concorde avec le manifeste, par la
     propre reconstruction du client (RB-7) **ou**, pour le client modal qui ne reconstruit pas
     (RB-7b), un décompte de reproducteurs **vérifiés indépendamment** sous RB-10 (jamais
     un décompte brut d'attestations) ;
  2. **fraîcheur** — un release-index ≥ le plus élevé que le client a témoigné sur cette
     ligne, ordonné dans le journal (RB-9a, RB-8a, UG-2c) ;
  3. **corroboration par journal** — apparition avec des racines diffusées par gossip cohérentes dans un
     quorum configuré des journaux qu'il surveille (ID-7b, homme de paille ≥2 (s)) ;
  4. **aucune équivocation** — aucune anomalie de vue dédoublée UG-6 en suspens contre cette ligne.

  Il n'y a **aucune étape de verrou de signature**, par construction (UG-2a). Un client NE DOIT PAS (MUST NOT)
  présenter aucun de ces éléments comme « vérifié » lorsqu'il n'a qu'une corroboration-par-le-nombre ; il
  porte l'état `reproduit-par-d'autres-non-vérifié` de la Partie 10 jusqu'à l'interface (RB-7b).
- **UG-4b (la politique d'adoption est déclarée, locale au client, conservatrice par défaut).
  [normatif]** La politique qui transforme les vérifications UG-4a en une *proposition* est
  locale au client et DOIT (MUST) être déclarée à l'utilisateur (défaut homme de paille : ne proposer qu'une
  publication plus fraîche par index, corroborée par reproduction au-dessus du seuil du client,
  corroborée par journal en quorum, et exempte d'équivocation ; ne jamais proposer à travers un
  changement de `line_id` (UG-2c) sans une étape utilisateur explicite (s)). Un client PEUT (MAY) exposer une
  politique plus stricte (p. ex. « ne proposer que ce que j'ai moi-même reconstruit ») ; il NE DOIT PAS (MUST NOT) en exposer une
  plus faible que « index plus frais + corroboré en quorum + aucune équivocation », parce que
  plus faible se réduit à adopter sur la parole d'une source unique (UG-3a). **Un signalement
  known-bad de classe vulnérabilité non réfuté (UG-8) NE DOIT PAS (MUST NOT) à lui seul abaisser une publication
  en dessous de ce seuil de proposition** (UG-8, défense H-diffamation).
- **UG-4c (proposer et installer sont mécaniquement distincts). [normatif]** **PROPOSER** est
  la remontée à l'utilisateur d'un état de disponibilité-et-de-corroboration ; il NE DOIT PAS (MUST NOT)
  récupérer le corps de l'artefact en réponse à un déclencheur de divergence ou de known-bad (UG-3c),
  et toute pré-récupération DOIT (MUST) chevaucher la cadence UG-3b de sorte qu'elle n'ajoute aucune balise
  distinctive. **INSTALLER** est un acte initié par l'utilisateur qui remplace le binaire en cours d'exécution.
  Aucune transition automatique de PROPOSER à INSTALLER ne peut exister (UG-10). Une implémentation qui
  pré-prépare un binaire à un tapotement de son exécution, ou récupère sur un signal d'un pair, a construit un
  push et est non conforme même si elle appelle l'étape « proposition ».

## 5. La défense anti-rétrogradation reproductible, côté client

- **UG-5 (ne jamais accepter silencieusement un index inférieur ; le faire remonter). [normatif]** Un client
  NE DOIT PAS (MUST NOT) adopter, ni traiter silencieusement comme courante, aucune publication dont l'index est
  **inférieur** au plus élevé qu'il a témoigné pour ce `line_id` (RB-9a). Un index
  inférieur présenté est la signature à vantage unique d'une **attaque de rétrogradation
  reproductible** — un ancien tag, se reproduisant parfaitement, à vulnérabilité connue, alimenté au
  client (RB-9a) — et DOIT (MUST) être fait remonter à l'utilisateur et diffusé par gossip comme une anomalie
  de rétrogradation (UG-7d), jamais consommé comme une « dernière » ordinaire. Parce que l'index est
  lié à la date de commit dérivée et à la chaîne de manifestes (RB-8a, UG-2c) et
  ordonné dans le journal (RB-13), « index inférieur » est une propriété vérifiable, non un
  jugement.
- **UG-5a (la péremption est remontée, non actionnée). [normatif]** Lorsque le propre
  index en cours d'exécution d'un client tombe en dessous de l'index courant d'un quorum corroboré pour sa ligne, il
  DOIT (MUST) faire remonter la péremption à l'utilisateur (la surface d'honnêteté de PS-9, réutilisée) — *vous
  exécutez une publication plus ancienne que vos pairs corroborés ; une plus récente existe.* Il
  NE DOIT PAS (MUST NOT) agir sur cette remontée en tirant (pull), en invitant-comme-push, ou en adoptant (UG-3c) ;
  il informe, et l'utilisateur décide (UG-4). L'asymétrie honnête avec ID-9a est
  délibérée : la machinerie de la carte *re-récupère* en cas de divergence ; l'adoption de mise à jour ne
  doit **pas** le faire, parce qu'une re-récupération forcée serait un push déguisé. La péremption s'arrête à
  la surface d'honnêteté.

## 6. Vue dédoublée et équivocation sur les publications

- **UG-6 (deux « dernières » différentes à deux clients sont attrapées par les racines diffusées par gossip).
  [normatif]** Un adversaire servant la publication X à Alice et la publication Y à Bob — même
  triple, même `line_id` — est une attaque de vue dédoublée sur la *fraîcheur*, l'attaque ID-7a
  portant un masque de mise à jour. La défense n'est **pas** de faire confiance à l'opérateur du journal ; c'est de
  diffuser par gossip les têtes d'arbre signées des journaux sur GR-6 (à sources mélangées GR-8) et d'exiger
  des **preuves de cohérence** entre deux racines quelconques qu'un client voit (ID-7a, RB-14). Un client
  détenant les deux racines a une preuve cryptographique que le journal a équivoqué et DOIT (MUST) le traiter
  comme hostile (ID-10, UG-7b).
- **UG-6a (l'équivocation d'index est la signature inter-vantages ; désambiguïsée de la
  rétrogradation). [normatif]** La **rétrogradation** (UG-5 / UG-7d) est la signature à *vantage
  unique* : *mon propre* maximum témoigné sur une ligne a régressé. L'**équivocation d'index**
  (UG-7b) est la signature *inter-vantages* : le même `line_id` présenté avec un
  index le plus élevé différent à des vantages différents à sources mélangées **et** les racines des journaux
  échouent à une preuve de cohérence — deux index différents seuls ne sont pas une équivocation (un
  vantage peut simplement être en retard) ; c'est l'**échec de la preuve de cohérence** qui le prouve.
  Un seul événement sous-jacent peut lever les deux signatures (la victime épinglée à un index
  périmé voit une rétrogradation quand elle entend plus tard le plus élevé ; une partie détenant les deux
  racines voit une équivocation) ; il DOIT (MUST) être dédupliqué par `(line_id, racines conflictuelles)`
  (la discipline de déduplication RB-10a, réutilisée) de sorte qu'il soit compté une fois. L'équivocation d'index est
  diffusée par gossip de sorte qu'un client partiellement éclipsé l'attrape auprès de pairs non éclipsés.

## 7. Les anomalies de publication sont diffusées par gossip, non supprimées

- **UG-7 (gossip d'anomalie obligatoire). [normatif]** Cinq événements sont des anomalies de
  publication que tout client DOIT (MUST) diffuser par gossip à la détection, en comparant uniquement des données de
  même triple, même `line_id`, et dédupliquées selon RB-10a : (a) un `H_build` qui échoue à la
  reproduction depuis son manifeste (RB-7a / RB-15a) ; (b) un journal présentant des racines
  incohérentes sur les annonces de publication — équivocation prouvée (RB-15b, UG-6/UG-6a) ; (c) une
  divergence `H_build` de même triple persistante face à des reproducteurs indépendants (RB-15c) ; (d) une
  **régression de release-index** sur une ligne — la signature de rétrogradation
  (UG-5 / RB-15d) ; (e) un **signalement known-bad** (UG-8). Un client NE DOIT PAS (MUST NOT) supprimer une
  anomalie pour faire paraître une publication en bonne santé (ID-10, pour les publications).

## 8. Le problème de la révocation (le difficile)

- **UG-8 (known-bad est un SIGNALEMENT sans permission, corroboré, sans force — jamais une
  révocation faisant autorité). [normatif]** « La publication X est known-bad » ne peut pas être une
  déclaration faisant autorité : *toute* partie à qui l'on fait confiance pour prononcer qu'une publication est mauvaise est un
  interrupteur de coupure (kill switch) (elle peut **censurer** une publication honnête en la déclarant mauvaise — l'autorité I-3
  inversée), donc aucune telle partie n'existe. À la place, cette partie fournit un **signalement
  known-bad** : une affirmation `(line_id, triple, H_build, reason-class, evidence-locator)`
  que **n'importe qui PEUT (MAY) publier et que n'importe qui PEUT (MAY) ignorer**. Les signalements traversent le fil et alimentent
  un décompte, donc ils DOIVENT (MUST) réutiliser **RB-10a verbatim** : CBOR canonique, déduplication par
  `(identité de reproduction du signaleur, line_id, triple, H_build, reason-class)`, et
  poids **par-reproducteur-indépendant, jamais par-chaîne-d'octets-de-signalement** — sans quoi le
  canal est un levier de bourrage-de-format / de diffamation (H-diffamation). La preuve se scinde
  en deux genres :
  - **preuve reproductible (le signalement s'auto-vérifie ; aucune confiance nécessaire)** —
    *non-reproduction* (reconstruire depuis le manifeste et voir RB-7a échouer), *régression
    d'index / rétrogradation* (l'ordre du journal le montre, UG-5), *équivocation de journal* (la
    preuve de cohérence échoue, UG-6). Pour un client qui **peut reconstruire / atteindre un
    reproducteur honnête**, « known-bad » ici se réduit à une vérification de la Partie 10 qu'il exécute lui-même ;
    le signalement ne fait que *localiser* le défaut, il n'*autorise* pas le verdict.
  - **preuve non reproductible (se réduit à un consensus social)** — *« cette construction qui se
    reproduit contient une vulnérabilité / porte dérobée. »* Aucune vérification cryptographique ne tranche cela
    — c'est le résidu d'honnêteté-de-source du §10.1 / OP-10 de la Partie 10. Ici « known-bad » est une
    affirmation pondérée par la révision publique (I-1), le décompte de corroboration, et la reproductibilité
    de-la-preuve-là-où-elle-existe (un PoC qui se reconstruit), et elle se réduit à **OP-2
    et à la couche sociale du projet**. Un **signalement de classe vulnérabilité non réfuté NE DOIT
    PAS (MUST NOT) à lui seul conditionner une proposition** (UG-4b) : il PEUT (MAY) seulement *annoter* la proposition (« N
    parties vérifiées indépendamment allèguent une vulnérabilité ; preuve à … »), jamais
    abaisser la publication en dessous du seuil UG-4a — précisément parce que cette classe est
    votable par sybil (GR-19a) et que conditionner dessus laisserait un adversaire censurer un correctif
    de sécurité honnête en le réduisant à la péremption.

  **Le téléphone modal (RB-7b) ne jouit pas des classes reproductibles.** Un client qui
  ne peut pas reconstruire ne peut pas auto-vérifier un signalement de non-reproduction, et un client
  éclipsé ne peut pas détenir les deux racines dont une preuve d'équivocation de journal a besoin (ID-7a §10). Pour
  le client qui ne reconstruit pas ou qui est éclipsé, **tout sauf la vérification arithmétique de régression d'index
  se réduit à la corroboration RB-10, c.-à-d. OP-2** (la réduction du §10.5 de la Partie 10,
  héritée — voir §10.2). Un client conforme NE DOIT PAS (MUST NOT) auto-agir sur un signalement
  known-bad (cela recréerait le push et l'autorité d'un coup) ; il fait remonter le
  signalement avec son niveau de corroboration et sa classe de preuve, et l'utilisateur décide
  s'il faut s'arrêter ou changer.
- **UG-8a (la révocation ne peut qu'informer ; elle ne peut pas pousser (push), donc elle ne peut pas forcer-corriger).
  [normatif]** Parce qu'aucun push n'existe (UG-3) et qu'aucune autorité n'existe (UG-1), un
  signalement known-bad n'atteint un client que lorsque ce client tire (pull)/diffuse par gossip, et ne change
  rien jusqu'à ce que l'utilisateur agisse. Il n'y a **aucun mécanisme pour retirer un binaire known-bad
  d'un client en cours d'exécution**, et cette partie ne prétend pas en avoir un. Le signal known-bad
  rend une mauvaise publication *détectable et évitable par un utilisateur attentif et non éclipsé* ;
  il ne peut pas la rendre *inexécutable* par décret. C'est le résidu de révocation
  (§10.2), énoncé, non lissé.
- **UG-8b (refus d'exécution auto-vérifiant — libre d'autorité, volontaire, auto-preuve seule).
  [normatif]** Un client qui **lui-même** prouve (RB-7, aucune partie externe) que son
  **propre binaire en cours d'exécution** échoue à la reproduction face au manifeste qu'il a livré — ou que
  son propre index embarqué est une régression qu'il peut vérifier arithmétiquement contre un
  plancher non éclipsé — PEUT (MAY), **en tant que choix volontaire local au client, non un défaut**,
  refuser de continuer à exécuter ce binaire et retomber sur un ré-amorçage (ID-8). C'est
  **libre d'autorité** (la preuve est la propre reconstruction du client, et une fausse preuve de
  non-reproduction est *impossible* — l'adversaire ne peut pas faire que la source publique honnête
  se reproduise vers un mauvais `H`, ID-8a.3) et ce n'est **pas un push** (rien n'est
  installé ; le client refuse d'exécuter du code qu'il a prouvé ne pas être la reproduction de
  sa propre source déclarée — l'analogue à l'exécution de RB-7a, qui déjà *rejette* une
  publication qui ne se reproduit pas à l'adoption). Le refus d'exécution DOIT (MUST) rester **interdit** pour
  toute preuve que le client ne peut pas auto-vérifier — la classe vulnérabilité et tout ce qui
  repose sur un décompte de corroboration ou un plancher de quorum (tous deux OP-2 / falsifiables par éclipse)
  — parce que là un *faux* plancher ou signalement serait un déni de service contre un
  client honnête. Cela protège uniquement le client qui **reconstruit** ; le téléphone modal qui ne reconstruit pas
  (RB-7b) se réduit encore à OP-2 (§10.2), de sorte que UG-8b rétrécit l'écart
  de sûreté de flotte (§10.1) sans le refermer.

## 9. Amorçage : la première mise à jour est du TOFU

- **UG-9 (la première mise à jour hérite du TOFU de premier binaire de la Partie 10 et ne peut pas se vérifier
  elle-même). [normatif]** La vue d'un client de *quelle publication est courante* est médiatisée par
  le binaire qu'il exécute déjà ; un premier binaire compromis (§10.8 de la Partie 10) possède
  tout l'appareil de découverte, de fraîcheur et de gossip du client et peut donc
  **mentir sur la fraîcheur** — épingler l'utilisateur à un index périmé et vulnérable, cacher un
  signalement known-bad à son propre sujet, ou supprimer une équivocation à laquelle il participe. Un
  client ne peut pas honnêtement vérifier sa *propre* récence pas plus que sa *propre*
  reproduction (§10.8 de la Partie 10). La confiance de première mise à jour repose sur la même **corroboration
  indépendante hors bande** que celle du premier binaire : une vue de release-index et de known-bad
  atteinte depuis une machine ou un canal auquel l'utilisateur fait plus confiance qu'au binaire testé. C'est
  du TOFU déclaré (ID-8), non résolu.
- **UG-9a (le premier choix de publication d'un client neuf est du TOFU sur des canaux indépendants).
  [normatif]** À la première installation, un client DOIT (MUST) obtenir son
  `(line_id, index, H_build)` initial sur autant de canaux **indépendants** qu'il en a (§10.8 de la Partie
  10 / ID-8 : la ligne de pont hors bande GR-10 plus ≥2 miroirs sur des réseaux distincts (s)),
  exiger le **même** `(line_id, index, H_build)` de tous avant d'accepter
  provisoirement, et l'enregistrer comme **TOFU-non-vérifié** jusqu'à ce qu'il reconstruise
  (RB-7) ou accumule une corroboration par gossip cohérente. Il DOIT (MUST) faire remonter cet
  état : *vous faites confiance à votre premier client et à votre première notion de « dernière » ;
  ni l'un ni l'autre n'est encore corroboré.*

## 10. Ce que cette partie ne résout pas (le résidu déclaré)

Cette partie déplace la confiance d'adoption des mises à jour de *qui l'a livrée* vers *est-ce que ça se reproduit
et est-ce frais*, et refuse à la fois une autorité et un push — le bon choix pour un
projet dont chaque liste est une cible de coercition. Elle ne livre **pas** une flotte corrigée et
sécurisée. Les lacunes sont réelles et déclarées, non lissées :

- **§10.1 — Le résidu de flotte non corrigée, et son pire cas : aucun push signifie aucun
  correctif forcé, et le client compromis peut de façon prouvable n'entendre jamais parler du correctif.
  [résidu primaire]** Un client dont l'utilisateur n'adopte jamais manuellement — hors ligne,
  inattentif, ou abandonné — exécute sa publication courante, vulnérabilités et tout,
  **indéfiniment** (UG-4). Aucune outrepassation (override) n'existe, parce qu'une outrepassation est un push. Pire,
  les clauses se composent contre la flotte : dans le seul scénario qui compte le plus — un
  client exécutant une **RCE activement exploitée** — le binaire en cours d'exécution est **déjà
  contrôlé par l'attaquant**, et c'est exactement le binaire que UG-9 dit pouvoir mentir sur la
  fraîcheur et supprimer le known-bad à son propre sujet. Donc le mécanisme qui routerait le
  correctif (gossip + surface de péremption, UG-3/UG-5a) s'exécute **à l'intérieur du
  processus compromis** et peut être réduit au silence. La conclusion honnête : pour le cas
  RCE-compromis, la surface d'honnêteté et le chemin de gossip ne fournissent **aucune** garantie
  de livraison ; le résidu n'est pas « une correction plus lente » mais **« le sous-ensemble compromis
  peut n'adopter jamais »**, un état terminal jusqu'à un ré-amorçage hors bande (ID-8),
  borné seulement par le fait que l'utilisateur le remarque par un canal hors du client compromis.
  UG-8b rétrécit cela pour le client qui *reconstruit* et opte (il peut refuser d'exécuter un
  binaire auto-prouvé mauvais), non pour le téléphone modal. C'est le prix délibéré du
  refus d'un push et d'une autorité, et il est nommé en premier et à pleine force.
- **§10.2 — La révocation-sans-autorité est inatteignable pour la classe
  vulnérabilité, et se réduit à OP-2 pour le client modal à travers plus d'une classe.**
  La non-reproduction, la rétrogradation et l'équivocation sont révocables sans autorité *uniquement
  pour un client qui peut reconstruire ou atteindre un reproducteur honnête* (UG-8). « Cette
  construction qui se reproduit a une porte dérobée » n'est jamais sans autorité — aucune vérification ne tranche
  l'honnêteté-de-source (OP-10 / §10.1 de la Partie 10) — donc la révocation d'une publication
  révisée-mais-malveillante repose sur la révision publique (I-1), sur une corroboration dont l'indépendance est
  invérifiable (RB-10 / GR-19a), et sur l'utilisateur choisissant d'agir : OP-2 plus la
  couche sociale. Pour le **client modal qui ne reconstruit pas ou qui est éclipsé**, les classes non-
  reproduction et équivocation-de-journal se réduisent **aussi** à OP-2 (seule la vérification
  arithmétique de régression d'index survit à l'auto-vérification) — la réduction du §10.5 de la Partie 10,
  héritée. La contribution de la conception est de rendre l'*affirmation* known-bad
  sans permission, corroborée, à discipline de déduplication (RB-10a) et **sans force** de sorte qu'elle ne soit
  jamais une autorité ; elle ne contribue **aucun** mécanisme qui retire une publication mauvaise-mais-
  se-reproduisant d'une flotte en cours d'exécution.
- **§10.3 — Le client éclipsé n'entend jamais la mise à jour, et sa machinerie de fraîcheur
  est manipulable.** Un client éclipsé (OP-2) ne touche aucune racine honnête, de sorte que la
  détection d'équivocation de UG-6 **ne peut pas se déclencher** — la victime ne détient jamais deux racines conflictuelles.
  Sous éclipse, un adversaire peut épingler la victime à un **index périmé et à vulnérabilité connue**
  (une rétrogradation silencieuse que UG-5 ne peut pas attraper, parce que la victime ne témoigne jamais de
  l'index supérieur), **supprimer** chaque signalement known-bad sur la construction en cours d'exécution, et
  montrer un passé figé **corroboré par sybil**. La fraîcheur est une garantie *relative* —
  plus fraîche que ce que vous avez témoigné — et un client éclipsé n'a témoigné que de ce que
  l'adversaire a permis. Pour le client éclipsé qui ne reconstruit pas, « aucune autorité,
  pull uniquement » signifie « faire confiance au quorum à sources mélangées », et cela ne tient **qu'aussi loin
  qu'OP-2** — la réduction sur laquelle les Parties 8 et 10 s'achèvent.
- **§10.4 — L'utilisateur qui n'adopte jamais est bloqué par conception.** Le choix volontaire manuel de UG-4 signifie
  qu'un utilisateur qui écarte chaque proposition reste sur une ancienne construction ; il n'y a aucune outrepassation (override),
  parce qu'une outrepassation est un push. La conception accepte une **fraction en régime permanent non nulle
  de la flotte sur des publications périmées** comme le coût déclaré du refus d'un push, et
  fait remonter la péremption (UG-5a) plutôt que d'agir dessus.
- **§10.5 — Le TOFU de première mise à jour hérite du §10.8 de la Partie 10 et est strictement pire pour
  la fraîcheur.** Un premier binaire compromis peut mentir sur la récence aussi facilement que sur la
  reproduction — figeant l'utilisateur à un index périmé pour toujours, indétectablement de l'intérieur
  (UG-9). La première-notion-de-dernière est du TOFU, corroborée seulement hors bande.
- **§10.6 — L'outillage partagé, non l'autorité partagée, doit être ré-audité pour le journal de
  mise à jour.** Réutiliser la construction de journal et le canal de gossip de la carte / de la Partie 10 (RB-2a,
  ID-11a) est gratuit *uniquement* tant qu'aucun rôle de partie n'est porteur à la fois pour la carte/le code
  et pour la ligne de mise à jour. Un déploiement conforme DOIT (MUST) garder les appendeurs du journal de ligne de
  publication comme une non-liste (UG-2) et DEVRAIT (SHOULD) utiliser un ensemble de journaux indépendant de celui de la carte
  (ID-7b), de sorte que « commodité : réutiliser les mêmes opérateurs » ne recrée pas silencieusement
  l'interrupteur de coupure (kill switch) transversal que ID-11 interdit. Le cas fork-ou-échappement est un résidu
  supplémentaire : un fork dur honnête (divergence légitime) et un adversaire ouvrant une
  ligne parallèle pour échapper à une rétrogradation/un known-bad sur la ligne suivie sont
  **indistinguables au niveau du protocole** — les deux sont un nouveau `line_id` (UG-2c).
  UG-2c rend l'*existence* d'une seconde ligne visible ; il ne tranche pas l'*intention*,
  qui est un jugement social / OP-2, non cryptographique.

Le résumé honnête : cette partie refuse à la fois une autorité et un push, et en échange
est **muette** sur le fait de forcer un correctif (§10.1), **ne peut pas révoquer cryptographiquement une
publication révisée-mais-malveillante** (§10.2), **se réduit à OP-2 sous éclipse** (§10.3),
**laisse l'utilisateur qui n'adopte jamais bloqué par conception** (§10.4), et est en **TOFU sur la
première notion de « dernière »** (§10.5). La bonne réponse est de les borner — un gossip
known-bad bruyant, sans permission, à discipline de déduplication (UG-7/UG-8), une surface de péremption
visible (UG-5a), une corroboration de première mise à jour hors bande (UG-9a), un refus d'exécution
volontaire auto-vérifiant pour le reconstructeur (UG-8b), un mélange de sources agressif (UG-3a) —
et d'**énoncer** le compromis de latence de correctif dans l'interface et dans la spécification, non de le cacher derrière
« pas d'auto-mise-à-jour, c'est plus sûr ».

## 11. Exigences introduites ici

- **UG-1 / UG-1a** — aucune autorité de publication ; l'adoption se lie à la reproduction et à la
  fraîcheur, jamais à la publication (réénonce RB-2 à la frontière d'adoption).
- **UG-2 / UG-2a / UG-2b / UG-2c** — annonce par ajout à un journal sans permission, aucun
  signataire ; signé et non signé portent un poids d'adoption identique ; la ligne de version est
  possédée par aucune partie — `line_id` est une chaîne de manifestes vérifiable par reproduction depuis une
  genèse, un fork est une ligne visiblement distincte.
- **UG-3 / UG-3a / UG-3b / UG-3c** — la découverte est pull/gossip uniquement, aucun push ;
  à sources mélangées, bornée en confidentialité, sur l'horloge du client ; jamais une récupération réactive à un signal
  d'un pair (c'est la rétrogradation de re-récupération ID-9a).
- **UG-4 / UG-4a / UG-4b / UG-4c** — l'adoption est un choix volontaire manuel ; une liste de contrôle à quatre
  verrous sans verrou de signature ; une politique conservatrice déclarée ; proposer et installer sont
  mécaniquement distincts sans transition automatique.
- **UG-5 / UG-5a** — ne jamais accepter silencieusement un index inférieur (rétrogradation reproductible) ;
  la péremption est remontée sur PS-9, non actionnée (l'asymétrie délibérée avec ID-9a).
- **UG-6 / UG-6a** — vue dédoublée sur la fraîcheur attrapée par les racines diffusées par gossip + preuves de
  cohérence ; l'équivocation d'index est la signature inter-vantages, désambiguïsée de la
  rétrogradation à vantage unique et dédupliquée.
- **UG-7** — cinq anomalies de publication obligatoires, diffusées par gossip, dédupliquées selon RB-10a.
- **UG-8 / UG-8a / UG-8b** — known-bad est un signalement sans permission, à discipline RB-10a,
  sans force, jamais une autorité ; un signalement de classe vulnérabilité annote mais
  ne conditionne jamais une proposition ; la révocation ne peut qu'informer ; le refus d'exécution
  volontaire auto-vérifiant est libre d'autorité et permis, le refus d'exécution sur preuve externe est
  interdit.
- **UG-9 / UG-9a** — la première mise à jour est déclarée TOFU sur des canaux indépendants ; un
  premier binaire compromis peut mentir sur la fraîcheur, corroborée seulement hors bande.

UG-1 et UG-4 sont les deux porteurs : aucune autorité, et l'adoption est un acte manuel
lié à la reproduction. Les deux sont bornés, non absolus — UG-1 se réduit à OP-2 pour le
client qui ne reconstruit pas ou qui est éclipsé (§10.2, §10.3), et le no-push de UG-4 achète le
résidu de flotte non corrigée (§10.1), dont le pire cas — un client compromis qui
peut de façon prouvable n'entendre jamais parler du correctif — est nommé à pleine force plutôt qu'adouci.
Cassez cette partie en nommant un chemin de push qu'un client conforme PEUT (MAY) ajouter, un signataire qui
conditionne l'adoption, un moyen pour un signalement known-bad de forcer une action ou de censurer une publication
honnête au-delà de UG-4b, un moyen d'étendre une ligne de version sans reproduction (un propriétaire
de la ligne), ou un moyen pour le client qui ne reconstruit pas d'être laissé à faire confiance à une majorité qui n'est pas
OP-2. Telle est l'invitation, dans la voix de la Partie 8.
