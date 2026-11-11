# Spécification ScrambNet — Partie 7 : L'argument de sécurité pour I-2

> **Traduction informative.** La version canonique et normative est l'anglaise ([en](../../en/spec/07-security-argument.md)).

**Statut : BROUILLON (DRAFT).** Cette partie démontre, ou borne, l'unique affirmation sur laquelle tout le reste repose : le plancher de contenu inconditionnel (I-2). Elle est normative là où elle énonce une exigence (`SA-n`) et explicative ailleurs. Si l'argument présenté ici est faux, le projet est faux, et le moyen le plus rapide de le découvrir est d'attaquer *ce fichier*.

L'affirmation est délibérément étroite. Lisez d'abord les deux phrases du §1 ; tout ce qui suit en est la justification et le prix.

## 1. Ce qui est démontré, en deux phrases

- **Niveau inconditionnel (le plancher).** Un adversaire qui observe `k−1` quelconques des `n` parts d'un message n'apprend **rien** sur le texte chiffré de bout en bout — non pas « rien de faisable », mais rien du tout, face à un calcul non borné et à n'importe quel futur ordinateur quantique — parce que les `k−1` parts sont *statistiquement indépendantes du secret* (Shamir, démontré au §3).
- **Niveau calculatoire (la ceinture).** Un adversaire qui obtient `k` parts ou plus reconstruit le texte chiffré et affronte alors l'AEAD de bout en bout ; à partir de là, la confidentialité du contenu est exactement la confidentialité de ChaCha20-Poly1305 sous une clé que l'adversaire ne détient pas (SP-1a), ce qui **est** une hypothèse calculatoire.

Ces deux niveaux sont **disjoints et exhaustifs** : tout adversaire détient soit `< k` parts (niveau 1), soit `≥ k` (niveau 2), et la garantie de chacun est énoncée sans référence à l'autre. Le reste de cette partie démontre rigoureusement le niveau 1, énonce précisément pourquoi le niveau 2 ne peut pas être inconditionnel, et cloue l'unique endroit où les deux niveaux pourraient se contaminer (§4 : la clé AEAD doit être invisible en dessous de `k`).

## 2. Modèle et adversaire

- Un **message** est une chaîne d'octets `M`. L'expéditeur calcule d'abord le texte chiffré `C = AEAD-Seal(K, N, M)` (SP-1a), où `K = HKDF(kpair, "e2e-content")` et `N` est le nonce du message. C'est `C` — jamais `M` — qui entre dans la dispersion.
- La dispersion est un `(n, k)` Shamir sur GF(2⁸), **par octet** : pour la position d'octet `j`, l'octet secret `c_j` est le terme constant d'un polynôme de degré `(k−1)` indépendant et uniformément aléatoire `f_j`, et la part `i` à la position `j` est `f_j(i)` pour des points d'évaluation non nuls distincts `x_1,…,x_n ∈ GF(2⁸)\{0}` (les indices de part). « Indépendant, uniforme » est porteur et constitue lui-même une exigence (SA-3 ci-dessous).
- L'**adversaire en dessous de `k`** voit : `k−1` parts complètes quelconques (chaque position d'octet de ces `k−1` indices), plus tout ce qui est public — la spécification, les points d'évaluation, `n`, `k`, les octets sur le fil des autres paquets. Il **ne** voit **pas** `K`, `N`, ni aucune part au-delà de ses `k−1`. Il dispose d'un calcul non borné.
- Nous démontrons une propriété de `C` (le texte chiffré). Ce que l'adversaire veut en définitive est `M` ; le §4 montre que le résultat au niveau de `C` se transfère à `M` parce que `K` n'est pas dans la vue de l'adversaire.

## 3. Le plancher : `k−1` parts quelconques sont indépendantes du secret (niveau 1)

**SA-1 (secret parfait par octet).** Fixons une position d'octet `j`. Soit l'octet secret `s = c_j` et le polynôme `f_j(x) = s + a_1 x + … + a_{k−1} x^{k−1}` avec `a_1,…,a_{k−1}` indépendants et uniformes sur GF(2⁸). Pour tout ensemble de `k−1` points non nuls distincts `x_{i_1},…,x_{i_{k−1}}` et toutes valeurs cibles `y_1,…,y_{k−1}` :

> le nombre de tuples de coefficients `(a_1,…,a_{k−1})` cohérents avec `f_j(x_{i_t}) = y_t` pour tout `t` est **exactement un, pour chaque candidat `s`**.

