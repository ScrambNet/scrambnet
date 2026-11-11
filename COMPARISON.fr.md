# Comment ScrambNet se situe

Un positionnement honnête face aux systèmes qu'un relecteur nommera, à juste titre, en premier.
Ce document énonce ce que ScrambNet fait *différemment* et — plus important encore —
ce qu'il fait *moins bien*. Si une cellule ci-dessous est fausse, ouvre un ticket : se tromper ici
coûte plus cher que se tromper partout ailleurs dans le dépôt.

## La seule vraie différence

Tout système d'anonymat déployé protège le **contenu** des messages par
une hypothèse de calcul : casse le chiffrement (aujourd'hui ou avec un futur ordinateur
quantique) et le contenu devient lisible. Le plancher de contenu de ScrambNet est
**à sécurité informationnelle** : en deçà de `k` parts capturées, il n'y a aucun texte chiffré à
casser, car le contenu n'est présent dans aucun ensemble de `k−1` parts — une propriété du
partage de secret de Shamir, non de la robustesse d'un chiffrement (invariant I-2). C'est
là tout le pari. Tout le reste ici est de l'art antérieur, composé.

Cette différence ne porte **que sur le contenu**. Pour la **liaison** (qui parle à qui,
les métadonnées), ScrambNet est dans le même combat difficile que tous les autres, et ne fait
aucune promesse informationnelle là-dessus, en mode rapide.

## Côte à côte

| | **ScrambNet** | **Tor** | **Nym / Loopix** | **Briar** |
|---|---|---|---|---|
| Usage principal | Messagerie (asynchrone, par dead-drop) | Navigation à faible latence | Messagerie (mixnet) | Messagerie, P2P |
| Confidentialité du contenu | **Inconditionnelle en deçà de `k` parts** | Calculatoire (TLS + onion) | Calculatoire | Calculatoire |
| Défense contre la liaison | Circuits dispersés + mix (paranoïaque) | Circuits onion | Mixnet de Poisson (fort) | Onion + graphe de contacts |
| Annuaire / découverte | **Aucun** — gossip + échantillon vérifiable | ~9 autorités d'annuaire | Validateurs / nym-api | Introduction par contacts |
| Adversaire global passif | Hors modèle (rapide) / mix (paranoïaque) | Hors modèle | **Dans le modèle** (mixnet) | Partiel |
| Blackout / hors ligne | Maillage local, store-and-forward | Non | Non | **Oui** (Bluetooth/Wi-Fi) |
| Couche d'incitation | Aucune (bénévolat) | Bénévolat | **Jeton** | Bénévolat |
| Maturité | **Spéc pré-alpha + PoC** | Production, plus de 20 ans | Production | Production |

## Là où ScrambNet est en retard, dit sans détour

- **Maturité.** Tor, Nym et Briar sont déployés, audités et transportent du trafic
  réel aujourd'hui. ScrambNet est une spécification et une preuve de concept en Python.
  Personne ne devrait encore y faire passer un vrai secret, et le dépôt le dit.
- **Conception du mixnet.** Nym/Loopix ont une conception de mix de Poisson rigoureuse et publiée
  avec un modèle d'adversaire global passif. Le mode paranoïaque de ScrambNet est un
  espace réservé (OP-5) tant que personne n'a fait ce travail ici aussi.
- **Métadonnées de liaison.** Le schéma de récupération par dead-drop fuite la cadence de
  sondage vers un drop à l'intérieur d'une époque (OP-9) — un coût que le mixage continu de
  Nym amortit plus à fond.
- **Bande passante.** Le plancher inconditionnel coûte `×n` en bande passante (×4 au
  strawman). Tor coûte ×1 pour sa garantie de contenu plus faible. C'est le prix
  du pari, non un défaut, mais c'est un prix réel (OP-3).
- **Incitations.** Nym paie les relais ; ScrambNet demande des bénévoles, ce qui plafonne
  historiquement la croissance.

## Pourquoi le construire quand même

Parce que la garantie de contenu de tous les autres systèmes porte une date de péremption inscrite
dans les hypothèses de 2003–2017, et que « moissonner maintenant, déchiffrer plus tard » est une
stratégie d'adversaire bien réelle contre des dissidents dont les messages doivent rester illisibles
pendant des décennies. Un plancher de contenu que ni les progrès de la cryptanalyse ni ceux du
quantique ne peuvent éroder vaut une facture de bande passante `×n` et le travail de bâtir le reste.
Si ce pari est faux, le moyen le plus rapide de le découvrir est de l'attaquer ici.
