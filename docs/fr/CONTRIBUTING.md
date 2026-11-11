# Contribuer à ScrambNet

Le projet est au stade de pré-spécification. Les contributions les plus précieuses en ce
moment, par ordre :

1. **Attaquez le modèle de menace.** Ouvrez une issue contre toute affirmation de
   [docs/threat-model.md](threat-model.md), en particulier la liste des problèmes ouverts.
2. **Proposez du texte de spécification.** Des PR contre `docs/` — de style RFC, un mécanisme
   par PR.
3. **Traduisez.** Les README existent en six langues ; `docs/` n'est pour l'instant qu'en
   anglais. Les traductions et corrections par des locuteurs natifs sont des contributions de
   premier plan.
4. **Signalez les travaux antérieurs.** Si quelque chose ici réinvente la roue, nommez la roue.
   La philosophie de conception est de composer un travail publié et attaqué, jamais d'inventer
   là où une citation suffit.

## Comment nous travaillons

- Un sujet par issue. Les débats de conception vivent dans les issues, les décisions sont
  consignées dans `docs/`.
- L'anglais est la langue canonique de `docs/` ; si vous modifiez un README dans une langue,
  mettez à jour les autres ou indiquez dans la PR qu'ils sont désormais périmés.
- Pas de code tant que le modèle de menace et la spécification du protocole ne se sont pas
  stabilisés. Quand le code démarrera : un unique client de référence petit, ennuyeux et
  mobile-first.

## Politique de pseudonymat

Les vrais noms ne sont pas requis et ne le seront jamais. Les contributions pseudonymes et
anonymes sont de premier plan. Il n'y a pas de CLA ; en contribuant, vous publiez votre
contribution à la documentation sous [CC0 1.0](LICENSE).

Si votre propre modèle de menace l'exige, protégez-vous :

- Utilisez l'adresse noreply de votre forge dans les commits :
  `git config user.email "USERNAME@users.noreply.github.com"`
- Committez en UTC pour que votre fuseau horaire ne fuite pas :
  `git config alias.ci '!TZ=UTC git commit'`
- Ne signez pas les commits avec une clé liée à votre identité légale ; si vous signez,
  utilisez une clé créée pour ce seul pseudonyme.
- Ne réutilisez pas de pseudos employés ailleurs, et rappelez-vous que le style de la prose
  est une empreinte.

## Neutralité

Ce réseau transporte des paquets, pas des opinions. Il protège les dissidents et leurs
adversaires avec les mêmes mathématiques ; les adversaires politiques ne sont pas des ennemis.
Les propositions qui amèneraient le réseau à favoriser ou défavoriser des points de vue, des
origines ou des destinations particulières seront refusées quel que soit le point de vue —
cette neutralité est l'argument de sécurité du projet autant que son éthique.
