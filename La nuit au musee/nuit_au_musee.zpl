param museumfile := "test_file.txt";

set O := {read museumfile as "<1n, 2n>" skip 2};
set tmp_abs := {read museumfile as "<1n>" skip 2};
set tmp_ord := {read museumfile as "<2n>" skip 2};

set ordonnees := {1 .. max(tmp_ord)};
set abcisses := {1 .. max(tmp_abs)};

defset neighbors_4(i, j) := {<k, l> in ordonnees cross abcisses with sqrt((k - i)**2 + (l - j)**2) <= 4};
defset neighbors_8(i, j) := {<k, l> in ordonnees cross abcisses with sqrt((k - i)**2 + (l - j)**2) <= 8};

var map[ordonnees cross abcisses] >= 0 <= 2;

minimize cost: sum <i, j> in ordonnees cross abcisses: map[i, j];

subto allOffersAreProtected:
    forall <i, j> in O:
        sum <k, l> in neighbors_4(i, j): map(k, l) + sum <k, l> in neighbors_8(i, j): map() 