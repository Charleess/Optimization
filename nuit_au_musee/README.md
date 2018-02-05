# La nuit au musée

On désire surveiller toutes les oeuvres d'art présentes dans un musée avec un coût minimum. On dispose de deux types de caméras, ayant des rayons d'action et des coûts différents.

## Utilisation

Lancer simplement `nuit_au_musée.py`

```bash
$ pip install -r requirements.txt
$ python nuit_au_musee.py
```

## Démarche utilisant directement la syntaxe ZIMPL

Une première solution contenant très peu d'optimisations est d'utiliser directement la syntaxe ZIMPL pour communiquer avec SCIP.

La plus grosse difficulté dans l'utilisation de ZIMPL est la création d'ensembles par compréhension. On voudrait pourvoir créer des listes restreintes de positions possibles pour nos caméras. N'ayant pas réussi à optimiser cette partie, le ZIMPL va donc tester toutes les positions de la carte.

L'exécution complète prend environ 30 secondes et donne un résultat de 2680 !

## Démarche utilisant SCIP et une heuristique de recherche

L'utilisation de SCIP non installé à la racine peut demander de préciser l'endroit où est situé la librarie dynamique. Sur MacOS, `export DYLD_FALLBACK_LIBRARY_PATH=PATH/TO/YOUR/SCIP/lib` fait l'affaire.

L'idée générale va être de restreindre dramatiquement l'espace des possibilités d'implantation des caméras en imposant qu'elles aient au minimum 2 oeuvres d'art sur leur rayon maximal. On va uniqument garder les positions où la caméra couvre au moins 2 oeuvres, et ce avec une distance maximale pour espérer minimiser les coûts.

Pour trouver ces positions on parcourt l'ensemble des oeuvres d'art. Pour chaque oeuvre, on passe en revue les autres.

* Si la distance entre les deux est supérieure à la distance de la grande caméra, alors on passe à la suivante
* Si la distance entre les deux est comprise entre la petite distance et la grande distance, alors on peut tracer les cercles de rayon la grande distance, qui passent par les deux oeuvres. Il y en a un de chaque côté de la ligne qui relie les deux oeuvres. On obtient deux possibilités pour des caméras de grande portée
* Si la distance entre les deux est inférieure à la petite distance, alors on peut tracer les mêmes cercles que les précédents, plus ceux de rayon la petite distance

On passe de 638,401 positions possibles à 19,397 avec cette méthode. L'algorithme termine en 180s sur un MacBook Air i7@2*1.7GHz, 8Gb RAM, ce qui n'est pas optimal mais acceptable.

On procède ensuite de manière classique avec SCIP. Notons que le temps de résolution n'est que de 1.53s. Le vrai goulot d'étranglement est donc le calcul des contraintes et non leur résolution.

La solution obtenue coûte 3087, c'est moins bien que notre méthode brutale avec ZIMPL et plus lent...

Notes:

* Il est nécessaire d'imposer que le rayon des cercles soit légèrement inférieur au rayon théorique pour des raisons d'arrondi
* Après vérification, la solution n'est pas du tout optimisée car elle boucle sur toutes les positions à chaque fois. Ce ne sera pas fait ici pour des raisons de temps, mais on pourrait aisément l'améliorer en ne regardant pour chaque oeuvre que les positions qui sont dans un voisinage de l'oeuvre et non toutes les positions possibles.

## Démarche brute force

On peut aussi essayer de chercher une solution en ne posant pas d'heuristique de recherche, mais en testant toutes les positions possibles (fonction `__initialize_model_brute()`. On va commencer par chercher toutes les positions possibles de caméra autour des oeuvres. Ensuite, on va ajouter pour chaque oeuvre la contrainte qu'elle soit surveillée.

Cet algorithme devrait donner un score de `2680` puisque il implémente exactement la même méthode que ZIMPL. C'est mieux ! En revanche pour une raison inconnue, j'obtiens `4330`... Après avoir essayé des heures de comprendre pourquoi, j'ai préféré passer à la suite.

On se rend compte qu'on passe en fait plus de temps à calculer les positions des centres des cercles qu'à calculer la solution du problème. Dans le cas de ce problème, c'est plus rentable de le faire en force brute. Si l'espace était plus grand et plus étalé, cette methode serait bien plus longue.

## Recherche locale

L'idée de la recherche locale est:

1. Définir l'espace des solutions
1. Trouver la fonction objectif
1. Définir la notion de voisinage

Pour l'adapter au problème de la nuit au musée:

1. L'espace des solutions est l'ensemble des positions et des types de caméras qui recouvrent toutes les oeuvres d'art.
1. La fonction objectif est le coût total de la solution, soit le prix de chaque caméra multiplié par le nombre de caméras de ce type
1. On dispose de deux méthodes:
    * Pour une solution donnée, un voisinage de cette solution peut être obtenu en enlevant un certain nombre de caméras dans un cercle de rayon 4 aléatoire, et en redécoupant cet espace de manière gloutonne, c'est à dire en essayant de minimiser le nombre de caméras nécessaires pour couvrir les oeuvres dans ce cercle. L'intuition donne qu'il serait intéressant de jouer sur le facteur "Nombre de caméras retirées pour obtenir un voisinage".
    * Pour une solution donnée, un voisinage de cette solution peut être obtenu en ajoutant aléatoirement une caméra à la solution. On retire alors de la solution toute caméra dont l'espace de surveillance intersecte celui de la nouevlle caméra, et on complète les oeuvres d'art manquantes de manière gloutonne (On ajoute des petites caméras).

Dans les deux cas, si la nouvelle solution est meilleure, on remplace la solution précédente par celle là, sinon on l'oublie et on en cherche un autre.