
set SET0;
set SET1 within Integers;
set SET5 within Reals;
set SET3 within SET1;
set SET4 {SET1,SET1};
set SET6 {SET1,SET1} within Integers;
set SET7 {SET1,SET1} within Reals;
# SUCASA set SET8 within reals cross SET0 dimen 2
set SET8 within Reals cross SET0;
# SUCASA set SET9[SET1,SET1] within reals cross SET0 cross integers dimen 3
set SET9 {SET1,SET1} within Reals cross SET0 cross Integers;

param m;
param n in Integers;
param capacity {SET0} in Reals;
param Xcapacity {SET0};
param Ycapacity integer;
param Zcapacity binary;
param Acapacity symbolic;
# SUCASA param p1 in reals cross SET0
param p1 in Reals cross SET0;
# SUCASA param p2[SET0,SET1] in reals cross SET0 cross SET0
param p2 {SET0,SET1} in Reals cross SET0 cross SET0;

var A;
var B1 {SET3};
var B2 {SET0,SET3};
var B3 {SET0,SET3,SET0};
minimize C: A;
minimize D {i in SET3} : B1[i] + sum {j in SET0} (B2[j,i] + B3[j,i,j]);
s.t. E: A >= 0.0;
s.t. F {i in SET3}: B1[i] = 0.0;


# SUCASA SYMBOLS: * 

