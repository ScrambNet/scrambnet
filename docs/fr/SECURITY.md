# Politique de sécurité

ScrambNet est en pré-alpha : une spécification et une preuve de concept, pas encore un système avec
lequel protéger de vrais secrets. La contribution la plus précieuse que tu puisses apporter est une
cassure.

## Ce qui compte comme signalement

- Une faille dans la **conception** : un moyen de lire le contenu en deçà de `k` parts capturées ; un
  moyen de relier les parts d'un même message (SP-7) ; une attaque par éclipse, sybil ou
  défaisant la disjonction contre la découverte ou la sélection de chemins ; tout ce qui
  viole un invariant (I-1…I-4).
- Une faille dans le code de la **preuve de concept** sous `poc/`. Note que la PoC
  utilise délibérément une arithmétique à temps non constant et des constructions jouets ; ce sont
  des non-objectifs documentés, pas des signalements. Un écart par rapport à la spécification, ou un
  défaut de la spécification que le code révèle, est un signalement.

## Comment signaler

- **Failles de conception et problèmes de la PoC qui ne sont pas sensibles :** ouvre un ticket public.
  La discussion ouverte est la raison d'être de ce dépôt.
- **Tout ce que tu estimes devoir être traité d'abord en privé :** écris à
  `scrambnet@proton.me`. Chiffre les rapports sensibles avec la clé du projet (voir
  ci-dessous). Nous visons un accusé de réception dans un délai raisonnable ; tiens compte d'un
  projet pseudonyme, au rythme du bénévolat.

Merci de ne pas inclure ton identité légale dans un rapport, à moins que tu ne la veuilles
publique. Les rapports pseudonymes sont bienvenus et reçoivent la même considération.

## Portée

Dans la portée : la spécification dans `docs/`, la PoC dans `poc/`. Hors portée : la
sécurité de l'appareil ou du compte d'un contributeur ; la plateforme GitHub elle-même ; le
déni de service contre ce dépôt.

## Clé du projet

Une clé PGP pour `scrambnet@proton.me`, destinée aux rapports chiffrés, sera publiée
ici et dans le dépôt. Tant qu'une clé signée n'est pas listée dans ce fichier, traite
le courriel comme confidentiel-mais-non-authentifié et garde les détails les plus sensibles
pour un canal que tu peux vérifier.

## Divulgation

Divulgation coordonnée pour tout ce qui pourrait mettre en danger les utilisateurs d'un futur
déploiement ; discussion publique immédiate pour tout ce qui relève de cette étape pré-alpha,
où il n'y a aucun utilisateur à mettre en danger et où le but est de casser la conception avant que
quiconque ne s'y fie.
