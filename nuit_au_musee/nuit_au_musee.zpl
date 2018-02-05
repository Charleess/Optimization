param museumfile := "input_9.txt";

set O := {read museumfile as "<1n, 2n>" skip 2};
set tmp_abs := {read museumfile as "<1n>" skip 2};
set tmp_ord := {read museumfile as "<2n>" skip 2};

set abcisses := {0 .. max(tmp_abs)};
set ordonnees := {0 .. max(tmp_ord)};

defset square_4(i, j) := {max(0, i - 4) .. min(i + 4, max(tmp_abs))} cross {max(0, j - 4) .. min(j + 4, max(tmp_ord))};
defset square_8(i, j) := {max(0, i - 8) .. min(i + 8, max(tmp_abs))} cross {max(0, j - 8) .. min(j + 8, max(tmp_ord))};

defset neighbors_4(i, j) := {<k, l> in square_4(i, j) with sqrt((k - i)**2 + (l - j)**2) <= 4};
defset neighbors_8(i, j) := {<k, l> in square_8(i, j) with sqrt((k - i)**2 + (l - j)**2) <= 8};

set possible_cams_positions := abcisses cross ordonnees;
set possible_short_cams := possible_cams_positions;
set possible_long_cams := possible_cams_positions;

var scam[possible_short_cams] binary;
var lcam[possible_long_cams] binary;

minimize cost: (sum <i, j> in possible_short_cams: scam[i, j]) + (sum <i, j> in possible_long_cams: lcam[i, j] * 2);

subto allOffersAreProtected:
    forall <i, j> in O:
        sum <k, l> in neighbors_4(i, j): scam[k, l]
        + sum <k, l> in neighbors_8(i, j): lcam[k, l] >= 1;