*Démonstration.* Fixons `s`. Les `k−1` équations `f_j(x_{i_t}) = y_t` sont linéaires en les `k−1` inconnues `a_1,…,a_{k−1}` ; leur matrice de coefficients est la matrice de Vandermonde sur les points non nuls distincts `x_{i_t}` (colonnes `x, x², …, x^{k−1}`), qui est inversible sur le corps. Donc pour chaque `s` il existe exactement une solution. Par conséquent `Pr[parts = (y_1,…,y_{k−1}) | secret = s]` est le même (`= 1 / 256^{k−1}`) pour chaque `s` : les parts sont **indépendantes de `s`**. ∎

C'est l'énumération que le PoC exécute par force brute pour `k = 3` (`poc/dispersal.py`, `floor_demo()` — les 256 octets candidats reviennent tous également cohérents, d'une seule façon chacun). SA-1 est l'énoncé général de ce que cette démonstration vérifie pour un cas.

**SA-2 (le secret entier, pas un seul octet — indépendance conjointe).** Soit le texte chiffré `C = c_1 c_2 … c_L` (les `L` octets). L'expéditeur tire les tuples de coefficients des `L` positions **indépendamment** (SA-3). Alors la vue complète des `k−1` parts — les chaînes d'octets de longueur `L` détenues aux `k−1` indices — est *conjointement* indépendante de `C` :

> `Pr[vue = v | C = c]` est identique pour chaque `c ∈ (GF(2⁸))^L`.

*Démonstration.* La vue se factorise sur les positions : les octets que l'adversaire voit à la position `j` ne dépendent que de `(c_j, a^{(j)}_1,…,a^{(j)}_{k−1})`, et d'une position à l'autre les tirages de coefficients sont indépendants (SA-3). Donc `Pr[vue = v | C = c] = ∏_{j=1}^{L} Pr[vue_j = v_j | c_j]`, et par SA-1 chaque facteur vaut `1/256^{k−1}` indépendamment de `c_j`. Le produit est par conséquent `1/256^{(k−1)L}` pour **chaque** `c`. L'indépendance de `C` s'ensuit. ∎

SA-2 est l'étape que les anciens tests du PoC **ne** couvraient **pas** : `floor_demo()` porte sur un seul octet et les tests statistiques ne vérifiaient qu'une marginale (la distribution d'une seule position). L'argument du produit sur les positions est ce qui fait du plancher un énoncé sur le *message*, et il ne tient **que parce que** les coefficients par position sont indépendants — ce qui est exactement le mode de défaillance contre lequel SA-3 prémunit.

**SA-3 (l'aléa des coefficients est critique pour le plancher). [normatif]** Les coefficients du polynôme `a^{(j)}_t` DOIVENT (MUST) être tirés d'un RNG cryptographiquement sûr, indépendamment à la fois selon l'indice de coefficient `t` et la position d'octet `j`. Le plancher est exactement aussi fort que cet aléa et pas davantage :

- **La réutilisation entre positions** (p. ex. un tuple de coefficients réutilisé pour chaque octet, ou un court flux de clé répétitif de coefficients) casse l'indépendance de SA-2 : la factorisation échoue, les `k−1` parts deviennent *corrélées* à `C`, et un adversaire peut obtenir de l'information sur `C` en corrélant les positions entre elles. Un plancher bâti sur des coefficients réutilisés n'est pas un plancher.
- **Un RNG à faible entropie** (un générateur faible ou prévisible) effondre le tirage uniforme de SA-1 : si l'adversaire peut prédire ou énumérer la distribution des coefficients, le décompte « exactement un tuple cohérent par `s` » n'est plus uniforme sur `s`, et les parts fuient.

C'est l'exigence d'implémentation la plus importante de toute la spécification. Elle est bon marché à satisfaire et catastrophique à manquer, et, contrairement à une faiblesse de l'AEAD, elle ne peut pas être corrigée en faisant tourner une clé plus tard — un message découpé avec de mauvais coefficients est compromis pour toujours. Une implémentation conforme DOIT (MUST) traiter le RNG des coefficients comme son composant à la plus haute assurance (voir aussi les exigences de crypto de référence, roadmap 3.1).

## 4. La couture : la clé AEAD doit être invisible en dessous de `k` (aucune fuite entre niveaux)

SA-2 démontre que les `k−1` parts sont indépendantes du **texte chiffré `C`**. L'adversaire veut le **texte en clair `M`**. Le pont est que `M = AEAD-Open(K,N,C)` et que l'adversaire en dessous de `k` ne détient pas `K`. Cela n'est vrai que si `K` n'apparaît jamais dans quoi que ce soit que cet adversaire voie — ce qui est une exigence, non une coïncidence :

**SA-4 (séparation des clés à travers le plancher). [normatif]** Aucune valeur dérivable par un adversaire en dessous de `k` ne peut révéler `K = HKDF(kpair, "e2e-content")` ni `kpair`. En particulier :

- `K` NE DOIT PAS (MUST NOT) être placée dans une part, une étiquette ou un champ de paquet. (Dans cette conception, elle ne l'est pas : `K` n'est utilisée qu'aux extrémités, pour sceller et ouvrir `C` ; les parts transportent des octets de `C`, et l'étiquette SP-7 est dérivée d'une clé *séparée par étiquette* `HKDF(kpair, "tag")`, non de `K` — voir §5 et SP-7a.)
- Par conséquent la vue d'un adversaire en dessous de `k` est indépendante de `C` (SA-2) **et** ne porte aucune information sur `K`. Il ne peut ni lire `C` (il n'y a rien) ni obtenir `K` pour attaquer un futur `C`. Les deux niveaux ne se contaminent pas.

Si SA-4 était violée — si une valeur observable en dessous de `k` était une fonction de `K` — le plancher cacherait toujours *ce* `C`, mais l'adversaire pourrait moissonner `K` et le lire à l'instant où il obtiendrait plus tard `k` parts, ou lire *d'autres* messages sous le même `K`. SA-4 est ce qui empêche le niveau inconditionnel de devenir silencieusement calculatoire.

## 5. Pourquoi le niveau 2 est calculatoire, dit honnêtement

À `k` parts ou plus, l'adversaire reconstruit `C` exactement (interpolation de Lagrange — c'est le chemin *prévu*, c'est ainsi que le destinataire lit son courrier). À partir de `C`, la confidentialité de `M` est précisément la confidentialité de ChaCha20-Poly1305 sous `K`. C'est une hypothèse calculatoire : elle peut en principe être cassée par cryptanalyse du chiffrement. Elle **n'est pas** cassée par un futur ordinateur quantique via Shor, car `K` provient d'un secret *symétrique* pré-partagé sans transcription Diffie-Hellman à inverser (SP-1a) ; Grover coûte au plus une division par deux de la longueur effective de clé, d'où la recommandation de ≥256 bits. Donc l'énoncé honnête du niveau 2 est : *aussi fort qu'un AEAD symétrique sous une clé que l'adversaire ne possède pas, et pas davantage* — une garantie calculatoire réelle, conventionnelle, consciente du quantique, non une garantie inconditionnelle. Le projet ne prétend jamais autre chose, et chaque document public énonce désormais le régime (roadmap 0.1).

## 6. Ce que cette partie **ne** démontre **pas**

- **Liaison / métadonnées.** I-2 porte sur le contenu, pas sur qui parle à qui. Rien ici ne cache que *quelque* flux a eu lieu sur un chemin de part capturé ; c'est le résidu admis du modèle de menace, rétréci par la dispersion, non annulé.
- **Disponibilité.** Une partie hostile sur un chemin de part peut corrompre ou laisser tomber une part ; l'AEAD échoue en fermeture sûre (SP-7a), donc il s'agit d'un déni de service, non d'une divulgation. SA-1…SA-4 ne disent rien sur l'*arrivée* du message, seulement sur ce qu'un adversaire en dessous de `k` *apprend* s'il n'arrive pas.
- **Corrélation temporelle entre parts (SP-9 / OP-4).** SA-2 porte sur les *valeurs* des parts, non sur leurs instants d'émission. `n` parts entrant dans le réseau en quelques millisecondes forment une empreinte même si leurs octets sont indépendants de `C`. C'est un problème ouvert, non quelque chose que cette démonstration traite.
- **L'AEAD lui-même.** Le niveau 2 hérite de tout ce qui est vrai de ChaCha20-Poly1305. Si ce chiffrement tombe, le niveau 2 tombe ; le plancher (niveau 1), non.

## 7. Exigences introduites ici

- **SA-1** — secret parfait par octet de `k−1` parts quelconques (démontré).
- **SA-2** — indépendance conjointe sur le secret entier (démontré, étant donné SA-3).
- **SA-3** — *l'aléa des coefficients est critique pour le plancher* : CSPRNG, indépendant par position et par coefficient. **[normatif, plus haute assurance]**
- **SA-4** — séparation des clés à travers le plancher : aucune valeur observable en dessous de `k` ne révèle `K` ni `kpair`. **[normatif]**

SA-1 et SA-2 sont des théorèmes ; SA-3 et SA-4 sont les deux conditions sous lesquelles les théorèmes décrivent le système réel. Cassez l'un des quatre — trouvez une vue que la démonstration a manquée, une corrélation que SA-3 laisse passer, un champ qui transporte `K` — et vous aurez cassé I-2. Telle est l'invitation.
