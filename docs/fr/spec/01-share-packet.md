# Spécification ScrambNet — Partie 1 : Paquet de part

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/01-share-packet.md)).

**Statut : BROUILLON (DRAFT).** Les tailles homme de paille sont marquées `(s)`. Attaquez-les par numéro d'exigence.

## 1. Portée

Le paquet de part est la seule unité qui traverse la surcouche : il transporte une part d'un
message à travers un circuit en oignon. Tout dans cette partie sert deux objectifs :
le plancher inconditionnel (I-2) et l'uniformité sur le fil (I-4).

## 2. Mise en couches

```
message en clair
  └─ AEAD de bout en bout (clé de paire pré-partagée, SP-1a)  [calculatoire]
       └─ découpe de Shamir : n parts, seuil k           [plancher inconditionnel]
            └─ chiffrement en oignon par part, circuit propre, format Sphinx
                 └─ transport caméléon (Partie 4)
```

- **SP-1.** L'expéditeur DOIT (MUST) appliquer le chiffrement de bout en bout *avant* la dispersion, et
  la dispersion DOIT (MUST) être appliquée au texte chiffré de bout en bout. Avec moins de `k`
  parts, l'adversaire n'apprend rien sur le texte chiffré, inconditionnellement
  (Shamir) ; avec `k` parts ou plus, il affronte encore l'AEAD de bout en bout. Le
  plancher inconditionnel et la ceinture calculatoire se composent ; aucun ne remplace
  l'autre. La ceinture est démontrée de bout en bout dans `poc/e2e.py` (chiffrer →
  découper → reconstruire → déchiffrer, fermeture sûre en cas d'altération).
