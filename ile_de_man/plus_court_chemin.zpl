param graphfile := "man.txt";
param source := 283492455;
param target := 283494345;


set V := {read graphfile as "<2n>" comment "a"};
set A := {read graphfile as "<2n,3n>" comment "v"};
param time[A] := read graphfile as "<2n,3n> 4n" comment "v";

defset prec(v) := {<i, v> in A};
defset succ(v) := {<v, j> in A};

var x[A] binary;

do print x;

minimize cost: sum<i, j> in A: time[i, j] * x[i, j];

subto nodeIsConsistent: 
	forall <v> in V - {source, target}:
		sum <i, v> in prec(v): x[i, v] == sum <v, i> in succ(v): x[v, i];

subto sourceIsOk:
	sum <s, i> in succ(source): x[s, i] == 1;

subto targetIsOk:
	sum <i, t> in prec(target): x[i, t] == 1;

subto noWayBack:
	forall <i, j> in A:
		x[i, j] + x[j, i] <= 1;
