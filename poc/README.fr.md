# Cœur de dispersion — PoC de référence

Compagnon exécutable des Parties [1](../docs/fr/spec/01-share-packet.md) et
[6](../docs/fr/spec/06-rendezvous.md) de la spécification.
Python 3 pur, bibliothèque standard uniquement, écrit pour être lu et
attaqué : une spécification exécutable, pas le futur nœud.

Ce qu'il démontre :

- la **composition SP-1 complète**, exécutée, non affirmée : `e2e.py` chiffre
  le message sous une clé de paire pré-partagée (ChaCha20-Poly1305, vérifiée
  contre les vecteurs de test RFC 8439), puis `dispersal.send()` divise le
  *chiffré* et `receive()` reconstruit et déchiffre — encrypt → split →
  reconstruct → decrypt, une part inversée échouant en position fermée à
  l'AEAD, jamais reconstruite en déchets (SP-1, SP-1a) ;
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

    python3 e2e.py              # ceinture SP-1 : KAT AEAD + aller-retour seal/open
    python3 test_e2e.py         # suite de tests AEAD (vecteurs RFC 8439)
    python3 dispersal.py        # démo : SP-1 complet encrypt->split->...->decrypt
    python3 test_dispersal.py   # tests, y compris vectors.json
    python3 rendezvous.py       # démonstration Partie 6 : drops et sondage
    python3 test_rendezvous.py  # tests Partie 6
    python3 network_sim.py      # expérience : adversaire k-chemins vs taille
    python3 test_properties.py  # tests statistiques de propriétés (uniformité, SP-7)
    python3 run_all.py          # chaque démo + chaque test, un verdict

## L'expérience : ce que l'adversaire achète, en chiffres

`network_sim.py` transforme les questions ouvertes des issues #2/#4/#10 en une
table. Il modélise un message comme n=4 parts sur 4 circuits disjoints vers 4
drops ; un adversaire à k chemins possède une fraction des relais et « voit »
un circuit quand il en détient à la fois le guard et l'exit :

    expéditeur                                     drops (une part chacun)
      |  part 1 --[guard]--[mid]--[exit]-->  box 1  \
      |  part 2 --[guard]--[mid]--[exit]-->  box 2   |  le destinataire
      |  part 3 --[guard]--[mid]--[exit]-->  box 3   |  relève, prend 3
      |  part 4 --[guard]--[mid]--[exit]-->  box 4  /   au choix, reconstr.

- **vus >= k** -> rupture du contenu (et seulement alors ; sous k le plancher
  I-2 tient inconditionnellement, à toute taille) ;
- **vus < k** -> contenu sauf, mais chaque circuit vu révèle tout de même
  qu'*un* flux a circulé — la perte de métadonnées que le modèle de menace
  admet : la dispersion la réduit, ne l'annule pas.

Le résultat imprimé : les ruptures de contenu sont rares et disparaissent
quand le réseau grandit assez pour bâtir des circuits AS-disjoints ; la fuite
de lien est petite mais non nulle et pire sur un réseau minuscule qui *ne peut
pas* les bâtir — d'où la nécessité, pour un jeune réseau, d'un « mode petit
réseau » dégradé et déclaré (issue #4). Chiffres provisoires : reproduisez-les,
cassez le modèle, discutez sur les issues.

`vectors.json` contient des vecteurs pour d'autres implémentations : qui les
reproduit interopère à cette couche.

Ce que ce n'est **pas** : du code de production. L'AEAD dans `e2e.py` est en
Python pur et **n'est pas à temps constant** — il est correct (il reproduit les
vecteurs RFC 8439) mais fuit par le timing, donc un vrai nœud DOIT utiliser une
bibliothèque à temps constant éprouvée. Pas d'arithmétique à temps constant où
que ce soit, pas de réseau, pas de couche onion. N'en protégez rien.
