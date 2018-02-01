# La nuit au musée

On désire surveiller toutes les oeuvres d'art présentes dans un musée avec un coût minimum. On dispose de deux types de caméras, ayant des rayons d'action et des coûts différents.

## Utilisation

Lancer simplement `nuit_au_musée.py`

```bash
$ pip install -r requirements.txt
$ python nuit_au_musee.py
```

## Démarche utilisant SCIP

Après de nombreux essais infructeux, on utilisera l'intégration Python de SCIP pour résoudre le problème, ZIMPL étant trop obscur pour mettre en place la modélisation désirée. Les fichiers d'origine ZIMPL avec le début de raisonnement sont laissés à titre indicatif.

L'utilisation de SCIP non installé à la racine peut demander de préciser l'endroit où est situé la librarie dynamique. Sur MacOS, `export DYLD_FALLBACK_LIBRARY_PATH=PATH/TO/YOUR/SCIP/lib` fait l'affaire.

L'idée générale va être de restreindre dramatiquement l'espace des possibilités d'implantation des caméras en imposant qu'elles aient au minimum 2 oeuvres d'art sur leur rayon maximal. On va uniqument garder les positions où la caméra couvre au moins 2 oeuvres, et ce avec une distance maximale pour espérer minimiser les coûts.

Pour trouver ces positions on parcourt l'ensemble des oeuvres d'art. Pour chaque oeuvre, on passe en revue les autres.

- Si la distance entre les deux est supérieure à la distance de la grande caméra, alors on passe à la suivante
- Si la distance entre les deux est comprise entre la petite distance et la grande distance, alors on peut tracer les cercles de rayon la grande distance, qui passent par les deux oeuvres. Il y en a un de chaque côté de la ligne qui relie les deux oeuvres. On obtient deux possibilités pour des caméras de grande portée
- Si la distance entre les deux est inférieure à la petite distance, alors on peut tracer un cercle 

On passe de 638,401 positions possibles à 19,952 avec cette méthode. L'algorithme termine en 140s sur un MacBook Air i7@2*1.7GHz, 8Gb RAM

On procède ensuite de manière classique avec SCIP.

Il est nécessaire d'imposer que le rayon des cercles soit légèrement inférieur au rayon théorique pour des raisons d'arrondi.

La solution obtenue coûte 3086.