# Cœur de dispersion — PoC de référence

Compagnon exécutable des Parties [1](../docs/spec/01-share-packet.md) et
[6](../docs/spec/06-rendezvous.md) de la spécification.
Python 3 pur, bibliothèque standard uniquement, écrit pour être lu et
attaqué : une spécification exécutable, pas le futur nœud.

Ce qu'il démontre :

- la division Shamir (n, k) sur GF(2^8), octet par octet, et la
  reconstruction à partir de k parts quelconques (SP-1, SP-2) ;
- le plancher inconditionnel (I-2), par force brute : `floor_demo()` énumère
  chaque polynôme cohérent avec k−1 parts observées et trouve les 256 octets
  secrets candidats *exactement également cohérents* — on n'apprend rien,
  même avec une puissance de calcul illimitée ;
- les tags SP-7 à clé du destinataire (BLAKE2s à clé) et la reconnaissance
  par fenêtre de tags qu'ils impliquent ;
- le bourrage aléatoire SP-8 et le format de charge utile de la Partie 1 §4 ;
- le prix honnête : une dispersion (n, k) transmet ×n le volume du chiffré
  (issue #4).

Exécution :

    python3 dispersal.py        # démonstration
    python3 test_dispersal.py   # tests, y compris vectors.json
    python3 rendezvous.py       # démonstration Partie 6 : drops et sondage
    python3 test_rendezvous.py  # tests Partie 6

`vectors.json` contient des vecteurs pour d'autres implémentations : qui les
reproduit interopère à cette couche.

Ce que ce n'est **pas** : du code de production. Pas d'arithmétique à temps
constant, pas de réseau, pas de couche onion, pas d'AEAD de bout en bout
(par SP-1 cette couche ne voit que du chiffré opaque). N'en protégez rien.
