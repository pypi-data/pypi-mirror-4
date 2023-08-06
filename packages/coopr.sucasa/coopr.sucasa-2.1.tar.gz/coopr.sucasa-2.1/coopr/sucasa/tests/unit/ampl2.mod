
param n;

# SUCASA set A within integers dimen 1
set A := 1..n;

# SUCASA set B[Bindex] within integers dimen 1
set B {1..n};

var X;
minimize C: X;
s.t. E: X >= 0.0;

# SUCASA SYMBOLS: *


