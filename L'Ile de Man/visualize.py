#!/usr/bin/env python3
# école centrale supélec - c. dürr - 2016

# lit de l'entrée standard une solution produite par SCIP et
# produit des commandes javascript pour la visualiser

# une variable x#i#j > 0.5 correspond à la sélection d'un arc (i,j)
# le fichier passée en ligne de commande contient les coordonnées GPS des sommets

import sys

GPS = {}
arcs = []

hasIn = set()
hasOut = set()

if len(sys.argv) != 2:
    print("Usage: ./visualize [gpsfile]", file=sys.stderr)
    exit(1)

graphfile = sys.argv[1]
for line in open(graphfile,'r'):
    if line[0] == 'v':
        tab = line[1:].split()
        latitude  = float(tab[1])
        longitude = float(tab[2])
        GPS[int(tab[0])] = (latitude, longitude)


nb_fract = 0

for line in sys.stdin:
    if line[0] == 'x':
        tab = line.split()
        val = float(tab[1])
        if val != 0 and val != 1:
            nb_fract += 1
        if val >= 0.5:
            arc = tab[0].split("#")
            u = int(arc[1])
            v = int(arc[2])
            arcs.append((u, v))
            hasIn.add(v)
            hasOut.add(u)

if nb_fract > 0:
    print("// the solution is not integral.", file=sys.stderr)

if len(arcs)==0:
    print("// the input contained no line of the form x#[0-9]+#[0-9]+.", file=sys.stderr)

print ("var markers = [")
for u in hasIn ^ hasOut:
    print(" [%.6f, %.6f]," % GPS[u])
print("];")


print("var arcs = [")
for u, v in arcs:
    print(" [[%.6f, %.6f], [%.6f, %.6f]]," % (GPS[u] + GPS[v]))
print("];")

