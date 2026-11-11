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
  ci-dessous). Nous visons un accusé de réception **sous 7 jours** ; si tu n'as reçu aucune
  réponse passé ce délai, considère-le comme perdu dans la tuyauterie pseudonyme et relance sur
  un ticket public (sans le détail sensible) afin que nous le remarquions.

Merci de ne pas inclure ton identité légale dans un rapport, à moins que tu ne la veuilles
publique. Les rapports pseudonymes sont bienvenus et reçoivent la même considération.

## Portée

Dans la portée : la spécification dans `docs/`, la PoC dans `poc/`. Hors portée : la
sécurité de l'appareil ou du compte d'un contributeur ; la plateforme GitHub elle-même ; le
déni de service contre ce dépôt.

## Clé du projet

Une clé PGP pour `scrambnet@proton.me` est publiée dans le dépôt sous la forme du fichier
[`scrambnet-pubkey.asc`](../../scrambnet-pubkey.asc). Chiffre les rapports sensibles avec elle.

```
Fingerprint: E5B5 399D 751F 830D 35CB  5F4A 3087 9F3B F93D 44F7
Algorithm:   Ed25519 (sign) + Cv25519 (encrypt)
Created:     2026-11-11   Expires: 2028-11-10
```

Vérifie l'empreinte par rapport à ce fichier (et, idéalement, par rapport à une seconde copie de
ce document sur un autre miroir) avant de faire confiance à la clé — l'intérêt de la publier à la
fois dans le texte *et* comme fichier versionné, c'est que les deux doivent concorder.

Pour l'utiliser :

```
gpg --import scrambnet-pubkey.asc
gpg --fingerprint scrambnet@proton.me     # doit correspondre à la ligne ci-dessus
gpg --encrypt --armor -r scrambnet@proton.me your-report.txt
```

**Rotation (pourquoi la clé expire, invariant I-3).** La clé expire dans deux ans ; ce n'est
délibérément pas un singleton immortel. Avant qu'elle n'arrive à échéance, la clé suivante sera
publiée ici et **signée par celle-ci** tant que celle-ci est encore valide, de sorte que la
passation soit vérifiable plutôt qu'un acte de foi. Si cette clé venait à être perdue ou compromise
avant son expiration, un certificat de révocation (généré et conservé hors ligne au moment de la
création) sera publié ici et poussé vers `keys.openpgp.org`, et une nouvelle clé annoncée de la même
manière. Aucune clé de divulgation unique n'est un point de confiance permanent.

## Divulgation

Divulgation coordonnée pour tout ce qui pourrait mettre en danger les utilisateurs d'un futur
déploiement ; discussion publique immédiate pour tout ce qui relève de cette étape pré-alpha,
où il n'y a aucun utilisateur à mettre en danger et où le but est de casser la conception avant que
quiconque ne s'y fie.