- **SP-1a (établissement de la clé de contenu, et la conséquence post-quantique).** La clé
  AEAD de bout en bout DOIT (MUST) être dérivée du **secret symétrique de paire pré-partagé**
  `kpair` porté par la carte de contact (Partie 6, RZ-2), au moyen d'une KDF séparée par
  étiquette : `content_key = HKDF-BLAKE2s(kpair, "e2e-content")`, distincte de la clé
  d'étiquette SP-7 et de la clé d'identifiant de boîte dérivées du même `kpair`. Il NE DOIT
  PAS (MUST NOT) y avoir d'accord de clé asymétrique dans le chemin du contenu. C'est un choix
  délibéré à la conséquence porteuse : un adversaire `≥k` qui enregistre tout et dispose d'un
  futur ordinateur quantique à grande échelle ne peut toujours pas lire le contenu, car il
  n'existe aucune transcription Diffie-Hellman que Shor puisse casser — seulement un secret
  symétrique que les parties partagent déjà, et Grover coûte à l'AEAD au plus une division par
  deux de la force de sa clé (d'où une clé dérivée de ≥256 bits RECOMMANDÉE là où la marge
  importe). « Harvest now, decrypt later » (récolter maintenant, déchiffrer plus tard) est donc
  défait aux **deux** niveaux : en dessous de `k` par Shamir (inconditionnel), à `k` ou au-delà
  par un AEAD symétrique sous une clé pré-partagée (aucune hypothèse de clé publique à
  récolter). Le prix honnête est le **bootstrap** : `kpair` doit d'abord parvenir au destinataire
  par un canal confidentiel préalable (l'échange hors bande de carte de contact, Partie 6).
  Toute hypothèse résiduelle de clé publique ou de PQ-KEM réside là, dans l'échange de carte —
  pas dans le chemin du contenu — et acheminer un échange de carte lui-même post-quantique est
  un choix orthogonal et en couches, non une condition préalable au plancher. La suite AEAD est
  ChaCha20-Poly1305 (suite `0x01`) ; `msg_nonce` (SP-7) est le nonce de l'AEAD, ce qui lie les
  deux couches et rend un nonce réutilisé doublement fatal (collision d'étiquette SP-7 *et*
  perte de confidentialité de l'AEAD — voir SP-7).
- **SP-2.** Paramètres de dispersion par défaut pour la messagerie : `n = 4`, `k = 3` (s).
  Les profils de transfert de volume PEUVENT (MAY) utiliser la dispersion d'information de Rabin au lieu de Shamir, et DOIVENT (MUST) être
  étiquetés comme calculatoires dans l'IU du client, car l'IDA n'a aucun plancher
  inconditionnel (OP-3).

## 3. Format sur le fil

- **SP-3.** Chaque paquet sur chaque lien DOIT (MUST) faire exactement `P = 2048` octets (s).
- **SP-4.** Chaque octet du paquet DOIT (MUST) être indiscernable d'un aléa uniforme
  pour un observateur dépourvu des clés pertinentes, à chaque saut (propriété de
  Sphinx ; I-4). En particulier, il n'y a pas de version, de suite, de longueur, de
  compteur de sauts ni d'index de part en clair.

Disposition (tailles homme de paille, maximum 3 sauts) :

| Champ | Taille (s) | Visible par |
|---|---|---|
| `alpha` — élément de groupe Sphinx (X25519) | 32 o | tout le monde (uniforme) |
| `beta` — info de routage Sphinx, 3 × 48 o, complétée | 144 o | pelée par saut |
| `gamma` — MAC par saut | 16 o | saut courant |
| `delta` — charge utile, enveloppée par AEAD à chaque saut | 1856 o | segment sortie → destinataire |

- **SP-5.** Les relais DOIVENT (MUST) maintenir un cache de rejeu des valeurs `gamma` vues par époque
  de clé et DOIVENT (MUST) écarter les rejeux silencieusement (défense de rejeu Sphinx standard).
- **SP-6.** Les relais DOIVENT (MUST) émettre les paquets en lots de taille constante avec une gigue
  définie par l'implémentation en mode rapide, et DOIVENT (MUST) suivre la stratégie de mixage
  (stop-and-go ou mixage de Poisson, à déterminer) en mode paranoïaque. Le choix de la stratégie est
  du ressort d'OP-5 et délibérément non résolu ici.

## 4. Charge utile de la part (à l'intérieur de `delta`, fin du circuit)

Déchiffrée par le destinataire seul :

| Champ | Taille (s) | Notes |
|---|---|---|
| `tag` | 16 o | étiquette PRF à clé du destinataire, voir SP-7 |
| `index` | 1 o | index de part `1..n` |
| `params` | 1 o | `k`, `n` empaquetés (4 bits chacun) |
| `share` | 1792 o | octets de la part de Shamir |
| `pad` | reste | aléatoire |

- **SP-7 (aucune liaison inter-chemins).** Deux parts du même message NE DOIVENT PAS (MUST NOT)
  porter une valeur égale ou corrélable observable par quiconque sauf le
  destinataire. L'appartenance à un ensemble de parts n'est signalée que par `tag` :
  `tag = PRF(K_r, msg_nonce ‖ index)` où `K_r` est une clé détenue par le destinataire et
  `msg_nonce` est porté à l'intérieur de la couche de bout en bout. Un relais de sortie, ou une
  coalition de sorties, NE DOIT PAS (MUST NOT) pouvoir dire si deux paquets appartiennent au
  même message. Cette exigence est porteuse : sans elle, la dispersion
  se dégrade en une commodité d'énumération pour l'adversaire.
- **SP-7a (intégrité de la part : résidu accepté à fermeture sûre).** Le `tag` indique *à quel*
  message un paquet prétend appartenir ; il n'authentifie **pas** les octets de `share` ni l'octet
  de `params` (`k,n`). La reconstruction de Shamir n'a aucune intégrité propre, de sorte qu'un
  relais ou une sortie hostile qui inverse des bits dans une part — ou ment sur `k,n` — produit un
  candidat de texte en clair cohérent-mais-faux que Shamir ne peut détecter. Cela est **rattrapé
  une couche au-dessus** : l'AEAD de bout en bout (SP-1a) échoue à vérifier son étiquette sur toute
  reconstruction corrompue, et le destinataire écarte le message plutôt que d'agir sur des données
  corrompues (démontré dans `poc/dispersal.py`, test `test_tampered_share_fails_closed`). Le résidu
  n'est donc **pas une perte de confidentialité mais un déni de service ciblé** : un unique point de
  vue malveillant sur l'un des `n` chemins de part peut faire échouer la reconstruction d'un message
  précis, au prix d'un seul bit inversé. Le verdict pour ce brouillon est d'**accepter et documenter**
  ce résidu plutôt que d'ajouter un MAC par part, pour deux raisons : (1) un authentificateur par
  part dépenserait des octets de charge utile et introduirait une seconde clé à gérer sans supprimer
  le DoS — un relais qui peut corrompre une part peut tout aussi bien la *supprimer*, et `n−k` pertes
  de ce type sont déjà tolérées par conception ; (2) l'AEAD rend déjà l'échec sûr (fermeture sûre),
  de sorte que la question ouverte est la disponibilité, non le secret. Les mesures d'atténuation
  honnêtes sont la redondance (marge `n−k`), la disjonction des chemins pour qu'aucun point de vue
  unique ne se trouve sur `k` des `n` chemins (OP-1), et la réémission sur des chemins neufs. Une
  révision future PEUT (MAY) ajouter une liaison optionnelle par part pour les profils où la
  disponibilité est critique ; elle n'est délibérément pas imposée ici. `k,n` est verrouillé par
  vecteurs (ordre des quartets, vecteurs de la Partie 3 §3.2), de sorte qu'une implémentation ne peut
  pas être en désaccord *par accident*, seule une partie malveillante peut mentir.
- **SP-7b (aucune `tag` égale parmi des drops en collusion, et propriété du nonce).** La propriété
  qui doit tenir : aucun deux paquets qu'une coalition de drops peut voir ne portent une `tag` égale
  à moins que l'expéditeur n'ait réutilisé une paire `(msg_nonce, index)`. *Argument :*
  `tag = PRF(K_r, msg_nonce ‖ index)` avec `msg_nonce` fixé à 8 octets et `index` fixé à 1 octet, de
  sorte que l'entrée de la PRF est un encodage à largeur fixe non ambigu de `(msg_nonce, index)` — l'application
  `(msg_nonce, index) ↦ entrée` est injective. Une PRF BLAKE2s à clé ne donne des sorties égales que
  sur des entrées égales (hormis une collision de ~`2^-128`), de sorte que des étiquettes égales
  impliquent un `(msg_nonce, index)` égal. Les `n` parts d'un message partagent un seul `msg_nonce`
  mais utilisent des index *distincts* `1..n`, d'où des entrées distinctes, d'où des étiquettes
  distinctes : une coalition de drops ne peut pas distinguer deux parts d'un message de deux paquets
  sans rapport. Deux messages *différents* ne font collisionner une `tag` que s'ils réutilisent un
  `msg_nonce`. Par conséquent **la propriété du nonce est un DOIT (MUST)** : un expéditeur NE DOIT PAS
  (MUST NOT) réutiliser un `msg_nonce` sous un même `kpair`. La réutilisation est doublement fatale —
  elle fait collisionner les étiquettes SP-7 (rendant un ensemble de parts liable) *et*, parce que
  `msg_nonce` est le nonce de l'AEAD (SP-1a), elle détruit la confidentialité de ChaCha20-Poly1305 (un
  masque jetable réutilisé, épinglé par `test_nonce_reuse_is_detectable_catastrophe`). Un compteur de
  messages par `kpair` strictement croissant satisfait cela ; la ligne de crue du compteur DOIT (MUST)
  survivre aux redémarrages. À la couche de stockage, un drop DOIT (MUST) écarter un re-dépôt d'un
  `(box_id, slot)` déjà stocké (rejeu) et expulse le plus ancien d'abord sous le plafond par boîte
  (RZ-7), de sorte qu'un dépôt rejoué ne multiplie ni ne déplace le courrier honnête au-delà du plafond
  déclaré.
- **SP-8.** Un message qui ne remplit pas la charge utile de la part (`1792` octets, moins
  le préfixe de longueur de 2 octets) DOIT (MUST) être complété d'octets aléatoires avant la découpe ;
  un message qui la dépasse est fragmenté à une couche au-dessus de celle-ci
  (conception de la fragmentation à déterminer, interagit avec OP-4). Le prix honnête de Shamir : chaque
  part est aussi longue que le secret, de sorte qu'une dispersion (n, k) transmet ×`n` le
  volume de texte chiffré (OP-3).
- **SP-9 (temps).** L'expéditeur NE DOIT PAS (MUST NOT) émettre les `n` parts en une rafale
  simultanée. Les parts DEVRAIENT (SHOULD) être émises avec un délai aléatoire par part ; la
  distribution et son coût en latence relèvent d'OP-4 et sont non résolus. Les clients PEUVENT (MAY)
  émettre des parts leurres (paquets à `tag` aléatoire) à un débit configurable.

## 5. Le handshake de circuit (il n'y en a pas — c'est Sphinx)

La suite nommait autrefois `Noise_XK_25519_ChaChaPoly_BLAKE2s` comme un « handshake de
circuit » que rien ne spécifiait, un défaut I-1 : un implémenteur hostile ne pouvait pas
construire un nœud interopérable, car il n'existait aucune transcription à construire.
**La résolution est de supprimer la ligne.** Sphinx réalise déjà l'accord de clé par saut
dont un circuit a besoin, de sorte qu'un handshake Noise séparé est un vestige — hérité
très probablement de la lignée des « handshakes Noise » de WireGuard sans qu'on remarque
que Sphinx avait déjà avalé le travail. Cette section consigne cette décision et spécifie,
de façon normative, le handshake que Sphinx *est*, de sorte qu'I-1 est satisfait par
spécification, et non par un second protocole.

**La décision, en un paragraphe.** `alpha` (SP-3, 32 o, X25519) est un *éphémère client par
paquet* ; chaque relais dérive le secret de saut de `alpha` et de sa clé statique `onion`
(GR-2 clé 2). C'est un Diffie-Hellman éphémère–statique par saut, assurant la forward secrecy
*à la granularité de l'époque* (CH-6), avec authentification du relais via la signature
Ed25519 de l'enregistrement de gossip — exactement ce dont un circuit a besoin et tout ce
dont il a besoin. Un second handshake `Noise_XK` à état ré-exécuterait le même DH, ajouterait
des allers-retours qu'une part dispersée en un coup ne peut pas se permettre, poserait un
second format sur le fil du lien qu'I-4 devrait alors blanchir, et n'achèterait qu'**une**
propriété qui manque à Sphinx : cacher la clé statique de l'*initiateur*. Le client de circuit
de ScrambNet n'a **aucune clé statique** (il est anonyme par construction), de sorte que cette
propriété est vide. `XK` authentifie la machinerie d'une clé qui n'existe pas. Remplacer Sphinx
par XK (plus d'allers-retours pour moins), ou utiliser XK pour un canal auxiliaire (chaque flux
client↔relais à état — gossip GR-6, sondage GR-12/GR-13 — est délibérément tunnelé *à travers*
Sphinx pour que le client reste innommé, de sorte qu'aucun tel canal ne veut de session directe),
tous deux échouent à l'examen. La spécification est meilleure une fois la ligne supprimée.

```
  LE « HANDSHAKE » EST L'EN-TÊTE SPHINX. RIEN D'AUTRE N'EXISTE.

  client (pas de clé statique)  garde G          milieu M          sortie X
  ─────────────────────────    ───────          ────────          ──────
   par paquet : choisir UN SEUL éphémère x ; alpha_0 = x·B   (B = base X25519)
        │
        │  paquet de part  [ alpha_0 | beta | gamma | delta ]   (SP-3)
        │────────────────────────▶│
        │     G: s_G = DH(alpha_0, onion_G) ─► clé de saut ; peler une couche beta
        │     G: alpha_1 = blind(alpha_0)   (re-randomisation Sphinx)
        │                          │────────────────▶│
        │                          │  M: s_M = DH(alpha_1, onion_M) ─► clé de saut
        │                          │                  │──────────▶│
        │                          │                  │  X: s_X = DH(alpha_2, onion_X)
        ▼                          ▼                  ▼           ▼
   AUCUN RTT de handshake. AUCUN second format sur le fil. AUCUN message Noise. Le DH est
   éphémère(client)·statique(relais) à CHAQUE saut, porté entièrement dans `alpha`.

   Ce que Noise XK aurait ajouté, et pourquoi c'est supprimé :
      → e ; ← e,ee,s,es ; → s,se   (RTT en plus, le relais nomme une session, et le
      troisième message porte la statique INITIATEUR que XK existe pour cacher — que notre
      client sans clé n'a pas, donc rien à envoyer et aucune raison de l'exécuter)
```

- **CH-1 (supprimer le vestige).** La suite `0x01` n'a **aucun** handshake Noise ; la ligne
  de la table des suites de la Partie 0 est retirée. Une implémentation NE DOIT PAS (MUST NOT)
  émettre, attendre ni négocier un quelconque message de handshake Noise sur un circuit ; un
  paquet qui n'est pas un paquet de part de la Partie 1 ne fait pas partie de ce protocole.
  *Attaquez ceci en nommant une opération de circuit que l'en-tête Sphinx ne peut pas réaliser
  — une révision hostile a essayé et n'en a trouvé aucune.*
- **CH-2 (le handshake de circuit est l'en-tête Sphinx).** L'accord de clé par saut DOIT (MUST)
  être la construction Sphinx de SP-3/SP-4 : pour chaque saut `i`, le relais calcule
  `s_i = X25519(alpha_i, onion_i)` où `alpha_i` est l'élément de groupe aveuglé qu'il reçoit et
  `onion_i` est sa clé statique (GR-2 clé 2). Toutes les clés de saut (chiffrement de flux de
  l'info de routage, le MAC `gamma`, l'AEAD `delta`) DOIVENT (MUST) être dérivées de `s_i` par
  HKDF-BLAKE2s avec des étiquettes fixes distinctes (`"sphinx-rho"`, `"sphinx-mu"`,
  `"sphinx-delta"` — octets exacts verrouillés par vecteurs sous la feuille de route 3.2). Il
  n'y a aucun autre accord de clé dans la couche circuit.
- **CH-3 (l'initiateur est sans clé, par construction).** Un client de circuit NE DOIT PAS
  (MUST NOT) posséder ni présenter de clé statique de long terme sur le chemin du circuit. Son
  seul secret asymétrique est le scalaire **éphémère par paquet** `x` derrière `alpha_0`, qui
  DOIT (MUST) être fraîchement échantillonné depuis un CSPRNG par paquet (la feuille de route 3.1
  s'applique — la forward secrecy ci-dessous est exactement aussi forte que ce RNG) et détruit
  après la construction du paquet. Sans clé statique client, aucun motif cachant l'initiateur n'a
  rien à cacher ; `XK`/`IK`/`KK` sont tous inapplicables au chemin du circuit (CH-7).
- **CH-4 (authentification statique du relais, sans signature de handshake).** Un client DOIT
  (MUST) obtenir la clé statique `onion` de chaque relais *uniquement* depuis un enregistrement
  de gossip dont il a vérifié (GR-4) la signature Ed25519 (GR-2 clé 7) sur l'encodage canonique —
  qui couvre la clé 2. L'authentification du relais est **hors ligne et transférable** : une
  fois, lors de la validation de l'enregistrement, non interactivement par circuit. Il NE DOIT
  PAS (MUST NOT) y avoir de signature de relais dans le circuit (ce serait un sélecteur et une
  empreinte sur le fil, I-4). La limite honnête : un client authentifie *la clé*, non une
  *identité au-delà de cette signature* — le résidu sybil/eclipse réside dans la Partie 2 (OP-2,
  GR-19a/GR-20a), pas ici.
- **CH-5 (rotation de la clé statique — la fenêtre d'exposition ≤7 days).** Un relais DOIT (MUST)
  faire tourner sa clé statique `onion` au moins tous les `7 days` (s), et DOIT (MUST) remettre à
  zéro la moitié privée d'une clé retirée une fois passé le délai de grâce des paquets en vol ; un
  relais qui conserve d'anciennes statiques agrandit sa propre fenêtre d'exposition et n'est pas
  conforme. Les clients DOIVENT (MUST) rejeter un enregistrement dont l'`expiry` dépasse
  `created + 7 days` (GR-2 clé 6). Le plafond de rotation est imposé aux deux extrémités et
  constitue le plafond de la fenêtre de compromission de la statique (CH-6).
- **CH-5a (l'écart `ee`, et le correctif qui n'est pas XK).** Une révision hostile a nommé la
  seule propriété que la suppression coûte : parce que le DH de saut est éphémère(client)·
  **statique**(relais), un adversaire qui enregistre le trafic de lien d'un relais puis saisit sa
  statique `onion` *à l'intérieur de l'époque vivante* peut recalculer les secrets par saut de
  cette époque et récupérer la **liaison** d'un saut pour jusqu'à 7 days de paquets enregistrés
  (jamais le contenu — CH-6). Un `ee` Noise refuserait même cela. C'est une vraie régression par
  rapport à un handshake *interactif complet*, mais ce n'est **pas** une raison de garder `XK`
  (dont le camouflage de l'initiateur ne la ferme pas) et c'est fermable sans handshake : un
  déploiement qui juge la fenêtre trop large DOIT (MUST) soit (a) **raccourcir la rotation** en
  deçà de 7 days (CH-5 est un plafond, non une cible), soit (b) ajouter une **pré-clé de relais
  `ee` optionnelle** — une pré-clé éphémère de courte durée publiée dans l'enregistrement de
  gossip, mélangée au secret de saut à **zéro** aller-retour supplémentaire — tournée et détruite
  de sorte qu'une saisie tardive de la statique ne donne rien pour sa durée de vie. Le champ
  d'enregistrement de la pré-clé et sa rotation relèvent de GR-2 si un déploiement l'adopte ;
  CH-5a règle seulement que l'écart est réel, borné à la liaison, et fermable sans le handshake
  supprimé.
- **CH-6 (l'énoncé de forward secrecy, précisément).** `[claim-critical]` Un adversaire qui
  compromet la clé privée **statique** `onion` du relais `R` à l'instant `T` (et rien d'autre —
  les éphémères n'ont jamais quitté les clients et ont été détruits, CH-3) : (a) **le trafic passé
  est sûr d'une époque à l'autre** — les paquets dont le saut en `R` a utilisé une statique
  antérieure, tournée-et-détruite, ne sont pas déchiffrables (la clé a disparu, CH-5 ; le
  logarithme discret de l'éphémère client a disparu, CH-3) ; la forward secrecy est à la
  granularité de l'époque, la rotation ≤7 days étant cette granularité. (b) **À l'intérieur de
  l'époque vivante, l'exposition est la *liaison* d'un saut, jamais le contenu** — pour les paquets
  envoyés tant que la statique saisie était vivante, l'adversaire recalcule `s_i` pour les sauts en
  `R` et pèle la couche de `R`, apprenant le prédécesseur/successeur de `R`, c.-à-d. les métadonnées
  qu'un relais malveillant voit déjà. Cela ne donne **aucun** contenu : inconditionnel en dessous
  de `k` (I-2, Partie 7), et au-dessus de `k` l'AEAD de bout en bout est clavé depuis un `kpair`
  symétrique pré-partagé sans transcription DH que la clé saisie puisse toucher (SP-1a). Une
  statique saisie achète *la liaison d'un saut sur les paquets d'une époque* — exactement la
  corrélation garde+sortie que la conception de dispersion/disjonction traite déjà comme
  *atténuée, non éliminée* ; compromettre la statique ne mène l'adversaire pas plus loin que le
  fait de *faire tourner* ce relais déjà.
- **CH-7 (le camouflage de l'initiateur n'est pas nécessaire ; le saut a la forme `N`, non `XK`).**
  `[claim-critical]` Le client a-t-il besoin de la propriété de statique-initiateur-cachée de XK ?
  **Non**, de façon dirimante : le client n'a pas de clé statique d'initiateur (CH-3), de sorte que
  la propriété est vide. Dans le vocabulaire de Noise, le saut en un coup est un accord à sens
  unique, à initiateur éphémère et répondeur à statique connue — la forme de Noise `N` (`→ e, es`),
  non `XK`. Le circuit n'utilise aucun message Noise littéral (CH-2 : c'est Sphinx, qui subsume
  cette forme) ; les deux messages que XK ajoute au-delà de `N` ne portent rien et n'existent que
  pour authentifier une clé que nous n'avons pas. Le camouflage de l'initiateur est déjà fourni
  plus fortement par Sphinx (uniformité SP-4 ; le client n'est jamais une extrémité qu'un relais
  peut nommer, GR-12). Nous avons remplacé le camouflage de l'initiateur de XK par *« l'initiateur
  est anonyme et sans clé »*, qui n'a besoin d'aucun motif pour cacher ce qui n'est pas là.
- **CH-8 (les sessions relais↔relais, s'il en existe un jour, sont hors de cette partie et ne sont
  pas `XK`).** Un futur canal de contrôle ou de peering nécessitant une session à état,
  bidirectionnelle et mutuellement authentifiée entre deux parties **nommées** (p. ex. le
  chiffrement de lien relais-à-relais) est un document séparé et DOIT (MUST) tout de même
  satisfaire I-4 (CH-9). Même là, `XK` est faux : les statiques des deux relais sont **publiques**
  dans leurs enregistrements de gossip, de sorte qu'il n'y a rien à cacher et un motif à statique
  déjà connue (`IK`/`KK`) convient. Cette section ne spécifie aucun tel canal ; elle interdit
  seulement de ré-importer `XK` par réflexe.
- **CH-9 (I-4 en n'ayant aucun second format sur le fil).** `[claim-critical]` La couche circuit
  ne met rien sur le fil sinon des paquets de part de la Partie 1, chaque octet uniforme (SP-4). Il
  n'y a **aucun** message de handshake Noise à rendre uniforme — l'issue I-4 la plus propre,
  obtenue en *n'ayant pas* de second protocole. Une transcription Noise XK a une structure
  reconnaissable (motif de longueur de message, champs de clé publique `e`/`s`) ; garder XK aurait
  *ajouté* une exigence d'obfuscation que la suppression retire. Tout futur canal de session (CH-8)
  hérite de cette obligation dans son propre document.

**Ce que la section 5 ne décide pas.** Les paramètres Sphinx eux-mêmes (groupe, aveuglement, MAC,
étiquettes HKDF exactes et chaînage) sont au §3 et dans les vecteurs de la feuille de route 3.2 ;
CH-2 y renvoie. Post-quantique : la suite `0x02` peut remplacer le DH de saut X25519 par une KEM
PQ — la *forme* de forward secrecy de CH-6 est inchangée (éphémère + rotation statique ≤7 days), la
primitive change, et le plancher de contenu I-2 est PQ-sûr quoi qu'il en soit (SP-1a). Le canal
relais↔relais (CH-8) et le champ de pré-clé `ee` optionnelle (CH-5a) sont laissés aux parties
futures. CH-4 authentifie une *clé qu'un enregistrement a signée*, non une identité au-delà :
le résidu gossip/eclipse est celui de la Partie 2 (OP-2).

## 6. Ce que cette partie ne décide pas

La sélection des chemins et l'imposition de la disjonction (OP-1), les paramètres de mixage (OP-5),
la fragmentation (SP-8), l'économie des leurres (SP-9) sont ouverts à dessein. Chacun a une
issue numérotée ; argumentez là, avec des chiffres.
