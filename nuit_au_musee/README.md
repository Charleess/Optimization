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

L'utilisation de SCIP non installé à la racine peut demander de préciser l'endroit où est situé la librarie dynamique. SUr MacOS, `export DYLD_FALLBACK_LIBRARY_PATH=PATH/TO/YOUR/SCIP/lib` fait l'affaire.

L'idée générale va être de restreindre dramatiquement l'espace des possibilités d'implantation des caméras en imposant qu'elles aient au minimum 2 oeuvres d'art sur leur rayon maximal. Pour obtenir ce résultat, on choisit les implantations possibles à partir des positions des oeuvres, en tracant pour chaque paire d'oeuvres d'art un cercle qui passe par les deux points, et en prenant les deux centres obtenus.

On procède ensuite de manière classique avec SCIP.

Il est nécessaire d'imposer que le rayon des cercles soit légèrement inférieur au rayon théorique pour des raisons d'arrondi.

## Commentaires

Pour une raison assez étrange, le programme génère 20,000 caméras, alors qu'il n'y a que 5,000 oeuvres...