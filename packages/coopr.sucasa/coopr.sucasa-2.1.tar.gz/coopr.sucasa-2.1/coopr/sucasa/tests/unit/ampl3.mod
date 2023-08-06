
set SET0;
set SET1 within Integers;
set SET3 within SET1;
set SET4;

param m;
param n in Integers;
param capacity {SET0};
param Xcapacity {SET0};
param Ycapacity integer;
param Zcapacity binary;
param Acapacity symbolic;
var A;
var B1 {SET3};
var B2 {SET0,SET3};
var B3 {SET0,SET3,SET0};
minimize C: A;
minimize D {i in SET3} : B1[i] + sum {j in SET0} (B2[j,i] + B3[j,i,j]);
s.t. E: A >= 0.0;
s.t. F {i in SET3}: B1[i] = 0.0;

# SUCASA SYMBOLS: capacity A D F SET3

