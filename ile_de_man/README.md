# Plus court chemin

## Utilisation

Nécessite d'avoir installé SCIP. Pour pouvoir accéder à la ligne de commande, penser à exporter les deux variables d'environnement nécessaires:

```bash
export PATH=$PATH:/PATH/TO/SCIP/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:PATH/TO/SCIP/lib
```

Piper ensuite le résultat dans le `visualize.js` afin de pouvoir visualiser le résultat

```bash
$ scip -c "read plus_court_chemin.zpl" -c optimize -c "display sols 0" -c quit  | ./visualize.py man.txt > visualize.js
```

## Explications ZIMPL

```zpl
set V := { read graphfile as "<2n>" comment "a"};
```

On ne prend que le 2e élément de chaque ligne, interprété comme un nombre et on passe toutes les lignes qui commencent par un "a"

## Modélisation

Variables
    Xa pour tout arc a
    Xa >= 0

Contraintes
    Pour tout sommet V, la somme sur les arcs entrants en V des Xa - la somme sur les arcs sortants de V des Xa doit être égale à:
        -1 sur v est la source
        +1 si v est la destination
        0 sinon

Xa vaut 1 si l'arc est utilisé, 0 si il n'est pas utilisé

Comme on veut minimiser les poids, il n'y aura forcément pas de cycle.
Le format LP est utilisé pour des programmes très simples, le format ZIMPL est utilisé pour modéliser des problèmes plus complexes.

## Programme

- On lit tous les identifiants de chaque sommet, que l'on met dans le tableau V
- On lit toutes les arètes et on le met dans le tableau A
- On associe à chaque arête de A un temps que l'on met dans le tableau V
- On crée le tableau dans lequel on va mettre les Xa

On chercher ensuite à minimiser la somme les temps des arcs utilisés
Il faut ajouter à cela la contrainte d'entrée/sortie